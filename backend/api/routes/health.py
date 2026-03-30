from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get('/health')
def health():
    return {'status': 'healthy', 'service': 'CloudPilot',
            'timestamp': datetime.now().isoformat()}
