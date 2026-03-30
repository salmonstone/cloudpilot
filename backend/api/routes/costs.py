from fastapi import APIRouter
from services.aws_cost import CostExplorerClient
from services.dynamo import DynamoClient

router = APIRouter()
cost_client = CostExplorerClient()
dynamo = DynamoClient()

@router.get("/summary")
def get_cost_summary():
    data = cost_client.get_monthly_costs()
    return {"costs": data, "status": "ok"}

@router.get("/idle")
def get_idle_resources():
    idle = cost_client.get_idle_ec2()
    return {"idle_resources": idle}
