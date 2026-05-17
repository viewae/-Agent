from typing import Optional

from pydantic import BaseModel


class TaskExecuteRequest(BaseModel):
    instruction: str
    document_ids: Optional[list[int]] = None
    session_id: Optional[str] = None


class TaskStep(BaseModel):
    step: int
    description: str
    status: str


class TaskExecuteResponse(BaseModel):
    task_id: str
    intent: str
    steps: list[TaskStep] = []
    result: str
    session_id: Optional[str] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    intent: str
    status: str
    steps: list[TaskStep] = []
    result: Optional[str] = None
