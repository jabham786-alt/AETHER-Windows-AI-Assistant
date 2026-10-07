from uuid import uuid4
from fastapi import APIRouter,HTTPException
from backend.app.config import get_settings
from backend.app.providers import get_provider,ProviderError
from backend.app.schemas import ChatRequest,ChatResponse
from backend.app.database import SessionLocal
from backend.app.models import Conversation,Message
router=APIRouter()
@router.post("/chat",response_model=ChatResponse)
async def chat(request:ChatRequest):
 s=get_settings();msgs=[{"role":"system","content":"You are AETHER, a helpful personal Windows AI assistant."}]+[{"role":m.role,"content":m.content} for m in request.history]+[{"role":"user","content":request.message}]
 try:content=await get_provider().complete(msgs)
 except ProviderError as e:raise HTTPException(status_code=503,detail=str(e))
 with SessionLocal() as db:
  cid=str(uuid4());db.add(Conversation(id=cid,title=request.message[:80]));db.add(Message(id=str(uuid4()),conversation_id=cid,role="user",content=request.message));db.add(Message(id=str(uuid4()),conversation_id=cid,role="assistant",content=content));db.commit()
 return ChatResponse(content=content,provider=s.ai_provider,model=s.ai_model)