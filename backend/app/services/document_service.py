import logging
import os

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.exceptions import NotFoundError
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.schemas.document import (
    DocumentContentResponse,
    DocumentDeleteResponse,
    DocumentResponse,
)
from app.schemas.common import PaginatedData
from app.services.embedding_service import EmbeddingService
from app.services.parser_service import ParserService
from app.services.vector_store_service import VectorStoreService
from app.utils.file_utils import (
    generate_unique_filename,
    validate_file_extension,
    validate_file_size,
)
from app.utils.text_splitter import ChineseTextSplitter

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.parser_service = ParserService()
        self.embedding_service = EmbeddingService()
        self.vector_store_service = VectorStoreService()
        self.splitter = ChineseTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

    def upload(self, file: UploadFile) -> DocumentResponse:
        validate_file_extension(file.filename)
        unique_name = generate_unique_filename(file.filename)
        file_type = os.path.splitext(file.filename)[1].lstrip(".").lower()
        dest = os.path.join(settings.UPLOAD_DIR, unique_name)

        contents = file.file.read()
        file_size = len(contents)
        if file_size == 0:
            raise ValidationError("File is empty")
        validate_file_size(file_size)

        with open(dest, "wb") as f:
            f.write(contents)

        doc = Document(
            filename=file.filename,
            file_path=unique_name,
            file_type=file_type,
            file_size=file_size,
            status=DocumentStatus.PROCESSING.value,
        )
        self.db.add(doc)
        self.db.flush()

        try:
            text = self.parser_service.parse(dest, file_type)
            doc.content_text = text

            chunks = self.splitter.split(text)
            if chunks:
                texts = [c.text for c in chunks]
                embeddings = self.embedding_service.embed_batch(texts)
                ids = [f"doc_{doc.id}_chunk_{c.index}" for c in chunks]
                metadatas = [
                    {
                        "document_id": doc.id,
                        "chunk_index": c.index,
                        "filename": doc.filename,
                        "file_type": doc.file_type,
                        "token_count": c.token_count,
                    }
                    for c in chunks
                ]
                self.vector_store_service.add_documents(ids, embeddings, texts, metadatas)

                for c in chunks:
                    self.db.add(DocumentChunk(
                        document_id=doc.id,
                        chunk_index=c.index,
                        chunk_text=c.text,
                        token_count=c.token_count,
                        chroma_id=f"doc_{doc.id}_chunk_{c.index}",
                    ))

            doc.status = DocumentStatus.COMPLETED.value
        except Exception as e:
            logger.exception("Document processing failed for %s", file.filename)
            doc.status = DocumentStatus.FAILED.value

        self.db.commit()
        self.db.refresh(doc)
        return DocumentResponse.model_validate(doc)

    def list_documents(self, page: int, page_size: int) -> PaginatedData[DocumentResponse]:
        offset = (page - 1) * page_size
        total = self.db.query(Document).count()
        docs = (
            self.db.query(Document)
            .order_by(Document.upload_time.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        items = [DocumentResponse.model_validate(d) for d in docs]
        return PaginatedData(items=items, total=total, page=page, page_size=page_size)

    def get_content(self, document_id: int) -> DocumentContentResponse:
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if doc is None:
            raise NotFoundError(f"Document {document_id} not found")
        return DocumentContentResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            upload_time=doc.upload_time,
            status=doc.status,
            content=doc.content_text,
        )

    def delete(self, document_id: int) -> DocumentDeleteResponse:
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if doc is None:
            raise NotFoundError(f"Document {document_id} not found")
        file_path = os.path.join(settings.UPLOAD_DIR, doc.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        self.vector_store_service.delete_by_document_id(document_id)
        self.db.delete(doc)
        self.db.commit()
        return DocumentDeleteResponse(id=document_id, message="Document deleted successfully")
