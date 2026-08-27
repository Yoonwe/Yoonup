"""
校验清单模块
从技能文档中抽取的硬性规则，用于校验生成的流程代码是否符合规范
"""
import os
import re
from typing import TypedDict, List, Dict, Any


class CheckItem(TypedDict):
    id: str
    category: str
    description: str
    method: str  # "auto" = 自动化检查, "ai" = AI判断, "both" = 两者结合
    severity: str  # "hard" = 硬性规则, "soft" = 建议


# 从《流程脚手架规范》抽取的校验清单
CHECKLIST: List[CheckItem] = [
    # ===== 目录结构 =====
    {"id": "DIR_001", "category": "目录结构", "description": "必须包含主流程.py作为入口文件", "method": "auto", "severity": "hard"},
    {"id": "DIR_002", "category": "目录结构", "description": "子流程命名为流程{字母}_{数据源-用途}.py格式", "method": "auto", "severity": "hard"},
    {"id": "DIR_003", "category": "目录结构", "description": "必须包含通知.py飞书通知模块", "method": "auto", "severity": "hard"},
    {"id": "DIR_004", "category": "目录结构", "description": "必须包含运行记录.py模块", "method": "auto", "severity": "hard"},
    {"id": "DIR_005", "category": "目录结构", "description": "必须包含临时/目录用于中间文件", "method": "auto", "severity": "hard"},
    {"id": "DIR_006", "category": "目录结构", "description": "必须包含logs/目录用于日志", "method": "auto", "severity": "hard"},
    {"id": "DIR_007", "category": "目录结构", "description": "必须包含run.bat手动运行脚本", "method": "auto", "severity": "hard"},

    # ===== 命名规范 =====
    {"id": "NAME_001", "category": "命名规范", "description": "变量名一律使用中文命名，禁止英文变量名", "method": "both", "severity": "hard"},
    {"id": "NAME_002", "category": "命名规范", "description": "变量声明必须带类型注解（变量名: 类型 = 初始值）", "method": "both", "severity": "hard"},
    {"id": "NAME_003", "category": "命名规范", "description": "每个函数定义后必须有中文注释/docstring", "method": "ai", "severity": "hard"},
    {"id": "NAME_004", "category": "命名规范", "description": "函数体内每一行都必须有中文注释（尤其循环与请求）", "method": "ai", "severity": "hard"},

    # ===== 调用规则 =====
    {"id": "CALL_001", "category": "调用规则", "description": "每个子流程必须暴露run(tmp_dir: str, prev_file: str = None) -> dict函数", "method": "both", "severity": "hard"},
    {"id": "CALL_002", "category": "调用规则", "description": "主流程必须支持--limit N参数（argparse）用于小样本验证", "method": "both", "severity": "hard"},
    {"id": "CALL_003", "category": "调用规则", "description": "子流程间使用函数调用（import），禁止subprocess", "method": "ai", "severity": "hard"},
    {"id": "CALL_004", "category": "调用规则", "description": "主流程固定按A→B→C顺序调用子流程", "method": "ai", "severity": "hard"},

    # ===== 文件锁 =====
    {"id": "LOCK_001", "category": "文件锁", "description": "主流程启动时必须通过.running.lock文件锁防并发", "method": "both", "severity": "hard"},
    {"id": "LOCK_002", "category": "文件锁", "description": "锁文件必须在项目根目录，严禁放临时/目录", "method": "both", "severity": "hard"},
    {"id": "LOCK_003", "category": "文件锁", "description": "锁机制采用PID存活检测，内容为{PID}|{时间}格式", "method": "both", "severity": "hard"},
    {"id": "LOCK_004", "category": "文件锁", "description": "必须先acquire_lock()成功，再执行init_dirs()", "method": "ai", "severity": "hard"},
    {"id": "LOCK_005", "category": "文件锁", "description": "释放锁必须带LOCK_HELD持有标志，防止误删并发实例的锁", "method": "both", "severity": "hard"},
    {"id": "LOCK_006", "category": "文件锁", "description": "LOCK_TIMEOUT_HOURS必须与计划任务ExecutionTimeLimit一致（默认4小时）", "method": "both", "severity": "hard"},

    # ===== 日志规则 =====
    {"id": "LOG_001", "category": "日志规则", "description": "一次运行固定写入同一个日志文件（单文件，禁止每次新建）", "method": "both", "severity": "hard"},
    {"id": "LOG_002", "category": "日志规则", "description": "日志格式：[时间] 流程X_用途 - 成功/失败 - 详情", "method": "ai", "severity": "hard"},
    {"id": "LOG_003", "category": "日志规则", "description": "每个子流程成功行必须体现处理条数（成功 - N条）", "method": "both", "severity": "hard"},
    {"id": "LOG_004", "category": "日志规则", "description": "主流程结束必须输出条数汇总（流程A N条 / 流程B N条 / 合计N条）", "method": "both", "severity": "hard"},
    {"id": "LOG_005", "category": "日志规则", "description": "最多保留10个日志文件，超出删除最早的（启动时清理保留9个旧日志）", "method": "both", "severity": "hard"},

    # ===== 终端进度 =====
    {"id": "PROG_001", "category": "终端进度", "description": "抓取/API批量调用/写入时必须用\\r+\\033[K同行动态刷新进度", "method": "both", "severity": "hard"},
    {"id": "PROG_002", "category": "终端进度", "description": "多表/多数据源必须分别打印获取数量，禁止只打印汇总", "method": "ai", "severity": "hard"},
    {"id": "PROG_003", "category": "终端进度", "description": "进度行仅输出终端，禁止写入日志", "method": "ai", "severity": "hard"},
    {"id": "PROG_004", "category": "终端进度", "description": "禁止使用tqdm等第三方进度库，保持零依赖", "method": "auto", "severity": "hard"},

    # ===== 错误处理 =====
    {"id": "ERR_001", "category": "错误处理", "description": "任一子流程失败立即停止主流程", "method": "ai", "severity": "hard"},
    {"id": "ERR_002", "category": "错误处理", "description": "失败后调用通知.py的notify_groups()通知到群聊", "method": "both", "severity": "hard"},

    # ===== 飞书通知 =====
    {"id": "FEISHU_001", "category": "飞书通知", "description": "通知.py必须包含规范中的APP_ID和APP_SECRET凭证", "method": "both", "severity": "hard"},
    {"id": "FEISHU_002", "category": "飞书通知", "description": "失败通知群名关键词包含万威,黄俊文,肖晓雯", "method": "both", "severity": "hard"},
    {"id": "FEISHU_003", "category": "飞书通知", "description": "成功通知使用reply_message回复指定message_id", "method": "both", "severity": "hard"},
    {"id": "FEISHU_004", "category": "飞书通知", "description": "reply_message请求体必须包含msg_type: text字段", "method": "both", "severity": "hard"},
    {"id": "FEISHU_005", "category": "飞书通知", "description": "所有通知函数必须返回dict，调用方必须打印结果，严禁try/except: pass", "method": "both", "severity": "hard"},
    {"id": "FEISHU_006", "category": "飞书通知", "description": "成功通知模板：{文件夹名}-{时间}:完成；失败：{文件夹名}-{时间}:{错误}", "method": "ai", "severity": "hard"},

    # ===== 运行记录 =====
    {"id": "RECORD_001", "category": "运行记录", "description": "运行记录.py必须包含APP_TOKEN和TABLE_ID凭证", "method": "both", "severity": "hard"},
    {"id": "RECORD_002", "category": "运行记录", "description": "每次运行结束必须调用report_run_record写入记录", "method": "both", "severity": "hard"},
    {"id": "RECORD_003", "category": "运行记录", "description": "写入前查询今日同应用成功记录，命中则PUT覆盖，无则POST新建", "method": "ai", "severity": "hard"},
    {"id": "RECORD_004", "category": "运行记录", "description": "应用名称必须动态取os.path.basename(ROOT_DIR)，禁止硬编码", "method": "both", "severity": "hard"},
    {"id": "RECORD_005", "category": "运行记录", "description": "必须校验飞书API返回的code字段，code!=0返回失败", "method": "both", "severity": "hard"},

    # ===== Token与重试 =====
    {"id": "TOKEN_001", "category": "Token与重试", "description": "Token必须带缓存自动刷新，提前5分钟过期留buffer", "method": "both", "severity": "hard"},
    {"id": "TOKEN_002", "category": "Token与重试", "description": "所有HTTP请求必须显式设置timeout参数", "method": "both", "severity": "hard"},
    {"id": "TOKEN_003", "category": "Token与重试", "description": "所有外部API调用必须带重试逻辑（最多3次，遇RequestException重试）", "method": "both", "severity": "hard"},
    {"id": "TOKEN_004", "category": "Token与重试", "description": "批量写入3次重试仍失败则跳过该批，不得中断整个流程", "method": "ai", "severity": "hard"},
    {"id": "TOKEN_005", "category": "Token与重试", "description": "慢接口（如快递100识别）禁止加重复重试，失败返回空值由下一轮补跑", "method": "ai", "severity": "hard"},

    # ===== 定时任务 =====
    {"id": "CRON_001", "category": "定时任务", "description": "必须自动搭建Windows计划任务，每小时执行一次", "method": "ai", "severity": "hard"},
    {"id": "CRON_002", "category": "定时任务", "description": "Action必须为独立Python+带引号绝对路径+WorkingDirectory留空", "method": "ai", "severity": "hard"},
    {"id": "CRON_003", "category": "定时任务", "description": "触发器为DailyTrigger(2)+Repetition每小时重复，禁止IdleTrigger", "method": "ai", "severity": "hard"},
    {"id": "CRON_004", "category": "定时任务", "description": "ExecutionTimeLimit=PT4H，MultipleInstances=IgnoreNew，StartWhenAvailable=True", "method": "ai", "severity": "hard"},

    # ===== run.bat规范 =====
    {"id": "BAT_001", "category": "run.bat规范", "description": "run.bat必须用UTF-8 with BOM编码写入", "method": "auto", "severity": "hard"},
    {"id": "BAT_002", "category": "run.bat规范", "description": "run.bat必须使用CRLF换行符", "method": "auto", "severity": "hard"},
    {"id": "BAT_003", "category": "run.bat规范", "description": "必须固定引用独立Python绝对路径，禁止动态查找Marvis内置Python", "method": "both", "severity": "hard"},
    {"id": "BAT_004", "category": "run.bat规范", "description": "必须设置PYTHONDONTWRITEBYTECODE=1禁止生成__pycache__", "method": "both", "severity": "hard"},
    {"id": "BAT_005", "category": "run.bat规范", "description": "主流程.py头部必须加sys.dont_write_bytecode = True", "method": "both", "severity": "hard"},
    {"id": "BAT_006", "category": "run.bat规范", "description": "bat文件首行留空行避让BOM，从第二行开始写@echo off", "method": "auto", "severity": "hard"},

    # ===== 工具脚本规范 =====
    {"id": "TOOL_001", "category": "工具脚本规范", "description": "所有工具脚本禁止使用input()/raw_input()阻塞式交互", "method": "both", "severity": "hard"},
    {"id": "TOOL_002", "category": "工具脚本规范", "description": "参数通过argparse或环境变量传入，失败/成功通过sys.exit(0/1)返回", "method": "both", "severity": "hard"},

    # ===== 路径规范 =====
    {"id": "PATH_001", "category": "路径规范", "description": "流程根目录建在当前电脑桌面，用os.path.expanduser识别，不写死绝对路径", "method": "both", "severity": "hard"},

    # ===== 网页JS逆向抓取技能 =====
    {"id": "WEB_001", "category": "网页JS逆向", "description": "必须通过JS逆向/接口直连取数，禁止模拟人工操作（browser-agent点击/UI自动化）", "method": "ai", "severity": "hard"},
    {"id": "WEB_002", "category": "网页JS逆向", "description": "token通过影刀JS或CDP自动读取，禁止要求用户手动从Console复制", "method": "ai", "severity": "hard"},
    {"id": "WEB_003", "category": "网页JS逆向", "description": "输出result只传二维列表/字典，不附加无关内容", "method": "both", "severity": "hard"},
    {"id": "WEB_004", "category": "网页JS逆向", "description": "日期统一YYYY-MM-DD格式，提供开始时间+结束时间两个变量，接口紧凑格式由脚本内部转换", "method": "both", "severity": "hard"},
    {"id": "WEB_005", "category": "网页JS逆向", "description": "脚本顶部必须设可配置变量区，一行式精简备注，禁止长注释块", "method": "both", "severity": "hard"},
    {"id": "WEB_006", "category": "网页JS逆向", "description": "脚本分三层：配置区、通用模块（CDP/请求/分页/清洗）、业务函数", "method": "ai", "severity": "hard"},
    {"id": "WEB_007", "category": "网页JS逆向", "description": "Chrome路径留空时自动探测（注册表→常见路径），禁止写死单一路径", "method": "both", "severity": "hard"},
    {"id": "WEB_008", "category": "网页JS逆向", "description": "交付脚本必须同时输出请求结构（URL+method+参数），stdout的JSON带request字段", "method": "both", "severity": "hard"},
    {"id": "WEB_009", "category": "网页JS逆向", "description": "使用独立user-data-dir调试实例+CDP，禁止复制/重命名默认profile保留登录态", "method": "ai", "severity": "hard"},
    {"id": "WEB_010", "category": "网页JS逆向", "description": "分组/筛选参数必须实测可选值后固化，禁止靠猜", "method": "ai", "severity": "hard"},
    {"id": "WEB_011", "category": "网页JS逆向", "description": "依赖自动安装，兼容PEP 668和旧版pip", "method": "both", "severity": "hard"},
    {"id": "WEB_012", "category": "网页JS逆向", "description": "分页拉取取全量，禁止只取第一页", "method": "both", "severity": "hard"},
    {"id": "WEB_013", "category": "网页JS逆向", "description": "业务失败码（如999998）视为token失效，自动清缓存重取并重试一次", "method": "both", "severity": "hard"},
    {"id": "WEB_014", "category": "网页JS逆向", "description": "数据清洗：HTML标签剥离、时间戳格式化、嵌套对象文本提取", "method": "both", "severity": "hard"},
    {"id": "WEB_015", "category": "网页JS逆向", "description": "多分组结果合并必须extend展平后去重，禁止append嵌套列表", "method": "ai", "severity": "hard"},
    {"id": "WEB_016", "category": "网页JS逆向", "description": "执行过程发现问题必须同步更新技能文档，禁止只留在对话上下文", "method": "ai", "severity": "hard"},
]


