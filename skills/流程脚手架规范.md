---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_b9a4ad7b8d6c11f1b82d525400287e28
    ReservedCode1: 3Koz3qyJM3XSD7Wj4js038Gkf7kmO/7z0ZvDY8YB5U+2mqAIweWKcdjGTj2DoZjYKIATd5BNYhPs43YHFYiUyc8QKnurihLoY+YTFI6gM/fj6wRE13NtYYiny9CZLXfoMb1Xyeb62JI9OdNHmX+JhdW59Y4GU/td0GUBxWUzS62GwOQg9MvnlhynOIs=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_b9a4ad7b8d6c11f1b82d525400287e28
    ReservedCode2: 3Koz3qyJM3XSD7Wj4js038Gkf7kmO/7z0ZvDY8YB5U+2mqAIweWKcdjGTj2DoZjYKIATd5BNYhPs43YHFYiUyc8QKnurihLoY+YTFI6gM/fj6wRE13NtYYiny9CZLXfoMb1Xyeb62JI9OdNHmX+JhdW59Y4GU/td0GUBxWUzS62GwOQg9MvnlhynOIs=
---









# 流程脚手架规范 V1.0

## AI 生成行为约束（最高优先级）

以下规则约束 AI 在每次按本脚手架生成流程代码时的行为，**高于其他所有章节**：

1. **禁止向用户提问以下内容**：AI 必须自行从用户提供的脚本/文档内容中解析推断，不得反问用户确认——包括但不限于数据来源渠道（飞书多维表格/快递100/顺丰等）、处理范围（哪些表/哪些数据）、子流程如何拆分、文件夹名称、文件命名。用户只负责提供参考脚本或口头描述，不负责回答这些细节。
2. **流程划分**：按脚本内容中的**业务逻辑和数据源/接口**自行拆分，命名为 `流程{字母}_{数据源-用途}.py` 格式（如 `流程A_飞书-查询.py`、`流程B_快递100-物流状态.py`），**不是照搬脚本文件的拆分方式**。
3. **根目录**：直接在用户桌面新建文件夹作为流程根目录，文件夹名按业务用途命名，**不询问用户放哪里**。
4. **通知模块**：直接复用本规范已记录的飞书凭证和通知逻辑，**不需要问用户 APP_ID/APP_SECRET/群名/message_id**。
5. **工具脚本禁止交互式阻塞（硬性规则）**：所有生成的工具脚本（如定时任务搭建脚本）**禁止**使用 `input()`、`raw_input()` 等阻塞式交互。参数通过命令行参数（argparse）或环境变量传入，确保 AI 在非交互终端也能自动执行完整验证。失败/成功状态通过 `sys.exit(0/1)` 返回，供调用方判断。

**一句话原则**：用户给参考脚本和口头需求，AI 自己读脚本、自己拆步骤、自己建目录、直接生成已验证通过的完整代码，全程不反问。

## 目录结构

```
{流程根目录}/
├── 主流程.py                    # 入口文件，固定顺序调用子流程
├── 流程A_{源-用途}.py           # 子流程 A
├── 流程B_{源-用途}.py           # 子流程 B
├── 流程C_{源-用途}.py           # 子流程 C
├── 通知.py                      # 飞书通知模块（失败+成功）
├── 运行记录.py                   # 飞书多维表格运行记录模块
├── 临时/                        # 中间文件目录（每次运行覆盖）
│   ├── 流程A_{源-用途}.json
│   ├── 流程B_{源-用途}.json
│   └── ...
└── logs/                        # 日志目录
    ├── 2026-07-29 14-00-00.txt
    ├── 2026-07-29 13-00-00.txt
    └── ...（最多 10 个，超量删旧）
```

## 命名规范

| 项目 | 规则 |
|------|------|
| 主入口 | `主流程.py` |
| 子流程 | `流程{字母}_{数据源-用途}.py`，按调用顺序 A→B→C |
| 通知模块 | `通知.py` |
| 中间文件 | `临时/流程{字母}_{数据源-用途}.json` |
| 日志文件 | `YYYY-MM-DD HH-mm-ss.txt` |

## 变量命名与注释规范（硬性规则）

