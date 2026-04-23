# 思忆集 Android 客户端总体技术设计

本文档用于把“思忆集手机优先、桌面增强、双端自治”的路线落到当前项目可执行的技术方案上。

它不讨论 Android UI 细节优先长什么样，而是先回答四个更关键的问题：

1. Android 端在当前项目里扮演什么角色。
2. 它和桌面端、automation-hub 之间如何分工。
3. 现有代码里哪些能力可以直接复用，哪些必须新增。
4. 应该按什么顺序实现，避免范围失控。

Android 端 UI 布局与交互母版，另见 [docs/android-client-ui-layout.md](android-client-ui-layout.md)。

自 2026-04-21 起，本文档只负责 Android 端总览、角色边界、实施顺序，以及与桌面端、automation-hub 的分工，不再展开能力字段级合同。

与本文并列维护的配套文档：

- [docs/android-capability-architecture-adr.md](android-capability-architecture-adr.md)：固定“顶层助手统一控制面 + 下层能力注册调度 + 自研结构化同步”的架构决策。
- [docs/android-capability-contract-design.md](android-capability-contract-design.md)：定义能力描述协议、同步对象合同、权限分层和设计校验清单。

## 0. 当前开发门槛与判定顺序

为了让 AI 可以直接按文档开发，而不是把目标态草案误当成当前待做范围，Android 文档栈固定按下面顺序裁定冲突：

1. 阶段门槛和“能否启动 Android 正式产品化”，以 [docs/project-roadmap.md](project-roadmap.md) 和 [docs/siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md) 为准。
2. 当前可开发切片、当前 API、当前页面面，以本文第 0.2、0.3、13 节为准。
3. 对象命名、业务别名和对象状态，以 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 为准。
4. [docs/android-capability-architecture-adr.md](android-capability-architecture-adr.md) 与 [docs/assistant-execution-framework.md](assistant-execution-framework.md) 只定义目标态不可绕过约束，不代表当前已经全部落地。
5. [docs/android-client-ui-layout.md](android-client-ui-layout.md) 只定义交互母版与未来页面方向，不代表当前信息架构。

### 0.1 状态标签

- `Current`：当前代码、接口和页面已经存在，AI 可以直接据此实现、重构或补测试。
- `Transitional`：当前存在过渡链路，可局部优化，但不得当成长期真源或正式架构闭环。
- `Future`：目标态或候选合同，只冻结方向，不允许默认扩面实现。

### 0.2 M3 前允许开发的切片

在 [docs/project-roadmap.md](project-roadmap.md) 的 M3 门槛完成之前，Android 侧只允许推进下面这些切片：

- `Current`：设备接入，使用现有 API token 经 `GET /auth/me` 校验后，通过 `POST /auth/devices` 注册本机。
- `Current`：`notes`、`tasks`、`translations`、`wordbooks`、`words` 的只读拉取、本地 Room 缓存、手动刷新和同步状态展示。
- `Current`：首页快捷收件与当前 `FileTransfer` 路由只承担 “Quick Capture -> personal note” 的轻写入，不代表正式文件云或文件传输协议。
- `Transitional`：聊天页当前仍是“先走轻写入链路，再调用 `agent/ask` 取回复”的过渡实现；在 `assistant_task` 与统一 writeback 真正落地前，不得把它包装成正式统一任务入口。
- `Future`：`assistant_task`、`execution_receipt`、`inbox_item`、`continuation_card`、真正文件同步、`capability_descriptor` 运行时，以及外部 app 适配器注册表。

### 0.3 当前 API 真相矩阵

下表是 Android 当前唯一可直接依赖的服务真相；凡不在此表中的接口，一律视为 `Future` 或历史草案。

| 路径 | Android 当前用途 | 状态 | 说明 |
| --- | --- | --- | --- |
| `GET /auth/me` | 校验粘贴的 API token | `Current` | 设备接入第一步 |
| `POST /auth/devices` | 注册当前设备信息 | `Current` | 生成本地 paired state |
| `GET /personal/notes` | 笔记列表拉取 | `Current` | 首页摘要、笔记列表共用 |
| `POST /personal/notes` | Quick Capture/剪贴板写入 personal note | `Current` | 首页快捷收件与当前 `FileTransfer` 路由共用 |
| `GET /personal/tasks` | 任务列表拉取 | `Current` | 只读 |
| `GET /personal/translations` | 翻译历史拉取 | `Current` | 只读 |
| `GET /personal/wordbooks` | 单词本列表拉取 | `Current` | 只读 |
| `GET /personal/words` | 单词条目拉取 | `Current` | 只读 |
| `POST /agent/ask` | 聊天页助手回复 | `Transitional` | 当前仍未经过 `assistant_task` / `execution_receipt` |
| `GET /health` | 服务探活与诊断 | `Current` | 只返回非敏状态 |
| `GET /mobile/sync/changes` | 候选增量同步入口 | `Future` | 当前 `SyncCenter` 尚未接入，仍按资源级 refresh 汇总状态 |

