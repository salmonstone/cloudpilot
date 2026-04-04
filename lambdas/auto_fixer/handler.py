import boto3, json, os
from datetime import datetime
import time

ec2      = boto3.client('ec2', region_name='ap-south-1')
s3       = boto3.client('s3',  region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
AUDIT_TABLE = os.environ.get('AUDIT_TABLE', 'cloudpilot-audit')

def handler(event, context):
    action_type = event['type']
    resource    = event['resource']
    saving      = event.get('monthly_saving', 0)
    result      = 'unknown'

    try:
        if action_type == 'resize_ec2':
            target = event['target_type']

            # Stop instance
            ec2.stop_instances(InstanceIds=[resource])
            waiter = ec2.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[resource])

            # Resize
            ec2.modify_instance_attribute(
                InstanceId=resource,
                Attribute='instanceType',
                Value=target
            )

            # Start instance
            ec2.start_instances(InstanceIds=[resource])
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[resource])

            result = f"Resized {resource} to {target} and restarted"

        elif action_type == 'delete_ebs':
            ec2.delete_volume(VolumeId=resource)
            result = f"Deleted EBS volume {resource}"

        elif action_type == 'change_s3_storage_class':
            s3.copy_object(
                Bucket=event['bucket'], Key=event['key'],
                CopySource={'Bucket': event['bucket'], 'Key': event['key']},
                StorageClass='INTELLIGENT_TIERING'
            )
            result = f"Changed {resource} to INTELLIGENT_TIERING"

        # Save audit
        dynamodb.Table(AUDIT_TABLE).put_item(Item={
            'id': f'audit-{datetime.now().timestamp()}',
            'timestamp': datetime.now().isoformat(),
            'action': action_type,
            'resource': resource,
            'result': result,
            'monthly_saving': str(saving)
        })

        return {'statusCode': 200, 'result': result}

    except Exception as e:
        return {'statusCode': 500, 'error': str(e)}
