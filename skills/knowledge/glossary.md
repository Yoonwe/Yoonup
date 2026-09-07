---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_c8fcb445aa5b11f190de525400461939
    ReservedCode1: pP7zeLx06Z4WgFZ7kCfLu+0wp6s0s2l2deTmh0YWyyTLs4gN6OzvUGZVf85cZmyXkvG80oFQ92YpFecgiHIh2jzYjB4FkUqpbvgls2tlB1SfQzhcxOCCQNXZMKgrLf7lP+iJNZEgyR6Vqsmr2hjVLwH7Z5UafHclPhNK6XElpzJwMSLD+KUOkxtjz5U=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_c8fcb445aa5b11f190de525400461939
    ReservedCode2: pP7zeLx06Z4WgFZ7kCfLu+0wp6s0s2l2deTmh0YWyyTLs4gN6OzvUGZVf85cZmyXkvG80oFQ92YpFecgiHIh2jzYjB4FkUqpbvgls2tlB1SfQzhcxOCCQNXZMKgrLf7lP+iJNZEgyR6Vqsmr2hjVLwH7Z5UafHclPhNK6XElpzJwMSLD+KUOkxtjz5U=
---

# Yoonup 公共术语表（GLOSSARY）

> 目的：消除 python 与 web-js 技能对共享概念的重复书写与版本分叉。
> 引用方式：子技能只写差异点，涉及下列术语一律查本表，不再重复定义。

## Token 治理

- **Token 缓存自动刷新**：模块级缓存 Token + 过期时间；每次请求前查缓存，有效直接返回，否则自动刷新。
- **提前过期留 buffer**：缓存过期时间 = 实际过期时刻 - 5 分钟（python）或按 JWT exp 判断（web-js）。
- **业务失败码即失效信号**：接口返回业务失败码（如飞书 99991672、抖店 999998）视为 Token/登录态失效，清缓存重取并重试。

## 请求重试

- **统一重试上限 3 次**：网络异常（RequestException/Timeout/ConnectionError）自动重试，重试前重新取 Token，间隔 2s；3 次全失败返回失败结果由调用方决定。
- **批量写入失败重试**：单批失败丢整批数据，必须重试最多 3 次（可恢复错误码 + 网络异常）；3 次仍失败打印警告并跳过该批，不得中断流程，由下一轮定时补跑。
- **慢接口禁止无意义重试**：响应本身慢的接口（如快递100 autonumber 约 11s/条）严禁加重试放大耗时，失败返回空值由下一轮补跑。

## 超时

- **所有 HTTP 请求必须显式 timeout**：严禁依赖默认无超时（进程无限阻塞 → 定时任务卡死 → 后续触发全部跳过，沉默失效）。
- 推荐值：Token 获取/批量写入 60s；查询/搜索 30s。

## 进度输出

- **\r + \033[K 同行动态刷新**：`print(f"\r\033[K[...] 进度 x/y", end=""); sys.stdout.flush()`，禁止 tqdm 等第三方进度库。
- **仅终端、不入日志**：动态刷新行不得写入日志文件（否则日志被刷屏）；日志只保留每步结果行。

## 数据清洗（web-js）

- HTML 标签与实体剥离、时间戳（毫秒/秒）归一化、嵌套消息对象文本提取、多分组结果 `extend` 展平后去重（禁止 `append` 嵌套列表）。

## 运行记录

- **今日覆盖 + 无则新建**：写入前查"应用名称相同 且 运行成功 且 运行开始时间在今天"的记录，命中 PUT 覆盖、无则 POST 新建。
- **应用名称动态取**：`os.path.basename(ROOT_DIR)`，禁止硬编码；重命名文件夹后自动同步。
- **字段归一化**：单选字段可能为字符串/数组/{text,value}；时间戳可能毫秒/秒/字符串，比对前必须归一化。

## 验证模式

- **--limit N**：主流程 argparse 支持，联调只处理前 N 条，避免全量跑生产表；正式定时不传（全量）。
- **小样本试点 → 全量**：批量操作遵循"少量试点 → 确认结果 → 全量执行"。

## 交互边界

- **A 类解析型细节**（数据来源、范围、拆分、命名、目录、凭证复用）：AI 自决，禁止反问。
- **B 类决策型事项**（执行顺序、范围口径、技能归属、方案质疑）：必须提问确认。
- 详见 `adr/0001-提问边界仲裁.md`。
*（内容由AI生成，仅供参考）*
