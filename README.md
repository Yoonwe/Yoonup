# 流程脚手架工作流引擎

基于 LangGraph 的 AI 编程自动化工作流，按《流程脚手架规范》自动生成 Python 流程代码，并强制执行校验修复循环。

## 工作流程

```
需求解析 → 代码生成（按MD规范） → 校验（自动化+AI） → 条件判断
                                                         ├─ 通过 → 通知 → 结束
                                                         ├─ 不通过且<3次 → 修复（带上次失败项）→ 回到代码生成
                                                         └─ 不通过且≥3次 → 通知用户人工介入 → 结束
```

## 快速开始

### 1. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY 等配置
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 命令行运行
```bash
python main.py "抓取飞书表格订单数据，查询快递100物流状态，回填飞书"
```

### 4. HTTP API 运行
```bash
python api_server.py
# 调用：
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"requirement": "抓取飞书表格数据并写入数据库", "max_attempts": 3}'
```

### 5. MCP 接入（Cursor/豆包等）
在支持MCP的AI工具中添加配置：
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
然后在对话中说"调用流程脚手架生成工作流，需求是XXX"。

### 6. Docker 部署
```bash
docker-compose up -d
```

## 目录结构

```
workflow-engine/
├── main.py              # LangGraph工作流主文件
├── checklist.py         # 从MD抽取的60条校验清单
├── code_validator.py    # 自动化代码校验模块
├── api_server.py        # FastAPI HTTP接口
├── mcp_server.py        # MCP Server接口
├── skills/              # 技能规范文档（MD）
│   └── 流程脚手架规范.md
├── output/              # 生成的流程项目输出目录
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 校验机制

- **自动化检查**：40+条规则，检查文件结构、命名规范、锁机制、日志、飞书凭证等
- **AI辅助检查**：20条语义规则，检查注释完整性、调用顺序、错误处理逻辑等
- **循环修复**：校验不通过自动带上次失败条目重新生成，最多3次
- **人工兜底**：超3次通知用户，列出未通过项

## 添加新技能

1. 将新的MD规范文档放入 `skills/` 目录
2. 在 `checklist.py` 中添加对应的校验条目
3. 重启服务即生效

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| LLM_MODEL | 模型名称 | doubao-1-5-pro-32k |
| LLM_API_KEY | API密钥 | - |
| LLM_BASE_URL | API地址 | 豆包ark地址 |
| MAX_ATTEMPTS | 最大修复次数 | 3 |
| FEISHU_WEBHOOK | 飞书通知webhook | - |
| PORT | HTTP服务端口 | 8000 |
