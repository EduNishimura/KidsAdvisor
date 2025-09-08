from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.database import get_database
from app.auth import get_current_user
from app.services.recomendacao import RecomendacaoService
from app.models.gamificacao import RecomendacaoResponse

router = APIRouter()
recomendacao_service = RecomendacaoService()

@router.get("/{usuario_id}", response_model=List[RecomendacaoResponse])
async def obter_recomendacoes(
    usuario_id: str, 
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Obtém recomendações híbridas para o usuário"""
    db = get_database()
    
    # Verificar se o usuário existe
    usuario = await db.usuarios.find_one({"_id": usuario_id})
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Obter recomendações híbridas
    recomendacoes = await recomendacao_service.obter_recomendacoes_hibridas(usuario_id, limit)
    
    return recomendacoes

@router.get("/{usuario_id}/conteudo", response_model=List[RecomendacaoResponse])
async def obter_recomendacoes_conteudo(
    usuario_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Obtém recomendações baseadas em conteúdo"""
    db = get_database()
    
    # Verificar se o usuário existe
    usuario = await db.usuarios.find_one({"_id": usuario_id})
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Obter todos os eventos
    eventos = []
    async for evento in db.eventos.find():
        eventos.append(evento)
    
    # Obter recomendações de conteúdo
    recomendacoes_conteudo = await recomendacao_service._recomendacoes_por_conteudo(usuario, eventos)
    
    # Converter para formato de resposta
    recomendacoes = []
    eventos_dict = {str(evento["_id"]): evento for evento in eventos}
    
    for rec in recomendacoes_conteudo[:limit]:
        evento_id = rec["evento_id"]
        if evento_id in eventos_dict:
            evento = eventos_dict[evento_id]
            recomendacoes.append(RecomendacaoResponse(
                evento=EventoResponse(
                    id=str(evento["_id"]),
                    nome=evento["nome"],
                    descricao=evento["descricao"],
                    categoria=evento["categoria"],
                    localizacao=evento["localizacao"],
                    data=evento["data"],
                    idade_recomendada=evento["idade_recomendada"],
                    preco=evento["preco"],
                    organizadorId=evento["organizadorId"],
                    likes=evento["likes"],
                    data_criacao=evento.get("data_criacao")
                ),
                score=rec["score"],
                tipo="conteudo"
            ))
    
    return recomendacoes

@router.get("/{usuario_id}/colaborativo", response_model=List[RecomendacaoResponse])
async def obter_recomendacoes_colaborativas(
    usuario_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Obtém recomendações colaborativas baseadas em amigos"""
    db = get_database()
    
    # Verificar se o usuário existe
    usuario = await db.usuarios.find_one({"_id": usuario_id})
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Obter todos os eventos
    eventos = []
    async for evento in db.eventos.find():
        eventos.append(evento)
    
    # Obter recomendações colaborativas
    recomendacoes_colaborativas = await recomendacao_service._recomendacoes_colaborativas(usuario, eventos)
    
    # Converter para formato de resposta
    recomendacoes = []
    eventos_dict = {str(evento["_id"]): evento for evento in eventos}
    
    for rec in recomendacoes_colaborativas[:limit]:
        evento_id = rec["evento_id"]
        if evento_id in eventos_dict:
            evento = eventos_dict[evento_id]
            recomendacoes.append(RecomendacaoResponse(
                evento=EventoResponse(
                    id=str(evento["_id"]),
                    nome=evento["nome"],
                    descricao=evento["descricao"],
                    categoria=evento["categoria"],
                    localizacao=evento["localizacao"],
                    data=evento["data"],
                    idade_recomendada=evento["idade_recomendada"],
                    preco=evento["preco"],
                    organizadorId=evento["organizadorId"],
                    likes=evento["likes"],
                    data_criacao=evento.get("data_criacao")
                ),
                score=rec["score"],
                tipo="colaborativo"
            ))
    
    return recomendacoes
