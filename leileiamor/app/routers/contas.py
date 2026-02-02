"""
Rotas de Contas (CRUD Completo)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.conta import Conta
from app.schemas.schemas import ContaCreate, ContaUpdate, ContaResponse, MessageResponse

router = APIRouter(prefix="/contas", tags=["Contas"])


@router.get("/", response_model=List[ContaResponse])
def list_contas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas as contas do usuário autenticado (READ)
    """
    contas = db.query(Conta).filter(
        Conta.id_usuario == current_user.id_usuario
    ).offset(skip).limit(limit).all()
    return contas


@router.get("/{id_conta}", response_model=ContaResponse)
def get_conta(
    id_conta: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca conta por ID (READ)
    Apenas contas do usuário autenticado
    """
    conta = db.query(Conta).filter(
        Conta.id_conta == id_conta,
        Conta.id_usuario == current_user.id_usuario
    ).first()
    
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conta com ID {id_conta} não encontrada"
        )
    return conta


@router.post("/", response_model=ContaResponse, status_code=status.HTTP_201_CREATED)
def create_conta(
    conta_data: ContaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria nova conta (CREATE)
    Requer autenticação JWT
    """
    # Cria nova conta associada ao usuário autenticado
    new_conta = Conta(
        nome=conta_data.nome,
        saldo=conta_data.saldo,
        tipo=conta_data.tipo,
        id_usuario=current_user.id_usuario
    )
    
    db.add(new_conta)
    db.commit()
    db.refresh(new_conta)
    
    return new_conta


@router.put("/{id_conta}", response_model=ContaResponse)
def update_conta(
    id_conta: int,
    conta_data: ContaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza conta existente (UPDATE)
    Requer autenticação JWT
    """
    conta = db.query(Conta).filter(
        Conta.id_conta == id_conta,
        Conta.id_usuario == current_user.id_usuario
    ).first()
    
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conta com ID {id_conta} não encontrada"
        )
    
    # Atualiza apenas campos fornecidos
    update_data = conta_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(conta, field, value)
    
    db.commit()
    db.refresh(conta)
    
    return conta


@router.delete("/{id_conta}", response_model=MessageResponse)
def delete_conta(
    id_conta: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta conta (DELETE)
    Requer autenticação JWT
    """
    conta = db.query(Conta).filter(
        Conta.id_conta == id_conta,
        Conta.id_usuario == current_user.id_usuario
    ).first()
    
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conta com ID {id_conta} não encontrada"
        )
    
    db.delete(conta)
    db.commit()
    
    return {
        "message": "Conta deletada com sucesso",
        "detail": f"Conta {conta.nome} (ID: {id_conta}) foi removida"
    }