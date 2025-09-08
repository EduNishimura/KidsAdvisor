#!/usr/bin/env python3
"""
🔍 Script de Debug - KidsAdvisor API
Debug específico de cada componente da aplicação
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Debugger:
    def __init__(self):
        self.results = []
    
    def log(self, message: str, status: str = "INFO"):
        """Log com cores"""
        colors = {
            "SUCCESS": '\033[0;32m',
            "ERROR": '\033[0;31m',
            "WARNING": '\033[1;33m',
            "INFO": '\033[0;34m',
            "NC": '\033[0m'
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = colors.get(status, colors["INFO"])
        print(f"{color}🔍 [{timestamp}] {message}{colors['NC']}")
    
    async def debug_database(self):
        """Debug da conexão MongoDB"""
        self.log("=== DEBUG: CONEXÃO MONGODB ===", "INFO")
        
        try:
            from app.database import connect_to_mongo, get_database, close_mongo_connection
            
            # Testar conexão
            self.log("Testando conexão com MongoDB...")
            await connect_to_mongo()
            db = get_database()
            
            # Testar operações básicas
            self.log("Testando operações básicas...")
            
            # Inserir documento de teste
            test_doc = {
                "test": "debug",
                "timestamp": datetime.utcnow(),
                "data": {"debug": True}
            }
            
            result = await db.debug_test.insert_one(test_doc)
            self.log(f"✅ Inserção OK: {result.inserted_id}", "SUCCESS")
            
            # Buscar documento
            doc = await db.debug_test.find_one({"_id": result.inserted_id})
            if doc:
                self.log(f"✅ Busca OK: {doc['test']}", "SUCCESS")
            else:
                self.log("❌ Busca falhou", "ERROR")
            
            # Contar documentos
            count = await db.debug_test.count_documents({})
            self.log(f"✅ Contagem OK: {count} documentos", "SUCCESS")
            
            # Limpar teste
            await db.debug_test.delete_one({"_id": result.inserted_id})
            self.log("✅ Limpeza OK", "SUCCESS")
            
            # Verificar dados existentes
            users_count = await db.usuarios.count_documents({})
            events_count = await db.eventos.count_documents({})
            
            self.log(f"📊 Dados existentes:", "INFO")
            self.log(f"   👥 Usuários: {users_count}", "INFO")
            self.log(f"   🎪 Eventos: {events_count}", "INFO")
            
            await close_mongo_connection()
            self.log("✅ Conexão MongoDB OK", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro na conexão MongoDB: {str(e)}", "ERROR")
            return False
    
    async def debug_auth(self):
        """Debug do sistema de autenticação"""
        self.log("=== DEBUG: SISTEMA DE AUTENTICAÇÃO ===", "INFO")
        
        try:
            from app.auth import (
                get_password_hash, 
                verify_password, 
                create_access_token,
                authenticate_user
            )
            from app.database import connect_to_mongo, get_database
            
            # Testar hash de senha
            self.log("Testando hash de senha...")
            password = "teste123"
            hashed = get_password_hash(password)
            self.log(f"✅ Hash gerado: {hashed[:30]}...", "SUCCESS")
            
            # Testar verificação
            is_valid = verify_password(password, hashed)
            if is_valid:
                self.log("✅ Verificação de senha OK", "SUCCESS")
            else:
                self.log("❌ Verificação de senha falhou", "ERROR")
            
            # Testar token JWT
            self.log("Testando criação de token JWT...")
            token = create_access_token(
                {"sub": "test_user"}, 
                timedelta(minutes=30)
            )
            self.log(f"✅ Token gerado: {token[:50]}...", "SUCCESS")
            
            # Testar decodificação
            from jose import jwt
            payload = jwt.decode(
                token, 
                "your-super-secret-key-change-in-production", 
                algorithms=["HS256"]
            )
            self.log(f"✅ Token decodificado: {payload}", "SUCCESS")
            
            # Testar autenticação com usuário real
            self.log("Testando autenticação com usuário real...")
            await connect_to_mongo()
            db = get_database()
            
            # Buscar usuário de exemplo
            user = await db.usuarios.find_one({"email": "maria@gmail.com"})
            if user:
                auth_result = await authenticate_user("maria@gmail.com", "123456")
                if auth_result:
                    self.log("✅ Autenticação com usuário real OK", "SUCCESS")
                else:
                    self.log("❌ Autenticação com usuário real falhou", "ERROR")
            else:
                self.log("⚠️ Usuário de exemplo não encontrado", "WARNING")
            
            self.log("✅ Sistema de autenticação OK", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no sistema de autenticação: {str(e)}", "ERROR")
            return False
    
    async def debug_recommendations(self):
        """Debug do sistema de recomendações"""
        self.log("=== DEBUG: SISTEMA DE RECOMENDAÇÕES ===", "INFO")
        
        try:
            from app.services.recomendacao import RecomendacaoService
            from app.database import connect_to_mongo, get_database
            
            await connect_to_mongo()
            db = get_database()
            
            # Obter usuário de teste
            user = await db.usuarios.find_one({"email": "maria@gmail.com"})
            if not user:
                self.log("❌ Usuário de teste não encontrado", "ERROR")
                return False
            
            self.log(f"👤 Usuário: {user['nome']}", "INFO")
            self.log(f"📝 Eventos curtidos: {len(user.get('eventosCurtidos', []))}", "INFO")
            self.log(f"👥 Amigos: {len(user.get('amigos', []))}", "INFO")
            
            # Obter todos os eventos
            eventos = []
            async for evento in db.eventos.find():
                eventos.append(evento)
            
            self.log(f"🎪 Total de eventos: {len(eventos)}", "INFO")
            
            # Testar serviço de recomendações
            service = RecomendacaoService()
            
            # Testar recomendações de conteúdo
            self.log("Testando recomendações baseadas em conteúdo...")
            try:
                content_recs = await service._recomendacoes_por_conteudo(user, eventos)
                self.log(f"✅ Recomendações de conteúdo: {len(content_recs)}", "SUCCESS")
                
                for i, rec in enumerate(content_recs[:3]):
                    self.log(f"   {i+1}. Score: {rec['score']:.3f}")
                    
            except Exception as e:
                self.log(f"❌ Erro em recomendações de conteúdo: {str(e)}", "ERROR")
            
            # Testar recomendações colaborativas
            self.log("Testando recomendações colaborativas...")
            try:
                collab_recs = await service._recomendacoes_colaborativas(user, eventos)
                self.log(f"✅ Recomendações colaborativas: {len(collab_recs)}", "SUCCESS")
                
                for i, rec in enumerate(collab_recs[:3]):
                    self.log(f"   {i+1}. Score: {rec['score']:.3f}")
                    
            except Exception as e:
                self.log(f"❌ Erro em recomendações colaborativas: {str(e)}", "ERROR")
            
            # Testar recomendações híbridas
            self.log("Testando recomendações híbridas...")
            try:
                hybrid_recs = await service.obter_recomendacoes_hibridas(str(user["_id"]), 5)
                self.log(f"✅ Recomendações híbridas: {len(hybrid_recs)}", "SUCCESS")
                
                for i, rec in enumerate(hybrid_recs[:3]):
                    evento_nome = rec.evento.nome
                    score = rec.score
                    tipo = rec.tipo
                    self.log(f"   {i+1}. {evento_nome} (Score: {score:.3f}, Tipo: {tipo})")
                    
            except Exception as e:
                self.log(f"❌ Erro em recomendações híbridas: {str(e)}", "ERROR")
            
            self.log("✅ Sistema de recomendações OK", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no sistema de recomendações: {str(e)}", "ERROR")
            return False
    
    async def debug_gamification(self):
        """Debug do sistema de gamificação"""
        self.log("=== DEBUG: SISTEMA DE GAMIFICAÇÃO ===", "INFO")
        
        try:
            from app.services.gamificacao import GamificacaoService
            from app.database import connect_to_mongo, get_database
            
            await connect_to_mongo()
            db = get_database()
            
            # Obter usuário de teste
            user = await db.usuarios.find_one({"email": "joao@gmail.com"})
            if not user:
                self.log("❌ Usuário de teste não encontrado", "ERROR")
                return False
            
            self.log(f"👤 Usuário: {user['nome']}", "INFO")
            self.log(f"⭐ XP atual: {user.get('xp', 0)}", "INFO")
            self.log(f"🏆 Nível atual: {user.get('nivel', 1)}", "INFO")
            self.log(f"🎖️ Badges: {user.get('badges', [])}", "INFO")
            
            # Testar serviço de gamificação
            service = GamificacaoService()
            
            # Testar cálculo de nível
            self.log("Testando cálculo de nível...")
            nivel = await service.calcular_nivel(user.get('xp', 0))
            self.log(f"✅ Nível calculado: {nivel}", "SUCCESS")
            
            # Testar próximo nível
            prox_xp = await service.obter_proximo_nivel_xp(nivel)
            self.log(f"✅ XP para próximo nível: {prox_xp}", "SUCCESS")
            
            # Testar verificação de badges
            self.log("Testando verificação de badges...")
            novos_badges = await service.verificar_badges(str(user["_id"]))
            self.log(f"✅ Novos badges: {novos_badges}", "SUCCESS")
            
            # Testar progresso completo
            self.log("Testando progresso completo...")
            progresso = await service.obter_progresso_usuario(str(user["_id"]))
            if progresso:
                self.log(f"✅ Progresso: XP={progresso.xp}, Nível={progresso.nivel}", "SUCCESS")
                self.log(f"   Badges: {progresso.badges}", "INFO")
                self.log(f"   Eventos curtidos: {progresso.eventos_curtidos}", "INFO")
            else:
                self.log("❌ Falha ao obter progresso", "ERROR")
            
            # Testar leaderboard
            self.log("Testando leaderboard...")
            leaderboard = await service.obter_leaderboard(5)
            self.log(f"✅ Leaderboard: {len(leaderboard)} usuários", "SUCCESS")
            
            for i, entry in enumerate(leaderboard[:3]):
                self.log(f"   {i+1}. {entry.nome} - {entry.xp} XP (Nível {entry.nivel})")
            
            # Testar badges disponíveis
            self.log("Testando badges disponíveis...")
            badges_info = await service.obter_badges_disponiveis(str(user["_id"]))
            self.log(f"✅ Badges disponíveis: {len(badges_info)}", "SUCCESS")
            
            for badge in badges_info:
                status = "✅" if badge.conquistado else "⏳"
                self.log(f"   {status} {badge.nome}: {badge.descricao}")
            
            self.log("✅ Sistema de gamificação OK", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no sistema de gamificação: {str(e)}", "ERROR")
            return False
    
    async def debug_api_endpoints(self):
        """Debug dos endpoints da API"""
        self.log("=== DEBUG: ENDPOINTS DA API ===", "INFO")
        
        try:
            import requests
            
            base_url = "http://localhost:8000"
            
            # Testar health check
            self.log("Testando health check...")
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Health check OK", "SUCCESS")
            else:
                self.log(f"❌ Health check falhou: {response.status_code}", "ERROR")
            
            # Testar documentação
            self.log("Testando documentação...")
            response = requests.get(f"{base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log("✅ Swagger UI OK", "SUCCESS")
            else:
                self.log(f"❌ Swagger UI falhou: {response.status_code}", "ERROR")
            
            # Testar endpoint raiz
            self.log("Testando endpoint raiz...")
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                self.log("✅ Endpoint raiz OK", "SUCCESS")
            else:
                self.log(f"❌ Endpoint raiz falhou: {response.status_code}", "ERROR")
            
            self.log("✅ Endpoints da API OK", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro nos endpoints da API: {str(e)}", "ERROR")
            return False
    
    async def run_full_debug(self):
        """Executa debug completo"""
        self.log("🚀 Iniciando debug completo da KidsAdvisor API...", "INFO")
        
        debug_tasks = [
            ("Conexão MongoDB", self.debug_database),
            ("Sistema de Autenticação", self.debug_auth),
            ("Sistema de Recomendações", self.debug_recommendations),
            ("Sistema de Gamificação", self.debug_gamification),
            ("Endpoints da API", self.debug_api_endpoints)
        ]
        
        results = {}
        
        for task_name, task_func in debug_tasks:
            self.log(f"\n{'='*60}", "INFO")
            self.log(f"🔍 DEBUG: {task_name}", "INFO")
            self.log(f"{'='*60}", "INFO")
            
            try:
                result = await task_func()
                results[task_name] = result
            except Exception as e:
                self.log(f"❌ Erro inesperado em {task_name}: {str(e)}", "ERROR")
                results[task_name] = False
        
        # Resumo
        self.log(f"\n{'='*60}", "INFO")
        self.log("📊 RESUMO DO DEBUG", "INFO")
        self.log(f"{'='*60}", "INFO")
        
        total = len(results)
        passed = sum(1 for r in results.values() if r)
        failed = total - passed
        
        self.log(f"Total de componentes: {total}", "INFO")
        self.log(f"✅ OK: {passed}", "SUCCESS" if passed > 0 else "INFO")
        self.log(f"❌ Falharam: {failed}", "ERROR" if failed > 0 else "INFO")
        
        self.log("\n📋 Detalhes:", "INFO")
        for task_name, result in results.items():
            status = "✅" if result else "❌"
            self.log(f"  {status} {task_name}")
        
        if failed == 0:
            self.log("\n🎉 Todos os componentes estão funcionando corretamente!", "SUCCESS")
        else:
            self.log(f"\n⚠️ {failed} componente(s) com problemas", "WARNING")
        
        return results

async def main():
    """Função principal"""
    print("🔍 KidsAdvisor API - Debug Completo")
    print("="*50)
    
    debugger = Debugger()
    results = await debugger.run_full_debug()
    
    # Código de saída
    failed_count = sum(1 for r in results.values() if not r)
    sys.exit(1 if failed_count > 0 else 0)

if __name__ == "__main__":
    asyncio.run(main())

