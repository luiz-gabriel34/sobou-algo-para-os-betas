"""
Rotas de Usuários (CRUD Completo)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.models.usuario import Usuario
from app.schemas.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse, MessageResponse

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/me", response_model=UsuarioResponse)
def get_current_user_info(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado
    """
    return current_user


@router.get("/", response_model=List[UsuarioResponse])
def list_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todos os usuários (READ)
    Requer autenticação
    """
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios


@router.get("/{id_usuario}", response_model=UsuarioResponse)
def get_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca usuário por ID (READ)
    Requer autenticação
    """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com ID {id_usuario} não encontrado"
        )
    return usuario


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Cria novo usuário (CREATE)
    NÃO requer autenticação (registro público)
    """
    # Verifica se email já existe
    existing_email = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Cria novo usuário
    new_usuario = Usuario(
        nome=usuario_data.nome,
        email=usuario_data.email,
        senha=get_password_hash(usuario_data.senha)
    )
    
    db.add(new_usuario)
    db.commit()
    db.refresh(new_usuario)
    
    return new_usuario


@router.put("/{id_usuario}", response_model=UsuarioResponse)
def update_usuario(
    id_usuario: int,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza usuário existente (UPDATE)
    Requer autenticação JWT
    Usuário só pode atualizar seus próprios dados
    """
    # Verifica se é o próprio usuário
    if current_user.id_usuario != id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para alterar este usuário"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com ID {id_usuario} não encontrado"
        )
    
    # Atualiza apenas campos fornecidos
    update_data = usuario_data.model_dump(exclude_unset=True)
    
    # Se senha foi fornecida, faz hash
    if "senha" in update_data:
        update_data["senha"] = get_password_hash(update_data["senha"])
    
    # Verifica duplicação de email
    if "email" in update_data and update_data["email"] != usuario.email:
        existing = db.query(Usuario).filter(Usuario.email == update_data["email"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
    
    # Aplica atualizações
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    
    return usuario


@router.delete("/{id_usuario}", response_model=MessageResponse)
def delete_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta usuário (DELETE)
    Requer autenticação JWT
    Usuário só pode deletar sua própria conta
    """
    # Verifica se é o próprio usuário
    if current_user.id_usuario != id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar este usuário"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com ID {id_usuario} não encontrado"
        )
    
    db.delete(usuario)
    db.commit()
    
    return {
        "message": "Usuário deletado com sucesso",
        "detail": f"Usuário {usuario.nome} (ID: {id_usuario}) foi removido"
    }