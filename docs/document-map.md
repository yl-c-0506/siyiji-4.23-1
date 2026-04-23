<!-- 模块说明：仓库级文档地图，说明各专题文档的职责边界与推荐阅读顺序。 -->

# 文档地图

本文档用于解决一个现实问题：当前项目的产品、架构、客户端边界、AI 联网扩展和路线图都已经分别收口到不同专题文档里，如果没有一张总图，后续很容易再次把内容写散、写重或写冲突。

这份文档回答三个问题：

1. 每份文档各自负责什么。
2. 遇到不同问题时应该先看哪份文档。
3. 新内容以后应该补到哪里，而不是继续新增重复说明。

## 使用原则

1. 根 README 只负责仓库总览和入口，不承载完整专题细节。
2. 路线图只负责阶段目标、优先级和完成定义，不承载细化设计。
3. 产品想法、需求清单、架构边界、客户端结构、AI 扩展规则和安全设计分别维护在各自专题文档中。
4. 如果新内容已经能归到现有专题，就不要再新建平行文档。
5. 同一件事若同时涉及“是否该做”和“怎么拆结构”，先写边界文档，再写结构文档，避免直接从实现倒推产品范围。
6. Android 文档若发生冲突，固定按下面顺序裁定： [project-roadmap.md](project-roadmap.md) 与 [siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md) 的阶段门槛 -> [android-client-technical-design.md](android-client-technical-design.md) 的当前矩阵 -> [android-capability-contract-design.md](android-capability-contract-design.md) 的对象真源 -> [android-capability-architecture-adr.md](android-capability-architecture-adr.md) 与 [assistant-execution-framework.md](assistant-execution-framework.md) 的目标态约束 -> [android-client-ui-layout.md](android-client-ui-layout.md) 的交互母版。

## AI 直接开发判定顺序

当 AI 需要“直接按文档落实现”时，固定按下面顺序判定，不要跳读：

1. 先读 [project-roadmap.md](project-roadmap.md)：确认当前阶段、废弃口径和优先级。
2. 再读 [next-phase-product-boundary.md](next-phase-product-boundary.md)：确认该需求是否属于当前主线，还是延期或明确不做。
3. 再读 [app-platform-boundary-design.md](app-platform-boundary-design.md)：确认该能力属于客户端、本地自治层，还是 `automation-hub` 底座。
4. 再读 [app-client-structure-draft.md](app-client-structure-draft.md)：确认新增模块落点、迁移顺序和不应继续扩张的旧落点。
5. 触及小问代理、任务对象、能力市场或动作治理时，再读 [xiaowen-agent-layer-roadmap.md](xiaowen-agent-layer-roadmap.md) 与 [assistant-execution-framework.md](assistant-execution-framework.md)。
6. 准备真正开工时，以 [siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md) 作为工作包入口；未进入清单的未来方向，不直接扩成实现。
7. 开发 Android 或手机端功能时，必须按本页上方 Android 冲突裁定顺序执行。

直接开发时再补两条硬约束：

- [README.md](../README.md) 只作入口，不单独作为功能范围或架构真源。
- [android-client-ui-layout.md](android-client-ui-layout.md) 只作交互母版，不单独作为当前页面真源或新增路由依据。

## 代码学习主入口

- [../思忆集项目学习笔记/思忆集项目按文件学习笔记.md](../思忆集项目学习笔记/思忆集项目按文件学习笔记.md)

负责内容：

- 按文件的阅读顺序
- 关键入口文件的技术说明
- 运行与验证命令
- 后端、桌面端、同步链路三条主线的学习路线

不负责内容：

- 完整产品边界判断
- 长期路线图
- 客户端重构的详细结构草案

## 核心文档分工

### 一、仓库总览

- [README.md](../README.md)

负责内容：

- 仓库当前是什么
- 保留哪些文档入口
- 当前阶段最重要的事是什么

不负责内容：

- 完整产品设计
- 客户端结构细节
- AI 联网扩展的具体规则

### 二、阶段路线图

- [project-roadmap.md](project-roadmap.md)

负责内容：

- 阶段目标
- 推进顺序
- 完成定义
- 当前优先级判断

不负责内容：

- 具体目录结构
- 详细接口草案
- 逐项产品需求细节

### 三、桌面端产品总入口

- [../思忆集app/README.md](../思忆集app/README.md)

