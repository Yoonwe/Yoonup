# yoonup-workflow

按 Yoonup「工作流文件夹规范」稳定执行任务的豆包技能。

## 适用场景

- Python 流程自动化项目（多子流程编排、飞书通知、定时任务、运行记录、文件锁、日志、run.bat）
- 网页后台数据抓取（JS 逆向/接口直连，输出影刀可用二维列表）

## 技能结构

```
yoonup-workflow/
├── SKILL.md                          # 技能入口与执行约定
└── references/
    ├── agents-convention.md          # Agent 协作规范
    ├── python-app-standard.md        # Python 流程自动化项目规范
    └── web-js-app-implementation.md  # 网页后台数据抓取规范
```

## 执行流程

1. **识别技能** — 判断需求属于 python-app-standard 还是 web-js-app-implementation
2. **读取技能规范** — 读取对应 references 文件全文，含末尾「校验清单」
3. **需求拆分** — 向用户提问确认执行顺序，由用户拍板后开始
4. **按顺序执行** — 严格按规范做事（目录结构、命名、日志、通知、定时任务等）
5. **末端整合校验** — 按校验清单逐项核对，全部通过才允许交付

## 使用方式

在豆包工作中通过 `/yoonup-workflow` 调用，或上传至企业技能中心供团队使用。
