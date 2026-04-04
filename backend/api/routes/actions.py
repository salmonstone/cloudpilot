from fastapi import APIRouter
from pydantic import BaseModel
import boto3, json
from datetime import datetime

router = APIRouter()
lambda_client = boto3.client('lambda', region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

class ActionRequest(BaseModel):
    type: str
    resource: str
    monthly_saving: float = 0.0
    target_type: str = ""
    bucket: str = ""
    key: str = ""

@router.post("/execute")
def execute_action(req: ActionRequest):
    try:
        payload = {
            "type": req.type,
            "resource": req.resource,
            "monthly_saving": req.monthly_saving,
            "target_type": req.target_type
        }

        response = lambda_client.invoke(
            FunctionName='cloudpilot-auto-fixer',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        result = json.loads(response['Payload'].read())

        dynamodb.Table('cloudpilot-audit').put_item(Item={
            'id': f"audit-{datetime.now().timestamp()}",
            'timestamp': datetime.now().isoformat(),
            'action': req.type,
            'resource': req.resource,
            'monthly_saving': str(req.monthly_saving),
            'result': str(result)
        })

        return {"status": "success", "result": result}

    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get("/audit")
def get_audit():
    try:
        table = dynamodb.Table('cloudpilot-audit')
        items = sorted(table.scan()['Items'],
                      key=lambda x: x['timestamp'], reverse=True)
        return {"audit": items, "total": len(items)}
    except Exception as e:
        return {"audit": [], "error": str(e)}
