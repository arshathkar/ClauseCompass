from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.session.store import session_store
from app.api.deps import get_session
from app.session.store import SessionData

router = APIRouter()

class SessionCreateResponse(BaseModel):
    session_id: str

@router.post("/v1/sessions", response_model=SessionCreateResponse)
async def create_session():
    session_id = session_store.create()
    return {"session_id": session_id}

@router.delete("/v1/sessions/current", status_code=204)
async def delete_session(session: SessionData = Depends(get_session)):
    session_store.delete(session.id)
