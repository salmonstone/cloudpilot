from groq import Groq
import os, json, boto3, uuid
from datetime import datetime, timedelta

client = Groq(api_key=os.environ['GROQ_API_KEY'])

def get_real_aws_data():
    ce = boto3.client('ce', region_name='ap-south-1')
    ec2 = boto3.client('ec2', region_name='ap-south-1')

    end   = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    try:
        costs = ce.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='MONTHLY',
            Metrics=['BlendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )['ResultsByTime']
    except:
        costs = []

    try:
        instances = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        ec2_list = [
            {
                'id': i['InstanceId'],
                'type': i['InstanceType'],
                'launch': str(i['LaunchTime'])
            }
            for r in instances['Reservations']
            for i in r['Instances']
        ]
    except:
        ec2_list = []

    return costs, ec2_list

def analyze_and_save():
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table('cloudpilot-recommendations')

    costs, ec2_list = get_real_aws_data()

    prompt = f"""
    You are an AWS cost optimization expert.
    Analyze this REAL AWS data and return ONLY a JSON array.

    Real AWS costs (last 30 days): {json.dumps(costs, default=str)}
    Real running EC2 instances: {json.dumps(ec2_list)}

    Generate 3-5 specific recommendations using the REAL resource IDs above.
    Each must have:
    - id: rec-001 etc
    - type: resize | delete | storage_class | rightsizing
    - resource: USE REAL resource ID from the data above
    - current: current config
    - suggested: recommended config
    - reason: specific reason with real numbers
    - monthly_saving: realistic number in dollars
    - confidence: 0.0 to 1.0
    - auto_fixable: true or false

    Return ONLY the JSON array. No explanation.
    """

    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()
    if '```' in raw:
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]

    recs = json.loads(raw.strip())

    # Clear old
    scan = table.scan()
    for item in scan['Items']:
        table.delete_item(Key={'id': item['id']})

    # Save new
    for rec in recs:
        rec['id'] = str(uuid.uuid4())[:8]
        rec['monthly_saving'] = str(rec.get('monthly_saving', 0))
        rec['confidence']     = str(rec.get('confidence', 0.9))
        rec['created_at']     = datetime.now().isoformat()
        table.put_item(Item=rec)

    return recs