1. **变量名一律使用中文命名**：按变量的**实际作用**命名（如 `日期列表`、`金额`、`物流状态`、`订单号`），**禁止使用英文变量名**。源脚本中原本为英文的变量（如 `datalist`、`amount`），按脚手架重置生成时必须翻译为对应中文作用名（`datalist → 日期列表`、`amount → 金额`）
2. **变量名体现作用与类型**：变量声明时必须紧跟**类型注解**标注实际类型，格式 `变量名: 类型 = 初始值`（如 `日期列表: list = []`、`金额: float = 0.0`、`流程名称: str = "物流数据更新"`、`运行成功: bool = True`）。文档/注释中如需描述变量，写作 `作用(类型)` 形式（如 `日期列表(list)`、`金额(float)`）。**注意**：括号不能出现在实际代码的变量名中，类型一律用类型注解表达
3. **函数后必须有中文备注**：每个函数定义后紧跟中文注释或 docstring，说明该函数的作用（如 `# 从飞书查询指定表的所有记录，返回记录列表`）
4. **每行尽量有中文备注（硬性）**：函数体内**每一行**都必须有中文注释（行内或行尾）说明该行做什么，**尤其循环与请求**——`for`/`while` 循环必须注明循环对象、每轮处理什么（如 `for 记录 in 日期列表:  # 遍历每条日期记录，提取订单号`）；外部 API 请求必须注明请求目标、携带参数、返回用途（如 `请求结果 = 查询物流状态(订单号)  # 调快递100接口查询该订单物流状态，返回状态文本`）；简单的变量声明、函数调用同样逐行备注，保证阅读者无需理解代码即可知道每段在做什么

## 调用规则

- **拆分维度**：按数据源/外部接口拆分，每个独立接口一个子流程；通知、写入等操作也各自独立为子流程
- **调用顺序**：主流程固定按 A→B→C……依次调用
- **调用方式**：统一使用 **函数调用**。每个子流程暴露 `run()` 函数，主流程通过 import 调用，**不使用 subprocess**。异常直接向上传导，主流程捕获后走错误处理逻辑
- **统一入口函数签名**：每个子流程必须遵循以下签名

  ```python
  def run(tmp_dir: str, prev_file: str = None) -> dict:
      """
      tmp_dir: 临时/ 目录的绝对路径
      prev_file: 上一步输出的临时文件绝对路径，流程A 时为 None
      返回: {"status": "success", "data": {...}} 或 {"status": "fail", "error": "..."}
      """
  ```

- **数据传递**：主流程把 `tmp_dir` 和上一步产出的文件路径作为参数传入下一个子流程，子流程内部负责读写 `临时/` 目录，格式不限制
- **临时文件**：每次运行时 `临时/` 目录全部覆盖重写
- **运行环境**：使用**生产环境真实凭证**运行，不做测试/沙箱隔离。运行验证时会产生真实外部副作用（飞书通知到真实群、写入生产表格）
- **--limit 验证参数（硬性规则）**：主流程必须支持 `--limit N` 参数（argparse），用于小样本联调——流程A 查询完成后截断记录只处理前 N 条，避免全量数据（数千条）导致验证超时或重复写生产表。仅在验证时使用，正式定时执行不传（全量）。主流程模板：

  ```python
  parser = argparse.ArgumentParser(description="主流程")
  parser.add_argument("--limit", type=int, default=0, help="仅处理前 N 条记录（0=全量，用于验证）")
  args = parser.parse_args()
  # 流程A 成功后：
  if args.limit and args.limit > 0:
      with open(prev_file, "r", encoding="utf-8") as f:
          a_records = json.load(f)
      a_records = a_records[:args.limit]
      with open(prev_file, "w", encoding="utf-8") as f:
          json.dump(a_records, f, ensure_ascii=False)
      print(f"[验证] --limit {args.limit}：仅处理前 {len(a_records)} 条记录")
  ```

## 文件锁防并发与死锁恢复（硬性规则）

主流程启动时必须通过 `.running.lock` 文件锁防止同一项目并发执行。锁机制采用 **PID 存活检测**（默认实现，生成代码时直接内置以下模板，无需任何条件判断）：锁文件记录启动进程的 PID，下次启动时查询该 PID 是否存活——进程已不存在（被强杀/崩溃/断电）即视为死锁立即清除继续执行，**任何异常结束都不会阻塞下一次定时触发**：

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

主流程结束时统一在 `finally` 中释放锁，**只有 `LOCK_HELD` 为 True 的进程才有权删除锁文件**，防止误删并发实例的锁：

```python
finally:
    if LOCK_HELD and os.path.exists(LOCK_FILE):  # 仅本进程持有锁时才删除（防误删并发实例的锁）
        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass  # 删除失败交由下次运行的死锁检测兜底清除
```

