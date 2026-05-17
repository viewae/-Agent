from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    upload_time: datetime
    status: str

    model_config = {"from_attributes": True}


class DocumentContentResponse(DocumentResponse):
    content: Optional[str] = None


class DocumentDeleteResponse(BaseModel):
    id: int
    message: str
