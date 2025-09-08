from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.database import get_database
from app.auth import get_current_user
from app.services.gamificacao import GamificacaoService
from app.models.gamificacao import ProgressoResponse, LeaderboardEntry, BadgeInfo

router = APIRouter()
gamificacao_service = GamificacaoService()

@router.get("/usuarios/{usuario_id}/progresso", response_model=ProgressoResponse)
async def obter_progresso_usuario(
    usuario_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém o progresso completo do usuário"""
    db = get_database()
    
    # Verificar se o usuário existe
    usuario = await db.usuarios.find_one({"_id": usuario_id})
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Obter progresso
    progresso = await gamificacao_service.obter_progresso_usuario(usuario_id)
    
    return progresso

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def obter_leaderboard(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Obtém o ranking dos usuários"""
    leaderboard = await gamificacao_service.obter_leaderboard(limit)
    return leaderboard

@router.get("/usuarios/{usuario_id}/badges", response_model=List[BadgeInfo])
async def obter_badges_usuario(
    usuario_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém informações sobre badges do usuário"""
    db = get_database()
    
    # Verificar se o usuário existe
    usuario = await db.usuarios.find_one({"_id": usuario_id})
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Obter badges
    badges = await gamificacao_service.obter_badges_disponiveis(usuario_id)
    
    return badges

@router.post("/usuarios/{usuario_id}/verificar-badges")
async def verificar_badges_usuario(
    usuario_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Verifica e concede novos badges para o usuário"""
    db = get_database()
    
    # Verificar se o usuário existe
    usuario = await db.usuarios.find_one({"_id": usuario_id})
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar badges
    novos_badges = await gamificacao_service.verificar_badges(usuario_id)
    
    # Atualizar nível
    novo_nivel = await gamificacao_service.atualizar_nivel_usuario(usuario_id)
    
    return {
        "novos_badges": novos_badges,
        "novo_nivel": novo_nivel,
        "message": f"Conquistados {len(novos_badges)} novos badges!"
    }

@router.get("/usuarios/{usuario_id}/nivel")
async def obter_nivel_usuario(
    usuario_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém informações sobre o nível do usuário"""
    db = get_database()
    
    # Verificar se o usuário existe
    usuario = await db.usuarios.find_one({"_id": usuario_id})
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    xp = usuario.get("xp", 0)
    nivel_atual = await gamificacao_service.calcular_nivel(xp)
    proximo_nivel_xp = await gamificacao_service.obter_proximo_nivel_xp(nivel_atual)
    xp_necessario = proximo_nivel_xp - xp
    
    return {
        "nivel_atual": nivel_atual,
        "xp_atual": xp,
        "proximo_nivel_xp": proximo_nivel_xp,
        "xp_necessario": xp_necessario,
        "progresso_percentual": (xp / proximo_nivel_xp) * 100 if proximo_nivel_xp > 0 else 100
    }
