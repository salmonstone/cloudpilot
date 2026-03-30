import boto3, json, os
from datetime import datetime

ec2      = boto3.client('ec2', region_name='ap-south-1')
s3       = boto3.client('s3',  region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
AUDIT_TABLE = os.environ['AUDIT_TABLE']

def handler(event, context):
    action_type = event['type']
    resource    = event['resource']
    saving      = event.get('monthly_saving', 0)
    result      = 'unknown'

    if action_type == 'resize_ec2':
        ec2.modify_instance_attribute(
            InstanceId=resource, Attribute='instanceType', Value=event['target_type'])
        result = f"Resized {resource} to {event['target_type']}"

    elif action_type == 'delete_ebs':
        ec2.delete_volume(VolumeId=resource)
        result = f'Deleted EBS volume {resource}'

    elif action_type == 'change_s3_storage_class':
        s3.copy_object(Bucket=event['bucket'], Key=event['key'],
            CopySource={'Bucket': event['bucket'], 'Key': event['key']},
            StorageClass='INTELLIGENT_TIERING')
        result = f"Changed {resource} to INTELLIGENT_TIERING"

    # Save audit log
    dynamodb.Table(AUDIT_TABLE).put_item(Item={
        'id': f'audit-{datetime.now().timestamp()}',
        'timestamp': datetime.now().isoformat(),
        'action': action_type, 'resource': resource,
        'result': result, 'monthly_saving': str(saving)
    })
    return {'statusCode': 200, 'result': result}
