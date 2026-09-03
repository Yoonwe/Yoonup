---
name: yoonup-workflow
description: 按 Yoonup 工作流规范稳定执行任务：提问→读规范→生成计划→执行→校验交付。当用户要求开发/修改 Python 流程自动化项目或网页后台数据抓取时使用。
---

# Yoonup 工作流

⚠️ **3条铁律（违反任意一条立即停止并向用户报告）**
1. 不提问确认执行顺序，禁止开工
2. 不运行校验通过，禁止交付
3. 用户质疑时先讨论再动手，禁止莽做

## 5步执行流程（每步必须完成才能进入下一步）

### 第0步：提问确认
- 向用户提问确认执行顺序和关键需求
- **用户回答后才能进入下一步**，禁止自行跳过

### 第1步：读取规范
- 调用 MCP 工具 `get_skill_spec(skill_id)` 获取对应技能的完整规范
- 或读取 `references/` 下对应规范文件全文
- 禁止不读规范直接开干

### 第2步：生成计划
- 调用 MCP 工具 `plan_requirement(requirement, skill_id)` 获取执行计划骨架
- 结合用户需求细化步骤，按用户确认的顺序执行

### 第3步：按序执行
- 严格按技能规范做事（目录结构、命名、日志、通知、定时任务等）
- **每步开始/完成/失败必须实时反馈进度**，禁止憋到最后才汇报
- 执行中发现规范未覆盖的问题，同步更新 references 并推送

### 第4步：校验交付
- 调用 MCP 工具 `check_result(project_dir, skill_id)` 做末端校验
- 或运行 `python3 audit.py` 做完整校对
- **校验不通过禁止交付**，必须修复后重跑
- 交付时必须输出：产物路径 + 校验结果（退出码必须为0）+ 推送的提交号

## 技能选择

| 需求 | skill_id | 规范文件 |
|------|----------|----------|
| Python 流程自动化（多子流程、飞书通知、定时任务、运行记录） | python-app-standard | references/python-app-standard.md |
| 网页后台数据抓取（JS逆向/接口直连，输出影刀二维列表） | web-js-app-implementation | references/web-js-app-implementation.md |
| 技能本身的维护/更新/同步 | yoonup-workflow | references/core-conventions.md |

## 远程 MCP 工具

若已部署 Yoonup MCP 服务（地址 `http://<服务器IP>:8000/mcp`），必须调用以下工具：
- `list_skills`：查看可用技能
- `get_skill_spec`：获取技能规范全文
- `plan_requirement`：生成执行计划
- `check_result`：末端校验

无 MCP 时，直接读取 `references/` 规范文件执行同样流程。

## 交付前自检模板（必须填完才能说"完成了"）

```
1. 我提问确认执行顺序了吗？用户回答：___
2. 我读取规范全文了吗？___
3. 我每步反馈进度了吗？___
4. 校验结果：audit.py 退出码 ___（必须为0）/ check_result all_auto_passed=___
5. 发现的问题及修复：___
6. 推送的提交号：___
```

## 详细规范

全部详细规范（执行纪律、仓库同步、凭证处理、校对维度清单、常见错误等）见 `references/core-conventions.md`。
