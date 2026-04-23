# 思忆集

项目简介：思忆集客户端、automation-hub 后端底座与专题文档集合。

包含：桌面端源码、后端底座、自动化脚本与产品/架构文档。

使用说明：
- 在 Windows 上建议使用自带的 Python 虚拟环境运行项目脚本。
- 如需将本项目推送到 GitHub，请先安装 Git，然后运行 `push_to_github.ps1` 并传入目标仓库 URL。

## 学习入口

- 代码学习主入口： [思忆集项目学习笔记/思忆集项目按文件学习笔记.md](思忆集项目学习笔记/思忆集项目按文件学习笔记.md)
- 文档分工总览： [docs/document-map.md](docs/document-map.md)
- 当前这个 README 主要负责仓库总览、运行入口和门禁说明，不替代逐文件学习笔记，也不直接充当实现真源。

## 当前主线

- [思忆集app](思忆集app)：当前实施主线中的桌面增强客户端，负责本地工作台、收件/整理/建议/继续入口。
- [automation-hub](automation-hub)：当前唯一后端真源应用，负责认证、同步、审计、备份、跨设备能力与受控执行底座。
- [docs](docs)：仓库级专题文档真源，负责阶段边界、产品主线、客户端结构、小问代理层与 Android 合同。

当前产品战略定位已经调整为“手机优先、桌面增强、双端自治、语义单合同”；桌面端是当前实施切入点，不代表桌面重新成为唯一主线。详见 [docs/project-roadmap.md](docs/project-roadmap.md) 的 2026-04-20 重规划章节。

## AI 开发前最小阅读集

1. [docs/document-map.md](docs/document-map.md)
2. [docs/project-roadmap.md](docs/project-roadmap.md)
3. [docs/next-phase-product-boundary.md](docs/next-phase-product-boundary.md)
4. [docs/app-platform-boundary-design.md](docs/app-platform-boundary-design.md)
5. [docs/app-client-structure-draft.md](docs/app-client-structure-draft.md)
6. [docs/xiaowen-agent-layer-roadmap.md](docs/xiaowen-agent-layer-roadmap.md) 与 [docs/assistant-execution-framework.md](docs/assistant-execution-framework.md)
7. [docs/siyi-m0-m3-implementation-checklist.md](docs/siyi-m0-m3-implementation-checklist.md)
8. 触及 Android 或手机端开发时，必读 [docs/android-client-technical-design.md](docs/android-client-technical-design.md) 与 [docs/android-capability-contract-design.md](docs/android-capability-contract-design.md)；当前允许开发切片以 technical design 的当前矩阵为准。

判定规则：

- README 只给仓库入口、运行入口和门禁入口，不单独授权功能范围或实现方案。
- 当前阶段先做什么、哪些旧口径已废弃，以 [docs/project-roadmap.md](docs/project-roadmap.md) 和 [docs/next-phase-product-boundary.md](docs/next-phase-product-boundary.md) 为准。
- 直接开工的工作包，以 [docs/siyi-m0-m3-implementation-checklist.md](docs/siyi-m0-m3-implementation-checklist.md) 为准。
- Android 当前可直接开发切片，以 [docs/android-client-technical-design.md](docs/android-client-technical-design.md) 的当前矩阵为准；[docs/android-client-ui-layout.md](docs/android-client-ui-layout.md) 仅作交互母版参考。
<!-- 模块说明：仓库统一说明与整改清单。 -->

## automation-hub 后端底座与运行说明

当前唯一后端真源应用是 [automation-hub](automation-hub)。

目标不是继续堆零散脚本，而是把它收敛为一个“可被 AI 接入、但不会失控执行”的自动化执行底座：

1. 只允许白名单 tool_id 执行。
2. 写操作必须可回滚。
3. 关键动作必须可审计。

## 仓库结构