- **锁文件必须写到项目根目录 `.running.lock`**：严禁放入 `临时/` 目录——`init_dirs()` 每次运行都会 `shutil.rmtree` 清空临时目录，锁放临时目录会被清掉，失去防并发作用（实测：锁被清后同项目可并发启动、互相覆盖临时文件）
- **执行顺序**：主流程必须**先 `acquire_lock()` 成功，再执行 `init_dirs()`**。若顺序颠倒，init_dirs 清空临时目录时可能把锁文件一并删除
- **锁内容为 `{os.getpid()}|{datetime.now()}`**：启动时读取 PID 并用 `tasklist` 查询该进程是否存活，进程存活才视为"正在运行"并跳过本次，进程已不存在立即清锁继续执行。这是对"仅时间戳+超时自愈"锁的治本升级：旧锁在进程被强杀后，只要锁龄未到超时，后续每次触发都会被误判为"正在运行"而跳过
- **释放锁必须带持有标志（硬性规则）**：模块级 `LOCK_HELD` 标志仅在本进程成功写入锁后置 True；主流程 `finally` 中必须 `if LOCK_HELD and os.path.exists(LOCK_FILE)` 才删除锁文件。**获取锁失败（返回 False）时严禁删除锁文件**——否则并发实例的锁会被误删，导致两个实例同时运行、互相覆盖临时文件（实测：`finally` 无条件删除锁时，跳过本次的实例把正在运行实例的锁删掉，触发并发）
- **旧格式兼容**：锁内容不含 `|`（旧版纯时间戳锁）时按 `LOCK_TIMEOUT_HOURS` 超时兜底判断，老项目升级锁代码后无需清理旧锁文件
- `LOCK_TIMEOUT_HOURS` 仍须与计划任务 ExecutionTimeLimit 完全一致（默认 4 小时）并覆盖最长单次运行时间——作为旧锁格式兜底与极端场景（tasklist 查询异常）下的保险

## 日志规则

- **写入方式**：每一步执行完成后实时追加一行，打开日志文件即可看到最新进度
- **单文件写入（硬性规则）**：一次运行固定写入**同一个**日志文件（`YYYY-MM-DD HH-mm-ss.txt`），**禁止**每次 write_log 都新建文件（否则一次运行产生几十个文件，日志保留策略失效）。实现：模块级全局变量 `_CURRENT_LOG_FILE` 在首次调用时确定文件路径，后续所有行追加到该文件：

  ```python
  _CURRENT_LOG_FILE = None

  def write_log(message):
      global _CURRENT_LOG_FILE
      if _CURRENT_LOG_FILE is None:
          _CURRENT_LOG_FILE = os.path.join(
              LOG_DIR, datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"
          )
      line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
      with open(_CURRENT_LOG_FILE, "a", encoding="utf-8") as f:
          f.write(line)
  ```

- **日志格式**：`[2026-07-29 14:01:05] 流程A_xxx - 成功/失败 - 详情`
- **日志条数（硬性规则）**：每个子流程在日志中的成功行**必须体现处理条数**，格式 `流程X_用途 - 成功 - N 条`；失败行 `流程X_用途 - 失败 - 详情`。禁止在日志中只写"成功"不带条数，否则无法从日志判断本次实际处理量。各流程计数取子流程返回的 `data.count`（`--limit` 验证模式下流程A 取截断后的实际条数）
- **运行结束条数汇总（硬性规则）**：主流程在全部子流程成功、打印"全部完成"之后，**必须输出一次本次运行的条数汇总**（同时 print 到终端 + write_log 写入日志），格式：

  ```
  [汇总] 本次运行汇总 - 流程A N 条 / 流程B N 条 / 流程C N 条 / 流程D N 条 / 合计 N 条
  ```

  若某应用存在业务维度拆分（如物流应用区分京东/顺丰），可在对应流程行用括号补充，但**拆分维度由各应用自行定义，脚手架不强制任何业务语义**

  汇总放在成功通知之前，保证即使通知失败也能在日志中看到本次处理量；合计 = 各流程条数之和
- **保留策略**：最多保留 10 个日志文件，超出时删除最早的。清理在启动时执行，`clean_old_logs()` 保留最新 **9 个**旧日志（为本次运行的新日志留 1 个位置），避免运行结束后总数为 11 个：

  ```python
  def clean_old_logs():
      files = sorted(
          [f for f in os.listdir(LOG_DIR) if f.endswith(".txt")],
          key=lambda x: os.path.getmtime(os.path.join(LOG_DIR, x)),
          reverse=True,
      )
      for old in files[9:]:   # 保留 9 个旧日志 + 本次 1 个 = 10
          try:
              os.remove(os.path.join(LOG_DIR, old))
          except (FileNotFoundError, PermissionError):
              pass
  ```

## 终端进度输出（硬性规则）

每个子流程在涉及以下耗时操作时，**必须向终端输出动态刷新进度**，让执行者实时看到当前状态：

### 强制要求进度的场景

