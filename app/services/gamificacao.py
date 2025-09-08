from typing import List, Dict
from app.database import get_database
from app.models.gamificacao import ProgressoResponse, LeaderboardEntry, BadgeInfo
from bson import ObjectId

class GamificacaoService:
    
    # Definição de badges
    BADGES = {
        "primeiro_evento": {
            "nome": "Primeiro Passo",
            "descricao": "Curtiu seu primeiro evento",
            "requisito": "1 evento curtido"
        },
        "explorador": {
            "nome": "Explorador",
            "descricao": "Curtiu 5 eventos diferentes",
            "requisito": "5 eventos curtidos"
        },
        "social": {
            "nome": "Social",
            "descricao": "Adicionou 3 amigos",
            "requisito": "3 amigos"
        },
        "veterano": {
            "nome": "Veterano",
            "descricao": "Curtiu 20 eventos",
            "requisito": "20 eventos curtidos"
        },
        "influencer": {
            "nome": "Influencer",
            "descricao": "Alcançou nível 10",
            "requisito": "Nível 10"
        }
    }
    
    # XP necessário para cada nível
    XP_POR_NIVEL = {
        1: 0,
        2: 100,
        3: 250,
        4: 450,
        5: 700,
        6: 1000,
        7: 1350,
        8: 1750,
        9: 2200,
        10: 2700,
        11: 3250,
        12: 3850,
        13: 4500,
        14: 5200,
        15: 5950,
        16: 6750,
        17: 7600,
        18: 8500,
        19: 9450,
        20: 10450
    }
    
    async def calcular_nivel(self, xp: int) -> int:
        """Calcula o nível baseado no XP"""
        nivel = 1
        for nivel_atual, xp_necessario in self.XP_POR_NIVEL.items():
            if xp >= xp_necessario:
                nivel = nivel_atual
            else:
                break
        return nivel
    
    async def obter_proximo_nivel_xp(self, nivel_atual: int) -> int:
        """Obtém o XP necessário para o próximo nível"""
        proximo_nivel = nivel_atual + 1
        if proximo_nivel in self.XP_POR_NIVEL:
            return self.XP_POR_NIVEL[proximo_nivel]
        return self.XP_POR_NIVEL[20]  # Máximo nível
    
    async def verificar_badges(self, usuario_id: str) -> List[str]:
        """Verifica e concede badges para o usuário"""
        db = get_database()
        usuario = await db.usuarios.find_one({"_id": usuario_id})
        if not usuario:
            return []
        
        novos_badges = []
        badges_atuais = usuario.get("badges", [])
        
        # Verificar badge "primeiro_evento"
        if "primeiro_evento" not in badges_atuais and len(usuario.get("eventosCurtidos", [])) >= 1:
            novos_badges.append("primeiro_evento")
        
        # Verificar badge "explorador"
        if "explorador" not in badges_atuais and len(usuario.get("eventosCurtidos", [])) >= 5:
            novos_badges.append("explorador")
        
        # Verificar badge "social"
        if "social" not in badges_atuais and len(usuario.get("amigos", [])) >= 3:
            novos_badges.append("social")
        
        # Verificar badge "veterano"
        if "veterano" not in badges_atuais and len(usuario.get("eventosCurtidos", [])) >= 20:
            novos_badges.append("veterano")
        
        # Verificar badge "influencer"
        nivel_atual = await self.calcular_nivel(usuario.get("xp", 0))
        if "influencer" not in badges_atuais and nivel_atual >= 10:
            novos_badges.append("influencer")
        
        # Adicionar novos badges ao usuário
        if novos_badges:
            await db.usuarios.update_one(
                {"_id": usuario_id},
                {"$addToSet": {"badges": {"$each": novos_badges}}}
            )
        
        return novos_badges
    
    async def atualizar_nivel_usuario(self, usuario_id: str) -> int:
        """Atualiza o nível do usuário baseado no XP"""
        db = get_database()
        usuario = await db.usuarios.find_one({"_id": usuario_id})
        if not usuario:
            return 1
        
        xp_atual = usuario.get("xp", 0)
        novo_nivel = await self.calcular_nivel(xp_atual)
        
        # Atualizar nível no banco
        await db.usuarios.update_one(
            {"_id": usuario_id},
            {"$set": {"nivel": novo_nivel}}
        )
        
        return novo_nivel
    
    async def obter_progresso_usuario(self, usuario_id: str) -> ProgressoResponse:
        """Obtém o progresso completo do usuário"""
        db = get_database()
        usuario = await db.usuarios.find_one({"_id": usuario_id})
        if not usuario:
            return None
        
        xp = usuario.get("xp", 0)
        nivel = await self.calcular_nivel(xp)
        proximo_nivel_xp = await self.obter_proximo_nivel_xp(nivel)
        eventos_curtidos = len(usuario.get("eventosCurtidos", []))
        badges = usuario.get("badges", [])
        
        return ProgressoResponse(
            usuario_id=str(usuario["_id"]),
            xp=xp,
            nivel=nivel,
            badges=badges,
            proximo_nivel_xp=proximo_nivel_xp,
            eventos_curtidos=eventos_curtidos
        )
    
    async def obter_leaderboard(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Obtém o ranking dos usuários"""
        db = get_database()
        
        usuarios = []
        async for usuario in db.usuarios.find().sort("xp", -1).limit(limit):
            usuarios.append(LeaderboardEntry(
                usuario_id=str(usuario["_id"]),
                nome=usuario["nome"],
                xp=usuario.get("xp", 0),
                nivel=await self.calcular_nivel(usuario.get("xp", 0)),
                posicao=0  # Será definido abaixo
            ))
        
        # Definir posições
        for i, usuario in enumerate(usuarios):
            usuario.posicao = i + 1
        
        return usuarios
    
    async def obter_badges_disponiveis(self, usuario_id: str) -> List[BadgeInfo]:
        """Obtém informações sobre todos os badges disponíveis"""
        db = get_database()
        usuario = await db.usuarios.find_one({"_id": usuario_id})
        if not usuario:
            return []
        
        badges_conquistados = usuario.get("badges", [])
        badges_info = []
        
        for badge_id, badge_data in self.BADGES.items():
            badges_info.append(BadgeInfo(
                nome=badge_data["nome"],
                descricao=badge_data["descricao"],
                requisito=badge_data["requisito"],
                conquistado=badge_id in badges_conquistados
            ))
        
        return badges_info
