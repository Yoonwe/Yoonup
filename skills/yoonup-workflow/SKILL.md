---
name: yoonup-workflow
description: 按 Yoonup「工作流文件夹规范」稳定执行任务：识别技能→读取规范→需求拆分提问→按序执行→末端校验。当用户要求开发/修改 Python 流程自动化项目（多子流程编排、飞书通知、定时任务、运行记录、文件锁、日志、run.bat 等）或网页后台数据抓取（JS 逆向/接口直连，输出影刀可用二维列表）时使用。
---

# Yoonup 工作流执行约定

## 核心原则

- **技能是普通 MD 操作指南**：执行时严格按技能文档要求做事，禁止自创规范、禁止跳过技能要求。
- **任务体量大时必须**「稳定执行 + 规范执行 + 末端校验」，杜绝凭印象交差。

## 执行纪律与常见错误（后续 AI 必须遵守，禁止再犯）

本章节记录实际执行中犯过的错误，后续 AI 调用本技能时**必须逐条对照，禁止重犯**。

### 错误 1：不主动按规范执行，等用户催促才检查/修复
- **现象**：技能明确写了「末端校验」和「文档维护约定」，但 AI 执行完不主动校验、不主动同步文档，等用户说"检查一下""查漏补缺"才动手。
- **强制要求**：
  - 每一步执行完成后**主动**检查该步结果是否符合规范，不需要用户催促；
  - 全部步骤完成后**必须**执行末端校验（第 4 步），校验未通过**必须**主动修复，修复后重新校验；
  - 执行中发现规范未覆盖的新问题，**必须**主动更新对应 references 文件并同步到 GitHub，不需要用户要求；
  - **禁止**把"等用户确认后再检查"作为借口，校验是技能的强制步骤，不是可选项。

### 错误 2：涉及外部操作时自行假设，不检查已有资源
- **现象**：用户说"推到 GitHub"，AI 不检查用户已有仓库，直接 `gh repo create` 建新仓库，导致理解错误。
- **强制要求**：
  - 涉及推送、创建、删除、修改等外部操作时，**必须先检查已有资源**（如 `gh repo list`、`git remote -v`、目录是否存在）；
  - 发现已有对应资源时，**必须**使用已有资源，禁止自行创建新的；
  - 不确定时**必须向用户确认**，禁止自行假设；
  - 本技能的唯一 GitHub 仓库是 `Yoonwe/Yoonup`，详见「技能仓库与同步约定」。

### 错误 3：重复索要已配置的凭证
- **现象**：环境已配置 git credential store，但 AI 推送时不检查，直接向用户索要 token。
- **强制要求**：
  - 推送前**必须**先执行 `git credential fill` 检查凭证状态；
  - 已返回 username 时**直接推送**，禁止向用户索要 token；
  - 仅当凭证未配置时，才按「凭证处理」章节的步骤一次性配置，之后同一环境内禁止重复索要；
  - token 是敏感信息，**禁止**写进文档、代码或提交到 git 历史。

## 技能选择

| 需求 | 技能 id | 规范文件 |
|------|---------|----------|
| Python 流程自动化项目（多子流程编排、飞书通知、定时任务、运行记录、文件锁、日志、run.bat） | python-app-standard | `references/python-app-standard.md` |
| 网页后台数据抓取（JS 逆向/接口直连，输出影刀可用二维列表） | web-js-app-implementation | `references/web-js-app-implementation.md` |

## 技能自检与自动更新机制（每次调用必须执行，禁止跳过）

每次调用本技能时，**必须先执行技能自检**，确认技能本身完整、一致、可用。发现问题**立即修复并推送到 GitHub**，不需要用户要求。

### 自检内容（逐项检查）

