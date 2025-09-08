@echo off

REM Script para executar o KidsAdvisor no Windows

echo 🎯 KidsAdvisor - Sistema de Recomendações de Eventos Infantis
echo ==============================================================

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não está instalado. Por favor, instale o Docker primeiro.
    pause
    exit /b 1
)

REM Verificar se Docker Compose está instalado
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro.
    pause
    exit /b 1
)

echo 🐳 Iniciando serviços com Docker Compose...
docker-compose up --build -d

echo ⏳ Aguardando serviços ficarem prontos...
timeout /t 10 /nobreak >nul

echo 🌱 Executando seed de dados de exemplo...
python seed_data.py

echo.
echo ✅ KidsAdvisor está rodando!
echo.
echo 📋 Informações importantes:
echo    • API: http://localhost:8000
echo    • Documentação: http://localhost:8000/docs
echo    • MongoDB: localhost:27017
echo.
echo 👥 Usuários de exemplo criados:
echo    • maria@gmail.com (senha: 123456)
echo    • joao@gmail.com (senha: 123456)
echo    • ana@gmail.com (senha: 123456)
echo    • pedro@gmail.com (senha: 123456)
echo    • centro@cultural.com (senha: 123456)
echo.
echo 🧪 Para executar os testes:
echo    docker-compose exec api pytest
echo.
echo 🛑 Para parar os serviços:
echo    docker-compose down
echo.
pause
