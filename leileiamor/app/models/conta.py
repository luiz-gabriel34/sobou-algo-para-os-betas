"""
Modelo de Conta (SQLAlchemy ORM)
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Conta(Base):
    # ============================================================================
    # === AJUSTE SEUS DADOS AQUI ===
    # Nome da tabela no banco de dados
    __tablename__ = "conta"
    
    # Nomes das colunas no banco de dados
    id_conta = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    saldo = Column(Numeric(10, 2), nullable=False, default=0.00)
    tipo = Column(String, nullable=False)  # Ex: "corrente", "poupança", "investimento"
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    # ============================================================================
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="contas")
    transacoes = relationship("Transacao", back_populates="conta", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conta(id={self.id_conta}, nome='{self.nome}', saldo={self.saldo}, tipo='{self.tipo}')>"