补充硬规则：旧的 `/mobile/pair/*`、`/mobile/token/refresh`、`/api/mobile-ingest` 不再是当前主线接口。除非本文的当前矩阵显式升级，否则 AI 不得按这些旧路径新增调用。

## 1. 设计目标

- 保持“本地优先，云端增强”的总路线不变。
- Android 端与桌面端同属一等客户端，当前按“手机优先、桌面增强”推进，而不是继续作为桌面之后的尾端接入。
- 继续以 automation-hub 作为唯一后端底座，承接身份、同步、审计、AI 和后续文件内容云能力。
- 模型入口允许双活：手机、桌面、后端代理和后续自托管节点都可提供推理，但长期记忆、任务状态、收件箱、执行回执、偏好等可持续资产必须走同一套数据合同与同步层。
- 默认生产架构下，手机不运行 Docker；若临时启用手机直连第三方模型，也只承担认知层，不改变长期资产真源与动作治理边界。
- 第一阶段先打通结构化个人数据同步，第二阶段再接文件内容同步。

### 1.1 2026-04-20 重定位：双端自治，语义单合同

本次重定位后，Android 不再被视为“桌面端的远程壳”或“第二阶段补上的伴侣端”，而是手机优先的一等客户端。

这一定义固定四条约束：

- 手机和桌面都各自拥有本地数据库、本地模型入口和本地工作流。
- automation-hub 继续作为身份、同步、审计、备份和跨设备能力的统一脊柱，而不是唯一认知主脑。
- 可持续资产只有一套语义合同：长期记忆、任务状态、收件箱、执行回执、偏好和设备记录不允许双真源分叉。
- 第三方模型线程、临时摘要、向量索引和本地缓存都视为派生层或外部引用，不承担业务主键和长期真源职责。

### 1.2 2026-04-21 重定位：统一控制面，下层能力调度

在“手机优先、桌面增强、双端自治”的基础上，Android 端从 2026-04-21 起再固定五条实现约束：

- Android 顶层个人助手是移动端唯一控制面：聊天页、通知入口、分享入口、语音入口都先进入 Assistant Runtime，而不是各自直调底层服务。
- 下层系统能力、应用内能力和受控外部 app 适配器，统一作为 `capability` 进入注册表和动作代理，不把“已安装 app”直接等同为无约束插件。
- UI、ViewModel 和 provider 不允许绕过 `Action Broker`、统一 writeback 链路和审计回执，直接改长期资产或直接发起高风险动作。
- Android 与桌面共享同一套长期资产对象合同，但各自拥有本地模型入口、本地数据库和本地工作流；桌面端不再承担唯一主脑语义。
- 同步层由思忆集自己实现，默认只同步结构化长期资产和跨端继续所需摘要，不同步原始聊天全文、原始通知流、剪贴板原文、完整 app 清单和 provider 密钥。

重要约束：下层“受控外部 app 适配器”不等于“扫描已安装 app 并任意调用”。只有满足能力合同、可审计、可回滚、具备稳定 schema 与权限声明的适配器，才能注册为 capability；正式分类与字段口径见 [docs/android-capability-architecture-adr.md](android-capability-architecture-adr.md) 和 [docs/android-capability-contract-design.md](android-capability-contract-design.md)。

## 2. 与当前项目的关系

当前项目已经具备 Android 接入所需的几块基础，不应该推倒重来。

### 2.1 已有基础

- 桌面统一入口与应用装配： [思忆集app/思忆集test1.py](../思忆集app/思忆集test1.py) 、 [思忆集app/app_context.py](../思忆集app/app_context.py)
- 同步共性底座： [思忆集app/api_integration_hub.py](../思忆集app/api_integration_hub.py) 、 [思忆集app/api_sync_orchestrator.py](../思忆集app/api_sync_orchestrator.py)
- 远端请求收口： [思忆集app/automation_hub_client.py](../思忆集app/automation_hub_client.py)
- 权限、审计、回滚： [思忆集app/assistant_autonomy.py](../思忆集app/assistant_autonomy.py) 、 [思忆集app/audit_rollback.py](../思忆集app/audit_rollback.py)
- 设置键治理： [思忆集app/settings_schema.py](../思忆集app/settings_schema.py)
- app 与底座边界： [docs/app-platform-boundary-design.md](app-platform-boundary-design.md)
- 客户端结构草案： [docs/app-client-structure-draft.md](app-client-structure-draft.md)
- 项目路线图： [docs/project-roadmap.md](project-roadmap.md)

