---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_cc059fd1aa5b11f188bd525400287e28
    ReservedCode1: Itke+2avLv66lCMOcfidvnxeCw7jROkyPiCL0vucXXa2Ys/LuejJVZ4VZG3e/YMOX1K0hJ2yGkZ0vcDBPeCp1704sMdV/WhiQ+Jibf6Qx6GS44vlVCWgVo1z8VKAt2rrvhvPQePwHfeqZi90ho2QvdfU0WCPXIsS4/p6AIa5xFPSgtPDo31z1WzkJRE=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_cc059fd1aa5b11f188bd525400287e28
    ReservedCode2: Itke+2avLv66lCMOcfidvnxeCw7jROkyPiCL0vucXXa2Ys/LuejJVZ4VZG3e/YMOX1K0hJ2yGkZ0vcDBPeCp1704sMdV/WhiQ+Jibf6Qx6GS44vlVCWgVo1z8VKAt2rrvhvPQePwHfeqZi90ho2QvdfU0WCPXIsS4/p6AIa5xFPSgtPDo31z1WzkJRE=
---

# py-structure（目录结构 / 中文命名 / 注释 / 调用规则 / 数据传递 / 路径）

> 原子子技能（promoted）。原 python-app-standard「目录结构 / 命名规范 / 变量命名与注释规范 / 调用规则 / 路径规范」章节。

## 目录结构

```
{流程根目录}/
├── 主流程.py                    # 入口文件，固定顺序调用子流程
├── 流程A_{源-用途}.py           # 子流程 A
├── 流程B_{源-用途}.py           # 子流程 B
├── 流程C_{源-用途}.py           # 子流程 C
├── 通知.py                      # 飞书通知模块（失败+成功）
├── 运行记录.py                   # 飞书多维表格运行记录模块
├── .running.lock                # 文件锁（见 py-lock，运行期生成）
├── run.bat                      # 手动运行入口（见 py-bat）
├── 临时/                        # 中间文件目录（每次运行覆盖）
│   ├── 流程A_{源-用途}.json
│   └── ...
└── logs/                        # 日志目录
    ├── 2026-07-29 14-00-00.txt
    └── ...（最多 10 个，超量删旧）
```

- 根目录：建在当前电脑桌面，路径用 `desktop = os.path.join(os.path.expanduser("~"), "Desktop")` 动态识别，**不写死绝对路径**。
- 依赖第三方库在 `主流程.py` 顶部统一自动安装（requests/飞书 SDK/快递100 SDK 等），首次运行即就绪。

## 命名规范

| 项目 | 规则 |
|---|---|
| 主入口 | `主流程.py` |
| 子流程 | `流程{字母}_{数据源-用途}.py`，按调用顺序 A→B→C |
| 通知模块 | `通知.py` |
| 运行记录 | `运行记录.py` |
| 中间文件 | `临时/流程{字母}_{数据源-用途}.json` |
| 日志文件 | `YYYY-MM-DD HH-mm-ss.txt` |

## 变量命名与注释规范（硬性规则）

1. **变量名一律中文命名**：按实际作用命名（`日期列表`/`金额`/`物流状态`/`订单号`），禁止英文变量名；源脚本英文变量（`datalist`→`日期列表`、`amount`→`金额`）生成时必须翻译为中文作用名。
2. **变量声明带类型注解**：`变量名: 类型 = 初始值`（如 `日期列表: list = []`、`运行成功: bool = True`）；注释中描述变量写作 `作用(类型)` 形式。括号不能出现在实际变量名中，类型一律用注解表达。
3. **函数后必有中文备注**：每个函数定义后紧跟中文注释/docstring 说明作用。
4. **每行尽量有中文备注（硬性）**：函数体内每一行都有中文注释（行内或行尾）；`for`/`while` 必须注明循环对象与每轮处理内容；外部 API 请求必须注明请求目标、携带参数、返回用途。

## 调用规则

- 拆分维度：按数据源/外部接口拆分，每个独立接口一个子流程；通知、写入等操作各自独立。
- 调用顺序：主流程固定 A→B→C……依次调用。
- 调用方式：统一函数调用；每个子流程暴露 `run()`，主流程 import 调用，**不使用 subprocess**；异常向上传导，主流程捕获后走错误处理。
- 统一入口函数签名：

```python
def run(tmp_dir: str, prev_file: str = None) -> dict:
    """tmp_dir: 临时/ 目录绝对路径
    prev_file: 上一步输出临时文件绝对路径，流程A 时为 None
    返回: {"status": "success", "data": {...}} 或 {"status": "fail", "error": "..."}"""
```

- 临时文件每次运行全部覆盖重写。

## --limit 验证参数（硬性规则）

- 主流程必须支持 argparse `--limit N`：流程A 查询完成后截断记录只处理前 N 条，避免全量验证超时/重复写生产表；仅验证时使用，正式定时不传（全量）。
- 模板要点：

```python
parser = argparse.ArgumentParser(description="主流程")
parser.add_argument("--limit", type=int, default=0, help="仅处理前 N 条记录（0=全量，用于验证）")
...
# 流程A 成功后：
if args.limit and args.limit > 0:
    # 读取流程A输出文件 → 截断前N条 → 写回
    print(f"[验证] --limit {args.limit}：仅处理前 {len(a_records)} 条记录")
```

- **流程A 成功日志必须在 --limit 截断之后写入（实战经验）**：`write_log("流程A - 成功 - N 条")` 必须放在截断代码块之后，否则日志写入原始全量条数，与实际处理量不符。

## 校验清单

- [DIR_001] auto 必须包含主流程.py作为入口文件
- [DIR_002] auto 子流程命名为流程{字母}_{数据源-用途}.py格式
- [DIR_003] auto 必须包含通知.py飞书通知模块
- [DIR_004] auto 必须包含运行记录.py模块
- [DIR_005] auto 必须包含临时/目录用于中间文件
- [DIR_006] auto 必须包含logs/目录用于日志
- [DIR_007] auto 必须包含run.bat手动运行脚本
- [NAME_001] both 变量名一律使用中文命名，禁止英文变量名
- [NAME_002] both 变量声明必须带类型注解（变量名: 类型 = 初始值）
- [NAME_003] ai 每个函数定义后必须有中文注释/docstring
- [NAME_004] ai 函数体内每一行都必须有中文注释（尤其循环与请求）
- [CALL_001] both 每个子流程必须暴露run(tmp_dir: str, prev_file: str = None) -> dict函数
- [CALL_002] both 主流程必须支持--limit N参数（argparse）用于小样本验证
- [CALL_003] ai 子流程间使用函数调用（import），禁止subprocess
- [CALL_004] ai 主流程固定按A→B→C顺序调用子流程
- [PATH_001] both 流程根目录建在当前电脑桌面，用os.path.expanduser识别，不写死绝对路径
*（内容由AI生成，仅供参考）*