1. **文件完整性**：`SKILL.md`、`references/` 下 3 份规范文件、`CHANGELOG.md`、`README.md`、`.gitignore` 全部存在
2. **注册一致性**：`skills.json` 中注册的技能与 `skills/` 实际目录一致，字段完整（id/name/file/description/check_section/check_categories）
3. **校验清单可解析**：`validator.py` 能正确解析所有技能的校验清单，ID 唯一，类别与 `check_categories` 一致
4. **CHECKERS 覆盖**：所有 `auto`/`both` 条目的类别都有对应的检查器，无死代码
5. **本地与 GitHub 同步**：本地 `.user_skills/yoonup-workflow/` 与 GitHub `skills/yoonup-workflow/` 7 组文件完全一致
6. **代码质量**：`validator.py`、`mcp_server.py` 语法正确，无敏感信息泄露，无 BOM，无死代码

### 发现问题后的处理流程

1. **立即修复**：在本地修复发现的问题（技能文档、references、validator.py 等）
2. **同步到 GitHub**：按「技能仓库与同步约定」的标准流程，将修复推送到 `Yoonwe/Yoonup`
3. **重新自检**：修复后重新执行自检，直到全部通过
4. **记录变更**：在 `CHANGELOG.md` 中记录本次修复内容
5. **继续执行任务**：自检通过后，才进入正式工作流（第 0 步开始）

### 校对质量强制要求（三轮校对，每轮必须独立）

用户要求"校对直到三次没有问题"时，**必须按以下规则执行，禁止糊弄**：

1. **每轮校对必须重新 clone 仓库**，不能在已有目录上查（避免缓存/未提交文件干扰）
2. **每轮查不同维度**，不能重复跑同一个脚本：
   - 第 1 轮：结构与一致性（文件存在/注册一致/MD可解析/类别匹配/文件diff）
   - 第 2 轮：逻辑与边界（构造正反用例测试检查器/错误输入/空目录/不存在的ID/边界值）
   - 第 3 轮：安全与运维（敏感信息扫描/git历史/路径遍历/依赖完整性/Docker配置/启动测试）
3. **每一项检查必须执行具体命令并贴出输出**，不能只写"通过"二字。输出中必须包含实际数据（如"类别数: 7"、"passed: ['YW00','YW09']"），不能是泛泛而谈
4. **主动构造破坏用例**：不是查"有没有问题"，而是故意传入错误参数（文件路径当目录、不存在的技能ID、空字符串、特殊字符）看系统是否正确处理
5. **发现问题立即修复并推送**，然后从第 1 轮重新开始；连续三轮零问题才算完成
6. **校对结果必须可验证**：用户能根据你贴的命令和输出复现检查过程

### 糊弄行为清单（出现任意一项即校验不通过）

- 只说"全部通过/没问题"，不贴具体命令输出和数据
- 三轮校对跑同一个检查脚本，换个名字就算新一轮
- 只检查改过的文件，不重新检查整个仓库
- 用"应该没问题"、"看起来一致"等主观判断代替实际命令验证
- 验证脚本报错了还说"全部通过"
- 发现问题不修复不推送，只在对话里说"已记录"
- 跳过边界测试，只测正常输入

### 校对维度清单（每次校对必须覆盖以下全部维度，禁止遗漏）

用户要求校对时，必须按以下维度逐项检查，每项执行具体命令并贴出输出。**禁止只查其中一部分就说"全部通过"。**

#### 第 1 轮：结构与一致性（10 项）
1. 最新提交号（`git log --oneline -1`）
2. 技能注册数与字段完整性（id/name/file/description/check_section/check_categories）
3. 校验清单解析（3 个技能全部解析，统计类别数、条目数、ID 唯一性）
4. CHECKERS 覆盖（所有 auto/both 类别的条目都有对应检查器）
5. 本地与 GitHub 文件一致性（7 组文件 diff）
6. AGENTS.md ↔ references/agents-convention.md 一致
7. references ↔ skills 对应文件一致（python-app-standard、web-js-app-implementation）
8. Python 语法（validator.py + mcp_server.py）
9. 无 BOM（所有 .py/.md/.json/.yml 文件）
10. dist 3 个 zip 内容与 skills 目录一致

