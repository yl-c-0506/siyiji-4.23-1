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
?!