负责内容：

- 思忆集 app 的产品定位
- 当前两层产品定位摘要
- 模块规划
- 当前桌面端摘要
- 工作台、悬浮助手、插件体系的需求清单入口

适合什么时候看：

- 想理解这个产品到底要做什么
- 想知道当前桌面端主线是什么
- 想看可布局工作台、悬浮助手、插件体系的产品需求
- 想确认当前实际执行顺序，而不是只看模块列表

### 四、下一阶段产品边界

- [next-phase-product-boundary.md](next-phase-product-boundary.md)

负责内容：

- 当前第一期产品收口边界
- 下一阶段必须做什么
- 哪些能力可以延期
- 哪些方向当前明确不做
- 产品范围控制与优先级边界

适合什么时候看：

- 讨论某个新想法该不该进入主线
- 判断 QQ / 微信、动态监控、自动整理、自优化等能力应放在哪个阶段
- 避免产品范围再次发散

### 五、app 与底座分离总设计

- [app-platform-boundary-design.md](app-platform-boundary-design.md)

负责内容：

- app 与 `automation-hub` 的总体边界
- 本地独立模式与底座增强模式
- 模块职责分层
- 哪些能力放 app，哪些能力放底座

适合什么时候看：

- 想明确“没有底座时 app 也能工作”该怎么落地
- 想判断某个能力属于客户端还是后端
- 想确认哪些反模式必须避免，例如 UI 直接碰远端 API 或角色层绕过治理链路

### 六、客户端目录结构与接口草案

- [app-client-structure-draft.md](app-client-structure-draft.md)

负责内容：

- 客户端目标目录结构
- 模块职责拆分
- 接口草案
- 从当前文件迁移到目标结构的映射

适合什么时候看：

- 准备开始重构客户端结构
- 想知道当前文件以后应该迁到哪里
- 想定义 `AppContext`、工作台、插件、同步等接口
- 想确认当前最值得先拆的巨型文件和迁移顺序

### 七、桌面端日常可用化交付基线

- [siyi-desktop-delivery-plan-2026-04.md](siyi-desktop-delivery-plan-2026-04.md)

负责内容：

- 当前桌面端 P2-P3 交付节奏
- 设置治理、启动稳定性、布局收口和桌面 Doctor 的完成定义
- 当前轮次测试补强优先级

适合什么时候看：

- 准备排当前迭代
- 想知道桌面端这轮到底以什么算完成
- 想知道测试资源先投哪里

### Android 客户端文档栈

- [android-client-technical-design.md](android-client-technical-design.md)
- [android-capability-contract-design.md](android-capability-contract-design.md)
- [android-capability-architecture-adr.md](android-capability-architecture-adr.md)
- [android-client-ui-layout.md](android-client-ui-layout.md)

负责内容：

- Android 当前可开发切片、当前 API 真相、当前页面集合
- Android 对象命名、业务别名、对象状态矩阵
- Android 目标态运行时与能力分层约束
- Android 交互母版、视觉语言和未来页面方向

适合什么时候看：

- 想判断 Android 当前到底能直接开发什么
- 想知道某个对象是否只是冻结合同，还是已经允许落地
- 想区分“当前信息架构”和“未来 UI 母版”
- 想避免把旧 `/mobile/*` 草案或未来文件云误当成当前实现要求

不负责内容：

- Android 之外的桌面端主线排期
- 自动化执行域的服务设计
- 浏览器扩展、联网扩展等其他专题的细节

### 八、小问角色规划

- [xiaowen-character-assistant-plan.md](xiaowen-character-assistant-plan.md)

- [xiaowen-agent-layer-roadmap.md](xiaowen-agent-layer-roadmap.md)

负责内容：

- 小问的正确主线
- 统一事件入口、字幕层、主动说话、工具注册表与表现层的先后顺序
- 角色层与工作台、悬浮助手、治理层之间的关系
- 小问如何从桌面助手收口为统一任务入口
- “小问代理层 + 能力市场”的两层定位、第一期收口和第二/第三期路线

适合什么时候看：

- 讨论小问到底先做什么
- 判断桌宠表现层是否该优先投入
- 设计角色运行时边界
- 设计统一任务入口、结果交付和用户画像层

### 九、浏览器扩展与悬浮辅助现状

- [browser-extension-floating-assistant-status.md](browser-extension-floating-assistant-status.md)

