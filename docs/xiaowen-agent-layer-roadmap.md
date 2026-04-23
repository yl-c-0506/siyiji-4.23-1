<!-- 模块说明：小问从桌面助手收口为代理层的正式 路线图。 -->

# 小问代理层与能力市场路线图

本文档用于把当前关于小问的产品判断正式收口成一份可执行路线图。

它只回答四个问题：

1. 小问 在当前项目里到底是什么。
2. 哪些现有模块已经能直接复用。
3. 五个关键缺口应该按什么优先级关闭。
4. 下一阶段应该先改哪些控制点，而不是继续平铺新功能。

本文档不替代以下文档：

- [xiaowen-character-assistant-plan.md](xiaowen-character-assistant-plan.md)：回答小问作为“角色型助手”应具备的事件流、字幕层 和表现层。
- [next-phase-product-boundary.md](next-phase-product-boundary.md)：回答当前产品边界里哪些方向必须做、可延期、明确不做。
- [siyi-desktop-delivery-plan-2026-04.md](siyi-desktop-delivery-plan-2026-04.md)：回答当前桌面端交付轮次的启动、配置、布局和诊断基线。

本文档的职责是更窄也更硬的一层：

把“小问代理层 + 下层能力市场”定义成接下来 1 到 3 个阶段的主产品结构。

实 现层细节已继续拆到：

- [assistant-execution-framework.md](assistant-execution-framework.md)

## 文档职责与 AI 开工边界

- 本文档负责小问代理 层与能力市场的产品结构、阶段优先级和关键缺口排序，不单独替代仓库路线图、产品边界文档或执行框架。
- 某项能力是否属于当前主线，先以 [project-roadmap.md](project-roadmap.md) 与 [next-phase-product-boundary.md](next-phase-product-boundary.md) 为准，再回到本文判断它属于小问代理层还是下层能力市场。
- 任务对象、能力注册表、风险分级、授权和审计穿透链路的实现真源，以 [assistant-execution-framework.md](assistant-execution-framework.md) 为准。
- 真正进入开发时，以 [siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md) 作为工作包入口；本文档不单独授权未进入清单的未来角色表现层、安装型市场或高优外部推送壳层。

当前 AI 可直接落地的切片，优先只限于：

- 三类意图入口收口为 chat / execute / automate。
- 偏好真源与证据层分离。
- `inbox` / `notification`  结果交付收口。
- 能力目录摘要、治理摘要和统一 registry 读模型的第一阶段收口。

## 2026-04-20 生效定位与三期实施计划

本节是当前生效版本，优先级高于本文后续仍保留的历史阶段分析。

### 两层正式定位

思忆集当前正式收口为两层结构：

- 上层只有小问代理层，负责理解目标、跨能力编排、主动提醒和长期偏好。
- 下层只有能力市场，负责目录、权限、健康、启停和调用。

### 跨端统一代理，不再默认桌面主脑

本次重规划后，小问的正式定位还需再固定三条约束：

- 小问不是桌面独占实例；手机和桌面都可以各自运行小问实例与本地工作流。
- 手机和桌面都允许拥有本地模型入口，但长期偏好、任务、收件箱、执行回执和设备记录必须回写到同一套真源合同。
- 桌面端继续承担重型工作台、高风险执行节点和高级控制台职责，但不再承担“唯一主脑”的产品语义。

这意味着新闻、笔记、翻译、浏览器桥接、同步器、规则中心、子代理和 MCP 工具，不再各自争主入口，而是统一 降为小问可调用的能力单元。

当前主仓已经具备第一期所需的大部分骨架：

- [../思忆集app/assistant_intent_router.py](../思忆集app/assistant_intent_router.py)：统一三类意图入口。
- [../思忆集app/assistant_user_profile.py](../思忆集app/assistant_user_profile.py)：偏好真源候选。
- [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py)：统一检索证据层。
- [../思忆集app/assistant_inbox.py](../思忆集app/assistant_inbox.py)：统一结果交付通道。
- [../思忆集app/assistant_events.py](../思忆集app/assistant_events.py)：定时和事件触发。
- [../思忆集app/plugin_protocol.py](../思忆集app/plugin_protocol.py)：能力市场协议基础。
- [../思忆集app/ui_settings_dialog.py](../思忆集app/ui_settings_dialog.py)：画像偏好和能力目录摘要的现有 UI 入口。

