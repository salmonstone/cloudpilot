from fastapi import APIRouter

router = APIRouter()

@router.get("/30d")
def forecast_30d():
    return {"forecast": "30d", "status": "ok"}

@router.get("/90d")
def forecast_90d():
    return {"forecast": "90d", "status": "ok"}
