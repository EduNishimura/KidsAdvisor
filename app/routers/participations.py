from fastapi import APIRouter, Depends, HTTPException, status
from app.database import db
from app.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()


@router.post("/eventos/{event_id}/inscrever")
async def inscrever_evento(event_id: str, current_user=Depends(get_current_user)):
    """Usuário logado se inscreve em um evento"""

    # Verifica se evento existe
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # Evita duplicação
    exists = await db.event_participants.find_one({
        "event_id": ObjectId(event_id),
        "user_id": ObjectId(current_user["_id"])
    })
    if exists:
        raise HTTPException(
            status_code=400, detail="Usuário já inscrito neste evento")

    doc = {
        "event_id": ObjectId(event_id),
        "user_id": ObjectId(current_user["_id"]),
        "status": "confirmed",
        "created_at": datetime.utcnow()
    }
    res = await db.event_participants.insert_one(doc)

    return {"message": "Inscrição realizada com sucesso", "id": str(res.inserted_id)}


@router.delete("/eventos/{event_id}/cancelar")
async def cancelar_inscricao(event_id: str, current_user=Depends(get_current_user)):
    """Usuário logado cancela sua inscrição em um evento"""

    res = await db.event_participants.delete_one({
        "event_id": ObjectId(event_id),
        "user_id": ObjectId(current_user["_id"])
    })

    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    return {"message": "Inscrição cancelada com sucesso"}


@router.get("/usuarios/{user_id}/eventos")
async def listar_eventos_usuario(user_id: str, current_user=Depends(get_current_user)):
    """Lista todos os eventos em que um usuário está inscrito"""

    participations = []
    async for p in db.event_participants.find({"user_id": ObjectId(user_id)}):
        event = await db.events.find_one({"_id": p["event_id"]})
        if event:
            participations.append({
                "event_id": str(event["_id"]),
                "event_name": event.get("name"),
                "status": p.get("status"),
                "inscrito_em": p.get("created_at")
            })

    return participations


@router.get("/eventos/{event_id}/participantes")
async def listar_participantes_evento(event_id: str, current_user=Depends(get_current_user)):
    """Lista todos os usuários inscritos em um evento"""

    participants = []
    async for p in db.event_participants.find({"event_id": ObjectId(event_id)}):
        user = await db.users.find_one({"_id": p["user_id"]})
        if user:
            participants.append({
                "user_id": str(user["_id"]),
                "user_name": user.get("name"),
                "status": p.get("status"),
                "inscrito_em": p.get("created_at")
            })

    return participants