| 场景 | 进度内容 | 示例 |
|------|----------|------|
| 抓取表格/分页读取 | 当前页/总页、已读记录数 | `[流程A_飞书查询] 正在读取表格数据... 第 3/8 页 (125/400 条)` |
| API 批量调用 | 当前条目/总条目 | `[流程B_快递查询] 正在查询物流状态... 47/125` |
| 写入/回填操作 | 写入条数/总条数 | `[流程C_飞书写回] 正在回填表格... 89/125` |

### 多表/多目标分别统计（硬性规则）

**涉及查询多个表或多个数据源时，必须按每个表/每个数据源分别打印获取数量，禁止只打印汇总总数**；**涉及写入多个表或多个目标时，必须按每个目标分别打印写入数量**。每条记录一个独立输出行，格式统一为：

```
流程A - 「表1」：78 条
流程A - 「表2」：5 条
流程A 完成：共 83 条
```

- 每张表一行日志，必须带数量
- 若应用有业务维度拆分需求（如物流区分京东/顺丰），由各应用自行在括号内补充，**脚手架不规定任何业务语义**
- 全部表读取完毕后，输出一行汇总（总数）
- `\r` 动态刷新进度条（分页读取进度）**仅输出到终端**，**禁止写入日志**——日志只保留每表一行结果，否则日志被分页进度刷屏，完全不可读

### 实现规范

- **使用 `\r` + `\033[K` 同行动态刷新**，不允许使用 tqdm 等第三方进度库，保持零依赖
- 每个子流程内部维护自己的进度输出，步骤名称前缀统一：`[流程X_用途]`
- 进度行末尾**不加换行符**（`end=""`），直接用 `\r` 回到行首覆盖
- 操作完成后**换行输出最终结果**，再继续下一步

### 示例代码

```python
import sys

total = 125
for i in range(total):
    # 业务逻辑...
    print(f"\r\033[K[流程B_快递查询] 正在查询物流状态... {i+1}/{total}", end="")
    sys.stdout.flush()

# 完成后换行输出结果
print(f"\r\033[K[流程B_快递查询] 查询完成，成功 {success_count}/{total}")
```

## 错误处理

- 任一子流程失败，**立即停止主流程**
- 失败后调用 `通知.py` 中的 `notify_groups()` 通知到群聊

## 飞书通知配置

### 凭证

```python
APP_ID = "cli_a729a2469afed00c"
APP_SECRET = "cPVQMyS75d61KRcpNMxXygaBxhMv4gsH"
```

### 通知逻辑

- **失败通知群**：群名关键词 `"万威, 黄俊文, 肖晓雯"`，使用 `notify_groups()` 发送
- **成功通知**：使用 `reply_message()` 回复 `om_x100b553b7f9284b4c3f790e4b13825a`

### 通知文本模板

- **成功**：`{流程文件夹名}-{YYYY-MM-DD HH:mm:ss}:完成`
- **失败**：`{流程文件夹名}-{YYYY-MM-DD HH:mm:ss}:{具体错误信息}`

### 通知.py 核心接口（含返回值约束）

```python
def notify_groups(app_id: str, app_secret: str, group_names: list[str], message: str) -> dict
    # 向多个群聊发送通知（失败场景）
    # 返回: {"success": True/False, "detail": "结果描述", "codes": [...]}

def reply_message(app_id: str, app_secret: str, message_id: str, text: str) -> dict
    # 回复指定消息（成功场景）
    # 返回: {"success": True/False, "detail": "结果描述", "code": int}
```

**硬性要求**：
- `reply_message` 请求体必须包含 `msg_type: "text"` 字段，缺少会导致飞书返回 99992402 错误
- 所有通知函数必须返回 dict，调用方必须打印结果，**严禁** `try/except: pass` 静默吞异常
- 主流程调用通知后示例：`r = reply_message(...); print(f"[通知] 成功回复: {r['detail']}")`

## 依赖管理

- 每个流程所需的第三方库（requests、飞书 SDK、快递100 SDK 等）**在代码内自动安装**，不依赖外部手动安装
- 推荐在 `主流程.py` 顶部统一处理依赖安装，确保首次运行即可自动就绪

## 路径规范

- 流程根目录统一建在**当前电脑桌面**，路径识别方式：
  ```python
  desktop = os.path.join(os.path.expanduser("~"), "Desktop")
  ```
- 不写死绝对路径，保证在不同电脑上都能正确解析

## 通知模块

- `通知.py` 采用**多副本**模式：每个流程目录各自生成一份，内含本规范已记录的飞书凭证和通知逻辑
- 各流程独立维护自己的 `通知.py`，不跨流程共享

