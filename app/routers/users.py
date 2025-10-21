from app.routers.categories import DEFAULT_TAGS
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.usuario import UserCreate, UserOut
from app.database import db
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm
from bson.objectid import ObjectId
from datetime import datetime, timedelta

router = APIRouter()


def user_to_out(user_doc: dict) -> dict:
    return {
        "id": str(user_doc["_id"]),
        "name": user_doc["name"],
        "email": user_doc["email"],
        "role": user_doc.get("role", "parent"),
        "children": user_doc.get("children", []),
        "friends": user_doc.get("friends", []),
        "badges": user_doc.get("badges", []),
        "level": user_doc.get("level", 1),
        "xp": user_doc.get("xp", 0),
        "created_at": user_doc.get("created_at")
    }


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # prevent duplicate emails
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(user.password)
    doc = {
        "name": user.name,
        "email": user.email,
        "password": hashed,
        "role": user.role,
        "children": [c.dict() for c in user.children],
        "friends": [],
        "badges": [],
        "level": 1,
        "xp": 0,
        "created_at": datetime.utcnow()
    }
    res = await db.users.insert_one(doc)
    created = await db.users.find_one({"_id": res.inserted_id})
    return user_to_out(created)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm uses fields 'username' and 'password'
    user = await db.users.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect email or password")
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        {"sub": str(user["_id"])}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/friends-list")
async def get_friends(current_user=Depends(get_current_user)):
    """
    Retorna a lista de amigos do usuário autenticado.
    """
    user_id = str(current_user["_id"])
    
    # Busca o usuário atual
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Pega a lista de IDs dos amigos
    friend_ids = user.get("friends", [])
    
    if not friend_ids:
        return {"friends": [], "count": 0}
    
    # Converte os IDs para ObjectId para buscar os dados dos amigos
    friend_object_ids = [ObjectId(friend_id) for friend_id in friend_ids]
    
    # Busca os dados dos amigos
    friends_cursor = db.users.find({"_id": {"$in": friend_object_ids}})
    friends = await friends_cursor.to_list(length=None)
    
    # Converte para o formato de saída
    friends_data = []
    for friend in friends:
        friends_data.append({
            "id": str(friend["_id"]),
            "name": friend["name"],
            "email": friend["email"],
            "role": friend.get("role", "parent"),
            "level": friend.get("level", 1),
            "xp": friend.get("xp", 0)
        })
    
    return {
        "friends": friends_data,
        "count": len(friends_data)
    }


@router.get("/{id}", response_model=UserOut)
async def get_user(id: str, current_user=Depends(get_current_user)):
    user = await db.users.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_out(user)


@router.post("/amigos/{idAmigo}")
async def add_friend(idAmigo: str, current_user=Depends(get_current_user)):
    # get the current user's ID from the authenticated user
    user_id = str(current_user["_id"])
    
    if user_id == idAmigo:
        raise HTTPException(
            status_code=400, detail="Cannot add yourself as friend")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    friend = await db.users.find_one({"_id": ObjectId(idAmigo)})
    if not user or not friend:
        raise HTTPException(status_code=404, detail="User or friend not found")

    friend_id_str = str(friend["_id"])
    user_id_str = str(user["_id"])

    if friend_id_str in user.get("friends", []):
        return {"message": "Already friends"}

    await db.users.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"friends": friend_id_str}})
    await db.users.update_one({"_id": ObjectId(idAmigo)}, {"$addToSet": {"friends": user_id_str}})

    # optional: create a friendship document for audit
    await db.friendships.insert_one({
        "user_id": user_id_str,
        "friend_id": friend_id_str,
        "status": "accepted",
        "created_at": datetime.utcnow()
    })

    return {"message": "Friend added"}


@router.post("/me/tags")
async def definir_tags_usuario(tags: list[str], current_user=Depends(get_current_user)):
    """
    Permite que o usuário defina até 5 tags pessoais (preferências).
    Essas tags são usadas para recomendações de eventos.
    """
    if not (1 <= len(tags) <= 5):
        raise HTTPException(status_code=400, detail="Informe entre 1 e 5 tags")

    for tag in tags:
        if tag not in DEFAULT_TAGS:
            raise HTTPException(status_code=400, detail=f"Tag inválida: {tag}")

    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"preferred_tags": tags}}
    )

    return {"message": "Tags de preferência atualizadas com sucesso", "tags": tags}