因此，当前最该做的不是补更多功能，而是完成产品收口、真源划分和目录化呈现。

### 第一期：产品收口

目标：不加新大功能，先把小问收成唯一主入口。

必须完成：

- 统一入口固定成三类意图：聊天问答、执行任务、创建自动化。
- 把 [../思忆集app/assistant_user_profile.py](../思忆集app/assistant_user_profile.py) 设为偏好真源；把 [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py) 明确退回证据层。
- 能力市场先做目录页和治理摘要，不做安装型商店。
- 定时和主动结果统一落到 `inbox` 和 `notification` 两类主通道。
- 设置页稳定展示画像偏好和能力目录摘要。

验收标准：

- 一句话输入可 以稳定分流到 chat / execute / automate 三类链路。
- 规则输出和主动结果不再散 落到多种主通道，只走 `inbox` 和 `notification`。
- 设置页能看到画像偏好和能力目录摘要。
- 现有测试面继续成立：
	- [../思忆集app/tests/test_assistant_user_profile.py](../思忆集app/tests/test_assistant_user_profile.py)
	- [../思忆集app/tests/test_assistant_intent_router.py](../思忆集app/tests/test_assistant_intent_router.py)
	- [../思忆集app/tests/test_assistant_events.py](../思忆 集app/tests/test_assistant_events.py)
	- [../思忆集app/tests/test_autonomy_inbox_integration.py](../思忆集app/tests/test_autonomy_inbox_integration.py)

### 第二期：偏好进化与自动化中心（当前阶段明确延期）

本节只作未来阶段 参考，当前阶段不直接进入实施；真正推进时机以 [project-roadmap.md](project-roadmap.md) 与 [siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md) 的后续阶段门槛为准。

目标：让小问从“有偏好静态配置”升级到“偏好 可演化、自动化可管理”。

必须完成：

- 偏好来源、置信度和撤销路径。
- 用户反馈写回与任务模板沉淀。
- 规则创建、暂停、恢复、改时间的统一入口。
- 从自然语言到规则中心的安全建模。

验收标准：

- 每个偏好都有来 源、置信度和撤销路径。
- 自动化任务可以统一查看、暂停、恢复和改时间，不再散在多个模块里。

### 第三期：真正的能力市场（当前阶段明确延期）

本节只作未来阶段参考，当前阶段不直接进入实施；在统一能力合同与当前主线工作包未完成前，不应提前按本节扩安装型市场或开放式壳层。

目标：把下层能力从“注册表 + 摘要”升级到稳定的 Capability Descriptor 体系。

必须完成：

- 把内置能力、MCP、子代理、同步器统一成 Capability Descriptor。
- 补齐健康状态、权限声明 、启用禁用、来源分类。
- 让 planner 和目录页读取统一能力合同，而不是继续依赖 硬编码目录。

验收标准：

- 能力市场的唯一真源变成 Capability Descriptor。
- 安装型插件市场只在能力合同稳定后才进入实施，不提前做“市场壳子”。

### 当前实施约束

- 第一阶段优先级高于新能力扩张、高优外部推送和开放插件市场。
- 第二阶段优先补偏好演化和自动化中心，不提前跳到安装型市场。
- 第三阶段才进入真正的能力市场；否则会先做出壳子，没有稳定能力契约。

## 一句 话定义

小问不是桌面端里的一个聊天入口，也不是某个单一终端独占的主脑，而是思忆集跨端代理层的统一主入口。

用户面对的是小问；新闻、笔记、翻译、浏览器桥接、同步器、规则中心、子代理和 MCP 工具，都应降到下层能力市场，作为可调用、可 治理、可替换的能力单元。

## 当前判断

基于当前代码现状，项目并不缺“代理雏形”，缺的是“代理主链收口”。

当前已经存在的核心基础如下：

- [../思忆集app/assistant_planner.py](../思忆集app/assistant_planner.py)：已具备把 自然语言目标拆成 action_id 步骤的计划层雏形。
- [../思忆集app/assistant_capability_router.py](../思忆集app/assistant_capability_router.py)：已具备统一 action_id 执行路由。
- [../思忆集app/assistant_security_layer.py](../思忆集app/assistant_security_layer.py)：已具备授权、审计、风险分级和人工确认。
- [../思忆集app/assistant_events.py](../思忆集app/assistant_events.py)：已具备 daily brief、daily review、rule center 的定时和事件触发底座。
- [../思忆集app/settings_schema.py](../思忆集app/settings_schema.py)：已具备 focus topics、cron、rule center、browser bridge 等统一设置出口。
- [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py)：已具备统一可检索记忆，但当前更偏 recall，不是“用户画像层”。
- [../思忆集app/plugin_protocol.py](../思忆集app/plugin_protocol.py)：已具备 workbench card、quick action、floating assistant、data source 和 capability provider 的扩展方向。

