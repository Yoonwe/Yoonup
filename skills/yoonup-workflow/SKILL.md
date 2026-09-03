---
name: yoonup-workflow
description: 按 Yoonup「工作流文件夹规范」稳定执行任务：识别技能→读取规范→需求拆分提问→按序执行→末端校验。当用户要求开发/修改 Python 流程自动化项目（多子流程编排、飞书通知、定时任务、运行记录、文件锁、日志、run.bat 等）或网页后台数据抓取（JS 逆向/接口直连、输出影刀可用二维列表）时使用。
---

# Yoonup 工作流执行约定

## 核心原则

- **技能是普通 MD 操作指南**：执行时严格按技能文档要求做事，禁止自创规范、禁止跳过技能要求。
- **任务体量大时必须**「稳定执行 + 规范执行 + 末端校验」，杜绝凭印象交差。

## 技能选择

| 需求 | 技能 id | 规范文件 |
|------|---------|----------|
| Python 流程自动化项目（多子流程编排、飞书通知、定时任务、运行记录、文件锁、日志、run.bat） | python-app-standard | `references/python-app-standard.md` |
| 网页后台数据抓取（JS 逆向/接口直连，输出影刀可用二维列表） | web-js-app-implementation | `references/web-js-app-implementation.md` |

## 工作流（必须按此流程执行）

### 第 0 步：识别技能
判断需求属于哪个技能，不确定时按上表对照。

### 第 1 步：读取技能规范（禁止跳过）
读取对应 `references/` 文件的**全文**，含末尾「校验清单」章节。技能文档是唯一权威，**禁止不读规范直接开干**。

### 第 2 步：需求拆分（向用户提问，由用户定执行顺序）
- 结合具体需求细化步骤；
- **需求拆分时向用户提问确认执行顺序，由用户拍板后开始执行**，禁止自行跳过提问；
- 执行中**实时反馈进度**：每步开始/完成/失败都要反馈，不憋到最后才汇报。

### 第 3 步：按顺序执行
严格按技能规范做事（目录结构、命名、日志、通知、进度、token、重试、定时任务、run.bat 等）。执行中发现规范未覆盖的新问题 → 同步更新对应 references 文件（见「文档维护约定」）。

### 第 4 步：末端整合校验（必须，不可跳过）
- 全部步骤执行完成后，按该技能规范「校验清单」章节**逐项核对**；
- `auto` 未通过项必须修复；`ai` / `both` 条目**必须逐项核对**，不能跳过；
- 反复修复直到全部通过，**校验通过才允许交付**；
- 交付时给出：产物路径 + 运行验证结果 + 校验通过情况。

## 远程 MCP（可选接入）

若已部署 Yoonup 远程 MCP（streamable-http），可调用 `list_skills` / `get_skill_spec` / `plan_requirement` / `check_result` 获取计划骨架与末端校验；本地无 MCP 时，直接用本技能内置的 references 规范执行同样流程。

## 技能仓库与同步约定（必须遵守）

- **唯一 GitHub 仓库**：`Yoonwe/Yoonup`（描述：技能仓储）。所有技能的版本管理与多机同步**只推这个仓库**，**禁止为技能创建新的 GitHub 仓库**。
- **本地路径与仓库路径映射**：
  - 本地技能目录：`.user_skills/<skill-name>/`（含 `SKILL.md`、`references/` 等）
  - 仓库内路径：`skills/<skill-name>/`（将本地整个目录复制到仓库 `skills/` 下）
  - 本技能对应：本地 `.user_skills/yoonup-workflow/` → 仓库 `skills/yoonup-workflow/`
- **更新/推送技能的标准流程**：
  1. `git clone https://github.com/Yoonwe/Yoonup.git`（或 `git pull` 已有仓库）
  2. 将本地技能目录复制到仓库 `skills/` 下（如 `skills/yoonup-workflow/`）
  3. 在 `skills.json` 中注册该技能（id / name / file / description / check_section / check_categories）
  4. `git add -A && git commit -m "update: <skill-name>" && git push`
- **禁止行为**：禁止用 `gh repo create` 为技能新建仓库；禁止推送到其他仓库；禁止只改本地不同步到 GitHub。

## 文档维护约定

- 执行过程中发现的**问题/踩坑/新接口经验**，必须同步更新 `references/` 对应文件，禁止只留在对话上下文。
- 校验清单条目格式固定：`- [ID] auto|ai|both 检查内容`，检查方式为 auto（程序自动化检查）/ ai（AI 判断）/ both（程序检查 + AI 复核）。
- 正文与清单保持一致：执行中发现偏差以正文规范为准，并同步修正清单。

## 校验清单

- [YW01] ai 已正确识别需求所属子技能（python-app-standard / web-js-app-implementation），不确定时已向用户确认
- [YW02] ai 已读取对应 references 规范文件全文，含末尾校验清单章节，未跳过
- [YW03] ai 已向用户提问确认执行顺序，由用户拍板后才开始执行，未自行跳过提问
- [YW04] ai 执行中每步开始/完成/失败均实时反馈进度，未憋到最后才汇报
- [YW05] ai 严格按子技能规范做事（目录结构、命名、日志、通知、定时任务等），未自创规范
- [YW06] ai 执行中发现规范未覆盖的新问题，已同步更新对应 references 文件，未只留在对话上下文
- [YW07] both 末端校验已按子技能校验清单逐项核对，auto 未通过项已修复，全部通过才交付
- [YW08] ai 交付时已给出产物路径 + 运行验证结果 + 校验通过情况
- [YW09] both 技能变更已推送到唯一仓库 Yoonwe/Yoonup 的 skills/ 目录，未创建新仓库，已在 skills.json 注册