负责内容：

- 浏览器扩展和悬浮辅助当前成熟度
- 当前缺口与主线关系
- 两条线的下一步优先级和不建议先做的事

适合什么时候看：

- 想判断浏览器扩展该继续怎么投
- 想确认悬浮辅助先做状态承载还是先做表现层
- 想避免这两条线脱离主产品闭环单独扩张

### 十、AI 联网扩展产品规则

- [ai-networked-extension-rules.md](ai-networked-extension-rules.md)

负责内容：

- AI 联网扩展应该是什么产品能力
- 用户授权规则
- 来源规则
- 权限规则
- 产品阶段划分

适合什么时候看：

- 讨论 AI 是否应该联网装模块
- 讨论用户能授权 AI 到什么程度
- 讨论 AI 扩展的产品边界

### 十一、AI 联网扩展安全边界与技术方案

- [ai-networked-extension-security-design.md](ai-networked-extension-security-design.md)

负责内容：

- AI 联网扩展的威胁模型
- 技术控制点
- 安装、启用、配置、回滚的安全流程
- 最小放行标准

适合什么时候看：

- 准备把 AI 联网扩展做成技术实现
- 评估某个扩展流程是否安全
- 判断什么时候只能“推荐”，什么时候才能“安装”

## 推荐阅读顺序

### 场景一：第一次理解整个项目

1. [README.md](../README.md)
2. [project-roadmap.md](project-roadmap.md)
3. [../思忆集app/README.md](../思忆集app/README.md)
4. [next-phase-product-boundary.md](next-phase-product-boundary.md)

### 场景二：准备做桌面端产品规划

1. [../思忆集app/README.md](../思忆集app/README.md)
2. [next-phase-product-boundary.md](next-phase-product-boundary.md)
3. [siyi-desktop-delivery-plan-2026-04.md](siyi-desktop-delivery-plan-2026-04.md)
4. [app-platform-boundary-design.md](app-platform-boundary-design.md)
5. [app-client-structure-draft.md](app-client-structure-draft.md)

### 场景三：准备做客户端结构重构

1. [app-platform-boundary-design.md](app-platform-boundary-design.md)
2. [app-client-structure-draft.md](app-client-structure-draft.md)
3. [siyi-desktop-delivery-plan-2026-04.md](siyi-desktop-delivery-plan-2026-04.md)
4. [project-roadmap.md](project-roadmap.md)

### Android 客户端阅读顺序

1. [project-roadmap.md](project-roadmap.md)
2. [siyi-m0-m3-implementation-checklist.md](siyi-m0-m3-implementation-checklist.md)
3. [android-client-technical-design.md](android-client-technical-design.md)
4. [android-capability-contract-design.md](android-capability-contract-design.md)
5. [android-capability-architecture-adr.md](android-capability-architecture-adr.md)
6. [android-client-ui-layout.md](android-client-ui-layout.md)

### 场景四：准备做小问角色运行时

1. [xiaowen-character-assistant-plan.md](xiaowen-character-assistant-plan.md)
2. [xiaowen-agent-layer-roadmap.md](xiaowen-agent-layer-roadmap.md)
3. [../思忆集app/README.md](../思忆集app/README.md)
4. [app-platform-boundary-design.md](app-platform-boundary-design.md)
5. [project-roadmap.md](project-roadmap.md)

### 场景五：准备做浏览器扩展或悬浮辅助

1. [browser-extension-floating-assistant-status.md](browser-extension-floating-assistant-status.md)
2. [../思忆集app/README.md](../思忆集app/README.md)
3. [next-phase-product-boundary.md](next-phase-product-boundary.md)

### 场景六：准备做 AI 联网扩展

1. [ai-networked-extension-rules.md](ai-networked-extension-rules.md)
2. [ai-networked-extension-security-design.md](ai-networked-extension-security-design.md)
3. [app-platform-boundary-design.md](app-platform-boundary-design.md)

### 场景七：准备借鉴外部项目模式

适用于想从 openclaw、nanobot、syncthing、My-Neuro、七奈桌宠等参考项目中提取可复用模式时。

