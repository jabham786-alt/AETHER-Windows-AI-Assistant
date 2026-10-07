from pydantic import BaseModel,Field
class ChatMessage(BaseModel):role:str=Field(pattern="^(user|assistant|system)$");content:str=Field(min_length=1,max_length=20000)
class ChatRequest(BaseModel):message:str=Field(min_length=1,max_length=20000);history:list[ChatMessage]=Field(default_factory=list,max_length=50)
class ChatResponse(BaseModel):content:str;provider:str;model:str