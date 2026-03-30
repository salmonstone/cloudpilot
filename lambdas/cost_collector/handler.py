import boto3, json, os
from datetime import datetime, timedelta

ce  = boto3.client('ce')
sqs = boto3.client('sqs')
QUEUE_URL = os.environ['SQS_QUEUE_URL']

def handler(event, context):
    end   = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    resp  = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='DAILY',
        Metrics=['BlendedCost', 'UsageQuantity'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    payload = {
        'collected_at': datetime.now().isoformat(),
        'period': {'start': start, 'end': end},
        'data': resp['ResultsByTime']
    }
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(payload, default=str))
    return {'statusCode': 200, 'body': 'Cost data sent to SQS'}
