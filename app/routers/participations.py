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


@router.post("/{event_id}/tags")
async def adicionar_tags_evento(event_id: str, tags: list[str], current_user=Depends(get_current_user)):
    """
    Usuário adiciona de 1 a 3 tags ao evento em que participou.
    As tags são adicionadas diretamente no documento do evento
    e usadas para recomendações futuras.
    """

    # 1️⃣ Verifica se o evento existe
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # 2️⃣ Verifica se o usuário participou do evento
    participation = await db.event_participants.find_one({
        "event_id": ObjectId(event_id),
        "user_id": ObjectId(current_user["_id"])
    })
    if not participation:
        raise HTTPException(
            status_code=403, detail="Usuário não participou deste evento")

    # 3️⃣ Valida quantidade de tags
    if not (1 <= len(tags) <= 3):
        raise HTTPException(status_code=400, detail="Informe entre 1 e 3 tags")

    # 4️⃣ Valida se todas as tags estão dentro da lista fixa
    for tag in tags:
        if tag not in DEFAULT_TAGS:
            raise HTTPException(status_code=400, detail=f"Tag inválida: {tag}")

    # 5️⃣ Atualiza o evento com as novas tags, evitando duplicatas
    await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$addToSet": {"tags": {"$each": tags}}}
    )

    return {"message": "Tags adicionadas com sucesso", "tags_adicionadas": tags}
