from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.automation.executor import execute
from backend.app.automation.permissions import requires_confirmation, risk_for
from backend.app.database import SessionLocal
from backend.app.models import AutomationAction
import uuid

router = APIRouter(prefix="/automation", tags=["automation"])

class ActionRequest(BaseModel):
    action: str = Field(min_length=1, max_length=50)
    params: dict = Field(default_factory=dict)
    confirmed: bool = False

@router.get("/actions")
def actions():
    return {
        "actions": [
            {"id": key, "risk": risk_for(key).value, "requires_confirmation": requires_confirmation(key)}
            for key in [
                "open_app","open_url","open_folder","search_files","create_folder",
                "create_file","rename_file","copy_file","move_file","delete_file"
            ]
        ]
    }

@router.get("/history")
def history(limit: int = 50):
    limit = max(1, min(limit, 200))
    with SessionLocal() as db:
        rows = db.query(AutomationAction).order_by(AutomationAction.created_at.desc()).limit(limit).all()
        return [{
            "id": row.id, "action": row.action, "risk": row.risk, "status": row.status,
            "details": row.details, "created_at": row.created_at.isoformat()
        } for row in rows]

@router.post("/execute")
def run_action(request: ActionRequest):
    try:
        risk = risk_for(request.action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if requires_confirmation(request.action) and not request.confirmed:
        return {
            "status": "confirmation_required",
            "action": request.action,
            "risk": risk.value,
            "params": request.params,
            "message": "This action requires explicit confirmation."
        }
    try:
        result = execute(request.action, request.params)
    except (ValueError, RuntimeError, OSError, TypeError) as exc:
        with SessionLocal() as db:
            db.add(AutomationAction(
                id=str(uuid.uuid4()), action=request.action, risk=risk.value,
                status="failed", details=str(exc), created_at=datetime.now(timezone.utc)
            ))
            db.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    with SessionLocal() as db:
        db.add(AutomationAction(
            id=str(uuid.uuid4()), action=request.action, risk=risk.value,
            status="success", details=str(result), created_at=datetime.now(timezone.utc)
        ))
        db.commit()
    return {"status": "success", "risk": risk.value, "result": result}