## 运行记录模块

### 凭证

```python
APP_TOKEN = "FZgjbdV1Qa4rl3sr4GTcmbl4nhf"
TABLE_ID = "tbl4FpAG1a5Av0kJ"
```

### 接口签名

```python
def report_run_record(root_dir: str, project_name: str) -> dict:
    # 返回: {"success": True/False, "detail": "结果描述", "code": int}
```

### 字段规范

| 字段 | 取值 |
|------|------|
| 应用名称 | 流程文件夹名称 |
| 账号名称 | 本机 IP（运行时自动获取，非环境变量） |
| 应用UUID | 流程文件夹绝对路径 |
| 运行开始时间 | 毫秒时间戳 |
| 运行方式 | 手动触发 / 定时触发（环境变量 `RUN_MODE` 注入，缺省为手动触发） |
| 运行状态 | 运行成功 / 运行失败 |
| 运行结束时间 | 毫秒时间戳 |

### 约束

- **每天每次运行都写入**：每次运行结束后必须调用运行记录模块写入一次，任何时间都允许写入（无 22 点前跳过等时段限制）
- **写入去重与覆盖**：写入前先查询表内是否已有「应用名称相同 且 运行状态为运行成功 且 运行开始时间在今天」的记录：
  - **查询方式**：调用多维表格 records/search 接口，`filter` 使用 `conjunction=and`，条件为 `运行状态 is 运行成功`（**注意**：「应用名称」为单选字段，若其选项列表尚未包含当前项目名，直接对其做 `is` 精确过滤会返回 InvalidFilter(1254018)；因此「应用名称」匹配必须放本地判断，**禁止**在 filter 中对「应用名称」做精确过滤）；`sort` 按「运行开始时间」**倒序**（`desc=true`）；`page_size` 建议 100
  - **本地判断今天与应用名称**：遍历查询结果，在本机同时判断「应用名称 == 当前应用」且「运行开始时间」（毫秒时间戳）>= 当天 00:00 的毫秒时间戳，两者都满足才视为今日记录，不依赖飞书端日期过滤
  - **字段类型兼容（实战经验）**：飞书多维表格 API 返回的「应用名称」（单选字段）可能是字符串，也可能是数组或 `{text/value}` 对象；「运行开始时间」可能是毫秒/秒级时间戳，也可能是字符串。本地比对前必须先做归一化（字符串化应用名称；时间统一转毫秒：数值 < 1e12 视为秒级乘 1000，字符串先 float 转换），否则类型不匹配会导致今日记录永远匹配不上、每次运行都重复新建
  - **当天 00:00 毫秒时间戳计算（实战经验）**：必须用本地时区正确计算，推荐 `time.mktime((本地年, 本地月, 本地日, 0,0,0,0,0,-1))` 或 `datetime.now().replace(hour=0,...).timestamp()`。**禁止**使用 `now - now % 86400 - time.timezone` 公式——东八区会算出"当前时刻"而非当天零点，导致 `start >= today_start` 永远不成立，同样造成重复新建
  - **命中今日记录** → 调用 PUT 接口**覆盖更新**该记录（刷新账号名称/应用UUID/运行方式/运行状态/运行结束时间），返回 `{"success": True, "detail": "今日记录已存在，覆盖更新成功", "code": 0}`
  - **无今日记录** → 调用 POST 接口**新建写入**，返回 `{"success": True, "detail": "运行记录写入成功", "code": 0}`
- **应用名称取值**：`应用名称 = 主流程所在目录名`（即流程文件夹名，由 `os.path.basename(ROOT_DIR)` 获取）
- **禁止硬编码应用名称（实战经验）**：主流程中 `project_name` 必须动态取 `os.path.basename(ROOT_DIR)`，并作为参数传给 `report_run_record`；**严禁**在运行记录模块或主流程中写死应用名。用户重命名流程文件夹后，应用名称应自动同步为新文件夹名，无需改任何代码——验证时以「当前文件夹名」为准
- 必须校验飞书 API 返回的 `code` 字段，`code != 0` 时返回失败结果
- 主流程调用后必须打印结果，**严禁** `try/except: pass` 静默吞异常

## 外部 API Token 生命周期与重试策略（硬性规则）

适用于所有使用带有效期 Token 的外部 API（飞书 tenant_access_token 等），尤其长任务（单次运行可能超过 1~2 小时）必须遵守：

