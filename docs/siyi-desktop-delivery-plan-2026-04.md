# 思忆集桌面端 P2-P3 交付基线（2026-04）

## 文档职责与 AI 开工边界

- 本文档只负责桌面端 P2-P3 交付基线、六周执行包和 DoD，不单独承担仓库总体产品定位或手机端优先级判断。
- 开始任何桌面端实现前，先用 [project-roadmap.md](project-roadmap.md) 和 [next-phase-product-boundary.md](next-phase-product-boundary.md) 确认该任务仍属于当前硬范围。
- 触及小问代理层、任务对象、动作治理或手机端合同冻结时，必须补读 [xiaowen-agent-layer-roadmap.md](xiaowen-agent-layer-roadmap.md) 、 [assistant-execution-framework.md](assistant-execution-framework.md) 和相关 Android 文档栈，不能只按本文件开工。
- 真正进入工作包级实现时，与本文件并行使用 [siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md)；更细的 M0-M3 拆解与当前允许切片，以实施清单为准。

当前 AI 可以直接按本文推进的范围，只限于：

- 配置真源、迁移、快照和 Doctor 统一。
- 启动链路、托盘驻留、悬浮入口和主窗口恢复稳定性。
- 工作台基础布局能力与入口状态收口。
- release gate、冷启动、备份恢复、发布演练与回滚演练。

当前不应仅凭本文直接启动的方向：

- 完整小问角色 runtime。
- Android UI 复制或手机端扩面。
- 开放插件市场、高权限联网扩展或超出基线的产品化扩张。

## 本轮收口重点（补充）

本轮交付不以“再加多少功能”为核心，而以“把桌面端收成稳定日用入口”为核心。当前建议优先聚焦四件事：

