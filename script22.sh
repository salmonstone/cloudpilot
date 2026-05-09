cat > /tmp/fixer.py << 'EOF'
import boto3, json, os
from datetime import datetime

ec2      = boto3.client('ec2', region_name='ap-south-1')
elb      = boto3.client('elbv2', region_name='ap-south-1')
s3       = boto3.client('s3', region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

def handler(event, context):
    action_type = event['type']
    resource    = event['resource']
    saving      = event.get('monthly_saving', 0)
    result      = 'unknown'

    try:
        if action_type == 'resize_ec2':
            target = event['target_type']
            ec2.stop_instances(InstanceIds=[resource])
            waiter = ec2.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[resource])
            ec2.modify_instance_attribute(
                InstanceId=resource,
                Attribute='instanceType',
                Value=target
            )
            ec2.start_instances(InstanceIds=[resource])
            result = f"Resized {resource} to {target}"

        elif action_type == 'delete_ebs' or action_type == 'remove_unused':
            # Check if it's an EBS volume ID
            if resource.startswith('vol-'):
                ec2.delete_volume(VolumeId=resource)
                result = f"Deleted EBS volume {resource}"
            else:
                result = f"Skipped {resource} — not an EBS volume"

        elif action_type == 'delete_lb':
            # Delete unused load balancer
            elb.delete_load_balancer(LoadBalancerArn=resource)
            result = f"Deleted Load Balancer {resource}"

        elif action_type == 'delete_nat':
            # Delete unused NAT gateway
            ec2.delete_nat_gateway(NatGatewayId=resource)
            result = f"Deleted NAT Gateway {resource}"

        elif action_type == 'storage_class':
            bucket = event.get('bucket', '')
            key    = event.get('key', '')
            if bucket and key:
                s3.copy_object(
                    Bucket=bucket, Key=key,
                    CopySource={'Bucket': bucket, 'Key': key},
                    StorageClass='INTELLIGENT_TIERING'
                )
                result = f"Changed {resource} to INTELLIGENT_TIERING"
            else:
                result = f"S3 bucket/key not provided"

        else:
            result = f"Unknown action type: {action_type}"

        # Save audit log
        dynamodb.Table('cloudpilot-audit').put_item(Item={
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
EOF

# Package and update Lambda
cd /tmp
zip auto_fixer.zip fixer.py

# Rename to handler.py inside zip
mkdir -p /tmp/fixer_build
cp /tmp/fixer.py /tmp/fixer_build/handler.py
cd /tmp/fixer_build
zip /tmp/auto_fixer_new.zip handler.py

# Update Lambda
aws lambda update-function-code \
  --function-name cloudpilot-auto-fixer \
  --zip-file fileb:///tmp/auto_fixer_new.zip \
  --region ap-south-1

echo "Lambda updated!"
