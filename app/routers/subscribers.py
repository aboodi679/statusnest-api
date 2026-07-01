from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Subscriber
from app.schemas import SubscriberCreate, SubscriberOut
from app.routers.auth import get_current_user
from app.models import User
from typing import List

router = APIRouter(prefix="/subscribers", tags=["subscribers"])


@router.post("", response_model=SubscriberOut, status_code=status.HTTP_201_CREATED)
def add_subscriber(payload: SubscriberCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Subscriber).filter(Subscriber.user_id == current_user.id, Subscriber.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already subscribed")
    subscriber = Subscriber(user_id=current_user.id, email=payload.email)
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber


@router.get("", response_model=List[SubscriberOut])
def list_subscribers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Subscriber).filter(Subscriber.user_id == current_user.id).all()
