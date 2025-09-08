import pytest
from app.services.recomendacao import RecomendacaoService
from app.services.gamificacao import GamificacaoService

class TestRecomendacaoService:
    def test_init(self):
        """Test service initialization"""
        service = RecomendacaoService()
        assert service.vectorizer is not None

class TestGamificacaoService:
    def test_calcular_nivel(self):
        """Test level calculation"""
        service = GamificacaoService()
        
        # Test level 1
        assert service.calcular_nivel(0) == 1
        assert service.calcular_nivel(50) == 1
        
        # Test level 2
        assert service.calcular_nivel(100) == 2
        assert service.calcular_nivel(200) == 2
        
        # Test level 3
        assert service.calcular_nivel(250) == 3
        assert service.calcular_nivel(400) == 3

    def test_obter_proximo_nivel_xp(self):
        """Test next level XP calculation"""
        service = GamificacaoService()
        
        # Test level 1 -> 2
        assert service.obter_proximo_nivel_xp(1) == 100
        
        # Test level 2 -> 3
        assert service.obter_proximo_nivel_xp(2) == 250
        
        # Test max level
        assert service.obter_proximo_nivel_xp(20) == 10450

    def test_badges_definidos(self):
        """Test badges are properly defined"""
        service = GamificacaoService()
        
        assert "primeiro_evento" in service.BADGES
        assert "explorador" in service.BADGES
        assert "social" in service.BADGES
        assert "veterano" in service.BADGES
        assert "influencer" in service.BADGES
        
        # Test badge structure
        for badge_id, badge_data in service.BADGES.items():
            assert "nome" in badge_data
            assert "descricao" in badge_data
            assert "requisito" in badge_data
