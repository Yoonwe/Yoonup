"""
MCP Server
将工作流暴露为MCP工具，供Cursor/豆包等支持MCP的AI工具调用
"""
import json
from mcp.server.fastmcp import FastMCP
from main import run_workflow
from checklist import load_skills_config

mcp = FastMCP("流程脚手架工作流")


@mcp.tool()
def generate_workflow(requirement: str, skill_id: str, max_attempts: int = 3) -> str:
    """
    根据业务需求生成符合技能规范的Python流程代码，并自动校验修复。
    Args:
        requirement: 业务需求描述
        skill_id: 必填，技能ID（python-app 或 web-js-app）
        max_attempts: 最大校验修复尝试次数，默认3次
    Returns:
        生成结果的JSON字符串
    """
    try:
        result = run_workflow(requirement, skill_id=skill_id, max_attempts=max_attempts)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def list_skills() -> str:
    """列出所有可用技能（ID和名称）"""
    config = load_skills_config()
    return json.dumps({"skills": [{"id": s["id"], "name": s["name"]} for s in config["skills"]]}, ensure_ascii=False)


@mcp.tool()
def check_project(project_dir: str, skill_id: str = None) -> str:
    """
    对已有的流程项目目录执行规范校验。
    Args:
        project_dir: 流程项目的绝对路径
        skill_id: 技能ID，不传则使用全部技能校验规则
    Returns:
        校验结果的JSON字符串
    """
    from code_validator import auto_validate
    try:
        result = auto_validate(project_dir, skill_id=skill_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
