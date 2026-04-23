"""Automation Hub worker 的统一执行主链路。

学习提示：
- 技术：RQ worker 任务入口、JSON Schema 参数校验、Path 白名单、Host/Docker 执行器、审计日志。
- 技术功能：RQ 负责异步消费任务；JSON Schema 负责限制参数结构；Path 白名单负责限制文件系统边界；执行器负责真正落命令；审计日志负责留痕与追溯。
- 常用场景：需要把“用户请求”变成“后台异步执行”，同时又希望保留审批、参数校验、路径隔离和执行结果回放的系统。
- 当前文件场景：这里正是 tool run 的 worker 主入口，负责把 API 侧已经创建的 run 继续推进成 running、succeeded 或 failed，并同步写审计事件。
- 读法：优先关注审批兜底、安全边界、执行器切换、结果回写这四段。
"""

from __future__ import annotations
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from api.db import get_db_connection
from api.tools.registry import get_tool
from worker.policy_enforce import is_run_approved
from worker.executors.host import HostExecutor
from worker.executors.docker import DockerExecutor
from api.audit.service import log_event
from jsonschema import validate as js_validate
from jsonschema.exceptions import ValidationError


logger = logging.getLogger(__name__)


def now_iso() -> str:
    """返回当前 UTC 时间的 ISO 格式字符串。

    统一时间格式可以让数据库、日志和前端显示使用同一套时区语义。
    """
    return datetime.now(timezone.utc).isoformat()


