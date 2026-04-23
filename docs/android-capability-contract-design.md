# Android 能力合同设计稿

## 1. 文档职责

本文档承接 [docs/android-capability-architecture-adr.md](android-capability-architecture-adr.md)，只回答三类实现问题：

1. Android 端的能力描述协议应该长什么样。
2. 长期资产与跨端继续所需的同步对象合同应该怎么定义。
3. Android 端权限分层、动作确认和外发边界应该怎么建模。

本文档不讨论 UI 布局和视觉细节；它服务于运行时、同步层、写回层和能力适配层的实现。

在 Android 文档栈里，本文档同时承担两项额外职责：

- 它是 Android 对象命名与业务别名的唯一真源。
- 它决定某个对象当前是 `Implemented`、`ReadOnly` 还是 `Reserved`；只有 `Implemented` 和 `ReadOnly` 对象，AI 才可以默认生成 API 调用、Room 实体、ViewModel 和页面。

## 2. 固定术语

- `assistant_task`：顶层助手统一任务对象。
- `capability_descriptor`：能力注册表中的标准能力描述。
- `capability_invocation`：一次能力调用请求。
- `execution_receipt`：一次能力调用或动作执行的标准回执。
- `writeback_object`：进入长期资产真源的结构化对象。
- `sync_envelope`：跨设备同步时包裹对象元数据的通用信封。
- `privacy_level`：数据隐私级别。
- `confirmation_level`：动作执行前的确认等级。

### 2.1 业务别名与合同名

不同文档中可能使用业务别名；实际实现、同步合同和对象主键一律以本表为准。

| 业务别名 | 合同名 | 说明 |
| --- | --- | --- |
| `device` | `device_record` | 路线图和工作包里常用业务简称 |
| `user_profile` | `user_preference` | 当前先冻结偏好与交付偏好，不展开完整画像对象 |
| `translation_history` | `translation_record` | 集合级资源名保持复数，对象合同用单数 |
| `saved_articles` | `saved_article` | 集合级资源名保持复数，对象合同用单数 |
| `quick_capture` | `note` | 当前 Android 轻写入先沉淀为 personal note，而不是独立对象 |

若其他文档与本表冲突，以本表为准；业务文档可以继续使用别名，但实现文档不得再发明新的合同名。

## 3. 能力描述协议

### 3.1 设计目标

能力描述协议需要同时满足五个目标：

- 让 Android 顶层助手能在运行时发现和选择能力。
- 让 UI、ViewModel、Worker 不再绕过能力注册表直接调底层。
- 让权限、风险、外发策略成为能力元数据，而不是口头约定。
- 让每次执行都能产出统一回执并进入审计。
- 让同一能力合同未来可被桌面端、automation-hub 或其他终端复用。

### 3.2 能力对象

V1 固定三个能力层对象：

1. `capability_descriptor`
2. `capability_invocation`
3. `execution_receipt`

#### 3.2.1 capability_descriptor

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `capability_id` | 是 | 全局唯一标识，例如 `android.calendar.create_draft` |
| `version` | 是 | 合同版本 |
| `display_name` | 是 | 面向用户和日志的名称 |
| `category` | 是 | `internal_domain` / `system_bridge` / `external_app_adapter` / `hub_proxy` |
| `source` | 是 | 实现来源，例如 `android_intent`, `content_provider`, `internal_repo`, `hub_api` |
| `action_types` | 是 | 支持的动作类型列表 |
| `input_schema` | 是 | 输入结构摘要或 schema 引用 |
| `output_schema` | 是 | 输出结构摘要或 schema 引用 |
| `required_android_permissions` | 否 | 运行时权限列表 |
| `required_user_grants` | 否 | 助手侧授权列表 |
| `risk_level` | 是 | 风险等级 |
| `privacy_egress_policy` | 是 | 是否允许外发给第三方模型或外部服务 |
| `confirmation_level` | 是 | 执行前需要的确认等级 |
| `execution_mode` | 是 | `sync`, `async`, `foreground`, `background_worker` |
| `foreground_requirement` | 否 | 是否必须拉起前台界面 |
| `idempotency_class` | 是 | `safe_read`, `draft_write`, `retriable_write`, `non_retriable_side_effect` |
| `health_state` | 是 | `healthy`, `degraded`, `disabled`, `unknown` |
| `fallback_policy` | 否 | 失败时的降级策略 |
| `audit_level` | 是 | `none`, `summary`, `full` |

#### 3.2.2 capability_invocation

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `invocation_id` | 是 | 本次调用唯一 ID |
| `task_id` | 是 | 关联的 `assistant_task` |
| `capability_id` | 是 | 所调用能力 |
| `intent_summary` | 是 | 脱敏后的意图摘要 |
| `input_payload` | 是 | 结构化输入 |
| `base_object_refs` | 否 | 相关对象引用，例如 note/task/inbox item |
| `requested_by` | 是 | `chat`, `share`, `notification`, `widget`, `background_rule` |
| `requested_at` | 是 | 请求时间 |
| `confirmation_snapshot` | 否 | 本次确认结果 |
| `idempotency_key` | 是 | 幂等键 |

