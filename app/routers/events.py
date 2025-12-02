from fastapi import APIRouter, Depends, HTTPException, status
from app.database import db
from app.auth import get_current_user
from app.models.evento import EventCreate, EventOut
from app.services.scraper_clubinho import scrape_all
from datetime import datetime
from bson.objectid import ObjectId
import httpx
from app.routers.categories import DEFAULT_TAGS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from collections import defaultdict

router = APIRouter()

# Stopwords em português para filtros de texto
stopwords_pt = {
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "até", "com", "como", "da", "das", "do", "dos", "e", "ela", "elas", "ele", "eles", "em", "entre", "era", "eram", "essa", "essas", "esse", "esses", "esta", "estamos", "estas", "estava", "estavam", "este", "esteja", "estejam", "estejamos", "estes", "esteve", "estive", "estivemos", "estiver", "estivera", "estiveram", "estiverem", "estivermos", "estivesse", "estivessem", "estivéramos", "estivéssemos", "estou", "está", "estão", "eu", "foi", "fomos", "for", "fora", "foram", "forem", "formos", "fosse", "fossem", "fui", "fôramos", "fôssemos", "haja", "hajam", "hajamos", "havemos", "havia", "hei", "houve", "houvemos", "houver", "houvera", "houveram", "houverei", "houverem", "houveremos", "houveria", "houveriam", "houveríamos", "houverão", "houverá", "houveríamos", "houvesse", "houvessem", "houvéramos", "houvéssemos", "há", "hão", "isso", "isto", "já", "lhe", "lhes", "mais", "mas", "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "na", "nas", "nem", "no", "nos", "nossa", "nossas", "nosso", "nossos", "num", "numa", "não", "nós", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "qual", "quando", "que", "quem", "se", "seja", "sejam", "sejamos", "sem", "ser", "será", "serão", "seria", "seriam", "será", "serão", "seria", "seriam", "seu", "seus", "só", "sua", "suas", "são", "só", "também", "te", "tem", "temos", "tenha", "tenham", "tenhamos", "tenho", "ter", "terá", "terão", "teria", "teriam", "teve", "tinha", "tinham", "tive", "tivemos", "tiver", "tivera", "tiveram", "tiverem", "tivermos", "tivesse", "tivessem", "tivéramos", "tivéssemos", "tu", "tua", "tuas", "tém", "tínhamos", "um", "uma", "você", "vocês", "vos", "à", "às", "éramos", "é", "são", "está", "estão", "foi", "foram", "será", "serão", "seria", "seriam", "estava", "estavam", "estivera", "estiveram", "esteja", "estejam", "estivesse", "estivessem", "estiver", "estiverem", "hei", "há", "houve", "houverá", "houveria", "houveriam", "houver", "houverem", "houvera", "houveram", "haja", "hajam", "houvesse", "houvessem", "houvéramos", "houvéssemos", "tenho", "tem", "temos", "tém", "tinha", "tinham", "tínhamos", "tive", "tivemos", "teve", "terá", "terão", "teria", "teriam", "ter", "terem", "tera", "teram", "tenha", "tenham", "tenhamos", "tivesse", "tivessem", "tivéramos", "tivéssemos", "tiver", "tiverem", "tivera", "tiveram", "sou", "somos", "era", "éramos", "fui", "fomos", "será", "serão", "seria", "seriam", "seja", "sejam", "sejamos", "fosse", "fossem", "fôramos", "fôssemos", "for", "forem", "formos", "fora", "foram", "sou", "somos", "era", "éramos", "fui", "fomos", "será", "serão", "seria", "seriam", "seja", "sejam", "sejamos", "fosse", "fossem", "fôramos", "fôssemos", "for", "forem", "formos", "fora", "foram"
}


def clean_text(text: str) -> str:
    """
    Limpa o texto removendo stopwords em português e caracteres especiais.
    """
    if not text:
        return ""

    # Converte para minúsculas
    text = text.lower()

    # Remove caracteres especiais e números, mantém apenas letras e espaços
    text = re.sub(r'[^a-záàâãéèêíìîóòôõúùûç\s]', ' ', text)

    # Remove espaços extras
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove stopwords
    words = text.split()
    filtered_words = [
        word for word in words if word not in stopwords_pt and len(word) > 2]

    return ' '.join(filtered_words)


