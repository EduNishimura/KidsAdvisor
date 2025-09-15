# --------------------
# File: app/models/usuario.py
# --------------------
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class Child(BaseModel):
    name: str
    age: int


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "parent"
    children: Optional[List[Child]] = []


class UserOut(BaseModel):
    id: str = Field(..., alias="id")
    name: str
    email: EmailStr
    role: str
    children: List[Child] = []
    friends: List[str] = []
    badges: List[str] = []
    level: int = 1
    xp: int = 0
    created_at: datetime


class Config:
    allow_population_by_field_name = True
    json_encoders = {datetime: lambda v: v.isoformat()}
