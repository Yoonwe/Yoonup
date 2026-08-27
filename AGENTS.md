# Yoonup 工作流约定（AGENTS.md）

本仓库是「工作流约定 + 技能规范库 + 远程 MCP」三件套。任何智能体 / vibe-coding 产品
（豆包、Cursor、Dify、Marvis 等）接入本仓库执行任务时，**必须**按本文档的流程约定执行。

## 仓库角色

| 文件 | 角色 |
|------|------|
| `AGENTS.md` | 工作流流程约定（本文档，所有 AI 产品必须遵守） |
| `skills/*.md` | 技能规范库：普通 MD 操作指南，记录具体操作事项；**每份文档末尾含「校验清单」章节** |
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

## 工作流执行约定（必须按此流程执行）

### 第 0 步：识别技能
判断需求属于哪个技能，不确定时调用 `list_skills` 查看：
- `python-app`：Python 流程项目（多子流程编排、飞书通知、定时任务、运行记录等）
- `web-js-app`：网页后台数据抓取（JS 逆向 / 接口直连，输出影刀可用二维列表）

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

- 执行过程中发现的问题 / 踩坑 / 新接口经验，**必须同步更新 `skills/` 下对应 MD**，禁止只留在对话上下文。
- 本仓库以 GitHub 为版本管理与同步源，改动后提交并推送保持多机一致。

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
│   ├── python应用规范.md   # 技能1：Python 流程脚手架规范 + 校验清单
│   └── web-js应用实施.md   # 技能2：网页 JS 逆向抓取规范 + 校验清单
├── skills.json            # 技能注册表
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```
