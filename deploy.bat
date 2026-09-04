@echo off
REM Yoonup MCP Windows 自动部署脚本
REM 由 GitHub Actions 调用：上传新代码 zip 后执行本脚本解压重启

cd /d E:\yoonup

echo === Yoonup 自动部署 ===

REM 1. 停止旧服务
echo [1/4] 停止旧服务...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *mcp_server*" 2>nul
timeout /t 2 /nobreak >nul

REM 2. 解压新代码
echo [2/4] 解压新代码...
if exist E:\yoonup\new-version.zip (
    E:\app\python3.12\python.exe -c "import zipfile,os,shutil; zipfile.ZipFile(r'E:\yoonup\new-version.zip').extractall(r'E:\yoonup\temp'); [shutil.move(os.path.join(r'E:\yoonup\temp',f), os.path.join(r'E:\yoonup',f)) for f in os.listdir(r'E:\yoonup\temp')]; shutil.rmtree(r'E:\yoonup\temp'); os.remove(r'E:\yoonup\new-version.zip')"
    echo 代码已更新
) else (
    echo 未找到 new-version.zip，跳过代码更新
)

REM 3. 启动服务
echo [3/4] 启动服务...
start /B E:\app\python3.12\python.exe mcp_server.py --port 8081

REM 4. 验证
echo [4/4] 等待服务启动...
timeout /t 5 /nobreak >nul
netstat -ano | findstr :8081 >nul && (
    echo === 部署完成，服务正常 ===
) || (
    echo === 部署失败，服务未启动 ===
    exit /b 1
)