#### 3.2.3 execution_receipt

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `receipt_id` | 是 | 回执唯一 ID |
| `invocation_id` | 是 | 对应调用 ID |
| `task_id` | 是 | 对应任务 ID |
| `capability_id` | 是 | 能力 ID |
| `status` | 是 | `succeeded`, `failed`, `partial`, `pending_confirmation`, `unknown_side_effect` |
| `started_at` | 是 | 开始时间 |
| `ended_at` | 否 | 结束时间 |
| `result_summary` | 否 | 脱敏结果摘要 |
| `result_refs` | 否 | 生成或修改的对象引用 |
| `side_effect_level` | 是 | 副作用等级 |
| `retry_hint` | 否 | 是否允许重试以及重试方式 |
| `rollback_hint` | 否 | 是否可补偿/回滚 |
| `audit_payload` | 否 | 审计详情 |

### 3.3 能力分类

Android V1 只允许四类能力；以下自然语言分类与 ADR 第 4 条一一对应，括号内为正式 `category` 标识符：

- `internal_domain`: 应用内原生能力，例如建笔记、建任务、创建日记、写入收件箱。
- `system_bridge`: Android 系统能力，例如分享、相机、文件选择、日历、提醒、通知。
- `external_app_adapter`: 受控外部 app 适配器，例如地图搜索、浏览器打开、消息草稿、打车草稿。
- `hub_proxy`: 需要经由 automation-hub 的云侧能力。

重要约束：`external_app_adapter` 不等于“任意已安装 app”。只有具备稳定 schema、权限声明、统一回执、失败恢复和必要回滚提示的适配器，才能进入注册表。

以下能力类别暂不进入 V1：

- 通用 Accessibility 自动化
- 无 schema 的脚本执行
- 无统一回执的黑箱 app 调用

### 3.4 调用主链

固定执行主链如下：

`入口事件 -> Assistant Runtime -> assistant_task -> Capability Registry -> Action Broker -> capability_invocation -> execution_receipt -> writeback / 状态中心`

约束：

- UI 和 ViewModel 不直接执行高风险动作。
- `assistant_task` 可以不调用能力，但一旦调用，就必须留下 `capability_invocation` 和 `execution_receipt`。
- 能力执行失败时，允许生成失败回执，但不允许静默吞错。

### 3.5 失败恢复策略

根据 `idempotency_class` 区分恢复策略：

- `safe_read`：允许自动重试。
- `draft_write`：允许重试，且应优先保证不产生重复草稿。
- `retriable_write`：允许基于幂等键重试。
- `non_retriable_side_effect`：禁止盲重试，必须进入“待确认”或“待人工恢复”。

## 4. 同步对象合同

### 4.1 同步设计原则

- 只同步结构化长期资产和跨端继续所需摘要。
- 派生层、临时层、第三方线程层不承担长期真源。
- 同步主链只处理对象语义，不做数据库文件镜像。
- 每个对象都必须携带隐私、来源和版本元数据。

### 4.2 通用 sync_envelope

所有进入同步主链的对象统一包在 `sync_envelope` 中。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `object_type` | 是 | 对象类型 |
| `object_id` | 是 | 对象主键 |
| `version` | 是 | 当前版本 |
| `base_version` | 否 | 本次修改基于哪个版本 |
| `origin_device_id` | 是 | 变更来源设备 |
| `updated_at` | 是 | 更新时间 |
| `deleted_at` | 否 | 软删除时间 |
| `privacy_level` | 是 | 隐私级别 |
| `egress_policy` | 是 | 是否允许第三方模型外发 |
| `payload_hash` | 是 | 载荷哈希 |
| `sync_policy` | 是 | `append_only`, `mergeable`, `manual_conflict`, `local_only_shadow` |
| `content_ref` | 否 | 附件或外部大对象引用 |

### 4.3 V1 合同冻结对象

V1 先冻结以下对象类型；它们默认进入结构化同步主链，但不等于 Android 首发都要本地创建。若某对象由桌面端或 automation-hub 先生成，Android 首发至少要能识别、展示或消费。

