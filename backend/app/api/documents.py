from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.document import (
    DocumentContentResponse,
    DocumentDeleteResponse,
    DocumentResponse,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)


@router.post("/upload", response_model=ApiResponse[DocumentResponse], status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
):
    result = service.upload(file)
    return ApiResponse(code=201, message="Document uploaded successfully", data=result)


@router.get("/list", response_model=ApiResponse[PaginatedData[DocumentResponse]])
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: DocumentService = Depends(get_document_service),
):
    result = service.list_documents(page, page_size)
    return ApiResponse(data=result)


@router.get("/{document_id}/content", response_model=ApiResponse[DocumentContentResponse])
async def get_document_content(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
):
    result = service.get_content(document_id)
    return ApiResponse(data=result)


@router.delete("/{document_id}", response_model=ApiResponse[DocumentDeleteResponse])
async def delete_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
):
    result = service.delete(document_id)
    return ApiResponse(data=result)
