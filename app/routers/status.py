import json
import redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models import User, Service, ServiceStatus
from app.config import settings

router = APIRouter(prefix="/status", tags=["status"])

# Redis client — decode_responses so we get strings back
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


# ── Response schemas ──────────────────────────────────────────────────────────

class ServiceStatusOut(BaseModel):
    service_id: UUID
    name: str
    url: str
    status: str           # "UP", "DOWN", or "UNKNOWN"
    response_time: Optional[float]
    checked_at: Optional[datetime]

    class Config:
        from_attributes = True


class StatusPageOut(BaseModel):
    username: str
    services: List[ServiceStatusOut]


class HistoryEntry(BaseModel):
    status: str
    response_time: Optional[float]
    checked_at: datetime

    class Config:
        from_attributes = True


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_user_by_email(db: Session, username: str) -> User:
    """Username on the status page = email prefix (part before @)."""
    user = db.query(User).filter(
        User.email.like(f"{username}@%"),
        ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Status page not found")
    return user


def get_status_from_redis(service_id: str) -> Optional[dict]:
    """Returns {"status": "UP", "response_time": 42.3, "checked_at": "..."} or None."""
    try:
        raw = redis_client.get(f"status:{service_id}")
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None


def get_latest_status_from_db(db: Session, service_id: UUID) -> Optional[ServiceStatus]:
    return (
        db.query(ServiceStatus)
        .filter(ServiceStatus.service_id == service_id)
        .order_by(ServiceStatus.checked_at.desc())
        .first()
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/{username}", response_model=StatusPageOut)
def get_status_page(username: str, db: Session = Depends(get_db)):
    """
    Public endpoint — no auth required.
    Returns current status of all active services for a user.
    Redis-first, RDS fallback.
    """
    user = get_user_by_email(db, username)
    services = (
        db.query(Service)
        .filter(Service.user_id == user.id, Service.is_active == True)
        .all()
    )

    result = []
    for svc in services:
        cached = get_status_from_redis(str(svc.id))

        if cached:
            result.append(ServiceStatusOut(
                service_id=svc.id,
                name=svc.name,
                url=svc.url,
                status=cached.get("status", "UNKNOWN"),
                response_time=cached.get("response_time"),
                checked_at=cached.get("checked_at"),
            ))
        else:
            # Redis miss — fall back to latest RDS row
            row = get_latest_status_from_db(db, svc.id)
            result.append(ServiceStatusOut(
                service_id=svc.id,
                name=svc.name,
                url=svc.url,
                status=row.status if row else "UNKNOWN",
                response_time=row.response_time if row else None,
                checked_at=row.checked_at if row else None,
            ))

    return StatusPageOut(username=username, services=result)


@router.get("/{username}/history/{service_id}", response_model=List[HistoryEntry])
def get_service_history(username: str, service_id: UUID, db: Session = Depends(get_db)):
    """
    Public endpoint — no auth required.
    Returns last 24h of status history for one service.
    """
    user = get_user_by_email(db, username)

    # Verify service belongs to this user
    svc = db.query(Service).filter(
        Service.id == service_id,
        Service.user_id == user.id,
        Service.is_active == True,
    ).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")

    rows = (
        db.query(ServiceStatus)
        .filter(ServiceStatus.service_id == service_id)
        .filter(text("checked_at >= NOW() - INTERVAL '24 hours'"))
        .order_by(ServiceStatus.checked_at.desc())
        .all()
    )

    return rows