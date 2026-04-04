from fastapi import APIRouter
from services.dynamo import DynamoClient
from services.ai_engine import analyze_and_save
import boto3

router = APIRouter()
dynamo = DynamoClient()

@router.get("/recommendations")
def get_recommendations():
    try:
        # Try DynamoDB first
        recs = dynamo.get_recommendations()

        # If empty — run AI analysis now
        if not recs:
            recs = analyze_and_save()

        return {
            "recommendations": recs,
            "total": len(recs),
            "total_saving": sum(float(r.get('monthly_saving', 0)) for r in recs)
        }
    except Exception as e:
        return {"recommendations": [], "total": 0, "error": str(e)}

@router.post("/recommendations/refresh")
def refresh_recommendations():
    try:
        recs = analyze_and_save()
        return {"status": "refreshed", "count": len(recs)}
    except Exception as e:
        return {"status": "error", "error": str(e)}
