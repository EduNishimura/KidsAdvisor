from fastapi import APIRouter, Depends, HTTPException, status
from app.database import db
from app.auth import get_current_user
from app.models.evento import EventCreate, EventOut
from app.services.scraper_clubinho import scrape_all
from datetime import datetime
from bson.objectid import ObjectId
import httpx

router = APIRouter()


def event_to_out(event_doc: dict) -> dict:
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
        "host": event_doc.get("host"),
        "category_prim": event_doc.get("category_prim"),
        "category_sec": event_doc.get("category_sec"),
        "organizer_id": event_doc["organizer_id"],
        "created_at": event_doc["created_at"],
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

    res = await db.events.insert_one(doc)
    created = await db.events.find_one({"_id": res.inserted_id})
    return event_to_out(created)


@router.get("/", response_model=list[EventOut])
async def list_events():
    events = []
    async for ev in db.events.find({}).sort("start_date", 1):
        events.append(event_to_out(ev))
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
            status_code=403, detail="Somente administradores podem importar eventos")

    events = await scrape_all()
    if not events:
        return {"message": "Nenhum evento encontrado"}

    result = await db.events.insert_many(events)

    return {
        "message": f"{len(result.inserted_ids)} eventos inseridos",
        "ids": [str(_id) for _id in result.inserted_ids]
    }
