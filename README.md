# StatusNest API

<img width="955" height="470" alt="Screenshot 2026-07-03 144934" src="https://github.com/user-attachments/assets/46aea6a3-e806-4f61-804a-3dc4f9260b8f" />


> Hosted Status Page SaaS on AWS — like statuspage.io

A production-grade, multi-tenant status page platform built with FastAPI and deployed on AWS ECS Fargate. Companies sign up, add their services, and StatusNest monitors them every 60 seconds and serves a live public status page.

**Live Demo:** http://statusnest-dev-frontend.s3-website.us-east-1.amazonaws.com

---

## Architecture

```
ALB (Application Load Balancer)
├── /auth/*         → Auth Service        (Port 8000, ECS Fargate)
├── /api/monitor/*  → Monitor API Service (Port 8001, ECS Fargate)
└── /status/*       → Status Page Service (Port 8002, ECS Fargate)
          ↓
PostgreSQL RDS + ElastiCache Redis
          ↑
EventBridge (60s) → Lambda Monitor Worker → SQS → Lambda Processor
```

---

## Microservices

### Auth Service — `/auth/*`
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create tenant account |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/me` | Current user profile |

### Monitor API — `/api/monitor/*`
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/monitor/services` | Add a service to monitor |
| GET | `/api/monitor/services` | List all services |
| DELETE | `/api/monitor/services/{id}` | Remove a service |
| POST | `/api/monitor/incidents` | Create an incident |
| PATCH | `/api/monitor/incidents/{id}` | Update incident status |
| POST | `/api/monitor/subscribers` | Subscribe email to alerts |
| GET | `/api/monitor/subscribers` | List subscribers |

### Status Page — `/status/*`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/status/{username}` | Public status page (Redis-first) |
| GET | `/status/{username}/history/{service_id}` | 24h history |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Framework | FastAPI + Uvicorn |
| Database | PostgreSQL (AWS RDS) |
| Cache | ElastiCache Redis |
| Auth | JWT via python-jose |
| Tracing | AWS X-Ray |
| Containers | Docker + ECR + ECS Fargate |
| CI/CD | GitHub Actions + OIDC (zero stored keys) |
| Secrets | AWS Secrets Manager |

---

## Project Structure

```
statusnest-api/
├── app/
│   ├── routers/
│   │   ├── auth.py          # Auth endpoints
│   │   ├── services.py      # Service CRUD
│   │   ├── incidents.py     # Incident management
│   │   ├── subscribers.py   # Email subscribers
│   │   └── status.py        # Public status page
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # DB connection
│   ├── config.py            # Settings
│   └── security.py          # JWT helpers
├── main.py                  # Auth service entrypoint
├── main_monitor.py          # Monitor service entrypoint
├── main_status.py           # Status page entrypoint
├── Dockerfile               # Auth service
├── Dockerfile.monitor       # Monitor service
├── Dockerfile.status        # Status service
├── requirements.txt
└── .github/
    └── workflows/
        ├── deploy.yml           # Auth CI/CD
        ├── deploy-monitor.yml   # Monitor CI/CD
        └── deploy-status.yml    # Status CI/CD
```

---

## Local Development

### Prerequisites
- Python 3.11
- PostgreSQL
- Redis

### Setup

```bash
git clone https://github.com/aboodi679/statusnest-api
cd statusnest-api
pip install -r requirements.txt
```

Create `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost:5432/statusnest
JWT_SECRET=your-secret-key
REDIS_URL=redis://localhost:6379
```

Run auth service:
```bash
uvicorn main:app --reload --port 8000
```

Run monitor service:
```bash
uvicorn main_monitor:app --reload --port 8001
```

Run status page service:
```bash
uvicorn main_status:app --reload --port 8002
```

---

## CI/CD

Every push to `main` automatically:
1. Builds Docker image
2. Pushes to Amazon ECR
3. Updates ECS task definition
4. Deploys to ECS Fargate (zero downtime rolling update)

Uses GitHub Actions OIDC — no AWS keys stored anywhere.

---

## Related Repos

| Repo | Description |
|------|-------------|
| [statusnest-infra](https://github.com/aboodi679/statusnest-infra) | Terraform IaC — all AWS resources |
| [statusnest-worker](https://github.com/aboodi679/statusnest-worker) | Lambda monitor + processor |
| [statusnest-frontend](https://github.com/aboodi679/statusnest-frontend) | React dashboard |

---

*Built by [Muhammad Abdullah](https://github.com/aboodi679) · Powered by AWS*