### 2.2 当前结论

Android 端应建立在这套既有边界上：

- app 负责本地体验、本地缓存、离线编辑和轻交互。
- automation-hub 负责身份、同步、审计、备份和跨端能力。
- 桌面端继续保留“本地控制台”和“家庭网关”角色，用于设备管理、诊断、冲突处理和高级设置。

## 3. 产品定位与范围

Android 第一版不是桌面端全量移植，也不是桌面遥控器，而是“手机优先的一等客户端 + 个人数据入口 + 轻执行节点”。

### 3.1 当前工程切片（M3 前）

当前 Android 代码面已经存在的页面与能力，固定为下面这组最小切片：

- `DevicePairing`：接入 API token、校验身份、注册设备。
- `AssistantHome`：首页摘要、资源入口、快捷收件。
- `Chat`：过渡态问答入口，当前仍走 `personal note -> agent/ask` 双链路。
- `FileTransfer`：当前只是 Quick Capture 入口，支持文本/剪贴板写入 personal note。
- `NotesList`、`TasksList`、`TranslationHistory`、`Wordbook`：统一采用只读列表 + 本地缓存。
- `SyncCenter`：资源级手动刷新、最近同步时间、失败摘要；当前不是 cursor/tombstone 完整同步控制台。

这一切片的直接目标是：先把“设备接入 + 只读资源 + 轻收件 + 过渡态问答 + 手动同步状态”做稳，而不是抢先铺正式 Android 产品化的大页面。

### 3.2 正式产品化目标（Post-M3）

- 设备配对与身份绑定
- 笔记查看与编辑
- 个人任务查看与编辑
- 翻译历史与单词本查看
- 新闻收藏与稍后读入口
- 同步状态、失败原因、手动重试
- 本地离线缓存

这里描述的是 M3 之后正式 Android 产品化要覆盖的能力，不等于当前代码已经开始实现。

### 3.3 当前明确延期

- 桌面工作台完整布局复刻
- 桌宠、悬浮角色形态
- 重型 Agent 编排与高风险动作执行
- 任意目录级“云盘式”文件同步
- 全量插件生态

### 3.4 第二阶段范围

- 业务附件与导出包同步
- 文件版本保留、回收站、断点续传
- 设备管理与远程访问增强
- 统一通知中心与跨端继续事项

### 3.5 2026-04 补充：启动前置条件与 6 个月上限

Android 端不再被视为桌面之后才启动的尾端，而是与桌面并行演进的一等客户端；但正式 Android 产品化仍依赖个人知识管理 API 与长期资产合同先冻结。因此在未来 6 个月内，正式 Android 开发必须满足下面四个前置条件：

1. `notes`、`personal_tasks`、`saved_articles`、`translation_history`、`wordbooks/words` 这几类资源的后端接口与字段语义基本冻结。
2. `device_id`、token scope、refresh 生命周期和设备吊销语义已在桌面端与底座侧跑通。
3. sync cursor、冲突策略、tombstone 删除策略不再频繁调整。
4. 桌面端已先完成“收件 -> 整理 -> 建议 -> 继续入口”的稳定闭环，不再处于高频改协议阶段。

在这些条件满足之前，Android 端只建议并行推进四类工作：

- 配对与设备信任方案原型
- 手机独立认知入口与本地 writeback pipeline 原型
- 离线缓存 / 本地队列 / 同步状态页的数据模型原型
- 客户端与后端 API 合同对齐

当前明确不建议抢先启动的内容：

- 桌面工作台完整复刻
- 小问角色 runtime 与高风险动作执行
- 开放插件生态或复杂布局系统
- 未冻结协议前的大规模页面开发

### 3.6 2026-04 补充：移动通知与轻执行副驾驶

Android 在当前阶段的新增定位，不是替代桌面端做完整主控台，也不是桌面端的遥控器，而是手机优先的一等客户端：承接“通知接收 + 本地认知 + 轻执行 + 移动继续处理”。

先落地的链路应固定为：

- Android 除消费统一的 `inbox` / `notification` 结果外，也保留本地模型入口与本地工作流，用于电脑关机时的直接对话、轻量规划和快速捕获。
- 手机直连模型产生的长期价值结果，必须先走统一 writeback 链路，再进入思忆集自己的记忆、任务、收件箱和执行回执体系。
- 桌面端或 automation-hub 继续生成每日新闻简报、提醒摘要和待处理任务。
- Android 端优先消费统一的 `inbox` / `notification` 结果，而不是单独再造一套移动推送协议。
- 新闻晨报、任务提醒、同步异常和建议卡片都应视为同一条主动结果链路，只是移动端负责更快地接住它们。

