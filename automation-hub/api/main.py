"""Automation Hub API 装配入口。

学习提示：
- 技术：FastAPI、lifespan 生命周期、SQLite 初始化、后台维护线程。
- 技术功能：FastAPI 适合承载 HTTP API；lifespan 适合做应用级启动/关闭动作；后台线程适合做审批过期、产物清理这类持续治理任务。
- 常用场景：中小型服务的 API 入口装配、按领域拆分 router、把数据库初始化和守护型任务统一挂到应用生命周期。
- 当前文件场景：这里不处理复杂业务，只负责把 auth、tools、agent、personal_* 等路由，以及审批/产物治理任务装成一个可启动的后端应用。
- 扩展点：新增路由时先在子模块实现，再回到这里 include_router；新增维护任务时优先挂到 lifespan。
"""

from contextlib import asynccontextmanager
from threading import Event

from fastapi import FastAPI
from api.artifacts.service import start_artifact_cleaner
from api.routes import health, meta, scripts, tasks, runs
from api.routes.tool_runs import router as tool_runs_router
from api.routes.metrics import router as metrics_router
from api.approvals.service import start_approval_expirer
from api.config import settings
from api import db

# 领域路由集中在这里导入，体现的是“分模块实现、单入口装配”的 FastAPI 常见组织方式。
from api.auth.router import router as auth_router
from api.tools.router import router as tools_router
from api.approvals.router import router as approvals_router
from api.audit.router import router as audit_router
from api.proposals.router import router as proposals_router
from api.repos.router import router as repos_router
from api.routes.agent import router as agent_router
from api.routes.agent_nodes import router as agent_nodes_router
from api.routes.execution_authorizations import router as execution_authorizations_router
from api.routes.personal_news import router as personal_news_router
from api.routes.personal_notes import router as personal_notes_router
from api.routes.personal_tasks import router as personal_tasks_router
from api.routes.personal_translations import router as personal_translations_router
from api.routes.personal_wordbooks import router as personal_wordbooks_router
from api.routes.personal_words import router as personal_words_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动与关闭钩子。

    这里是后端的“进程级装配点”：
    - 启动阶段负责准备目录和数据库
    - 启动阶段同时拉起持续治理线程
    - 关闭阶段确保线程有序退出
    """
    print("Initializing database...")
    settings.ensure_dirs()
    db.init_db()
    # stop_event 是共享停止信号，让多个后台线程能在应用关闭时同时感知退出。
    stop_event = Event()
    # 这两个线程属于“维护型后台任务”，不直接响应请求，但会持续治理审批与运行产物。
    approval_expirer = start_approval_expirer(stop_event)
    artifact_cleaner = start_artifact_cleaner(stop_event)
    try:
        yield
    finally:
        # 关闭阶段先广播停止，再逐个等待线程回收，避免 Python 进程直接退出时留下未完成清理。
        if artifact_cleaner is not None:
            stop_event.set()
            artifact_cleaner.join(timeout=1)
        if approval_expirer is not None:
            stop_event.set()
            approval_expirer.join(timeout=1)


# FastAPI 应用对象只做一次实例化，后续测试、uvicorn 和脚本启动都会复用它。
app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)

# 第一层是基础与兼容路由：负责健康检查、元信息和历史入口兼容，通常最先加载也最先排查。
app.include_router(health.router)
app.include_router(meta.router, prefix="/meta", tags=["meta"])
app.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(runs.router, prefix="/runs", tags=["runs"])
app.include_router(tool_runs_router)
app.include_router(metrics_router)

# 第二层是当前主线业务路由：认证、执行治理、Agent 能力和个人数据同步都从这里暴露给客户端。
app.include_router(auth_router)
app.include_router(tools_router)
app.include_router(approvals_router)
app.include_router(audit_router)
app.include_router(proposals_router)
app.include_router(repos_router)
app.include_router(agent_router)
app.include_router(agent_nodes_router)
app.include_router(execution_authorizations_router)
app.include_router(personal_news_router)
app.include_router(personal_notes_router)
app.include_router(personal_tasks_router)
app.include_router(personal_translations_router)
app.include_router(personal_wordbooks_router)
app.include_router(personal_words_router)


# 保留本地直接运行入口，方便在不写额外 uvicorn 命令时快速起一个开发服务。
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)