- [automation-hub](automation-hub)：主应用，包含 API、Worker、Helm Chart、业务文档。
- [automation_hub](automation_hub)：兼容导入层，只用于把 Python 包名映射到 [automation-hub](automation-hub)，不是独立实现。
- [docs](docs)：仓库级专题文档入口，覆盖路线图、产品边界、客户端结构、小问执行框架、Android 合同，以及部署与治理说明。
- [data](data)：本地运行数据目录。
- [tests](tests)：根级测试目录，目前内容较少。

## 开发根目录统一约定（2026-04-03）

为避免误改仓、路径混用和任务执行漂移，后续统一使用以下规则：

- 开发根目录固定为 [思忆集](.)
- automation-hub 相关开发、测试、验收都从 [思忆集](.) 启动
- 只在两个代码入口执行日常改动：
  - 后端入口 [automation-hub](automation-hub)
  - 桌面端入口 [思忆集app](思忆集app)
- [automation_hub](automation_hub) 仅保留兼容导入职责，不承载业务逻辑修改
- 终端执行前先确认当前目录是 [思忆集](.)
- 验证脚本统一使用仓内相对路径（例如 `automation-hub/...`、`思忆集app/...`），不再混用外层工作区路径

VS Code 配置已同步收敛：

- 外层工作区 [/.vscode/tasks.json](../.vscode/tasks.json) 统一将 `cwd` 固定到 [思忆集](.) 并使用仓内相对路径
- 外层工作区 [/.vscode/settings.json](../.vscode/settings.json) 默认终端目录固定到 [思忆集](.)
- 若只打开 [思忆集](.) 作为单一工作区，可继续沿用 [思忆集/.vscode/tasks.json](.vscode/tasks.json) 的同一套入口

## 当前定位

产品已于 2026-04-20 正式重定位为“手机优先、桌面增强、双端自治、语义单合同”的个人记忆与执行系统。下列桌面端能力主线说明当前实施面，不替代产品总定位；完整口径以 [docs/project-roadmap.md](docs/project-roadmap.md) 为准。

项目已经具备安全自动化底座的主要代码骨架：

- 工具注册与执行
- 审批与审计
- tool-runs 新执行入口
- proposals 工作流基础能力
- repos 索引与搜索基础能力
- Helm/K8s 部署骨架

桌面端个人助手链路在当前版本额外补齐了三条能力主线：

- 本地统一可检索记忆：把笔记、任务、收件箱、助手决策和执行记录统一索引为本地记忆层，供助手检索与周报复用
- 多步检索增强：助手回答不再只做一次联网搜索，而是优先回看本地记忆，再做最多三轮联网补充，并对结果做缓存与去重
- 独立技术周报工作流：新增 `weekly_tech_digest` 子代理工作流，按 `assistant_focus_topics` 配置生成每周技术追踪，并写回笔记与收件箱

当前主要问题不是“没有方向”，而是：

- 真实部署环境的 live 验收路径还缺一次成功演练
- 真实部署环境的 Helm 渲染、Docker executor 与环境矩阵还缺一次成体系演练
- automation_hub 仍保留为兼容导入层，后续只应继续变薄，不再承载业务实现

补充状态：2026-03-10 已在本地 Windows 环境完成主库重建、token 补发与撤销、`live` 和 `live-worker` 两条真实验收链路；本地操作说明见 [automation-hub/README.md](automation-hub/README.md)，验收记录见 [automation-hub/docs/live-acceptance-2026-03-10-local.md](automation-hub/docs/live-acceptance-2026-03-10-local.md) 和 [automation-hub/docs/worker-live-acceptance-2026-03-10-local.md](automation-hub/docs/worker-live-acceptance-2026-03-10-local.md)。

补充状态：同日已完成 Docker Desktop 本地三容器栈联调，`http://127.0.0.1:8010` 上的 `live` 与 `live-worker --live-worker-executor host|docker` 均已通过；记录见 [automation-hub/docs/worker-live-acceptance-2026-03-10-docker-local.md](automation-hub/docs/worker-live-acceptance-2026-03-10-docker-local.md)。

