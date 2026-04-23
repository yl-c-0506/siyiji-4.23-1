# Android 端能力架构 ADR（2026-04-21）

## 状态

已采纳。

## 背景

Android 端已经在 [docs/android-client-technical-design.md](android-client-technical-design.md) 中被定义为一等客户端，而不是桌面端的远程壳。但当前实现仍存在“对话、写回、执行”绑在一起的问题，例如 [../思忆集app/安卓端app/source/app/src/main/java/cn/siyi/mobile/presentation/viewmodel/ChatViewModel.kt](../思忆集app/安卓端app/source/app/src/main/java/cn/siyi/mobile/presentation/viewmodel/ChatViewModel.kt) 会在发送消息时先调用 `ingestRepo.sendText()`，再请求 `agent/ask` 回复。

这会带来三个问题：

- Android 端没有真正的顶层控制面，聊天、分享、通知、快速写入仍在各走各的链路。
- “已安装 app 可被调动”这个目标没有能力合同约束，容易滑向不稳定、不可审计的直接跳转或直接自动化。
- 同步边界不清晰，容易把聊天全文、剪贴板、通知原文、完整 app 清单等派生层误塞进长期真源。

同时，现有跨端约束已经比较清楚：

- [docs/assistant-execution-framework.md](assistant-execution-framework.md) 已经要求上层围绕 `Task API`、`Action Broker`、`Capability Registry` 和统一 writeback 展开。
- [docs/app-platform-boundary-design.md](app-platform-boundary-design.md) 已经固定“双端自治、语义单合同”和隐私分级。
- [docs/xiaowen-agent-layer-roadmap.md](xiaowen-agent-layer-roadmap.md) 已经把“小问代理层 + 下层能力市场”收口为主产品结构。

本 ADR 的目的，是把这些约束正式收口到 Android 端能力架构上，形成后续移动端实现的固定边界。

## 决策摘要

Android 端采用“顶层个人助手统一控制面 + 下层能力注册与调度 + 自研结构化同步”的架构。

具体含义如下：

- 手机和桌面都各自运行同构的 Assistant Runtime，而不是让桌面端成为唯一主脑。
- Android 上所有动作都先经过顶层助手的意图解析、计划、风险判断和能力路由，再进入下层执行。
- 下层系统能力、应用内能力和外部 app 适配能力都必须以 `capability` 形式注册，而不是由 UI 直接调用。
- 长期资产只允许走统一 writeback 和同步链路；对话线程、临时摘要和缓存属于派生层。
- 同步由思忆集自己实现，并且默认只同步结构化长期资产和跨端继续所需摘要。

## 固定架构决策

### 1. Android 顶层助手是唯一控制面

Android 顶层个人助手负责：

- 统一接住聊天、通知、分享、语音、小组件、深链等入口。
- 将自然语言或多模态输入转成统一 `assistant_task`。
- 决定是否需要追问、是否需要确认、是否需要调用能力、是否需要写回长期资产。

以下路径一律不再作为正式主链：

- 页面直接调远端 API。
- ViewModel 直接串写回、执行和同步。
- provider 线程直接承担长期状态主键。

### 2. 双端同构，不设桌面唯一主脑

固定要求：

- Android 和桌面都可以拥有本地数据库、本地模型入口和本地工作流。
- 双端都允许创建 `assistant_task`，但长期记忆、任务、收件箱、执行回执、偏好和设备记录必须写回同一套对象合同。
- 桌面端继续承担重型工作台、高风险动作节点和高级控制台职责，但不承担唯一主脑语义。

### 3. Android 能力架构固定为六层

1. 入口层：聊天、通知、分享、语音、小组件、深链。
2. Assistant Runtime：意图判定、计划生成、风险分级、继续处理状态。
3. Action Broker / Capability Registry：能力发现、权限校验、能力选择、执行调度、回执标准化。
4. Writeback Domain：把结果写成笔记、任务、记忆、收件箱、日记、洞察卡、执行回执等长期对象。
5. Sync / Identity / Audit：设备身份、增量同步、冲突、删除墓碑、导出、吊销、审计。
6. Resource / Adapter 层：Room/SQLite、本地索引、系统服务、外部 app 适配器、provider、automation-hub API。

### 4. app-as-capability，但不是 app-as-plugin

Android 端借鉴“能力市场/MCP”思路，但不把“已安装 app”直接等同为可安全调用的插件。

只有满足以下条件的系统能力或外部 app 适配器，才能进入能力注册表：

- 有稳定的能力标识、输入输出结构和前置权限说明。
- 能声明风险等级、是否需要前台界面、是否可回滚、超时和失败恢复策略。
- 能产出统一 `execution_receipt`，进入审计和状态中心。

这意味着 Android 首发只适合接入少量能力簇，例如：