def event_to_out(event_doc: dict) -> dict:
    host = event_doc.get("host")
    # Se host não for dict ou não tiver name, retorna None
    if not isinstance(host, dict) or not host.get("name"):
        host = None
    return {
        "id": str(event_doc["_id"]),   # id do Mongo
        "reference_id": event_doc.get("reference_id"),
        "name": event_doc.get("name"),
        "detail": event_doc.get("detail"),
        "start_date": event_doc.get("start_date"),
        "end_date": event_doc.get("end_date"),
        "private_event": event_doc.get("private_event", 0),
        "published": event_doc.get("published", 1),
        "cancelled": event_doc.get("cancelled", 0),
        "image": event_doc.get("image"),
        "url": event_doc.get("url"),
        "address": event_doc.get("address"),
        "host": host,
        "category_prim": event_doc.get("category_prim"),
        "category_sec": event_doc.get("category_sec"),
        "organizer_id": event_doc.get("organizer_id"),
        "created_at": event_doc.get("created_at"),
        "tags": event_doc.get("tags", []),
    }


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, current_user=Depends(get_current_user)):
    # apenas admin pode cadastrar
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Somente administradores podem cadastrar eventos")

    doc = event.dict()
    doc["created_at"] = datetime.utcnow()

    # --- INÍCIO DA CORREÇÃO ---
    # Converte os campos de URL para string, se existirem
    if doc.get("image"):
        doc["image"] = str(doc["image"])

    if doc.get("url"):
        doc["url"] = str(doc["url"])
    # --- FIM DA CORREÇÃO ---

    for tag in event.tags:
        if tag not in DEFAULT_TAGS:
            raise HTTPException(status_code=400, detail=f"Tag inválida: {tag}")

    res = await db.events.insert_one(doc)
    created = await db.events.find_one({"_id": res.inserted_id})
    return event_to_out(created)


@router.get("/", response_model=list[EventOut])
async def list_events():
    events = []
    async for ev in db.events.find({}).sort("start_date", 1):
        event_data = event_to_out(ev)

        # Conta o número de likes do evento
        likes_count = await db.event_reactions.count_documents({
            "event_id": ObjectId(ev["_id"]),
            "reaction": "like"
        })

        # Conta o número de dislikes (opcional)
        dislikes_count = await db.event_reactions.count_documents({
            "event_id": ObjectId(ev["_id"]),
            "reaction": "dislike"
        })

        # Adiciona as contagens ao dicionário do evento
        event_data["likes"] = likes_count
        event_data["dislikes"] = dislikes_count

        events.append(event_data)

    return events
# Importar eventos da Sympla (simplificado)


@router.post("/import-sympla")
async def import_sympla_events(sympla_token: str, current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Somente administradores podem importar eventos")

    headers = {"s_token": sympla_token}
    url = "https://api.sympla.com.br/public/v3/events"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code,
                                detail="Erro ao acessar Sympla")

        data = resp.json().get("data", [])
        inserted = []
        for ev in data:
            doc = {
                "name": ev.get("name"),
                "description": ev.get("detail"),
                "start_date": ev.get("start_date"),
                "end_date": ev.get("end_date"),
                "location": ev.get("address", {}).get("name", "Local não informado"),
                "organizer_id": str(current_user["_id"]),
                "sympla_id": ev.get("id"),
                "created_at": datetime.utcnow()
            }
            # Evita duplicar pelo sympla_id
            exists = await db.events.find_one({"sympla_id": doc["sympla_id"]})
            if not exists:
                res = await db.events.insert_one(doc)
                inserted.append(str(res.inserted_id))

        return {"imported": len(inserted), "ids": inserted}


