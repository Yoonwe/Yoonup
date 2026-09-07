---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_cfd97469aa5b11f188bd525400287e28
    ReservedCode1: Sm/4tU7VgmV9d9ZjwhId07oCEX+J3St7A7NwGl1BmdPxp2KeJUz1H5N0IWFJQ192eUbovjQG3z1eXhPKqR6PW9RCAfC6uMvqBrsd1FkdlH+2/Eu78dfvhcH9OEZoLoWYpscu5xtzWo01ul7kxY9PJ4is4mR2PgJefXATdoA8pOZ1vQbwR++zjF2a4Zo=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_cfd97469aa5b11f188bd525400287e28
    ReservedCode2: Sm/4tU7VgmV9d9ZjwhId07oCEX+J3St7A7NwGl1BmdPxp2KeJUz1H5N0IWFJQ192eUbovjQG3z1eXhPKqR6PW9RCAfC6uMvqBrsd1FkdlH+2/Eu78dfvhcH9OEZoLoWYpscu5xtzWo01ul7kxY9PJ4is4mR2PgJefXATdoA8pOZ1vQbwR++zjF2a4Zo=
---

# py-token（外部 API Token 生命周期与重试策略）

> 原子子技能（promoted）。原 python-app-standard「外部 API Token 生命周期与重试策略」章节，适用于所有使用带有效期 Token 的外部 API（飞书 tenant_access_token 等），尤其长任务（单次运行可能超 1~2 小时）。

## 硬性规则

1. **Token 必须带缓存自动刷新**：严禁只在流程开头获取一次全程复用——长任务后半段 Token 过期，后续写入/回填全部失败。实现：模块级缓存 Token 与过期时间，**提前 5 分钟过期**留 buffer；每次请求前调用获取函数，缓存有效直接返回，否则自动刷新：

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

2. **所有 HTTP 请求必须显式设置 timeout**：每个 `requests.get()` / `requests.post()` 必须带 `timeout=N`。推荐：Token 获取/批量写入 60s，查询/搜索接口 30s。严禁依赖 requests 默认无超时——服务端无响应时无限阻塞，定时任务卡死后后续触发全部跳过、且无日志无通知（实测：读飞书表格 read timeout 30s，进程挂起无输出，下一轮整点检测到锁文件「正在运行」跳过，陷入沉默失效）。
3. **所有外部 API 调用必须带重试**：不仅批量写入，**查询/Token 获取等所有 HTTP 请求**也必须 try-except，遇 `requests.RequestException`（含 Timeout、ConnectionError 等）自动重试最多 3 次，每次重试前重新获取 Token 并 sleep 2s。3 次全失败返回失败结果，由调用方决定中断或跳过。避免单次网络抖动打断整个流程。
4. **批量写入必须失败重试**：批量更新接口（如 records/batch_update）单批失败丢整批数据，**必须重试最多 3 次**，每次重试前重新获取 Token。以下属可恢复错误必须重试：
   - Token 过期类错误码（飞书 `99991672`）
   - 频率限制类错误码（飞书 `99991663`）
   - 网络异常（`requests.RequestException`）
5. **3 次重试仍失败**：打印警告并跳过该批，**不得中断整个流程**——剩余批次继续处理，失败批次由下一轮定时补跑。
6. **慢接口禁止无意义重试**：对响应本身就慢的外部接口（如快递100 autonumber 识别约 11s/条），**严禁**加"3 次重试 + 每次 sleep 2 秒 + 每次重试重新调用识别"——会把单条耗时放大数倍、全流程从分钟级拖到小时级。正确做法：识别一次查询一次，失败返回空值由下一轮定时补跑；瓶颈在官方接口限流，不在代码逻辑。

## 校验清单

- [TOKEN_001] both Token必须带缓存自动刷新，提前5分钟过期留buffer
- [TOKEN_002] both 所有HTTP请求必须显式设置timeout参数
- [TOKEN_003] both 所有外部API调用必须带重试逻辑（最多3次，遇RequestException重试）
- [TOKEN_004] ai 批量写入3次重试仍失败则跳过该批，不得中断整个流程
- [TOKEN_005] ai 慢接口（如快递100识别）禁止加重复重试，失败返回空值由下一轮补跑
*（内容由AI生成，仅供参考）*
