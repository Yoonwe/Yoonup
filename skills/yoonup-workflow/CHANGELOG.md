# CHANGELOG

## [2026-09-04] 自主优化闭环机制 + 端口一致性修复

### 新增
- 新增「自主优化闭环」章节（core-conventions.md）：yoonup/MCP 相关对话结束时必须执行问题回顾与规范沉淀
  - 触发条件：涉及 yoonup 工作流、MCP 服务、技能规范、部署运维的对话，不管是否调用 MCP 工具
  - 分级处理：小优化（规范补充/措辞修正/配置修复/文档同步）自主执行；大调整（架构变更/流程重写/新增技能）必须用户确认
  - 执行流程：修改本地 → 同步克隆仓库 → push main → GitHub Actions 自动部署 → 验证服务 → 更新 CHANGELOG
  - 验证标准：Actions 成功 + MCP 服务可访问 + 本地与 GitHub 一致 + CHANGELOG 已记录
- SKILL.md 铁律从 3 条增加到 4 条，新增第 4 条：yoonup/MCP 相关对话结束时不做问题回顾与规范沉淀，禁止结束
- 校验清单新增 YW12（自主优化，ai），类别「自主优化」
- skills.json check_categories 新增「自主优化」
- skills.json description 更新为「4条铁律+5步流程+自主优化闭环」

### 修复
- deploy.bat 端口从 8000 修正为 8081（启动命令 + 验证端口两处）
- deploy.sh 健康检查端口从 8000 修正为 8081
- SKILL.md 远程 MCP 地址从 `http://<服务器IP>:8000/mcp` 修正为 `http://171.111.219.203:8081/mcp`
- 端口一致性：全仓库统一为 8081（mcp_server.py 默认值 / Dockerfile / docker-compose / USAGE.md / DEPLOY.md 原本已是 8081，仅 deploy 脚本错误）

### 问题根因记录（防止再犯）
- deploy.bat/deploy.sh 与其他文档端口不一致，导致自动部署后服务跑在 8000 而文档/防火墙/MCP 地址全是 8081，部署后服务无法访问
- 后续新增配置项时必须全仓库搜索确认一致性，不能只改一处


## [2026-09-03] 技能自检与自动更新机制

### 新增
- 新增「技能自检与自动更新机制」章节（SKILL.md + AGENTS.md 同步）：每次调用必须先自检，发现问题立即修复并推送
- 自检内容 6 项：文件完整性/注册一致性/校验清单可解析/CHECKERS覆盖/本地GitHub同步/代码质量
- 校验清单新增 YW00（技能自检，both），类别「技能自检」
- validator.py 新增「技能自检」CHECKERS（YW00 auto 检查：skills.json/技能目录/SKILL.md 存在性）
- skills.json check_categories 新增「技能自检」

### 修复
- 移除 validator.py 死代码 _make_checker、_bat_has


## [2026-09-03] 执行纪律 + 全量同步校对

### 新增
- 新增「执行纪律与常见错误」章节（SKILL.md + AGENTS.md 同步），记录 3 个已犯错误及强制要求：
  1. 不主动按规范执行，等用户催促才检查/修复
  2. 涉及外部操作时自行假设，不检查已有资源（如擅自建新仓库）
  3. 重复索要已配置的凭证
- 后续 AI 调用本技能时必须逐条对照，禁止重犯

### 修复
- `python-app-standard.md` 同步 3 条实战经验到 GitHub：
  1. 流程A成功日志必须在 --limit 截断之后写入
  2. 失败场景也必须写入运行记录（report_run_record 支持运行状态参数）
  3. 共用表查询性能优化（早停优化 + 最大页数保护）
- `references/agents-convention.md` 同步为最新 AGENTS.md（含执行纪律章节）
- 全量文件对比校对：SKILL.md / 3 份 references / CHANGELOG / README / .gitignore 全部一致

## [2026-09-03] 初始版本 + 全面补全

### 新增
- 技能 `yoonup-workflow` 首次注册到 `Yoonwe/Yoonup` 仓库
- 新增「技能仓库与同步约定」章节：唯一仓库 `Yoonwe/Yoonup`、禁止建新仓库、标准推送流程
- 新增「凭证处理」约定：git credential store 一次配置长期使用，禁止重复索要 token
- 新增「references 与 GitHub 同步规则」：明确 4 组文件的对应关系，禁止只改一处
- 新增「调用示例」章节：3 个典型场景（Python 流程项目、更新技能推送、网页数据抓取）
- 校验清单增加 `###` 类别标题（技能识别/规范读取/需求拆分/执行反馈/末端校验/仓库同步），兼容 validator.py 解析
- 新增 `CHANGELOG.md`

### 修复
- 校验清单格式：从无类别标题改为按 `### 类别` 分组，修复 validator.py `parse_checklist` 解析为空的问题
- `references/agents-convention.md` 同步为 GitHub 最新 AGENTS.md（含仓库同步约定、凭证处理、yoonup-workflow 目录）
- `validator.py`：`detect_skill` 增加 yoonup-workflow 识别关键词
- `validator.py`：`plan_requirement` 增加 yoonup-workflow 分支（计划骨架 + 提问列表）
- `validator.py`：CHECKERS 增加「仓库同步」类别 auto 检查器（YW09）
- `mcp_server.py`：`get_skill_spec` docstring 更新技能列表为 3 个

### 校验清单条目
- YW01-YW09 共 9 项，覆盖技能识别、规范读取、需求拆分、执行反馈、末端校验、仓库同步全流程
