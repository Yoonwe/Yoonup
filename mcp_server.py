"""
MCP Server
将工作流暴露为MCP工具，供Cursor/豆包等支持MCP的AI工具调用
"""
import json
from mcp.server.fastmcp import FastMCP
from main import run_workflow

mcp = FastMCP("流程脚手架工作流")


@mcp.tool()
def generate_workflow(requirement: str, skill: str = None, max_attempts: int = 3) -> str:
    """
    根据业务需求生成符合技能规范的Python流程代码，并自动校验修复。

    Args:
        requirement: 业务需求描述
        skill: 技能名称（如 web-js-extractor 或 流程脚手架规范），不传则使用全部技能
        max_attempts: 最大校验修复尝试次数，默认3次

    Returns:
        生成结果的JSON字符串
    """
    try:
        result = run_workflow(requirement, skill=skill, max_attempts=max_attempts)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def list_skills() -> str:
    """列出所有可用的技能文档名称"""
    from main import list_skills as _list_skills
    return json.dumps({"skills": _list_skills()}, ensure_ascii=False)


@mcp.tool()
def check_project(project_dir: str) -> str:
    """
    对已有的流程项目目录执行规范校验。

    Args:
        project_dir: 流程项目的绝对路径

    Returns:
        校验结果的JSON字符串
    """
    from code_validator import auto_validate
    try:
        result = auto_validate(project_dir)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
