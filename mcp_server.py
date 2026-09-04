# -*- coding: utf-8 -*-
"""
远程 MCP Server（mcp_server.py）
将 Yoonup 工作流三件套中的"远程MCP"能力暴露为标准 MCP 服务，支持任意支持 MCP 的
AI 产品（豆包 / Cursor / Dify / Marvis 等）远程接入，实现"任何电脑可用"：

  工具列表：
    list_skills       列出所有可用技能（id/name/description）
    get_skill_spec    获取技能规范全文 + 校验清单章节
    plan_requirement  按技能规范生成执行计划骨架（含需向用户确认的问题）
    check_result      对执行结果做末端整合校验（自动检查 + 返回清单供 AI 核对）

运行方式：
    python mcp_server.py                 # streamable-http 传输，默认 0.0.0.0:8081
    python mcp_server.py --port 9000     # 自定义端口
    python mcp_server.py --transport sse # 兼容旧 SSE 传输（部分平台）

部署到云服务器后，在 Dify / 其他 MCP 客户端填入:
    http://<服务器IP>:8081/mcp
"""
import argparse
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from validator import (
    list_skills as _list_skills,
    get_skill_spec as _get_skill_spec,
    plan_requirement as _plan_requirement,
    check_result as _check_result,
)

mcp = FastMCP("yoonup")


@mcp.tool()
def list_skills() -> Dict[str, Any]:
    """列出所有可用技能（id/name/description/check_section）"""
    return {"skills": [
        {"id": s["id"], "name": s["name"], "description": s.get("description", "")}
        for s in _list_skills()
    ]}


@mcp.tool()
def get_skill_spec(skill_id: str, include_checklist: bool = True) -> Dict[str, Any]:
    """
    获取指定技能的规范全文与校验清单章节。
    参数:
        skill_id: 技能ID（yoonup-workflow / python-app-standard / web-js-app-implementation，可先调 list_skills 查看）
        include_checklist: 是否同时返回校验清单（默认 true）
    返回:
        skill_id / skill_name / description / spec（MD全文） / checklist（结构化） / checklist_text（AI核对文本）
    """
    return _get_skill_spec(skill_id, include_checklist=include_checklist)


@mcp.tool()
def plan_requirement(requirement: str, skill_id: Optional[str] = None) -> Dict[str, Any]:
    """
    按技能规范生成执行计划骨架（规则引擎，不依赖 LLM）。
    参数:
        requirement: 用户原始需求
        skill_id: 可选；不传时按需求关键词自动识别
    返回:
        skill_id / skill_name / plan_steps（分步计划） / questions_to_user（需要向用户提问确认的事项） / note
    使用约定: 拿到计划后结合需求细化步骤，需求拆分时向用户提问确认执行顺序，禁止自行跳过提问；
             全部执行完成后必须调用 check_result 做末端整合校验。
    """
    return _plan_requirement(requirement, skill_id)


@mcp.tool()
def check_result(project_dir: str, skill_id: Optional[str] = None,
                 include_details: bool = True) -> Dict[str, Any]:
    """
    对执行结果（项目目录/交付物目录）做末端整合校验，按技能「校验清单」章节逐项核对。
    参数:
        project_dir: 执行结果所在目录的绝对路径（服务端可访问的路径）
        skill_id: 可选；不传则按全部技能校验
        include_details: 是否返回需 AI 逐项核对的清单文本（默认 true）
    返回:
        auto_passed / auto_failed / all_auto_passed / ai_checklist / summary
    使用约定: ai_checklist 中的条目必须由调用方 AI 结合交付物逐项核对，未通过项修复后重新校验。
    """
    return _check_result(project_dir, skill_id, include_details=include_details)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yoonup 远程 MCP Server")
    parser.add_argument("--port", type=int, default=8081, help="监听端口（默认8081）")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="监听地址（默认0.0.0.0）")
    parser.add_argument("--transport", type=str, default="streamable-http",
                        choices=["streamable-http", "sse"], help="传输协议")
    args = parser.parse_args()

    mcp.settings.host = args.host
    mcp.settings.port = args.port
    mcp.run(transport=args.transport)
