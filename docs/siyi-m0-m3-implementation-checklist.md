# 思忆集 M0-M3 实施清单（2026-04-19）

本文档把当前主路线拆成可执行工作包，作为以下文档的实施层补充：

- [project-roadmap.md](project-roadmap.md)
- [siyi-desktop-delivery-plan-2026-04.md](siyi-desktop-delivery-plan-2026-04.md)
- [desktop-doctor-debug-assets.md](desktop-doctor-debug-assets.md)
- [assistant-execution-framework.md](assistant-execution-framework.md)
- [main-window-decoupling-plan.md](main-window-decoupling-plan.md)
- [xiaowen-agent-layer-roadmap.md](xiaowen-agent-layer-roadmap.md)
- [android-client-technical-design.md](android-client-technical-design.md)

## 使用原则

- M0 未闭环，不启动 Android 正式产品化。
- M1 未稳定，不继续向 [../思忆集app/ui_main_window.py](../思 忆集app/ui_main_window.py) 堆业务入口。
- M2 未稳定，不抢角色表现层和更重自治能力。
- 每个工作包都必须带验证口径与完成定义，不接受只改结构不验行为。
- Android 当前允许开发的切片，以 [android-client-technical-design.md](android-client-technical-design.md) 第 0 节和第 13 节为准；对象是否允许直接落地，以 [android-capability-contract-design.md](android-capability-contract-design.md) 的对象状 态矩阵为准。

## 当前已启动

- 已完成第一刀： [../scripts/desktop_doctor.py](../scripts/desktop_doctor.py) 新增 `--debug-assets-json`，可导出结构化 Doctor 调试资产 JSON。
- 已补回归测试： [../思忆集app/tests/test_p2_min_acceptance.py](../思忆集app/tests/test_p2_min_acceptance.py) 覆盖新导出参数和旧 `--json` 兼容语义。
- 已完成第二刀： [../思忆集app/ui_startup_guide_dialog.py](../思忆集app/ui_startup_guide_dialog.py) 的 `DesktopDoctorDialog` 新增“导出调试资产 JSON”按钮，并复用当前 `debug_assets`。
- 已补 UI 回归： [../思忆集app/tests/test_ui_startup_guide_dialog.py](../思忆集app/tests/test_ui_startup_guide_dialog.py) 覆盖导出成功和无资产告警。
- 已完成第三刀： [../思忆集app/ui_startup_guide_dialog.py](../思忆集app/ui_startup_guide_dialog.py) 已把 `hero` 和 `issues`  拆成可复用 widget，为主窗口状态卡和工作台卡片铺路。
- 当前下一刀默认落在 M1-WP3 和 M1-WP4：Doctor 资产复用到更多入口，以及主窗口第一刀解耦。

## M0 远 端放行闭环

### M0-WP1 远端环境归属与 values 策略冻结

- 目标：固定 `live`、`live-worker` 的部署归属、values 选型和 `live_api_base` 真源。
- 依赖前置：无。
- 涉及文件/模块： [../automation-hub/deploy/charts/automation-hub/Chart.yaml](../automation-hub/deploy/charts/automation-hub/Chart.yaml) 、 [../automation-hub/deploy/charts/automation-hub/values-prod.yaml](../automation-hub/deploy/charts/automation-hub/values-prod.yaml) 、 [../automation-hub/deploy/charts/automation-hub/values-prod-minimal.yaml](../automation-hub/deploy/charts/automation-hub/values-prod-minimal.yaml) 、 [../automation-hub/deploy/charts/automation-hub/values-prod-external-redis.yaml](../automation-hub/deploy/charts/automation-hub/values-prod-external-redis.yaml) 、 [../automation-hub/deploy/charts/automation-hub/values-prod-docker-executor.yaml](../automation-hub/deploy/charts/automation-hub/values-prod-docker-executor.yaml) 。
- 验证口径：同一环境只对应一 套 values 组合，`live` 与 `live-worker` 能按固定组合完成 smoke 校对。
- 完成 定义：环境归属、base URL、values 组合形成单一真源，后续 release_check 不再依赖人工猜测。
- 是否可并行：否。

### M0-WP2 认证、token 与 scope 语义冻结

