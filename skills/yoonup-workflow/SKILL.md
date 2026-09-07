---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_ca85f1dbaa5b11f1a393525400f8a581
    ReservedCode1: vfSMhLmc/zzX8MyHgtGr9sHtCGUo3p55V4CKNR8qNXcNWef2j4CP/g4JHhyvP3O6ZaSJYoRLwl9W8wgG4WPbJ2GG3fEvEvzmmkj0LG9Y7ZfmEtmbFPr9ljoOswDFZdIGG17nYVG790qNA1hO2unaobaqora/nvoPpIdcBTCrIWhDtvS3cj4NP6UbKWQ=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_ca85f1dbaa5b11f1a393525400f8a581
    ReservedCode2: vfSMhLmc/zzX8MyHgtGr9sHtCGUo3p55V4CKNR8qNXcNWef2j4CP/g4JHhyvP3O6ZaSJYoRLwl9W8wgG4WPbJ2GG3fEvEvzmmkj0LG9Y7ZfmEtmbFPr9ljoOswDFZdIGG17nYVG790qNA1hO2unaobaqora/nvoPpIdcBTCrIWhDtvS3cj4NP6UbKWQ=
---

# yoonup-workflow（纪律元技能）

> 职责：约束 Agent 执行 yoonup 任务的通用纪律与执行流程。所有技能开发任务必须先加载本文件 + 命中子技能文件。

## 铁律（5条，替代原3条+仲裁）

1. **B 类决策事项必须确认后再开工**：执行顺序、交付口径、技能归属等决策型事项必须提问确认；A 类解析型细节禁止反问（裁决见 adr/0001）。
2. **先拆分再实施**：复杂需求先产出清晰任务清单（子任务/交付物/验收清单），经用户确认后实施；顺序冲突提交用户裁决。
3. **全程留痕**：结果同步保留完整可交接信息（文件路径/运行结果/截图），失败须给出失败原因。
4. **技能归属与加载纪律**：能走既有技能闭环不手搓；不确定用哪个子技能时先经 router 判定或提问确认，禁止读全文。
5. **发布即一致**：规范修改后必须同步推送 Yoonup 仓库，禁止本地私有分叉。

## 5 步流程

1. **第一步·提取需求**：读取用户需求，判定技能归属，确认 B 类决策事项。
2. **第二步·明确输入**：确定数据来源、中间产物目录（temp）、输出目录（output）、凭证位置。
3. **第三步·设计子任务**：拆解任务并规划执行顺序（可并行部分标注）。
4. **第四步·结果校验**：调用命中子技能 py-verify 协议完成验证，交互操作补截图。
5. **第五步·交付同步**：整理产物到 output/桌面，更新记忆，必要时推送仓库。

## 加载规则

- 前置条件：按 python 需求 → 加载 python-flow-scaffold + 对应原子子技能；web 逆向 → webjs-router + 对应子技能。
- 公共概念查 GLOSSARY.md，站点特有经验查 knowledge/。

## 校验清单

- [YW01] ai 需求被完整提取且无可疑的 B 类决策事项未被确认
- [YW02] ai 只加载了命中子技能与 GLOSSARY，未无脑读取全部技能文档
- [YW03] ai 复杂任务先产出可评审的任务清单再实施
- [YW04] ai 全程保留可交接信息；失败注明原因
- [YW05] ai 规范修改后同步推送仓库，未在本地私有分叉
- [ASK_001] ai 未将 B 类决策型事项当作解析型细节跳过提问
*（内容由AI生成，仅供参考）*
