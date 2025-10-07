from fastapi import APIRouter, Depends, HTTPException, status
from app.database import db
from app.auth import get_current_user

router = APIRouter()

# Lista fixa de categorias (pré-definidas)
DEFAULT_TAGS = [
    "Aventura",
    "Aquático",
    "Recreação/Lazer",
    "Cultural",
    "Show",
    "Musical",
    "Teatro",
    "Educativo/Científico",
    "Ar Livre",
    "Parque Temático",
    "Indoor/Fechado",
    "Day Use/Passeio",
    "Familiar",
    "Infantil/Crianças",
]


@router.get("/", response_model=list[str])
async def listar_tags():
    """Retorna as categorias fixas de eventos."""
    return DEFAULT_TAGS


@router.post("/adicionar", status_code=status.HTTP_201_CREATED)
async def adicionar_tag(tag: str, current_user=Depends(get_current_user)):
    """Permite que o admin adicione novas tags."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Somente administradores podem adicionar tags")

    if tag in DEFAULT_TAGS:
        raise HTTPException(status_code=400, detail="Tag já existe")

    DEFAULT_TAGS.append(tag)
    return {"message": f"Tag '{tag}' adicionada com sucesso"}