Android 第一批允许承接的动作限定为低风险、本地可回收动作：

- 标记完成
- 稍后提醒
- 保存到稍后读
- 快速追加笔记
- 创建本机闹钟或提醒
- 播放晨报或新闻摘要

以下动作继续保留在桌面端或 automation-hub：

- 重型 Agent 编排
- 高风险自动执行
- 跨系统批量修改
- 需要完整审计确认的执行链路

这意味着“每日新闻定时推送”第一版的正确实现顺序应是：

1. 先让桌面端稳定生成每日新闻简报。
2. 统一把结果投递到 `inbox` / `notification`。
3. Android 端只负责接收、展示、播放和轻执行，不重复承担内容生成。

若后续要做系统级悬浮建议，也应晚于上述闭环；第一阶段更适合先用通知深链和助手唤起层承接，而不是立即上持续悬浮窗。

## 4. 总体架构

2026-04-21 起，总体架构按“双端同构控制面 + 共享语义脊柱”收口：

```text
Android 客户端（手机优先）
  ├─ 入口层（聊天 / 通知 / 分享 / 语音 / 小组件）
  ├─ Assistant Runtime（意图、计划、风险判断）
  ├─ Action Broker / Capability Registry
  ├─ Writeback Domain（记忆 / 任务 / 收件箱 / 回执）
  ├─ Sync / Identity / Audit
  └─ Resource / Adapter 层（本地库 / 系统服务 / app 适配器 / provider）

桌面端思忆集app（桌面增强）
  ├─ 与 Android 同构的控制面与写回链路
  ├─ 重型工作台
  └─ 冲突处理与运维控制台

共享语义脊柱
  ├─ 统一长期资产对象合同
  ├─ 统一同步协议与审计回执
  └─ automation-hub 个人云 API

结构化数据云 / 文件内容云 / 审计 / 备份 / 设备管理
```

Android 能力架构的固定决策另见 [docs/android-capability-architecture-adr.md](android-capability-architecture-adr.md)。

### 4.1 角色分工

#### Android 端

- 提供移动场景的数据查看、轻写入、收件、提醒、直接对话和轻量同步；正式编辑能力按资源矩阵逐步开放。
- 本地保存缓存、离线队列、设备令牌、同步 cursor、本地工作流状态和移动端模型入口配置。
- 默认生产架构下不直接持有真实 OpenAI 或第三方服务 API Key；若为追求移动体验临时启用直连模型，也只能作为受控例外，并且结果必须回写统一数据合同。

#### 桌面端

- 继续作为重型工作台和高级控制台，而不是唯一认知主脑。
- 承担局域网配对、设备管理、同步诊断、冲突介入和桌面侧恢复能力。
- 在仅局域网方案中可临时兼任移动网关；长期仍以 automation-hub 为主后端，并承接更重的本地执行与恢复职责。

#### automation-hub

- 承接统一身份、设备、同步、审计、备份和后续文件云能力，作为双端共享的协同脊柱。
- 为 Android 与桌面提供同一套个人知识管理 API。
- 不复用自动化执行域的 task/run 模型承接个人数据，也不作为唯一认知主脑。

## 5. 数据分层策略

### 5.1 第一层：结构化个人数据云

Android V1 先冻结一组统一对象合同，并与 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 第 4 节保持一致。它们默认进入结构化同步主链，但不等于 Android 首发都要本地创建；部分对象可以先由桌面端或 automation-hub 生成，Android 首发只要求识别、展示或继续处理。

对象命名以 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 为唯一真源；路线图中的 `user_profile`、`device` 等业务别名，当前分别映射到 `user_preference`、`device_record`。

V1 合同冻结对象分为三层：

- 设备与偏好层：`device_record`, `user_preference`
- 个人内容层：`note`, `personal_task`, `journal_entry`, `saved_article`, `translation_record`, `wordbook`, `word`
- 助手与继续处理层：`memory_entry`, `inbox_item`, `assistant_task`, `execution_receipt`, `continuation_card`, `insight_card`

其中集合级资源名继续沿用当前项目的复数命名，例如 `saved_articles`、`translation_history`；对象合同在同步层统一使用单数 `saved_article`、`translation_record`。

当前 Android 支持状态与合同冻结批次分开维护：

