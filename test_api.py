#!/usr/bin/env python3
"""
🧪 Script de Teste Python - KidsAdvisor API
Teste automatizado completo da API com relatórios detalhados
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class KidsAdvisorTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.test_results: List[Dict] = []
        
    def log(self, message: str, status: str = "INFO"):
        """Log com cores"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if status == "SUCCESS":
            print(f"{Colors.GREEN}✅ [{timestamp}] {message}{Colors.NC}")
        elif status == "ERROR":
            print(f"{Colors.RED}❌ [{timestamp}] {message}{Colors.NC}")
        elif status == "WARNING":
            print(f"{Colors.YELLOW}⚠️ [{timestamp}] {message}{Colors.NC}")
        else:
            print(f"{Colors.BLUE}ℹ️ [{timestamp}] {message}{Colors.NC}")
    
    def test_endpoint(self, method: str, endpoint: str, data: Dict = None, 
                     headers: Dict = None, expected_status: int = 200) -> Dict:
        """Testa um endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_time": response_time,
                "success": response.status_code == expected_status,
                "response_data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
            
            if result["success"]:
                self.log(f"{method} {endpoint} - OK ({response.status_code}) - {response_time:.3f}s", "SUCCESS")
            else:
                self.log(f"{method} {endpoint} - FAIL ({response.status_code}, esperado {expected_status}) - {response_time:.3f}s", "ERROR")
                self.log(f"Response: {result['response_data']}", "ERROR")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            result = {
                "method": method,
                "endpoint": endpoint,
                "status_code": "ERROR",
                "expected_status": expected_status,
                "response_time": end_time - start_time,
                "success": False,
                "error": str(e)
            }
            self.log(f"{method} {endpoint} - ERROR: {str(e)}", "ERROR")
            return result
    
    def test_health_check(self) -> bool:
        """Testa o endpoint de health check"""
        self.log("Testando Health Check...")
        result = self.test_endpoint("GET", "/health")
        return result["success"]
    
    def test_user_registration(self) -> bool:
        """Testa cadastro de usuário"""
        self.log("Testando Cadastro de Usuário...")
        
        user_data = {
            "nome": "Teste Python",
            "email": f"teste.python.{int(time.time())}@example.com",
            "senha": "123456",
            "tipo": "pai"
        }
        
        result = self.test_endpoint("POST", "/usuarios/", data=user_data)
        
        if result["success"]:
            self.user_id = result["response_data"]["id"]
            self.log(f"Usuário criado: {result['response_data']['nome']} (ID: {self.user_id})", "SUCCESS")
            return True
        else:
            self.log("Falha no cadastro de usuário", "ERROR")
            return False
    
    def test_login(self, email: str, password: str) -> bool:
        """Testa login e obtém token"""
        self.log("Testando Login...")
        
        login_data = {"email": email, "senha": password}
        result = self.test_endpoint("POST", "/usuarios/login", data=login_data)
        
        if result["success"]:
            self.token = result["response_data"]["access_token"]
            self.log("Login realizado com sucesso!", "SUCCESS")
            return True
        else:
            self.log("Falha no login", "ERROR")
            return False
    
    def test_create_event(self) -> Optional[str]:
        """Testa criação de evento"""
        self.log("Testando Criação de Evento...")
        
        event_data = {
            "nome": "Evento de Teste Python",
            "descricao": "Evento criado para testes automatizados em Python",
            "categoria": "arte",
            "localizacao": "São Paulo",
            "data": "2025-12-31T14:00:00",
            "idade_recomendada": "6-12",
            "preco": 30.0,
            "organizadorId": self.user_id
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        result = self.test_endpoint("POST", "/eventos/", data=event_data, headers=headers)
        
        if result["success"]:
            event_id = result["response_data"]["id"]
            self.log(f"Evento criado: {result['response_data']['nome']} (ID: {event_id})", "SUCCESS")
            return event_id
        else:
            self.log("Falha na criação de evento", "ERROR")
            return None
    
    def test_like_event(self, event_id: str) -> bool:
        """Testa curtir evento"""
        self.log(f"Testando Curtir Evento {event_id}...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        result = self.test_endpoint("POST", f"/eventos/{event_id}/like", headers=headers)
        
        if result["success"]:
            self.log("Evento curtido com sucesso!", "SUCCESS")
            return True
        else:
            self.log("Falha ao curtir evento", "ERROR")
            return False
    
    def test_recommendations(self) -> List[Dict]:
        """Testa sistema de recomendações"""
        self.log("Testando Sistema de Recomendações...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        result = self.test_endpoint("GET", f"/recomendacoes/{self.user_id}", headers=headers)
        
        if result["success"]:
            recommendations = result["response_data"]
            self.log(f"Recomendações obtidas: {len(recommendations)} encontradas", "SUCCESS")
            
            # Mostrar top 3 recomendações
            for i, rec in enumerate(recommendations[:3]):
                score = rec.get("score", 0)
                evento_nome = rec.get("evento", {}).get("nome", "N/A")
                self.log(f"  {i+1}. {evento_nome} (Score: {score:.3f})")
            
            return recommendations
        else:
            self.log("Falha ao obter recomendações", "ERROR")
            return []
    
    def test_gamification(self) -> Optional[Dict]:
        """Testa sistema de gamificação"""
        self.log("Testando Sistema de Gamificação...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        result = self.test_endpoint("GET", f"/gamificacao/usuarios/{self.user_id}/progresso", headers=headers)
        
        if result["success"]:
            progress = result["response_data"]
            xp = progress.get("xp", 0)
            nivel = progress.get("nivel", 1)
            badges = progress.get("badges", [])
            
            self.log(f"Progresso obtido: XP={xp}, Nível={nivel}", "SUCCESS")
            self.log(f"Badges: {badges}")
            
            return progress
        else:
            self.log("Falha ao obter progresso", "ERROR")
            return None
    
    def test_leaderboard(self) -> bool:
        """Testa leaderboard"""
        self.log("Testando Leaderboard...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        result = self.test_endpoint("GET", "/gamificacao/leaderboard", headers=headers)
        
        if result["success"]:
            leaderboard = result["response_data"]
            self.log(f"Leaderboard obtido: {len(leaderboard)} usuários", "SUCCESS")
            
            # Mostrar top 3
            for i, user in enumerate(leaderboard[:3]):
                nome = user.get("nome", "N/A")
                xp = user.get("xp", 0)
                nivel = user.get("nivel", 1)
                self.log(f"  {i+1}. {nome} - {xp} XP (Nível {nivel})")
            
            return True
        else:
            self.log("Falha ao obter leaderboard", "ERROR")
            return False
    
    def test_error_handling(self) -> bool:
        """Testa tratamento de erros"""
        self.log("Testando Tratamento de Erros...")
        
        # Teste com token inválido
        headers = {"Authorization": "Bearer token_invalido"}
        result = self.test_endpoint("GET", f"/usuarios/{self.user_id}", headers=headers, expected_status=401)
        
        if result["success"]:
            self.log("Tratamento de erro funcionando corretamente", "SUCCESS")
            return True
        else:
            self.log("Falha no tratamento de erro", "ERROR")
            return False
    
    def run_comprehensive_test(self) -> Dict:
        """Executa teste completo"""
        self.log("🚀 Iniciando teste completo da KidsAdvisor API...", "INFO")
        
        test_results = {
            "start_time": datetime.now(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "total_time": 0
            }
        }
        
        start_time = time.time()
        
        # Lista de testes
        tests = [
            ("Health Check", self.test_health_check),
            ("Cadastro de Usuário", self.test_user_registration),
            ("Login", lambda: self.test_login(f"teste.python.{int(time.time())}@example.com", "123456")),
            ("Criação de Evento", self.test_create_event),
            ("Curtir Evento", lambda: self.test_like_event(self.user_id) if self.user_id else False),
            ("Recomendações", self.test_recommendations),
            ("Gamificação", self.test_gamification),
            ("Leaderboard", self.test_leaderboard),
            ("Tratamento de Erros", self.test_error_handling)
        ]
        
        # Executar testes
        for test_name, test_func in tests:
            self.log(f"\n{'='*50}", "INFO")
            self.log(f"🧪 Executando: {test_name}", "INFO")
            self.log(f"{'='*50}", "INFO")
            
            test_start = time.time()
            try:
                result = test_func()
                test_end = time.time()
                
                test_info = {
                    "name": test_name,
                    "success": bool(result),
                    "duration": test_end - test_start,
                    "timestamp": datetime.now()
                }
                
                test_results["tests"].append(test_info)
                test_results["summary"]["total"] += 1
                
                if test_info["success"]:
                    test_results["summary"]["passed"] += 1
                else:
                    test_results["summary"]["failed"] += 1
                    
            except Exception as e:
                test_end = time.time()
                self.log(f"Erro inesperado em {test_name}: {str(e)}", "ERROR")
                
                test_info = {
                    "name": test_name,
                    "success": False,
                    "duration": test_end - test_start,
                    "error": str(e),
                    "timestamp": datetime.now()
                }
                
                test_results["tests"].append(test_info)
                test_results["summary"]["total"] += 1
                test_results["summary"]["failed"] += 1
        
        end_time = time.time()
        test_results["summary"]["total_time"] = end_time - start_time
        test_results["end_time"] = datetime.now()
        
        return test_results
    
    def print_summary(self, results: Dict):
        """Imprime resumo dos testes"""
        self.log("\n" + "="*60, "INFO")
        self.log("📊 RESUMO DOS TESTES", "INFO")
        self.log("="*60, "INFO")
        
        summary = results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        duration = summary["total_time"]
        
        self.log(f"Total de testes: {total}", "INFO")
        self.log(f"✅ Aprovados: {passed}", "SUCCESS" if passed > 0 else "INFO")
        self.log(f"❌ Falharam: {failed}", "ERROR" if failed > 0 else "INFO")
        self.log(f"⏱️ Tempo total: {duration:.2f}s", "INFO")
        
        if total > 0:
            success_rate = (passed / total) * 100
            self.log(f"📈 Taxa de sucesso: {success_rate:.1f}%", "SUCCESS" if success_rate >= 80 else "WARNING")
        
        self.log("\n📋 Detalhes dos testes:", "INFO")
        for test in results["tests"]:
            status = "✅" if test["success"] else "❌"
            duration = test["duration"]
            self.log(f"  {status} {test['name']} ({duration:.3f}s)")
        
        self.log("\n🔗 URLs úteis:", "INFO")
        self.log(f"  📖 Documentação: {self.base_url}/docs")
        self.log(f"  🔄 ReDoc: {self.base_url}/redoc")
        self.log(f"  ❤️ Health: {self.base_url}/health")

def main():
    """Função principal"""
    print(f"{Colors.BLUE}🧪 KidsAdvisor API - Teste Automatizado Python{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    
    # Verificar se a API está rodando
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print(f"{Colors.RED}❌ API não está respondendo corretamente{Colors.NC}")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"{Colors.RED}❌ Não foi possível conectar à API em http://localhost:8000{Colors.NC}")
        print(f"{Colors.YELLOW}💡 Certifique-se de que a API está rodando com: docker-compose up{Colors.NC}")
        sys.exit(1)
    
    # Executar testes
    tester = KidsAdvisorTester()
    results = tester.run_comprehensive_test()
    tester.print_summary(results)
    
    # Código de saída baseado nos resultados
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()

