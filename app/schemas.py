from pydantic import BaseModel, EmailStr, HttpUrl
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Services
class ServiceCreate(BaseModel):
    name: str
    url: str

class ServiceOut(BaseModel):
    id: UUID
    name: str
    url: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True


# Incidents
class IncidentCreate(BaseModel):
    service_id: UUID
    title: str
    body: Optional[str] = None

class IncidentUpdate(BaseModel):
    status: str
    body: Optional[str] = None

class IncidentOut(BaseModel):
    id: UUID
    service_id: UUID
    title: str
    status: str
    body: Optional[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# Subscribers
class SubscriberCreate(BaseModel):
    email: EmailStr

class SubscriberOut(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True
