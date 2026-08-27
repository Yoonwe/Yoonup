"""
FastAPI HTTP 接口
暴露工作流为REST API，供外部工具调用
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from main import run_workflow

app = FastAPI(title="流程脚手架工作流 API", version="1.0.0")


class WorkflowRequest(BaseModel):
    requirement: str
    max_attempts: Optional[int] = 3


class WorkflowResponse(BaseModel):
    status: str
    project_name: str
    project_dir: str
    attempts: int
    validation: Optional[Dict[str, Any]] = None
    notify_message: Optional[str] = None
    files: list


@app.post("/run", response_model=WorkflowResponse)
async def run_workflow_api(request: WorkflowRequest):
    """运行工作流：传入需求，返回生成结果和校验状态"""
    try:
        result = run_workflow(request.requirement, request.max_attempts)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "workflow-engine"}


@app.get("/skills")
async def list_skills():
    """列出已加载的技能文档"""
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    files = [f for f in os.listdir(skills_dir) if f.endswith('.md')]
    return {"skills": files}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
