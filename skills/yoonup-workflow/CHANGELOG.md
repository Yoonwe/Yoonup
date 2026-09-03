# CHANGELOG

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
