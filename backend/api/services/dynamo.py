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
            return sorted(resp['Items'], key=lambda x: float(x.get('monthly_saving', 0)), reverse=True)
        except Exception:
            # DynamoDB tables not created yet (Terraform not run)
            # Return demo data so frontend works
            return [
                {
                    "id": "rec-001",
                    "type": "resize",
                    "resource": "i-0abc123def456",
                    "current": "t3.xlarge",
                    "suggested": "t3.medium",
                    "reason": "CPU avg 8% over 30 days — instance is oversized",
                    "monthly_saving": 45.20,
                    "confidence": 0.94,
                    "auto_fixable": True
                },
                {
                    "id": "rec-002",
                    "type": "delete",
                    "resource": "vol-0xyz789abc123",
                    "current": "100GB EBS gp2",
                    "suggested": "Delete volume",
                    "reason": "Not attached to any instance for 14 days",
                    "monthly_saving": 12.00,
                    "confidence": 0.99,
                    "auto_fixable": True
                },
                {
                    "id": "rec-003",
                    "type": "storage_class",
                    "resource": "s3://cloudpilot-logs-bucket",
                    "current": "S3 Standard",
                    "suggested": "S3 Intelligent-Tiering",
                    "reason": "Objects not accessed in 90 days",
                    "monthly_saving": 70.20,
                    "confidence": 0.87,
                    "auto_fixable": True
                },
            ]

    def save_cost_snapshot(self, data: dict):
        try:
            self.costs_table.put_item(Item={
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(), **data
            })
        except Exception as e:
            print(f"DynamoDB not available yet: {e}")

    def save_audit_log(self, action, resource, saving):
        try:
            self.audit_table.put_item(Item={
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'action': action, 'resource': resource,
                'monthly_saving': str(saving),
                'executed_by': 'cloudpilot-api'
            })
        except Exception as e:
            print(f"DynamoDB not available yet: {e}")