def get_checklist_by_category(category: str = None) -> List[CheckItem]:
    """按类别获取校验清单"""
    if category:
        return [c for c in CHECKLIST if c["category"] == category]
    return CHECKLIST


def get_auto_check_items() -> List[CheckItem]:
    """获取可自动化检查的条目"""
    return [c for c in CHECKLIST if c["method"] in ("auto", "both")]


def get_ai_check_items() -> List[CheckItem]:
    """获取需要AI判断的条目"""
    return [c for c in CHECKLIST if c["method"] in ("ai", "both")]


def format_checklist_for_ai() -> str:
    """将校验清单格式化为AI可读的文本"""
    lines = ["# 流程脚手架规范 - 校验清单\n"]
    current_category = None
    for item in CHECKLIST:
        if item["category"] != current_category:
            current_category = item["category"]
            lines.append(f"\n## {current_category}\n")
        severity_tag = "[硬性]" if item["severity"] == "hard" else "[建议]"
        lines.append(f"- {item['id']} {severity_tag} {item['description']}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(f"校验清单共 {len(CHECKLIST)} 条")
    print(f"其中自动化检查 {len(get_auto_check_items())} 条")
    print(f"AI判断 {len(get_ai_check_items())} 条")
    print("\n" + format_checklist_for_ai())
