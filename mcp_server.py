"""
MCP Server
将工作流暴露为MCP工具，供Cursor/豆包等支持MCP的AI工具调用
"""
import json
from mcp.server.fastmcp import FastMCP
from main import run_workflow

mcp = FastMCP("流程脚手架工作流")


@mcp.tool()
def generate_workflow(requirement: str, max_attempts: int = 3) -> str:
    """
    根据业务需求生成符合流程脚手架规范的Python流程代码，并自动校验修复。

    Args:
        requirement: 业务需求描述，例如"抓取飞书表格订单数据，查询快递100物流状态，回填飞书"
        max_attempts: 最大校验修复尝试次数，默认3次

    Returns:
        生成结果的JSON字符串，包含状态、项目目录、校验结果、文件列表
    """
    try:
        result = run_workflow(requirement, max_attempts)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


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