1. 配置与诊断统一：设置项统一从 [思忆集app/settings_schema.py](../思忆集app/settings_schema.py) 出口治理，设置页、迁移、快照和桌面 Doctor 使用同一套配置口径。
2. 启动与入口稳定：优先保证启动链路、托盘驻留、悬浮入口和主窗口恢复行为稳定，不再出现“能启动但状态漂移”的问题。
3. 工作台基础收口：先把显示/隐藏、排序、模板、恢复默认这类高频布局能力做稳，不先追求复杂布局器。
4. 关键耦合收口：继续把 [思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 的布局与入口逻辑外提，避免主窗口继续膨胀。

## 交付节奏（建议）

### Sprint A（5 天）

- 完成配置模型统一、迁移、设置页快照管理增强。
- 完成启动链路稳定化。
- 补齐核心布局测试。
- 补齐桌面 Doctor 对配置、桥接、同步和启动问题的统一诊断口径。

### Sprint B（5 天）

- 完成一致性交互与来源说明。
- 完成备份恢复闭环。
- 完成性能优化第一轮。
- 把工作台基础布局、悬浮入口状态反馈和最近操作提示收口为一套规则。

### Sprint C（5 天）

- 完成发布流水线与版本节奏。
- 完成埋点与错误分级。
- 完成发布演练和回滚演练。
- 对高频失败场景补齐用户提示、日志锚点和修复路径说明。

## 2026-04 至 2026-06 六周执行包（建议）

本节只作桌面端连续推进的宏观分组参考，不单独构成第二套执行真源。
真正进入实现时，依赖前置、验证口径和完成定义统一以 [siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md) 为准；本节用于帮助排连续节奏，不替代实施清单。

在本轮 P2-P3 基线不变的前提下，若按连续 6 周推进，建议固定为 4 个工作包，而不是在设置、Doctor、工作台、悬浮助手和主窗口解耦之间来回切换。

更细的 M0-M3 工作包与阶段 2 到阶段 3 的 Sprint 级拆解，统一见： [siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md) 。

### 工作包 1：配置、入口与 Doctor 统一（第 1 到 2 周）

- 范围： [../思忆集app/settings_schema.py](../思忆集app/settings_schema.py) 、 [../思忆集app/app_context.py](../思忆集app/app_context.py) 、 [../思忆集app/ui_settings_dialog.py](../思忆集app/ui_settings_dialog.py) 、 [../思忆集app/desktop_doctor_service.py](../思忆集app/desktop_doctor_service.py) 。
- 目标：统一配置口径、迁移口径、快照口径和 Doctor 诊断口径。
- 当前进度：CLI 已完成结构化调试资产 JSON 导出第一刀，见 [../scripts/desktop_doctor.py](../scripts/desktop_doctor.py) 。
- 退出标准：设置项在设置页、迁移器、快照与 Doctor 中表现一致；Doctor 结构化资产可稳定输出并支持 JSON 导出。

### 工作包 2：主窗口第一刀解耦与工作台壳层（第 2 到 3 周）

- 范围： [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py) 、 [main-window-decoupling-plan.md](main-window-decoupling-plan.md) 。
- 目标：先抽离记忆上下文组装、动作分发表和工作台入口状态，让主窗口开始只保留入口层与少量编排职责。
- 退出标准：新增业务逻辑不再直接进入主窗口；至少一类工作台或诊断逻辑转入 service/context。

### 工作包 3：工作台基础容器与悬浮入口状态（第 4 到 5 周）

- 范围：工作台显示/隐藏、排序、模板、恢复默认，以及悬浮入口状态摘要与最近操作提示。
- 目标：让桌面端先成为“继续入口”，而不是继续往首页堆更多固定模块。
- 退出标准：工作台具备最小布局能力；悬浮入口能承接至少一个高频动作和最近状态提示。

### 工作包 4：发布稳定性与回滚演练（第 6 周）

- 范围：冷启动稳定性、release 门禁、埋点、错误分级、备份恢复与发布演练。
- 目标：把本轮收口结果转成可发布、可回滚、可解释的版本。
- 退出标准：DoD 30 轮冷启动通过，release 门禁通过，至少一次发布演练与一次回滚演练留档。

## 本轮明确不抢做

- 不在本文件范围内启动完整小问角色 runtime。
- 不把 Android 端 UI 复制拉进当前桌面交付轮次。
- 不做开放插件市场或高权限联网扩展。
- 不把工作台基础布局提前拉成无限自由拖放设计器。

## 验收标准（DoD）

### 功能

- 布局相关设置全部可在设置页查看、修改、应用、重置。
- 任何默认值可解释、可恢复。
- 快照全生命周期可操作。

### 稳定性

- 连续 30 次冷启动无阻断错误。
- 核心 smoke 100% 通过。
- 关键异常都有可读提示和日志锚点。

### 体验

- 用户从打开到完成一次布局调整不超过 3 步。
- 设置页不出现“改了但不生效”场景。
- 操作反馈统一且可预期。
- 桌面 Doctor 至少能给出“能否启动、能否同步、能否桥接、能否恢复”的明确结论。

## 风险与对策

- 风险：配置键扩散导致维护成本上升。
- 对策：集中 schema + 迁移器 + 单测。

- 风险：主窗口逻辑继续膨胀。
- 对策：把布局逻辑抽成独立 service，主窗口只做调用与渲染。

- 风险：回归用例跟不上迭代。
- 对策：每新增 1 个设置项，强制新增至少 1 条 smoke 或单测。

- 风险：主窗口与对话框继续承接过多业务逻辑，后续交付速度会越来越慢。
- 对策：先补最小重构，优先把布局、入口状态和诊断逻辑从窗口文件外提到 service/context。

## 测试补强优先级（补充）

本轮若测试资源有限，建议按下面顺序补：

1. 设置模型、迁移和快照测试。
2. 主窗口布局与入口状态 smoke。
3. 浏览器桥接与桌面 Doctor 的关键诊断场景。
4. 仓储层和同步状态映射测试。

说明：当前不建议把测试资源优先投入低频外观变体；应先守住“可启动、可配置、可恢复、可诊断”。

## 执行命令基线

### 稳定性 DoD

- 30 次冷启动稳定性检查：

```powershell
python 思忆集/scripts/cold_start_stability_check.py --rounds 30 --auto-exit-ms 1200
```

### 核心回归 DoD

- 核心 UI smoke：

```powershell
python 思忆集/思忆集app/smoke_check.py --suite core
```

- 发布门禁（automation-hub smoke + 思忆集 p2）：

```powershell
python 思忆集/automation-hub/scripts/release_check.py --mode smoke --with-desktop-gate --desktop-suite p2
```

- 发布全链路门禁（automation-hub smoke + 思忆集 release）：

```powershell
python 思忆集/automation-hub/scripts/release_check.py --mode smoke --with-desktop-gate --desktop-suite release
```

## 测试优先级矩阵（2026-04-06 参考项目对标补充）

基于对 openclaw / nanobot / syncthing 测试策略的分析，结合本轮交付重点，将测试目标按 ROI 分为三级：

### P0 — 立即补齐（阻断发布）

| 测试目标 | 理由 | 预期形态 |
|----------|------|---------|
| 仓储层 CRUD（repositories） | 所有上层功能依赖数据层 | 单元测试，mock 存储后端 |
| OAuth token 刷新与过期回退 | 线上反馈过 token 失效后无法恢复 | 集成测试，模拟 401 + refresh 循环 |
| settings_schema 迁移 | 迁移器出错会导致配置丢失 | 单元测试，覆盖从旧版本到新版本全路径 |
| action_guard 白名单/黑名单 | 安全网关，错放一次就不可收回 | 单元测试，覆盖允许/拒绝/未知动作 |

### P1 — 当前 Sprint 内完成

| 测试目标 | 理由 | 预期形态 |
|----------|------|---------|
| 同步冲突路径 | 双端写冲突目前未验证 | 集成测试，模拟双写 + version 冲突 |
| 浏览器桥接 E2E | 扩展 ↔ 桌面通信是新链路 | E2E，Playwright 模拟扩展请求到本地桥 |
| 冷启动稳定性 | 本轮 DoD 核心指标 | 自动化脚本，30 轮冷启动 |
| 桌面 Doctor 诊断准确性 | Doctor 给出错误结论比不给更糟 | 单元测试，喂入各类异常返回预期诊断 |

### P2 — 下一轮迭代

| 测试目标 | 理由 | 预期形态 |
|----------|------|---------|
| 小问助手自治能力 | 当前自治功能稳定性不够，需先收口再测 | 集成测试 |
| 工作台布局变体 | 外观变化频繁，ROI 低 | 视觉回归（截图对比） |
| 插件宿主隔离 | 插件体系尚未成形 | 沙箱隔离 + 资源泄漏检测 |

### 补充说明

- syncthing 项目把所有数据安全路径（冲突、恢复、增量同步）都列为 CI 必测项，这在思忆集的同步链路上同样适用。
- openclaw 对每个 Tool（shell 执行、浏览器操作等）都有独立的权限门控测试，思忆集需要对 `action_guard` 达到同样覆盖密度。
- 测试预算有限时，遵循"先守住可启动、可配置、可恢复、可诊断"原则，不先追求低频外观变体的覆盖。

## 每日站会检查项（建议）

- 昨日新增设置项数与对应新增测试数是否 1:1。
- 冷启动稳定性最近一次结果是否通过。
- release 门禁最近一次是否通过。
- 新增异常是否具备用户提示与日志锚点。