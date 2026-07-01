from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.models import Incident, Service
from app.schemas import IncidentCreate, IncidentUpdate, IncidentOut
from app.routers.auth import get_current_user
from app.models import User
from typing import List

router = APIRouter(prefix="/incidents", tags=["incidents"])

VALID_STATUSES = {"investigating", "identified", "resolved"}


@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = db.query(Service).filter(Service.id == payload.service_id, Service.user_id == current_user.id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    incident = Incident(user_id=current_user.id, service_id=payload.service_id, title=payload.title, body=payload.body)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("", response_model=List[IncidentOut])
def list_incidents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Incident).filter(Incident.user_id == current_user.id).order_by(Incident.created_at.desc()).all()


@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(incident_id: UUID, payload: IncidentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {VALID_STATUSES}")
    incident = db.query(Incident).filter(Incident.id == incident_id, Incident.user_id == current_user.id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = payload.status
    if payload.body is not None:
        incident.body = payload.body
    db.commit()
    db.refresh(incident)
    return incident