因此，当前不应该继续把新能力并列堆进主窗口，而应该做两件事：

1. 让所有用户目标都先进入“小问代理任务”主链。
2. 让所有执行能力都退到“能力市场”一层，由小问按策略调用。

## 产品结构

建议把后续结构稳定为两层。

### 上层：小问代理层

这一层直接 面向用户，负责：

- 接住目标
- 读用户画像
- 做任务拆解
- 决定是否追问
- 决定是否调用能力
- 统一交付结果
- 记录结果并更新记忆

这层的目标不是“提供更多功能按钮”，而是“把当前功能收成一个统一入口”。

### 下层：能力市场

这一层不直接面向用户，负责提供标准化能力单元。

能力单元至少包括：

- 知识与联网能力：news.lookup、news.briefing、web.search、web.fetch、memory.recall
- 本地执行能力：file.read、clipboard.read、browser.open 、app.launch、shell.run
- 调度能力：cron.list、cron.add、cron.remove、event trigger
- 后台能力：subagent.spawn、subagent.list、subagent.get
- 外部扩展 能力：MCP 工具、插件 provider、浏览器桥接来源、后续受控外设

这层的目标不 是开放插件市场，而是先形成统一能力合同。

## 五个关键缺口与优先级

### P0：统一任务收口

这是最高优先级。

当前各入口已经能分别触发能力 ，但还没有一个对用户和系统都稳定可见的统一任务对象。

如果这层不补上，会持续出现下面的问题：

- 对话入口、规则中心、浏览器桥接和后台触发各走各的链路。
- 任务无法统一追踪状态、失败点、交付目标和复用结果。
- 小问始终像“能调 用一些工具的聊天框”，而不是任务代理。

阶段 1 必须先把所有入口收成同一类代理任务。

### P1：结果交付通道

没有稳定交付，用户就感知不到代理完成了什么。

当前项目已经能生成新闻、周报、笔记、子代理运行结果，但结果仍分散在聊天区、笔记、收件箱、日志和临时提示里。

必须补一层统一交付路由，至少先支持：

- 主窗口聊天区
- 桌面收件箱卡片
- 悬浮入口状态提示
- 系统通知
- 已有的邮件交付链路

### P2：用户画像层

当前 [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py) 已经能检索“ 记住了什么”，但还不能稳定表达“这个用户偏好什么”。

最小用户画像建议先收以 下几类：

- 关注主题
- 常用信息来源
- 默认结果交付方式
- 安静时段与主动提醒容忍度
- 输出风格偏好
- 高风险动作的确认习惯

这一层不应该直接塞进 memory index，而应该建立在它之上。

### P3：联网搜集质量

 当前联网能力已经从“单次搜索”升级到“本地记忆 + 多轮联网 + 缓存 + 去重”的组合路径 ，方向是对的。

但它还缺少正式的质量门控，例如：

- 来源可信度排序
- 新鲜度与相关度评分
- 同题聚合与去重解释
- 失败与降级原因展示

这一层应在主链和画像层收口后再重点打磨。

### P4：主动性策略

当前 [../思忆集app/assistant_events.py](../思忆集app/assistant_events.py) 已经有定时和规则触发，但更像“后台主动执行”，还不是“面向用户的主动说话和主动交付”。

主动性必须建立在三个前提上：

1. 小问知道用户偏好什么。
2. 小问知道结果该交付到哪里。
3. 小问能区分“建议”和“打断”。

因此它应该放在这五个缺口的最 后一位。

## 四阶段路线图

### 阶段 1：收口代理主干

目标：

让小问第一次真正具备“目标 -> 规划 -> 执行 -> 交付 -> 记住”的完整闭环。

必须产出：

- 统一代理任务对象，承接聊天、规则、定时和桥接来源。
-  统一结果交付路由，把结果发到聊天区、收件箱、悬浮入口或邮件。
- 最小用户画像模型，至少覆盖关注主题、来源偏好、交付偏好和主动性开关。
- 规划层能读取画像摘要，而不是只读能力目录。

