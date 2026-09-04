# Yoonup 使用手册 / Yoonup Usage Guide

> 本文档面向 **AI 执行者** 和 **人类运维人员**，中英双语。
> This document is for both **AI agents** and **human operators**, bilingual.

---

## 目录 / Table of Contents

1. [项目简介 / Introduction](#1-项目简介--introduction)
2. [核心概念 / Core Concepts](#2-核心概念--core-concepts)
3. [MCP 服务部署（Windows）/ MCP Service Deployment (Windows)](#3-mcp-服务部署windows--mcp-service-deployment-windows)
4. [MCP 工具说明 / MCP Tools Reference](#4-mcp-工具说明--mcp-tools-reference)
5. [技能调用流程 / Skill Invocation Workflow](#5-技能调用流程--skill-invocation-workflow)
6. [自动部署配置 / Auto Deployment](#6-自动部署配置--auto-deployment)
7. [常见问题与故障排查 / FAQ & Troubleshooting](#7-常见问题与故障排查--faq--troubleshooting)
8. [版本记录 / Changelog](#8-版本记录--changelog)

---

## 1. 项目简介 / Introduction

### 中文

Yoonup 是一套「工作流约定 + 技能规范库 + 远程 MCP 服务」三件套，目标是让任何 AI 产品（豆包、Cursor、Dify、Marvis 等）在执行开发任务时，都能严格按照规范流程做事，杜绝"不提问就开工、不校验就交付、校对走过场"等问题。

**核心价值：**
- 技能规范集中管理，更新后所有 AI 立即生效
- 执行流程强制卡点（不提问不开工、不校验不交付）
- 末端校验确定性输出，AI 无法糊弄
- 远程 MCP 服务 7×24 在线，不依赖某台本地电脑

### English

Yoonup is a three-part system: **workflow conventions + skill specification library + remote MCP service**. Its goal is to ensure any AI product (Doubao, Cursor, Dify, Marvis, etc.) follows standardized workflows when executing development tasks, eliminating issues like "starting work without asking", "delivering without verification", and "superficial review".

**Core Value:**
- Centralized skill management, updates apply to all AIs instantly
- Mandatory checkpoints in workflow (no work without asking, no delivery without verification)
- Deterministic end-check output, AI cannot fake results
- Remote MCP service 24/7, not dependent on any local machine

---

## 2. 核心概念 / Core Concepts

### 中文

| 概念 | 说明 |
|------|------|
| **技能 (Skill)** | 一个 MD 格式的操作指南，包含规范正文 + 末尾校验清单 |
| **MCP 服务** | 远程运行的服务，暴露 4 个工具，AI 通过 HTTP 调用 |
| **校验清单** | 技能 MD 末尾的检查项，分 `auto`（程序检查）/ `ai`（AI判断）/ `both`（两者） |
| **3条铁律** | 不提问不开工、不校验不交付、用户质疑先讨论再动手 |
| **5步流程** | 提问确认 → 读取规范 → 生成计划 → 按序执行 → 校验交付 |

### English

| Concept | Description |
|---------|-------------|
| **Skill** | A Markdown operation guide containing spec body + checklist at the end |
| **MCP Service** | Remotely running service exposing 4 tools, AI invokes via HTTP |
| **Checklist** | Check items at end of skill MD, categorized as `auto` / `ai` / `both` |
| **3 Iron Rules** | No work without asking, no delivery without verification, discuss before acting when user questions |
| **5-Step Workflow** | Ask → Read spec → Generate plan → Execute in order → Verify & deliver |

---

## 3. MCP 服务部署（Windows）/ MCP Service Deployment (Windows)

### 中文

#### 3.1 环境要求 / Environment Requirements

- Windows Server 2016+ 或 Windows 10/11
- Python 3.10+（推荐 3.12）
- 公网 IP 或可被 AI 工具访问的网络地址
- 至少 1GB 可用内存

#### 3.2 部署步骤 / Deployment Steps

**第1步：下载代码 / Download Code**

由于国内服务器可能无法直接访问 GitHub，推荐从本地打包后上传：

```bash
# 本地打包 / Package locally
git clone https://github.com/Yoonwe/Yoonup.git
cd Yoonup
zip -r yoonup-deploy.zip . -x "*.git*"

# 通过 SFTP 或远程桌面上传到服务器 / Upload to server via SFTP or RDP
# 解压到 E:\yoonup / Extract to E:\yoonup
```

**第2步：安装 Python 依赖 / Install Python Dependencies**

```cmd
cd /d E:\yoonup
E:\app\python3.12\python.exe -m pip install mcp fastapi uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> ⚠️ **重要：必须安装 mcp 1.x 版本**，mcp 2.x 不兼容 FastMCP API。如果已安装 2.x，请降级：
> ```cmd
> E:\app\python3.12\python.exe -m pip install "mcp<2" -i https://pypi.tuna.tsinghua.edu.cn/simple
> ```

**第3步：配置 Host 头允许 / Configure Host Header Allowance**

`mcp_server.py` 已默认配置允许所有 Host 访问（关闭了 FastMCP 的 DNS 重绑定保护）。如果需要手动配置，确保以下代码存在：

```python
mcp.settings.transport_security.enable_dns_rebinding_protection = False
mcp.settings.transport_security.allowed_hosts = ["*"]
mcp.settings.transport_security.allowed_origins = ["*"]
```

**第4步：启动服务 / Start Service**

```cmd
cd /d E:\yoonup
E:\app\python3.12\python.exe mcp_server.py --port 8081
```

**第5步：配置开机自启 / Configure Auto-Start**

使用 Windows 任务计划程序：

```cmd
# 创建启动脚本 / Create startup script
echo @echo off > E:\yoonup\start.bat
echo cd /d E:\yoonup >> E:\yoonup\start.bat
echo E:\app\python3.12\python.exe mcp_server.py --port 8081 >> E:\yoonup\start.bat

# 创建任务计划 / Create scheduled task
schtasks /create /tn "YoonupMCP" /tr "E:\yoonup\start.bat" /sc onstart /ru admin2 /rp YourPassword /f
```

**第6步：开放防火墙 / Open Firewall**

```cmd
netsh advfirewall firewall add rule name="Yoonup MCP" dir=in action=allow protocol=TCP localport=8081
```

**第7步：云服务商安全组 / Cloud Provider Security Group**

在云服务商控制台（阿里云/腾讯云/华为云等）的安全组**入方向**添加规则：
- 协议：TCP
- 端口：8081
- 来源：0.0.0.0/0

#### 3.3 验证部署 / Verify Deployment

```cmd
:: 本地验证 / Local verification
curl -s -o nul -w "%{http_code}" http://localhost:8081/mcp
:: 应返回 406（正常，因为 curl 不支持 MCP 流式协议）/ Should return 406

:: 用 Python 发送完整 MCP 请求 / Send full MCP request with Python
python -c "import http.client,json; c=http.client.HTTPConnection('localhost',8081,timeout=5); c.request('POST','/mcp',body=json.dumps({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'test','version':'1.0'}}}),headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}); r=c.getresponse(); print(r.status, r.read().decode()[:200])"
:: 应返回 200 和包含 serverInfo 的 JSON / Should return 200 with JSON containing serverInfo
```

### English

#### 3.1 Environment Requirements

- Windows Server 2016+ or Windows 10/11
- Python 3.10+ (3.12 recommended)
- Public IP or network address accessible by AI tools
- At least 1GB available RAM

#### 3.2 Deployment Steps

**Step 1: Download Code**

Servers in China may not access GitHub directly. Package locally and upload:

```bash
# Package locally
git clone https://github.com/Yoonwe/Yoonup.git
cd Yoonup
zip -r yoonup-deploy.zip . -x "*.git*"

# Upload to server via SFTP or RDP
# Extract to E:\yoonup
```

**Step 2: Install Python Dependencies**

```cmd
cd /d E:\yoonup
E:\app\python3.12\python.exe -m pip install mcp fastapi uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> ⚠️ **Important: Must install mcp 1.x**. mcp 2.x is incompatible with FastMCP API. If 2.x is installed, downgrade:
> ```cmd
> E:\app\python3.12\python.exe -m pip install "mcp<2" -i https://pypi.tuna.tsinghua.edu.cn/simple
> ```

**Step 3: Configure Host Header Allowance**

`mcp_server.py` already allows all Hosts by default (FastMCP DNS rebinding protection disabled). If configuring manually, ensure:

```python
mcp.settings.transport_security.enable_dns_rebinding_protection = False
mcp.settings.transport_security.allowed_hosts = ["*"]
mcp.settings.transport_security.allowed_origins = ["*"]
```

**Step 4: Start Service**

```cmd
cd /d E:\yoonup
E:\app\python3.12\python.exe mcp_server.py --port 8081
```

**Step 5: Configure Auto-Start**

Use Windows Task Scheduler:

```cmd
:: Create startup script
echo @echo off > E:\yoonup\start.bat
echo cd /d E:\yoonup >> E:\yoonup\start.bat
echo E:\app\python3.12\python.exe mcp_server.py --port 8081 >> E:\yoonup\start.bat

:: Create scheduled task
schtasks /create /tn "YoonupMCP" /tr "E:\yoonup\start.bat" /sc onstart /ru admin2 /rp YourPassword /f
```

**Step 6: Open Firewall**

```cmd
netsh advfirewall firewall add rule name="Yoonup MCP" dir=in action=allow protocol=TCP localport=8081
```

**Step 7: Cloud Provider Security Group**

Add an **inbound** rule in your cloud provider console:
- Protocol: TCP
- Port: 8081
- Source: 0.0.0.0/0

#### 3.3 Verify Deployment

```cmd
:: Local verification
curl -s -o nul -w "%{http_code}" http://localhost:8081/mcp
:: Should return 406 (normal - curl doesn't support MCP streaming protocol)

:: Send full MCP request with Python
python -c "import http.client,json; c=http.client.HTTPConnection('localhost',8081,timeout=5); c.request('POST','/mcp',body=json.dumps({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'test','version':'1.0'}}}),headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}); r=c.getresponse(); print(r.status, r.read().decode()[:200])"
:: Should return 200 with JSON containing serverInfo
```

---

## 4. MCP 工具说明 / MCP Tools Reference

### 中文

MCP 服务暴露 4 个工具，AI 执行任务时必须按流程调用。

#### 4.1 list_skills

**用途**：列出所有可用技能。

**参数**：无

**返回示例**：
```json
{
  "skills": [
    {"id": "yoonup-workflow", "name": "Yoonup工作流", "description": "..."},
    {"id": "python-app-standard", "name": "Python流程标准", "description": "..."},
    {"id": "web-js-app-implementation", "name": "网页JS抓取", "description": "..."}
  ]
}
```

**调用时机**：不确定需求属于哪个技能时。

#### 4.2 get_skill_spec

**用途**：获取指定技能的完整规范全文与校验清单。

**参数**：
- `skill_id` (string, 必填)：技能 ID
- `include_checklist` (bool, 可选，默认 true)：是否返回校验清单

**返回**：`skill_id` / `skill_name` / `description` / `spec`（MD全文）/ `checklist`（结构化）/ `checklist_text`（AI核对文本）

**调用时机**：第1步读取规范，**禁止跳过**。

#### 4.3 plan_requirement

**用途**：按技能规范生成执行计划骨架（规则引擎，不依赖 LLM）。

**参数**：
- `requirement` (string, 必填)：用户原始需求
- `skill_id` (string, 可选)：不传时按关键词自动识别

**返回**：`skill_id` / `skill_name` / `plan_steps`（分步计划）/ `questions_to_user`（需向用户确认的事项）/ `note`

**调用时机**：第2步生成计划，拿到计划后必须向用户提问确认执行顺序。

#### 4.4 check_result

**用途**：对执行结果做末端整合校验，按技能校验清单逐项核对。

**参数**：
- `project_dir` (string, 必填)：执行结果所在目录的绝对路径
- `skill_id` (string, 可选)：不传则按全部技能校验
- `include_details` (bool, 可选，默认 true)：是否返回 AI 核对清单

**返回**：`auto_passed` / `auto_failed` / `all_auto_passed` / `ai_checklist` / `summary`

**调用时机**：第4步末端校验，**校验不通过禁止交付**。

### English

The MCP service exposes 4 tools that AI must invoke following the workflow.

#### 4.1 list_skills

**Purpose**: List all available skills.

**Parameters**: None

**Returns**: List of skills with id/name/description.

**When to call**: When unsure which skill the requirement belongs to.

#### 4.2 get_skill_spec

**Purpose**: Get full specification and checklist for a skill.

**Parameters**:
- `skill_id` (string, required): Skill ID
- `include_checklist` (bool, optional, default true): Whether to return checklist

**Returns**: skill_id / skill_name / description / spec (full MD) / checklist (structured) / checklist_text

**When to call**: Step 1 - Read spec, **must not skip**.

#### 4.3 plan_requirement

**Purpose**: Generate execution plan skeleton (rule engine, no LLM dependency).

**Parameters**:
- `requirement` (string, required): User's original requirement
- `skill_id` (string, optional): Auto-detected by keywords if not provided

**Returns**: skill_id / skill_name / plan_steps / questions_to_user / note

**When to call**: Step 2 - Generate plan. Must ask user to confirm execution order after getting plan.

#### 4.4 check_result

**Purpose**: End-to-end verification of execution results against skill checklist.

**Parameters**:
- `project_dir` (string, required): Absolute path to execution result directory
- `skill_id` (string, optional): All skills if not provided
- `include_details` (bool, optional, default true): Whether to return AI checklist

**Returns**: auto_passed / auto_failed / all_auto_passed / ai_checklist / summary

**When to call**: Step 4 - End verification. **Delivery prohibited if verification fails**.

---

## 5. 技能调用流程 / Skill Invocation Workflow

### 中文

#### ⚠️ 3条铁律（违反任意一条立即停止并报告）

1. **不提问确认执行顺序，禁止开工**
2. **不运行校验通过，禁止交付**
3. **用户质疑时先讨论再动手，禁止莽做**

#### 5步执行流程

| 步骤 | 动作 | MCP工具 | 卡点 |
|------|------|---------|------|
| 第0步 | 向用户提问确认执行顺序 | - | 用户回答后才能继续 |
| 第1步 | 读取技能规范全文 | `get_skill_spec` | 禁止不读规范直接开干 |
| 第2步 | 生成执行计划 | `plan_requirement` | 必须向用户确认顺序 |
| 第3步 | 按序执行，每步反馈进度 | - | 禁止憋到最后才汇报 |
| 第4步 | 末端校验，通过才交付 | `check_result` | 校验不通过禁止交付 |

#### 交付前自检模板（必须填完）

```
1. 我提问确认执行顺序了吗？用户回答：___
2. 我读取规范全文了吗？___
3. 我每步反馈进度了吗？___
4. 校验结果：check_result all_auto_passed=___（必须为true）
5. 发现的问题及修复：___
6. 推送的提交号：___
```

### English

#### ⚠️ 3 Iron Rules (Stop and report if any is violated)

1. **No work without confirming execution order with user**
2. **No delivery without passing verification**
3. **Discuss before acting when user questions, no reckless action**

#### 5-Step Workflow

| Step | Action | MCP Tool | Checkpoint |
|------|--------|----------|------------|
| Step 0 | Ask user to confirm execution order | - | Cannot proceed until user answers |
| Step 1 | Read full skill specification | `get_skill_spec` | Must not start without reading |
| Step 2 | Generate execution plan | `plan_requirement` | Must confirm order with user |
| Step 3 | Execute in order, report progress each step | - | Must not wait until end to report |
| Step 4 | End verification, deliver only if passed | `check_result` | Delivery prohibited if failed |

#### Pre-Delivery Self-Check Template (must complete)

```
1. Did I ask to confirm execution order? User answer: ___
2. Did I read full spec? ___
3. Did I report progress each step? ___
4. Verification result: check_result all_auto_passed=___ (must be true)
5. Issues found and fixed: ___
6. Commit hash pushed: ___
```

---

## 6. 自动部署配置 / Auto Deployment

### 中文

#### 6.1 工作原理 / How It Works

每次 push 到 GitHub main 分支，GitHub Actions 自动：
1. 打包代码为 zip
2. 通过 SCP 上传到服务器 `E:\yoonup\new-version.zip`
3. 通过 SSH 执行服务器上的 `deploy.bat`
4. `deploy.bat` 自动：停止旧服务 → 解压新代码 → 启动服务 → 验证

#### 6.2 配置步骤 / Configuration Steps

**第1步：GitHub Secrets 配置**

仓库 → Settings → Secrets and variables → Actions，新增 3 个 Secrets：

| Secret名 | 值 |
|----------|-----|
| `SERVER_HOST` | 服务器公网IP，如 `171.111.219.203` |
| `SERVER_USER` | Windows用户名，如 `admin2` |
| `SERVER_PASSWORD` | Windows登录密码 |

**第2步：确认 deploy.bat 存在于服务器**

`deploy.bat` 应位于 `E:\yoonup\deploy.bat`，内容包含：停止服务、解压、启动、验证。

**第3步：触发部署 / Trigger Deployment**

```bash
git add -A
git commit -m "update: ..."
git push origin main
```

push 后自动触发，可在 GitHub → Actions 页面查看部署进度。

### English

#### 6.1 How It Works

On every push to GitHub main branch, GitHub Actions automatically:
1. Package code as zip
2. Upload to server `E:\yoonup\new-version.zip` via SCP
3. Execute `deploy.bat` on server via SSH
4. `deploy.bat` automatically: stop old service → extract new code → start service → verify

#### 6.2 Configuration Steps

**Step 1: Configure GitHub Secrets**

Repo → Settings → Secrets and variables → Actions, add 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `SERVER_HOST` | Server public IP, e.g. `171.111.219.203` |
| `SERVER_USER` | Windows username, e.g. `admin2` |
| `SERVER_PASSWORD` | Windows login password |

**Step 2: Ensure deploy.bat exists on server**

`deploy.bat` should be at `E:\yoonup\deploy.bat`, containing: stop service, extract, start, verify.

**Step 3: Trigger Deployment**

```bash
git add -A
git commit -m "update: ..."
git push origin main
```

Auto-triggered after push. Check progress at GitHub → Actions page.

---

## 7. 常见问题与故障排查 / FAQ & Troubleshooting

### 中文

#### Q1: 公网访问 MCP 地址超时 / Public access to MCP address times out

**可能原因及排查步骤：**

1. **服务是否运行？**
   ```cmd
   netstat -ano | findstr :8081
   ```
   应看到 `0.0.0.0:8081 LISTENING`。如果没有，重新启动服务。

2. **Windows防火墙是否开放？**
   ```cmd
   netsh advfirewall firewall show rule name="Yoonup MCP"
   ```
   没有就添加：`netsh advfirewall firewall add rule name="Yoonup MCP" dir=in action=allow protocol=TCP localport=8081`

3. **云服务商安全组是否开放入方向？**
   登录云控制台检查安全组入方向规则，确保 TCP 8081 来源 0.0.0.0/0。

4. **用 nc 测试 TCP 连接（比 curl 准确）：**
   ```bash
   nc -zv -w 3 171.111.219.203 8081
   ```
   - 如果 `succeeded` → TCP通，问题在HTTP层
   - 如果 `timed out` → 安全组或防火墙问题

5. **⚠️ curl 测试 MCP 会误报超时！**
   MCP 使用 `text/event-stream` 流式响应，普通 curl 可能挂起。必须用 Python `http.client` 或专业 MCP 客户端测试：
   ```python
   import http.client, json
   c = http.client.HTTPConnection("171.111.219.203", 8081, timeout=10)
   c.request("POST", "/mcp", body=json.dumps({...}), headers={"Content-Type":"application/json","Accept":"application/json, text/event-stream"})
   r = c.getresponse()
   print(r.status)  # 应为 200
   ```

#### Q2: 访问返回 "Invalid Host header" / Access returns "Invalid Host header"

**原因**：FastMCP 默认开启 DNS 重绑定保护，只允许 `localhost` / `127.0.0.1` / `[::1]` 作为 Host 头，公网IP被拒绝。

**解决**：在 `mcp_server.py` 的 `mcp.run()` 之前添加：
```python
mcp.settings.transport_security.enable_dns_rebinding_protection = False
mcp.settings.transport_security.allowed_hosts = ["*"]
mcp.settings.transport_security.allowed_origins = ["*"]
```

#### Q3: 启动报错 `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`

**原因**：安装了 mcp 2.x，FastMCP 在 2.x 中被重命名为 MCPServer。

**解决**：降级到 mcp 1.x：
```cmd
pip install "mcp<2"
```

#### Q4: 国内服务器 pip 安装超时 / pip install times out on China servers

**解决**：使用清华镜像源：
```cmd
pip install mcp fastapi uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

#### Q5: 国内服务器无法 git clone GitHub / Cannot git clone GitHub from China server

**解决**：从本地打包代码，通过 SFTP/远程桌面上传到服务器解压。不要在服务器上直接 git clone。

#### Q6: 服务重启后自动消失 / Service disappears after restart

**原因**：没有配置开机自启，或任务计划程序配置错误。

**解决**：
```cmd
schtasks /create /tn "YoonupMCP" /tr "E:\yoonup\start.bat" /sc onstart /ru admin2 /rp YourPassword /f
```
确保 `/ru` 和 `/rp` 参数正确（用户名和密码）。

#### Q7: GitHub Actions 推送 workflow 文件被拒 / Push of workflow file rejected

**原因**：GitHub Personal Access Token 没有 `workflow` 权限。

**解决**：重新生成 token，勾选 `workflow` 权限，更新本地 git 凭证。

### English

#### Q1: Public access to MCP address times out

**Possible causes and troubleshooting steps:**

1. **Is the service running?**
   ```cmd
   netstat -ano | findstr :8081
   ```
   Should show `0.0.0.0:8081 LISTENING`. If not, restart service.

2. **Is Windows firewall open?**
   ```cmd
   netsh advfirewall firewall show rule name="Yoonup MCP"
   ```
   Add if missing: `netsh advfirewall firewall add rule name="Yoonup MCP" dir=in action=allow protocol=TCP localport=8081`

3. **Is cloud provider security group inbound open?**
   Check cloud console for inbound rule TCP 8081 source 0.0.0.0/0.

4. **Test TCP connection with nc (more accurate than curl):**
   ```bash
   nc -zv -w 3 171.111.219.203 8081
   ```
   - If `succeeded` → TCP works, issue at HTTP layer
   - If `timed out` → security group or firewall issue

5. **⚠️ curl testing MCP may falsely report timeout!**
   MCP uses `text/event-stream` streaming response, regular curl may hang. Must use Python `http.client` or proper MCP client:
   ```python
   import http.client, json
   c = http.client.HTTPConnection("171.111.219.203", 8081, timeout=10)
   c.request("POST", "/mcp", body=json.dumps({...}), headers={"Content-Type":"application/json","Accept":"application/json, text/event-stream"})
   r = c.getresponse()
   print(r.status)  # Should be 200
   ```

#### Q2: Access returns "Invalid Host header"

**Cause**: FastMCP enables DNS rebinding protection by default, only allowing `localhost` / `127.0.0.1` / `[::1]` as Host header. Public IPs are rejected.

**Fix**: Add before `mcp.run()` in `mcp_server.py`:
```python
mcp.settings.transport_security.enable_dns_rebinding_protection = False
mcp.settings.transport_security.allowed_hosts = ["*"]
mcp.settings.transport_security.allowed_origins = ["*"]
```

#### Q3: Startup error `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`

**Cause**: mcp 2.x installed, FastMCP was renamed to MCPServer in 2.x.

**Fix**: Downgrade to mcp 1.x:
```cmd
pip install "mcp<2"
```

#### Q4: pip install times out on China servers

**Fix**: Use Tsinghua mirror:
```cmd
pip install mcp fastapi uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

#### Q5: Cannot git clone GitHub from China server

**Fix**: Package code locally, upload to server via SFTP/RDP and extract. Do not git clone directly on server.

#### Q6: Service disappears after restart

**Cause**: No auto-start configured, or Task Scheduler misconfigured.

**Fix**:
```cmd
schtasks /create /tn "YoonupMCP" /tr "E:\yoonup\start.bat" /sc onstart /ru admin2 /rp YourPassword /f
```
Ensure `/ru` and `/rp` parameters are correct (username and password).

#### Q7: GitHub Actions push of workflow file rejected

**Cause**: GitHub Personal Access Token lacks `workflow` scope.

**Fix**: Regenerate token with `workflow` scope checked, update local git credentials.

---

## 8. 版本记录 / Changelog

### 中文

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-09-04 | 初始版本，MCP服务部署到Windows服务器，公网访问调通 |

**本次部署踩坑记录（防止再犯）：**
1. FastMCP 默认 DNS 重绑定保护导致公网IP访问被拒 → 已在代码中关闭
2. curl 不支持 MCP 流式响应，误判为服务不通 → 文档中明确用 Python 测试
3. mcp 2.x 不兼容 FastMCP API → 必须安装 mcp<2
4. 国内服务器访问 GitHub/PyPI 超时 → 用本地打包上传 + 清华镜像
5. Windows 服务器无 git/docker → 直接用 Python 运行 + 任务计划程序自启
6. GitHub token 需 workflow 权限才能推送 .github/workflows/ 文件

### English

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-04 | Initial release, MCP service deployed on Windows server, public access verified |

**Deployment pitfalls recorded (to prevent recurrence):**
1. FastMCP default DNS rebinding protection rejects public IP access → disabled in code
2. curl doesn't support MCP streaming response, falsely reports service down → document explicitly to use Python for testing
3. mcp 2.x incompatible with FastMCP API → must install mcp<2
4. China servers timeout accessing GitHub/PyPI → use local package upload + Tsinghua mirror
5. Windows servers lack git/docker → run directly with Python + Task Scheduler auto-start
6. GitHub token needs workflow scope to push .github/workflows/ files

---

## 附录 / Appendix

### 关键文件说明 / Key Files

| 文件 | 用途 |
|------|------|
| `mcp_server.py` | MCP 服务主程序，暴露4个工具 |
| `validator.py` | 校验器，解析校验清单、自动化检查、计划生成 |
| `skills.json` | 技能注册表 |
| `skills/*/SKILL.md` | 各技能规范文档 |
| `audit.py` | 自动化校对脚本，37项检查 |
| `deploy.bat` | Windows 自动部署脚本 |
| `start.bat` | 服务启动脚本 |
| `.github/workflows/deploy.yml` | GitHub Actions 自动部署配置 |
| `USAGE.md` | 本文档 |

### MCP 接入地址 / MCP Endpoint

```
http://171.111.219.203:8081/mcp
```
