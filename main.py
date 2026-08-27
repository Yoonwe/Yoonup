"""
LangGraph 工作流主文件
流程：需求解析 → 代码生成 → 校验（自动化+AI） → 修复循环 → 通知
"""
import os
import sys
import json
import time
import shutil
import logging
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from checklist import format_checklist_for_ai, CHECKLIST, get_skill_by_id, list_skill_ids, get_checklist_by_skill
from code_validator import auto_validate, build_ai_validation_prompt, ValidationResult

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

# 工作目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# LLM配置（支持OpenAI兼容接口，如豆包）
LLM_MODEL = os.getenv("LLM_MODEL", "doubao-1-5-pro-32k")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))

# 飞书通知配置
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")


def get_llm() -> ChatOpenAI:
    """获取LLM实例"""
    return ChatOpenAI(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        temperature=0.3,
        timeout=120
    )


def read_skill_doc(skill_id: str = None) -> str:
    """读取技能规范文档，按skill_id精确匹配"""
    if skill_id:
        skill = get_skill_by_id(skill_id)
        if skill:
            fpath = os.path.join(SKILLS_DIR, skill["file"])
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as fp:
                    return fp.read()
        raise ValueError(f"技能ID不存在: {skill_id}，可用技能: {list_skill_ids()}")
    # 未指定skill_id时加载全部
    docs = []
    for f in os.listdir(SKILLS_DIR):
        if f.endswith('.md'):
            with open(os.path.join(SKILLS_DIR, f), 'r', encoding='utf-8') as fp:
                docs.append(fp.read())
    return "\n\n".join(docs)


def list_skills() -> list:
    """列出所有可用技能（ID和名称）"""
    from checklist import load_skills_config
    config = load_skills_config()
    return [f"{s['id']} - {s['name']}" for s in config["skills"]]


def detect_skill(requirement: str) -> str:
    """根据需求关键词自动识别技能ID，匹配不到返回空字符串"""
    req = requirement.lower()
    # web-extractor 关键词：网页抓取、JS逆向、浏览器、CDP、接口直连
    web_keywords = ["网页", "js逆向", "js 逆向", "接口直连", "cdp", "浏览器", "后台数据", "token", "逆向", "网页后台", "抓包", "加密参数", "签名"]
    if any(kw in req for kw in web_keywords):
        return "web-js-app"
    # 默认 python-app（流程、飞书、表格、订单、物流、通知、定时等）
    return "python-app"


# ===== 状态定义 =====
class WorkflowState(TypedDict):
    requirement: str                    # 用户需求
    skill_id: str                       # 使用的技能ID
    project_name: str                   # 项目名称（文件夹名）
    project_dir: str                    # 生成的项目目录
    generated_files: Dict[str, str]     # 生成的文件 {文件名: 内容}
    auto_validation: Optional[ValidationResult]  # 自动化校验结果
    ai_validation: Optional[Dict]       # AI校验结果
    final_validation: Optional[ValidationResult]  # 合并后的最终校验
    attempt: int                        # 当前尝试次数
    max_attempts: int                   # 最大尝试次数
    status: str                         # 状态：generating/validating/fixing/done/failed
    error: Optional[str]                # 错误信息
    notify_message: Optional[str]       # 通知消息


# ===== 节点函数 =====

def parse_requirement(state: WorkflowState) -> WorkflowState:
    """节点1：需求解析（不反问，自行拆分）"""
    logger.info(f"[需求解析] 处理需求: {state['requirement'][:50]}...")
    requirement = state['requirement']

    # 从需求中提取项目名称（取关键词，不反问）
    llm = get_llm()
    prompt = f"""根据以下业务需求，提取一个简洁的项目文件夹名称（中文，2-8个字，描述业务用途）。
只返回文件夹名称，不要其他内容。

需求：{requirement}
"""
    try:
        resp = llm.invoke([HumanMessage(content=prompt)])
        project_name = resp.content.strip().replace('"', '').replace("'", "")
    except Exception as e:
        project_name = f"流程项目_{int(time.time())}"
        logger.warning(f"[需求解析] LLM提取名称失败，使用默认: {e}")

    project_dir = os.path.join(OUTPUT_DIR, project_name)
    logger.info(f"[需求解析] 项目名称: {project_name}, 目录: {project_dir}")

    return {
        **state,
        "project_name": project_name,
        "project_dir": project_dir,
        "attempt": 0,
        "status": "generating"
    }