@router.post("/scrape-clubinho")
async def scrape_clubinho_events(current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Somente administradores podem importar eventos"
        )

    raw_events = scrape_all()

    if not raw_events:
        return {"message": "Nenhum evento encontrado"}

    docs = []
    for ev in raw_events:
        doc = {
            "name": ev.get("name"),
            "detail": ev.get("detail"),
            "start_date": ev.get("start_date"),
            "end_date": ev.get("end_date"),
            "private_event": ev.get("private_event", 0),
            "published": ev.get("published", 1),
            "cancelled": ev.get("cancelled", 0),
            "image": ev.get("image"),
            "url": ev.get("url"),
            "address": ev.get("address"),
            "host": ev.get("host"),
            "category_prim": ev.get("category_prim"),
            "category_sec": ev.get("category_sec"),
            "organizer_id": str(current_user["_id"]),
            "created_at": ev.get("created_at", datetime.utcnow()),
        }
        docs.append(doc)

    result = await db.events.insert_many(docs)

    return {
        "message": f"{len(result.inserted_ids)} eventos inseridos",
        "ids": [str(_id) for _id in result.inserted_ids]
    }


@router.get("/relacionados")
async def listar_eventos_relacionados(current_user=Depends(get_current_user)):
    """
    Retorna eventos relacionados com base em:
    - Eventos curtidos pelo usuário
    - Tags dos eventos e community_tags_count
    - Categorias primária/secundária
    """

    user_id = ObjectId(current_user["_id"])

    # 🔹 1. Buscar eventos curtidos pelo usuário
    liked_cursor = db.event_reactions.find({
        "user_id": user_id,
        "reaction": "like"
    })
    liked_event_ids = [doc["event_id"] async for doc in liked_cursor]

    if not liked_event_ids:
        raise HTTPException(
            status_code=404, detail="Usuário ainda não curtiu nenhum evento.")

    # 🔹 2. Coletar tags e categorias dos eventos curtidos
    liked_tags = set()
    liked_categories = set()

    async for ev in db.events.find({"_id": {"$in": liked_event_ids}}):
        liked_tags.update(ev.get("tags", []))

        # categorias prim/sec
        if ev.get("category_prim"):
            liked_categories.add(ev["category_prim"].get("name"))
        if ev.get("category_sec"):
            liked_categories.add(ev["category_sec"].get("name"))

        # adiciona as community_tags mais votadas (top 3)
        if "community_tags_count" in ev:
            sorted_tags = sorted(
                ev["community_tags_count"].items(),
                key=lambda x: x[1],
                reverse=True
            )
            top_tags = [t[0] for t in sorted_tags[:3]]
            liked_tags.update(top_tags)

    if not liked_tags and not liked_categories:
        raise HTTPException(
            status_code=404, detail="Não há dados suficientes para recomendações.")

    # 🔹 Buscar eventos participados pelo usuário
    participated_cursor = db.event_participants.find({
        "user_id": user_id,
        "status": "confirmed"
    })
    participated_event_ids = [p["event_id"] async for p in participated_cursor]

    # 🔹 Combinar curtidos + participados
    excluded_event_ids = list(set(liked_event_ids + participated_event_ids))

    # 🔹 3. Buscar outros eventos com tags OU categorias semelhantes
    related_cursor = db.events.find({
        "$and": [
            {"_id": {"$nin": excluded_event_ids}},
            {
                "$or": [
                    {"tags": {"$in": list(liked_tags)}},
                    {"category_prim.name": {"$in": list(liked_categories)}},
                    {"category_sec.name": {"$in": list(liked_categories)}}
                ]
            }
        ]
    })

    related_events = []
    async for ev in related_cursor:
        score = 0

        # +1 para cada tag em comum
        score += len(set(ev.get("tags", [])) & liked_tags)

        # +1 para cada tag da comunidade que bate
        if "community_tags_count" in ev:
            comm_tags = set(ev["community_tags_count"].keys())
            score += len(comm_tags & liked_tags)

        # +2 para categoria primária equivalente
        if ev.get("category_prim") and ev["category_prim"].get("name") in liked_categories:
            score += 2

        # +1 para categoria secundária equivalente
        if ev.get("category_sec") and ev["category_sec"].get("name") in liked_categories:
            score += 1

        if score > 0:
            related_events.append({
                "id": str(ev["_id"]),
                "name": ev.get("name"),
                "tags": ev.get("tags", []),
                "category_prim": ev.get("category_prim"),
                "category_sec": ev.get("category_sec"),
                "image": ev.get("image"),
                "score": score
            })

    # 🔹 4. Ordena por afinidade
    related_events.sort(key=lambda e: e["score"], reverse=True)

    return {
        "related_tags": list(liked_tags),
        "related_categories": list(liked_categories),
        "related_events": related_events
    }


