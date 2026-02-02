"""
Rotas de Transações (CRUD Completo)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.transacao import Transacao
from app.models.conta import Conta
from app.models.categoria import Categoria
from app.schemas.schemas import TransacaoCreate, TransacaoUpdate, TransacaoResponse, MessageResponse

router = APIRouter(prefix="/transacoes", tags=["Transações"])


@router.get("/", response_model=List[TransacaoResponse])
def list_transacoes(
    skip: int = 0,
    limit: int = 100,
    tipo: str = None,  # Filtro opcional por tipo (receita/despesa)
    id_conta: int = None,  # Filtro opcional por conta
    id_categoria: int = None,  # Filtro opcional por categoria
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas as transações do usuário autenticado (READ)
    Filtros opcionais: ?tipo=receita&id_conta=1&id_categoria=2
    """
    query = db.query(Transacao).filter(Transacao.id_usuario == current_user.id_usuario)
    
    if tipo:
        query = query.filter(Transacao.tipo == tipo)
    if id_conta:
        query = query.filter(Transacao.id_conta == id_conta)
    if id_categoria:
        query = query.filter(Transacao.id_categoria == id_categoria)
    
    transacoes = query.order_by(Transacao.data.desc()).offset(skip).limit(limit).all()
    return transacoes


@router.get("/{id_transacao}", response_model=TransacaoResponse)
def get_transacao(
    id_transacao: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca transação por ID (READ)
    Apenas transações do usuário autenticado
    """
    transacao = db.query(Transacao).filter(
        Transacao.id_transacao == id_transacao,
        Transacao.id_usuario == current_user.id_usuario
    ).first()
    
    if not transacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transação com ID {id_transacao} não encontrada"
        )
    return transacao


@router.post("/", response_model=TransacaoResponse, status_code=status.HTTP_201_CREATED)
def create_transacao(
    transacao_data: TransacaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria nova transação (CREATE)
    Requer autenticação JWT
    Atualiza automaticamente o saldo da conta
    """
    # Valida se conta pertence ao usuário
    conta = db.query(Conta).filter(
        Conta.id_conta == transacao_data.id_conta,
        Conta.id_usuario == current_user.id_usuario
    ).first()
    
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conta com ID {transacao_data.id_conta} não encontrada"
        )
    
    # Valida se categoria pertence ao usuário
    categoria = db.query(Categoria).filter(
        Categoria.id_categoria == transacao_data.id_categoria,
        Categoria.id_usuario == current_user.id_usuario
    ).first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com ID {transacao_data.id_categoria} não encontrada"
        )
    
    # Valida se tipo da transação corresponde ao tipo da categoria
    if transacao_data.tipo != categoria.tipo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo da transação ({transacao_data.tipo}) não corresponde ao tipo da categoria ({categoria.tipo})"
        )
    
    # Cria nova transação
    new_transacao = Transacao(
        valor=transacao_data.valor,
        data=transacao_data.data,
        descricao=transacao_data.descricao,
        tipo=transacao_data.tipo,
        id_usuario=current_user.id_usuario,
        id_conta=transacao_data.id_conta,
        id_categoria=transacao_data.id_categoria
    )
    
    # Atualiza saldo da conta
    if transacao_data.tipo == "receita":
        conta.saldo += Decimal(str(transacao_data.valor))
    else:  # despesa
        conta.saldo -= Decimal(str(transacao_data.valor))
    
    db.add(new_transacao)
    db.commit()
    db.refresh(new_transacao)
    
    return new_transacao


@router.put("/{id_transacao}", response_model=TransacaoResponse)
def update_transacao(
    id_transacao: int,
    transacao_data: TransacaoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza transação existente (UPDATE)
    Requer autenticação JWT
    Recalcula saldo da conta se valor for alterado
    """
    transacao = db.query(Transacao).filter(
        Transacao.id_transacao == id_transacao,
        Transacao.id_usuario == current_user.id_usuario
    ).first()
    
    if not transacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transação com ID {id_transacao} não encontrada"
        )
    
    # Guarda valores antigos para recalcular saldo
    valor_antigo = transacao.valor
    conta_antiga = transacao.conta
    tipo_antigo = transacao.tipo
    
    # Atualiza apenas campos fornecidos
    update_data = transacao_data.model_dump(exclude_unset=True)
    
    # Valida nova conta se fornecida
    if "id_conta" in update_data:
        nova_conta = db.query(Conta).filter(
            Conta.id_conta == update_data["id_conta"],
            Conta.id_usuario == current_user.id_usuario
        ).first()
        if not nova_conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conta com ID {update_data['id_conta']} não encontrada"
            )
    
    # Valida nova categoria se fornecida
    if "id_categoria" in update_data:
        nova_categoria = db.query(Categoria).filter(
            Categoria.id_categoria == update_data["id_categoria"],
            Categoria.id_usuario == current_user.id_usuario
        ).first()
        if not nova_categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria com ID {update_data['id_categoria']} não encontrada"
            )
    
    # Aplica atualizações
    for field, value in update_data.items():
        setattr(transacao, field, value)
    
    # Recalcula saldo
    # 1. Reverte valor antigo
    if tipo_antigo == "receita":
        conta_antiga.saldo -= Decimal(str(valor_antigo))
    else:
        conta_antiga.saldo += Decimal(str(valor_antigo))
    
    # 2. Aplica novo valor
    conta_nova = transacao.conta
    if transacao.tipo == "receita":
        conta_nova.saldo += Decimal(str(transacao.valor))
    else:
        conta_nova.saldo -= Decimal(str(transacao.valor))
    
    db.commit()
    db.refresh(transacao)
    
    return transacao


@router.delete("/{id_transacao}", response_model=MessageResponse)
def delete_transacao(
    id_transacao: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta transação (DELETE)
    Requer autenticação JWT
    Atualiza saldo da conta ao deletar
    """
    transacao = db.query(Transacao).filter(
        Transacao.id_transacao == id_transacao,
        Transacao.id_usuario == current_user.id_usuario
    ).first()
    
    if not transacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transação com ID {id_transacao} não encontrada"
        )
    
    # Reverte o valor no saldo da conta
    conta = transacao.conta
    if transacao.tipo == "receita":
        conta.saldo -= Decimal(str(transacao.valor))
    else:  # despesa
        conta.saldo += Decimal(str(transacao.valor))
    
    db.delete(transacao)
    db.commit()
    
    return {
        "message": "Transação deletada com sucesso",
        "detail": f"Transação de {transacao.tipo} no valor de R$ {transacao.valor} foi removida"
    }