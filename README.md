# ☁ CloudPilot — AI-Powered Cloud Cost Optimization Platform

<div align="center">

![CloudPilot](https://img.shields.io/badge/CloudPilot-AI%20Cost%20Optimizer-blue?style=for-the-badge&logo=amazonaws)
![Live](https://img.shields.io/badge/LIVE-www.pilotcost.online-brightgreen?style=for-the-badge)
![EKS](https://img.shields.io/badge/AWS-EKS%20Spot-orange?style=for-the-badge&logo=amazonaws)
![Jenkins](https://img.shields.io/badge/CI%2FCD-Jenkins-red?style=for-the-badge&logo=jenkins)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple?style=for-the-badge&logo=terraform)

**🌐 Live Demo: [www.pilotcost.online](http://www.pilotcost.online)**

*AI-powered platform that monitors AWS infrastructure in real time, detects wasted resources, predicts future costs, and automatically executes fixes using serverless Lambda functions.*

</div>

---

## 🏗️ Full Architecture

```
Developer pushes code to GitHub
        │
        ▼  (webhook triggers)
┌─────────────────────────────────────────┐
│         Jenkins CI/CD Pipeline          │
│                                         │
│  Stage 1:  Checkout from GitHub         │
│  Stage 2:  Docker Build (backend+front) │
│  Stage 3:  Trivy Security Scan          │
│  Stage 4:  Push to DockerHub            │
│  Stage 5:  Terraform Apply              │
│  Stage 6:  Configure kubectl            │
│  Stage 7:  Namespace + Secrets          │
│  Stage 8:  Nginx Ingress Controller     │
│  Stage 9:  ELK Stack Deploy             │
│  Stage 10: ArgoCD + Prometheus/Grafana  │
│  Stage 11: Helm Deploy                  │
│  Stage 12: Health Check + Auto-Rollback │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│   AWS EKS Cluster — ap-south-1          │
│   Spot Instances (70% cheaper)          │
│                                         │
│  [cloudpilot namespace]                 │
│    FastAPI Backend  ← REST API          │
│    React Dashboard  ← UI               │
│                                         │
│  [data-pipeline]                        │
│    EventBridge (hourly)                 │
│      → Lambda: cost_collector           │
│      → SQS Queue                        │
│      → Lambda: anomaly_detector         │
│      → DynamoDB Tables                  │
│      → Groq AI Analysis                 │
│      → Recommendations saved            │
│                                         │
│  [monitoring namespace]                 │
│    Prometheus + Grafana + Alertmanager  │
│                                         │
│  [logging namespace]                    │
│    Elasticsearch + Kibana + Filebeat    │
│                                         │
│  [argocd namespace]                     │
│    ArgoCD GitOps Controller             │
│                                         │
│  Nginx Ingress ← Single AWS ELB         │
└─────────────────────────────────────────┘
        │
        ▼
www.pilotcost.online        grafana.pilotcost.online
kibana.pilotcost.online     argocd.pilotcost.online
```

---

## ⚡ Auto-Fix Flow

```
User clicks "Apply Fix" on Dashboard
        │
        ▼
FastAPI: POST /api/actions/execute
        │
        ▼
Lambda: cloudpilot-auto-fixer
        │
   ┌────┴────────────────┐
   ▼         ▼           ▼
Resize EC2  Delete EBS  Change S3
Instance    Volume      Storage Class
   │
   ▼
Audit log → DynamoDB
   │
   ▼
Result shown on Dashboard ✅
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend API** | FastAPI (Python) | Async, auto OpenAPI docs |
| **Frontend** | React + Recharts | Interactive dashboards |
| **Database** | AWS DynamoDB | Serverless, free tier |
| **Queue** | AWS SQS | Decoupled data pipeline |
| **Functions** | AWS Lambda | Serverless auto-fixes |
| **AI Engine** | Groq (llama-3.3-70b) | Free, fast LLM analysis |
| **Containers** | Docker multi-stage | Minimal image size |
| **Orchestration** | AWS EKS + Spot | 70% cost saving |
| **CI/CD** | Jenkins (12 stages) | Self-hosted, full control |
| **IaC** | Terraform + Terragrunt | DRY infrastructure code |
| **GitOps** | ArgoCD | Git as source of truth |
| **Monitoring** | Prometheus + Grafana | Metrics + dashboards |
| **Logging** | ELK Stack | Centralized logs |
| **Ingress** | Nginx Ingress | Single ELB for all services |
| **Secrets** | K8s Secrets + IAM Role | Never stored in code |
| **Security** | Trivy image scanning | HIGH/CRITICAL blocks deploy |
| **Cloud** | AWS ap-south-1 | Mumbai region |

---

## 📁 Project Structure

```
cloudpilot/
├── backend/
│   ├── api/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── routes/
│   │   │   ├── costs.py            # GET /api/costs
│   │   │   ├── recommendations.py  # GET /api/recommendations
│   │   │   ├── actions.py          # POST /api/actions/execute
│   │   │   ├── forecast.py         # GET /api/forecast
│   │   │   └── health.py           # GET /health
│   │   └── services/
│   │       ├── aws_cost.py         # Cost Explorer client
│   │       ├── ai_engine.py        # Groq AI analysis
│   │       ├── dynamo.py           # DynamoDB client
│   │       └── optimizer.py        # Fix executor
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   └── App.js                  # React dashboard
│   └── Dockerfile
│
├── lambdas/
│   ├── cost_collector/handler.py   # Pulls Cost Explorer hourly
│   ├── anomaly_detector/handler.py # Detects unusual spending
│   └── auto_fixer/handler.py       # Executes optimizations
│
├── infrastructure/
│   └── terraform/
│       ├── main.tf                 # VPC + EKS + DynamoDB + Lambda + SQS
│       └── variables.tf
│
├── helm/cloudpilot/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       └── hpa.yaml
│
├── elk/
│   ├── 01-elasticsearch.yaml
│   ├── 02-logstash.yaml
│   ├── 03-kibana.yaml
│   └── 04-filebeat.yaml
│
├── k8s/monitoring/
│   └── alertmanager-rules.yaml
│
└── Jenkinsfile                     # 12-stage pipeline
```

---

## 🚀 Features

### 💰 Cost Monitoring
- Pulls AWS Cost Explorer data every hour via EventBridge + Lambda
- Real-time cost breakdown by service (EC2, EKS, Lambda, DynamoDB, NAT Gateway)
- 30/60/90 day cost forecasting

### 🤖 AI Analysis
- Groq LLM (llama-3.3-70b) analyzes real AWS cost data
- Identifies idle EC2 instances, oversized resources, unused EBS volumes
- Generates specific recommendations with exact dollar savings

### ⚡ Auto-Fix Engine
- One-click executes fixes via Lambda
- Resizes EC2 instances (stop → resize → start)
- Deletes unused EBS volumes
- Changes S3 storage class to Intelligent-Tiering
- Full audit trail saved to DynamoDB

### 📊 Observability Stack
- **Prometheus** — scrapes `/metrics` every 15s
- **Grafana** — dashboards for pod CPU, memory, request rate
- **Alertmanager** — Slack alerts on pod crashes, high CPU, app down
- **ELK Stack** — centralized logs from all pods via Filebeat DaemonSet
- **ArgoCD** — GitOps, auto-syncs K8s to GitHub state

---

## 📊 Monthly Cost (Self-Optimized!)

| Resource | Cost | Optimization |
|----------|------|-------------|
| EKS Control Plane | $72 | Cannot avoid |
| EC2 Spot Instances (2x t3.large) | ~$18 | Spot = 70% cheaper |
| AWS Lambda | $0 | Free tier |
| DynamoDB | $0 | Free tier |
| NAT Gateway | ~$32 | Single NAT (saves $32/mo) |
| **Total** | **~$122/mo** | vs $200+ without optimization |

> 💡 *CloudPilot finds $150-300/month in savings on a typical AWS account — it pays for itself!*

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check for K8s probes |
| GET | `/docs` | Swagger UI — auto-generated |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/costs/summary` | Real AWS cost breakdown |
| GET | `/api/recommendations` | AI-generated savings suggestions |
| POST | `/api/recommendations/refresh` | Re-run AI analysis |
| POST | `/api/actions/execute` | Execute auto-fix via Lambda |
| GET | `/api/audit` | History of all executed fixes |

---

## ⚙️ CI/CD Pipeline (12 Stages)

```
Stage 1:  Checkout          → Pull from GitHub
Stage 2:  Docker Build      → Build backend + frontend images
Stage 3:  Trivy Scan        → Security scan (HIGH/CRITICAL blocks)
Stage 4:  Push DockerHub    → Push with BUILD_NUMBER tag
Stage 5:  Terraform         → Provision VPC, EKS, DynamoDB, Lambda, SQS
Stage 6:  Configure kubectl → Connect Jenkins to EKS cluster
Stage 7:  Secrets           → Inject GROQ_API_KEY into K8s
Stage 8:  Nginx Ingress     → Install/verify ingress controller
Stage 9:  ELK Stack         → Deploy Elasticsearch, Kibana, Filebeat
Stage 10: ArgoCD+Monitoring → Deploy ArgoCD, Prometheus, Grafana
Stage 11: Helm Deploy       → Deploy CloudPilot app with atomic flag
Stage 12: Health Check      → Verify /health returns 200, auto-rollback on fail
```

---

## 🏃 Running Locally

```bash
# Clone repo
git clone https://github.com/salmonstone/cloudpilot.git
cd cloudpilot

# Backend
cd backend/api
pip3 install -r requirements.txt
export GROQ_API_KEY=your_groq_key
export AWS_DEFAULT_REGION=ap-south-1
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm start
```

- Backend: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

---

## 🌐 Live URLs

| Service | URL |
|---------|-----|
| Dashboard | http://www.pilotcost.online |
| API Docs | http://www.pilotcost.online/docs |
| Health | http://www.pilotcost.online/health |
| Grafana | http://grafana.pilotcost.online |
| Kibana | http://kibana.pilotcost.online |
| ArgoCD | http://argocd.pilotcost.online |

---

## 👤 Author

**Aryan Singh Chauhan**
- GitHub: [@salmonstone](https://github.com/salmonstone)
- DockerHub: [salmonstone](https://hub.docker.com/u/salmonstone)
- Email: arysingh9832@gmail.com
- Target Role: DevOps Engineer

---

## 🔗 Related Projects

- **InfraGPT** (Phase 1) — AI-powered DevOps chatbot: [www.infragpt.online](http://www.infragpt.online)
- **CloudPilot** (Phase 2) — This project: [www.pilotcost.online](http://www.pilotcost.online)

---

<div align="center">

*Built with ❤️ to solve real problems. Every line of infrastructure was written, broken, debugged, and fixed.*

⭐ Star this repo if it helped you!

</div>

