---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_d5aaad7faa5b11f190de525400461939
    ReservedCode1: gp1T8hLd63fip2lCHkym65gnN1QQeaOIMjxH4/xL3ov0IJDoiX/9Hw2Ollst8KwxfXGmCNVctDuPzA5kLyFdju+qnPBqi7WG8cu5CXJlp7yQk7vwdaXyD6HLGQBNveZvVtgRFpmxLNIl4nsj3Q6LUD30Y+9J/En8cR/lqYBN7YLN/SfjMzzeHpOKifM=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_d5aaad7faa5b11f190de525400461939
    ReservedCode2: gp1T8hLd63fip2lCHkym65gnN1QQeaOIMjxH4/xL3ov0IJDoiX/9Hw2Ollst8KwxfXGmCNVctDuPzA5kLyFdju+qnPBqi7WG8cu5CXJlp7yQk7vwdaXyD6HLGQBNveZvVtgRFpmxLNIl4nsj3Q6LUD30Y+9J/En8cR/lqYBN7YLN/SfjMzzeHpOKifM=
---

# 【站点知识卡】抖店客服（fxg.jinritemai.com）

> 知识卡定位：只记录抖店客服后台的**站点特有实测经验**，不晋级为通用技能；换站点时新建对应知识卡，禁止把站点经验写进通用规范。
> 数据日期：2026-08-24 实测；接口/页面可能变动，失效时更新本卡并知会用户。

## 登录

- 登录页真实地址：`fxg.jinritemai.com/login/common`。`im.jinritemai.com` 根域是宣传页，未登录访问工作台 URL 不会重定向到独立登录页，而是直接渲染页面提示"登录过期，请重新登录"——模拟登录前先定位页面内登录触发点，或直接导航到登录页。
- **邮箱登录（无验证码，更优方案）**：登录页切"邮箱登录"tab，邮箱+密码直登，无短信验证码环节，可全自动（实测 WAN_2003@126.COM 成功）。表单元素：邮箱输入框 `placeholder="请输入邮箱"`、密码输入框 `input[type="password"]`、登录按钮。脚本顶部配置区新增 `登录账号` / `登录密码` / `登录店铺` 三个变量。

## 选店（多店铺账号）

- 出现"请选择店铺"页时，店铺卡片为 `div[class*="roleItem"]`，React 事件绑定在元素上，`el.click()` 不触发跳转，必须用 CDP `Input.dispatchMouseEvent` 按真实坐标点击。
- **登录态判定时机**：`currentuser` 接口在未选店前返回 code=10005（即使账号已登录并显示店铺列表），选店后才 code=0 且 `data.ShopName` 显示店铺名。判定"已进入目标店铺"必须等选店动作完成后，再取 currentuser 确认 ShopName 匹配目标店铺（如"352官方旗舰店"）。

## 客服分组与筛选（queryStaffData）

- `queryType` 实测：`1` 按客服（每行一名客服）、`2` 按客服分组（每行一个分组，含 `staffGroupName`/`staffGroupCount`），其余值返回业务错误码即不可用。
- 表头差异：按客服含"账号"列；按分组含"分组、客服人数"列。
- **按客服明细（queryType=1）支持按特定分组筛选**：URL 追加 `groupId=<编号>`。
- 分组编号映射表（从页面"客服分组"下拉逐个选择后抓包实测）：

  | 分组名称 | groupId | 说明 |
  |---|---|---|
  | 全店 | （不传 groupId） | 默认全部客服 |
  | 售前客服 | 9878 | |
  | 售后客服 | 146284 | |
  | 售后疑难 | 1233096 | |
  | 未分组客服 | （无） | 页面下拉无此选项，无法单独筛选 |

- **接口不支持多选**：`groupId=A,B` 与 `groupId=A|B` 均返回业务错误码 609039000；重复参数 `groupId=A&groupId=B` 只取第一个生效（实测 `146284&9878` 只返回售后 8 人）。
- **多选必须脚本层实现**：循环多个 groupId 分别请求全量，按"客服名+账号"去重合并；脚本配置区用分组名称列表表达（如 `["售后客服","售前客服"]`），名称到编号映射在脚本内维护，用户无需记数字。
- 日期紧凑格式：接口要求 startTime=YYYYMMDD，脚本内部由 YYYY-MM-DD 转换。

## 退出清理（抖店域范围）

取数完毕执行"退出登录并清理"三步：`Network.deleteCookies` 清抖店域会话 cookie → `Page.reload` → `Page.close`；只清浏览器会话 cookie，不动本地缓存 JSON。下次取数仍先注入缓存，缓存失效才触发邮箱重登。

## 滑块

- 现状：抖店邮箱登录实测无验证码（账号密码直登），正常不经过滑块环节。若触发（全新实例/IP 异常/频繁登录），应对框架见 webjs-login 通用规范。
- 跨域 iframe（如 verify.snssdk.com）无法读内部坐标或点选类验证码，自动方案不可用 → 打印提示人工完成。

## 踩坑备忘

- 参数名别靠猜：实际用 `groupId`，`staffGroupIds`/`staffGroupName`/`groupName` 等猜测参数均不生效（返回全部数据而非筛选结果）。
- 分组编号必须从页面下拉逐个选择后抓包获取，禁止臆造。
- 邮箱登录优先于手机号+短信验证码（更快更稳）。

## 校验清单

- [WEB_018] ai 取数完毕执行"退出登录并清理"：清抖店域会话 cookie → 刷新 → 关闭，不动本地缓存 JSON
- [WEB_019] ai 登录态判定时机：选店动作完成后再取 currentuser 确认 ShopName 匹配目标店铺
- [KB_DOUYIN_001] both groupId/queryType 取值来自实测映射表，禁止臆造
*（内容由AI生成，仅供参考）*
