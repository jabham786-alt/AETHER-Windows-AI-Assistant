from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import health,chat,system
app=FastAPI(title="AETHER Core",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1:5173","http://localhost:5173"],allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["Content-Type"])
app.include_router(health.router,prefix="/api");app.include_router(chat.router,prefix="/api");app.include_router(system.router,prefix="/api")