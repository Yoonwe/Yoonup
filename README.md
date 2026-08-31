# Yoonup

让**任何智能体 / vibe-coding 产品**都能按「工作流文件夹规范」稳定执行任务、调用指定技能，并在末端做整合校验的**三件套**仓库：

> **工作流约定（AGENTS.md） + 技能规范库（skills/*/SKILL.md） + 远程 MCP（mcp_server.py）**

## 解决什么问题

- 任务体量大时 AI 容易纰漏 → 用**固定工作流约定**保证稳定执行、规范执行、末端校验；
- 技能就是普通 MD 操作指南 → 任何 AI 产品读文档即会做，**不绑定某个引擎**；
- 本地电脑关机就不能用 → 远程 MCP 部署在**云服务器 7×24 在线**，任何电脑都能接入。

## 工作流（接入方 AI 必须遵守）

1. **识别技能**：`list_skills` 查看可用技能（python-app-standard / web-js-app-implementation）
2. **读取规范**：`get_skill_spec` 获取技能 MD 全文 + 校验清单（禁止跳过）
3. **拆分需求**：`plan_requirement` 获取计划骨架 → **向用户提问确认执行顺序** → 按序执行，实时反馈进度
4. **末端校验**：`check_result` 对执行结果按校验清单逐项核对，未通过修复重跑，**通过才交付**

详细约定见 [AGENTS.md](AGENTS.md)。

## 快速开始

### 本地运行

```bash
pip install -r requirements.txt
python mcp_server.py                # streamable-http，默认 0.0.0.0:8000
python mcp_server.py --port 9000    # 自定义端口
```

### 云服务器部署（推荐，7×24 在线）

```bash
docker compose up -d --build
# 服务地址：http://<服务器IP>:8000/mcp
```

安全组放行对应端口；生产环境建议套 HTTPS 反向代理或内网穿透。

### 接入 Dify / Cursor / 豆包等支持远程 MCP 的产品

MCP 服务地址填入：`http://<服务器IP>:8000/mcp`（streamable-http）

## MCP 工具

| 工具 | 说明 |
|------|------|
| `list_skills` | 列出所有可用技能（id / name / description） |
| `get_skill_spec` | 获取技能规范全文 + 校验清单章节 |
| `plan_requirement` | 按技能规范生成执行计划骨架（含需向用户确认的问题，不依赖 LLM） |
| `check_result` | 对执行结果做末端整合校验（自动检查 + 返回清单供 AI 逐项核对） |

## 技能规范库

技能是**普通 MD 操作指南**，放在 `skills/<skill-name>/SKILL.md`（agentskills.io 标准格式：YAML frontmatter + 正文），每份文档末尾含 `## 校验清单` 章节：

- **skills/python-app-standard/SKILL.md**：Python 流程项目脚手架（目录结构、命名规范、文件锁、日志、飞书通知、运行记录、Token 重试、定时任务、run.bat 规范、运行验证 9 项）
- **skills/web-js-app-implementation/SKILL.md**：网页 JS 逆向 / 接口直连数据抓取（token 自动化、CDP、分页、清洗、抖店登录与选店规范、滑块应对）

### 扩展技能 / 新增校验项

1. 在 `skills/` 下新建技能目录，编写 `SKILL.md`（第一行 `---` 开头，frontmatter 含 `name` / `description` / `metadata`，正文末尾必须有 `## 校验清单` 章节）；
2. 在 `skills.json` 注册（id / name / file / description / check_section / check_categories）；
3. 校验清单条目格式固定：`- [ID] auto|ai|both 检查内容`；
4. 若新增 ID 想在 validator.py 里自动检查，按对应类别补检查器；否则自动归入 AI 核对清单（无需改代码）。

> 校验清单是运行时解析的，**改 MD 即可，不用改代码**。

## 目录结构

```
Yoonup/
├── AGENTS.md              # 工作流执行约定（接入方 AI 必须遵守）
├── mcp_server.py          # 远程 MCP Server（4 工具）
├── validator.py           # 校验器：解析校验清单 + 自动化检查 + 计划规划
├── skills/
│   ├── python-app-standard/
│   │   └── SKILL.md       # 技能1：Python 流程脚手架规范 + 校验清单
│   └── web-js-app-implementation/
│       └── SKILL.md       # 技能2：网页 JS 逆向抓取规范 + 校验清单
├── skills.json            # 技能注册表
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 技术栈

- Python 3.11+，零业务依赖（仅 `mcp` + `requests`）
- MCP 官方 Python SDK（FastMCP），streamable-http / SSE 双传输
- 校验器为纯规则引擎，不依赖 LLM，稳定可复现