def generate_code(state: WorkflowState) -> WorkflowState:
    """节点2：代码生成（按MD规范生成完整流程代码）"""
    attempt = state.get("attempt", 0) + 1
    logger.info(f"[代码生成] 第 {attempt} 次生成")

    skill_id = state.get("skill_id", "")
    skill_doc = read_skill_doc(skill_id)
    checklist = format_checklist_for_ai(skill_id)
    requirement = state["requirement"]
    project_name = state["project_name"]

    # 如果是修复重试，带上次失败信息
    fix_hint = ""
    if state.get("final_validation") and state["final_validation"]["failed_items"]:
        failed = state["final_validation"]["failed_items"]
        fix_hint = f"\n\n## 上一次校验未通过的条目（必须修复）\n"
        for item in failed:
            fix_hint += f"- {item['id']}: {item['reason']}\n"

    prompt = f"""你是一名Python流程开发工程师。请根据以下规范和需求，生成一套完整的流程代码。

## 业务需求
{requirement}

## 项目名称
{project_name}

## 技能规范（必须严格遵守）
{skill_doc}

## 校验清单（生成时必须全部满足）
{checklist}
{fix_hint}

## 输出要求
请生成完整的项目文件，每个文件用 ===文件名=== 分隔，文件内容紧随其后。
必须包含：主流程.py、至少一个子流程（流程A_xxx.py）、通知.py、运行记录.py、run.bat
所有变量使用中文命名，带类型注解，每行有中文注释。
不要输出解释性文字，只输出文件内容。
"""

    try:
        llm = get_llm()
        resp = llm.invoke([HumanMessage(content=prompt)])
        content = resp.content

        # 解析生成的文件
        files = parse_generated_files(content)

        # 保存到项目目录
        project_dir = state["project_dir"]
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, "临时"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "logs"), exist_ok=True)

        for filename, file_content in files.items():
            fpath = os.path.join(project_dir, filename)
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            # run.bat特殊处理：UTF-8 BOM + CRLF
            if filename == "run.bat":
                with open(fpath, 'wb') as f:
                    f.write(b'\xef\xbb\xbf')
                    f.write(file_content.encode('utf-8').replace(b'\n', b'\r\n'))
            else:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(file_content)

        logger.info(f"[代码生成] 生成 {len(files)} 个文件: {list(files.keys())}")

        return {
            **state,
            "generated_files": files,
            "attempt": attempt,
            "status": "validating"
        }

    except Exception as e:
        logger.error(f"[代码生成] 失败: {e}")
        return {
            **state,
            "attempt": attempt,
            "status": "failed",
            "error": f"代码生成失败: {str(e)}"
        }


def parse_generated_files(content: str) -> Dict[str, str]:
    """解析LLM输出的文件内容"""
    files = {}
    # 匹配 ===文件名=== 或 ```文件名 格式
    import re
    # 格式1: ===文件名===
    pattern1 = r'===\s*(.+?)\s*===\s*\n(.*?)(?====|\Z)'
    matches = re.findall(pattern1, content, re.DOTALL)
    if matches:
        for filename, file_content in matches:
            filename = filename.strip()
            if filename:
                files[filename] = file_content.strip()

    # 格式2: ```python\n# filename.py ... ```
    if not files:
        pattern2 = r'```(?:python)?\s*\n(?:#\s*(.+?)\n)?(.*?)```'
        matches = re.findall(pattern2, content, re.DOTALL)
        for i, (filename, file_content) in enumerate(matches):
            if not filename:
                filename = f"文件_{i}.py"
            files[filename.strip()] = file_content.strip()

    # 如果都没解析到，把整个内容当一个文件
    if not files:
        files["主流程.py"] = content.strip()

    return files