@router.get("/recomendados-tfidf")
async def recomendar_eventos_tfidf(current_user=Depends(get_current_user)):
    """
    Recomenda eventos usando TF-IDF + Similaridade do Cosseno,
    considerando tags, categorias e descrições.
    """
    user_id = ObjectId(current_user["_id"])

    # 🔹 Buscar eventos curtidos e participados
    liked_cursor = db.event_reactions.find(
        {"user_id": user_id, "reaction": "like"})
    liked_event_ids = [doc["event_id"] async for doc in liked_cursor]

    participated_cursor = db.event_participants.find({
        "user_id": user_id,
        "status": "confirmed"
    })
    participated_event_ids = [p["event_id"] async for p in participated_cursor]

    excluded_event_ids = list(set(liked_event_ids + participated_event_ids))

    # 🔹 Buscar todos os eventos publicados
    events = [e async for e in db.events.find({"published": 1})]
    if not events:
        raise HTTPException(
            status_code=404, detail="Nenhum evento encontrado.")

    # 🔹 Montar texto base de cada evento
    corpus = []
    event_ids = []
    for e in events:
        text_parts = []

        # tags e categorias
        text_parts.extend(e.get("tags", []))
        if e.get("community_tags_count"):
            text_parts.extend(list(e["community_tags_count"].keys()))
        if e.get("category_prim"):
            text_parts.append(e["category_prim"].get("name", ""))
        if e.get("category_sec"):
            text_parts.append(e["category_sec"].get("name", ""))

        # descrição
        if e.get("detail"):
            text_parts.append(e["detail"])

        # texto final - limpa stopwords e caracteres especiais
        text = " ".join(text_parts)
        cleaned_text = clean_text(text)
        corpus.append(cleaned_text)
        event_ids.append(e["_id"])

    # 🔹 Criar vetor TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # 🔹 Construir texto do perfil do usuário
    user_tags = set(current_user.get("preferred_tags", []))

   # 1. Combine todos os eventos de interesse (curtidos + participados)
    interest_event_ids = list(set(liked_event_ids + participated_event_ids))

    # 2. Busque os detalhes desses eventos
    user_profile_texts = []
    async for ev in db.events.find({"_id": {"$in": interest_event_ids}}):
        user_tags.update(ev.get("tags", []))
        if ev.get("category_prim"):
            user_tags.add(ev["category_prim"].get("name"))
        if ev.get("category_sec"):
            user_tags.add(ev["category_sec"].get("name"))

        # Adiciona a descrição (detail) ao corpus do usuário
        if ev.get("detail"):
            user_profile_texts.append(ev.get("detail"))

    # 3. Crie o perfil final
    # Junta as tags únicas + todas as descrições
    user_profile_text = " ".join(list(user_tags) + user_profile_texts)

    cleaned_user_profile = clean_text(user_profile_text)
    user_vector = vectorizer.transform([cleaned_user_profile])

    # 🔹 Calcular similaridade do cosseno
    similarities = cosine_similarity(user_vector, tfidf_matrix)[0]

    # 🔹 Ordenar eventos por afinidade
    top_indices = np.argsort(similarities)[::-1]

    recomendados = []
    for idx in top_indices:
        ev = events[idx]
        if ev["_id"] in excluded_event_ids:
            continue  # não recomenda eventos já vistos
        score = float(similarities[idx])
        if score <= 0:
            continue
        recomendados.append({
            "id": str(ev["_id"]),
            "name": ev.get("name"),
            "score": round(score, 3),
            "tags": ev.get("tags", []),
            "category_prim": ev.get("category_prim"),
            "image": ev.get("image"),
            "detail": (ev.get("detail") or "")[:120] + "..."
        })

    return {
        "user_tags_profile": list(user_tags),
        "recommended_events": recomendados[:10]  # limita a top 10
    }


