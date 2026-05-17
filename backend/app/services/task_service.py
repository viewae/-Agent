from __future__ import annotations

import json
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.intents.classifier import IntentClassifier
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskExecuteResponse, TaskStep
from app.tasks.executor import EXECUTOR_MAP, GeneralExecutor


class TaskService:
    def __init__(self, db: Session | None = None):
        self._classifier = IntentClassifier()
        self._db = db

    def execute(
        self,
        instruction: str,
        document_ids: list[int] | None = None,
        chat_history: list[dict] | None = None,
    ) -> TaskExecuteResponse:
        task_id = uuid.uuid4().hex[:16]
        steps: list[TaskStep] = []
        step_counter = [0]

        def add_step(description: str):
            step_counter[0] += 1
            steps.append(TaskStep(
                step=step_counter[0],
                description=description,
                status="completed",
            ))

        # Persist initial task record
        self._save_task(task_id, "", TaskStatus.PENDING, instruction, steps)

        try:
            self._update_task(task_id, status=TaskStatus.RUNNING)

            add_step("分析用户意图")
            intent = self._classifier.classify(instruction)
            steps[-1].description = f"意图识别: {intent.value}"
            self._update_task(task_id, intent=intent.value, steps=steps)

            executor = EXECUTOR_MAP.get(intent, GeneralExecutor())
            result = executor.execute(instruction, document_ids, chat_history, add_step)

            self._update_task(task_id, status=TaskStatus.COMPLETED, steps=steps, result=result)

            return TaskExecuteResponse(
                task_id=task_id,
                intent=intent.value,
                steps=steps,
                result=result,
            )
        except Exception:
            self._update_task(task_id, status=TaskStatus.FAILED, steps=steps)
            raise

    def get_status(self, task_id: str) -> Task | None:
        if not self._db:
            return None
        return self._db.query(Task).filter(Task.task_id == task_id).first()

    def get_history(self, limit: int = 20) -> list[Task]:
        if not self._db:
            return []
        return (
            self._db.query(Task)
            .order_by(Task.created_at.desc())
            .limit(limit)
            .all()
        )

    def _save_task(self, task_id, intent, status, instruction, steps):
        if not self._db:
            return
        task = Task(
            task_id=task_id,
            intent=intent,
            status=status,
            instruction=instruction,
            steps_json=json.dumps([s.model_dump() for s in steps], ensure_ascii=False),
        )
        self._db.add(task)
        self._db.commit()

    def _update_task(self, task_id, **kwargs):
        if not self._db:
            return
        task = self._db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            return
        if "steps" in kwargs:
            kwargs["steps_json"] = json.dumps(
                [s.model_dump() for s in kwargs.pop("steps")], ensure_ascii=False
            )
        if kwargs.get("status") in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            kwargs["completed_at"] = datetime.utcnow()
        for k, v in kwargs.items():
            setattr(task, k, v)
        self._db.commit()