补充状态：2026-03-11 已再次通过 [automation-hub/scripts/docker_local_stack.ps1](automation-hub/scripts/docker_local_stack.ps1) 在本机自部署 Docker 三容器栈，并完成 `live` 与 `live-worker --live-worker-executor docker` 复验；记录见 [automation-hub/docs/live-acceptance-2026-03-11-docker-self-deployed.md](automation-hub/docs/live-acceptance-2026-03-11-docker-self-deployed.md) 和 [automation-hub/docs/worker-live-acceptance-2026-03-11-docker-self-deployed.md](automation-hub/docs/worker-live-acceptance-2026-03-11-docker-self-deployed.md)。

说明：上述 2026-03-11 记录只代表“本机自部署 Docker 环境已通过复验”，不能替代 [automation-hub/docs/live-acceptance-2026-03-11-remote.md](automation-hub/docs/live-acceptance-2026-03-11-remote.md) 和 [automation-hub/docs/worker-live-acceptance-2026-03-11-remote.md](automation-hub/docs/worker-live-acceptance-2026-03-11-remote.md) 这两份真实部署环境留档。

说明：主应用目录 [automation-hub](automation-hub) 现已具备固定质量门禁入口。

- 命令行统一入口： [automation-hub/scripts/release_check.py](automation-hub/scripts/release_check.py)
- VS Code 任务：根工作区 [/.vscode/tasks.json](.vscode/tasks.json)
- CI 门禁： [automation-hub/.github/workflows/ci.yaml](automation-hub/.github/workflows/ci.yaml)

当前门禁分层为：Pull Request 跑 `smoke`，`main` 分支跑 `regression`。

补充说明：CI 现已固定加入 Helm chart 校验，`workflow_dispatch` 也已支持 `live-worker` 的执行器类型选择。

## 验收状态

### 已完成的本机验收

- 本地 Windows 主库链路已完成 `live` 与 `live-worker`： [automation-hub/docs/live-acceptance-2026-03-10-local.md](automation-hub/docs/live-acceptance-2026-03-10-local.md)、[automation-hub/docs/worker-live-acceptance-2026-03-10-local.md](automation-hub/docs/worker-live-acceptance-2026-03-10-local.md)
- Docker Desktop 本地三容器栈已完成联调： [automation-hub/docs/worker-live-acceptance-2026-03-10-docker-local.md](automation-hub/docs/worker-live-acceptance-2026-03-10-docker-local.md)
- 2026-03-11 已再次完成本机自部署 Docker 三容器栈复验： [automation-hub/docs/live-acceptance-2026-03-11-docker-self-deployed.md](automation-hub/docs/live-acceptance-2026-03-11-docker-self-deployed.md)、[automation-hub/docs/worker-live-acceptance-2026-03-11-docker-self-deployed.md](automation-hub/docs/worker-live-acceptance-2026-03-11-docker-self-deployed.md)

### 仍待完成的真实环境验收

- 真实部署环境 `live` 留档仍待回填： [automation-hub/docs/live-acceptance-2026-03-11-remote.md](automation-hub/docs/live-acceptance-2026-03-11-remote.md)
- 真实部署环境 `live-worker --live-worker-executor docker` 留档仍待回填： [automation-hub/docs/worker-live-acceptance-2026-03-11-remote.md](automation-hub/docs/worker-live-acceptance-2026-03-11-remote.md)

说明：本机验收记录只能证明当前仓库脚本、镜像和本地运行时可用，不能替代真实部署环境的放行证据。

## 本地 K8s 快速入口

如果当前目标是操作 Docker Desktop 本地 Kubernetes，不需要先读完整 README，直接从下面两个入口开始：

