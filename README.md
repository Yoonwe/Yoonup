# 流程脚手架工作流引擎

基于 LangGraph 的 AI 编程自动化工作流。按技能规范自动生成代码，强制执行校验修复循环，最多3次，超次数通知用户。

## 工作流程

```
需求解析 → 代码生成（按技能规范） → 校验（自动化+AI） → 条件判断
                                                         ├─ 通过 → 通知 → 结束
                                                         ├─ 不通过且<3次 → 修复（带上次失败项）→ 回到代码生成
                                                         └─ 不通过且≥3次 → 通知用户人工介入 → 结束
```

## 技能列表

| 技能ID | 名称 | 校验规则数 | 适用场景 |
|--------|------|-----------|---------|
| `python-app` | python应用规范技能 | 61条 | 多步骤流程项目：飞书表格读写、API调用、通知、定时任务 |
| `web-js-app` | web-js应用实施技能 | 16条 | 网页后台数据抓取：JS逆向、接口直连、CDP调试 |

不传技能ID时自动识别：含"网页/JS逆向/CDP/接口直连/浏览器"等关键词用 `web-js-app`，其余默认 `python-app`。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY
```

### 3. 命令行运行

```bash
# 自动识别技能（推荐）
python main.py "抓取飞书表格订单数据，查询快递100物流状态，回填飞书"

# 指定技能
python main.py "通过JS逆向获取电商后台订单数据" --skill-id web-js-app

# 查看可用技能
python main.py --list-skills
```

### 4. HTTP API 运行

```bash
python api_server.py
```

调用：

```bash
# 自动识别技能
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"requirement": "抓取飞书表格数据并写入数据库"}'

# 指定技能
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"requirement": "JS逆向抓取网页后台数据", "skill_id": "web-js-app"}'

# 查看技能列表
curl http://localhost:8000/skills
```

### 5. MCP 接入（Cursor/豆包等）

```json
{
  "mcpServers": {
    "流程脚手架": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

可用工具：`generate_workflow(requirement, skill_id, max_attempts)`、`list_skills()`、`check_project(project_dir, skill_id)`

## 目录结构

```
workflow-engine/
├── main.py              # LangGraph工作流主文件
├── checklist.py         # 校验清单（77条，按技能分组）
├── code_validator.py    # 自动化代码校验模块
├── api_server.py        # FastAPI HTTP接口
├── mcp_server.py        # MCP Server接口
├── skills.json          # 技能注册表（ID、名称、MD文件、校验类别）
├── skills/              # 技能规范文档
│   ├── python应用规范.md
│   └── web-js应用实施.md
├── output/              # 生成的项目输出目录
├── AGENTS.md            # AI操作规范（修改同步GitHub等）
├── requirements.txt
└── .env.example
```

## 添加新技能

1. 将MD规范文档放入 `skills/` 目录
2. 在 `skills.json` 中注册：填写 `id`、`name`、`file`、`description`、`check_categories`
3. 在 `checklist.py` 的 `CHECKLIST` 中添加对应校验条目，`category` 与 `skills.json` 的 `check_categories` 对应
4. 在 `main.py` 的 `detect_skill()` 中添加自动识别关键词（可选）
5. 提交并推送到GitHub

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| LLM_MODEL | 模型名称 | doubao-1-5-pro-32k |
| LLM_API_KEY | API密钥 | - |
| LLM_BASE_URL | API地址 | 豆包ark地址 |
| MAX_ATTEMPTS | 最大修复次数 | 3 |
| FEISHU_WEBHOOK | 飞书通知webhook | - |
| PORT | HTTP服务端口 | 8000 |
