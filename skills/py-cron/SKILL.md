---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_d08ab0c4aa5b11f190de525400461939
    ReservedCode1: xwAr/LO+pHhBpRXNC2uwb+vxmoP0SsEX4mWd/dogaN8tbp/gRTX8MS8qdAnu/JsKBVImI6GuA6pJFmulXJGnWxkUGx9ksG7Bg9D83I7gKz3LX7/lVLDJAxC+VgPzZdc8nBjmUnlu8lTtV6NLKGN1BeITKhJ1ePCQWjAtrVWEj/7fbyJg7h/ouZ1GGJ4=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_d08ab0c4aa5b11f190de525400461939
    ReservedCode2: xwAr/LO+pHhBpRXNC2uwb+vxmoP0SsEX4mWd/dogaN8tbp/gRTX8MS8qdAnu/JsKBVImI6GuA6pJFmulXJGnWxkUGx9ksG7Bg9D83I7gKz3LX7/lVLDJAxC+VgPzZdc8nBjmUnlu8lTtV6NLKGN1BeITKhJ1ePCQWjAtrVWEj/7fbyJg7h/ouZ1GGJ4=
---

# py-cron（Windows 计划任务定时执行）

> 原子子技能（promoted）。原 python-app-standard「定时执行」章节。**每小时执行一次**；由 AI 生成流程时自动搭建 Windows 计划任务，触发独立 Python 直接运行 `主流程.py`，无需用户手动创建。

## 固定写法（唯一允许方案，不做条件分支）

计划任务创建使用 PowerShell 的 `Schedule.Service` COM 对象。**Action 配置为固定写法**：直接调用独立 Python 并以带引号的绝对路径运行主流程，WorkingDirectory 留空。此写法天然兼容括号/空格/中文路径，任何文件夹名都不会触发路径解析问题，生成时照抄：

| 参数 | 值 | 说明 |
|---|---|---|
| Trigger | `Triggers.Create(2)` | **DailyTrigger**，不是 IdleTrigger(6)。必须叠加 Repetition 实现每小时重复 |
| Action.Path | 独立 Python 绝对路径（如 `C:\Users\<用户名>\AppData\Local\Programs\Python\Python311\python.exe`） | 直接调用独立 Python 运行主流程；**不经过 cmd.exe / run.bat 中转** |
| Action.Arguments | `"流程根目录\主流程.py"` | **双引号包裹绝对路径**；脚本内用 `os.path.dirname(os.path.abspath(__file__))` 定位自身目录 |
| Action.WorkingDirectory | **留空（不设置）** | 目录定位完全交给 Arguments 绝对路径与脚本内 `__file__` |
| Settings.ExecutionTimeLimit | `PT4H` | 超时 4 小时 Windows 强制终止，防任务卡死阻塞后续触发；**必须与主流程 LOCK_TIMEOUT_HOURS 一致**，且 ≥ 单次最长运行时间 |
| Settings.MultipleInstances | `2` (IgnoreNew) | 运行中新的触发直接忽略，不排队不并行；防长任务未跑完队列积压，配合文件锁双保险 |
| Settings.StartWhenAvailable | `True` | 错过计划时间（睡眠/重启/关机）后开机即补跑 |

**该固定写法的由来**：cmd.exe 会把路径中 `()` 当作命令分组/子表达式解析，把空格当参数分隔——若经 `cmd.exe /c run.bat` 中转或设置 WorkingDirectory 指向含括号/空格的目录（如 `物流回填(客服)`），路径会在第一个特殊字符处被截断（实测截断为 `C:\Users\EDY\Desktop\`），任务秒失败且报错诡异。因此规范直接指定"独立 Python + 带引号绝对路径 + WorkingDirectory 留空"为**唯一写法**，生成阶段即规避，不需要运行时判断路径是否含特殊字符。

## 每小时重复触发（硬性规则）

仅建 DailyTrigger 每天只触发 1 次。必须设置触发器 Repetition：`trigger.Repetition.Interval = "PT1H"`（每 1 小时）、`trigger.Repetition.Duration = "P1D"`（重复 24 小时，次日同点重新开新周期），再通过 `RegisterTaskDefinition` 注册生效。

**触发器类型固定为 DailyTrigger(2)**：`Triggers.Create(2)`（DailyTrigger）+ Repetition 是唯一允许的触发器写法；**不提供 IdleTrigger(6)**——它是空闲触发，只有电脑空闲时才执行。

## PowerShell 代码嵌入 Python 注意事项（实战经验）

AI 生成计划任务脚本时 PowerShell 代码通常嵌在 Python f-string 或字符串中通过 `subprocess.run` 执行。注意：
- **f-string 转义**：PowerShell `-f` 格式化操作符的 `{0}` 会被 Python f-string 解析为字面量 `0`，参数丢失。**推荐在 PowerShell 中用字符串拼接**：`$动作.Arguments = '\"' + $脚本路径 + '\"'`（而非 `'\"{0}\"' -f $脚本路径`）。
- **单引号嵌套**：PowerShell 单引号是字面字符串，注意与 Python 字符串引号不冲突。
- **花括号**：PowerShell 代码块中 `{ }` 在 Python f-string 内统一写成 `{{ }}` 转义。

## run.bat 定位

run.bat 仅作**手动/诊断入口**，**Windows 计划任务不经过它**；定时触发一律按上面固定写法直连（详见 py-bat）。

## 校验清单

- [CRON_001] ai 必须自动搭建Windows计划任务，每小时执行一次
- [CRON_002] ai Action必须为独立Python+带引号绝对路径+WorkingDirectory留空
- [CRON_003] ai 触发器为DailyTrigger(2)+Repetition每小时重复，禁止IdleTrigger
- [CRON_004] ai ExecutionTimeLimit=PT4H，MultipleInstances=IgnoreNew，StartWhenAvailable=True
*（内容由AI生成，仅供参考）*
