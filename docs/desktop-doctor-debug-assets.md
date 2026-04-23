<!-- 模块说明：桌面端 Doctor 的结构化调试资产设计与执行计划。 -->

# 桌面端可视化调试资产方案

本文档用于把“可视化调试资产”从一个抽象方向收口成可执行方案。

它只回答六个问题：

1. 哪些诊断结果应该成为稳定资产。
2. 这些资产应如何结构化，而不是继续只拼 summary 文本。
3. 哪些入口会消费这些资产。
4. 当前第一段实现已经做到哪里。
5. 后续 UI 与工作台如何复用同一份数据模型。
6. 这一条路线的完成定义是什么。

## 目标

- 让桌面 Doctor 的诊断结果既能给人看，也能给 UI 复用。
- 让主窗口、Doctor 对话框、工作台卡片后续都消费同一份调试视图模型。
- 避免每个入口各自拼文本、各自做排序、各自做建议去重。

## 非目标

- 当前不做新的远端诊断协议。
- 当前不继续扩大 Doctor 对话框视觉改造范围，只收口 hero、issues 等结构化资产的复用载体。
- 当前不把调试资产扩张成完整监控平台。

## 资产范围

第一阶段固定为四类资产：

1. 结论卡：`can_start`、`can_sync`、`can_bridge`、`can_recover`
2. 问题列表：按 `critical -> warning -> info` 排序的归因项
3. 修复建议：面向用户的去重建议列表
4. 技术详情卡：`llm`、`automation_hub`、`browser_bridge`、`sync`、`command_whitelist`、`plugins`

## 统一数据模型

结构固定为：

```text
debug_assets
├── hero
├── issues
├── suggestions
└── detail_cards
```

约束：

- `hero` 只放四项可操作结论，不塞技术细节
- `issues` 保留 `category`、`message`、`severity`
- `suggestions` 必须去重，顺序稳定
- `detail_cards` 是技术快照，不承接结论推导逻辑

## 消费入口

当前与后续消费方按下面顺序接入：

1. `DesktopDoctorDialog`
2. 主窗口里的 Doctor 入口与状态卡片
3. 后续工作台诊断卡片
4. 导出 JSON / 复现包摘要

要求：所有入口只消费 `build_debug_assets()` 的结果，不再各自重复推导结论。

## 当前已执行切片

2026-04-19 已完成第一段服务层实现：

- [../思忆集app/desktop_doctor_service.py](../思忆集app/desktop_doctor_service.py) 新增 `build_debug_assets(report)`
- 输出结构化 `hero / issues / suggestions / detail_cards`
- 按严重度排序问题项
- 对建议列表做顺序去重
- [../思忆集app/ui_startup_guide_dialog.py](../思忆集app/ui_startup_guide_dialog.py) 中的 `DesktopDoctorDialog` 已开始消费结构化资产，同时保留完整诊断明细，避免排障信息回退
- [../scripts/desktop_doctor.py](../scripts/desktop_doctor.py) 已新增 `--debug-assets-json`，用于导出结构化调试资产 JSON，同时保留旧 `--json` 的原始 report 语义
- `DesktopDoctorDialog` 已新增 UI 级“导出调试资产 JSON”入口，沿用同一份 `debug_assets` 模型
- `DesktopDoctorDialog` 已把 `hero` 和 `issues` 拆成可复用 widget，legacy 明细仍保留在文本区域
- 已补单测验证输出结构

对应测试：

- [../思忆集app/tests/test_desktop_doctor.py](../思忆集app/tests/test_desktop_doctor.py)
- [../思忆集app/tests/test_ui_startup_guide_dialog.py](../思忆集app/tests/test_ui_startup_guide_dialog.py)

## 下一步执行顺序

1. 让主窗口里的 Doctor 入口与后续状态卡片直接消费同一份 `debug_assets`
2. 把 `suggestions` 和 `detail_cards` 也逐步收成可复用视图模型，而不是只停留在文本块里
3. 把关键问题映射到一键修复动作，但仅限安全修复项

## 验收标准

- Doctor UI 不再自己重做归因和建议排序
- 同一份调试资产可被至少两个入口复用
- 结构化资产的单测覆盖缺失配置、降级状态和健康状态三类样本
- 用户能同时看到结论、问题、建议和技术详情，而不是只有一段长文本