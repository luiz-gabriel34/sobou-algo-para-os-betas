"""
Modelo de Categoria (SQLAlchemy ORM)
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Categoria(Base):
    # ============================================================================
    # === AJUSTE SEUS DADOS AQUI ===
    # Nome da tabela no banco de dados
    __tablename__ = "categoria"
    
    # Nomes das colunas no banco de dados
    id_categoria = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # "receita" ou "despesa"
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    # ============================================================================
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="categorias")
    transacoes = relationship("Transacao", back_populates="categoria", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Categoria(id={self.id_categoria}, nome='{self.nome}', tipo='{self.tipo}')>"