1. [project-roadmap.md](project-roadmap.md) — 末尾的"参考项目对标分析与借鉴（2026-04-06）"，包含对标总表、借鉴清单、执行优先级和反模式。
2. [app-client-structure-draft.md](app-client-structure-draft.md) — 末尾的"参考项目模式补充（2026-04-06）"，包含 EventBus、Theme Token、Plugin Contract、SyncResource、LLM Provider 五个接口草案。
3. [xiaowen-character-assistant-plan.md](xiaowen-character-assistant-plan.md) — 末尾的"参考项目对标补充（2026-04-06）"，包含 EmotionState、MemoryEntry、OutputSink、CharacterRenderer 和 Live2D 路径。
4. [app-platform-boundary-design.md](app-platform-boundary-design.md) — 末尾的"参考项目借鉴与安全补充（2026-04-06）"，包含浏览器桥接安全、LLM 调用安全、数据库演进和同步协议参考。
5. [next-phase-product-boundary.md](next-phase-product-boundary.md) — 新增的"参考项目反模式与约束补充（2026-04-06）"，包含产品陷阱对照表和质量债务边界。
6. [siyi-desktop-delivery-plan-2026-04.md](siyi-desktop-delivery-plan-2026-04.md) — 新增的"测试优先级矩阵（2026-04-06）"，包含 P0/P1/P2 测试目标 ROI 分级。

## 新内容应该写到哪里

### 如果是新增产品想法

- 先判断是产品定位还是具体需求。
- 产品定位和模块规划，优先补到 [../思忆集app/README.md](../思忆集app/README.md)。
- 如果是“该不该做、何时做、暂不做什么”的边界判断，优先补到 [next-phase-product-boundary.md](next-phase-product-boundary.md)。
- 阶段目标和优先级变化，补到 [project-roadmap.md](project-roadmap.md)。

### 如果是新增架构边界

- app 和底座分工，补到 [app-platform-boundary-design.md](app-platform-boundary-design.md)。
- 客户端目录和接口细化，补到 [app-client-structure-draft.md](app-client-structure-draft.md)。

### 如果是新增 Android 内容

- 当前 API、当前页面集合、当前允许开发的切片，补到 [android-client-technical-design.md](android-client-technical-design.md)。
- 对象命名、业务别名、对象状态矩阵，补到 [android-capability-contract-design.md](android-capability-contract-design.md)。
- 目标态运行时约束、控制面和能力分层，补到 [android-capability-architecture-adr.md](android-capability-architecture-adr.md)。
- 交互母版、视觉方向和未来页面，补到 [android-client-ui-layout.md](android-client-ui-layout.md)。

### 如果是新增 AI 联网扩展规则

- 产品行为和授权边界，补到 [ai-networked-extension-rules.md](ai-networked-extension-rules.md)。
- 技术控制、安全流程和放行标准，补到 [ai-networked-extension-security-design.md](ai-networked-extension-security-design.md)。

### 如果只是仓库入口变更

- 只更新 [README.md](../README.md) 和必要的入口引用，不新增平行文档。

## 当前建议维护方式

后续尽量保持下面这个层次：

- 总览： [README.md](../README.md)
- 路线： [project-roadmap.md](project-roadmap.md)
- 产品： [../思忆集app/README.md](../思忆集app/README.md)
- 产品边界： [next-phase-product-boundary.md](next-phase-product-boundary.md)
- 当前迭代交付： [siyi-desktop-delivery-plan-2026-04.md](siyi-desktop-delivery-plan-2026-04.md)
- 架构： [app-platform-boundary-design.md](app-platform-boundary-design.md)
- 结构： [app-client-structure-draft.md](app-client-structure-draft.md)
- Android 当前真相： [android-client-technical-design.md](android-client-technical-design.md)
- Android 合同真源： [android-capability-contract-design.md](android-capability-contract-design.md)
- Android 目标架构： [android-capability-architecture-adr.md](android-capability-architecture-adr.md)
- Android UI 母版： [android-client-ui-layout.md](android-client-ui-layout.md)
- 小问角色： [xiaowen-character-assistant-plan.md](xiaowen-character-assistant-plan.md)
- 浏览器/悬浮现状： [browser-extension-floating-assistant-status.md](browser-extension-floating-assistant-status.md)
- AI 产品规则： [ai-networked-extension-rules.md](ai-networked-extension-rules.md)
- AI 安全设计： [ai-networked-extension-security-design.md](ai-networked-extension-security-design.md)

如果后续再新增专题文档，优先先更新本文档，说明它负责什么，避免文档体系再次失控。
