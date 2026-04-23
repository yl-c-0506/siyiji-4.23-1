<!-- 模块说明：ui_main_window.py 的分层拆分与迁移计划。 -->

# 主窗口解耦实施方案

本文档用于把“主窗口解耦方案”从口头判断收口成可执行迁移计划。

它只回答五个问题：

1. 当前主窗口为什么难继续扩展。
2. 第一批应该抽离哪些职责。
3. 哪些职责允许暂时保留在 MainWindow。
4. 每一刀迁移后如何验证不回退。
5. 迁移顺序如何避免把 UI 改成新的大泥球。

## 当前问题盘点

[../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 当前同时承接：

- 启动与引导
- Doctor 与诊断入口
- 助手运行时状态
- 工作台卡片重建
- 动作治理入口
- 悬浮助手与桌宠控制
- 多个业务对话框打开逻辑

这会持续放大三个问题：

1. 新功能只能继续堆进主窗口
2. 单测越来越依赖 UI 环境
3. 同一逻辑在主窗口、服务层、对话框之间重复出现

## 目标分层

建议把主窗口后续收口为四层：

1. 入口层：菜单、按钮、导航
2. 编排层：把用户动作路由到服务对象
3. 服务层：诊断、收件、建议、运行时、桌宠控制
4. 纯 UI 工厂层：卡片、列表、状态组件

MainWindow 最终只保留入口层和少量编排职责。

## 第一批待抽离模块

第一阶段只动四组职责：

1. Doctor 调试资产与诊断视图模型
2. 助手记忆上下文组装
3. 动作执行映射表与分发
4. 桌宠 / 悬浮入口控制

其中当前已启动第一刀：Doctor 调试资产已在服务层形成结构化导出接口。

## 当前已启动执行

2026-04-19 已落第一段：

- [../思忆集app/desktop_doctor_service.py](../思忆集app/desktop_doctor_service.py) 新增 `build_debug_assets(report)`
- 该接口为 Doctor UI 与主窗口后续复用提供稳定输入
- [../思忆集app/ui_startup_guide_dialog.py](../思忆集app/ui_startup_guide_dialog.py) 中的 `DesktopDoctorDialog` 已开始消费这份模型
- 主窗口暂时不直接消费这份模型，但后续接 UI 时不需要再在窗口层推导结论、归因、建议

这一步的意义不是“Doctor 功能又加了一点”，而是开始把一类原本可能塞回主窗口的展示逻辑提前收口到服务层。

2026-04-20 已落第二段：

- [../思忆集app/assistant_prompt_context.py](../思忆集app/assistant_prompt_context.py) 新增 `build_assistant_memory_layers(...)` 与 `load_long_term_memory_context(...)`
- [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 中的 `_build_assistant_memory_layers()` 已降为委托层，不再自己直接加载长期记忆与组装多层上下文
- [../思忆集app/tests/test_assistant_prompt_context.py](../思忆集app/tests/test_assistant_prompt_context.py) 已补纯组装器单测，先做 RED 再转 GREEN

这一步的意义不是“多了一个 helper 文件”，而是把主窗口里一段与 UI 渲染无关、但会持续膨胀提示词链路的上下文组装职责，明确下沉到独立模块，给后续 `_execute_action_key()` 和托盘/悬浮入口编排外提留出一致边界。

2026-04-20 已落第三段：

- [../思忆集app/desktop_companion_controller.py](../思忆集app/desktop_companion_controller.py) 新增 `DesktopCompanionController`，统一托盘、悬浮圆球、悬浮面板入口和桌宠情绪联动的壳层编排
- [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 中的 `_setup_system_tray()`、`_on_tray_icon_activated()`、`open_floating_assistant_dialog()`、`open_floating_assistant_panel()`、`_set_pet_mood()`、`_assistant_subtitle_anchor_point()` 已降为委托层
- [../思忆集app/tests/test_desktop_companion_controller.py](../思忆集app/tests/test_desktop_companion_controller.py) 已补统一编排器单测，覆盖托盘最小化、资源清理、悬浮圆球创建复用、面板入口委托与情绪联动

这一步的意义不是“把主窗口里几段方法换了个文件名”，而是把原来半分散在主窗口、半分散在桌宠 controller 的桌面陪伴壳层控制点，收口成单一编排边界，后续托盘行为、悬浮入口和桌宠反馈不需要再分别回到主窗口里改。

2026-04-20 已落第四段：

- [../思忆集app/assistant_action_dispatcher.py](../思忆集app/assistant_action_dispatcher.py) 新增 `AssistantActionDispatcher`，统一 `action_key` 到对话框聚焦、收件箱分支、passthrough 动作和 notify 动作的分发口径
- [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 中的 `_execute_action_key()` 已降为装配依赖并委托调用，不再自己持有整段映射表与 `inbox` 分支细节
- [../思忆集app/tests/test_assistant_action_dispatcher.py](../思忆集app/tests/test_assistant_action_dispatcher.py) 已补分发器单测，覆盖对话框 target focus、收件详情/摘要回退、passthrough 返回值和 notify 动作触发

这一步的意义不是“把 if/else 搬到另一个文件”，而是把主窗口里一段会继续膨胀的动作路由和执行分支收口为独立边界，后续新增 action_key 时优先扩展分发器契约，而不是继续把映射表塞回 `ui_main_window.py`。

2026-04-20 已落第五段：

- [../思忆集app/assistant_suggestion_planner.py](../思忆集app/assistant_suggestion_planner.py) 新增 `build_assistant_suggestions(...)` 与 `build_assistant_suggestions_meta_text(...)`，统一工作台建议和助手入口建议的编排口径
- [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 中的 `_build_suggestions()` 与建议卡片 meta 文案已降为委托层，不再自己直接拼 service 建议、fallback 建议和待审提案统计
- [../思忆集app/tests/test_assistant_suggestion_planner.py](../思忆集app/tests/test_assistant_suggestion_planner.py) 已补纯 planner 单测，覆盖能力目录置顶、service 建议去重限流、fallback 建议和 meta 文案
- [../思忆集app/tests/test_assistant_suggestion_workbench_entry.py](../思忆集app/tests/test_assistant_suggestion_workbench_entry.py) 已补工作台入口测试，锁住 `_build_suggestions()` 与 `_update_suggestions()` 经过 planner 委托后仍会正确刷新建议列表和 meta 文案

这一步的意义不是“把建议列表换个文件生成”，而是把工作台卡片和助手入口共用的一段上下文建议编排从主窗口里抽成稳定边界；后续要改建议优先级、fallback 口径或待审提案摘要，不需要再回到 `ui_main_window.py` 里改 UI 层分支。

## 允许暂时保留在 MainWindow 的职责

- 菜单动作绑定
- 对话框打开入口
- 顶层状态刷新触发
- UI 生命周期桥接

这些职责在当前阶段可以保留，但不应继续下沉业务逻辑。

## 每刀迁移的验证规则

每次抽离必须满足：

1. 先补服务层或纯函数层单测
2. 再从 MainWindow 调用新接口
3. 不允许只做“复制粘贴到新文件”而没有边界变化
4. 抽离后保留最小回退路径

## 下一步迁移顺序

1. 把新的动作分发器回接到更明确的主窗口入口测试，避免 `_execute_action_key()` 逻辑再次吸回 `ui_main_window.py`
2. 把新的壳层 controller 回接到更明确的入口测试，避免托盘/悬浮/桌宠逻辑再次吸回主窗口
3. 最后继续拆工作台与助手入口周边的剩余编排，保持主窗口只做入口层与少量路由

## 完成定义

- 主窗口不再自己做诊断资产推导
- 至少两类复杂职责从主窗口移到服务层或纯 UI 工厂层
- 新增功能优先接入服务层/插件边界，而不是继续直接进主窗口
- `ui_main_window.py` 的新增代码量开始持续下降，而不是继续上升