#### 第 2 轮：逻辑与边界（6 类用例）
1. **check_result 边界**：传入文件路径（如 /etc/passwd）、不存在路径、空目录、正常目录、不传 skill_id
2. **get_skill_checklist 边界**：不存在的技能 ID、空字符串、正常技能
3. **detect_skill 边界**：空字符串、各技能关键词、模糊需求
4. **plan_requirement 边界**：空需求、不存在的 skill_id、三个技能都有 steps 和 questions
5. **检查器逻辑正反用例**：YW00（有/无 skills.json）、YW09（有/无 git remote）
6. **parse_checklist 边界**：无校验清单章节、空章节、格式错误条目（缺 method）、正常条目

#### 第 3 轮：安全与运维（7 项）
1. 敏感信息扫描（工作区 + git 历史，搜 github_pat/ghp_/token 等）
2. 路径遍历测试（_read_project 不会读取项目目录外的文件）
3. MCP 服务启动测试（timeout 3 秒，确认 startup complete）
4. Docker 配置（Dockerfile 基础镜像、docker-compose 端口映射）
5. 依赖检查（mcp/fastapi 已安装，requirements.txt 完整）
6. git 状态（无未推送提交、无未提交变更）
7. 配置文件（.env.example、requirements.txt、.gitignore 都存在）

#### 代码质量专项（发现问题即修复，不计入三轮）
- 未使用的 import（ast 分析）
- 类型注解覆盖率（参数注解、返回值注解）
- 缺返回值注解的函数
- 异常处理覆盖（open/listdir/subprocess.run 是否在 try 中）
- 调试代码残留（print/pdb/breakpoint，排除 __main__ 块）
- 函数命名一致性（私有函数以 _ 开头）
- README 描述与实际功能一致
- skills.json description 与 SKILL.md frontmatter 一致
- check_section 字段与实际章节标题匹配
- 文件读写指定 encoding
- 路径处理用 os.path.join，不硬编码 /

#### 校对完成标准
- 上述全部维度逐项检查，每项有命令输出为证
- 发现问题立即修复并推送，然后从第 1 轮重新开始
- 连续三轮（每轮重新 clone）零问题，才算完成
- 禁止用"全部通过"四个字代替具体证据

### 禁止行为

- **禁止**跳过技能自检直接执行任务
- **禁止**发现技能问题后只修本地不推送到 GitHub
- **禁止**等用户要求才检查或修复技能问题
- **禁止**把"技能有问题"作为借口降低交付标准
- **禁止**用"全部通过"四个字代替具体的校对证据

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
- **凭证处理（一次配置，长期使用）**：
  - 推送前先检查 `git credential fill` 是否返回 username；若已配置凭证，直接 `git push`，**禁止重复向用户索要 token**。
  - 若未配置，执行：`git config --global credential.helper store`，然后将 `https://<用户名>:<token>@github.com` 写入 `~/.git-credentials`（权限 600），之后所有推送自动读取，不再交互。
  - **重要**：`~/.git-credentials` 凭证文件持久化，但 `git config --global user.name/user.email` 在新环境/新会话中可能丢失。**每次推送前必须执行**：`git config user.name "Yoonwe" && git config user.email "wanwei@352group.com.cn"`（仓库级别即可，不依赖全局配置）。
  - 换电脑/换环境时只需重新执行一次上述配置；同一环境内禁止反复索要凭证。
  - token 是敏感信息，**禁止写进技能文档、代码或提交到 git 历史**，仅存于本地 `~/.git-credentials`。

## references 与 GitHub 同步规则

- `references/agents-convention.md` ↔ GitHub 仓库根目录 `AGENTS.md`（必须保持一致）
- `references/python-app-standard.md` ↔ GitHub `skills/python-app-standard/SKILL.md`（必须保持一致）
- `references/web-js-app-implementation.md` ↔ GitHub `skills/web-js-app-implementation/SKILL.md`（必须保持一致）
- 本地 `SKILL.md` ↔ GitHub `skills/yoonup-workflow/SKILL.md`（必须保持一致）
- 修改任一文件时，另一边必须同步更新，禁止只改一处。

