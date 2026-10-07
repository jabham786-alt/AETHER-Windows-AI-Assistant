from abc import ABC,abstractmethod
import httpx
from backend.app.config import get_settings
class ProviderError(RuntimeError):pass
class AIProvider(ABC):
 @abstractmethod
 async def complete(self,messages:list[dict[str,str]])->str:...
class OpenAIProvider(AIProvider):
 async def complete(self,messages):
  s=get_settings()
  if not s.openai_api_key:raise ProviderError("OPENAI_API_KEY is not configured.")
  async with httpx.AsyncClient(timeout=60) as c:r=await c.post("https://api.openai.com/v1/chat/completions",json={"model":s.ai_model,"messages":messages,"temperature":0.2},headers={"Authorization":"Bearer "+s.openai_api_key})
  if r.status_code>=400:raise ProviderError("OpenAI error "+str(r.status_code)+": "+r.text[:500])
  return r.json()["choices"][0]["message"]["content"]
class GeminiProvider(AIProvider):
 async def complete(self,messages):
  s=get_settings()
  if not s.gemini_api_key:raise ProviderError("GEMINI_API_KEY is not configured.")
  contents=[{"role":"model" if m["role"]=="assistant" else "user","parts":[{"text":m["content"]}]} for m in messages if m["role"]!="system"]
  async with httpx.AsyncClient(timeout=60) as c:r=await c.post("https://generativelanguage.googleapis.com/v1beta/models/"+s.ai_model+":generateContent",params={"key":s.gemini_api_key},json={"contents":contents})
  if r.status_code>=400:raise ProviderError("Gemini error "+str(r.status_code)+": "+r.text[:500])
  return r.json()["candidates"][0]["content"]["parts"][0]["text"]
def get_provider():return GeminiProvider() if get_settings().ai_provider.lower()=="gemini" else OpenAIProvider()