不要做：

- 不新增角色表现层。
- 不接更多新能力 provider。
- 不开始做开放插件市场。
- 不做多端协同和多人模型。

验证标准：

- 用户输入一句“帮我整理本周 AI 新闻并发我一份简报”，小问可 以走统一主链完成。
- 同一类代理任务可同时由聊天入口和规则中心入口创建。
- 交付结果不再散落在日志或内部数据里，而能稳定出现在用户可见通道。

### 阶段 2：补搜集质量与主动建议

目标：

让小问从“会查”升级到“会筛”，从“你 问我答”升级到“在合适时机提醒你看一眼”。

必须产出：

- 搜集质量门控 ：可信度、相关度、新鲜度、去重解释。
- 主动建议引擎：早晚固定提醒、积压项提醒、高价值变动提醒。
- 主动建议与普通回复共用同一套交付通道。
- 用户画像能从历史成功结果和使用频次自动更新。

不要做：

- 不做复杂推荐系统。
- 不做无边界实时监控。
- 不开放更多高权限输入源。

验证标准：

- 主动建议能说明为什么现在提醒。
- 搜集结果能解释为什么保留、为什么过滤。
- 用户可以在设置中一键关闭主动建议。

### 阶段 3：收成能力市场

目标：

把当前静态 capability catalog 逐步替换为动态能力注册表，让下层能力真正变成可注册、可分组、可治理的市场结构。

必须产出：

- 动态 capability registry。
- 内建能力、MCP 工具、插件 provider 的统一注册方式。
- 健康状态、风险等级、能力分组的统一展示与治理。
- planner 不再依赖硬编码能力目录，而改读注册表。

不要做：

- 不开放第三方插件市场。
- 不引入复杂依赖解析和远程分发。
- 不让 UI 直接绕过 registry 调底层执行器。

验证标准：

- 关闭某个能力组后，planner 不会继续选择它。
- 新 provider 注入后，planner 可以自动发现并规划使用。
- registry 成为唯一能力真源。

### 阶段 4 ：打磨日常闭环与角色体验

目标：

让小问从“可以跑通”变成“值得每天用”。

必须产出：

- 任务进度和失败重试可视化。
- 用户画像自省面板。
- 日报、周报和主动建议统一交付。
- 与角色型助手文档衔接的字幕和表现层最小闭环。

不要做：

- 不把表现层先于主链交付。
- 不让角色化外观抢占任务代理主线资源。

验证标准：

- 小问的日常高频场景不再依赖用户手动切多个模块完成。
- 用户能看懂小问为什么这么做、做到了哪一步、结果去了哪里。

## 2026-04 至 2026-09 收口边界（补充）

结合当前桌面端主线和工程现实，未来 6 个月内，小问路线不应同时把四个阶段全部拉开，而应遵守下面的串行依赖。

### 启动前置条件

1. 先完成桌面端日用入口稳定化：设置治理、启动稳定、Doctor 诊断和主窗口第一刀解耦先稳定。
2. 再完成产品主线闭环：个人动态收件箱、私人空间整理、当前内容整理和低打扰建议先形成稳定闭环。
3. 只有在“用户每天能稳定收、整理、继续”之后，小问才进入统一任务主链阶段。

### 未来 6 个月建议上限

- 以完整落地“阶段 1：收口代理主干”为硬目标。
- “阶段 2：补搜集质量 与主动建议”只推进到最小可用：可信度/相关度/新鲜度解释、主动提醒开关和不打断式交 付。
- “阶段 3：收成能力市场”只允许先形成 registry 读模型和统一能力视图，不要求完全替换所有静态目录。
- “阶段 4：打磨日常闭环与角色体验”只允许推进字幕层和最小输出表现，不抢先做 Live2D 或重角色化外观。

### 当前明确不做

- 不把小问产品化成 `openclaw` / `nanobot` 那样的多渠道消息平台。
- 不把角色表现层排在统一任务对象、交付通道和字幕层之前。
- 不在 capability registry 未形成 唯一真源前，继续向 UI文件散落新工具入口。
- 不在用户画像和交付通道未稳定前，做高频主动打断或更重的自治能力。

## 阶段 1 的核心控制点

如果只做第一阶段，建议把改动收在下面这些控制点，而不要继续分散到更多 UI 文件。

### 一、任务对象与总控入口