def validate_code(state: WorkflowState) -> WorkflowState:
    """节点3：校验（自动化检查 + AI辅助检查）"""
    logger.info(f"[校验] 开始校验，第 {state['attempt']} 次尝试")
    project_dir = state["project_dir"]

    # 自动化校验
    auto_result = auto_validate(project_dir)
    logger.info(f"[校验] 自动化检查: 通过 {auto_result['passed_count']}/{auto_result['total_count']}")

    # AI辅助校验（只在自动化有未通过或需要判断语义时调用）
    ai_result = {"passed": [], "failed": [], "summary": ""}
    if not auto_result["all_passed"] or True:  # 始终调用AI做语义校验
        try:
            ai_prompt = build_ai_validation_prompt(project_dir, auto_result)
            llm = get_llm()
            resp = llm.invoke([HumanMessage(content=ai_prompt)])
            ai_content = resp.content.strip()
            # 提取JSON
            json_match = ai_content.find('{')
            if json_match >= 0:
                ai_result = json.loads(ai_content[json_match:])
        except Exception as e:
            logger.warning(f"[校验] AI校验失败: {e}")

    # 合并结果
    all_failed = list(auto_result["failed_items"])
    for item in ai_result.get("failed", []):
        # 避免重复
        if not any(f["id"] == item["id"] for f in all_failed):
            all_failed.append(item)

    all_passed_ids = set(auto_result["passed_items"])
    for pid in ai_result.get("passed", []):
        all_passed_ids.add(pid)

    skill_id = state.get("skill_id", "")
    skill_checklist = get_checklist_by_skill(skill_id) if skill_id else CHECKLIST
    total = len(skill_checklist)

    final_result: ValidationResult = {
        "all_passed": len(all_failed) == 0,
        "passed_items": list(all_passed_ids),
        "failed_items": all_failed,
        "total_count": total,
        "passed_count": len(all_passed_ids),
        "failed_count": len(all_failed)
    }

    logger.info(f"[校验] 最终结果: 通过 {final_result['passed_count']}/{final_result['total_count']}, "
                f"未通过 {final_result['failed_count']} 项")

    if final_result["failed_items"]:
        logger.info("[校验] 未通过条目:")
        for item in final_result["failed_items"][:10]:
            logger.info(f"  {item['id']}: {item['reason']}")

    return {
        **state,
        "auto_validation": auto_result,
        "ai_validation": ai_result,
        "final_validation": final_result,
        "status": "validating"
    }


def should_continue(state: WorkflowState) -> str:
    """条件判断：校验通过/修复/通知用户"""
    if state.get("status") == "failed":
        return "notify_user"

    validation = state.get("final_validation")
    if not validation:
        return "notify_user"

    if validation["all_passed"]:
        logger.info("[条件判断] 校验全部通过，完成")
        return "pass"

    if state["attempt"] >= state["max_attempts"]:
        logger.info(f"[条件判断] 已达最大尝试次数 {state['max_attempts']}，通知用户")
        return "notify_user"

    logger.info(f"[条件判断] 校验未通过，进入修复（第 {state['attempt']}/{state['max_attempts']} 次）")
    return "fix"


