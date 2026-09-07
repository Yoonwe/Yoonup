---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_d2b92f25aa5b11f1be88525400aeaaa3
    ReservedCode1: 7CmsikR4e3Sx+pdo2lazFR1hSow/+KADZdQjvNP3MD4KY9RLtCWcfdPdWh2pO51iaa/lkiHyDX9Hmaunem6nEkd1z1DXf2vEsWL8vkTcLWbw36RSo0QhK8dIsVFZ8NEvaqKxxncPRDYs0KkFjzMV6POUXSkpgqGL6+OW7EX2r6v6paFl2z83LOpycyY=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_d2b92f25aa5b11f1be88525400aeaaa3
    ReservedCode2: 7CmsikR4e3Sx+pdo2lazFR1hSow/+KADZdQjvNP3MD4KY9RLtCWcfdPdWh2pO51iaa/lkiHyDX9Hmaunem6nEkd1z1DXf2vEsWL8vkTcLWbw36RSo0QhK8dIsVFZ8NEvaqKxxncPRDYs0KkFjzMV6POUXSkpgqGL6+OW7EX2r6v6paFl2z83LOpycyY=
---

# webjs-router（JS 逆向直连·路由入口）

> 定位：面向任意网页后台（客服系统、电商平台、商家后台等）结构化数据抓取的**唯一入口 router**。Agent 先读本文件判定技能归属，再按需加载 webjs-core / webjs-login / webjs-verify；站点特有经验查 knowledge/。

## 触发条件（任一命中即走本 router 链）

- 用户要求从某网页后台抓取结构化数据（客服对话、订单、报表等），交影刀/表格使用。
- 目标数据在登录墙后，且页面无直接导出、或导出不满足结构要求。

## 核心原则（强制）

1. **JS 逆向 / 接口直连**：必须通过逆向页面 Network 请求、直接调用业务接口取数。禁止模拟人工操作（禁止 browser-agent 点击页面、禁止 UI 自动化采集）。
2. **token 自动化**：token 通过影刀执行 JS 从页面存储读取后传参，或通过 CDP 连接调试浏览器自动读取。禁止要求用户手动从 Console 复制。
3. **一次成型**：动手前先确认需求全面性（B 类决策事项，遵循 adr/0001），确认后交付可用脚本并自行验证，反对反复试错式交付。
4. **输出即用**：输出给影刀的 result 只传二维列表 / 字典，符合影刀参数格式，不附加无关内容。

## 执行前必问清单（B 类决策，必须与用户确认）

- 数据范围：哪些业务模块、每模块的筛选条件（时间区间 / 部门分组 / 关键词 / 分页）。
- 输出结构：二维列表（表头行 + 数据行）还是字典列表；是否带合计行。
- 合并约定：多模块数据合并方向（横向延长列 vs 纵向追加行）、表头与合计行组织方式。
- token 来源：影刀传参 / CDP 自动读取 / 缓存复用。
- 交付物：脚本路径、运行验证结果。

> A 类解析细节（接口还原、字段映射、清洗实现）由 AI 自行解析，禁止反问。

## 技术路径（总览，细节见对应子技能）

1. **逆向定位接口**：Network 面板筛选 XHR/Fetch 定位数据接口；必要时从前端 chunk/JS 源文件提取接口路径与字段映射。
   - 辅助手段（可选）：陌生站点/需登录可见数据时，可选用 browser-use 类框架自动登录、设筛选、翻页以观察请求参数；**仅作逆向观察辅助，严禁其逐项点击页面取数**。
2. **还原请求**：method、URL、Query/body、必要请求头（token 注入、Origin、Referer、Cookie、语言时区）、分页参数、响应结构（列表/合计/分页元数据/成功码判定）。
3. **获取/恢复 token**：优先影刀 JS 读页面存储，或 CDP 连接调试 Chrome；实现本地缓存 + 过期检测（如 JWT exp）。见 webjs-login。
4. **本地直连验证**：脚本补全 headers 直连接口，与页面数据逐项核对（数量、合计、字段值）。
5. **编写脚本**：三层结构见 webjs-core。
6. **验证交付**：见 webjs-verify。

## 路由决策表

| 子技能 | 加载条件 |
|---|---|
| webjs-core | 通用逆向流程、三层脚本、能力要求、踩坑通用项 |
| webjs-login | 登录态、调试实例、CDP、cookie 缓存注入 |
| webjs-verify | 输出结构验证、交付核对 |
| knowledge/site-douyin-kefu | 目标站点为抖店客服（fxg.jinritemai.com） |

## 技能文档同步更新规则

执行中发现问题（报错/参数失效/接口变动/登录态坑）或更优方案，**必须同步更新对应技能文档或 knowledge/ 站点卡**，并在回复中向用户告知本次修改要点。禁止只留在对话上下文。

## 校验清单

- [WEB_001] ai 通过 JS 逆向/接口直连取数，禁止模拟人工操作（browser-agent 点击/UI 自动化）
- [WEB_002] ai token 通过影刀 JS 或 CDP 自动读取，禁止要求用户手动从 Console 复制
- [WEB_010] ai 分组/筛选参数必须实测可选值后固化，禁止靠猜
- [WEB_016] ai 执行过程发现问题必须同步更新技能文档，禁止只留在对话上下文
*（内容由AI生成，仅供参考）*
