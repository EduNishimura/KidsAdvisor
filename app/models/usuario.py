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

class UsuarioBase(BaseModel):
    nome: str
    email: str
    tipo: str = Field(..., description="Tipo de usuário: 'pai' ou 'organizador'")

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)

class UsuarioLogin(BaseModel):
    email: str
    senha: str

class Usuario(UsuarioBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    senha: str
    amigos: List[str] = Field(default_factory=list)
    eventosCurtidos: List[str] = Field(default_factory=list)
    xp: int = Field(default=0)
    nivel: int = Field(default=1)
    badges: List[str] = Field(default_factory=list)
    data_criacao: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str
    tipo: str
    amigos: List[str]
    eventosCurtidos: List[str]
    xp: int
    nivel: int
    badges: List[str]
    data_criacao: datetime

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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class RecomendacaoResponse(BaseModel):
    evento: EventoResponse
    score: float
    tipo: str  # "conteudo" ou "colaborativo"

class ProgressoResponse(BaseModel):
    usuario_id: str
    xp: int
    nivel: int
    badges: List[str]
    proximo_nivel_xp: int
    eventos_curtidos: int

class LeaderboardEntry(BaseModel):
    usuario_id: str
    nome: str
    xp: int
    nivel: int
    posicao: int