def notify_user(state: WorkflowState) -> WorkflowState:
    """节点：通知用户（飞书/打印）"""
    validation = state.get("final_validation")
    project_name = state["project_name"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if state.get("status") == "failed":
        message = f"{project_name}-{now}:生成失败 - {state.get('error', '未知错误')}"
        status = "failed"
    elif validation and validation["all_passed"]:
        message = f"{project_name}-{now}:完成，校验通过 {validation['passed_count']}/{validation['total_count']}"
        status = "success"
    else:
        failed_detail = "; ".join([f"{item['id']}" for item in validation["failed_items"][:5]]) if validation else ""
        message = f"{project_name}-{now}:校验未通过，尝试{state['attempt']}次，未通过项: {failed_detail}"
        status = "need_review"

    logger.info(f"[通知] {message}")

    # 飞书webhook通知
    if FEISHU_WEBHOOK:
        try:
            import requests
            requests.post(FEISHU_WEBHOOK, json={
                "msg_type": "text",
                "content": {"text": message}
            }, timeout=10)
        except Exception as e:
            logger.warning(f"[通知] 飞书推送失败: {e}")

    return {
        **state,
        "notify_message": message,
        "status": status
    }


# ===== 组装工作流 =====
def build_workflow() -> StateGraph:
    """构建并编译工作流"""
    graph = StateGraph(WorkflowState)

    graph.add_node("parse", parse_requirement)
    graph.add_node("generate", generate_code)
    graph.add_node("validate", validate_code)
    graph.add_node("notify", notify_user)

    graph.set_entry_point("parse")
    graph.add_edge("parse", "generate")
    graph.add_edge("generate", "validate")
    graph.add_conditional_edges("validate", should_continue, {
        "pass": "notify",
        "fix": "generate",  # 修复后重新生成（带上次失败信息）
        "notify_user": "notify"
    })
    graph.add_edge("notify", END)

    return graph.compile()


# 全局工作流实例
workflow_app = build_workflow()


def run_workflow(requirement: str, skill_id: str = None, max_attempts: int = MAX_ATTEMPTS) -> Dict[str, Any]:
    """运行工作流的入口函数，必须指定skill_id"""
    # 强制必须传skill_id，避免误调用
    if not skill_id:
        raise ValueError(f"必须指定技能ID。可用技能: {list_skill_ids()}，请使用 --skill-id 参数指定")
    # 校验skill_id
    if get_skill_by_id(skill_id) is None:
        raise ValueError(f"技能ID不存在: {skill_id}，可用技能: {list_skill_ids()}")

    logger.info(f"=" * 50)
    logger.info(f"[工作流启动] 技能: {skill_id or '全部'}, 需求: {requirement[:50]}...")
    logger.info(f"=" * 50)

    result = workflow_app.invoke({
        "requirement": requirement,
        "skill_id": skill_id or "",
        "project_name": "",
        "project_dir": "",
        "generated_files": {},
        "auto_validation": None,
        "ai_validation": None,
        "final_validation": None,
        "attempt": 0,
        "max_attempts": max_attempts,
        "status": "pending",
        "error": None,
        "notify_message": None
    })

    logger.info(f"[工作流结束] 状态: {result['status']}")
    if result.get("notify_message"):
        logger.info(f"[工作流结束] 通知: {result['notify_message']}")

    return {
        "status": result["status"],
        "project_name": result["project_name"],
        "project_dir": result["project_dir"],
        "attempts": result["attempt"],
        "validation": result.get("final_validation"),
        "notify_message": result.get("notify_message"),
        "files": list(result.get("generated_files", {}).keys())
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="流程脚手架工作流")
    parser.add_argument("requirement", nargs="?", help="业务需求描述")
    parser.add_argument("--skill-id", type=str, required=True, help="必填，指定技能ID（python-app 或 web-js-app）")
    parser.add_argument("--max-attempts", type=int, default=3, help="最大修复尝试次数")
    parser.add_argument("--list-skills", action="store_true", help="列出所有可用技能")
    args = parser.parse_args()

    if args.list_skills:
        print("可用技能：")
        for s in list_skills():
            print(f"  - {s}")
        sys.exit(0)

    req = args.requirement or "抓取飞书多维表格中的订单数据，查询快递100物流状态，回填到飞书表格"
    result = run_workflow(req, skill_id=args.skill_id, max_attempts=args.max_attempts)
    print("\n" + "=" * 50)
    print(f"状态: {result['status']}")
    print(f"项目: {result['project_name']}")
    print(f"目录: {result['project_dir']}")
    print(f"尝试次数: {result['attempts']}")
    if result['validation']:
        v = result['validation']
        print(f"校验: {v['passed_count']}/{v['total_count']} 通过, {v['failed_count']} 未通过")
    print(f"通知: {result['notify_message']}")
    print(f"文件: {result['files']}")
