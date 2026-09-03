# Yoonup 工作流约定（AGENTS.md）

本仓库是「工作流约定 + 技能规范库 + 远程 MCP」三件套。任何智能体 / vibe-coding 产品
（豆包、Cursor、Dify、Marvis 等）接入本仓库执行任务时，**必须**按本文档的流程约定执行。

## 仓库角色

| 文件 | 角色 |
|------|------|
| `AGENTS.md` | 工作流流程约定（本文档，所有 AI 产品必须遵守） |
| `skills/*/SKILL.md` | 技能规范库：一个技能一个目录，SKILL.md 为普通 MD 操作指南（YAML frontmatter + 正文）；**每份文档末尾含「校验清单」章节** |
| `skills.json` | 技能注册表：id / name / file / description / check_section |
| `validator.py` | 校验器：解析 MD 校验清单、自动化检查、执行计划规划（不依赖 LLM） |
| `mcp_server.py` | 远程 MCP Server：暴露 list_skills / get_skill_spec / plan_requirement / check_result 四个工具 |
| `Dockerfile` / `docker-compose.yml` | 云服务器 7×24 部署 |
| `requirements.txt` | 依赖清单 |

## 核心原则

1. **技能是普通 MD 操作指南**：执行时严格按技能文档要求做事，禁止自创规范、禁止跳过技能要求。
2. **任何智能体都能执行**：本仓库不内置执行引擎，执行者就是接入的 AI 产品本身。
3. **任务体量大时 AI 易纰漏**：必须做到「稳定执行 + 规范执行 + 末端校验」，杜绝凭印象交差。
4. **任何电脑可用**：远程 MCP 部署在云服务器（7×24），不依赖某台本地电脑关机与否。

## 执行纪律与常见错误（后续 AI 必须遵守，禁止再犯）

本章节记录实际执行中犯过的错误，后续 AI 接入本仓库执行任务时**必须逐条对照，禁止重犯**。

### 错误 1：不主动按规范执行，等用户催促才检查/修复
- **现象**：技能明确写了「末端校验」和「文档维护约定」，但 AI 执行完不主动校验、不主动同步文档，等用户说"检查一下""查漏补缺"才动手。
- **强制要求**：
  - 每一步执行完成后**主动**检查该步结果是否符合规范，不需要用户催促；
  - 全部步骤完成后**必须**执行末端校验（第 4 步），校验未通过**必须**主动修复，修复后重新校验；
  - 执行中发现规范未覆盖的新问题，**必须**主动更新对应技能 MD 并同步到 GitHub，不需要用户要求；
  - **禁止**把"等用户确认后再检查"作为借口，校验是技能的强制步骤，不是可选项。

### 错误 2：涉及外部操作时自行假设，不检查已有资源
- **现象**：用户说"推到 GitHub"，AI 不检查用户已有仓库，直接 `gh repo create` 建新仓库，导致理解错误。
- **强制要求**：
  - 涉及推送、创建、删除、修改等外部操作时，**必须先检查已有资源**（如 `gh repo list`、`git remote -v`、目录是否存在）；
  - 发现已有对应资源时，**必须**使用已有资源，禁止自行创建新的；
  - 不确定时**必须向用户确认**，禁止自行假设；
  - 本仓库唯一 GitHub 地址：`Yoonwe/Yoonup`，详见「技能仓库与同步约定」。

### 错误 3：重复索要已配置的凭证
- **现象**：环境已配置 git credential store，但 AI 推送时不检查，直接向用户索要 token。
- **强制要求**：
  - 推送前**必须**先执行 `git credential fill` 检查凭证状态；
  - 已返回 username 时**直接推送**，禁止向用户索要 token；
  - 仅当凭证未配置时，才按「凭证处理」章节的步骤一次性配置，之后同一环境内禁止重复索要；
  - token 是敏感信息，**禁止**写进文档、代码或提交到 git 历史。

## 工作流执行约定（必须按此流程执行）

### 第 0 步：识别技能
判断需求属于哪个技能，不确定时调用 `list_skills` 查看：
- `yoonup-workflow`：工作流总入口（识别子技能→读取规范→需求拆分→按序执行→末端校验），含仓库同步约定
- `python-app-standard`：Python 流程项目（多子流程编排、飞书通知、定时任务、运行记录等）
- `web-js-app-implementation`：网页后台数据抓取（JS 逆向 / 接口直连，输出影刀可用二维列表）

### 第 1 步：读取技能规范（禁止跳过）
调用 `get_skill_spec(skill_id)` 获取技能规范全文与校验清单章节。
技能文档是唯一权威，**禁止不读规范直接开干**。

### 第 2 步：需求拆分（向用户提问，由用户定执行顺序）
调用 `plan_requirement(requirement, skill_id)` 获取计划骨架，然后：
- 结合具体需求细化步骤；
- **需求拆分时向用户提问确认执行顺序，由用户拍板后开始执行**，禁止自行跳过提问；
- 执行中**实时反馈进度**：每步开始 / 完成 / 失败都要反馈，不憋到最后才汇报。

