"""
Modelo de Usuário (SQLAlchemy ORM)
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Usuario(Base):
    # ============================================================================
    # === AJUSTE SEUS DADOS AQUI ===
    # Nome da tabela no banco de dados
    __tablename__ = "usuario"
    
    # Nomes das colunas no banco de dados
    id_usuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)  # Armazena hash da senha
    # ============================================================================
    
    # Relacionamentos
    contas = relationship("Conta", back_populates="usuario", cascade="all, delete-orphan")
    categorias = relationship("Categoria", back_populates="usuario", cascade="all, delete-orphan")
    transacoes = relationship("Transacao", back_populates="usuario", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, nome='{self.nome}', email='{self.email}')>"