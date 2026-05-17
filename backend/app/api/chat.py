import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import MessageRole
from app.schemas.chat import ChatRequest, ChatResponse, SessionResponse
from app.schemas.common import ApiResponse
from app.services.conversation_service import ConversationService
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["chat"])


def get_rag_service() -> RAGService:
    return RAGService()


def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    return ConversationService(db)


@router.post("/query", response_model=ApiResponse[ChatResponse])
async def chat_query(
    req: ChatRequest,
    rag: RAGService = Depends(get_rag_service),
    conv: ConversationService = Depends(get_conversation_service),
):
    session_id = conv.create_or_get_session(req.session_id)
    conv.save_message(session_id, MessageRole.USER.value, req.query)
    history = conv.get_session_history(session_id)[:-1]

    result = rag.answer(req.query, req.document_ids, history)

    conv.save_message(
        session_id,
        MessageRole.ASSISTANT.value,
        result["answer"],
        metadata={"sources": result["sources"]},
    )

    return ApiResponse(data=ChatResponse(
        answer=result["answer"],
        session_id=session_id,
        sources=result["sources"],
    ))


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    rag: RAGService = Depends(get_rag_service),
    conv: ConversationService = Depends(get_conversation_service),
):
    session_id = conv.create_or_get_session(req.session_id)
    conv.save_message(session_id, MessageRole.USER.value, req.query)
    history = conv.get_session_history(session_id)[:-1]

    full_answer = []

    async def generate():
        for chunk in rag.answer_stream(req.query, req.document_ids, history):
            data = json.loads(chunk.replace("data: ", "").strip())
            if "content" in data:
                full_answer.append(data["content"])
            elif "sources" in data:
                conv.save_message(
                    session_id, MessageRole.ASSISTANT.value,
                    "".join(full_answer), metadata={"sources": data["sources"]},
                )
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/sessions", response_model=ApiResponse[list[SessionResponse]])
async def list_sessions(
    conv: ConversationService = Depends(get_conversation_service),
):
    result = conv.get_user_sessions()
    return ApiResponse(data=[SessionResponse(**r) for r in result])


@router.get("/sessions/{session_id}", response_model=ApiResponse[list[dict]])
async def get_session_history(
    session_id: str,
    conv: ConversationService = Depends(get_conversation_service),
):
    history = conv.get_session_history(session_id)
    return ApiResponse(data=history)


@router.delete("/sessions/{session_id}", response_model=ApiResponse)
async def delete_session(
    session_id: str,
    conv: ConversationService = Depends(get_conversation_service),
):
    conv.delete_session(session_id)
    return ApiResponse(message=f"Session {session_id} deleted")
