import boto3
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

class DynamoClient:
    def __init__(self):
        self.costs_table = dynamodb.Table('cloudpilot-costs')
        self.recs_table  = dynamodb.Table('cloudpilot-recommendations')
        self.audit_table = dynamodb.Table('cloudpilot-audit')

    def get_recommendations(self):
        try:
            resp = self.recs_table.scan()
            items = resp['Items']
            print(f"DynamoDB returned {len(items)} items")
            if not items:
                return []
            # Convert Decimal to float
            for item in items:
                item['monthly_saving'] = float(str(item.get('monthly_saving', 0)))
                item['confidence']     = float(str(item.get('confidence', 0.9)))
            return sorted(items, key=lambda x: x['monthly_saving'], reverse=True)
        except Exception as e:
            print(f"DynamoDB error: {e}")
            return []

    def save_cost_snapshot(self, data: dict):
        try:
            self.costs_table.put_item(Item={
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(), **data
            })
        except Exception as e:
            print(f"DynamoDB save error: {e}")

    def save_audit_log(self, action, resource, saving):
        try:
            self.audit_table.put_item(Item={
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'action': action, 'resource': resource,
                'monthly_saving': str(saving)
            })
        except Exception as e:
            print(f"DynamoDB audit error: {e}")
