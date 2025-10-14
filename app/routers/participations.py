from app.routers.categories import DEFAULT_TAGS
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import db
from app.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()


@router.post("/{event_id}/inscrever")
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


@router.delete("/{event_id}/cancelar")
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


@router.get("/{event_id}/participantes")
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


@router.post("/{event_id}/classificar-tags")
async def classificar_tags_evento(
    event_id: str,
    tags: list[str],
    current_user=Depends(get_current_user)
):
    """
    Usuário participante pode classificar um evento com até 3 tags.
    As tags são agregadas no campo 'community_tags_count' do evento.
    """
    # ✅ valida quantidade
    if not (1 <= len(tags) <= 3):
        raise HTTPException(
            status_code=400, detail="Escolha entre 1 e 3 tags.")

    # ✅ valida tags válidas
    for tag in tags:
        if tag not in DEFAULT_TAGS:
            raise HTTPException(status_code=400, detail=f"Tag inválida: {tag}")

    # ✅ verifica se evento existe
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    # ✅ verifica se usuário participou do evento
    participou = await db.event_participants.find_one({
        "event_id": ObjectId(event_id),
        "user_id": ObjectId(current_user["_id"]),
        "status": "confirmed"
    })
    if not participou:
        raise HTTPException(
            status_code=403,
            detail="Apenas usuários que participaram do evento podem classificá-lo."
        )

    # ✅ cria ou atualiza campo de contagem
    community_tags = event.get("community_tags_count", {})

    for tag in tags:
        community_tags[tag] = community_tags.get(tag, 0) + 1

    await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": {"community_tags_count": community_tags}}
    )

    return {
        "message": "Classificação registrada com sucesso.",
        "community_tags_count": community_tags
    }


@router.get("/me/eventos")
async def listar_meus_eventos(current_user=Depends(get_current_user)):
    """Lista todos os eventos em que o usuário autenticado está inscrito"""
    participations = []
    async for p in db.event_participants.find({"user_id": ObjectId(current_user["_id"])}):
        event = await db.events.find_one({"_id": p["event_id"]})
        if event:
            participations.append({
                "event_id": str(event["_id"]),
                "event_name": event.get("name"),
                "status": p.get("status"),
                "inscrito_em": p.get("created_at")
            })
    return participations
