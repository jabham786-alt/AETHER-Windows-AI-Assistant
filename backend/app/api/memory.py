from uuid import uuid4
from fastapi import APIRouter,HTTPException,Query
from pydantic import BaseModel,Field
from sqlalchemy import select,or_
from backend.app.database import SessionLocal
from backend.app.models import Memory

router=APIRouter()

class MemoryCreate(BaseModel):
 category:str=Field(default="general",min_length=1,max_length=40)
 content:str=Field(min_length=1,max_length=10000)
 source:str=Field(default="user",min_length=1,max_length=40)

class MemoryUpdate(BaseModel):
 category:str|None=Field(default=None,min_length=1,max_length=40)
 content:str|None=Field(default=None,min_length=1,max_length=10000)

def _item(m:Memory)->dict:
 return {"id":m.id,"category":m.category,"content":m.content,"source":m.source,"created_at":m.created_at.isoformat(),"updated_at":m.updated_at.isoformat()}

@router.get("/memories")
def list_memories(limit:int=Query(default=100,ge=1,le=500)):
 with SessionLocal() as db:
  rows=db.scalars(select(Memory).order_by(Memory.updated_at.desc()).limit(limit)).all()
 return [_item(m) for m in rows]

@router.post("/memories",status_code=201)
def create_memory(request:MemoryCreate):
 with SessionLocal() as db:
  m=Memory(id=str(uuid4()),category=request.category.strip(),content=request.content.strip(),source=request.source.strip())
  db.add(m);db.commit();db.refresh(m);return _item(m)

@router.patch("/memories/{memory_id}")
def update_memory(memory_id:str,request:MemoryUpdate):
 with SessionLocal() as db:
  m=db.get(Memory,memory_id)
  if not m: raise HTTPException(status_code=404,detail="Memory not found")
  if request.category is not None:m.category=request.category.strip()
  if request.content is not None:m.content=request.content.strip()
  db.commit();db.refresh(m);return _item(m)

@router.delete("/memories/{memory_id}",status_code=204)
def delete_memory(memory_id:str):
 with SessionLocal() as db:
  m=db.get(Memory,memory_id)
  if not m: raise HTTPException(status_code=404,detail="Memory not found")
  db.delete(m);db.commit()

@router.get("/memories/search")
def search_memories(q:str=Query(min_length=1,max_length=200),limit:int=Query(default=8,ge=1,le=20)):
 terms=[x.strip() for x in q.split() if len(x.strip())>=2][:12]
 if not terms:return []
 with SessionLocal() as db:
  conditions=[or_(Memory.content.ilike(f"%{term}%"),Memory.category.ilike(f"%{term}%")) for term in terms]
  rows=db.scalars(select(Memory).where(or_(*conditions)).order_by(Memory.updated_at.desc()).limit(limit)).all()
 return [_item(m) for m in rows]
