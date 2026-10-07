from uuid import uuid4
from fastapi import APIRouter,HTTPException
from backend.app.config import get_settings
from backend.app.providers import get_provider,ProviderError
from backend.app.schemas import ChatRequest,ChatResponse
from backend.app.database import SessionLocal
from backend.app.models import Conversation,Message,Memory
from sqlalchemy import or_,select

router=APIRouter()

def retrieve_memories(query:str,limit:int=6)->list[Memory]:
 terms=[x.strip() for x in query.split() if len(x.strip())>=2][:10]
 if not terms:return []
 with SessionLocal() as db:
  rows=db.scalars(select(Memory).where(or_(*[or_(Memory.content.ilike(f"%{t}%"),Memory.category.ilike(f"%{t}%")) for t in terms])).order_by(Memory.updated_at.desc()).limit(limit)).all()
 return rows

@router.post("/chat",response_model=ChatResponse)
async def chat(request:ChatRequest):
 s=get_settings()
 memory_rows=retrieve_memories(request.message)
 memory_context=[{"role":"system","content":"Relevant AETHER memories (use only when relevant; do not invent facts):\n"+"\n".join(f"- [{m.category}] {m.content}" for m in memory_rows)}] if memory_rows else []
 msgs=[{"role":"system","content":"You are AETHER, a helpful personal Windows AI assistant."}]+memory_context+[{"role":m.role,"content":m.content} for m in request.history]+[{"role":"user","content":request.message}]
 try:content=await get_provider().complete(msgs)
 except ProviderError as e:raise HTTPException(status_code=503,detail=str(e))
 with SessionLocal() as db:
  cid=str(uuid4());db.add(Conversation(id=cid,title=request.message[:80]));db.add(Message(id=str(uuid4()),conversation_id=cid,role="user",content=request.message));db.add(Message(id=str(uuid4()),conversation_id=cid,role="assistant",content=content));db.commit()
 return ChatResponse(content=content,provider=s.ai_provider,model=s.ai_model)
