from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from app.database import get_database
from app.auth import get_current_user
from app.models.evento import EventoCreate, EventoResponse, EventoUpdate
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=EventoResponse)
async def criar_evento(evento: EventoCreate, current_user: dict = Depends(get_current_user)):
    """Cria um novo evento"""
    db = get_database()
    
    evento_dict = evento.dict()
    evento_dict["organizadorId"] = str(current_user["_id"])
    evento_dict["likes"] = 0
    
    result = await db.eventos.insert_one(evento_dict)
    evento_dict["_id"] = result.inserted_id
    
    return EventoResponse(
        id=str(evento_dict["_id"]),
        nome=evento_dict["nome"],
        descricao=evento_dict["descricao"],
        categoria=evento_dict["categoria"],
        localizacao=evento_dict["localizacao"],
        data=evento_dict["data"],
        idade_recomendada=evento_dict["idade_recomendada"],
        preco=evento_dict["preco"],
        organizadorId=evento_dict["organizadorId"],
        likes=evento_dict["likes"],
        data_criacao=evento_dict.get("data_criacao")
    )

@router.get("/", response_model=List[EventoResponse])
async def listar_eventos(
    categoria: Optional[str] = None,
    localizacao: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Lista eventos com filtros opcionais"""
    db = get_database()
    
    filter_dict = {}
    if categoria:
        filter_dict["categoria"] = categoria
    if localizacao:
        filter_dict["localizacao"] = localizacao
    
    eventos = []
    async for evento in db.eventos.find(filter_dict).skip(skip).limit(limit):
        eventos.append(EventoResponse(
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
        ))
    return eventos

@router.get("/{evento_id}", response_model=EventoResponse)
async def obter_evento(evento_id: str):
    """Obtém um evento específico"""
    db = get_database()
    evento = await db.eventos.find_one({"_id": ObjectId(evento_id)})
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    return EventoResponse(
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
    )

@router.post("/{evento_id}/like")
async def curtir_evento(evento_id: str, current_user: dict = Depends(get_current_user)):
    """Curtir um evento"""
    db = get_database()
    
    # Verificar se o evento existe
    evento = await db.eventos.find_one({"_id": ObjectId(evento_id)})
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    user_id = str(current_user["_id"])
    
    # Verificar se já curtiu
    if evento_id in current_user["eventosCurtidos"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evento já foi curtido"
        )
    
    # Adicionar like ao evento
    await db.eventos.update_one(
        {"_id": ObjectId(evento_id)},
        {"$inc": {"likes": 1}}
    )
    
    # Adicionar evento aos curtidos do usuário
    await db.usuarios.update_one(
        {"_id": user_id},
        {"$addToSet": {"eventosCurtidos": evento_id}}
    )
    
    # Adicionar XP ao usuário
    await db.usuarios.update_one(
        {"_id": user_id},
        {"$inc": {"xp": 10}}
    )
    
    return {"message": "Evento curtido com sucesso"}

@router.put("/{evento_id}", response_model=EventoResponse)
async def atualizar_evento(
    evento_id: str, 
    evento_update: EventoUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """Atualiza um evento (apenas o organizador)"""
    db = get_database()
    
    # Verificar se o evento existe e se o usuário é o organizador
    evento = await db.eventos.find_one({"_id": ObjectId(evento_id)})
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if evento["organizadorId"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o organizador pode atualizar o evento"
        )
    
    # Atualizar evento
    update_data = {k: v for k, v in evento_update.dict().items() if v is not None}
    await db.eventos.update_one(
        {"_id": ObjectId(evento_id)},
        {"$set": update_data}
    )
    
    # Retornar evento atualizado
    evento_atualizado = await db.eventos.find_one({"_id": ObjectId(evento_id)})
    return EventoResponse(
        id=str(evento_atualizado["_id"]),
        nome=evento_atualizado["nome"],
        descricao=evento_atualizado["descricao"],
        categoria=evento_atualizado["categoria"],
        localizacao=evento_atualizado["localizacao"],
        data=evento_atualizado["data"],
        idade_recomendada=evento_atualizado["idade_recomendada"],
        preco=evento_atualizado["preco"],
        organizadorId=evento_atualizado["organizadorId"],
        likes=evento_atualizado["likes"],
        data_criacao=evento_atualizado.get("data_criacao")
    )

@router.delete("/{evento_id}")
async def deletar_evento(evento_id: str, current_user: dict = Depends(get_current_user)):
    """Deleta um evento (apenas o organizador)"""
    db = get_database()
    
    # Verificar se o evento existe e se o usuário é o organizador
    evento = await db.eventos.find_one({"_id": ObjectId(evento_id)})
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if evento["organizadorId"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o organizador pode deletar o evento"
        )
    
    # Deletar evento
    await db.eventos.delete_one({"_id": ObjectId(evento_id)})
    
    return {"message": "Evento deletado com sucesso"}
