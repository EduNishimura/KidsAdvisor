#!/bin/bash

# Script para executar o KidsAdvisor

echo "🎯 KidsAdvisor - Sistema de Recomendações de Eventos Infantis"
echo "=============================================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

echo "🐳 Iniciando serviços com Docker Compose..."
docker-compose up --build -d

echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

echo "🌱 Executando seed de dados de exemplo..."
python seed_data.py

echo ""
echo "✅ KidsAdvisor está rodando!"
echo ""
echo "📋 Informações importantes:"
echo "   • API: http://localhost:8000"
echo "   • Documentação: http://localhost:8000/docs"
echo "   • MongoDB: localhost:27017"
echo ""
echo "👥 Usuários de exemplo criados:"
echo "   • maria@gmail.com (senha: 123456)"
echo "   • joao@gmail.com (senha: 123456)"
echo "   • ana@gmail.com (senha: 123456)"
echo "   • pedro@gmail.com (senha: 123456)"
echo "   • centro@cultural.com (senha: 123456)"
echo ""
echo "🧪 Para executar os testes:"
echo "   docker-compose exec api pytest"
echo ""
echo "🛑 Para parar os serviços:"
echo "   docker-compose down"
