from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        return {"type": "string"}

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
        populate_by_name = True
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
