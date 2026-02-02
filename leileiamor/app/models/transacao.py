"""
Modelo de Transação (SQLAlchemy ORM)
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Transacao(Base):
    # ============================================================================
    # === AJUSTE SEUS DADOS AQUI ===
    # Nome da tabela no banco de dados
    __tablename__ = "transacao"
    
    # Nomes das colunas no banco de dados
    id_transacao = Column(Integer, primary_key=True, index=True)
    valor = Column(Numeric(10, 2), nullable=False)
    data = Column(Date, nullable=False)
    descricao = Column(String)
    tipo = Column(String, nullable=False)  # "receita" ou "despesa"
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    id_conta = Column(Integer, ForeignKey("conta.id_conta"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)
    # ============================================================================
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="transacoes")
    conta = relationship("Conta", back_populates="transacoes")
    categoria = relationship("Categoria", back_populates="transacoes")
    
    def __repr__(self):
        return f"<Transacao(id={self.id_transacao}, valor={self.valor}, tipo='{self.tipo}', data={self.data})>"