- 应用内原生能力：笔记、任务、收件箱、回顾、继续处理。
- 系统能力：分享、相机、文件选择、日历、提醒、通知。
- 受控外部 app 适配能力：地图搜索、浏览器打开、打车草稿、消息草稿、播放器控制。

这些自然语言分类在合同层分别映射为 `internal_domain`、`system_bridge`、`external_app_adapter`、`hub_proxy`，详见 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 第 3.3 节。

### 5. 长期资产必须先 writeback，再同步

以下对象属于长期资产真源：

- `memory_entry`
- `assistant_task`
- `inbox_item`
- `execution_receipt`
- `user_preference`
- 与个人内容相关的结构化资源，如 `note`、`personal_task`、`journal_entry`

任何模型回答、语音摘要、读屏结果、抓取结果，要成为长期价值，必须先进入统一 writeback，再同步。

以下内容默认不承担长期真源职责：

- provider thread/session id
- 原始聊天全文
- 原始通知原文
- 剪贴板原文
- 向量索引、临时摘要、缓存键

### 6. 同步采用结构化对象同步，不做镜像同步

同步固定为“语义对象 + 增量 cursor + tombstone + 幂等提交”的自研主链。

不采用以下路线：

- SQLite/JSON 文件级镜像同步
- 聊天记录全文默认同步
- 网盘式任意目录镜像作为第一阶段主线

### 7. 权限分层与隐私分级属于合同，不属于 UI 约定

能力元数据和对象元数据必须显式声明：

- Android 系统权限
- 助手能力授权
- 动作确认等级
- 数据隐私级别
- 是否允许送第三方模型

字段级定义和五层门控的默认判定矩阵，以 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 第 5 节为准。

默认原则是最小授权、最小外发、先草稿后执行、先摘要后同步。

### 8. 高风险动作默认留在桌面端或 automation-hub

Android 第一阶段允许的动作必须是低风险、可回收、可确认的动作，例如：

- 创建草稿
- 快速追加笔记
- 标记完成
- 稍后提醒
- 打开外部 app 到指定页面

以下动作默认不在 Android 首发自动执行：

- 跨系统批量修改
- 高风险自动化
- 不可回滚的外部发送或金融动作
- 通用 Accessibility 驱动自动化

### 9. 直连第三方模型是受控例外

若 Android 为改善响应体验临时直连第三方模型，该模式只允许承担认知层职责，不改变：

- `Task API`
- `Memory API`
- `Action Broker`
- 长期资产真源

具体约束以 [docs/android-client-technical-design.md](android-client-technical-design.md) 第 6.4 节和 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 第 5.6 节为准。

换言之，直连 provider 只是替换模型来源，不替换任务、写回、同步和审计契约。

## 非目标

本 ADR 明确不覆盖以下内容：

- Android UI 视觉方案与页面布局细节
- 开放第三方插件市场
- 全量目录级文件云
- 通用桌面自动化在 Android 端的复制
- 单一厂商模型的接入细节

## 影响与迁移要求

### 1. 现有聊天链路需要拆耦

当前 Android 端的“发送消息 -> 写入 personal notes -> 请求 `agent/ask`”链路需要拆开：

- 对话先进入顶层助手。
- 是否写回长期资产由 Writeback Broker 决定。
- 若只是问答，不应默认落个人笔记。

### 2. Android 能力必须先注册后可用

后续新增系统能力或 app 适配能力时，不允许直接从 UI 接到底层服务，必须先形成统一 `capability_descriptor`。

### 3. 执行回执成为必需对象

所有动作执行后都必须生成统一 `execution_receipt`，用于：

- 审计
- 跨端继续
- 失败恢复
- 用户状态中心

### 4. 同步对象合同要先冻结，再做大页面

在 `assistant_task`、`memory_entry`、`inbox_item`、`execution_receipt`、`device_record` 等对象合同稳定前，不应大规模平铺 Android 页面和能力接入。

## 开放问题

- `capability_descriptor` 首版字段集哪些必填、哪些可选。
- 外部 app 适配首发范围是否包含消息草稿以外的社交发送动作。
- 会话级授权、设备级授权和单次确认如何组合。
- 第二批何时把 `journal_entry`、`memory_entry` 从合同冻结推进到 Android 本地创建。
- 附件元数据与附件内容的同步是否分阶段上线。

字段级开放问题与对象批次细节，另见 [docs/android-capability-contract-design.md](android-capability-contract-design.md)。

## 关联文档

- [docs/android-client-technical-design.md](android-client-technical-design.md)
- [docs/android-capability-contract-design.md](android-capability-contract-design.md)
- [docs/assistant-execution-framework.md](assistant-execution-framework.md)
- [docs/app-platform-boundary-design.md](app-platform-boundary-design.md)
- [docs/xiaowen-agent-layer-roadmap.md](xiaowen-agent-layer-roadmap.md)