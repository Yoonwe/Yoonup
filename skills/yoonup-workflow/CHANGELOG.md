# CHANGELOG

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