| 对象 | 作用 | 默认同步 | Android 合同批次 | 当前支持状态 | 当前实现说明 |
| --- | --- | --- | --- | --- | --- |
| `device_record` | 设备身份、能力摘要、吊销状态 | 是 | 首发读写 | `Implemented` | 当前已存在 token 校验 + 设备注册 + 本地 paired state，但还不是完整同步对象 |
| `user_preference` | 偏好、静默时段、提醒容忍度、默认交付方式 | 是 | 首发读写 | `Reserved` | 先冻结命名与语义，不默认生成 Android 本地实体或页面 |
| `note` | 笔记与结构化摘录 | 是 | 首发读写 | `Implemented` | 当前支持只读拉取与 Quick Capture 写入 |
| `personal_task` | 任务、提醒、任务状态 | 是 | 首发读写 | `ReadOnly` | 当前 Android 只有列表拉取与本地缓存 |
| `saved_article` | 稍后读与结构化文章引用 | 是 | 首发读取 | `Reserved` | 当前 Android 无 API、无页面、无 Room 实体 |
| `translation_record` | 翻译历史条目 | 是 | 首发读取 | `ReadOnly` | 当前 Android 已接只读拉取与本地缓存 |
| `wordbook` | 单词本容器 | 是 | 首发读取 | `ReadOnly` | 当前 Android 已接只读拉取与本地缓存 |
| `word` | 单词条目与释义沉淀 | 是 | 首发读取 | `ReadOnly` | 当前 Android 已接只读拉取与本地缓存 |
| `inbox_item` | 收件箱条目、待处理建议卡片 | 是 | 首发消费 | `Reserved` | 当前 Android 未直接消费统一 inbox 对象 |
| `assistant_task` | 跨端继续处理的任务对象 | 是 | 首发消费 | `Reserved` | 当前聊天页仍是过渡链路，不得冒充已落地任务对象 |
| `execution_receipt` | 执行回执摘要 | 是 | 首发消费 | `Reserved` | 当前 Android 未生成统一执行回执 |
| `continuation_card` | 跨端继续卡片 | 是 | 首发消费 | `Reserved` | 当前 Android 未接该对象 |
| `insight_card` | 日报/周报/回顾生成的可读成果 | 是 | 首发消费 | `Reserved` | 当前 Android 未接该对象 |
| `journal_entry` | 日记条目与生活记录 | 是 | 第二批读写 | `Reserved` | 当前 Android 未接该对象 |
| `memory_entry` | 长期记忆条目 | 是 | 第二批读写 | `Reserved` | 当前 Android 未接该对象 |

说明：集合级资源名若沿用 `saved_articles`、`translation_history` 这类复数集合，`object_type` 在同步合同里统一使用单数 `saved_article`、`translation_record`。

补充规则：

- `Implemented`：当前允许 AI 直接围绕现有接口和数据模型实现、重构、补测试。
- `ReadOnly`：当前允许 AI 做拉取、缓存、展示、错误态，但不允许默认新增写回协议。
- `Reserved`：当前只冻结名字、角色和未来语义；AI 不得据此默认新增 API、Room 实体、同步逻辑或页面。

### 4.4 V1 只同步摘要或引用的对象

| 对象 | 说明 | 默认策略 |
| --- | --- | --- |
| `capture_item` | 来自分享、截图、剪贴板、通知的原始捕获 | 只同步脱敏摘要或引用 |
| `attachment_meta` | 附件元数据 | 同步元数据，不同步内容本体 |
| `activity_digest` | 设备使用记录或日回顾摘要 | 同步摘要，不同步原始轨迹 |

### 4.5 默认不同步对象

以下内容默认不进入统一同步主链：

- 原始聊天全文
- provider thread/session id
- 原始通知历史
- 剪贴板原文
- 完整 app 清单
- provider API key、第三方凭证
- 向量索引、缓存、调试日志

### 4.6 冲突策略

按对象类型固定冲突策略：

- `append_only`：`execution_receipt`, `inbox_item`, `activity_digest`
- `mergeable`：`user_preference`, `personal_task` 的轻字段状态，`continuation_card`
- `manual_conflict`：`note`, `journal_entry`, 富文本或复杂结构对象
- `local_only_shadow`：仅本地可见但可挂引用的对象

具体规则：

- 追加型对象不覆盖，只追加。
- 轻状态字段允许最后写入者生效，但必须保留版本。
- 富文本对象冲突时默认保留双版本，由用户或桌面端合并。
- 删除统一走 tombstone，不做物理删除直推。

## 5. 权限分层

### 5.1 五层权限模型

Android 端固定五层门控：

1. 系统权限层：Android 运行时权限，例如日历、通知、文件、相机。
2. 设备信任层：设备是否已配对、是否被吊销、是否在受信网络环境。
3. 能力授权层：用户是否允许助手调用某个 capability。
4. 动作确认层：本次动作是否需要逐次确认。
5. 内容外发层：本次输入或相关对象是否允许送第三方模型或外部服务。

任何一层未通过，能力都不进入实际执行。

### 5.2 风险等级

V1 固定四档风险等级：