- **Token 必须带缓存自动刷新（硬性规则）**：严禁只在流程开头获取一次 Token 全程复用——长任务运行到后半段 Token 过期，后续所有写入/回填全部失败。实现：模块级缓存 Token 与过期时间，**提前 5 分钟过期**留 buffer；每次发起 API 请求前调用获取函数，缓存有效直接返回，否则自动刷新：

  ```python
  _token_cache = {"token": None, "expires_at": 0}

  def _get_token() -> str:
      now = time.time()
      if _token_cache["token"] and now < _token_cache["expires_at"]:
          return _token_cache["token"]
      # ... 请求新 token，假设响应体含 expire ...
      _token_cache["token"] = new_token
      _token_cache["expires_at"] = now + expire - 300  # 提前5分钟过期
      return new_token
  ```

- **所有 HTTP 请求必须显式设置 timeout（硬性规则）**：每个 `requests.get()` / `requests.post()` 必须带 `timeout=N` 参数。推荐值：Token 获取/批量写入设为 60s，查询/搜索接口设为 30s。严禁依赖 requests 默认无超时——服务端无响应时会无限阻塞，定时任务卡死后后续触发全部跳过、且无日志无通知（实测：读飞书表格时 read timeout 30s，进程挂起无输出，下一轮整点检测到锁文件「正在运行」跳过，陷入沉默失效）
- **所有外部 API 调用必须带重试逻辑（硬性规则）**：不仅批量写入需要重试，**查询/Token 获取等所有 HTTP 请求**也必须包裹 try-except，遇到 `requests.RequestException`（含 Timeout、ConnectionError 等）时自动重试最多 3 次，每次重试前重新获取 Token 并 sleep 2s。3 次全失败则返回失败结果，由调用方决定中断或跳过。避免单次网络抖动就打断整个流程

- **批量写入必须失败重试（硬性规则）**：批量更新接口（如飞书 records/batch_update）单批失败会丢整批数据，**必须重试最多 3 次**，每次重试前重新获取 Token；以下情况属于可恢复错误，必须重试：
  - Token 过期类错误码（飞书 `99991672`）
  - 频率限制类错误码（飞书 `99991663`）
  - 网络异常（`requests.RequestException`）
- **3 次重试仍失败**：打印警告并跳过该批，**不得中断整个流程**——剩余批次继续处理，失败批次由下一轮定时补跑
- **慢接口禁止无意义重试（硬性规则）**：对响应本身就慢的外部接口（如快递100 autonumber 识别接口约 11s/条），**严禁**加"3 次重试 + 每次 sleep 2 秒 + 每次重试重新调用识别"这类逻辑——会把单条耗时放大数倍、全流程从分钟级拖到小时级。正确做法：识别一次查询一次，失败返回空值由下一轮定时补跑；瓶颈在官方接口限流，不在代码逻辑

## 定时执行

