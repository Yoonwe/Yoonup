---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_cb45fa7daa5b11f190de525400461939
    ReservedCode1: mG9h4QwgcsaVmg2bdyGKPvHH2BZy1Oo6bd87O2j7LxsIUrDiAShFi9pzkth3CO5kEiNRGjUbFFG4Zmgm6hLD3jA6UcJPmzQ4uvZpaquKIHjXavsaUsv+HIAWSZUJqjXD99s1Mm0h07CHvG9SNjCHBfLIOV8/LTbQJPi/yK0dfAI7qI4Xg92nkEQto0o=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_cb45fa7daa5b11f190de525400461939
    ReservedCode2: mG9h4QwgcsaVmg2bdyGKPvHH2BZy1Oo6bd87O2j7LxsIUrDiAShFi9pzkth3CO5kEiNRGjUbFFG4Zmgm6hLD3jA6UcJPmzQ4uvZpaquKIHjXavsaUsv+HIAWSZUJqjXD99s1Mm0h07CHvG9SNjCHBfLIOV8/LTbQJPi/yK0dfAI7qI4Xg92nkEQto0o=
---

# python-flow-scaffold（Python 流程脚手架·路由入口）

> 定位：所有 Python 流程开发任务的唯一入口（router）。Agent 必须先读本文件确认任务归属，再按需加载下方原子子技能；共享概念查 GLOSSARY。原 python-app-standard（39k 单体）已按此拆分为 1 router + 10 原子子技能。

## 触发条件（任一命中即走本 router 链）

- 用户要求按脚本/文档批量处理数据或调 API 同步（电商、物流、飞书表等 RPA 流程）。
- 已存在参考脚本/文件，要求按其实现新流程或修复。
- 用户给出业务目标 + 参考材料，要求产出自包含可运行 Python 流程。

## AI 生成行为约束（遵循 adr/0001 提问边界仲裁）

1. **A 类解析型细节禁止反问（自行解析推断）**：数据来源渠道（飞书多维表格/快递100/顺丰等）、处理范围（哪些表/哪些数据）、子流程如何拆分、文件夹名称、文件命名、根目录位置、飞书凭证复用。
2. **B 类决策型事项必须提问确认**：多任务执行顺序、交付口径与全量运行范围、用户明确有偏好的方案选择。
3. **流程划分**：按参考材料中的**业务逻辑和数据源/接口**自行拆分，命名为 `流程{字母}_{数据源-用途}.py`（如 `流程A_飞书-查询.py`、`流程B_快递100-物流状态.py`），不照搬参考文件的拆分方式。
4. **根目录**：直接在用户桌面新建文件夹作为流程根目录，按业务用途命名，不询问用户放哪里。
5. **通知/运行记录模块**：直接复用既有飞书凭证与逻辑，不需要问用户 APP_ID/APP_SECRET/群名/message_id/表 ID。
6. **工具脚本禁止交互式阻塞（硬性）**：生成的所有工具脚本禁止 `input()`/`raw_input()` 阻塞式交互；参数用 argparse 或环境变量传入；成功/失败用 `sys.exit(0/1)` 返回，保证非交互终端可自动验证。

一句话原则：用户给参考材料和口头需求，AI 自己读材料、自己拆步骤、自己建目录，直接生成已验证通过的完整代码；决策型事项除外。

## 路由规则

| 子技能 | 加载条件（trigger） |
|---|---|
| py-structure | 目录结构/中文命名/变量注释/run() 契约/数据传递/--limit/路径 |
| py-lock | 并发/死锁/.running.lock/PID 检测 |
| py-log | 日志写入/条数/汇总/保留策略/终端进度 |
| py-feishu | 飞书群通知/失败通知/成功回复 |
| py-runrecord | 运行记录多维表格/今日覆盖 |
| py-token | Token 缓存刷新/重试/timeout/慢接口 |
| py-cron | Windows 计划任务/每小时触发 |
| py-bat | run.bat 手动入口/编码/独立 Python |
| py-verify | 空跑/联调/失败路径/定时/记录/锁验证 |

## 主流程编排规则（router 层通用）

- 主流程.py 固定按 A→B→C 顺序调用子流程；子流程经 import 函数调用（禁止 subprocess），异常向上传导由主流程捕获。
- 子流程统一签名：`def run(tmp_dir: str, prev_file: str = None) -> dict`，返回 `{"status": "success"/"fail", ...}`。
- 数据传递：主流程把 `tmp_dir` 与上一步输出文件路径传给下一子流程；`临时/` 每次运行覆盖重写。
- 任一子流程失败：立即停止主流程，调用 `通知.py` 的 `notify_groups()` 通知到群（错误处理归属 py-log/py-feishu 细则）。
- 运行环境：生产环境真实凭证，无沙箱隔离；验证时用 `--limit N` 控制样本，正式定时不传。

## 工具脚本规范（AI 自建脚本通用）

- 禁止 input()/raw_input() 阻塞式交互；参数 argparse 或环境变量传入；结果 sys.exit(0/1) 返回。

## 校验清单

- [TOOL_001] both 所有工具脚本禁止使用 input()/raw_input() 阻塞式交互
- [TOOL_002] both 参数通过 argparse 或环境变量传入，失败/成功通过 sys.exit(0/1) 返回
- [PY_ROUTER_001] ai 子流程划分依据业务逻辑与数据源，命名流程{字母}_{数据源-用途}.py
- [PY_ROUTER_002] ai 只加载命中子技能，未重读 39k 旧单体全文
*（内容由AI生成，仅供参考）*
