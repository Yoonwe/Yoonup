# Yoonup MCP 服务部署指南

## 一次性部署

### 1. 服务器准备
- 云服务器（2核2G以上，Ubuntu 22.04推荐）
- 安装 Docker + Docker Compose
- 开放 8081 端口

### 2. 部署
```bash
ssh user@your-server
git clone https://github.com/Yoonwe/Yoonup.git /opt/yoonup
cd /opt/yoonup
docker compose up -d --build
```

### 3. 验证
```bash
curl http://localhost:8081/mcp
# 或浏览器打开 http://<服务器IP>:8081/mcp
```

### 4. 接入AI工具
在 Dify/Cursor/豆包等工具的 MCP 配置中填入：
```
http://<服务器IP>:8081/mcp
```

## 自动更新（推荐）

### 配置 GitHub Actions 自动部署
1. GitHub 仓库 → Settings → Secrets and variables → Actions
2. 添加3个 Secrets：
   - `SERVER_HOST`: 你的服务器IP
   - `SERVER_USER`: SSH用户名
   - `SERVER_SSH_KEY`: SSH私钥内容
3. 配置后，每次 push 到 main 分支自动部署

### 手动更新
```bash
ssh user@your-server
cd /opt/yoonup
./deploy.sh
```
deploy.sh 会自动：拉取代码 → 构建重启 → 健康检查 → 失败自动回滚

## 服务不中断说明
- 更新时旧容器继续服务，新容器构建完成后才切换
- 切换中断约3-5秒（容器启动时间）
- 健康检查失败自动回滚到上一个版本
- MCP客户端会自动重试，用户无感知
