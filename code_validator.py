"""
代码校验模块
对生成的流程代码进行自动化检查 + AI辅助检查
"""
import os
import re
from typing import Dict, List, Any, TypedDict
from checklist import CHECKLIST, get_auto_check_items, format_checklist_for_ai


class ValidationResult(TypedDict):
    all_passed: bool
    passed_items: List[str]
    failed_items: List[Dict[str, str]]
    total_count: int
    passed_count: int
    failed_count: int


def auto_validate(project_dir: str, skill_id: str = None) -> ValidationResult:
    """自动化检查生成的项目目录，可按技能过滤校验规则"""
    passed: List[str] = []
    failed: List[Dict[str, str]] = []
    auto_items = get_auto_check_items(skill_id)

    files = os.listdir(project_dir) if os.path.exists(project_dir) else []
    file_contents: Dict[str, str] = {}
    for f in files:
        fpath = os.path.join(project_dir, f)
        if os.path.isfile(fpath) and f.endswith('.py'):
            try:
                with open(fpath, 'r', encoding='utf-8') as fp:
                    file_contents[f] = fp.read()
            except:
                pass

    all_code = "\n".join(file_contents.values())

    # DIR_001: 主流程.py
    if "主流程.py" in files:
        passed.append("DIR_001")
    else:
        failed.append({"id": "DIR_001", "reason": "缺少主流程.py入口文件"})

    # DIR_002: 子流程命名
    sub_flows = [f for f in files if re.match(r'^流程[A-Z]_.+\.py$', f)]
    if sub_flows:
        passed.append("DIR_002")
    else:
        failed.append({"id": "DIR_002", "reason": "未找到符合命名规范的子流程文件（流程{字母}_{数据源-用途}.py）"})

    # DIR_003: 通知.py
    if "通知.py" in files:
        passed.append("DIR_003")
    else:
        failed.append({"id": "DIR_003", "reason": "缺少通知.py"})

    # DIR_004: 运行记录.py
    if "运行记录.py" in files:
        passed.append("DIR_004")
    else:
        failed.append({"id": "DIR_004", "reason": "缺少运行记录.py"})

    # DIR_005: 临时目录
    if os.path.isdir(os.path.join(project_dir, "临时")):
        passed.append("DIR_005")
    else:
        failed.append({"id": "DIR_005", "reason": "缺少临时/目录"})

    # DIR_006: logs目录
    if os.path.isdir(os.path.join(project_dir, "logs")):
        passed.append("DIR_006")
    else:
        failed.append({"id": "DIR_006", "reason": "缺少logs/目录"})

    # DIR_007: run.bat
    if "run.bat" in files:
        passed.append("DIR_007")
    else:
        failed.append({"id": "DIR_007", "reason": "缺少run.bat"})

    # NAME_001: 中文变量名（检查是否有明显的英文变量名）
    english_vars = re.findall(r'\b([a-z_][a-z0-9_]{2,})\s*[:=]', all_code)
    common_en = ['import', 'from', 'def', 'return', 'if', 'else', 'for', 'while', 'try', 'except',
                 'print', 'open', 'with', 'as', 'in', 'not', 'and', 'or', 'true', 'false', 'none',
                 'self', 'cls', 'init', 'str', 'int', 'float', 'list', 'dict', 'bool', 'set', 'tuple',
                 'os', 'sys', 're', 'json', 'time', 'datetime', 'requests', 'subprocess', 'argparse',
                 'app', 'root', 'dir', 'file', 'path', 'tmp', 'log', 'lock', 'token', 'url', 'api',
                 'data', 'code', 'msg', 'res', 'req', 'headers', 'params', 'payload', 'response']
    suspicious = [v for v in set(english_vars) if v.lower() not in common_en and len(v) > 2]
    if len(suspicious) <= 5:  # 允许少量必要的英文（如库名）
        passed.append("NAME_001")
    else:
        failed.append({"id": "NAME_001", "reason": f"发现可能的英文变量名: {', '.join(suspicious[:10])}"})

    # NAME_002: 类型注解（检查变量声明是否有: 类型）
    typed_vars = re.findall(r'[\u4e00-\u9fa5]+\s*:\s*\w+', all_code)
    if typed_vars:
        passed.append("NAME_002")
    else:
        failed.append({"id": "NAME_002", "reason": "未发现带类型注解的中文变量声明"})

    # CALL_001: run函数签名
    run_pattern = r'def\s+run\s*\(\s*tmp_dir\s*:\s*str\s*,\s*prev_file\s*:\s*str\s*=\s*None\s*\)\s*->\s*dict'
    if re.search(run_pattern, all_code):
        passed.append("CALL_001")
    else:
        failed.append({"id": "CALL_001", "reason": "子流程未找到符合规范的run(tmp_dir: str, prev_file: str = None) -> dict函数"})

    # CALL_002: --limit参数
    if "--limit" in all_code and "argparse" in all_code:
        passed.append("CALL_002")
    else:
        failed.append({"id": "CALL_002", "reason": "主流程缺少--limit参数或未使用argparse"})

    # LOCK_001: 文件锁
    if ".running.lock" in all_code and "acquire_lock" in all_code:
        passed.append("LOCK_001")
    else:
        failed.append({"id": "LOCK_001", "reason": "缺少.running.lock文件锁机制"})

    # LOCK_002: 锁在根目录
    if "ROOT_DIR" in all_code and ".running.lock" in all_code:
        passed.append("LOCK_002")
    else:
        failed.append({"id": "LOCK_002", "reason": "锁文件路径可能不在项目根目录"})

    # LOCK_003: PID锁格式
    if "os.getpid()" in all_code and "tasklist" in all_code:
        passed.append("LOCK_003")
    else:
        failed.append({"id": "LOCK_003", "reason": "未使用PID存活检测锁机制"})

    # LOCK_005: LOCK_HELD标志
    if "LOCK_HELD" in all_code:
        passed.append("LOCK_005")
    else:
        failed.append({"id": "LOCK_005", "reason": "缺少LOCK_HELD持有标志"})

    # LOCK_006: LOCK_TIMEOUT_HOURS
    if "LOCK_TIMEOUT_HOURS" in all_code:
        passed.append("LOCK_006")
    else:
        failed.append({"id": "LOCK_006", "reason": "缺少LOCK_TIMEOUT_HOURS配置"})

    # LOG_001: 单文件日志
    if "_CURRENT_LOG_FILE" in all_code:
        passed.append("LOG_001")
    else:
        failed.append({"id": "LOG_001", "reason": "未使用单文件日志机制（_CURRENT_LOG_FILE）"})

    # LOG_003: 条数
    if re.search(r'成功\s*-\s*\d+\s*条', all_code) or "count" in all_code.lower():
        passed.append("LOG_003")
    else:
        failed.append({"id": "LOG_003", "reason": "日志中未体现处理条数"})

    # LOG_004: 汇总
    if "汇总" in all_code and "合计" in all_code:
        passed.append("LOG_004")
    else:
        failed.append({"id": "LOG_004", "reason": "缺少运行结束条数汇总"})

    # LOG_005: 保留10个
    if "clean_old_logs" in all_code or ("10" in all_code and "logs" in all_code.lower()):
        passed.append("LOG_005")
    else:
        failed.append({"id": "LOG_005", "reason": "缺少日志保留策略（最多10个）"})

    # PROG_001: \r进度
    if "\\r" in all_code or "\r" in all_code:
        passed.append("PROG_001")
    else:
        failed.append({"id": "PROG_001", "reason": "未使用\\r动态刷新进度"})

    # PROG_004: 禁止tqdm
    if "tqdm" not in all_code:
        passed.append("PROG_004")
    else:
        failed.append({"id": "PROG_004", "reason": "使用了tqdm第三方进度库，禁止使用"})

    # ERR_002: 失败通知
    if "notify_groups" in all_code:
        passed.append("ERR_002")
    else:
        failed.append({"id": "ERR_002", "reason": "失败后未调用notify_groups通知"})

    # FEISHU_001: 飞书凭证
    if "cli_a729a2469afed00c" in all_code or "APP_ID" in all_code:
        passed.append("FEISHU_001")
    else:
        failed.append({"id": "FEISHU_001", "reason": "通知.py缺少飞书APP_ID/APP_SECRET凭证"})

    # FEISHU_002: 群名
    if "万威" in all_code and "黄俊文" in all_code:
        passed.append("FEISHU_002")
    else:
        failed.append({"id": "FEISHU_002", "reason": "失败通知群名缺少关键词（万威/黄俊文/肖晓雯）"})

    # FEISHU_003: reply_message
    if "reply_message" in all_code and "om_x100b553b7f9284b4c3f790e4b13825a" in all_code:
        passed.append("FEISHU_003")
    else:
        failed.append({"id": "FEISHU_003", "reason": "成功通知未使用reply_message回复指定message_id"})

    # FEISHU_004: msg_type
    if 'msg_type' in all_code and '"text"' in all_code:
        passed.append("FEISHU_004")
    else:
        failed.append({"id": "FEISHU_004", "reason": "reply_message缺少msg_type: text字段"})

    # FEISHU_005: 返回dict
    if "def notify_groups" in all_code and "def reply_message" in all_code:
        passed.append("FEISHU_005")
    else:
        failed.append({"id": "FEISHU_005", "reason": "通知函数缺少规范的返回值"})

    # RECORD_001: 运行记录凭证
    if "FZgjbdV1Qa4rl3sr4GTcmbl4nhf" in all_code or "APP_TOKEN" in all_code:
        passed.append("RECORD_001")
    else:
        failed.append({"id": "RECORD_001", "reason": "运行记录.py缺少APP_TOKEN/TABLE_ID凭证"})

    # RECORD_002: report_run_record
    if "report_run_record" in all_code:
        passed.append("RECORD_002")
    else:
        failed.append({"id": "RECORD_002", "reason": "未调用report_run_record写入运行记录"})

    # RECORD_004: 动态应用名
    if "os.path.basename" in all_code and "ROOT_DIR" in all_code:
        passed.append("RECORD_004")
    else:
        failed.append({"id": "RECORD_004", "reason": "应用名称未动态取os.path.basename(ROOT_DIR)"})

    # RECORD_005: code校验
    if "code" in all_code and "!= 0" in all_code:
        passed.append("RECORD_005")
    else:
        failed.append({"id": "RECORD_005", "reason": "未校验飞书API返回的code字段"})

    # TOKEN_001: Token缓存
    if "_token_cache" in all_code and "expires_at" in all_code:
        passed.append("TOKEN_001")
    else:
        failed.append({"id": "TOKEN_001", "reason": "缺少Token缓存自动刷新机制"})

    # TOKEN_002: timeout
    timeouts = re.findall(r'timeout\s*=', all_code)
    if len(timeouts) >= 2:
        passed.append("TOKEN_002")
    else:
        failed.append({"id": "TOKEN_002", "reason": "HTTP请求缺少显式timeout参数"})

    # TOKEN_003: 重试
    if "retry" in all_code.lower() or "重试" in all_code or "for i in range(3)" in all_code:
        passed.append("TOKEN_003")
    else:
        failed.append({"id": "TOKEN_003", "reason": "外部API调用缺少重试逻辑"})

    # BAT_001: UTF-8 BOM
    bat_path = os.path.join(project_dir, "run.bat")
    if os.path.exists(bat_path):
        with open(bat_path, 'rb') as f:
            head = f.read(3)
        if head == b'\xef\xbb\xbf':
            passed.append("BAT_001")
        else:
            failed.append({"id": "BAT_001", "reason": "run.bat不是UTF-8 with BOM编码"})

        # BAT_002: CRLF
        with open(bat_path, 'rb') as f:
            content = f.read()
        if b'\r\n' in content or b'\r' in content:
            passed.append("BAT_002")
        else:
            failed.append({"id": "BAT_002", "reason": "run.bat未使用CRLF换行符"})

        # BAT_006: 首行空行
        text = content.decode('utf-8-sig', errors='ignore')
        lines = text.split('\n')
        if lines[0].strip() == '' and '@echo off' in lines[1] if len(lines) > 1 else False:
            passed.append("BAT_006")
        else:
            failed.append({"id": "BAT_006", "reason": "run.bat首行未留空行避让BOM"})
    else:
        for bid in ["BAT_001", "BAT_002", "BAT_006"]:
            failed.append({"id": bid, "reason": "run.bat不存在"})

    # BAT_003: 独立Python路径
    bat_content = ""
    if os.path.exists(bat_path):
        with open(bat_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            bat_content = f.read()
    if "Python311" in bat_content or "Python.Python.3.11" in bat_content:
        passed.append("BAT_003")
    else:
        failed.append({"id": "BAT_003", "reason": "run.bat未固定引用独立Python绝对路径"})

    # BAT_004: PYTHONDONTWRITEBYTECODE
    if "PYTHONDONTWRITEBYTECODE" in bat_content:
        passed.append("BAT_004")
    else:
        failed.append({"id": "BAT_004", "reason": "run.bat未设置PYTHONDONTWRITEBYTECODE=1"})

    # BAT_005: sys.dont_write_bytecode
    if "dont_write_bytecode" in all_code:
        passed.append("BAT_005")
    else:
        failed.append({"id": "BAT_005", "reason": "主流程.py头部缺少sys.dont_write_bytecode = True"})

    # TOOL_001: 禁止input()
    if "input(" not in all_code and "raw_input(" not in all_code:
        passed.append("TOOL_001")
    else:
        failed.append({"id": "TOOL_001", "reason": "使用了input()/raw_input()阻塞式交互，禁止使用"})

    # PATH_001: 桌面路径
    if "expanduser" in all_code and "Desktop" in all_code:
        passed.append("PATH_001")
    else:
        failed.append({"id": "PATH_001", "reason": "未使用os.path.expanduser识别桌面路径"})

    return {
        "all_passed": len(failed) == 0,
        "passed_items": passed,
        "failed_items": failed,
        "total_count": len(auto_items),
        "passed_count": len(passed),
        "failed_count": len(failed)
    }


def build_ai_validation_prompt(project_dir: str, auto_result: ValidationResult) -> str:
    """构建AI校验提示词，让AI对自动化无法覆盖的条目进行判断"""
    files = os.listdir(project_dir) if os.path.exists(project_dir) else []
    code_summary = []
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(project_dir, f)
            try:
                with open(fpath, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                code_summary.append(f"=== {f} ===\n{content[:3000]}")
            except:
                pass

    prompt = f"""你是代码规范校验专家。请根据以下校验清单，检查生成的代码是否符合规范。

## 自动化检查结果
已通过 {auto_result['passed_count']} 项，未通过 {auto_result['failed_count']} 项。
未通过项：
{chr(10).join([f"- {item['id']}: {item['reason']}" for item in auto_result['failed_items']])}

## 需要你判断的条目（自动化无法覆盖）
请重点检查以下方面：
1. 函数体内每一行是否都有中文注释（尤其循环与API请求）
2. 每个函数定义后是否有中文docstring
3. 子流程间是否使用import函数调用（禁止subprocess）
4. 主流程是否按A→B→C顺序调用
5. 是否先acquire_lock()再init_dirs()
6. 多表/多数据源是否分别打印数量（禁止只打印汇总）
7. 进度行是否仅输出终端、未写入日志
8. 任一子流程失败是否立即停止主流程
9. 通知模板格式是否正确（成功：{文件夹名}-{时间}:完成）
10. 运行记录写入前是否查询今日记录做覆盖去重
11. 批量写入3次失败是否跳过该批不中断流程
12. 慢接口是否禁止重复重试
13. 定时任务Action是否为独立Python+带引号路径+WorkingDirectory留空
14. 触发器是否为DailyTrigger+Repetition每小时重复

## 生成的代码
{chr(10).join(code_summary)}

## 输出格式
请严格按以下JSON格式输出，不要其他内容：
{{
  "passed": ["ID1", "ID2", ...],
  "failed": [
    {{"id": "ID", "reason": "具体原因"}}
  ],
  "summary": "整体评价"
}}
"""
    return prompt


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = auto_validate(sys.argv[1])
        print(f"自动化校验：通过 {result['passed_count']}/{result['total_count']}")
        if result['failed_items']:
            print("未通过：")
            for item in result['failed_items']:
                print(f"  {item['id']}: {item['reason']}")
    else:
        print("用法: python code_validator.py <项目目录>")
