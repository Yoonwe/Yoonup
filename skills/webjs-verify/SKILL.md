---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_d4f40118aa5b11f188bd525400287e28
    ReservedCode1: M6sIBE4Gpg+hTZk1rq3T8II2ccBObNaqohmQrqceHy4xKa/DECLsy9oitW2NvU2v2QfDz9SzQcwFUFkFOZ2YcrHztOUdUoAz/rh0L8fKO1BNcitia9pL4AbYhXuFbNy80qwXdSaLUjqYMum+xoWHzsGSdkDp5m/TqtxFse2hL3z8FtwYtDQYylxpQgk=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_d4f40118aa5b11f188bd525400287e28
    ReservedCode2: M6sIBE4Gpg+hTZk1rq3T8II2ccBObNaqohmQrqceHy4xKa/DECLsy9oitW2NvU2v2QfDz9SzQcwFUFkFOZ2YcrHztOUdUoAz/rh0L8fKO1BNcitia9pL4AbYhXuFbNy80qwXdSaLUjqYMum+xoWHzsGSdkDp5m/TqtxFse2hL3z8FtwYtDQYylxpQgk=
---

# webjs-verify（数据验证与交付）

> 原子子技能。web-js 抓取脚本交付前必须执行的输出结构与运行验证协议。

## 输出规范（强制）

- result 只传二维列表 / 字典，不附加无关内容。
- 用户指定固定长度的表（如"长度 2 = 表头 + 合计"）时必须严格保持；新数据按列横向延长，不纵向追加成多行。
- 日期类字段统一 **YYYY-MM-DD**：有日期选择框的页面一律提供"开始时间 + 结束时间"两个变量（如 `开始时间 = "2026-08-24"`）；接口要求紧凑格式（如抖店 startTime=20260824）由脚本内部自动转换，用户侧只见 YYYY-MM-DD。

## 交付要求

1. **交付脚本必须同时输出请求结构**：向用户交付时在回复中给出实际请求的完整 URL + 查询参数结构（method / URL / query 参数 / 分页参数）；脚本运行 stdout 的 JSON 中带 `request` 字段（本次实际发起的第一条请求 URL）。用户无法核对与复用是交付失败。
2. **脚本顶部可配置变量区**：核心变量（抓取日期、抓取分组、端口、页大小）默认值取自顶部变量，命令行参数仅作覆盖项。
3. **交付前必须自行运行验证**：不能只贴代码。本地直连验证 = 脚本补全 headers 直连接口，与页面数据逐项核对（数量、合计、字段值），确认输出长度、列数、关键值符合约定。
4. 验证后输出核对结论（行数/列数/合计/抽样值），与脚本路径一并交付。

## 通用分组/多选核对

- 多分组抓取核对合并后行数 = 各分组去重后总和（防止 append 嵌套导致的只保留第一组）。
- 请求 stdout 的 `request` 字段应体现实际使用的分组参数（如 groupId），与配置区意图一致。

## 校验清单

- [WEB_003] both 输出 result 只传二维列表/字典，不附加无关内容
- [WEB_004] both 日期统一 YYYY-MM-DD 格式，提供开始时间+结束时间两个变量，接口紧凑格式由脚本内部转换
- [WEB_005] both 脚本顶部必须设可配置变量区，一行式精简备注，禁止长注释块
- [WEB_008] both 交付脚本必须同时输出请求结构（URL+method+参数），stdout 的 JSON 带 request 字段
- [WEB_020] ai 交付前必须自行运行验证，不能只贴代码
*（内容由AI生成，仅供参考）*
