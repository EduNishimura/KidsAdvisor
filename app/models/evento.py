from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict
from datetime import datetime


class Address(BaseModel):
    name: str
    address: Optional[str] = None
    address_num: Optional[str] = None
    address_alt: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    lon: Optional[str] = None
    lat: Optional[str] = None


class Host(BaseModel):
    name: str
    description: Optional[str] = None


class Category(BaseModel):
    name: str


class EventCreate(BaseModel):
    id: Optional[str] = None
    reference_id: Optional[int] = None
    name: str
    detail: Optional[str] = None
    start_date: datetime
    end_date: datetime
    private_event: Optional[int] = 0
    published: Optional[int] = 1
    cancelled: Optional[int] = 0
    image: Optional[HttpUrl] = None
    url: Optional[HttpUrl] = None
    address: Optional[Address] = None
    host: Optional[Host] = None
    category_prim: Optional[Category] = None
    category_sec: Optional[Category] = None
    organizer_id: str  # quem cadastrou no sistema


class EventOut(EventCreate):
    db_id: str = Field(..., alias="id")  # id interno do Mongo
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