- 当前已实现或已接入：`device_record` 的过渡映射、`note`、`personal_task`（只读）、`translation_record`（只读）、`wordbook`（只读）、`word`（只读）。
- 当前仅冻结命名与语义、不允许默认落地：`user_preference`, `saved_article`, `inbox_item`, `assistant_task`, `execution_receipt`, `continuation_card`, `insight_card`, `journal_entry`, `memory_entry`。
- AI 是否允许直接生成 API、Room 实体和页面，以 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 的对象状态矩阵为准。

这些资源继续沿用当前桌面同步骨架已经使用的字段约定：

- updated_at
- version
- deleted_at
- device_id
- sync_state
- last_synced_at

### 5.2 第二层：文件内容云

第二阶段再引入非结构化内容：

- 笔记附件
- 图片与截图
- 导出包与备份包
- 音频与文档

文件不应先做成独立网盘产品，而是作为业务对象的附件资源进入统一元数据管理。

## 6. 身份、安全与设备信任

Android 端的完整权限模型由五层门控组成：系统权限、设备信任、能力授权、动作确认、内容外发，详见 [docs/android-capability-contract-design.md](android-capability-contract-design.md)。本节只保留设备信任、令牌生命周期和移动端受控例外原则，不重复展开能力级权限。

### 6.1 核心原则

- 默认生产架构下，手机不保存真实第三方 API Key；若临时启用手机直连模型，也仅限认知层，不改变长期收口方向。
- 手机默认仅保存设备令牌和必要的刷新凭证；受控例外中的第三方模型密钥不参与平台同步，不视为设备令牌替代品。
- 任何设备都必须可吊销、可冻结、可审计。

### 6.2 推荐机制

#### 配对

- `Current`：用户在 Android 端粘贴 API token，应用先调 `GET /auth/me` 校验身份，再调 `POST /auth/devices` 注册设备。
- `Future`：二维码或短码配对可以作为正式产品化体验层，但只能建立在同一套设备合同之上，不能反向要求当前代码先实现 `/mobile/pair/*`。
- 配对后生成本地 `device_id`、`device_name`、`device_fingerprint` 视图，并写入安全存储。

#### 令牌

- `Current`：Android 当前以手动输入 API token 为主，不依赖 refresh token 生命周期。
- `Future`：正式产品化后再引入短期 access token + refresh token，但这属于设备合同后续批次，不是当前实现前置条件。
- 无论哪种模式，token 都必须绑定 `device_id` 与 scope。

#### scope 建议

以下是正式产品化阶段的建议 scope，当前不要求 Android 代码先依赖这些完整拆分：

- notes:read
- notes:write
- tasks:read
- tasks:write
- sync:pull
- sync:push
- files:upload
- files:download
- device:self

#### 吊销

- 电脑端或后台可一键吊销设备。
- 吊销后 refresh token 立即失效，access token 最多短期存活。

### 6.3 传输安全

- 同 Wi-Fi 阶段也必须使用 TLS 或至少做设备指纹校验与配对态校验。
- Android 端启用证书固定或可信指纹缓存。
- 所有 token 仅放请求头，不放 URL。

### 6.4 2026-04 补充：手机直连第三方模型的加速模式（受控例外）

当移动端体验优先级高于当前架构一致性时，可临时启用“手机直连第三方模型”的加速模式，用于尽快让手机具备接近豆包的对话、语音、图片理解和轻量规划能力。但这只能视为过渡方案，不应成为长期控制面。

此模式下必须同时满足以下约束：

- 只允许承担认知层：聊天、语音理解、图片理解、网页摘要、轻量规划；不直接承担任务真源、长期记忆真源、企业连接器和审计主链。
- 手机直连使用独立的移动专用 provider key，不复用桌面主 key，不复用 automation-hub 服务端 key。
- provider key 必须保存在系统安全存储中，不进入设置同步、备份导出、日志、截图文案或云侧 profile。
- 任何本机动作仍通过 Action Broker 或 capability registry 受控执行，先产生命令意图，再走白名单权限和必要确认，不允许模型直接跨过本机执行边界。
- 短期记忆、长期记忆、任务状态、执行记录仍写回思忆集自己的记忆与任务体系，而不是以第三方模型会话线程为真源。
- 一旦需要切换到 automation-hub 代理、自托管节点或更强设备，保留同一组 Memory API、Task API 和 Action Broker 接口，确保迁移只替换模型来源，不替换记忆与任务契约。

对于晨报、提醒摘要、收件整理等主动结果链路，移动端仍优先消费统一的 `inbox` / `notification` 投递结果；手机直连模型不等于另造第二套结果链路。

## 7. 同步模型（原则与 Android 补充能力）

