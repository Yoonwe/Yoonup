---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_ce51ae90aa5b11f188bd525400287e28
    ReservedCode1: IFHmVrOLkYnHeC0Fv2j8dnXM3BmLF+Paly0fz1DKUFz5Fpc/wkien74bZvIcHS55zNDoXZRVFp3h4IBntDybuZ3GWtcdbexLPfDbOxhEJYoJYqL8eCwxoEKEPrsCamsIUTfcw2Nk6ZMhCjb+td2P1K1zZiJUuvXUch89N4UI7hRTUT33kJVzujlp4v4=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_ce51ae90aa5b11f188bd525400287e28
    ReservedCode2: IFHmVrOLkYnHeC0Fv2j8dnXM3BmLF+Paly0fz1DKUFz5Fpc/wkien74bZvIcHS55zNDoXZRVFp3h4IBntDybuZ3GWtcdbexLPfDbOxhEJYoJYqL8eCwxoEKEPrsCamsIUTfcw2Nk6ZMhCjb+td2P1K1zZiJUuvXUch89N4UI7hRTUT33kJVzujlp4v4=
---

# py-feishu（飞书通知）

> 原子子技能（promoted）。原 python-app-standard「飞书通知配置 / 通知模块」章节。凭证沿用原规范既有值；如遇流程需要复用既有飞书应用无需向用户索取。

## 凭证

```python
APP_ID = "cli_a729a2469afed00c"
APP_SECRET = "cPVQMyS75d61KRcpNMxXygaBxhMv4gsH"
```

## 通知逻辑

- **失败通知群**：群名关键词 `"万威, 黄俊文, 肖晓雯"`，使用 `notify_groups()` 发送。
- **成功通知**：使用 `reply_message()` 回复 `om_x100b553b7f9284b4c3f790e4b13825a`。

## 通知文本模板

- 成功：`{流程文件夹名}-{YYYY-MM-DD HH:mm:ss}:完成`
- 失败：`{流程文件夹名}-{YYYY-MM-DD HH:mm:ss}:{具体错误信息}`

## 通知.py 核心接口（含返回值约束）

```python
def notify_groups(app_id: str, app_secret: str, group_names: list[str], message: str) -> dict
    # 向多个群聊发送通知（失败场景）
    # 返回: {"success": True/False, "detail": "结果描述", "codes": [...]}

def reply_message(app_id: str, app_secret: str, message_id: str, text: str) -> dict
    # 回复指定消息（成功场景）
    # 返回: {"success": True/False, "detail": "结果描述", "code": int}
```

**硬性要求**：
- `reply_message` 请求体必须包含 `msg_type: "text"` 字段，缺少会导致飞书返回 99992402 错误。
- 所有通知函数必须返回 dict，调用方必须打印结果，**严禁** `try/except: pass` 静默吞异常。
- 主流程调用通知后示例：`r = reply_message(...); print(f"[通知] 成功回复: {r['detail']}")`。

## 通知模块（多副本模式）

- `通知.py` 采用**多副本**模式：每个流程目录各自生成一份，内含本技能已记录的飞书凭证和通知逻辑；各流程独立维护，不跨流程共享。

## 校验清单

- [FEISHU_001] both 通知.py必须包含规范中的APP_ID和APP_SECRET凭证
- [FEISHU_002] both 失败通知群名关键词包含万威,黄俊文,肖晓雯
- [FEISHU_003] both 成功通知使用reply_message回复指定message_id
- [FEISHU_004] both reply_message请求体必须包含msg_type: text字段
- [FEISHU_005] both 所有通知函数必须返回dict，调用方必须打印结果，严禁try/except: pass
- [FEISHU_006] ai 成功通知模板：{文件夹名}-{时间}:完成；失败：{文件夹名}-{时间}:{错误}
*（内容由AI生成，仅供参考）*
