from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
from app.database import get_database
from app.models.evento import EventoResponse
from app.models.gamificacao import RecomendacaoResponse
from bson import ObjectId

class RecomendacaoService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='portuguese',
            ngram_range=(1, 2)
        )
    
    async def obter_recomendacoes_hibridas(self, usuario_id: str, limit: int = 10) -> List[RecomendacaoResponse]:
        """Obtém recomendações híbridas (70% conteúdo + 30% colaborativo)"""
        db = get_database()
        
        # Obter usuário
        usuario = await db.usuarios.find_one({"_id": usuario_id})
        if not usuario:
            return []
        
        # Obter todos os eventos
        eventos = []
        async for evento in db.eventos.find():
            eventos.append(evento)
        
        if not eventos:
            return []
        
        # Calcular recomendações de conteúdo
        recomendacoes_conteudo = await self._recomendacoes_por_conteudo(usuario, eventos)
        
        # Calcular recomendações colaborativas
        recomendacoes_colaborativas = await self._recomendacoes_colaborativas(usuario, eventos)
        
        # Combinar recomendações (70% conteúdo + 30% colaborativo)
        scores_finais = {}
        
        # Adicionar scores de conteúdo (peso 0.7)
        for rec in recomendacoes_conteudo:
            evento_id = rec["evento_id"]
            scores_finais[evento_id] = rec["score"] * 0.7
        
        # Adicionar scores colaborativos (peso 0.3)
        for rec in recomendacoes_colaborativas:
            evento_id = rec["evento_id"]
            if evento_id in scores_finais:
                scores_finais[evento_id] += rec["score"] * 0.3
            else:
                scores_finais[evento_id] = rec["score"] * 0.3
        
        # Ordenar por score e retornar top eventos
        eventos_ordenados = sorted(scores_finais.items(), key=lambda x: x[1], reverse=True)
        
        recomendacoes = []
        eventos_dict = {str(evento["_id"]): evento for evento in eventos}
        
        for evento_id, score in eventos_ordenados[:limit]:
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
                    score=score,
                    tipo="hibrida"
                ))
        
        return recomendacoes
    
    async def _recomendacoes_por_conteudo(self, usuario: dict, eventos: List[dict]) -> List[dict]:
        """Calcula recomendações baseadas em conteúdo usando TF-IDF"""
        if not usuario["eventosCurtidos"]:
            return []
        
        # Obter eventos curtidos pelo usuário
        eventos_curtidos_ids = usuario["eventosCurtidos"]
        eventos_curtidos = [e for e in eventos if str(e["_id"]) in eventos_curtidos_ids]
        
        if not eventos_curtidos:
            return []
        
        # Preparar textos para TF-IDF
        textos_eventos = [f"{e['nome']} {e['descricao']} {e['categoria']}" for e in eventos]
        textos_curtidos = [f"{e['nome']} {e['descricao']} {e['categoria']}" for e in eventos_curtidos]
        
        # Calcular TF-IDF
        try:
            tfidf_matrix = self.vectorizer.fit_transform(textos_eventos)
            tfidf_curtidos = self.vectorizer.transform(textos_curtidos)
            
            # Calcular similaridade do cosseno
            similaridades = cosine_similarity(tfidf_curtidos, tfidf_matrix)
            
            # Média das similaridades para eventos curtidos
            scores_medios = np.mean(similaridades, axis=0)
            
            # Criar lista de recomendações
            recomendacoes = []
            for i, score in enumerate(scores_medios):
                evento_id = str(eventos[i]["_id"])
                if evento_id not in eventos_curtidos_ids:  # Não recomendar eventos já curtidos
                    recomendacoes.append({
                        "evento_id": evento_id,
                        "score": float(score)
                    })
            
            return sorted(recomendacoes, key=lambda x: x["score"], reverse=True)
        
        except Exception as e:
            print(f"Erro no cálculo TF-IDF: {e}")
            return []
    
    async def _recomendacoes_colaborativas(self, usuario: dict, eventos: List[dict]) -> List[dict]:
        """Calcula recomendações colaborativas baseadas em amigos"""
        if not usuario["amigos"]:
            return []
        
        db = get_database()
        
        # Obter eventos curtidos pelos amigos
        eventos_amigos = set()
        for amigo_id in usuario["amigos"]:
            amigo = await db.usuarios.find_one({"_id": amigo_id})
            if amigo and "eventosCurtidos" in amigo:
                eventos_amigos.update(amigo["eventosCurtidos"])
        
        # Remover eventos já curtidos pelo usuário
        eventos_amigos = eventos_amigos - set(usuario["eventosCurtidos"])
        
        if not eventos_amigos:
            return []
        
        # Calcular scores baseados na frequência de likes dos amigos
        scores = {}
        for evento_id in eventos_amigos:
            evento = await db.eventos.find_one({"_id": ObjectId(evento_id)})
            if evento:
                # Score baseado no número de likes e se amigos curtiram
                score = evento["likes"] * 0.1  # Normalizar likes
                scores[evento_id] = score
        
        # Converter para lista ordenada
        recomendacoes = [
            {"evento_id": evento_id, "score": score}
            for evento_id, score in scores.items()
        ]
        
        return sorted(recomendacoes, key=lambda x: x["score"], reverse=True)