- 目标：固定 token 来源、scope、refresh 生命周期，以及桌面端与 worker 的认证口径。
- 依赖前置：M0-WP1。
- 涉及文件/模块： [../automation-hub/api/auth/router.py](../automation-hub/api/auth/router.py) 、 [../思忆集app/automation_hub_client.py](../思忆集app/automation_hub_client.py) 、 [../automation-hub/tests/test_api_auth_flow.py](../automation-hub/tests/test_api_auth_flow.py) 。
-  验证口径：认证流回归通过，桌面端与远端 worker 使用同一 scope 与 refresh 规则。
- 完成定义：live token 行为可解释，后续桌面同步与设备令牌不再频繁改语义。
- 是否可并行：可，与 M0-WP3 并行，但必须先有 M0-WP1 基线。

### M0-WP3 放行门禁与审计闭环

- 目标：把“服务能起”升级为“release gate、audit、artifact  都可复原”。
- 依赖前置：M0-WP1、M0-WP2。
- 涉及文件/模块： [../automation-hub/scripts/release_check.py](../automation-hub/scripts/release_check.py) 、 [../automation-hub/api/audit/router.py](../automation-hub/api/audit/router.py) 、 [../automation-hub/tests/test_release_check.py](../automation-hub/tests/test_release_check.py) 、 [../automation-hub/tests/test_api_audit_consistency.py](../automation-hub/tests/test_api_audit_consistency.py) 。
- 验证口径：release_check smoke 通过，审计事件可还原关键放行动作。
- 完成定义：至少一条 live 放行链路留有可复验 gate 输出与审计证据。
- 是否可并行：可，与 M0-WP4 的准备工作并行。

### M0-WP4 双环境验收与回滚演练

- 目标：完成 `live`、`live-worker` 双环境验收和一次真实回滚演练。
- 依赖前置：M0-WP2、M0-WP3。
- 涉及文件/模 块： [../automation-hub/scripts/release_check.py](../automation-hub/scripts/release_check.py) 、 [../automation-hub/deploy/charts/automation-hub/values-prod.yaml](../automation-hub/deploy/charts/automation-hub/values-prod.yaml) 、 [../automation-hub/deploy/charts/automation-hub/values-prod-docker-executor.yaml](../automation-hub/deploy/charts/automation-hub/values-prod-docker-executor.yaml) 。
- 验证口径：双环境 smoke、回滚演练、验收留档三件事同时成立。
- 完成定义：M0  结束后，桌面同步、Agent、多端能力都可以视为“远端已放行”。
- 是否可并行：否。

## M1 桌面日用入口稳定化

### M1-WP1 配置 schema、迁移、快照与Doctor 真源统一

- 目标：让设置页、迁移器、快照、Doctor 统一消费同一套配置语义。
- 依赖前置：M0 完成。
- 涉及文件/模块： [../思忆集app/settings_schema.py](../思忆集app/settings_schema.py) 、 [../思忆集app/ui_settings_dialog.py](../ 思忆集app/ui_settings_dialog.py) 、 [../思忆集app/app_context.py](../思忆集app/app_context.py) 、 [../思忆集app/desktop_doctor_service.py](../思忆集app/desktop_doctor_service.py) 、 [../思忆集app/tests/test_settings_schema_migration.py](../思忆集app/tests/test_settings_schema_migration.py) 、 [../思忆集app/tests/test_settings_migration_manager.py](../思忆集app/tests/test_settings_migration_manager.py) 、 [../思忆集app/tests/test_ui_settings_dialog.py](../思忆集app/tests/test_ui_settings_dialog.py) 、 [../思忆集app/tests/test_desktop_doctor.py](../思忆集app/tests/test_desktop_doctor.py) 。
- 验证口径：配置迁移、设置页、Doctor 三类测试全绿，设置值在设置页和 Doctor 中表现一致。
- 完成定义：所有高频配置键都从 settings_schema 出口治理，Doctor 只消费冻结后的配置语义。
- 是否可并行：部分可并行。

### M1-WP2 启动链路、托盘与悬浮入口稳定

- 目标：收口冷启 动、托盘驻留、关闭隐藏、主窗口恢复这条高频链路。
- 依赖前置：M1-WP1。
- 涉及文件/模块： [../思忆集app/app_context.py](../思忆集app/app_context.py) 、 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 、 [../思忆集app/ui_startup_guide_dialog.py](../思忆集app/ui_startup_guide_dialog.py) 、 [../scripts/cold_start_stability_check.py](../scripts/cold_start_stability_check.py) 、 [../思忆集app/smoke_check.py](../思忆集app/smoke_check.py) 。
- 验证口径：30 轮冷启动通过，关闭后隐藏到托盘、从托盘或悬浮入口恢复主窗口成功。
- 完成定义：桌面端不再出现“能启动但状态漂移”和“关闭即丢工作流”的问题。
- 是否可并行：可。