同步字段级对象合同、首发对象批次、默认不同步对象和冲突映射规则，以 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 第 4 节为准。本节只保留 Android 直接需要补的同步主链原则和客户端能力，不重复展开字段级合同。

### 7.1 复用当前桌面同步主链路

Android 不另造同步模型，直接对齐现有 [思忆集app/api_sync_orchestrator.py](../思忆集app/api_sync_orchestrator.py) 的基本流程：

1. 读取 cursor
2. 拉取远端变更
3. 合并本地数据
4. 冲突入队
5. 推送本地变更
6. 更新 cursor
7. 记录审计

### 7.2 Android 端需要补的能力

- 本地离线操作队列
- 网络恢复后的重试与幂等提交
- 设备级同步状态页
- 前台与后台同步策略切换

### 7.3 冲突策略

默认不静默覆盖，支持三种策略：

- prefer_local
- prefer_remote
- manual

移动端第一版可以做轻量冲突体验：

- 默认展示“保留两份”
- 简单文本字段支持手动选择本地或远端
- 复杂冲突可提示回到桌面端处理

### 7.4 删除策略

继续沿用 tombstone 软删除，而不是物理删除。

### 7.5 事件流

参考 Syncthing 的事件 cursor 思路，并对齐当前项目审计与观察能力：

- 每条同步事件都有递增 ID 或时间 cursor
- Android 端按 cursor 增量拉取
- 仅渲染新增状态，不做全量轮询

### 7.6 2026-04-21 补充：默认不同步的派生层

为了避免 Android 端重新退化成“聊天记录镜像 + 设备遥测上送器”，以下内容默认不进入统一同步主链：

- 原始聊天全文与 provider thread/session id
- 原始通知历史与剪贴板原文
- 完整已安装 app 清单与系统遥测细项
- provider API Key、refresh token 以外的第三方凭证
- 向量索引、临时摘要、缓存键和调试日志

这些内容若后续存在跨端需要，应先提升为结构化对象或脱敏摘要，再进入统一 writeback 与同步链路；对象级默认不同步口径以 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 第 4.5 节为准。

## 8. 文件内容同步设计

文件同步不是第一阶段主线，但需要提前留接口。

### 8.1 文件能力目标

- 上传下载
- 分块传输
- 哈希校验
- 断点续传
- 版本保留
- 回收站

### 8.2 元数据模型建议

- file_assets
- file_versions
- file_chunks
- file_tombstones
- file_links

### 8.3 与业务对象的关系

- note 可以挂多个附件
- saved_article 可以挂截图或摘要导出
- translation_history 可以挂语音或结果导出
- workbench 后续可以挂导出快照

### 8.4 第一版不做

- 任意目录镜像同步
- 全量本地磁盘扫描
- 公网分享链路

## 9. Android 客户端分层建议

建议 Android 端采用以下结构：

```text
android-app/
  app/
    bootstrap/
    auth/
    sync/
    data/
    domain/
    features/
      notes/
      tasks/
      inbox/
      articles/
      translate/
      vocabulary/
      settings/
      devices/
    network/
    storage/
    workers/
```

### 9.1 技术栈建议

- Kotlin
- Retrofit + OkHttp
- Room
- WorkManager
- Android Keystore
- Jetpack Compose 或 XML 均可，优先保证可维护性

### 9.2 端内模块职责

#### auth/

- 配对
- access token / refresh token 管理
- 设备信息注册

#### sync/

- cursor 管理
- 本地变更收集
- 推拉编排
- 失败重试

#### data/

- Room 实体
- DAO
- 本地缓存与迁移

#### features/

- 各资源业务入口
- 只处理界面状态与交互

#### workers/

- 后台自动同步
- Wi-Fi、充电、电量约束

## 10. Post-M3 / Future 需要补的模块

本节描述的是 Android 正式产品化后的补全方向，不代表这些模块或接口当前已经存在。

### 10.1 桌面端

建议新增：

- mobile_gateway_service.py
- sync_center_service.py
- device_registry_service.py
- file_asset_service.py

职责：

- 承接移动端配对与局域网接入
- 统一桌面端同步状态、冲突摘要和最近同步时间
- 收口设备注册、吊销和会话状态
- 承接业务附件与版本目录

### 10.2 automation-hub

建议新增个人云相关模块：

- api/routes/personal_notes.py
- api/routes/personal_tasks.py
- api/routes/personal_articles.py
- api/routes/mobile_devices.py
- api/routes/mobile_sync.py
- api/routes/file_assets.py

要求：

- 与现有自动化执行域平行建模
- 不复用 runs / tasks 表语义
- schema.sql 同步补齐对应表

