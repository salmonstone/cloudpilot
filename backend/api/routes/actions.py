from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ActionRequest(BaseModel):
    type: str
    resource: str
    monthly_saving: float = 0.0

@router.post("/execute")
def execute_action(req: ActionRequest):
    return {"status": "queued", "action": req.type, "resource": req.resource}
