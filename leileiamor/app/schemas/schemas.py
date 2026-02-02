"""
Schemas Pydantic para validação e serialização de dados
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
from decimal import Decimal


# ============================================================================
# SCHEMAS DE USUÁRIO
# ============================================================================

class UsuarioBase(BaseModel):
    """Schema base para usuário"""
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuário"""
    senha: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    """Schema para atualização de usuário"""
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    senha: Optional[str] = Field(None, min_length=6)


class UsuarioResponse(UsuarioBase):
    """Schema de resposta de usuário"""
    id_usuario: int
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE AUTENTICAÇÃO
# ============================================================================

class Token(BaseModel):
    """Schema de resposta do token"""
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    """Schema de requisição de login"""
    email: str
    senha: str


# ============================================================================
# SCHEMAS DE CONTA
# ============================================================================

class ContaBase(BaseModel):
    """Schema base para conta"""
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: str = Field(..., min_length=1, max_length=50)  # Ex: "corrente", "poupanca", "investimento"
    saldo: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0)


class ContaCreate(ContaBase):
    """Schema para criação de conta"""
    pass


class ContaUpdate(BaseModel):
    """Schema para atualização de conta"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[str] = Field(None, min_length=1, max_length=50)
    saldo: Optional[Decimal] = Field(None, ge=0)


class ContaResponse(ContaBase):
    """Schema de resposta de conta"""
    id_conta: int
    id_usuario: int
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE CATEGORIA
# ============================================================================

class CategoriaBase(BaseModel):
    """Schema base para categoria"""
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: str = Field(..., pattern="^(receita|despesa)$")  # Apenas "receita" ou "despesa"


class CategoriaCreate(CategoriaBase):
    """Schema para criação de categoria"""
    pass


class CategoriaUpdate(BaseModel):
    """Schema para atualização de categoria"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[str] = Field(None, pattern="^(receita|despesa)$")


class CategoriaResponse(CategoriaBase):
    """Schema de resposta de categoria"""
    id_categoria: int
    id_usuario: int
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE TRANSAÇÃO
# ============================================================================

class TransacaoBase(BaseModel):
    """Schema base para transação"""
    valor: Decimal = Field(..., gt=0)
    data: date
    descricao: Optional[str] = Field(None, max_length=255)
    tipo: str = Field(..., pattern="^(receita|despesa)$")  # Apenas "receita" ou "despesa"
    id_conta: int = Field(..., gt=0)
    id_categoria: int = Field(..., gt=0)


class TransacaoCreate(TransacaoBase):
    """Schema para criação de transação"""
    pass


class TransacaoUpdate(BaseModel):
    """Schema para atualização de transação"""
    valor: Optional[Decimal] = Field(None, gt=0)
    data: Optional[date] = None
    descricao: Optional[str] = Field(None, max_length=255)
    tipo: Optional[str] = Field(None, pattern="^(receita|despesa)$")
    id_conta: Optional[int] = Field(None, gt=0)
    id_categoria: Optional[int] = Field(None, gt=0)


class TransacaoResponse(TransacaoBase):
    """Schema de resposta de transação"""
    id_transacao: int
    id_usuario: int
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS DE RESPOSTA GENÉRICOS
# ============================================================================

class MessageResponse(BaseModel):
    """Schema para mensagens de resposta"""
    message: str
    detail: Optional[str] = None