from pydantic import BaseModel
from typing import List
from app.models.evento import EventoResponse

class RecomendacaoResponse(BaseModel):
    evento: EventoResponse
    score: float
    tipo: str  # "conteudo", "colaborativo" ou "hibrida"

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

class BadgeInfo(BaseModel):
    nome: str
    descricao: str
    requisito: str
    conquistado: bool = False
