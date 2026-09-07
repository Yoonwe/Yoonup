---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_cf14db82aa5b11f1be88525400aeaaa3
    ReservedCode1: 5LPgIkc98nQJr44Y9Qupw9MrEzJStfHsuWzPU/qcmz3hrHzvZXLlmxYjTG3Nc1EV7zFfIVl+qwc8Zv9IMFG5Ewb/bKflbZlRc/v4/tIWz+fn16RoGby/N1itj5OoWRsvCoquU9an2wWYex01741UZpc6rYbqSVqwBNVaFV99LFRphONyke2OqjPrvew=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_cf14db82aa5b11f1be88525400aeaaa3
    ReservedCode2: 5LPgIkc98nQJr44Y9Qupw9MrEzJStfHsuWzPU/qcmz3hrHzvZXLlmxYjTG3Nc1EV7zFfIVl+qwc8Zv9IMFG5Ewb/bKflbZlRc/v4/tIWz+fn16RoGby/N1itj5OoWRsvCoquU9an2wWYex01741UZpc6rYbqSVqwBNVaFV99LFRphONyke2OqjPrvew=
---

# py-runrecord（运行记录多维表格）

> 原子子技能（promoted）。原 python-app-standard「运行记录模块」章节。

## 凭证

```python
APP_TOKEN = "FZgjbdV1Qa4rl3sr4GTcmbl4nhf"
TABLE_ID = "tbl4FpAG1a5Av0kJ"
```

## 接口签名

```python
def report_run_record(root_dir: str, project_name: str, 运行状态: str = "运行成功") -> dict:
    # 返回: {"success": True/False, "detail": "结果描述", "code": int}
```

## 字段规范

| 字段 | 取值 |
|---|---|
| 应用名称 | 流程文件夹名称（动态取 os.path.basename(ROOT_DIR)） |
| 账号名称 | 本机 IP（运行时自动获取，非环境变量） |
| 应用UUID | 流程文件夹绝对路径 |
| 运行开始时间 | 毫秒时间戳 |
| 运行方式 | 手动触发 / 定时触发（环境变量 `RUN_MODE` 注入，缺省为手动触发） |
| 运行状态 | 运行成功 / 运行失败 |
| 运行结束时间 | 毫秒时间戳 |

## 约束

- **每天每次运行都写入**：每次运行结束必须调用写入一次，任何时间都允许写入（无时段限制）。
- **写入去重与覆盖**：写入前先查询表内是否已有「应用名称相同 且 运行状态为运行成功 且 运行开始时间在今天」的记录：
  - **查询方式**：调 records/search，filter 用 `conjunction=and`，条件为 `运行状态 is 运行成功`（**注意**：「应用名称」为单选字段，若选项列表尚未包含当前项目名，直接对其做 `is` 精确过滤会返回 InvalidFilter(1254018)；因此「应用名称」匹配必须放本地判断，**禁止**在 filter 中对「应用名称」做精确过滤）；sort 按「运行开始时间」**倒序**（desc=true）；page_size 建议 100。
  - **本地判断今天与应用名称**：遍历结果，本机同时判断「应用名称 == 当前应用」且「运行开始时间」（毫秒）>= 当天 00:00 毫秒，都满足才视为今日记录，不依赖飞书端日期过滤。
  - **字段类型兼容（实战经验）**：API 返回的「应用名称」（单选字段）可能是字符串、数组或 `{text/value}` 对象；「运行开始时间」可能是毫秒/秒级时间戳或字符串。本地比对前先归一化（应用名称字符串化；时间统一转毫秒：数值 < 1e12 视为秒级乘 1000，字符串先 float 转换），否则类型不匹配导致今日记录永远匹配不上、每次运行都重复新建。
  - **当天 00:00 毫秒计算（实战经验）**：必须用本地时区正确计算，推荐 `time.mktime((本地年, 本地月, 本地日, 0,0,0,0,0,-1))` 或 `datetime.now().replace(hour=0,...).timestamp()`。**禁止** `now - now % 86400 - time.timezone`——东八区会算出"当前时刻"而非零点，导致重复新建。
  - **命中今日记录** → PUT 覆盖更新（刷新账号名称/应用UUID/运行方式/运行状态/运行结束时间），返回 `{"success": True, "detail": "今日记录已存在，覆盖更新成功", "code": 0}`。
  - **无今日记录** → POST 新建写入，返回 `{"success": True, "detail": "运行记录写入成功", "code": 0}`。
- **应用名称取值**：`os.path.basename(ROOT_DIR)` 动态获取；**严禁硬编码应用名称**，用户重命名文件夹后自动同步，验证以「当前文件夹名」为准。
- 必须校验飞书 API 返回的 `code` 字段，`code != 0` 时返回失败结果。
- 主流程调用后必须打印结果，**严禁** `try/except: pass` 静默吞异常。
- **失败场景也必须写入**：`report_run_record` 增加可选参数 `运行状态: str = "运行成功"` 支持"运行失败"；主流程 `_处理失败` 在发送失败通知后必须调用写入失败记录。失败记录每次新建，不参与今日成功记录的覆盖逻辑。
- **共用表查询性能优化（实战经验）**：若运行记录表被多用途共用（含大量非运行记录数据），records/search 倒序可能数千条，全量分页超时（实测单页 1.7s，10 页即 17s+）。分页遍历必须加**早停优化**：遇到第一条「运行开始时间有效且早于今天零点」的记录立即 return（倒序排列，后面只会更早）；同时加**最大页数保护**（如最多 10 页），超过停止查询走新建逻辑。

## 校验清单

- [RECORD_001] both 运行记录.py必须包含APP_TOKEN和TABLE_ID凭证
- [RECORD_002] both 每次运行结束必须调用report_run_record写入记录
- [RECORD_003] ai 写入前查询今日同应用成功记录，命中则PUT覆盖，无则POST新建
- [RECORD_004] both 应用名称必须动态取os.path.basename(ROOT_DIR)，禁止硬编码
- [RECORD_005] both 必须校验飞书API返回的code字段，code!=0返回失败
*（内容由AI生成，仅供参考）*