### 10.3 settings_schema

建议新增的桌面端设置键：

- mobile_sync_enabled
- mobile_gateway_enabled
- mobile_gateway_port
- mobile_pairing_mode
- mobile_allowed_networks
- mobile_sync_wifi_only
- mobile_sync_require_charging
- mobile_sync_pause_low_battery
- mobile_sync_conflict_policy
- mobile_sync_version_keep_count
- mobile_sync_version_keep_days

## 11. API 与服务真相

### 11.1 Current：当前可调用 API 矩阵

| 路径 | Android 当前用途 | 状态 | 备注 |
| --- | --- | --- | --- |
| `GET /auth/me` | 校验当前 token | `Current` | 配对第一步 |
| `POST /auth/devices` | 注册设备 | `Current` | 配对第二步 |
| `GET /personal/notes` | 拉取笔记列表 | `Current` | 首页摘要与笔记列表共用 |
| `POST /personal/notes` | Quick Capture 写入 note | `Current` | 主页快捷收件与当前 `FileTransfer` 路由共用 |
| `GET /personal/tasks` | 拉取任务列表 | `Current` | 只读 |
| `GET /personal/translations` | 拉取翻译历史 | `Current` | 只读 |
| `GET /personal/wordbooks` | 拉取单词本 | `Current` | 只读 |
| `GET /personal/words` | 拉取单词条目 | `Current` | 只读 |
| `POST /agent/ask` | 聊天页助手回复 | `Transitional` | 当前仍未进入统一任务对象 |
| `GET /health` | 探活与诊断 | `Current` | 非敏状态 |
| `GET /mobile/sync/changes` | 候选增量同步入口 | `Future` | 当前 `SyncCenter` 未接入 |

### 11.2 Future：候选合同

- `GET /mobile/sync/config`
- `GET /mobile/sync/changes?cursor=...`
- `POST /mobile/sync/push`
- `POST /mobile/sync/conflict/resolve`
- `GET /mobile/events?cursor=...`
- `POST /mobile/files/upload/init`
- `PUT /mobile/files/upload/chunk`
- `POST /mobile/files/upload/complete`
- `GET /mobile/files/download/{asset_id}`
- `POST /mobile/files/rollback`

### 11.3 历史草案处理规则

- 旧的 `/mobile/pair/*`、`/mobile/token/refresh`、`/api/mobile-ingest` 只保留为历史草案，不作为当前开发依据。
- 若其他文档仍提到这些旧接口，以本文第 0.3 节和本节为准。
- AI 不得因为看到旧路径，就自动新增 Retrofit、Room、ViewModel 或页面逻辑。

## 12. 本地数据存储演进

当前路线图已经明确，本地主存应逐步从 JSON 过渡到 SQLite。

Android 端从一开始就应以 SQLite 或 Room 为正式主存，不再重复桌面端早期的 JSON 原型路径。

桌面端也应继续按路线图推进：

- 领域仓储抽象继续保留
- LocalDataStore 逐步下沉为兼容层
- 核心资源统一切到 SQLite 主存

## 13. 当前阶段实施计划

### 13.1 M3 前允许直接开发的工作包

1. 设备接入稳固化：围绕 `auth/me`、`auth/devices`、安全存储和错误恢复补稳配对闭环。
2. 只读资源补齐：继续做 `notes`、`tasks`、`translations`、`wordbooks`、`words` 的只读拉取、本地缓存和错误态。
3. Quick Capture 收口：把首页快捷收件和当前 `FileTransfer` 路由统一解释为 Quick Capture，而不是文件云。
4. 过渡态问答拆耦：允许优化聊天页的错误恢复和本地状态，但在 `assistant_task` 真正落地前，不引入伪 capability registry。
5. 同步中心摘要：继续按资源级 refresh 汇总状态，不提前实现完整 cursor/tombstone 冲突控制台。

### 13.2 当前页面-能力矩阵

