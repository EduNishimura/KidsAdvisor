from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class EventoBase(BaseModel):
    nome: str
    descricao: str
    categoria: str
    localizacao: str
    data: datetime
    idade_recomendada: str
    preco: float
    organizadorId: str

class EventoCreate(EventoBase):
    pass

class Evento(EventoBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    likes: int = Field(default=0)
    data_criacao: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EventoResponse(BaseModel):
    id: str
    nome: str
    descricao: str
    categoria: str
    localizacao: str
    data: datetime
    idade_recomendada: str
    preco: float
    organizadorId: str
    likes: int
    data_criacao: datetime

class EventoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    localizacao: Optional[str] = None
    data: Optional[datetime] = None
    idade_recomendada: Optional[str] = None
    preco: Optional[float] = None
