from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.database import get_database
from app.auth import get_password_hash, create_access_token, get_current_user, authenticate_user
from app.models.usuario import UsuarioCreate, UsuarioLogin, UsuarioResponse, Token
from datetime import timedelta
import os

router = APIRouter()

@router.post("/", response_model=UsuarioResponse)
async def criar_usuario(usuario: UsuarioCreate):
    """Cria um novo usuário"""
    db = get_database()
    
    # Verificar se email já existe
    existing_user = await db.usuarios.find_one({"email": usuario.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar usuário
    usuario_dict = usuario.dict()
    usuario_dict["senha"] = get_password_hash(usuario.senha)
    usuario_dict["amigos"] = []
    usuario_dict["eventosCurtidos"] = []
    usuario_dict["xp"] = 0
    usuario_dict["nivel"] = 1
    usuario_dict["badges"] = []
    
    result = await db.usuarios.insert_one(usuario_dict)
    usuario_dict["_id"] = result.inserted_id
    
    return UsuarioResponse(
        id=str(usuario_dict["_id"]),
        nome=usuario_dict["nome"],
        email=usuario_dict["email"],
        tipo=usuario_dict["tipo"],
        amigos=usuario_dict["amigos"],
        eventosCurtidos=usuario_dict["eventosCurtidos"],
        xp=usuario_dict["xp"],
        nivel=usuario_dict["nivel"],
        badges=usuario_dict["badges"],
        data_criacao=usuario_dict.get("data_criacao")
    )

@router.post("/login", response_model=Token)
async def login(usuario_login: UsuarioLogin):
    """Autentica usuário e retorna token JWT"""
    user = await authenticate_user(usuario_login.email, usuario_login.senha)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/{user_id}", response_model=UsuarioResponse)
async def obter_usuario(user_id: str, current_user: dict = Depends(get_current_user)):
    """Obtém perfil do usuário"""
    db = get_database()
    user = await db.usuarios.find_one({"_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UsuarioResponse(
        id=str(user["_id"]),
        nome=user["nome"],
        email=user["email"],
        tipo=user["tipo"],
        amigos=user["amigos"],
        eventosCurtidos=user["eventosCurtidos"],
        xp=user["xp"],
        nivel=user["nivel"],
        badges=user["badges"],
        data_criacao=user.get("data_criacao")
    )

@router.post("/{user_id}/amigos/{friend_id}")
async def adicionar_amigo(user_id: str, friend_id: str, current_user: dict = Depends(get_current_user)):
    """Adiciona um amigo"""
    db = get_database()
    
    # Verificar se o usuário atual é o dono do perfil
    if str(current_user["_id"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode adicionar amigos ao seu próprio perfil"
        )
    
    # Verificar se o amigo existe
    friend = await db.usuarios.find_one({"_id": friend_id})
    if not friend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário amigo não encontrado"
        )
    
    # Verificar se já são amigos
    if friend_id in current_user["amigos"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuários já são amigos"
        )
    
    # Adicionar amigo
    await db.usuarios.update_one(
        {"_id": user_id},
        {"$addToSet": {"amigos": friend_id}}
    )
    
    return {"message": "Amigo adicionado com sucesso"}

@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios(current_user: dict = Depends(get_current_user)):
    """Lista todos os usuários"""
    db = get_database()
    usuarios = []
    async for user in db.usuarios.find():
        usuarios.append(UsuarioResponse(
            id=str(user["_id"]),
            nome=user["nome"],
            email=user["email"],
            tipo=user["tipo"],
            amigos=user["amigos"],
            eventosCurtidos=user["eventosCurtidos"],
            xp=user["xp"],
            nivel=user["nivel"],
            badges=user["badges"],
            data_criacao=user.get("data_criacao")
        ))
    return usuarios