| 当前页面 / 路由名 | 当前能力 | 后端路径 | 状态 | 开发约束 |
| --- | --- | --- | --- | --- |
| `AssistantHome` | 首页摘要、快捷收件、资源入口 | `GET /personal/*`, `POST /personal/notes` | `Current` | 不扩成多标签壳 |
| `DevicePairing` | token 校验与设备注册 | `GET /auth/me`, `POST /auth/devices` | `Current` | 当前先走 token 粘贴 |
| `Chat` | 文本问答 | `POST /personal/notes`, `POST /agent/ask` | `Transitional` | 不冒充正式 `assistant_task` |
| `FileTransfer` | Quick Capture（文本/剪贴板） | `POST /personal/notes` | `Transitional` | 当前不是文件上传/下载 |
| `NotesList` | 笔记只读列表 | `GET /personal/notes` | `Current` | 不先做编辑器 |
| `TasksList` | 任务只读列表 | `GET /personal/tasks` | `Current` | 不先做写回 |
| `TranslationHistory` | 翻译历史只读列表 | `GET /personal/translations` | `Current` | 不先做在线翻译 |
| `Wordbook` | 单词本与单词只读列表 | `GET /personal/wordbooks`, `GET /personal/words` | `Current` | 不先做编辑/发音 |
| `SyncCenter` | 资源级同步摘要与手动刷新 | 逐资源 `GET /personal/*` | `Current` | 当前不是增量同步控制台 |

### 13.3 当前禁止默认扩面的内容

- 不把 `saved_article`、`user_preference`、`assistant_task`、`execution_receipt`、`inbox_item` 当成当前 Android 现成对象去实现 UI 和 API。
- 不把 `FileTransfer` 当前路由误当成文件云能力。
- 不按 UI 母版直接新建识屏页、晨报详情页、通知中心、外部 app 适配器页。
- 不因为未来合同存在，就默认增加 `/mobile/*` 或 `mobile/files/*` 调用。

## 14. Post-M3 正式产品化首批范围

只有在 [docs/project-roadmap.md](project-roadmap.md) 与 [docs/siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md) 的门槛满足后，才启动下面这批正式产品化能力：

| 批次 | 能力 | 完成定义 | 当前非目标 |
| --- | --- | --- | --- |
| B1 | `note`、`personal_task` 正式编辑 | 本地编辑 + 同步冲突摘要可解释 | 不做富文本协同 |
| B2 | `saved_article`、`user_preference`、晨报/提醒结果承接 | 有稳定对象合同与只读/轻写路径 | 不做独立资讯主页 |
| B3 | `assistant_task`、`execution_receipt`、统一写回 | 聊天、通知、分享入口进入同一对象主链 | 不做无边界自治 |
| B4 | 附件元数据与文件内容层 | 先元数据、后内容、再断点续传 | 不做云盘式目录镜像 |

## 15. Future：文件云与能力注册表

下面这些内容是目标态方向，只有在当前矩阵升级后才允许进入开发主线：

- `capability_descriptor`、`capability_invocation`、`execution_receipt` 全链路
- `saved_article`、`inbox_item`、`continuation_card`、`insight_card`
- 真正文件上传下载、断点续传、版本保留、回收站
- 受控外部 app 适配器与 capability registry 读模型
- `mobile/sync/changes`、`mobile/sync/push`、`mobile/events` 等正式增量同步协议

## 16. AI 开发前检查清单

开始任何 Android 开发前，必须先通过下面四个检查：

1. 目标能力是否在本文第 0.2 节或第 13.2 节标成 `Current` 或 `Transitional`。
2. 目标对象是否在 [docs/android-capability-contract-design.md](android-capability-contract-design.md) 里被标成 `Implemented` 或 `ReadOnly`。
3. 目标接口是否出现在本文第 0.3 节或第 11.1 节的当前矩阵中。
4. 若页面只出现在 [docs/android-client-ui-layout.md](android-client-ui-layout.md) 而不在本文第 13.2 节当前矩阵中，则默认视为 `Future`，不能直接开做。

只要以上任一条件不满足，就先回到合同冻结、命名对齐或路线图门槛，而不是直接写代码。

## 17. 关键风险与约束

### 17.1 风险

- 继续把同步逻辑散落在 UI 文件里，会导致 Android 无法复用现有主链路。
- 继续扩大 DatabaseHandler 或 JSON 主存，会拖慢多端接入。
- 如果让手机直接持有真实 API Key，会破坏后续设备治理和审计。
- 如果第一版直接做通用网盘，会挤占个人助手主线资源。

### 17.2 约束

- Android 第一版必须优先做结构化数据，不做全量文件云。
- 高风险动作仍需经过现有权限矩阵与审计链路，不允许移动端绕过。
- automation-hub 仍是唯一后端底座，不再新增平行服务。

## 18. 当前阶段建议的下一步

按优先级建议直接进入以下三个工作包：

1. 桌面端同步中心收口：先把状态、冲突和自动同步配置统一。
2. 桌面端移动接入骨架：新增 mobile gateway、device registry、settings 键。
3. automation-hub 个人云 API 骨架：先补 devices、mobile_sync、personal_notes 三类入口。

在这三步完成之前，不建议直接开始写 Android UI 大量页面，否则会先把接口边界写散。