- 每小时执行一次
- **由 AI 在生成流程时自动搭建 Windows 计划任务**，触发独立 Python 直接运行 `主流程.py`，无需用户手动创建
- 计划任务创建方式使用 PowerShell 的 `Schedule.Service` COM 对象。**Action 配置为固定写法（唯一允许方案，不做条件分支）**：直接调用独立 Python 并以带引号的绝对路径运行主流程，WorkingDirectory 留空。此写法天然兼容括号/空格/中文路径，任何文件夹名都不会触发路径解析问题，生成时照抄即可：

  | 参数 | 值 | 说明 |
  |------|-----|------|
  | Trigger | `Triggers.Create(2)` | **DailyTrigger**，不是 IdleTrigger(6)。必须叠加 Repetition 实现每小时重复（见下） |
  | Action.Path | 独立 Python 绝对路径（如 `C:\Users\<用户名>\AppData\Local\Programs\Python\Python311\python.exe`） | 直接调用独立 Python 运行主流程；**不经过 cmd.exe / run.bat 中转** |
  | Action.Arguments | `"流程根目录\主流程.py"` | **双引号包裹绝对路径**；脚本内用 `os.path.dirname(os.path.abspath(__file__))` 定位自身目录 |
  | Action.WorkingDirectory | **留空（不设置）** | 不设置任何值；目录定位完全交给 Arguments 中的绝对路径与脚本内 `__file__` |
  | Settings.ExecutionTimeLimit | `PT4H` | 超时 4 小时（240分钟）Windows 强制终止，防止任务卡死阻塞后续触发；**必须与主流程 LOCK_TIMEOUT_HOURS 一致**，且 ≥ 单次最长运行时间 |
  | Settings.MultipleInstances | `2` (IgnoreNew) | 运行中新的触发直接忽略，不排队不并行（COM 枚举：0=Parallel, 1=Queue, 2=IgnoreNew）。防止长任务未跑完时队列积压，配合文件锁双保险 |
  | Settings.StartWhenAvailable | `True` | 错过计划时间（电脑睡眠/重启/关机）后开机即补跑，保证不漏跑 |

  **该固定写法的由来（为什么不做 cmd 中转、不设 WorkingDirectory）**：cmd.exe 会把路径中的 `()` 当作命令分组/子表达式语法解析，把空格当作参数分隔——若经 `cmd.exe /c run.bat` 中转或设置 WorkingDirectory 指向含括号/空格的目录（如 `物流回填(客服)`），路径会在第一个特殊字符处被截断（实测截断为 `C:\Users\EDY\Desktop\`），任务秒失败且报错诡异难查。因此规范直接指定"独立 Python + 带引号绝对路径 + WorkingDirectory 留空"为**唯一写法**，生成阶段即规避，不需要运行时判断路径是否含特殊字符

- **每小时重复触发（硬性规则）**：仅建 DailyTrigger 每天只触发 1 次。必须设置触发器 Repetition：`trigger.Repetition.Interval = "PT1H"`（每 1 小时）、`trigger.Repetition.Duration = "P1D"`（重复 24 小时，次日同点重新开新周期），再通过 `RegisterTaskDefinition` 注册生效
- **触发器类型固定为 DailyTrigger(2)**：`Triggers.Create(2)`（DailyTrigger）+ Repetition 是唯一允许的触发器写法；**不提供 IdleTrigger(6)**——它是空闲触发，只有电脑空闲时才执行，平时不跑

- **PowerShell 代码嵌入 Python 注意事项（实战经验）**：AI 生成计划任务脚本时，PowerShell 代码通常嵌入在 Python f-string 或字符串中通过 `subprocess.run` 执行。注意以下陷阱：
  - **f-string 转义**：PowerShell 的 `-f` 格式化操作符中的 `{0}` 会被 Python f-string 解析为字面量 `0`，导致参数丢失。**推荐直接在 PowerShell 中用字符串拼接代替**：`$动作.Arguments = '"' + $脚本路径 + '"'`（而非 `'"{0}"' -f $脚本路径`）
  - **单引号嵌套**：PowerShell 中单引号是字面字符串，生成时注意与 Python 字符串引号不冲突
  - **花括号**：PowerShell 代码块中的 `{ }` 如果在 Python f-string 内，统一写成 `{{ }}` 转义

- **run.bat 中转脚本（定位：仅手动/诊断入口，不参与定时）**：流程生成时一并创建 `run.bat`，供用户**手动双击运行**与排查问题时使用；**Windows 计划任务不经过它**，定时触发一律按上表"独立Python + 带引号Arguments + WorkingDirectory留空"直连。**Python 解释器必须使用独立安装的 Python（硬性规则），严禁依赖 Marvis 内置 Python 或动态查找其路径**——Marvis 升级会导致路径失效、全流程停摆。独立 Python 通过 `winget install Python.Python.3.11` 安装到 `C:\Users\<用户名>\AppData\Local\Programs\Python\Python311\python.exe` 后固定引用（安装后执行 `pip install requests` 等按需依赖）：

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

  - **编码**：bat 文件必须用 **UTF-8 with BOM** 编码写入，否则中文文件名"主流程.py"会被截断为"???.py"；同时必须执行 `chcp 65001 >nul` 切换到 UTF-8 代码页，否则中文路径（根目录名/主流程.py）会被按 GBK 解析成乱码，cmd 无法定位 python 脚本（实测报 `can't open file`）
  - **换行符**：bat 文件必须使用 **CRLF 换行**（0D 0A），若写成 LF（0A），cmd 解析批处理会错位，出现"命令前缀被吃掉"（如 `f "tokens=*"` 丢失 `for /`）等异常
  - **首行空行避让 BOM**：UTF-8 BOM 会被 cmd 当作命令的一部分报"不是内部或外部命令"，建议文件第一行留空行（BOM 落在空行上），从第二行开始写命令，保证 `@echo off` 正常生效
  - **禁止生成 __pycache__**：bat 中必须 `set "PYTHONDONTWRITEBYTECODE=1"`（放在 python 调用前即可），否则 Python import 模块时会在流程根目录生成 `__pycache__` 缓存目录；同时主流程.py 文件头部必须加 `sys.dont_write_bytecode = True`，保证直接运行 `python 主流程.py` 时也不生成缓存（双保险）
  - **独立 Python 安装（实战经验）**：用 `winget install Python.Python.3.11` 安装独立 Python 到 `C:\Users\<用户名>\AppData\Local\Programs\Python\Python311\`，run.bat 固定引用该绝对路径，与 Marvis 彻底解耦——Marvis 升级不影响流程，属于**治本方案**；**禁止**动态查找 Marvis 内置 Python 路径（升级即失效，属治标不治本）

## 运行验证（硬性规则）

每次按本脚手架生成流程代码后，**必须实际运行验证通过才算完成**。

验证标准：

1. **空跑验证**：先生成代码后，对不依赖外部 API 的骨架逻辑（日志写入、临时文件管理、主流程编排、通知模块）进行一次空跑，确保语法正确、目录创建正常、文件读写正常。**AI 自检标准**：终端输出 `OK 主流程.py`、`OK 物流公共.py` 等全部文件通过信息，且测试运行无异常退出。
2. **联调验证**：各子流程的 API 串联起来完整运行一次，确认全部步骤走完、日志正常生成、成功/失败通知正常触发。**数据量大时必须使用 `--limit N` 小样本联调**（如 3~50 条），避免全量运行超时或重复写生产表；全量运行仅留给正式定时任务。**AI 自检标准**：终端应输出「全部完成!」+ `[汇总] 本次运行汇总` + `[通知] 成功回复` + `[运行记录]`，且 `--limit` 截断提示正常出现。
3. **失败路径验证**：人为制造某个步骤的异常，确认错误处理逻辑生效——失败即停、飞书通知到群。**AI 自检标准**：终端应输出 `[通知] 失败通知` 且流程在失败步骤停止，不继续后续步骤。
4. **日志校验**：确认日志文件按规范格式写入、一次运行只产生 1 个日志文件、文件数超过 10 个时旧文件被正确清理。**AI 自检标准**：`logs/` 目录下应只有本次运行的一个新日志文件，内容含 `流程A_飞书查询 - 成功 - N 条`、`流程B_快递100查询 - 成功 - N 条` 等每步条数行，末尾含 `本次运行汇总` 行。
5. **定时任务验证（硬性规则）**：设定 Windows 计划任务后**手动触发一次**，确认 `LastTaskResult=0` 且 `logs/` 生成对应日志。核对 Action 为固定写法：独立Python + 带引号Arguments + WorkingDirectory留空，`MultipleInstancesPolicy=IgnoreNew`（XML 中确认），确认计划任务不经过 cmd.exe / run.bat 中转。全量触发会真实处理全部数据，**建议先手动触发后再用 `--limit N` 跑主流程.py 覆盖验证日志**。
6. **运行记录校验（硬性规则）**：`--limit N` 联调**连续运行两次**，并校验：
   - **覆盖逻辑**：第二次运行的终端/日志应输出 `[运行记录] 今日记录已存在，覆盖更新成功`（而非"运行记录写入成功"），证明今日同应用成功记录被 PUT 覆盖而非重复新建；必要时查飞书表确认当日该应用仅 1 条成功记录
   - **应用名称**：运行记录写入的「应用名称」必须等于**当前文件夹名**（改名后自动同步，无需改代码）
   - **日志条数与汇总**：日志中每个流程成功行均含 `成功 - N 条`，且末尾含 `本次运行汇总 - 流程A N 条 / ... / 合计 N 条`
7. **锁机制校验（硬性规则）**：确认生成的锁代码为**默认 PID 锁实现**（模板原样内置，无需条件分支）：锁文件生成在**项目根目录** `.running.lock`（非临时目录）、内容为 `PID|时间` 格式、主流程**先取锁后 init_dirs**、`LOCK_TIMEOUT_HOURS` 与计划任务 ExecutionTimeLimit 一致。核对默认行为：
   - **并发拦截**：锁内容为**当前存活进程 PID** 时再次运行，应输出"检测到正在运行（PID=...），跳过本次"
   - **死锁自愈**：锁内容为**不存在进程 PID**（如 `999999|...`）时再次运行，应输出"检测到死锁（PID=... 进程已不存在），强制清除"并正常跑完、锁被自动清除——即进程被强杀后下次定时触发不受影响
   - 手动删除锁文件后再次运行应恢复正常
8. **长任务健壮性校验**：涉及带有效期 Token 的外部 API 时，确认 Token 有缓存 + 提前过期自动刷新；批量写回接口带重试（可恢复错误码 99991672/99991663、网络异常重试 3 次），3 次失败跳过该批不中断流程；慢接口无重复重试
9. **独立 Python 校验（硬性规则）**：run.bat 必须固定引用独立安装的 Python 绝对路径（`C:\Users\<用户名>\AppData\Local\Programs\Python\Python311\python.exe`），**禁止**动态查找 Marvis 内置 Python；检查 `winget list Python.Python.3.11` 已安装，`pip show requests` 已就绪

**未通过验证的流程不得交付，修改后重新验证，直到正常运行结束为止。**

