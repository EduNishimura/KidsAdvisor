from fastapi import APIRouter, Depends, HTTPException, status
from app.database import db
from app.auth import get_current_user
from app.models.evento import EventCreate, EventOut
from app.services.scraper_clubinho import scrape_all
from datetime import datetime
from bson.objectid import ObjectId
import httpx
from app.routers.categories import DEFAULT_TAGS

router = APIRouter()


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
        "start_date": event_doc["start_date"],
        "end_date": event_doc["end_date"],
        "private_event": event_doc.get("private_event", 0),
        "published": event_doc.get("published", 1),
        "cancelled": event_doc.get("cancelled", 0),
        "image": event_doc.get("image"),
        "url": event_doc.get("url"),
        "address": event_doc.get("address"),
        "host": host,
        "category_prim": event_doc.get("category_prim"),
        "category_sec": event_doc.get("category_sec"),
        "organizer_id": event_doc["organizer_id"],
        "created_at": event_doc["created_at"],
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


@router.get("/recomendados")
async def recomendar_eventos(current_user=Depends(get_current_user)):
    """
    Recomenda eventos com base nas tags preferidas do usuário.
    """
    user = await db.users.find_one({"_id": ObjectId(current_user["_id"])})
    user_tags = user.get("preferred_tags", [])

    if not user_tags:
        raise HTTPException(
            status_code=400, detail="Usuário não definiu tags de preferência")

    recomendados = []
    async for ev in db.events.find({"tags": {"$in": user_tags}}):
        recomendados.append({
            "id": str(ev["_id"]),
            "name": ev.get("name"),
            "tags": ev.get("tags", []),
            "image": ev.get("image"),
            "address": ev.get("address"),
            "start_date": ev.get("start_date")
        })

    return {"recomendados": recomendados}


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