### M1-WP3 Doctor 结构化资产复用与 JSON 导出

- 目标：让Doctor 对话框、主窗口状态卡、导出链路共用同一份 `debug_assets`。
- 依赖前置：M1-WP1。
- 涉及文件/模块： [../思忆集app/desktop_doctor_service.py](../思忆集app/desktop_doctor_service.py) 、 [../思忆集app/ui_startup_guide_dialog.py](../思忆集app/ui_startup_guide_dialog.py) 、 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 、 [../scripts/desktop_doctor.py](../scripts/desktop_doctor.py) 、 [../思忆集app/tests/test_desktop_doctor.py](../思忆集app/tests/test_desktop_doctor.py) 、 [../思忆集app/tests/test_p2_min_acceptance.py](../思忆集app/tests/test_p2_min_acceptance.py) 。
- 验证口径：同一诊断报告在多个入口得到一致的 `hero`、`issues`、`suggestions`，CLI 可稳定导出 JSON。
- 完成定义：Doctor UI 不再 各自推导诊断结论，至少两个入口复用同一份结构化资产。
- 是否可并行：可。

### M1-WP4 主窗口第一刀解耦与依赖注入冻结

- 目标：把 MainWindow 收口成 入口壳层，先抽离上下文组装、动作分发和共享依赖注入。
- 依赖前置：M1-WP1。
- 涉及文件/模块： [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 、 [../思忆集app/app_context.py](../思忆集app/app_context.py) 、 [../思忆集app/ui_base_dialogs.py](../思忆集app/ui_base_dialogs.py) 、 [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py) 。
- 验证口径：核 心 smoke 通过；新打开的对话框通过 app_context 获取依赖，而不是沿着 parent_ref 查找业务字段。
- 完成定义：至少两类复杂职责移出MainWindow，后续新增功能默认接 服务层而不是继续加主窗口字段。
- 是否可并行：可。

### M1-WP5 工作台基 础容器与发布 DoD 收口

- 目标：做稳工作台显示、隐藏、排序、模板、恢复默认 ，并把桌面 gate 纳入发布门禁。
- 依赖前置：M1-WP2、M1-WP4。
- 涉及文件/模 块： [../思忆集app/workbench_service.py](../思忆集app/workbench_service.py) 、 [../思忆集app/workbench_layout_config.py](../思忆集app/workbench_layout_config.py) 、 [../思忆集app/workbench_card_renderer.py](../思忆集app/workbench_card_renderer.py) 、 [../思忆集app/smoke_check.py](../思忆集app/smoke_check.py) 、 [../scripts/cold_start_stability_check.py](../scripts/cold_start_stability_check.py) 、 [../automation-hub/scripts/release_check.py](../automation-hub/scripts/release_check.py) 。
- 验证口径：核心 smoke、30 轮冷启动、with-desktop-gate 放行门禁 同时通过。
- 完成定义：工作台成为最小继续入口，当前桌面版本具备可发布、可回滚、可解释的 DoD。
- 是否可并行：部分可并行。

## M2 产品主线闭环

### M2-WP1 收件模型统一与多来源收口

- 目标：把浏览器桥接、手动收件、助手 收件统一收成一套 inbox schema。
- 依赖前置：M1 完成。
- 涉及文件/模块： [../思忆集app/browser_assistant_bridge.py](../思忆集app/browser_assistant_bridge.py) 、 [../思忆集app/inbox_capture_service.py](../思忆集app/inbox_capture_service.py) 、 [../思忆集app/assistant_inbox.py](../思忆集app/assistant_inbox.py) 、 [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py)  、 [../思忆集app/tests/test_browser_assistant_bridge.py](../思忆集app/tests/test_browser_assistant_bridge.py) 、 [../思忆集app/tests/test_assistant_inbox.py](../思忆集app/tests/test_assistant_inbox.py) 。
- 验证口径：同一条输入从浏览器与桌面入口进入后字段一致，收件测试通过。
- 完成定义：收件不再按来源各走各路，后续整理、建议、同步都对齐同一模型。
- 是否可并行：否。

### M2-WP2 私人 空间 inbox、daily、insights 三层落盘

- 目标：把收件后的状态推进、归档、沉淀做成稳定状态机，而不是 UI 临时列表。
- 依赖前置：M2-WP1。
- 涉及文件/模 块： [../思忆集app/assistant_inbox.py](../思忆集app/assistant_inbox.py) 、 [../ 思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py) 、 [../思忆集app/DatabaseHandler.py](../思忆集app/DatabaseHandler.py) 、 [../思忆集app/api_sync_orchestrator.py](../思忆集app/api_sync_orchestrator.py) 、 [../思忆集app/tests/test_api_sync_orchestrator.py](../思忆集app/tests/test_api_sync_orchestrator.py) 、 [../思忆集app/tests/test_sync_services.py](../思忆集app/tests/test_sync_services.py) 。
- 验证口径：条目在 `inbox`、`daily`、`insights` 三层 之间流转后，`version`、`device_id`、`sync_state` 仍保持一致。
- 完成定义：至 少 `notes`、`personal_tasks`、`saved_articles` 三类资源能稳定进入三层模型。
- 是否可并行：可。

### M2-WP3 当前内容整理动作统一

- 目标：把“转笔 记、转任务、稍后看、忽略”收成统一整理动作，而不是散落在各个对话框里。
- 依赖 前置：M2-WP1、M2-WP2。
- 涉及文件/模块： [../思忆集app/ui_news_dialog.py](../思忆集app/ui_news_dialog.py) 、 [../思忆集app/ui_notes_dialog.py](../思忆集app/ui_notes_dialog.py) 、 [../思忆集app/ui_translate_dialog.py](../思忆集app/ui_translate_dialog.py) 、 [../思忆集app/assistant_execution.py](../思忆集app/assistant_execution.py) 、 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 。
- 验证口径：一条当前内容可通过同一动作链进入笔记、任务或稍后看，并保留 同一状态语义。
- 完成定义：不再存在每个模块各自实现一套“整理当前内容”的分叉逻辑。
- 是否可并行：可。

### M2-WP4 低打扰建议与继续入口

- 目标 ：把建议变成工作台、悬浮入口、收件卡片上的低打扰继续入口，而不是主动打断。
- 依赖前置：M2-WP2、M2-WP3。
- 涉及文件/模块： [../思忆集app/workbench_service.py](../思忆集app/workbench_service.py) 、 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 、 [../思忆集app/assistant_events.py](../思忆集app/assistant_events.py) 、 [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py) 、 [../思忆集app/tests/test_assistant_proactive_strategy.py](../思忆集app/tests/test_assistant_proactive_strategy.py) 。
- 验证口径： 建议能解释“为什么现在提醒”，可一键关闭，可转成动作，不直接打断主流程。
- 完成定义：桌面端具备“建议但不骚扰”的继续入口。
- 是否可并行：可。

### M2-WP5 同步中心与 Android 前置合同冻结

- 目标：统一同步状态、冲突摘要、最近同步时间，并冻结结构化资源字段与设备语义，为 Android 留稳定合同。
- 依赖前置：M2-WP2。
- 涉及文件/模块： [../思忆集app/api_sync_orchestrator.py](../思忆集app/api_sync_orchestrator.py) 、 [../思忆集app/automation_hub_client.py](../思忆集app/automation_hub_client.py) 、 [../思忆集app/settings_schema.py](../思忆集app/settings_schema.py) 、 [../automation-hub/api/main.py](../automation-hub/api/main.py) 、 [../automation-hub/api/schema.sql](../automation-hub/api/schema.sql) 、 [android-client-technical-design.md](android-client-technical-design.md) 、 [../思忆集app/tests/test_sync_conflict_paths.py](../思忆集app/tests/test_sync_conflict_paths.py) 。
- 验证口径：高频对话框展示统一同步摘要；冲突路径测试通过；核心资源字段语义停止漂移。
- 完成定义：Android 只需对齐合同和当前矩阵，不必反推桌面端 UI 逻辑；`user_profile/device` 等业务别名已对齐到 `user_preference/device_record`。
- 是否可并行：部分可并行。

## M3 小问统一任务入口

### M3-WP1 assistant_task 统一任务对象与总控入口

- 目标：让聊天、规则中心、定时入口、浏览器桥接统一进入 `assistant_task` 主链。
- 依赖前置：M2 完成。
- 涉及文件/模块： [../思忆集app/assistant_models.py](../思忆集app/assistant_models.py) 、 [../思忆集app/assistant_autonomy.py](../思忆集app/assistant_autonomy.py) 、 [../思忆集app/assistant_planner.py](../思忆集app/assistant_planner.py) 、 [../思忆集app/assistant_events.py](../思忆集app/assistant_events.py) 、 [../思 忆集app/browser_assistant_bridge.py](../思忆集app/browser_assistant_bridge.py)  、 [../思忆集app/tests/test_assistant_autonomy.py](../思忆集app/tests/test_assistant_autonomy.py) 、 [../思忆集app/tests/test_assistant_task_ui.py](../思忆集app/tests/test_assistant_task_ui.py) 、 [../思忆集app/tests/test_assistant_intent_router.py](../思忆集app/tests/test_assistant_intent_router.py) 。
- 验证口径：同一用户目标从聊天入口和规则中心进入后，生成同一类任务对象与状态流转。
- 完成定义：新增助手能力不再先做独立入口，而是必须先进入 `assistant_task`。
- 是否 可并行：否。

### M3-WP2 delivery_route 统一交付与最小字幕层

- 目标：把聊天区、收件箱卡片、悬浮入口、系统通知、最小字幕提示收成统一交付路由。
- 依赖前置：M3-WP1。
- 涉及文件/模块： [../思忆集app/assistant_execution.py](../思忆集app/assistant_execution.py) 、 [../思忆集app/assistant_character_runtime.py](../思忆集app/assistant_character_runtime.py) 、 [../思忆集app/assistant_inbox.py](../思忆集app/assistant_inbox.py) 、 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 、 [../思忆集app/workbench_service.py](../思忆集app/workbench_service.py) 、 [../思忆集app/tests/test_assistant_execution.py](../思忆集app/tests/test_assistant_execution.py) 、 [../思忆集app/tests/test_assistant_character_runtime.py](../思忆集app/tests/test_assistant_character_runtime.py) 。
- 验证口径：同一任务可选择交付到不同可见通道，并在至少一个字幕式提示入口上展 示进度或完成摘要。
- 完成定义：结果不再散落在日志或能力私有 UI 中，用户能稳定看到“做到了哪一步、结果去了哪里”。
- 是否可并行：可。

### M3-WP3 最小 用户画像层

- 目标：在 memory index 之上建立关注主题、来源偏好、交付偏好、安静时段、确认习惯的最小画像层。
- 依赖前置：M3-WP1。
- 涉及文件/模块： [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py)  、 [../思忆集app/assistant_memory_layer.py](../思忆集app/assistant_memory_layer.py) 、 [../思忆集app/settings_schema.py](../思忆集app/settings_schema.py) 、 [../思忆集app/tests/test_assistant_user_profile.py](../思忆集app/tests/test_assistant_user_profile.py) 、 [../思忆集app/tests/test_assistant_memory_index.py](../思忆集app/tests/test_assistant_memory_index.py) 。
- 验证口径：planner 能读取画像摘要，设置页能改交付偏好与主动性开关。
- 完成定义：画像不再混在 recall 结果里，用户可查看和修改关键偏好。
- 是否可并行：可。

### M3-WP4 受控执行 闭环与安全层串联

- 目标：让 planner、router、security、audit 共享同一条风险、授权、执行、重试链。
- 依赖前置：M3-WP1、M3-WP2。
- 涉及文件/模块： [../思忆集app/assistant_capability_router.py](../思忆集app/assistant_capability_router.py) 、 [../思忆集app/assistant_security_layer.py](../思忆集app/assistant_security_layer.py) 、 [../思忆集app/assistant_execution.py](../思忆集app/assistant_execution.py) 、 [../automation-hub/api/auth/router.py](../automation-hub/api/auth/router.py) 、 [../automation-hub/api/audit/router.py](../automation-hub/api/audit/router.py) 、 [../思忆集app/tests/test_assistant_capability_router.py](../思忆集app/tests/test_assistant_capability_router.py) 、 [../思忆集app/tests/test_assistant_runtime_guard.py](../思忆集app/tests/test_assistant_runtime_guard.py) 、 [../automation-hub/tests/test_api_audit_consistency.py](../automation-hub/tests/test_api_audit_consistency.py) 。
- 验证口径：高风险任务会进入确认或审批 路径，拒绝与失败路径都能被审计还原。
- 完成定义：没有 provider 可以绕过安全层直连执行，受控执行闭环真正成立。
- 是否可并行：可。

### M3-WP5 capability registry 读模型与 provider 统一注册

- 目标：把内建能力、插件 provider、MCP provider 收口到统一 registry 读模型。
- 依赖前置：M3-WP1。
- 涉及文 件/模块： [../思忆集app/plugin_protocol.py](../思忆集app/plugin_protocol.py) 、 [../思忆集app/assistant_capability_router.py](../思忆集app/assistant_capability_router.py) 、 [../思忆集app/assistant_planner.py](../思忆集app/assistant_planner.py) 、 [assistant-execution-framework.md](assistant-execution-framework.md) 、 [../思忆集app/tests/test_assistant_planner.py](../思忆集app/tests/test_assistant_planner.py) 、 [../思忆集app/tests/test_assistant_capability_router.py](../思忆集app/tests/test_assistant_capability_router.py) 。
- 验证口径：关闭某能力组 后 planner 不再选它；新 provider 注入后 planner 能自动发现。
- 完成定义：registry 成为能力唯一真源，UI 不再直接加底层工具入口。
- 是否可并行：可。

### M3-WP6 手机端（当前 Android）合同冻结

- 目标：只冻结配对、device、sync、token、cursor 这些未来手机端 MVP 必需合同；当前移动端落地载体仍以 Android 当 前矩阵为准，不在本轮启动 Android UI 扩面。
- 依赖前置：M2-WP5、M3-WP2、M3-WP5。
- 涉及文件/模块： [android-client-technical-design.md](android-client-technical-design.md) 、 [../思忆集app/automation_hub_client.py](../思忆集app/automation_hub_client.py) 、 [../思忆集app/api_sync_orchestrator.py](../思忆集app/api_sync_orchestrator.py) 、 [../automation-hub/api/main.py](../automation-hub/api/main.py) 、 [../automation-hub/api/schema.sql](../automation-hub/api/schema.sql)  、 [../automation-hub/tests/test_api_auth_flow.py](../automation-hub/tests/test_api_auth_flow.py) 、 [../思忆集app/tests/test_api_sync_orchestrator.py](../思忆 集app/tests/test_api_sync_orchestrator.py) 。
- 验证口径：设备与同步合同可 smoke，resource 字段、scope、cursor、tombstone 语义停止周更。
- 完成定义：手机 端 MVP 后续可在冻结合同上启动，而不是靠桌面端页面行为反推接口；当前移动端落地仍 以 [android-client-technical-design.md](android-client-technical-design.md) 当前矩阵为准，在该矩阵未升级前，不新增 Android 路由和未来页面。
- 是否可并行：可 ，但需要核心任务、交付、registry 三个接口基本冻结后进行。

## 桌面端 6 个 连续 Sprint

### Sprint 1：配置真源与Doctor 资产冻结

- 冻结 [../思忆集app/settings_schema.py](../思忆集app/settings_schema.py) 的默认值、迁移键和 隐藏键口径。
- 让 [../思忆集app/ui_settings_dialog.py](../思忆集app/ui_settings_dialog.py) 只从 schema 读取渲染与校验规则。
- 冻结 [../思忆集app/desktop_doctor_service.py](../思忆集app/desktop_doctor_service.py) 的 `debug_assets` 契约，并补齐 JSON 导出。
- 让 [../思忆集app/ui_startup_guide_dialog.py](../思忆集app/ui_startup_guide_dialog.py) 和 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 共用同一份 Doctor 资产。
- 补齐 settings/Doctor 相关测试 。
- 跑一次 [../思忆集app/smoke_check.py](../思忆集app/smoke_check.py) 的 core 基线，留配置与 Doctor 输出基准。

### Sprint 2：启动链路与主窗口第一刀

- 在入口层把 app_context 注入 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py)，停止主窗口自建核心依赖。
- 在 [../思忆集app/ui_base_dialogs.py](../思忆集app/ui_base_dialogs.py) 暴露统一的 app_context 访问方式，移除 对 `parent_ref` 业务字段的依赖。
- 把主窗口内的Doctor 结论拼接逻辑移除，改为直接消费 `debug_assets`。
- 按 [main-window-decoupling-plan.md](main-window-decoupling-plan.md) 先抽离助手记忆上下文组装。
- 固定关闭隐藏到托盘、托盘恢复 主窗口、启动后状态恢复三条高频路径。
- 跑 [../scripts/cold_start_stability_check.py](../scripts/cold_start_stability_check.py) 的 30 轮冷启动与一次 core smoke。

