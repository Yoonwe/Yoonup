---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 57fb548516b32a13ed9be7c0410d64ef_d37e9b9daa5b11f1be88525400aeaaa3
    ReservedCode1: mtqlYso8i8mF6NeMJDkdvCPVDVSBGf2Hrmt2wIISgb7pCUtWMnMnbpsOiMnLukXxnQOZek81HHDLVKmOe6HbSoo4sAgbo2di6nKJp38OWwpSo3M4sW6ztya3jzxbkx1CO4cubXko1STzWCHOyHXxLrZnIckGpWjYg9BGOSUAb/fp4wT6ep/fCKIXH3I=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 57fb548516b32a13ed9be7c0410d64ef_d37e9b9daa5b11f1be88525400aeaaa3
    ReservedCode2: mtqlYso8i8mF6NeMJDkdvCPVDVSBGf2Hrmt2wIISgb7pCUtWMnMnbpsOiMnLukXxnQOZek81HHDLVKmOe6HbSoo4sAgbo2di6nKJp38OWwpSo3M4sW6ztya3jzxbkx1CO4cubXko1STzWCHOyHXxLrZnIckGpWjYg9BGOSUAb/fp4wT6ep/fCKIXH3I=
---

# webjs-core（逆向通用流程与三层脚本）

> 原子子技能。web-js 抓取的通用能力要求、技术路径与脚本结构。站点特有细节一律查 knowledge/，不写本文件。

## 通用能力要求（Agent 自行实现，不限定语言）

- 依赖自动安装（兼容系统级 Python 的 PEP 668 保护与旧版 pip）。
- 统一请求头构造：token 注入、Origin/Referer 等防跨域头补全。
- 分页拉取：按总页数 / 游标循环取全量，避免只取第一页。
- 响应校验：成功码判定；业务失败码（如 999998）视为 token 失效信号，自动清缓存重取并重试一次（术语见 GLOSSARY）。
- 数据清洗：HTML 标签与实体剥离、时间戳（毫秒/秒）格式化、嵌套消息对象文本提取。
- 表格构建：按列定义生成二维列表（表头行 + 数据行 + 可选合计行）；支持多模块横向延长合并（表头追加列、数据行按位补值）。
- CDP 浏览器管理：调试端口探测、独立 user-data-dir 启动调试实例、优雅关闭；动用户 Chrome 前必须提示风险。
- **Chrome 可执行文件自动探测（换电脑零配置）**：脚本顶部配置区 `Chrome路径` 留空时自动探测，顺序：显式配置路径 → 注册表 App Paths（HKLM/HKCU 的 `...\App Paths\chrome.exe`，覆盖自定义安装）→ 常见默认路径（Program Files / Program Files (x86) / LOCALAPPDATA）；全部未命中再报错提示手动填顶部变量。禁止写死单一路径。

## 脚本结构规范（三层模板）

1. **顶部配置区**：全中文变量命名；备注必须**一行式精简**（每变量一行短注释）；日期用**开始时间 + 结束时间**两个变量（YYYY-MM-DD，留空默认昨天 / 等于开始时间），接口紧凑格式由脚本内部转换；命令行参数仅作覆盖项，默认值取自顶部变量。**禁止长注释块**（影刀魔法指令复制粘贴时超长/多行中文备注会导致无法识别，实测踩坑）。
2. **通用模块**：CDP 客户端、请求封装、分页拉取、行映射构建（含不同分组的表头与字段映射分支）。
3. **业务函数**：薄封装取数 + 清洗 + 组表；`main` 解析命令行覆盖顶部变量并输出 JSON。

## 分组维度确认规范（通用流程）

- 逆向接口的分组/筛选参数必须**实测可选值**后再固化到脚本与文档：逐项尝试后确认哪些值有效、哪些返回业务错误码；禁止靠猜参数名与取值。
- 不同分组维度表头不同（如按明细含"账号"列、按分组含"分组、人数"列），字段映射一并实测。
- 多分组/多选若接口不支持，**必须脚本层实现**：循环多个取值分别请求全量，再按业务主键（如"客服名+账号"）去重合并。

## 踩坑要点（通用，非站点特定）

- 交付脚本的顶部配置区备注要一行式精简；中文变量名无碍，长注释才是问题。
- 多分组结果合并必须 `extend` 展平后再去重，禁止把每组行列表整体 `append`（嵌套列表被当单行，只保留第一组）。
- 逆向列定义优先从前端 chunk 找字段映射，再与 Network 响应逐列核对，避免猜字段名。
- 合并结构理解偏差 → 开工前确认方向（B 类决策），默认按用户偏好横向延长。
- 分页接口需确认总页数 / 合计对象，防漏数据。
- 交付脚本必须输出请求结构（见 webjs-verify）。
- token 本地未过期但服务端失效（业务失败码）→ 需兜底清缓存重取。

## 校验清单

- [WEB_006] ai 脚本分三层：配置区、通用模块（CDP/请求/分页/清洗）、业务函数
- [WEB_007] both Chrome 路径留空时自动探测（注册表→常见路径），禁止写死单一路径
- [WEB_011] both 依赖自动安装，兼容 PEP 668 和旧版 pip
- [WEB_012] both 分页拉取取全量，禁止只取第一页
- [WEB_013] both 业务失败码（如 999998）视为 token 失效，自动清缓存重取并重试一次
- [WEB_014] both 数据清洗：HTML 标签剥离、时间戳格式化、嵌套对象文本提取
- [WEB_015] ai 多分组结果合并必须 extend 展平后去重，禁止 append 嵌套列表
*（内容由AI生成，仅供参考）*
