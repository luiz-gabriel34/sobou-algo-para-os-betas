"""
Rotas de Autenticação
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import verify_password, create_access_token
from app.models.usuario import Usuario
from app.schemas.schemas import Token, LoginRequest

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login
    Valida credenciais (email e senha) e retorna token JWT
    """
    # Busca usuário no banco de dados pelo email
    user = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    
    # Valida se usuário existe e senha está correta
    if not user or not verify_password(login_data.senha, user.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria token de acesso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }