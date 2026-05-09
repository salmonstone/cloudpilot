python3 -c "
import json
with open('/tmp/payload.json', 'w') as f:
    json.dump({
        'type': 'delete_ebs',
        'resource': 'vol-0ee7e3e814e448276',
        'monthly_saving': 5
    }, f)
"

aws lambda invoke \
  --function-name cloudpilot-auto-fixer \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  --payload file:///tmp/payload.json \
  /tmp/out.json

cat /tmp/out.json