### 第 3 步：按顺序执行
- 按用户确认的顺序执行每一步，严格按技能规范做事（目录结构、命名、日志、通知、进度、token、重试、定时任务、run.bat 等）。
- 执行中发现规范未覆盖的新问题 → 同步更新对应技能 MD（见「文档维护约定」）。

### 第 4 步：末端整合校验（必须，不可跳过）
- 全部步骤执行完成后，调用 `check_result(project_dir, skill_id)` 做末端校验；
- `auto_failed` 未通过项必须修复；返回的 `ai_checklist` 条目**必须逐项核对**，不能跳过；
- 反复修复直到全部通过，**校验通过才允许交付**；
- 交付时给出：产物路径 + 运行验证结果 + 校验通过情况。

## 校验清单约定

- 每份技能 MD 末尾有 `## 校验清单` 章节，条目格式固定：
  `- [ID] 检查方式 检查内容`，检查方式为 `auto`（程序自动化检查）/ `ai`（AI 判断）/ `both`（程序检查 + AI 复核）。
- `validator.py` 运行时解析该章节并驱动 `check_result`；**修改校验清单只改 MD，不改代码**。
- 新增检查项：在 MD 校验清单追加符合格式的行即可；若 ID 在 validator.py 有对应检查器则自动检查，否则自动归入 AI 核对清单。
- 校验清单章节前是技能正文，正文与清单保持一致；执行中发现偏差以正文规范为准并同步修正清单。

## 文档维护约定

- 执行过程中发现的问题 / 踩坑 / 新接口经验，**必须同步更新 `skills/<skill-name>/SKILL.md`**，禁止只留在对话上下文。

## 技能仓库与同步约定（必须遵守）

- **唯一 GitHub 仓库**：`Yoonwe/Yoonup`（描述：技能仓储）。所有技能的版本管理与多机同步**只推这个仓库**，**禁止为技能创建新的 GitHub 仓库**。
- **本地路径与仓库路径映射**：
  - 本地技能目录：`.user_skills/<skill-name>/`（含 `SKILL.md`、`references/` 等）
  - 仓库内路径：`skills/<skill-name>/`（将本地整个目录复制到仓库 `skills/` 下）
- **更新/推送技能的标准流程**：
  1. `git clone https://github.com/Yoonwe/Yoonup.git`（或 `git pull` 已有仓库）
  2. 将本地技能目录复制到仓库 `skills/` 下
  3. 在 `skills.json` 中注册该技能（id / name / file / description / check_section / check_categories）
  4. `git add -A && git commit -m "update: <skill-name>" && git push`
- **禁止行为**：禁止用 `gh repo create` 为技能新建仓库；禁止推送到其他仓库；禁止只改本地不同步到 GitHub。
- **凭证处理（一次配置，长期使用）**：
  - 推送前先检查 `git credential fill` 是否返回 username；若已配置凭证，直接 `git push`，**禁止重复向用户索要 token**。
  - 若未配置，执行：`git config --global credential.helper store`，然后将 `https://<用户名>:<token>@github.com` 写入 `~/.git-credentials`（权限 600），之后所有推送自动读取，不再交互。
  - 换电脑/换环境时只需重新执行一次上述配置；同一环境内禁止反复索要凭证。
  - token 是敏感信息，**禁止写进技能文档、代码或提交到 git 历史**，仅存于本地 `~/.git-credentials`。

## 部署与接入

- 本地调试：`python mcp_server.py`（默认 `0.0.0.0:8000`，streamable-http）。
- 云服务器：`docker compose up -d --build`（或 `python mcp_server.py --port 8000`），保持 7×24 在线。
- 接入方（Dify / Cursor / Marvis 等支持远程 MCP 的产品）填入服务地址：
  `http://<服务器IP>:8000/mcp`
- 云服务器安全组需放行对应端口；建议使用 HTTPS 反向代理或内网穿透保障安全。

## 目录结构

```
Yoonup/
├── AGENTS.md              # 工作流执行约定（本文档）
├── mcp_server.py          # 远程 MCP Server（4 工具）
├── validator.py           # 校验器（解析校验清单 + 自动化检查 + 计划规划）
├── skills/
│   ├── yoonup-workflow/
│   │   ├── SKILL.md       # 技能0：工作流总入口 + 仓库同步约定 + 校验清单
│   │   └── references/    # 子技能规范文档（agents-convention / python-app-standard / web-js-app-implementation）
│   ├── python-app-standard/
│   │   └── SKILL.md       # 技能1：Python 流程脚手架规范 + 校验清单
│   └── web-js-app-implementation/
│       └── SKILL.md       # 技能2：网页 JS 逆向抓取规范 + 校验清单
├── skills.json            # 技能注册表
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```