1. 操作手册： [automation-hub/docs/local-k8s-runbook.md](automation-hub/docs/local-k8s-runbook.md)
2. VS Code 聚合任务： [/.vscode/tasks.json](.vscode/tasks.json#L121) 的 `automation-hub: k8s-host-flow` 和 [/.vscode/tasks.json](.vscode/tasks.json#L245) 的 `automation-hub: k8s-docker-flow`

推荐使用方式：

- 默认本地联调：先看 runbook，再执行 `automation-hub: k8s-host-flow`
- 验证 Kubernetes 内 Docker executor：先看 runbook，再执行 `automation-hub: k8s-docker-flow`
- 本地状态明显脏了或 profile 对不上：先看 runbook 中的 reset 说明，再执行 `automation-hub: k8s-reset`

## 建议保留的文档入口

以下文档保留，作为后续维护的正式入口：

- 根目录专题文档
  - [docs/api-reference.md](docs/api-reference.md)
  - [docs/helm-deployment.md](docs/helm-deployment.md)
  - [docs/observability.md](docs/observability.md)
  - [docs/token-management.md](docs/token-management.md)
  - [docs/docker-best-practices.md](docs/docker-best-practices.md)
- 主应用总览与约束
  - [automation-hub/README.md](automation-hub/README.md)
  - [automation-hub/THREE_LAWS.md](automation-hub/THREE_LAWS.md)
  - [automation-hub/DEPLOYMENT_CHECKLIST.md](automation-hub/DEPLOYMENT_CHECKLIST.md)
- 主应用细分规范
  - [automation-hub/docs/api.md](automation-hub/docs/api.md)
  - [automation-hub/docs/approvals.md](automation-hub/docs/approvals.md)
  - [automation-hub/docs/rbac.md](automation-hub/docs/rbac.md)
  - [automation-hub/docs/tool-spec.md](automation-hub/docs/tool-spec.md)
- 设计与未来路线
  - [docs/project-roadmap.md](docs/project-roadmap.md)
  - [automation-hub/docs/design/ARCHITECTURE_DESIGN.md](automation-hub/docs/design/ARCHITECTURE_DESIGN.md)
  - [automation-hub/docs/design/AGENT_INTEGRATION_GUIDE.md](automation-hub/docs/design/AGENT_INTEGRATION_GUIDE.md)
  - [automation-hub/docs/design/intel/INTEL_FEATURE_DESIGN.md](automation-hub/docs/design/intel/INTEL_FEATURE_DESIGN.md)

## 根级操作清单

### 1. 代码入口清单

- FastAPI 主入口： [automation-hub/api/main.py](automation-hub/api/main.py)
- Worker 启动入口： [automation-hub/worker/worker.py](automation-hub/worker/worker.py)
- 主执行链路： [automation-hub/worker/jobs_v2.py](automation-hub/worker/jobs_v2.py)
- Docker 执行器： [automation-hub/worker/executors/docker.py](automation-hub/worker/executors/docker.py)
- Helm Chart： [automation-hub/deploy/charts/automation-hub](automation-hub/deploy/charts/automation-hub)

### 2. 当前推荐接口清单

- 健康检查： `/health`
- 工具执行： `/tool-runs`
- 审批中心： `/approvals`
- 审计查询： `/audit`
- 提案流转： `/proposals`
- 仓库索引： `/repos`
- 指标暴露： `/metrics`

说明：`/runs` 是兼容层，后续应持续弱化。

### 3. 上线前整改清单

- [x] 主入口已统一到 [automation-hub/api/main.py](automation-hub/api/main.py)，核心路由已接齐到 tool-runs、audit、proposals、repos、metrics。
- [x] Token 生命周期已补齐基础治理：expires_at 校验、默认 TTL、模板创建、轮换与撤销。
- [x] approvals 已切到精细 scope，区分 approval:read 与 approval:decide，并补齐审批审计。
- [x] quickstart、verify_system、release-check 已对齐当前 API 现实。
- [x] DockerExecutor 结构问题已修复，主执行链路已有回归覆盖。
- [x] auth、tools、approvals、audit、tool-runs、worker、repos、proposals 已纳入固定回归门禁。
- [ ] 按 [automation-hub/docs/remote-acceptance-plan.md](automation-hub/docs/remote-acceptance-plan.md) 在真实部署环境完成一次 `live` 验收，并回填 [automation-hub/docs/live-acceptance-2026-03-11-remote.md](automation-hub/docs/live-acceptance-2026-03-11-remote.md)。
- [ ] 按 [automation-hub/docs/remote-acceptance-plan.md](automation-hub/docs/remote-acceptance-plan.md) 在真实部署环境完成一次 `live-worker --live-worker-executor docker` 验收，并回填 [automation-hub/docs/worker-live-acceptance-2026-03-11-remote.md](automation-hub/docs/worker-live-acceptance-2026-03-11-remote.md)。

补充说明（2026-03-12）：已在当前工作站重新执行 `--mode live` 与 `--mode live-worker --live-worker-executor docker`，两者均在 preflight 阶段因缺少 `automation-hub/.admin_token` 失败；详见两份 remote 留档中的“本次实际执行”与“阻塞信息”更新。
- [x] 已将 [automation_hub](automation_hub) 明确收口为兼容导入层，并完成历史归档目录的无引用核对与移除。

### 4. 固定质量门禁

- 桌面端统一依赖安装：`.venv3.11/Scripts/python.exe -m pip install -r requirements-desktop.txt`
- 命令行统一入口：`python automation-hub/scripts/release_check.py --mode smoke|regression|full|live|live-worker`
- VS Code 任务入口： [/.vscode/tasks.json](.vscode/tasks.json)
- VS Code 调试入口： [/.vscode/launch.json](.vscode/launch.json)
- 思忆集桌面端入口说明： [思忆集app/README.md](思忆集app/README.md)
- 思忆集桌面端离线冒烟：`.venv3.11/Scripts/python.exe 思忆集app/smoke_check.py` 或 VS Code 任务 `思忆集app: smoke-check`
- 思忆集桌面端 P2 最小验收：`.venv3.11/Scripts/python.exe 思忆集app/smoke_check.py --suite p2`
- 思忆集桌面端发布门禁（core+ui+p2）：`.venv3.11/Scripts/python.exe 思忆集app/smoke_check.py --suite release`
- 思忆集桌面端统一门禁入口（smoke + 发布报告）：`.venv3.11/Scripts/python.exe scripts/desktop_quality_gate.py --suite release`
- 旧 `.venv` 路径防回退检查：`.venv3.11/Scripts/python.exe scripts/check_legacy_venv_refs.py` 或 VS Code 任务 `思忆集: legacy-venv-guard`
- 思忆集桌面端当前运行入口：`.venv3.11/Scripts/python.exe 思忆集app/思忆集test1.py` 或 VS Code 任务 `思忆集app: run`
- 思忆集桌面端冷启动稳定性检查（DoD 30 轮）：`.venv3.11/Scripts/python.exe scripts/cold_start_stability_check.py --rounds 30 --auto-exit-ms 1200`
- 思忆集桌面端推荐顺序：VS Code 任务 `思忆集app: smoke-then-run`
- 思忆集桌面端历史归档： [思忆集app/思忆集test1_backup.py](思忆集app/思忆集test1_backup.py)；该文件仅供比对，已禁止直接运行
- 思忆集翻译功能凭证：优先读取环境变量 `SIYI_YOUDAO_APP_KEY` / `SIYI_YOUDAO_APP_SECRET`，其次读取 `思忆集app/data/settings.json` 中的 `youdao_app_key` / `youdao_app_secret`
- 思忆集桌面端 automation-hub 接入配置：优先读取环境变量 `SIYI_AUTOMATION_HUB_API_BASE` / `SIYI_AUTOMATION_HUB_API_TOKEN`，其次读取 `思忆集app/data/settings.json` 中的 `automation_hub_api_base` / `automation_hub_api_token`
- 思忆集桌面端现已提供应用设置入口，可在主窗口“应用设置”中维护本地翻译凭证
- 思忆集桌面端现已提供 automation-hub 连接测试，可在主窗口“应用设置”中验证 `/health` 和可选的 `/auth/me`
- CI 工作流入口： [automation-hub/.github/workflows/ci.yaml](automation-hub/.github/workflows/ci.yaml)
- 统一发布前门禁（automation-hub + 桌面端）：`python automation-hub/scripts/release_check.py --mode smoke --with-desktop-gate --desktop-suite p2`
- 桌面端本地数据治理（清理+去重+回填，默认 dry-run 建议先试跑）：`.venv3.11/Scripts/python.exe scripts/desktop_data_governance.py --dry-run`
- Helm chart 固定校验：GitHub Actions `helm-validate` 作业
- PR 高风险配置审计：GitHub Actions `risk-config-audit` 作业（若修改 release gate / action guard / CI 配置，需同时补充 `docs/risk-config-change-*.md` 复核说明）
- 运维清理任务：`automation-hub: artifact-cleanup-dry-run`、`automation-hub: artifact-cleanup`
- 本地 K8s 任务：`automation-hub: k8s-host-preflight`、`automation-hub: k8s-host-install`、`automation-hub: k8s-host-live`、`automation-hub: k8s-host-worker-live`、`automation-hub: k8s-host-status`、`automation-hub: k8s-host-flow`、`automation-hub: k8s-docker-preflight`、`automation-hub: k8s-docker-install`、`automation-hub: k8s-docker-live`、`automation-hub: k8s-docker-worker-live`、`automation-hub: k8s-docker-status`、`automation-hub: k8s-docker-flow`、`automation-hub: k8s-reset`

本地 Docker Desktop Kubernetes 的推荐操作顺序已经单独整理为手册： [automation-hub/docs/local-k8s-runbook.md](automation-hub/docs/local-k8s-runbook.md)。后续涉及 host 或 docker-executor 的本地联调、重建、验收，优先以这份 runbook 为准。

真实部署环境的 live / live-worker 验收计划已经单独整理为： [automation-hub/docs/remote-acceptance-plan.md](automation-hub/docs/remote-acceptance-plan.md)。后续需要关闭根 README 中这两项待办时，直接按这份计划执行并补留档。

当前模式约定：

- `smoke`：快速主链路校验，适合开发期频繁执行。
- `regression`：默认完整回归门禁，适合提交前和主分支校验。
- `full`：完整回归加详细 pytest 输出，适合排查失败。
- `live`：连接真实 API 服务执行 API 验收，进入完整校验前会先检查 token 文件、`/health`、`/auth/me`。
- `live-worker`：连接真实 API 服务执行 worker 消费验收，验证低风险 run 与审批后高风险 run 的真实执行闭环；生产环境建议搭配 `--live-worker-executor docker`。

当前 CI 分层策略：

- Pull Request：执行 Helm 校验和 `smoke`。
- Push 到 `main`：执行 Helm 校验和 `regression`。
- 手动触发：通过 [automation-hub/.github/workflows/ci.yaml](automation-hub/.github/workflows/ci.yaml) 的 `workflow_dispatch` 可选执行 `smoke`、`regression`、`full`、`live`、`live-worker`、`artifact-cleanup-dry-run`、`artifact-cleanup`；其中 `live` 与 `live-worker` 需要提供 `live_api_base`，`live-worker` 还可显式选择 `live_worker_executor=host|docker`，清理模式可选提供 `run_retention_days` 与 `proposal_retention_days`，并预先配置仓库 Secret `AUTOMATION_HUB_LIVE_TOKEN`。

手动触发说明：

1. 在 GitHub Actions 页面选择 [automation-hub/.github/workflows/ci.yaml](automation-hub/.github/workflows/ci.yaml) 对应工作流。
2. 点击 Run workflow，并选择需要执行的 `mode`。
3. 若选择 `live` 或 `live-worker`，填写目标 API 地址 `live_api_base`。
4. 若选择 `live-worker`，按目标环境填写 `live_worker_executor`，真实部署环境优先选择 `docker`。
5. 若选择产物清理模式，可按需填写 `run_retention_days` 与 `proposal_retention_days` 覆写默认保留天数。
6. 提前在仓库 Secrets 中配置 `AUTOMATION_HUB_LIVE_TOKEN`，供 live 验收模式生成临时 token 文件使用。

### 5. 生产部署清单

- [ ] 明确集群运行时是 docker 还是 containerd。
- [ ] 若使用 DockerExecutor，确认 worker 节点具备 docker.sock，并通过调度约束固定到可用节点。
- [ ] 生产环境外置 Redis，避免内置 emptyDir Redis 丢状态。
- [ ] 所有敏感配置通过 Secret 注入，不使用明文配置文件落盘。
- [ ] 选择明确的 Helm 生产模板：
  - [ ] 通用生产基线使用 [automation-hub/deploy/charts/automation-hub/values-prod-external-redis.yaml](automation-hub/deploy/charts/automation-hub/values-prod-external-redis.yaml)
  - [ ] Docker executor 场景使用 [automation-hub/deploy/charts/automation-hub/values-prod-docker-executor.yaml](automation-hub/deploy/charts/automation-hub/values-prod-docker-executor.yaml)
- [ ] 若 `DATABASE_PATH` 仍指向 SQLite 文件，保持 API 单副本；不要把 `replicaCount` 提到 2 以上。
- [ ] 若关闭 chart 内置 Redis，必须显式提供外部 `REDIS_URL`。
- [ ] 若不使用 chart 自建 Secret，必须显式提供外部 `existingSecretName`。
- [ ] 若 Prometheus Operator 存在，再启用 ServiceMonitor。

live 验收留档模板： [automation-hub/docs/live-acceptance-template.md](automation-hub/docs/live-acceptance-template.md)

worker live 验收留档模板： [automation-hub/docs/worker-live-acceptance-template.md](automation-hub/docs/worker-live-acceptance-template.md)

真实部署环境的执行顺序和完成定义见： [automation-hub/docs/remote-acceptance-plan.md](automation-hub/docs/remote-acceptance-plan.md)

### 6. 未来实现规划

正式路线图已收敛到 [docs/project-roadmap.md](docs/project-roadmap.md)。本节只保留阶段摘要，避免根 README 持续膨胀。

#### 阶段一：底座收口

- 关闭真实部署环境 `live` / `live-worker` 放行缺口
- 收敛仓库级文档入口和远端验收留档

#### 阶段二：安全工作流闭环

- 固化生产部署基线、审批终态、审计追溯与产物治理

#### 阶段三：产品化扩展

- 在安全底座稳定后，优先推进思忆集 PC 桌面端与 automation-hub 的客户端/后端整合，先把桌面端收敛为“主窗口 + 悬浮助手”的个人助手入口，再沿“个人数据云 -> 个人内容云 -> 个人云工作台”路线扩展

补充说明：百度网盘类外部服务后续只作为备份、归档或迁移辅助通道，不作为本项目个人云平台的核心能力依赖；正式路线以 [docs/project-roadmap.md](docs/project-roadmap.md) 为准。

## 文档收敛原则

从现在开始：

- 根目录 [README.md](README.md) 负责回答“这个仓库现在是什么、保留哪些文档、先做什么”。
- 细分能力只在对应专题文档维护，不再新增重复的阶段总结、功能宣传稿、完整大杂烩指南。
- 阶段性总结如果需要保留，应转为 issue、milestone 或 changelog，而不是新的长期说明文档。
