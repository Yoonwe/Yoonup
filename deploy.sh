#!/bin/bash
# Yoonup MCP 服务自动部署脚本
# 用法：./deploy.sh
set -e

cd "$(dirname "$0")"

echo "=== Yoonup 自动部署 ==="

# 1. 拉取最新代码
echo "[1/4] 拉取最新代码..."
git pull origin main

# 2. 记录当前镜像ID（用于回滚）
OLD_IMAGE=$(docker images --format "{{.ID}}" yoonup-yoonup-mcp:latest 2>/dev/null || echo "")
echo "[2/4] 当前镜像: ${OLD_IMAGE:-无}"

# 3. 构建并重启
echo "[3/4] 构建并重启服务..."
docker compose up -d --build

# 4. 等待启动并验证
echo "[4/4] 等待服务启动..."
for i in $(seq 1 15); do
    sleep 2
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/mcp 2>/dev/null | grep -q "200\|400\|405"; then
        echo "✅ 服务启动成功，健康检查通过"
        echo "=== 部署完成 ==="
        docker compose ps
        exit 0
    fi
    echo "  等待中... ($i/15)"
done

# 验证失败，回滚
echo "❌ 服务启动失败，开始回滚..."
if [ -n "$OLD_IMAGE" ]; then
    docker tag "$OLD_IMAGE" yoonup-yoonup-mcp:latest 2>/dev/null || true
    docker compose up -d
    echo "✅ 已回滚到上一个版本"
else
    echo "⚠️  无旧镜像可回滚，请手动检查"
fi
docker compose logs --tail=30
exit 1
