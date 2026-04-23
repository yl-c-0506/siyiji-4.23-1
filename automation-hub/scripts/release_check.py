#!/usr/bin/env python
"""Automation Hub 统一发布门禁入口。

学习提示：
- 技术：argparse CLI、subprocess、pytest、urllib preflight、发布报告生成。
- 技术功能：argparse 负责参数化运行模式；subprocess 负责串联 pytest 与 live 验证脚本；urllib preflight 负责在真正执行前先确认服务和 token 是否可用；发布报告负责沉淀本次放行结果。
- 常用场景：一个仓库同时有本地测试、真实环境验收和跨子系统门禁时，用统一 release_check 脚本把不同层级的校验收口。
- 当前文件场景：这里把 automation-hub 的 smoke/regression/full/live/live-worker，再加上思忆集桌面端 gate，统一成一个对外可执行的发布门禁入口。
- 读法：先看 mode 分层，再看 live preflight，最后看桌面端门禁如何串进发布流程。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


SMOKE_TARGETS = [
    "tests/test_api_auth_flow.py",
    "tests/test_api_execution_flow.py",
    "tests/test_local_agent_flow_smoke.py",
    "-q",
]

REGRESSION_TARGETS = [
    "tests",
    "-q",
]

FULL_TARGETS = [
    "tests",
    "-vv",
]

DEFAULT_LIVE_API_BASE = "http://127.0.0.1:30000"


# 这组函数负责把“模式”翻译成具体命令、版本号和输出物，是整个脚本的调度骨架。
# smoke 用最小主链路，regression/full 扩大覆盖面，live/live-worker 则验证真实部署闭环。
def _build_release_version(mode: str) -> str:
    now = datetime.now()
    year, week, _ = now.isocalendar()
    if mode in {"regression", "full", "live", "live-worker"}:
        return f"{year}.{week}.0"
    return f"{now.year}.{now.month:02d}{now.day:02d}-dev.1"


def _emit_release_report(
    repo_root: Path,
    mode: str,
    output_path: str | None = None,
    desktop_gate_summary: str = "未启用",
) -> Path:
    # 发布报告是给人看的留档物，和 pytest/live 日志不同，它回答的是“这次能不能放、放的是什么”。
    report_path = Path(output_path).expanduser().resolve() if output_path else (repo_root / "release_report.md").resolve()
    channel = "stable" if mode in {"regression", "full", "live", "live-worker"} else "dev"
    report_lines = [
        f"# 发布报告 {_build_release_version(mode)} ({channel})",
        "",
        f"发布日期: {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 功能变化",
        "- 本次发布已通过自动化校验门禁。",
        f"- 桌面端门禁：{desktop_gate_summary}",
        "",
        "## 已知问题",
        "- 暂无新增阻断问题；请关注运行日志中的降级告警。",
        "",
        "## 回滚步骤",
        "1. 停止当前发布批次并冻结流量扩容。",
        "2. 回退到上一个稳定版本。",
        "3. 执行快照恢复并重启服务。",
        "4. 复核启动、同步、配置保存、布局应用链路。",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"[release-check] release report written: {report_path}")
    return report_path


def _resolve_live_token_file(token_file: str | None) -> Path:
    if token_file:
        return Path(token_file).expanduser().resolve()
    return (Path(__file__).resolve().parents[1] / ".admin_token").resolve()


def _run_step(title: str, command: list[str], cwd: Path) -> None:
    """统一执行一个子步骤，并把标题与命令打印出来，方便 CI 或人工排障。"""
    print(f"[release-check] {title}")
    print(f"[release-check] command: {' '.join(command)}")
    subprocess.run(command, cwd=str(cwd), check=True)


def _resolve_pytest_basetemp(repo_root: Path, mode: str) -> Path:
    basetemp = (repo_root.parent / ".pytest-tmp" / f"release-check-{mode}").resolve()
    basetemp.mkdir(parents=True, exist_ok=True)
    return basetemp


def _resolve_pytest_args(mode: str, override_args: list[str] | None) -> list[str]:
    # 允许外部显式覆盖 pytest 参数，但默认仍按 mode 选择一套稳定目标集。
    if override_args:
        return override_args
    if mode == "smoke":
        return SMOKE_TARGETS.copy()
    if mode == "full":
        return FULL_TARGETS.copy()
    return REGRESSION_TARGETS.copy()


def _resolve_live_command(repo_root: Path, python_executable: str, script_name: str, api_base: str | None, token_file: str | None, executor: str | None = None) -> list[str]:
    # live 模式本质上是在拼一个“验证脚本命令行”，这样 verify_system 和 verify_worker_system 可复用同一套装配逻辑。
    resolved_api_base = (api_base or DEFAULT_LIVE_API_BASE).rstrip("/")
    resolved_token_file = _resolve_live_token_file(token_file)

    command = [python_executable, str(repo_root / script_name), "--api-base", resolved_api_base]
    command.extend(["--token-file", str(resolved_token_file)])
    if executor:
        command.extend(["--executor", executor])
    return command


def _run_live_preflight(api_base: str | None, token_file: str | None) -> None:
    # live preflight 先把“服务不可达 / token 无效”和“脚本逻辑失败”分离开，方便定位问题。
    resolved_api_base = (api_base or DEFAULT_LIVE_API_BASE).rstrip("/")
    resolved_token_file = _resolve_live_token_file(token_file)

    print(f"[release-check] live preflight api: {resolved_api_base}")
    print(f"[release-check] live preflight token file: {resolved_token_file}")

    if not resolved_token_file.exists():
        raise RuntimeError(
            f"live preflight failed: token file not found: {resolved_token_file}. "
            "use --live-token-file or set AUTOMATION_HUB_TOKEN_FILE"
        )

    token = resolved_token_file.read_text(encoding="utf-8").lstrip("\ufeff").strip()
    if not token:
        raise RuntimeError(f"live preflight failed: token file is empty: {resolved_token_file}")

    health_url = f"{resolved_api_base}/health"
    try:
        with urlopen(health_url, timeout=5) as response:
            if int(response.status) != 200:
                raise RuntimeError(f"live preflight failed: GET {health_url} returned {response.status}")
    except HTTPError as exc:
        raise RuntimeError(f"live preflight failed: GET {health_url} returned {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"live preflight failed: cannot reach {health_url}: {exc.reason}") from exc

    auth_me_url = f"{resolved_api_base}/auth/me"
    auth_request = Request(auth_me_url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urlopen(auth_request, timeout=5) as response:
            if int(response.status) != 200:
                raise RuntimeError(f"live preflight failed: GET {auth_me_url} returned {response.status}")
    except HTTPError as exc:
        raise RuntimeError(
            f"live preflight failed: GET {auth_me_url} returned {exc.code}. "
            "check whether the token is valid and has not expired"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"live preflight failed: cannot reach {auth_me_url}: {exc.reason}") from exc

    print("[release-check] live preflight passed")


def _run_desktop_gate(repo_root: Path, python_executable: str, suite: str) -> None:
    # 桌面端属于联动交付物，因此 release_check 不只管 automation-hub，也会把桌面端质量门一起纳管。
    desktop_gate_script = (repo_root.parent / "scripts" / "desktop_quality_gate.py").resolve()
    if not desktop_gate_script.is_file():
        raise RuntimeError(f"desktop gate failed: gate script not found: {desktop_gate_script}")

    _run_step(
        f"run desktop gate suite={suite}",
        [
            python_executable,
            str(desktop_gate_script),
            "--suite",
            suite,
            "--skip-report",
        ],
        cwd=repo_root.parent,
    )


def _should_run_desktop_gate(mode: str, with_desktop_gate: bool, skip_desktop_gate: bool) -> bool:
    # 默认策略：高于 smoke 的模式都带桌面端 gate；命令行也允许显式打开或跳过。
    if skip_desktop_gate:
        return False
    if with_desktop_gate:
        return True
    return mode in {"regression", "full", "live", "live-worker"}


def main() -> int:
    # main 只做三件事：解析参数、按模式分发、统一收口错误码与发布报告。
    parser = argparse.ArgumentParser(description="Automation Hub 发布前校验入口")
    parser.add_argument(
        "--mode",
        choices=["smoke", "regression", "full", "live", "live-worker"],
        default="regression",
        help="选择校验层级：smoke 为主链路快速校验，regression 为默认回归集，full 为详细输出全量回归，live 为连接真实 API 的 API 验收，live-worker 为连接真实 API 的 worker 消费验收。",
    )
    parser.add_argument(
        "--pytest-args",
        nargs="*",
        default=None,
        help="传给 pytest 的额外参数；设置后会覆盖 --mode 的默认目标。",
    )
    parser.add_argument("--live-api-base", default=None, help=f"live 模式下传给 verify_system.py 的 API 地址，默认 {DEFAULT_LIVE_API_BASE}")
    parser.add_argument("--live-token-file", default=None, help="live 模式下传给 verify_system.py 的 token 文件路径")
    parser.add_argument("--live-worker-executor", choices=["host", "docker"], default="host", help="live-worker 模式下要验证的执行器类型")
    parser.add_argument("--with-desktop-gate", action="store_true", help="额外执行思忆集桌面端 smoke_check 门禁")
    parser.add_argument("--skip-desktop-gate", action="store_true", help="跳过默认启用的桌面端 release 门禁")
    parser.add_argument(
        "--desktop-suite",
        choices=["core", "ui", "p2", "all", "release"],
        default="release",
        help="桌面端门禁套件，默认 release（core+ui+p2 全链路）",
    )
    parser.add_argument("--release-report", default="", help="发布报告输出路径（默认 automation-hub/release_report.md）")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    python_executable = sys.executable

    try:
        if args.mode in {"live", "live-worker"}:
            # 真实环境校验和本地 pytest 是两类问题，所以这里走独立分支处理。
            _run_live_preflight(args.live_api_base, args.live_token_file)
            script_name = "verify_system.py" if args.mode == "live" else "verify_worker_system.py"
            title = "run live api verification" if args.mode == "live" else "run live worker verification"
            _run_step(
                title,
                _resolve_live_command(
                    repo_root,
                    python_executable,
                    script_name,
                    args.live_api_base,
                    args.live_token_file,
                    executor=args.live_worker_executor if args.mode == "live-worker" else None,
                ),
                cwd=repo_root,
            )
        else:
            pytest_args = _resolve_pytest_args(args.mode, args.pytest_args)
            pytest_basetemp = _resolve_pytest_basetemp(repo_root, args.mode)
            _run_step(
                f"run {args.mode} tests",
                [python_executable, "-m", "pytest", "--basetemp", str(pytest_basetemp), *pytest_args],
                cwd=repo_root,
            )

        # 桌面端 gate 放在主校验之后执行，这样可以更清楚地区分“后端失败”还是“联动交付失败”。
        desktop_gate_summary = "未启用"
        if _should_run_desktop_gate(args.mode, args.with_desktop_gate, args.skip_desktop_gate):
            # 思忆集桌面端与 automation-hub 是联动交付物，所以桌面端 gate 也挂进统一放行口。
            _run_desktop_gate(repo_root, python_executable, args.desktop_suite)
            desktop_gate_summary = f"通过（suite={args.desktop_suite}）"
    except subprocess.CalledProcessError as exc:
        print(f"[release-check] failed with exit code {exc.returncode}")
        return exc.returncode
    except RuntimeError as exc:
        print(f"[release-check] {exc}")
        return 2

    # 只有所有校验都通过后才写正式 release report，避免误把失败批次当成可放行版本。
    _emit_release_report(
        repo_root,
        args.mode,
        output_path=args.release_report or None,
        desktop_gate_summary=desktop_gate_summary,
    )
    print("[release-check] all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())