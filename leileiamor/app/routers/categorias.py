"""
Rotas de Categorias (CRUD Completo)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.schemas.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse, MessageResponse

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("/", response_model=List[CategoriaResponse])
def list_categorias(
    skip: int = 0,
    limit: int = 100,
    tipo: str = None,  # Filtro opcional por tipo (receita/despesa)
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas as categorias do usuário autenticado (READ)
    Pode filtrar por tipo: ?tipo=receita ou ?tipo=despesa
    """
    query = db.query(Categoria).filter(Categoria.id_usuario == current_user.id_usuario)
    
    if tipo:
        query = query.filter(Categoria.tipo == tipo)
    
    categorias = query.offset(skip).limit(limit).all()
    return categorias


@router.get("/{id_categoria}", response_model=CategoriaResponse)
def get_categoria(
    id_categoria: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca categoria por ID (READ)
    Apenas categorias do usuário autenticado
    """
    categoria = db.query(Categoria).filter(
        Categoria.id_categoria == id_categoria,
        Categoria.id_usuario == current_user.id_usuario
    ).first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com ID {id_categoria} não encontrada"
        )
    return categoria


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def create_categoria(
    categoria_data: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria nova categoria (CREATE)
    Requer autenticação JWT
    """
    # Cria nova categoria associada ao usuário autenticado
    new_categoria = Categoria(
        nome=categoria_data.nome,
        tipo=categoria_data.tipo,
        id_usuario=current_user.id_usuario
    )
    
    db.add(new_categoria)
    db.commit()
    db.refresh(new_categoria)
    
    return new_categoria


@router.put("/{id_categoria}", response_model=CategoriaResponse)
def update_categoria(
    id_categoria: int,
    categoria_data: CategoriaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza categoria existente (UPDATE)
    Requer autenticação JWT
    """
    categoria = db.query(Categoria).filter(
        Categoria.id_categoria == id_categoria,
        Categoria.id_usuario == current_user.id_usuario
    ).first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com ID {id_categoria} não encontrada"
        )
    
    # Atualiza apenas campos fornecidos
    update_data = categoria_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(categoria, field, value)
    
    db.commit()
    db.refresh(categoria)
    
    return categoria


@router.delete("/{id_categoria}", response_model=MessageResponse)
def delete_categoria(
    id_categoria: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta categoria (DELETE)
    Requer autenticação JWT
    """
    categoria = db.query(Categoria).filter(
        Categoria.id_categoria == id_categoria,
        Categoria.id_usuario == current_user.id_usuario
    ).first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com ID {id_categoria} não encontrada"
        )
    
    db.delete(categoria)
    db.commit()
    
    return {
        "message": "Categoria deletada com sucesso",
        "detail": f"Categoria {categoria.nome} (ID: {id_categoria}) foi removida"
    }