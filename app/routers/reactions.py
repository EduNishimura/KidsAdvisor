from fastapi import APIRouter, Depends, HTTPException, status
from app.database import db
from app.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()


@router.post("/{event_id}/reagir")
async def reagir_evento(event_id: str, reaction: str, current_user=Depends(get_current_user)):
    """
    Permite que o usuário reaja (like/dislike) a um evento.
    Se o usuário já tiver reagido, a reação é atualizada.
    """
    if reaction not in ["like", "dislike"]:
        raise HTTPException(
            status_code=400, detail="Reação inválida. Use 'like' ou 'dislike'.")

    # Verifica se o evento existe
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # Cria ou atualiza a reação do usuário
    await db.event_reactions.update_one(
        {"user_id": ObjectId(current_user["_id"]),
         "event_id": ObjectId(event_id)},
        {
            "$set": {
                "reaction": reaction,
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    return {"message": f"Evento marcado como {reaction}"}


@router.get("/stats/top-liked")
async def listar_top_eventos(limit: int = 10):
    """
    Retorna os eventos mais curtidos com base na contagem de 'likes'
    """
    pipeline = [
        {"$match": {"reaction": "like"}},
        {"$group": {
            "_id": "$event_id",
            "likes": {"$sum": 1}
        }},
        {"$sort": {"likes": -1}},
        {"$limit": limit}
    ]

    results = db.event_reactions.aggregate(pipeline)
    top_events = []

    async for r in results:
        event = await db.events.find_one({"_id": r["_id"]})
        if event:
            top_events.append({
                "id": str(event["_id"]),
                "name": event.get("name"),
                "likes": r["likes"],
                "tags": event.get("tags", []),
                "image": event.get("image"),
                "start_date": event.get("start_date"),
                "address": event.get("address")
            })

    return {"top_liked_events": top_events}


@router.get("/likes/me")
async def listar_eventos_curtidos(current_user=Depends(get_current_user)):
    """
    Lista todos os eventos que o usuário deu like.
    """
    reactions_cursor = db.event_reactions.find({
        "user_id": ObjectId(current_user["_id"]),
        "reaction": "like"
    })

    liked_events = []
    async for r in reactions_cursor:
        event = await db.events.find_one({"_id": r["event_id"]})
        if event:
            liked_events.append({
                "id": str(event["_id"]),
                "name": event.get("name"),
                "tags": event.get("tags", [])
            })

    return liked_events