| 风险等级 | 说明 | 默认执行策略 |
| --- | --- | --- |
| `R1_READ` | 只读查询、检索、摘要 | 自动执行 |
| `R2_DRAFT` | 创建草稿、创建本地待确认对象 | 自动执行或一次性授权 |
| `R3_REVERSIBLE_WRITE` | 可回滚写入，如本地任务、日历草稿 | 默认确认 |
| `R4_IRREVERSIBLE_SIDE_EFFECT` | 发送、支付、外部不可回滚副作用 | Android 首发不自动执行 |

### 5.3 确认等级

| 确认等级 | 说明 |
| --- | --- |
| `none` | 不需要额外确认 |
| `session` | 当前会话内同类动作免确认 |
| `per_action` | 每次动作都需要确认 |
| `blocked_on_mobile` | 移动端禁止直接执行 |

### 5.4 隐私级别

沿用平台隐私分级，但在 Android 端落为对象元数据：

| 隐私级别 | 含义 |
| --- | --- |
| `local_only` | 仅本地，不同步，不外发 |
| `syncable` | 可同步，不默认分享，不默认外发 |
| `shareable` | 可在显式操作下分享或导出 |
| `model_egress_allowed` | 允许送第三方模型 |

约束：

- `syncable` 不等于 `model_egress_allowed`。
- 未标记为 `model_egress_allowed` 的内容，不允许默认送第三方模型。
- 高敏对象默认 `local_only` 或 `syncable`，需要单独升格。

### 5.5 默认判定矩阵

| 条件 | 判定 |
| --- | --- |
| 只读 + 非敏内容 + 已授权能力 | 自动执行 |
| 草稿写入 + 已授权能力 + 可回滚 | 可自动执行或会话授权 |
| 可回滚写入 + 涉及系统资源 | 默认逐次确认 |
| 不可回滚外部副作用 | Android 默认阻断或转桌面/automation-hub |
| 对象未授权外发 | 不允许送第三方模型 |

### 5.6 手机直连第三方模型的特殊路径

当启用“手机直连第三方模型”的加速模式时（详见 [docs/android-client-technical-design.md](android-client-technical-design.md) 第 6.4 节），以下约束必须同时成立：

- provider key 只允许保存在系统安全存储中，不进入设置同步、备份导出、日志、截图文案或 `device_record`。
- 直连 provider 只替换模型来源，不替换 `assistant_task`、`execution_receipt`、`Action Broker` 和统一 writeback 链路。
- 对话结果若要成为长期价值，仍必须先进入 `writeback_object` 真源，再进入同步主链。
- `privacy_level` 和 `egress_policy` 判定不会因“走手机直连”而自动升格；未授权外发的对象仍不得送第三方模型。
- Android 消费 `inbox_item` / `notification` 的主动结果链路保持不变，直连 provider 不得另造第二套长期结果协议。

## 6. 分阶段实施建议

### 阶段 1：冻结合同和控制面

- M3 前，本阶段优先冻结命名、状态和门控规则，不默认扩 Android 页面。
- `assistant_task`、`capability_descriptor`、`execution_receipt` 可以先作为合同对象存在，但在对象状态仍为 `Reserved` 时，不默认要求 Android 代码实现。
- 聊天页“先写入再回复”的耦合链路可以继续作为过渡链路优化，但不能把过渡实现包装成正式统一任务主链。

### 阶段 2：同步 MVP

- Post-M3 再上线 `sync_envelope` 和对象级 cursor 增量同步。
- 在对象状态没有从 `Reserved` 升级之前，不默认进入同步 MVP。
- 当前 Android `SyncCenter` 仍是资源级 refresh 摘要，不等于这里的正式对象同步控制台。

### 阶段 3：受控外部 app 能力

- 按能力描述协议引入首批 `external_app_adapter`。
- 加入失败恢复、补偿提示和跨端继续。
- 评估哪些动作仍必须上收桌面端或 automation-hub。

## 7. 设计校验清单

- 新入口是否先进入 Assistant Runtime，而不是直调底层。
- 新能力是否先定义 `capability_descriptor`，再进入 UI。
- 新动作是否会生成 `execution_receipt`。
- 新对象是否声明 `privacy_level` 和 `egress_policy`。
- 新同步对象是否明确 `sync_policy` 与冲突策略。
- 新外部 app 适配是否声明风险等级、确认等级、回滚策略。

## 8. 开放问题

- 第二批何时把 `journal_entry`、`memory_entry` 从合同冻结推进到 Android 本地创建。
- `activity_digest` 的生成链路是本机生成、桌面生成还是底座生成。
- `capability_descriptor` 的 schema 最终落在 Kotlin 常量、JSON 清单还是服务端下发。
- 首批 `external_app_adapter` 白名单如何治理，是否需要单独签名或版本闸门。
- 附件内容同步与附件元数据同步是否要拆两期。