---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_cd99f7edaa5b11f190de525400461939
    ReservedCode1: MdahULZ9hVunOfQpd5XuyFb+k/THd7eduVagLImt5R1M4KeyrOnLO9gEjHVUpQOVUEWCvyAm/kZB0qQcW8s2ZbXEXyDT116GnLjnmAeKcXRNjaEOaq2eSisZdrjzQGcWmzq0J2bZum/25LWzo3eUkqEVYV/PXZNK7mVi7z6eN0mstaEQ4HIH0YcMgA4=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_cd99f7edaa5b11f190de525400461939
    ReservedCode2: MdahULZ9hVunOfQpd5XuyFb+k/THd7eduVagLImt5R1M4KeyrOnLO9gEjHVUpQOVUEWCvyAm/kZB0qQcW8s2ZbXEXyDT116GnLjnmAeKcXRNjaEOaq2eSisZdrjzQGcWmzq0J2bZum/25LWzo3eUkqEVYV/PXZNK7mVi7z6eN0mstaEQ4HIH0YcMgA4=
---

# py-log（日志规则 / 条数汇总 / 保留策略 / 终端进度 / 错误处理）

> 原子子技能（promoted）。原 python-app-standard「日志规则 / 终端进度输出 / 错误处理」章节。

## 日志写入方式

- 每步执行完成实时追加一行，打开日志文件即见最新进度。
- **单文件写入（硬性规则）**：一次运行固定写**同一个**日志文件（`YYYY-MM-DD HH-mm-ss.txt`），**禁止**每次 write_log 新建文件（否则一次运行几十个文件、保留策略失效）。实现：模块级 `_CURRENT_LOG_FILE` 首次调用确定路径，后续行追加到该文件：

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

- 日志格式：`[2026-07-29 14:01:05] 流程A_xxx - 成功/失败 - 详情`
- **成功行必须带条数（硬性）**：格式 `流程X_用途 - 成功 - N 条`；失败行 `流程X_用途 - 失败 - 详情`。禁止只写"成功"不带条数。各流程计数取子流程返回的 `data.count`（`--limit` 模式下流程A 取截断后实际条数）。
- **运行结束条数汇总（硬性）**：主流程全部子流程成功、打印"全部完成"后，必须输出一次本次运行条数汇总（同时 print + write_log）：

```
[汇总] 本次运行汇总 - 流程A N 条 / 流程B N 条 / 流程C N 条 / 流程D N 条 / 合计 N 条
```

  汇总放在成功通知之前，保证通知失败也能在日志看到处理量；合计 = 各流程条数之和。业务维度拆分（京东/顺丰）由各应用自行补充，脚手架不强制业务语义。

- **保留策略**：最多保留 10 个日志文件，超出删除最早。`clean_old_logs()` 保留最新 **9 个**旧日志（为本次新日志留 1 个位置），避免结束后总数 11 个。

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

每个子流程在耗时操作时必须向终端动态刷新进度：

| 场景 | 进度内容 | 示例 |
|---|---|---|
| 抓取表格/分页读取 | 当前页/总页、已读记录数 | `[流程A_飞书查询] 正在读取表格数据... 第 3/8 页 (125/400 条)` |
| API 批量调用 | 当前条目/总条目 | `[流程B_快递查询] 正在查询物流状态... 47/125` |
| 写入/回填操作 | 写入条数/总条数 | `[流程C_飞书写回] 正在回填表格... 89/125` |

- **多表/多目标分别统计（硬性）**：查多个表/多数据源必须按每个表分别打印数量，禁止只打印汇总总数；写多个目标按每个目标分别打印。每表一行日志（带数量），全部读取完毕输出汇总总数行：

```
流程A - 「表1」：78 条
流程A - 「表2」：5 条
流程A 完成：共 83 条
```

- `\r` 动态刷新进度条**仅输出到终端，禁止写入日志**——日志只保留每表一行结果，否则被分页进度刷屏不可读。
- 实现规范：`\r` + `\033[K` 同行动态刷新；**禁止 tqdm 等第三方进度库，零依赖**；每个子流程维护自己的进度输出，前缀 `[流程X_用途]`；进度行不加换行符（`end=""`），用 `\r` 回到行首覆盖；操作完成后换行输出最终结果。

```python
import sys
total = 125
for i in range(total):
    # 业务逻辑...
    print(f"\r\033[K[流程B_快递查询] 正在查询物流状态... {i+1}/{total}", end="")
    sys.stdout.flush()
print(f"\r\033[K[流程B_快递查询] 查询完成，成功 {success_count}/{total}")
```

## 错误处理

- 任一子流程失败，**立即停止主流程**。
- 失败后调用 `通知.py` 中的 `notify_groups()` 通知到群聊（见 py-feishu）。

## 校验清单

- [LOG_001] both 一次运行固定写入同一个日志文件（单文件，禁止每次新建）
- [LOG_002] ai 日志格式：[时间] 流程X_用途 - 成功/失败 - 详情
- [LOG_003] both 每个子流程成功行必须体现处理条数（成功 - N条）
- [LOG_004] both 主流程结束必须输出条数汇总（流程A N条 / 流程B N条 / 合计N条）
- [LOG_005] both 最多保留10个日志文件，超出删除最早的（启动时清理保留9个旧日志）
- [PROG_001] both 抓取/API批量调用/写入时必须用\r+\033[K同行动态刷新进度
- [PROG_002] ai 多表/多数据源必须分别打印获取数量，禁止只打印汇总
- [PROG_003] ai 进度行仅输出终端，禁止写入日志
- [PROG_004] auto 禁止使用tqdm等第三方进度库，保持零依赖
- [ERR_001] ai 任一子流程失败立即停止主流程
- [ERR_002] both 失败后调用通知.py的notify_groups()通知到群聊
*（内容由AI生成，仅供参考）*