@router.get("/recomendados-colaborativo")
async def recomendar_eventos_colaborativo(current_user=Depends(get_current_user)):
    """
    Recomenda eventos com base em filtragem colaborativa.
    Usa similaridade entre usuários (curtidas e participações em comum).
    """

    user_id = ObjectId(current_user["_id"])

    # 🔹 1. Buscar todos os usuários e eventos com interações (likes + participações)
    reactions_cursor = db.event_reactions.find({"reaction": "like"})
    participations_cursor = db.event_participants.find({"status": "confirmed"})

    user_event_map = defaultdict(set)

    # Reações positivas contam como interesse
    async for r in reactions_cursor:
        user_event_map[str(r["user_id"])].add(str(r["event_id"]))

    # Participações também contam como interesse
    async for p in participations_cursor:
        user_event_map[str(p["user_id"])].add(str(p["event_id"]))

    # 🔹 2. Garantir que temos pelo menos 2 usuários
    if len(user_event_map) < 2:
        raise HTTPException(
            status_code=404, detail="Dados insuficientes para recomendações colaborativas")

    user_ids = list(user_event_map.keys())
    event_ids = list({eid for events in user_event_map.values()
                     for eid in events})

    # 🔹 3. Criar matriz usuário x evento
    matrix = np.zeros((len(user_ids), len(event_ids)))
    for i, uid in enumerate(user_ids):
        for eid in user_event_map[uid]:
            j = event_ids.index(eid)
            matrix[i, j] = 1

    # 🔹 4. Calcular similaridade de usuários
    similarity = cosine_similarity(matrix)

    # 🔹 5. Encontrar usuário atual na matriz
    if str(user_id) not in user_ids:
        raise HTTPException(
            status_code=404, detail="Usuário não possui interações suficientes")

    user_idx = user_ids.index(str(user_id))
    user_similarities = similarity[user_idx]

    # 🔹 6. Pegar top usuários semelhantes (exceto ele mesmo)
    similar_users_idx = np.argsort(user_similarities)[::-1][1:6]  # top 5
    similar_users = [user_ids[i]
                     for i in similar_users_idx if user_similarities[i] > 0]

    if not similar_users:
        raise HTTPException(
            status_code=404, detail="Nenhum usuário similar encontrado")

    # 🔹 7. Coletar eventos que usuários semelhantes gostaram, mas o atual não viu
    current_user_events = user_event_map[str(user_id)]
    recommended_event_ids = set()

    for uid in similar_users:
        for eid in user_event_map[uid]:
            if eid not in current_user_events:
                recommended_event_ids.add(eid)

    if not recommended_event_ids:
        raise HTTPException(
            status_code=404, detail="Nenhum evento recomendado encontrado")

    # 🔹 8. Buscar dados dos eventos recomendados
    recommended_events = []
    async for ev in db.events.find({"_id": {"$in": [ObjectId(eid) for eid in recommended_event_ids]}}):
        recommended_events.append({
            "id": str(ev["_id"]),
            "name": ev.get("name"),
            "tags": ev.get("tags", []),
            "category_prim": ev.get("category_prim"),
            "image": ev.get("image"),
            "detail": (ev.get("detail") or "")[:120] + "..."
        })

    return {
        "method": "filtragem_colaborativa",
        "similar_users_count": len(similar_users),
        "recommended_events": recommended_events[:10]  # top 10
    }


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str, current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Somente administradores podem deletar eventos")

    res = await db.events.delete_one({"_id": ObjectId(event_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return


@router.delete("/eventos", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_events(current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Somente administradores podem deletar eventos")

    await db.events.delete_many({})
    return


@router.get("/{event_id}", response_model=EventOut)
async def get_event_by_id(event_id: str):
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event_to_out(event)
