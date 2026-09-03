# -*- coding: utf-8 -*-
"""
校验器模块（validator.py）
替代原 checklist.py + code_validator.py，面向"任意智能体按技能规范执行"的工作流约定：

- 校验清单以技能文档 MD 的「校验清单」章节为唯一权威来源，运行时动态解析，不硬编码清单条目
- 提供四个核心能力，经 mcp_server.py 暴露为远程 MCP 工具：
    list_skills      列出所有可用技能
    get_skill_spec   获取技能规范全文 + 校验清单章节
    plan_requirement 按技能规范生成执行计划骨架（规则引擎，不依赖 LLM）
    check_result     按技能校验清单对执行结果做整合校验（自动化检查 + 返回清单供 AI 逐项核对）
"""
import os
import re
import json
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
SKILLS_CONFIG_PATH = os.path.join(BASE_DIR, "skills.json")

CHECKLIST_SECTION = "校验清单"


# ========== 技能配置 ==========

def load_skills_config() -> Dict[str, Any]:
    """加载技能注册表 skills.json"""
    with open(SKILLS_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def list_skills() -> List[Dict[str, Any]]:
    """列出所有技能（id/name/file/description/check_section）"""
    return load_skills_config()["skills"]


def get_skill_by_id(skill_id: str) -> Optional[Dict[str, Any]]:
    """按 ID 获取技能配置"""
    for s in list_skills():
        if s["id"] == skill_id:
            return s
    return None


def read_skill_md(skill: Dict[str, Any]) -> str:
    """读取技能规范 MD 全文（SKILL.md，自动剥离 YAML frontmatter 返回正文）"""
    fpath = os.path.join(SKILLS_DIR, skill["file"])
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    # agentskills.io 标准：skills/<skill-name>/SKILL.md，以 --- 开头为 YAML frontmatter，剥离后为正文
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip("\n")
    return content


def detect_skill(requirement: str) -> str:
    """根据需求关键词自动识别技能ID（匹配不到默认 python-app-standard）"""
    req = requirement.lower()
    yoonup_keywords = ["工作流", "yoonup", "技能同步", "更新技能", "推送技能", "仓库同步",
                       "技能仓库", "校验清单", "技能规范", "同步到github", "推到github",
                       "更新skill", "技能上传", "企业技能"]
    if any(kw in req for kw in yoonup_keywords):
        return "yoonup-workflow"
    web_keywords = ["网页", "js逆向", "js 逆向", "接口直连", "cdp", "浏览器", "后台数据",
                    "token", "逆向", "网页后台", "抓包", "加密参数", "签名"]
    if any(kw in req for kw in web_keywords):
        return "web-js-app-implementation"
    return "python-app-standard"


# ========== 校验清单解析（从 MD「校验清单」章节动态读取） ==========

def parse_checklist(md_text: str) -> Dict[str, List[Dict[str, str]]]:
    """
    解析 MD 中的「校验清单」章节，返回 {类别: [条目...]}。
    条目行格式：- [ID] 检查方式 描述（检查方式：auto=自动化检查 / ai=AI判断 / both=两者结合）
    """
    result: Dict[str, List[Dict[str, str]]] = {}
    current_cat: Optional[str] = None
    in_section = False
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_section:
                break  # 遇到下一个二级标题，校验清单章节结束
            if stripped[3:].strip() == CHECKLIST_SECTION:
                in_section = True
            continue
        if not in_section:
            continue
        if stripped.startswith("### "):
            current_cat = stripped[4:].strip()
            result.setdefault(current_cat, [])
            continue
        m = re.match(r"^- \[([A-Z0-9_]+)\]\s*(\w+)\s*(.*)$", stripped)
        if m and current_cat is not None:
            result[current_cat].append({
                "id": m.group(1),
                "method": m.group(2),
                "description": m.group(3).strip(),
            })
    return result


def get_skill_checklist(skill_id: str) -> Dict[str, Any]:
    """获取技能规范全文与解析后的校验清单"""
    skill = get_skill_by_id(skill_id)
    if not skill:
        raise ValueError(f"技能ID不存在: {skill_id}，可用技能: {[s['id'] for s in list_skills()]}")
    md_text = read_skill_md(skill)
    checklist = parse_checklist(md_text)
    return {"skill": skill, "md_text": md_text, "checklist": checklist}


def flatten_checklist(checklist: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
    """将 {类别: [条目]} 展平为条目列表（带类别字段）"""
    items: List[Dict[str, str]] = []
    for cat, cat_items in checklist.items():
        for item in cat_items:
            items.append({**item, "category": cat})
    return items


def format_checklist_text(skill_id: str) -> str:
    """将校验清单格式化为 AI 可逐项核对的文本"""
    data = get_skill_checklist(skill_id)
    lines = [f"# {data['skill']['name']} - 校验清单（执行完成后逐项核对）\n"]
    for cat, items in data["checklist"].items():
        lines.append(f"\n## {cat}\n")
        for item in items:
            tag = {"auto": "[自动]", "ai": "[AI判断]", "both": "[自动+AI]"}.get(item["method"], "")
            lines.append(f"- {item['id']} {tag} {item['description']}")
    return "\n".join(lines)


# ========== 自动化检查器（按类别注册，只处理 MD 中声明为 auto/both 的条目） ==========

def _read_project(project_dir: str) -> Dict[str, Any]:
    """读取项目目录：文件列表、py 代码全文、run.bat 内容"""
    files = os.listdir(project_dir) if os.path.exists(project_dir) else []
    file_contents: Dict[str, str] = {}
    for f in files:
        fpath = os.path.join(project_dir, f)
        if os.path.isfile(fpath) and f.endswith(".py"):
            try:
                with open(fpath, "r", encoding="utf-8") as fp:
                    file_contents[f] = fp.read()
            except Exception:
                pass
    all_code = "\n".join(file_contents.values())
    bat_content = ""
    bat_path = os.path.join(project_dir, "run.bat")
    if os.path.exists(bat_path):
        try:
            with open(bat_path, "r", encoding="utf-8-sig", errors="ignore") as fp:
                bat_content = fp.read()
        except Exception:
            pass
    return {"files": files, "file_contents": file_contents, "all_code": all_code,
            "bat_content": bat_content, "project_dir": project_dir}


def _make_checker(check_map: Dict[str, Any]):
    """构造通用检查器：check_map = {ID: 函数(ctx)->(通过:bool, 失败原因:str)}"""
    def checker(ctx: Dict[str, Any], auto_ids: set) -> tuple:
        passed, failed = [], []
        for cid, fn in check_map.items():
            if cid not in auto_ids:
                continue
            try:
                ok, reason = fn(ctx)
            except Exception as e:
                ok, reason = False, f"检查异常: {e}"
            if ok:
                passed.append(cid)
            else:
                failed.append({"id": cid, "reason": reason})
        return passed, failed
    return checker


def _has(ctx: Dict[str, Any], *needles: str) -> bool:
    """all_code 中同时包含所有关键词"""
    code = ctx["all_code"]
    return all(n in code for n in needles)


def _bat_has(ctx: Dict[str, Any], *needles: str) -> bool:
    return all(n in ctx["bat_content"] for n in needles)


CHECKERS: Dict[str, Any] = {}


# ---- 目录结构 ----
def _check_dir_structure(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    files = ctx["files"]
    passed, failed = [], []
    checks = {
        "DIR_001": ("主流程.py", "缺少主流程.py入口文件"),
        "DIR_003": ("通知.py", "缺少通知.py飞书通知模块"),
        "DIR_004": ("运行记录.py", "缺少运行记录.py模块"),
        "DIR_007": ("run.bat", "缺少run.bat手动运行脚本"),
    }
    for cid, (fname, reason) in checks.items():
        if cid not in auto_ids:
            continue
        if fname in files:
            passed.append(cid)
        else:
            failed.append({"id": cid, "reason": reason})
    if "DIR_002" in auto_ids:
        sub_flows = [f for f in files if re.match(r"^流程[A-Z]_.+\.py$", f)]
        if sub_flows:
            passed.append("DIR_002")
        else:
            failed.append({"id": "DIR_002", "reason": "未找到符合命名规范的子流程文件（流程{字母}_{数据源-用途}.py）"})
    if "DIR_005" in auto_ids:
        if os.path.isdir(os.path.join(ctx["project_dir"], "临时")):
            passed.append("DIR_005")
        else:
            failed.append({"id": "DIR_005", "reason": "缺少临时/目录"})
    if "DIR_006" in auto_ids:
        if os.path.isdir(os.path.join(ctx["project_dir"], "logs")):
            passed.append("DIR_006")
        else:
            failed.append({"id": "DIR_006", "reason": "缺少logs/目录"})
    return passed, failed


CHECKERS["目录结构"] = _check_dir_structure


# ---- 命名规范（自动部分：类型注解） ----
def _check_naming(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    if "NAME_002" in auto_ids:
        typed_vars = re.findall(r"[\u4e00-\u9fa5]+\s*:\s*\w+", all_code)
        if typed_vars:
            passed.append("NAME_002")
        else:
            failed.append({"id": "NAME_002", "reason": "未发现带类型注解的中文变量声明（变量名: 类型 = 初始值）"})
    if "NAME_001" in auto_ids:
        english_vars = re.findall(r"\b([a-z_][a-z0-9_]{2,})\s*[:=]", all_code)
        common_en = {'import', 'from', 'def', 'return', 'if', 'else', 'for', 'while', 'try', 'except',
                     'print', 'open', 'with', 'as', 'in', 'not', 'and', 'or', 'true', 'false', 'none',
                     'self', 'cls', 'str', 'int', 'float', 'list', 'dict', 'bool', 'set', 'tuple',
                     'os', 'sys', 're', 'json', 'time', 'datetime', 'requests', 'subprocess', 'argparse',
                     'app', 'root', 'dir', 'file', 'path', 'tmp', 'log', 'lock', 'token', 'url', 'api',
                     'data', 'code', 'msg', 'res', 'req', 'headers', 'params', 'payload', 'response',
                     'run', 'main', 'input', 'range', 'len', 'join', 'split', 'append', 'items', 'keys',
                     'values', 'get', 'post', 'put', 'delete', 'read', 'write', 'close', 'encode', 'decode'}
        suspicious = [v for v in set(english_vars) if v.lower() not in common_en and len(v) > 2]
        if len(suspicious) <= 5:
            passed.append("NAME_001")
        else:
            failed.append({"id": "NAME_001", "reason": f"发现可能的英文变量名: {', '.join(sorted(suspicious)[:10])}"})
    return passed, failed


CHECKERS["命名规范"] = _check_naming


# ---- 调用规则 ----
def _check_call(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    if "CALL_001" in auto_ids:
        run_pattern = r"def\s+run\s*\(\s*tmp_dir\s*:\s*str\s*,\s*prev_file\s*:\s*str\s*=\s*None\s*\)\s*->\s*dict"
        if re.search(run_pattern, all_code):
            passed.append("CALL_001")
        else:
            failed.append({"id": "CALL_001", "reason": "子流程未找到符合规范的 run(tmp_dir: str, prev_file: str = None) -> dict 函数"})
    if "CALL_002" in auto_ids:
        if "--limit" in all_code and "argparse" in all_code:
            passed.append("CALL_002")
        else:
            failed.append({"id": "CALL_002", "reason": "主流程缺少 --limit 参数或未使用 argparse"})
    return passed, failed


CHECKERS["调用规则"] = _check_call


# ---- 文件锁 ----
def _check_lock(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    checks = {
        "LOCK_001": (lambda: _has(ctx, ".running.lock", "acquire_lock"), "缺少 .running.lock 文件锁机制"),
        "LOCK_002": (lambda: _has(ctx, "ROOT_DIR", ".running.lock"), "锁文件路径可能不在项目根目录"),
        "LOCK_003": (lambda: _has(ctx, "os.getpid()", "tasklist"), "未使用 PID 存活检测锁机制"),
        "LOCK_005": (lambda: "LOCK_HELD" in all_code, "缺少 LOCK_HELD 持有标志"),
        "LOCK_006": (lambda: "LOCK_TIMEOUT_HOURS" in all_code, "缺少 LOCK_TIMEOUT_HOURS 配置"),
    }
    for cid, (fn, reason) in checks.items():
        if cid not in auto_ids:
            continue
        if fn():
            passed.append(cid)
        else:
            failed.append({"id": cid, "reason": reason})
    return passed, failed


CHECKERS["文件锁"] = _check_lock


# ---- 日志规则 ----
def _check_log(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    checks = {
        "LOG_001": (lambda: "_CURRENT_LOG_FILE" in all_code, "未使用单文件日志机制（_CURRENT_LOG_FILE）"),
        "LOG_003": (lambda: bool(re.search(r"成功\s*-\s*\d+\s*条", all_code)) or "count" in all_code.lower(),
                    "日志中未体现处理条数（成功 - N 条）"),
        "LOG_004": (lambda: "汇总" in all_code and "合计" in all_code, "缺少运行结束条数汇总（本次运行汇总/合计）"),
        "LOG_005": (lambda: "clean_old_logs" in all_code, "缺少日志保留策略（最多保留10个，clean_old_logs）"),
    }
    for cid, (fn, reason) in checks.items():
        if cid not in auto_ids:
            continue
        if fn():
            passed.append(cid)
        else:
            failed.append({"id": cid, "reason": reason})
    return passed, failed


CHECKERS["日志规则"] = _check_log


# ---- 终端进度 ----
def _check_progress(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    if "PROG_001" in auto_ids:
        if "\\r" in all_code or "\r" in all_code:
            passed.append("PROG_001")
        else:
            failed.append({"id": "PROG_001", "reason": "未使用 \\r 动态刷新进度"})
    if "PROG_004" in auto_ids:
        if "tqdm" not in all_code:
            passed.append("PROG_004")
        else:
            failed.append({"id": "PROG_004", "reason": "使用了 tqdm 第三方进度库，禁止使用"})
    return passed, failed


CHECKERS["终端进度"] = _check_progress


# ---- 错误处理 ----
def _check_error(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    if "ERR_002" in auto_ids:
        if "notify_groups" in ctx["all_code"]:
            passed.append("ERR_002")
        else:
            failed.append({"id": "ERR_002", "reason": "失败后未调用 notify_groups 通知到群"})
    return passed, failed


CHECKERS["错误处理"] = _check_error


# ---- 飞书通知 ----
def _check_feishu(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    checks = {
        "FEISHU_001": (lambda: "APP_ID" in all_code and "APP_SECRET" in all_code, "通知.py 缺少飞书 APP_ID/APP_SECRET 凭证"),
        "FEISHU_002": (lambda: "万威" in all_code and "黄俊文" in all_code, "失败通知群名缺少关键词（万威/黄俊文/肖晓雯）"),
        "FEISHU_003": (lambda: "reply_message" in all_code and "om_x100b553b7f9284b4c3f790e4b13825a" in all_code,
                       "成功通知未使用 reply_message 回复指定 message_id"),
        "FEISHU_004": (lambda: "msg_type" in all_code and '"text"' in all_code, "reply_message 缺少 msg_type: text 字段"),
        "FEISHU_005": (lambda: "def notify_groups" in all_code and "def reply_message" in all_code,
                       "通知函数缺少规范接口（notify_groups/reply_message）或未返回 dict"),
    }
    for cid, (fn, reason) in checks.items():
        if cid not in auto_ids:
            continue
        if fn():
            passed.append(cid)
        else:
            failed.append({"id": cid, "reason": reason})
    return passed, failed


CHECKERS["飞书通知"] = _check_feishu


# ---- 运行记录 ----
def _check_record(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    checks = {
        "RECORD_001": (lambda: "APP_TOKEN" in all_code and "TABLE_ID" in all_code, "运行记录.py 缺少 APP_TOKEN/TABLE_ID 凭证"),
        "RECORD_002": (lambda: "report_run_record" in all_code, "未调用 report_run_record 写入运行记录"),
        "RECORD_004": (lambda: "os.path.basename" in all_code and "ROOT_DIR" in all_code,
                       "应用名称未动态取 os.path.basename(ROOT_DIR)"),
        "RECORD_005": (lambda: "code" in all_code and "!= 0" in all_code, "未校验飞书 API 返回的 code 字段"),
    }
    for cid, (fn, reason) in checks.items():
        if cid not in auto_ids:
            continue
        if fn():
            passed.append(cid)
        else:
            failed.append({"id": cid, "reason": reason})
    return passed, failed


CHECKERS["运行记录"] = _check_record


# ---- Token 与重试 ----
def _check_token(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    if "TOKEN_001" in auto_ids:
        if "_token_cache" in all_code and "expires_at" in all_code:
            passed.append("TOKEN_001")
        else:
            failed.append({"id": "TOKEN_001", "reason": "缺少 Token 缓存自动刷新机制（_token_cache/expires_at）"})
    if "TOKEN_002" in auto_ids:
        timeouts = re.findall(r"timeout\s*=", all_code)
        if len(timeouts) >= 2:
            passed.append("TOKEN_002")
        else:
            failed.append({"id": "TOKEN_002", "reason": "HTTP 请求缺少显式 timeout 参数"})
    if "TOKEN_003" in auto_ids:
        if "retry" in all_code.lower() or "重试" in all_code or "for i in range(3)" in all_code:
            passed.append("TOKEN_003")
        else:
            failed.append({"id": "TOKEN_003", "reason": "外部 API 调用缺少重试逻辑"})
    return passed, failed


CHECKERS["Token与重试"] = _check_token


# ---- run.bat ----
def _check_bat(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    bat_path = os.path.join(ctx["project_dir"], "run.bat")
    bat_exists = os.path.exists(bat_path)

    def _bom_ok():
        if not bat_exists:
            return False
        with open(bat_path, "rb") as f:
            return f.read(3) == b"\xef\xbb\xbf"

    def _crlf_ok():
        if not bat_exists:
            return False
        with open(bat_path, "rb") as f:
            content = f.read()
        return b"\r\n" in content or b"\r" in content

    def _first_line_ok():
        if not bat_exists:
            return False
        with open(bat_path, "rb") as f:
            text = f.read().decode("utf-8-sig", errors="ignore")
        lines = text.split("\n")
        return len(lines) > 1 and lines[0].strip() == "" and "@echo off" in lines[1]

    checks = {
        "BAT_001": (_bom_ok, "run.bat 不是 UTF-8 with BOM 编码"),
        "BAT_002": (_crlf_ok, "run.bat 未使用 CRLF 换行符"),
        "BAT_003": (lambda: "Python311" in ctx["bat_content"] or "Python.Python.3.11" in ctx["bat_content"],
                    "run.bat 未固定引用独立 Python 绝对路径（Python311）"),
        "BAT_004": (lambda: "PYTHONDONTWRITEBYTECODE" in ctx["bat_content"],
                    "run.bat 未设置 PYTHONDONTWRITEBYTECODE=1"),
        "BAT_006": (_first_line_ok, "run.bat 首行未留空行避让 BOM"),
    }
    for cid, (fn, reason) in checks.items():
        if cid not in auto_ids:
            continue
        if fn():
            passed.append(cid)
        else:
            failed.append({"id": cid, "reason": reason})
    if "BAT_005" in auto_ids:
        if "dont_write_bytecode" in ctx["all_code"]:
            passed.append("BAT_005")
        else:
            failed.append({"id": "BAT_005", "reason": "主流程.py 头部缺少 sys.dont_write_bytecode = True"})
    return passed, failed


CHECKERS["run.bat规范"] = _check_bat


# ---- 工具脚本 ----
def _check_tool(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    if "TOOL_001" in auto_ids:
        if "input(" not in all_code and "raw_input(" not in all_code:
            passed.append("TOOL_001")
        else:
            failed.append({"id": "TOOL_001", "reason": "使用了 input()/raw_input() 阻塞式交互，禁止使用"})
    if "TOOL_002" in auto_ids:
        if ("argparse" in all_code or "environ" in all_code) and "sys.exit" in all_code:
            passed.append("TOOL_002")
        else:
            failed.append({"id": "TOOL_002", "reason": "工具脚本未通过 argparse/环境变量传参或未用 sys.exit(0/1) 返回状态"})
    return passed, failed


CHECKERS["工具脚本规范"] = _check_tool


# ---- 路径规范 ----
def _check_path(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    if "PATH_001" in auto_ids:
        if "expanduser" in ctx["all_code"] and "Desktop" in ctx["all_code"]:
            passed.append("PATH_001")
        else:
            failed.append({"id": "PATH_001", "reason": "未使用 os.path.expanduser 识别桌面路径"})
    return passed, failed


CHECKERS["路径规范"] = _check_path


# ---- 网页JS逆向（web-js-app-implementation）----
def _check_web(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    all_code = ctx["all_code"]
    checks = {
        "WEB_003": (lambda: ("list" in all_code.lower() or "二维" in all_code), "输出 result 未体现二维列表/字典结构"),
        "WEB_004": (lambda: "开始时间" in all_code and "结束时间" in all_code, "未提供 开始时间+结束时间 两个日期变量（YYYY-MM-DD）"),
        "WEB_005": (lambda: "配置区" in all_code or "顶部配置" in all_code, "脚本顶部未设可配置变量区"),
        "WEB_007": (lambda: "App Paths" in all_code or "chrome.exe" in all_code, "Chrome 路径未做自动探测（注册表/常见路径）"),
        "WEB_008": (lambda: "request" in all_code, "脚本未输出请求结构（request 字段）"),
        "WEB_011": (lambda: "pip" in all_code.lower() or "install" in all_code.lower(), "未实现依赖自动安装"),
        "WEB_012": (lambda: "page" in all_code.lower() or "cursor" in all_code.lower() or "分页" in all_code,
                    "未实现分页拉取全量逻辑"),
        "WEB_013": (lambda: "999998" in all_code or "清缓存" in all_code or "token" in all_code.lower(),
                    "未实现业务失败码→token失效重取逻辑"),
        "WEB_014": (lambda: "清洗" in all_code or "strip" in all_code or "html" in all_code.lower(),
                    "未实现数据清洗逻辑"),
    }
    for cid, (fn, reason) in checks.items():
        if cid not in auto_ids:
            continue
        if fn():
            passed.append(cid)
        else:
            failed.append({"id": cid, "reason": reason})
    return passed, failed


CHECKERS["网页JS逆向"] = _check_web


# ---- 仓库同步（yoonup-workflow）----
def _check_repo_sync(ctx: Dict[str, Any], auto_ids: set) -> tuple:
    passed, failed = [], []
    project_dir = ctx["project_dir"]

    def _git_remote_ok() -> bool:
        try:
            import subprocess
            r = subprocess.run(["git", "-C", project_dir, "remote", "-v"],
                               capture_output=True, text=True, timeout=5)
            return "Yoonwe/Yoonup" in r.stdout
        except Exception:
            return False

    def _skills_json_registered() -> bool:
        skills_path = os.path.join(project_dir, "skills.json")
        if not os.path.exists(skills_path):
            return False
        try:
            with open(skills_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ids = {s["id"] for s in data.get("skills", [])}
            return "yoonup-workflow" in ids
        except Exception:
            return False

    def _no_unpushed() -> bool:
        try:
            import subprocess
            r = subprocess.run(["git", "-C", project_dir, "status", "-sb"],
                               capture_output=True, text=True, timeout=5)
            return "ahead" not in r.stdout
        except Exception:
            return False

    checks = {
        "YW09": (lambda: _git_remote_ok() and _skills_json_registered(),
                 "技能未正确同步：git remote 不是 Yoonwe/Yoonup 或 skills.json 未注册 yoonup-workflow"),
    }
    for cid, (fn, reason) in checks.items():
        if cid not in auto_ids:
            continue
        if fn():
            passed.append(cid)
        else:
            failed.append({"id": cid, "reason": reason})
    return passed, failed


CHECKERS["仓库同步"] = _check_repo_sync


# ========== 整合校验入口 ==========

def check_result(project_dir: str, skill_id: Optional[str] = None,
                 include_details: bool = True) -> Dict[str, Any]:
    """
    对执行结果（项目目录）做末端整合校验：
    1. 读取技能 MD 的「校验清单」章节
    2. auto/both 条目：能自动检查的走 CHECKERS，其余并入 AI 清单
    3. 返回自动检查结果 + 需要 AI 逐项核对的清单文本
    """
    if not os.path.exists(project_dir):
        return {"error": f"项目目录不存在: {project_dir}"}

    skill_ids = [skill_id] if skill_id else [s["id"] for s in list_skills()]
    ctx = _read_project(project_dir)

    all_passed_ids: List[str] = []
    all_failed: List[Dict[str, str]] = []
    ai_checklist_lines: List[str] = []

    for sid in skill_ids:
        data = get_skill_checklist(sid)
        checklist = data["checklist"]
        items = flatten_checklist(checklist)
        auto_ids = {it["id"] for it in items if it["method"] in ("auto", "both")}

        for cat, cat_items in checklist.items():
            checker = CHECKERS.get(cat)
            cat_auto_ids = {it["id"] for it in cat_items if it["method"] in ("auto", "both")}
            if checker and cat_auto_ids:
                p, f = checker(ctx, cat_auto_ids)
                all_passed_ids.extend(p)
                all_failed.extend(f)
            # 未自动覆盖的 auto 条目 + 全部 ai 条目 → 交给调用方 AI 核对
            for item in cat_items:
                if item["id"] not in all_passed_ids and item["id"] not in {f["id"] for f in all_failed}:
                    ai_checklist_lines.append(
                        f"- [{item['id']}] [{item['method']}] {item['description']}")

    # 去重
    all_passed_ids = sorted(set(all_passed_ids))
    seen = set()
    unique_failed = []
    for f in all_failed:
        if f["id"] not in seen:
            seen.add(f["id"])
            unique_failed.append(f)

    result: Dict[str, Any] = {
        "skill_ids": skill_ids,
        "project_dir": project_dir,
        "auto_passed": all_passed_ids,
        "auto_failed": unique_failed,
        "auto_passed_count": len(all_passed_ids),
        "auto_failed_count": len(unique_failed),
        "all_auto_passed": len(unique_failed) == 0,
        "ai_checklist": "\n".join(ai_checklist_lines) if include_details else None,
        "summary": f"自动化检查通过 {len(all_passed_ids)} 项，未通过 {len(unique_failed)} 项，"
                   f"另有 {len(ai_checklist_lines)} 项需调用方 AI 逐项核对"
    }
    return result


# ========== 执行计划规划（规则引擎，不依赖 LLM） ==========

def plan_requirement(requirement: str, skill_id: Optional[str] = None) -> Dict[str, Any]:
    """
    按技能规范生成执行计划骨架。
    调用方 AI 拿到计划后，结合用户需求细化步骤、向用户提问确认执行顺序，再按序执行。
    """
    sid = skill_id or detect_skill(requirement)
    skill = get_skill_by_id(sid)
    if not skill:
        raise ValueError(f"技能ID不存在: {sid}")

    if sid == "yoonup-workflow":
        steps = [
            {"step": 1, "name": "识别子技能", "action": "判断需求所属子技能（python-app-standard / web-js-app-implementation），不确定时向用户确认"},
            {"step": 2, "name": "读取规范全文", "action": "读取对应 references 规范文件全文，含末尾校验清单章节，禁止跳过"},
            {"step": 3, "name": "需求拆分提问", "action": "结合需求细化步骤，向用户提问确认执行顺序，由用户拍板后开始，禁止自行跳过"},
            {"step": 4, "name": "按序执行", "action": "严格按子技能规范做事，每步开始/完成/失败实时反馈进度，发现新问题同步更新 references"},
            {"step": 5, "name": "末端校验", "action": "按子技能校验清单逐项核对，auto 未通过项修复，全部通过才交付，给出产物路径+验证结果"},
            {"step": 6, "name": "同步到 GitHub", "action": "若涉及技能变更，复制到仓库 skills/ 目录、更新 skills.json、commit & push 到 Yoonwe/Yoonup，禁止建新仓库"},
        ]
        questions = [
            "需求所属子技能：python-app-standard（流程自动化）还是 web-js-app-implementation（网页抓取）？",
            "是否涉及技能文件变更需要同步到 GitHub？",
            "若需同步，改动范围：仅 SKILL.md / references / 还是 skills.json 也要更新？",
        ]
    elif sid == "web-js-app-implementation":
        steps = [
            {"step": 1, "name": "逆向定位接口", "action": "打开目标页，Network 筛选 XHR/Fetch 定位数据接口；必要时从前端 chunk 提取接口路径与字段映射"},
            {"step": 2, "name": "还原请求", "action": "确认请求方法/URL/参数/必要请求头/分页参数/响应结构，本地直连验证与页面数据核对"},
            {"step": 3, "name": "获取token", "action": "影刀执行JS读页面存储 或 CDP 连接调试浏览器读取，禁止要求用户手动复制"},
            {"step": 4, "name": "编写脚本", "action": "三层模板：顶部配置区 + 通用模块 + 业务函数；顶部变量一行式精简备注"},
            {"step": 5, "name": "验证交付", "action": "运行脚本核对输出长度/列数/关键值，输出请求结构，交付即用"},
        ]
        questions = [
            "数据范围：哪些业务模块、每模块的筛选条件（时间区间/部门分组/关键词/分页）",
            "输出结构：二维列表（表头行+数据行）还是字典列表，是否带合计行",
            "合并约定：多模块数据合并方向（横向延长列 vs 纵向追加行）",
            "token 来源：影刀传参 / CDP 自动读取 / 缓存复用",
            "交付物：脚本路径、运行验证结果",
        ]
    else:  # python-app-standard
        steps = [
            {"step": 1, "name": "解析需求与拆分", "action": "读取技能规范，按业务逻辑和数据源/接口拆分子流程（流程A/B/C...），不反问规范已覆盖的细节"},
            {"step": 2, "name": "向用户确认执行顺序", "action": "展示拆分后的步骤清单与执行顺序，由用户拍板后开始执行"},
            {"step": 3, "name": "按顺序执行各步骤", "action": "每个子流程执行中实时反馈进度（分页/批量调用/写入均输出动态进度），完成一步进入下一步"},
            {"step": 4, "name": "末端整合校验", "action": "全部步骤执行完成后，按技能文档「校验清单」章节逐项核对；未通过项修复后重新校验，通过后交付"},
        ]
        questions = [
            "需求拆分后的执行顺序（由用户确定先跑哪个子流程）",
            "业务维度拆分（如物流区分京东/顺丰等，如需）",
        ]

    return {
        "skill_id": sid,
        "skill_name": skill["name"],
        "requirement": requirement,
        "plan_steps": steps,
        "questions_to_user": questions,
        "note": "以上为计划骨架，请结合具体需求细化；需求拆分时务必向用户提问确认执行顺序，禁止自行跳过提问。"
                "执行完成必须调用 check_result 做末端校验。"
    }


# ========== 技能规范读取 ==========

def get_skill_spec(skill_id: str, include_checklist: bool = True) -> Dict[str, Any]:
    """获取技能规范全文 + 校验清单章节"""
    data = get_skill_checklist(skill_id)
    result = {
        "skill_id": data["skill"]["id"],
        "skill_name": data["skill"]["name"],
        "description": data["skill"].get("description", ""),
        "spec": data["md_text"],
    }
    if include_checklist:
        result["checklist"] = data["checklist"]
        result["checklist_text"] = format_checklist_text(skill_id)
    return result


if __name__ == "__main__":
    import sys
    print("可用技能:")
    for s in list_skills():
        print(f"  - {s['id']}: {s['name']}")
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "check":
            target = sys.argv[2] if len(sys.argv) > 2 else "."
            sid = sys.argv[3] if len(sys.argv) > 3 else None
            print(json.dumps(check_result(target, sid), ensure_ascii=False, indent=2))
        elif arg == "plan":
            req = sys.argv[2] if len(sys.argv) > 2 else "示例需求"
            print(json.dumps(plan_requirement(req), ensure_ascii=False, indent=2))
        elif arg == "spec":
            sid = sys.argv[2] if len(sys.argv) > 2 else "python-app-standard"
            data = get_skill_spec(sid)
            print(f"技能: {data['skill_id']} - {data['skill_name']}")
            print(f"规范长度: {len(data['spec'])} 字符")
            print("校验清单类别:", list(data["checklist"].keys()))
