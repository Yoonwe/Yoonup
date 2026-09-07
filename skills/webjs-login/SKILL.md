---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_d43ce37baa5b11f1a393525400f8a581
    ReservedCode1: c1Xbw9crUrl/sDPPNGTCjOuLdjadSOPTS6tfO9xTO+kgczDAX+QWfNGjmBZg47UhR1h5cwrfHN0OWYlmW4xN72GdeUE9dSkxJRxCcyuhDpspNC5Q6e+dlZLNECEio+4cg8RAPZeQSwsMqgFj6y9w3uaVH6nOZNZR53abJ3z22LkYmQ4p6q4rMPk9Vg4=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_d43ce37baa5b11f1a393525400f8a581
    ReservedCode2: c1Xbw9crUrl/sDPPNGTCjOuLdjadSOPTS6tfO9xTO+kgczDAX+QWfNGjmBZg47UhR1h5cwrfHN0OWYlmW4xN72GdeUE9dSkxJRxCcyuhDpspNC5Q6e+dlZLNECEio+4cg8RAPZeQSwsMqgFj6y9w3uaVH6nOZNZR53abJ3z22LkYmQ4p6q4rMPk9Vg4=
---

# webjs-login（登录态保全与调试实例）

> 原子子技能。负责 Chrome 调试实例的启动/关闭、登录态保全（ABE 限制下唯一可靠取数路径）、cookie 导出注入。站点特有登录/选店细节见 knowledge/。

## Chrome 127+/136+ 关键限制（实测，通用）

1. **Chrome 127+ 全面启用 v20（App-Bound Encryption）加密 cookie**：cookie 只能由 Chrome 进程自身解密，外部程序（DPAPI+AES-GCM 直读 SQLite）一律失败。**严禁复制 / 重命名 / junction 指向原 profile 来"保留登录态"**——profile 路径或完整性变化后 Chrome 拒绝解密 cookie，登录态清空（接口返回 code 10005 登录过期）。
2. **Chrome 136+ 安全限制**：user-data-dir 为默认路径（含显式传入默认路径）时 `--remote-debugging-port` 被强制忽略，无法用已登录的默认 profile 直接开调试端口。

## 唯一可靠取数路径

1. 启动独立 user-data-dir 调试实例：`--remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir=<非默认路径>`；
2. 请用户在调试实例内扫码/账号登录一次（站点若需扫码且无法 AI 替代，明确告知用户这是唯一一次人工操作）；
3. 登录成功后立即用 CDP `Network.getAllCookies` 由 Chrome 自身解密导出全部 cookie 存 JSON 永久缓存；
4. 后续取数：启动独立调试实例 → `Network.setCookies` 注入缓存 cookie 恢复登录态 → 导航目标页 → 接口直连。

## 安全与操作纪律

- 动用户浏览器前必须提示风险；优先探测 9222/9223 是否已监听；已登录浏览器无调试端口时不要无谓重启。
- cookie 保存时机：必须在可驱动浏览器（调试实例）登录成功后立即导出，保存到独立 JSON 并本地缓存；禁止从无效副本导出后误报"已保存"。
- browser-use 定位：底层 Playwright/CDP，连接现有浏览器仍需调试端口，自启实例为空白登录态，无法绕过 ABE 与默认路径调试限制；仅作逆向观察辅助，严禁替代取数。

## 登录滑块验证应对（通用框架）

- 触发条件：全新调试实例首次登录（无指纹积累）、登录/登出过于频繁、IP 异常（代理/机房/频繁切换）、短时间内反复失败重试。
- 避免优先级：① 缓存 cookie 优先注入（能不登录就不登录）；② 首次登录人工一次并导出永久缓存；③ 固定 user-data-dir 积累指纹；④ 自动登录时模拟人工节奏（输入/点击间隔随机化）；⑤ 控制登录频率，避免频繁"清 cookie 退出登录 → 重登"。
- 兜底策略（脚本层）：登录提交后轮询检测验证码特征（`iframe[src*="captcha"/"verify"]`、`tcaptcha`、`div[class*="captcha"]` 且尺寸 >50px 才算可见）→ 优先自动过滑块：定位拖拽按钮 → 读缺口偏移 → CDP `Input.dispatchMouseEvent` 拟人轨迹拖动（先快后慢 + 随机微抖 14~22 段）→ 等待校验；跨域 iframe 无法读内部坐标或点选类验证码 → 打印提示人工完成 → 完成后元素消失自动继续。
- 检测到验证码禁止硬刚重试（连续失败加重风控）；`自动过滑块` 顶部变量可关闭；登录等待秒数不足时人工完成可能超时，可调大 `登录等待秒数`。

## 退出登录与清理（通用模板）

- 请求完毕后执行三步：`Network.deleteCookies` 清目标域会话 cookie → `Page.reload` → `Page.close`；只清浏览器会话 cookie，不动本地缓存 JSON。下次取数仍先注入缓存，缓存失效才触发重登。
- 站点特有清理范围（如抖店域）见 knowledge/ 站点卡。

## 校验清单

- [WEB_009] ai 使用独立 user-data-dir 调试实例 + CDP，禁止复制/重命名默认 profile 保留登录态
- [WEB_017] ai 动用户浏览器前必须提示风险；优先探测 9222/9223 监听，不无谓重启浏览器
- [WEB_LOGIN_001] ai cookie 在可驱动浏览器登录成功后立即导出至独立 JSON，禁止无效副本误报已保存
- [WEB_LOGIN_002] both 滑块应对走注入缓存→人工一次→固定指纹→拟人节奏→兜底自动滑块的优先级，禁止硬刚重试
*（内容由AI生成，仅供参考）*
