from fastapi import APIRouter
from backend.app.database import Base,engine
from backend.app import models
router=APIRouter();Base.metadata.create_all(bind=engine)
@router.get("/health")
def health():return {"status":"ok","service":"aether-core","version":"0.1.0"}