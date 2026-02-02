"""
Configurações do Banco de Dados e Aplicação
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ============================================================================
# === AJUSTE SEUS DADOS AQUI ===
# ============================================================================
# Configuração da URL do Banco de Dados
# Exemplos:
# PostgreSQL: "postgresql://usuario:senha@localhost:5432/nome_do_banco"
# MySQL: "mysql+pymysql://usuario:senha@localhost:3306/nome_do_banco"
# SQLite: "sqlite:///./banco.db"
DATABASE_URL = "postgresql://postgres:kpdn2008@localhost:5432/Dream_Lin"
# Chave secreta para geração de tokens JWT (ALTERE PARA UM VALOR SEGURO!)
# Pode ter até 64 caracteres
SECRET_KEY = "1234"
# ============================================================================

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Criação do engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# SessionLocal para criar sessões de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos ORM
Base = declarative_base()


def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:

        db.close()
