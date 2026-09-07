---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_ccb887c0aa5b11f190de525400461939
    ReservedCode1: BlsjmWEghnj0MveRScTYqnr+SrOivj/sPC6/cfC0iOIRcVfPGVCpo1rS2B5DzUxbPS+TLP6zLqzjdmqKvUcTkzc2x75ZiCrGufyYvwzU9IiAWVhdmCb7DPISqlZV7HNTUTH/t7UKcxu5nJ7VlbvhruMGnoFL7diCB5deDg2MZYhduU83Qc/+Ox7PO44=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_ccb887c0aa5b11f190de525400461939
    ReservedCode2: BlsjmWEghnj0MveRScTYqnr+SrOivj/sPC6/cfC0iOIRcVfPGVCpo1rS2B5DzUxbPS+TLP6zLqzjdmqKvUcTkzc2x75ZiCrGufyYvwzU9IiAWVhdmCb7DPISqlZV7HNTUTH/t7UKcxu5nJ7VlbvhruMGnoFL7diCB5deDg2MZYhduU83Qc/+Ox7PO44=
---

# py-lock（文件锁防并发与死锁恢复）

> 原子子技能（promoted）。原 python-app-standard「文件锁防并发与死锁恢复」章节，PID 存活检测为默认实现，生成时直接内置模板。

## 核心规则（硬性）

1. 主流程启动时通过 `.running.lock` 文件锁防止同一项目并发执行。
2. 锁机制采用 **PID 存活检测**：锁文件记录启动进程 PID，下次启动查询该 PID 是否存活——进程已不存在（强杀/崩溃/断电）视为死锁立即清除继续执行；**任何异常结束都不会阻塞下一次定时触发**。
3. **锁文件必须放项目根目录 `.running.lock`，严禁放 `临时/`**：`init_dirs()` 每次运行 `shutil.rmtree` 清空临时目录，锁放临时目录会被清掉失去防并发作用（实测：锁被清后同项目可并发启动、互相覆盖临时文件）。
4. **执行顺序**：主流程必须**先 `acquire_lock()` 成功，再执行 `init_dirs()`**。顺序颠倒则 init_dirs 清空临时目录时可能把锁文件一并删除。
5. 锁内容格式 `{os.getpid()}|{datetime.now()}`；启动读取 PID 用 `tasklist` 查询进程是否存活。进程存活才视为"正在运行"跳过本次，进程不存在立即清锁继续。这是对"仅时间戳+超时自愈"锁的治本升级。
6. **释放锁必须带持有标志**：模块级 `LOCK_HELD` 仅本进程成功写入锁后置 True；主流程 `finally` 中必须 `if LOCK_HELD and os.path.exists(LOCK_FILE)` 才删除锁文件。**获取锁失败（返回 False）时严禁删除锁文件**，否则并发实例的锁会被误删（实测：finally 无条件删除锁时，跳过本次的实例把正在运行实例的锁删掉，触发并发）。
7. **旧格式兼容**：锁内容不含 `|`（旧版纯时间戳锁）时按 `LOCK_TIMEOUT_HOURS` 超时兜底判断，老项目升级后无需清理旧锁文件。
8. `LOCK_TIMEOUT_HOURS` 须与计划任务 ExecutionTimeLimit 完全一致（默认 4 小时）并覆盖最长单次运行时间——作为旧锁格式兜底与 tasklist 查询异常下的保险。

## 生成模板（直接内置，无需条件判断）

```python
LOCK_FILE = os.path.join(ROOT_DIR, ".running.lock")  # 必须放项目根目录，严禁放临时/
LOCK_TIMEOUT_HOURS = 4  # 与计划任务 ExecutionTimeLimit 一致；仅用于兼容旧版时间戳锁
LOCK_HELD = False  # 模块级标志：仅本进程持有锁才有权删除锁文件（防 finally 误删并发实例的锁）

def _is_process_alive(pid: int) -> bool:
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True
        ).stdout
        return str(pid) in out
    except Exception:
        return True  # 查询失败按存活处理，宁可跳过不可并发

def acquire_lock() -> bool:
    if os.path.exists(LOCK_FILE):
        try:
            content = open(LOCK_FILE, "r", encoding="utf-8").read().strip()
            if "|" in content:
                # PID|时间 格式：进程存活才占用，死亡即清锁
                pid_str, _ = content.split("|", 1)
                if pid_str.isdigit() and _is_process_alive(int(pid_str)):
                    print(f"[锁] 检测到正在运行（PID={pid_str}），跳过本次")
                    return False
                print(f"[锁] 检测到死锁（PID={pid_str} 进程已不存在），强制清除")
            else:
                # 旧时间戳格式：按超时兜底
                mtime = os.path.getmtime(LOCK_FILE)
                age_hours = (time.time() - mtime) / 3600
                if age_hours > LOCK_TIMEOUT_HOURS:
                    print(f"[锁] 检测到死锁（锁龄 {age_hours:.1f}h），强制清除")
                else:
                    print(f"[锁] 检测到正在运行（锁龄 {age_hours:.1f}h），跳过本次")
                    return False
            os.remove(LOCK_FILE)
        except OSError:
            os.remove(LOCK_FILE)
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        f.write(f"{os.getpid()}|{datetime.now()}")
    LOCK_HELD = True  # 成功写入锁后才标记持有，获取失败（返回 False）不置位
    return True
```

主流程结束统一释放（只允许持有者删除）：

```python
finally:
    if LOCK_HELD and os.path.exists(LOCK_FILE):  # 仅本进程持有锁时才删除（防误删并发实例的锁）
        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass  # 删除失败交由下次运行的死锁检测兜底清除
```

## 校验清单

- [LOCK_001] both 主流程启动时必须通过.running.lock文件锁防并发
- [LOCK_002] both 锁文件必须在项目根目录，严禁放临时/目录
- [LOCK_003] both 锁机制采用PID存活检测，内容为{PID}|{时间}格式
- [LOCK_004] ai 必须先acquire_lock()成功，再执行init_dirs()
- [LOCK_005] both 释放锁必须带LOCK_HELD持有标志，防止误删并发实例的锁
- [LOCK_006] both LOCK_TIMEOUT_HOURS必须与计划任务ExecutionTimeLimit一致（默认4小时）
*（内容由AI生成，仅供参考）*
