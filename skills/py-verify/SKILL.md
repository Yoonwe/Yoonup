---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_d202b94daa5b11f1be88525400aeaaa3
    ReservedCode1: 3LM82jQ5g4vC/tUkmgn3h7D8+qxJYLNioZwmL06Dd22+NDHjlCwpaEMatuNCGcT7MAP2CVnm3wN0g4Z36C9AJdNCGjT8lHJL/opSC5C6GzkX/sUXZBCZz1OOmL7LXlYR/VzEP9Te4dX7p8ZPyLpNUVo1jJVwBtdvfC710E+OJhQOn3usOuNeRuaMuUc=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_d202b94daa5b11f1be88525400aeaaa3
    ReservedCode2: 3LM82jQ5g4vC/tUkmgn3h7D8+qxJYLNioZwmL06Dd22+NDHjlCwpaEMatuNCGcT7MAP2CVnm3wN0g4Z36C9AJdNCGjT8lHJL/opSC5C6GzkX/sUXZBCZz1OOmL7LXlYR/VzEP9Te4dX7p8ZPyLpNUVo1jJVwBtdvfC710E+OJhQOn3usOuNeRuaMuUc=
---

# py-verify（运行验证协议）

> 原子子技能（promoted）。原 python-app-standard「运行验证」章节。每次按脚手架生成流程代码后，**必须实际运行验证通过才算完成**。未通过验证的流程不得交付，修改后重新验证，直到正常运行结束为止。

## 验证标准（九步）

1. **空跑验证**：先生成代码，对不依赖外部 API 的骨架逻辑（日志写入、临时文件管理、主流程编排、通知模块）空跑一次，确保语法正确、目录创建正常、文件读写正常。**AI 自检标准**：终端输出 `OK 主流程.py`、`OK 物流公共.py` 等全部文件通过信息，且测试运行无异常退出。
2. **联调验证**：各子流程 API 串联完整运行一次，确认全部步骤走完、日志正常生成、成功/失败通知正常触发。**数据量大时必须用 `--limit N` 小样本联调**（如 3~50 条），避免全量运行超时或重复写生产表；全量运行仅留给正式定时任务。**AI 自检标准**：终端输出「全部完成!」+ `[汇总] 本次运行汇总` + `[通知] 成功回复` + `[运行记录]`，且 `--limit` 截断提示正常出现。
3. **失败路径验证**：人为制造某步骤异常，确认错误处理生效——失败即停、飞书通知到群。**AI 自检标准**：终端输出 `[通知] 失败通知` 且流程在失败步骤停止，不继续后续步骤。
4. **日志校验**：确认日志按规范写入、一次运行只产生 1 个日志文件、文件数超过 10 个时旧文件被正确清理。**AI 自检标准**：`logs/` 下只有本次运行一个新日志，内容含 `流程A_飞书查询 - 成功 - N 条` 等每步条数行，末尾含 `本次运行汇总` 行。
5. **定时任务验证（硬性规则）**：设定 Windows 计划任务后**手动触发一次**，确认 `LastTaskResult=0` 且 `logs/` 生成对应日志。核对 Action 为固定写法：独立Python + 带引号Arguments + WorkingDirectory留空，`MultipleInstancesPolicy=IgnoreNew`（XML 中确认），确认计划任务不经过 cmd.exe / run.bat 中转。全量触发会真实处理全部数据，**建议先手动触发后再用 `--limit N` 跑主流程.py 覆盖验证日志**。
6. **运行记录校验（硬性规则）**：`--limit N` 联调**连续运行两次**，校验：
   - **覆盖逻辑**：第二次终端/日志输出 `[运行记录] 今日记录已存在，覆盖更新成功`（而非"运行记录写入成功"），证明今日同应用成功记录被 PUT 覆盖而非重复新建；必要时查飞书表确认当日该应用仅 1 条成功记录。
   - **应用名称**：写入的「应用名称」必须等于**当前文件夹名**（改名后自动同步，无需改代码）。
   - **日志条数与汇总**：日志中每个流程成功行均含 `成功 - N 条`，末尾含 `本次运行汇总 - 流程A N 条 / ... / 合计 N 条`。
7. **锁机制校验（硬性规则）**：确认生成锁代码为**默认 PID 锁实现**（模板原样内置）：锁文件在项目根目录 `.running.lock`（非临时目录）、内容 `PID|时间`、主流程**先取锁后 init_dirs**、`LOCK_TIMEOUT_HOURS` 与计划任务 ExecutionTimeLimit 一致。核对默认行为：
   - **并发拦截**：锁内容为**当前存活进程 PID** 时再次运行，应输出"检测到正在运行（PID=...），跳过本次"。
   - **死锁自愈**：锁内容为**不存在进程 PID**（如 `999999|...`）时再次运行，应输出"检测到死锁（PID=... 进程已不存在），强制清除"并正常跑完、锁被自动清除。
   - 手动删除锁文件后再次运行应恢复正常。
8. **长任务健壮性校验**：涉及带有效期 Token 的外部 API 时，确认 Token 有缓存 + 提前过期自动刷新；批量写回接口带重试（可恢复错误码 99991672/99991663、网络异常重试 3 次），3 次失败跳过该批不中断流程；慢接口无重复重试。
9. **独立 Python 校验（硬性规则）**：run.bat 必须固定引用独立安装 Python 绝对路径（`C:\Users\<用户名>\AppData\Local\Programs\Python\Python311\python.exe`），**禁止**动态查找 Marvis 内置 Python；检查 `winget list Python.Python.3.11` 已安装，`pip show requests` 已就绪。

## 校验清单

- [VERIFY_001] ai 空跑验证通过：骨架逻辑（日志/临时文件/编排/通知）语法正确、目录与文件读写正常
- [VERIFY_002] ai 联调验证通过：API串联完整运行一次，数据量大时用--limit N小样本，终端输出"全部完成!"+汇总+成功通知+运行记录
- [VERIFY_003] ai 失败路径验证通过：人为制造异常，确认失败即停+飞书失败通知到群
- [VERIFY_004] ai 日志校验通过：一次运行仅1个日志文件、每步含"N 条"、末尾含汇总、旧日志清理正常
- [VERIFY_005] ai 定时任务验证通过：手动触发LastTaskResult=0、MultipleInstances=IgnoreNew、不经cmd/run.bat中转
- [VERIFY_006] ai 运行记录校验通过：连续运行两次，第二次为"覆盖更新成功"、应用名称=文件夹名
- [VERIFY_007] ai 锁机制校验通过：并发拦截输出"检测到正在运行"、死锁自愈（不存在PID被强制清除）
- [VERIFY_008] ai 长任务健壮性校验通过：Token缓存+提前刷新、批量重试3次失败跳批、慢接口不重复重试
- [VERIFY_009] ai 独立Python校验通过：run.bat固定引用独立Python绝对路径，winget list确认已安装
*（内容由AI生成，仅供参考）*
