import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(32), unique=True, nullable=False, index=True)
    intent = Column(String(20), nullable=False)
    status = Column(String(20), default=TaskStatus.PENDING, nullable=False)
    instruction = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    steps_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