def run_tool_job(run_id: str, tool_id: str, args: dict, user_id: str | None = None) -> None:
    """执行工具任务（RQ Job 入口）。
    
    完整流程：
    1. 检查审批状态
    2. 加载工具配置
    3. 选择执行器
    4. 执行工具
    5. 记录审计日志
    
    Args:
        run_id: 运行 ID
        tool_id: 工具 ID
        args: 工具参数
        user_id: 用户 ID（用于审计）
    """
    logger.info(f"Starting run {run_id} for tool {tool_id}")
    execution_started_at = datetime.now(timezone.utc)

    # 先规整参数，避免 None 在后续遍历、注入环境变量和 schema 校验里制造分支噪音。
    args = args or {}
    
    # 审批通常在 API 侧完成；worker 再检查一遍，是为了防止队列侧绕过审批边界。
    if not is_run_approved(run_id):
        logger.warning(f"Run {run_id} not approved, skipping execution")
        with get_db_connection() as conn:
            # 如果审批被拒绝/未批准，保持 pending_approval/denied 由审批表决定
            row = conn.execute(
                """SELECT status FROM approval_requests
                   WHERE resource_type='run' AND resource_id=?
                   ORDER BY created_at DESC
                   LIMIT 1""",
                (run_id,),
            ).fetchone()
            approval_status = row["status"] if row else None
            new_status = "denied" if approval_status in {"denied", "expired", "cancelled"} else "pending_approval"
            conn.execute("UPDATE tool_runs SET status=? WHERE id=?", (new_status, run_id))
            conn.commit()

        log_event(
            event_type="run.blocked",
            action="execute",
            status="fail",
            actor_user_id=user_id,
            resource_type="run",
            resource_id=run_id,
            message="Run blocked: not approved",
            meta={"tool_id": tool_id, "approval_status": approval_status},
        )
        return
    
    # tool 配置定义了命令、参数契约、路径白名单和执行器类型，是整条执行链路的中心契约。
    tool = get_tool(tool_id)
    if not tool:
        logger.error(f"Tool {tool_id} not found")
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE tool_runs SET status='failed', finished_at=? WHERE id=?",
                (now_iso(), run_id),
            )
            conn.commit()
        return
    
    # tool_runs 记录是 API 与 worker 共享的状态面：前端、审计和回放都会依赖这里的结果。
    with get_db_connection() as conn:
        run = conn.execute(
            "SELECT * FROM tool_runs WHERE id=?",
            (run_id,),
        ).fetchone()
        
        if not run:
            logger.error(f"Run {run_id} not found")
            return
        
        # 状态切到 running 代表“worker 已接手 run，进入执行准备阶段”；后续仍会继续做 schema 和路径校验。
        started_at_iso = execution_started_at.isoformat()
        conn.execute(
            "UPDATE tool_runs SET status='running', started_at=? WHERE id=?",
            (started_at_iso, run_id),
        )
        conn.commit()
        
        run = dict(run)
    
    # command_json / args_schema / allowed_paths 是 tool 注册时最关键的三类配置。
    # 可以把它理解为：执行内容、输入契约、访问边界。
    command = json.loads(tool["command_json"])
    cwd = tool.get("cwd")
    timeout = int(tool.get("timeout_sec") or 120)

    # JSON Schema 是参数安全边界之一：先挡掉结构错误，再谈真正执行。
    try:
        schema_raw = tool.get("args_schema_json")
        if schema_raw:
            schema = json.loads(schema_raw)
            js_validate(instance=args or {}, schema=schema)
    except ValidationError as e:
        msg = f"args_schema 校验失败: {e.message}"
        logger.warning(msg)
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE tool_runs SET status='failed', finished_at=?, error_msg=? WHERE id=?",
                (now_iso(), msg, run_id),
            )
            conn.commit()
        log_event(
            event_type="run.invalid_args",
            action="execute",
            status="fail",
            actor_user_id=user_id,
            resource_type="run",
            resource_id=run_id,
            message=msg,
            meta={"tool_id": tool_id},
        )
        return
    except Exception as e:
        msg = f"args_schema 解析/校验异常: {str(e)}"
        logger.exception(msg)
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE tool_runs SET status='failed', finished_at=?, error_msg=? WHERE id=?",
                (now_iso(), msg, run_id),
            )
            conn.commit()
        return

    # 这里把 run 上下文转成环境变量，目的是让 Host/Docker 两类执行器和最终脚本都用同一套输入口径。
    env = os.environ.copy()
    env["WORKSPACE"] = env.get("WORKSPACE") or "/workspace"
    env["DATA_DIR"] = env.get("DATA_DIR") or "/data"
    env["RUN_ID"] = run_id
    env["TOOL_ID"] = tool_id

    # 参数转成 ARG_* 环境变量后，脚本侧就能用统一方式读取运行输入。
    # 这比强依赖固定 CLI 位置参数更容易扩展，也更适合被 AI 代理生成调用。
    for key, value in args.items():
        env[f"ARG_{key.upper()}"] = str(value)

    # allowed_paths 是文件系统边界：即使参数结构合法，路径不安全也不能执行。
    # 这两个内部函数是路径治理核心：一个负责从参数里抽候选路径，一个负责判定路径是否落在允许前缀内。
    def _extract_paths(a: dict) -> list[str]:
        keys = {"path", "file", "files", "dir", "directory", "cwd", "root", "source", "destination", "target"}
        out: list[str] = []
        for k, v in (a or {}).items():
            if k not in keys:
                continue
            if isinstance(v, str) and v.strip():
                out.append(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str) and item.strip():
                        out.append(item)
        return out

    def _is_allowed(raw: str, allowed_prefixes: list[Path], base: Path) -> bool:
        if not allowed_prefixes:
            return True
        candidate = Path(raw)
        try:
            if not candidate.is_absolute():
                candidate = (base / candidate)
            candidate = candidate.resolve(strict=False)
        except Exception:
            return False

        for pref in allowed_prefixes:
            try:
                p = pref
                if str(p) == ".":
                    p = base
                if not p.is_absolute():
                    p = (base / p)
                p = p.resolve(strict=False)
                if candidate == p or p in candidate.parents:
                    return True
            except Exception:
                continue
        return False

    # allowed_paths 为空时等同于“不做路径限制”；有值时则每个候选路径都必须被白名单覆盖。
    try:
        allowed_raw = tool.get("allowed_paths_json") or "[]"
        allowed_list = json.loads(allowed_raw)
        if not isinstance(allowed_list, list):
            allowed_list = []
    except Exception:
        allowed_list = []

    base_dir = Path(env.get("WORKSPACE") or os.getcwd())
    allowed_prefixes = [Path(str(x)) for x in allowed_list if isinstance(x, str) and x.strip()]
    for pv in _extract_paths(args or {}):
        if not _is_allowed(pv, allowed_prefixes, base_dir):
            msg = f"路径不在 allowed_paths 白名单内: {pv}"
            logger.warning(msg)
            with get_db_connection() as conn:
                conn.execute(
                    "UPDATE tool_runs SET status='failed', finished_at=?, error_msg=? WHERE id=?",
                    (now_iso(), msg, run_id),
                )
                conn.commit()
            log_event(
                event_type="run.path_blocked",
                action="execute",
                status="fail",
                actor_user_id=user_id,
                resource_type="run",
                resource_id=run_id,
                message=msg,
                meta={"tool_id": tool_id, "allowed_paths": allowed_list},
            )
            return
    
    # 执行器选择是天然扩展点：未来要加 sandbox / remote executor，也应该继续复用这个接口层。
    executor_name = tool.get("executor", "docker")
    if executor_name == "host":
        executor = HostExecutor()
    else:
        # 默认使用 Docker
        executor = DockerExecutor()
    
    logger.info(f"Executing with {executor_name} executor")
    
    # 真正执行后，无论成功失败，都要把状态和审计写完整，方便前端和运维复盘。
    try:
        exit_code = executor.run(
            command=command,
            cwd=cwd,
            env=env,
            timeout=timeout,
            stdout_path=run["stdout_path"],
            stderr_path=run["stderr_path"]
        )

        # 执行结果回写分两层：tool_runs 存状态真相，audit log 存行为事件，二者一起保证可观测性。
        finished_at = datetime.now(timezone.utc)
        duration_sec = round((finished_at - execution_started_at).total_seconds(), 3)
        finished_at_iso = finished_at.isoformat()
        
        status = "succeeded" if exit_code == 0 else "failed"
        logger.info(f"Run {run_id} finished with status={status}, exit_code={exit_code}")
        
        # 数据库状态是前端最常读的面板数据，所以先保证状态和退出码入库。
        with get_db_connection() as conn:
            conn.execute(
                """UPDATE tool_runs
                   SET status=?, finished_at=?, exit_code=?
                   WHERE id=?""",
                (status, finished_at_iso, exit_code, run_id),
            )
            conn.commit()
        
        # 审计事件负责给“谁在什么时间执行了什么、结果如何”留正式记录。
        log_event(
            event_type="run.executed",
            action="execute",
            status="success" if exit_code == 0 else "fail",
            actor_user_id=user_id,
            resource_type="run",
            resource_id=run_id,
            message=f"Tool executed with exit code {exit_code}",
            meta={
                "tool_id": tool_id,
                "exit_code": exit_code,
                "duration_sec": duration_sec,
            }
        )
        
    except Exception as e:
        logger.exception(f"Run {run_id} failed with exception")
        failed_at = datetime.now(timezone.utc)
        duration_sec = round((failed_at - execution_started_at).total_seconds(), 3)
        
        # 运行时异常和命令返回非零退出码是两类失败：这里处理的是前者，通常表示执行器或调用链本身抛错。
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE tool_runs SET status='failed', finished_at=? WHERE id=?",
                (failed_at.isoformat(), run_id),
            )
            conn.commit()
        
        # 即使抛异常，也要把失败事件写到审计里，方便区分“命令失败”和“链路异常”。
        log_event(
            event_type="run.failed",
            action="execute",
            status="fail",
            actor_user_id=user_id,
            resource_type="run",
            resource_id=run_id,
            message=f"Tool execution failed: {str(e)}",
            meta={"tool_id": tool_id, "error": str(e), "duration_sec": duration_sec}
        )
