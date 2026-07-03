# StatusNest API

FastAPI backend for the StatusNest multi-tenant service monitoring platform. Three independently deployed microservices running on AWS ECS Fargate behind an Application Load Balancer.

---

## Services

| Service | Port | Responsibility |
|---|---|---|
| `auth` | 8000 | User registration, login, JWT issuance |
| `monitor` | 8001 | Services CRUD, incidents, subscribers |
| `status` | 8002 | Public status page (Redis-first, RDS fallback) |

All three are routed through CloudFront → ALB using path-based routing.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL (AWS RDS) |
| Cache | Redis (AWS ElastiCache) |
| Auth | JWT (python-jose) + bcrypt |
| Tracing | AWS X-Ray SDK |
| Container | Docker → AWS ECR → ECS Fargate |

---

## API Endpoints

### Auth — `/auth`
```
POST /auth/register       # Create account
POST /auth/login          # Returns JWT access token
GET  /auth/me             # Current user info (requires Bearer token)
```

### Monitor — `/api/monitor`
```
GET    /api/monitor/services           # List active services
POST   /api/monitor/services           # Add service
DELETE /api/monitor/services/{id}      # Soft-delete service

GET    /api/monitor/incidents          # List incidents
POST   /api/monitor/incidents          # Create incident
PATCH  /api/monitor/incidents/{id}     # Update incident status

GET    /api/monitor/subscribers        # List subscribers
POST   /api/monitor/subscribers        # Add subscriber
```

### Status — `/api/status`
```
GET /api/status/{username}                        # Public status page data
GET /api/status/{username}/history/{service_id}   # 24h history for a service
```

---

## Infrastructure

```
CloudFront
  /auth/*  → ALB → auth ECS service  (port 8000)
  /api/*   → ALB → monitor / status  (ports 8001, 8002)
```

| Resource | Value |
|---|---|
| ECS Cluster | `statusnest-dev-cluster` |
| ALB | `statusnest-dev-alb-1293848550.us-east-1.elb.amazonaws.com` |
| RDS | `statusnest-dev-db.c2hcyc4yyuxy.us-east-1.rds.amazonaws.com` |
| Redis | `statusnest-dev-redis.b8x2ra.0001.use1.cache.amazonaws.com:6379` |
| Region | `us-east-1` |

---

## Environment Variables

Each service reads from AWS Secrets Manager / ECS task definition environment:

```
DATABASE_URL      postgresql://user:pass@host:5432/statusnest
REDIS_URL         redis://host:6379
JWT_SECRET        <secret>
```

---

## CI/CD

GitHub Actions with OIDC (no long-lived AWS keys):
1. Build Docker image
2. Push to ECR
3. Update ECS service (force new deployment)

Role: `arn:aws:iam::026243800492:role/statusnest-dev-github-actions-role`

---

## Related Repos

| Repo | Description |
|---|---|
| [statusnest-frontend](https://github.com/aboodi679/statusnest-frontend) | React SPA |
| [statusnest-worker](https://github.com/aboodi679/statusnest-worker) | Lambda monitor + SQS processor |
| [statusnest-infra](https://github.com/aboodi679/statusnest-infra) | Terraform IaC for all AWS infrastructure |
