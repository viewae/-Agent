from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.task import (
    TaskExecuteRequest,
    TaskExecuteResponse,
    TaskStatusResponse,
    TaskStep,
)
from app.services.conversation_service import ConversationService
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    return ConversationService(db)


@router.post("/execute", response_model=ApiResponse[TaskExecuteResponse])
async def execute_task(
    req: TaskExecuteRequest,
    task_svc: TaskService = Depends(get_task_service),
    conv: ConversationService = Depends(get_conversation_service),
):
    session_id = conv.create_or_get_session(req.session_id)
    result = task_svc.execute(req.instruction, req.document_ids)
    result.session_id = session_id
    return ApiResponse(data=result)


@router.get("/{task_id}/status", response_model=ApiResponse[TaskStatusResponse])
async def get_task_status(
    task_id: str,
    task_svc: TaskService = Depends(get_task_service),
):
    task = task_svc.get_status(task_id)
    if not task:
        return ApiResponse(data=TaskStatusResponse(
            task_id=task_id, intent="unknown", status="not_found",
            steps=[], result=None,
        ))
    steps_data = json.loads(task.steps_json) if task.steps_json else []
    return ApiResponse(data=TaskStatusResponse(
        task_id=task.task_id, intent=task.intent, status=task.status,
        steps=[TaskStep(**s) for s in steps_data], result=task.result,
    ))


@router.get("/history", response_model=ApiResponse[list[TaskStatusResponse]])
async def list_task_history(
    task_svc: TaskService = Depends(get_task_service),
):
    tasks = task_svc.get_history()
    result = []
    for t in tasks:
        steps_data = json.loads(t.steps_json) if t.steps_json else []
        result.append(TaskStatusResponse(
            task_id=t.task_id, intent=t.intent, status=t.status,
            steps=[TaskStep(**s) for s in steps_data], result=t.result,
        ))
    return ApiResponse(data=result)
