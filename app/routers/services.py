from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.models import Service
from app.schemas import ServiceCreate, ServiceOut
from app.routers.auth import get_current_user
from app.models import User
from typing import List

router = APIRouter(prefix="/services", tags=["services"])


@router.post("", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = Service(user_id=current_user.id, name=payload.name, url=payload.url)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("", response_model=List[ServiceOut])
def list_services(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Service).filter(Service.user_id == current_user.id, Service.is_active == True).all()


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = db.query(Service).filter(Service.id == service_id, Service.user_id == current_user.id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.is_active = False
    db.commit()