### Sprint 3：任务、提醒与最小仓储边界

- 清理 [../思忆集app/ui_tasks_dialog.py](../思忆集app/ui_tasks_dialog.py) 中重复定义的历史方法。
-  在 [../思忆集app/DatabaseHandler.py](../思忆集app/DatabaseHandler.py) 上先抽出 PersonalTaskRepository、ReminderRepository、SettingsRepository 适配层。
- 用 ReminderService 替代主窗口上的临时 alarms 列表，改造 [../思忆集app/ui_alarm_dialog.py](../思忆集app/ui_alarm_dialog.py) 。
- 让任务新增、编辑、完成、删除统一 经仓储与提醒服务，不再直接操作父窗口共享字段。
- 为任务与提醒链路补一条最小 smoke 回归，并固定关闭重开后的保留行为。
- 给同步中心预留统一状态接口，后续不 再让任务、笔记、新闻、翻译各自拼同步摘要。

### Sprint 4：工作台壳层与悬浮入口

- 把工作台布局状态从 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 外提到 [../思忆集app/workbench_service.py](../思忆集app/workbench_service.py) 与 [../思忆集app/workbench_layout_config.py](../思忆集app/workbench_layout_config.py) 。
- 做稳显示、隐藏、排序、模板、恢复默认五个基础布局能力。
- 让 [../思忆集app/workbench_card_renderer.py](../思忆集app/workbench_card_renderer.py) 只消费视图模型，不再自行拼业务状态。
- 给悬浮入口补“恢复主窗 口”和“显示最近同步状态”两个最小能力。
- 给悬浮入口接一个高频动作，优先快速记 笔记或快速加任务。
- 跑一次主窗口、工作台、悬浮入口联合 smoke，确认入口收口不回退。

