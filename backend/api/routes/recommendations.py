from fastapi import APIRouter
from services.dynamo import DynamoClient

router = APIRouter()
dynamo = DynamoClient()

@router.get("/recommendations")
def get_recommendations():
    recs = dynamo.get_recommendations()
    return {"recommendations": recs, "total": len(recs)}
