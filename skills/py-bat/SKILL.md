---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_d1435da2aa5b11f1be88525400aeaaa3
    ReservedCode1: V3yPmZZoe7MRUUrRdGy9l2S3P+nq9rTR+T/jZAoQ8zkBaY8KCzjezi1YxVuOD2wXDflfJJUk/aHkozhPFMaz91S9OJk7DZdqo1QHLpkl8X+AAzzWyQtcDHlDkbrnKEWF2+1hLOi3u40HN2QlvoGlZsA7FF/ER9AfwVhXWdKJnx1O02LK1bWBPTy7KOI=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_d1435da2aa5b11f1be88525400aeaaa3
    ReservedCode2: V3yPmZZoe7MRUUrRdGy9l2S3P+nq9rTR+T/jZAoQ8zkBaY8KCzjezi1YxVuOD2wXDflfJJUk/aHkozhPFMaz91S9OJk7DZdqo1QHLpkl8X+AAzzWyQtcDHlDkbrnKEWF2+1hLOi3u40HN2QlvoGlZsA7FF/ER9AfwVhXWdKJnx1O02LK1bWBPTy7KOI=
---

# py-bat（run.bat 手动运行入口）

> 原子子技能（promoted）。原 python-app-standard「定时执行 - run.bat 中转脚本」章节。run.bat 定位：**仅手动/诊断入口，不参与定时**——供用户手动双击运行与排查问题；Windows 计划任务不经过它（见 py-cron）。

## 标准模板

```bat

@echo off
chcp 65001 >nul
cd /d "%~dp0"
REM Disable __pycache__ generation
set "PYTHONDONTWRITEBYTECODE=1"
set "PY=C:\Users\EDY\AppData\Local\Programs\Python\Python311\python.exe"
if not exist "%PY%" (
    echo [ERROR] Python not found: %PY%
    exit /b 1
)
"%PY%" "%~dp0主流程.py"
exit /b %ERRORLEVEL%
```

## 硬性规则

1. **Python 解释器必须使用独立安装的 Python**，严禁依赖 Marvis 内置 Python 或动态查找其路径——Marvis 升级会导致路径失效、全流程停摆。独立 Python 通过 `winget install Python.Python.3.11` 安装到 `C:\Users\<用户名>\AppData\Local\Programs\Python\Python311\python.exe` 后固定引用（安装后按需 `pip install requests` 等）。**禁止**动态查找 Marvis 内置 Python 路径（升级即失效，属治标不治本）。
2. **编码**：bat 文件必须用 **UTF-8 with BOM** 编码写入，否则中文文件名"主流程.py"会被截断为"???.py"；同时必须 `chcp 65001 >nul` 切 UTF-8 代码页，否则中文路径被按 GBK 解析乱码，cmd 无法定位脚本（实测报 `can't open file`）。
3. **换行符**：bat 文件必须使用 **CRLF 换行**；写成 LF（0A）会导致 cmd 解析批处理错位，出现"命令前缀被吃掉"（如 `f "tokens=*"` 丢失 `for /`）等异常。
4. **首行空行避让 BOM**：UTF-8 BOM 会被 cmd 当作命令的一部分报"不是内部或外部命令"，建议文件第一行留空行（BOM 落在空行上），从第二行开始写命令，保证 `@echo off` 正常生效（模板已体现）。
5. **禁止生成 __pycache__**：bat 中必须 `set "PYTHONDONTWRITEBYTECODE=1"`（放在 python 调用前）；同时主流程.py 文件头部必须加 `sys.dont_write_bytecode = True`，保证直接运行 `python 主流程.py` 也不生成缓存（双保险）。

## 校验清单

- [BAT_001] auto run.bat必须用UTF-8 with BOM编码写入
- [BAT_002] auto run.bat必须使用CRLF换行符
- [BAT_003] both 必须固定引用独立Python绝对路径，禁止动态查找Marvis内置Python
- [BAT_004] both 必须设置PYTHONDONTWRITEBYTECODE=1禁止生成__pycache__
- [BAT_005] both 主流程.py头部必须加sys.dont_write_bytecode = True
- [BAT_006] auto bat文件首行留空行避让BOM，从第二行开始写@echo off
*（内容由AI生成，仅供参考）*
