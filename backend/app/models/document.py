import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text

from app.database import Base


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, default=1, nullable=False)
    status = Column(String(20), default=DocumentStatus.UPLOADED.value, nullable=False)
    content_text = Column(Text, nullable=True)