- [../思忆集app/assistant_models.py](../思忆集app/assistant_models.py)
- [../思忆集app/assistant_autonomy.py](../思忆集app/assistant_autonomy.py)

目标：

统一代理任务对象，统一聊天、规则、定时、桥接入口进入主链。

### 二、规划层

- [../思忆集app/assistant_planner.py](../思忆集app/assistant_planner.py)

目标：

把用户画像摘要、默认交付偏好和高价值能力提示带入规划阶段。

### 三、执行与交付层

- [../思忆集app/assistant_capability_router.py](../思忆集app/assistant_capability_router.py)
- [../思忆集app/assistant_execution.py](../思忆集app/assistant_execution.py)

目标：

继续保持 capability router 只负责能力执行，把统一 交付路由放到执行层或邻近服务层，不再塞进具体能力实现里。

### 四、安全与治理层

- [../思忆集app/assistant_security_layer.py](../思忆集app/assistant_security_layer.py)
- [../思忆集app/settings_schema.py](../思忆集app/settings_schema.py)

目标：

把用户画像偏好、默认交付方式和主动性开关收进统一配置出口，并明确哪些任务类型允许默认自动完成、哪些仍要确认。

### 五、记忆与画像层

- [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py)
- [../思忆集app/assistant_memory_layer.py](../思忆集app/assistant_memory_layer.py)

目标：

保持 memory index 做统一检索；在其上建立更稳定的用户画像层，而不是让 recall 结构继续承担全部“记住用户”的职责。

### 2026-04 补充：数据主权与真源划分

围绕小问代理层，当前必须把“什么 是证据层，什么是真源层”写死，否则后续一旦切换模型、移动入口或云端运行形态，画像 与记忆会重新漂散。

固定原则：

- [../思忆集app/assistant_memory_index.py](../思忆集app/assistant_memory_index.py) 继续承担统一检索证据层，负责 recall、召回、摘要索引和证据拼装，但不再被视为用户偏好、任务状态或设备状态的唯一真源。
- [../思忆集app/assistant_user_profile.py](../思忆集app/assistant_user_profile.py) 负责偏好真源，至少承接交付偏好、安静时段、来源偏好、确认习惯和关注主题 。
- 任务状态、执行历史、设备能力和审计记录必须进入独立真源对象，而不是继续散落在模型线程、UI 临时状态、日志文本或移动缓存里。
- 第三方模型会话线程、外部 向量索引和手机本地缓存都只能算派生层或缓存层，不能直接承担 `memory_id`、`task_id`、`device_id`、`audit_id` 的主键职责。
- 小问后续无论接 Kimi、OpenAI、手机直连 provider，还是切到自托管推理，用户真正长期保留的资产都必须仍然回写到思忆集自 己的记忆、任务和偏好体系。

这一层的长期目标不是“让小问更会记”，而是“让小 问记住的东西不会因为模型、入口或设备换代而丢失语义”。

## 当前阶段明确不做

为了防止主线再次发散，当前阶段明确不做下面几件事：

- 不先做桌宠外观升级、Live2D 接入和复杂情绪表现。
- 不先做开放插件市场和第三方扩展生态。
- 不先做无边界实时监控和全量聊天平台化。
- 不先做多设备强一致协同。
- 不 继续把新业务逻辑直接堆进 [../思忆集app/ui_main_window.py](../思忆集app/ui_main_window.py)。

## 与现有文档的关系

如果当前目标是：

- 判断“小 问到底该先做角色层还是工具层”，先看 [xiaowen-character-assistant-plan.md](xiaowen-character-assistant-plan.md)。
- 判断“这个产品点子应不应该进入主线”，先看 [next-phase-product-boundary.md](next-phase-product-boundary.md)。
- 判断“这轮桌面端交付到底要以什么算完成”，先看 [siyi-desktop-delivery-plan-2026-04.md](siyi-desktop-delivery-plan-2026-04.md)。
- 判断“怎么把现有项目正式收成小问代理层 + 能力市场”，以本文档为准。

## 下一步执行建议

如果下一步只允许启动一个实施文档，建议从本文档继续下钻为：

1. 阶段 1 任务对象与交付路由设计稿。
2. 阶段 1 文件级改造清单与验证命令。
3. 阶段 1 用户画像最小模型说明。

顺序不要反过来。

如果先做角色表现层、复杂插件体系或更多零散能力扩展，都会重新把项目带回“功能很多，但小问不是统一入口”的旧路径。