## 调用示例

### 示例 1：开发 Python 流程自动化项目
用户：「帮我做一个每天自动抓取销售数据并飞书通知的脚本」
1. 识别技能 → python-app-standard
2. 读取 references/python-app-standard.md 全文
3. 需求拆分提问：数据来源？通知群？定时时间？输出格式？
4. 用户确认后按序执行，实时反馈
5. 末端按校验清单核对，通过后交付

### 示例 2：更新技能并同步到 GitHub
用户：「把 yoonup-workflow 技能更新一下，推到 GitHub」
1. 识别技能 → yoonup-workflow（本技能）
2. 读取本 SKILL.md 全文 + references
3. 需求拆分提问：改哪些内容？是否同步 references？
4. 修改本地技能文件 → 复制到仓库 skills/ → 更新 skills.json → commit & push
5. 末端校验：检查凭证已配置、推送成功、GitHub 内容一致

### 示例 3：网页后台数据抓取
用户：「抓某后台的订单列表，输出影刀能用的二维列表」
1. 识别技能 → web-js-app-implementation
2. 读取 references/web-js-app-implementation.md 全文
3. 需求拆分提问：目标 URL？筛选条件？分页？token 来源？
4. 按序执行：逆向定位接口 → 还原请求 → 获取 token → 编写脚本 → 验证交付
5. 末端校验通过后交付

## 文档维护约定

- 执行过程中发现的**问题/踩坑/新接口经验**，必须同步更新 `references/` 对应文件，禁止只留在对话上下文。
- 校验清单条目格式固定：`- [ID] auto|ai|both 检查内容`，检查方式为 auto（程序自动化检查）/ ai（AI 判断）/ both（程序检查 + AI 复核）。
- 正文与清单保持一致：执行中发现偏差以正文规范为准，并同步修正清单。

## 校验清单

> 执行完成后按本节逐项核对，全部通过方可交付。行格式：`- [ID] 检查方式 检查内容`，检查方式为 auto（程序自动化检查）/ ai（AI 判断）/ both（程序检查 + AI 复核）。
> 本节能被 validator.py 自动解析并驱动 check_result 末端整合校验。

### 技能自检
- [YW00] both 每次调用已先执行技能自检（文件完整性/注册一致性/校验清单可解析/CHECKERS覆盖/本地GitHub同步/代码质量），发现问题已修复并推送

### 技能识别
- [YW01] ai 已正确识别需求所属子技能（python-app-standard / web-js-app-implementation），不确定时已向用户确认

### 规范读取
- [YW02] ai 已读取对应 references 规范文件全文，含末尾校验清单章节，未跳过

### 需求拆分
- [YW03] ai 已向用户提问确认执行顺序，由用户拍板后才开始执行，未自行跳过提问

### 执行反馈
- [YW04] ai 执行中每步开始/完成/失败均实时反馈进度，未憋到最后才汇报
- [YW05] ai 严格按子技能规范做事（目录结构、命名、日志、通知、定时任务等），未自创规范
- [YW06] ai 执行中发现规范未覆盖的新问题，已同步更新对应 references 文件，未只留在对话上下文

### 末端校验
- [YW07] ai 末端校验已按子技能校验清单逐项核对，auto 未通过项已修复，全部通过才交付
- [YW08] ai 交付时已给出产物路径 + 运行验证结果 + 校验通过情况

### 校对质量
- [YW10] ai 用户要求三轮校对时，每轮重新clone仓库、查不同维度、每项贴命令输出和实际数据，未用"全部通过"糊弄
- [YW11] ai 已主动构造破坏用例测试（错误参数/空目录/不存在ID/边界值），未只测正常输入

### 仓库同步
- [YW09] both 技能变更已推送到唯一仓库 Yoonwe/Yoonup 的 skills/ 目录，未创建新仓库，已在 skills.json 注册