### Sprint 5：收件、整理、建议、继续入口闭环

- 串起 [../思 忆集app/browser_assistant_bridge.py](../思忆集app/browser_assistant_bridge.py)  、 [../思忆集app/inbox_capture_service.py](../思忆集app/inbox_capture_service.py) 、 [../思忆集app/assistant_inbox.py](../思忆集app/assistant_inbox.py) 的统一收件链。
- 固定 `inbox`、`daily`、`insights` 三层状态转移与落盘规则。
- 把 [../思忆集app/ui_news_dialog.py](../思忆集app/ui_news_dialog.py) 、 [../思忆集app/ui_notes_dialog.py](../思忆集app/ui_notes_dialog.py) 、 [../思忆集app/ui_translate_dialog.py](../思忆集app/ui_translate_dialog.py) 的“整理当前内容”动作收成同一语义。
- 把建议统一投递到工作台、悬浮入口或收件卡片，默认不打断。
- 收口统一同步摘要、冲突摘要、最近同步时间，准备 Android 合同冻结。
- 跑一条浏览器收 件到继续入口的端到端桌面链路，留基准录屏或日志。

### Sprint 6：发布门禁与 M3 前置冻结

- 把桌面 gate 固定接入 [../automation-hub/scripts/release_check.py](../automation-hub/scripts/release_check.py) ，并留档输出。
- 做一次备份恢复和一次回滚演练，确认桌面端不是“只能往前不能退”。
- 冻结 `notes`、`personal_tasks`、`saved_articles`、`translation_history`、`wordbooks` 的字段语义与 sync cursor、tombstone 规则。
- 冻结 `assistant_task` 与 `delivery_route` 的最 小接口，不再让聊天、规则、桥接各自扩字段。
- 冻结 `device_id`、token scope、refresh、吊销语义，为 Android 只保留合同级准备。
- 给启动、同步、桥接三类失败 补统一错误分级和日志锚点。
- 产出一份里程碑验收包，至少包含冷启动结果、core smoke、Doctor JSON、同步冲突回归、认证流回归。

## 本周建议的连续动作

1. 在 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 接入统 一 `debug_assets`，停止主窗口自己拼 Doctor 结论。
2. 在 [../思忆集app/ui_startup_guide_dialog.py](../思忆集app/ui_startup_guide_dialog.py) 增加结构化调试资产导出入口，并沿用 CLI 同一份模型。
3. 进入 [main-window-decoupling-plan.md](main-window-decoupling-plan.md) 的下一刀，先抽离 `app_context` 访问与助手记忆上下 文组装。