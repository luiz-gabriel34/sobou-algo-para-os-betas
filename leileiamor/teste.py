"""
Script de Teste de Conexão com o Banco de Dados
Execute este arquivo separadamente para validar a conexão com o banco
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# ============================================================================
# === AJUSTE SEUS DADOS AQUI ===
# ============================================================================
# Configuração da URL do Banco de Dados
# DEVE SER A MESMA URL usada em app/core/database.py
# 
# Exemplos:
# PostgreSQL: "postgresql://usuario:senha@localhost:5432/nome_do_banco"
# MySQL: "mysql+pymysql://usuario:senha@localhost:3306/nome_do_banco"
# SQLite: "sqlite:///./banco.db"
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/leloca"
# ============================================================================


def test_connection():
    """
    Testa a conexão com o banco de dados
    """
    print("=" * 70)
    print("TESTE DE CONEXÃO COM O BANCO DE DADOS")
    print("=" * 70)
    print(f"\n📍 Database URL: {DATABASE_URL}\n")
    
    try:
        # Cria engine
        print("🔄 Criando engine SQLAlchemy...")
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
        )
        
        # Tenta conectar
        print("🔄 Tentando conectar ao banco de dados...")
        with engine.connect() as connection:
            # Executa query simples para validar conexão
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            
            print("✅ CONEXÃO BEM-SUCEDIDA!\n")
            
            # Informações adicionais
            print("📊 Informações da conexão:")
            print(f"   - Driver: {engine.driver}")
            print(f"   - Dialect: {engine.dialect.name}")
            
            # Lista tabelas existentes (se possível)
            try:
                from sqlalchemy import inspect
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                
                if tables:
                    print(f"\n📋 Tabelas encontradas ({len(tables)}):")
                    for table in tables:
                        print(f"   - {table}")
                else:
                    print("\n⚠️  Nenhuma tabela encontrada no banco de dados")
                    print("   Execute a aplicação principal para criar as tabelas")
            except Exception as e:
                print(f"\n⚠️  Não foi possível listar tabelas: {e}")
            
            print("\n" + "=" * 70)
            print("✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("=" * 70)
            return True
            
    except SQLAlchemyError as e:
        print("❌ ERRO DE CONEXÃO COM O BANCO DE DADOS!\n")
        print("📝 Detalhes do erro:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        print("\n💡 Possíveis soluções:")
        print("   1. Verifique se a URL do banco está correta")
        print("   2. Verifique se o banco de dados existe")
        print("   3. Verifique as credenciais (usuário/senha)")
        print("   4. Verifique se o servidor do banco está rodando")
        print("   5. Para PostgreSQL/MySQL, instale o driver necessário:")
        print("      - PostgreSQL: uv add psycopg2-binary")
        print("      - MySQL: uv add pymysql")
        print("\n" + "=" * 70)
        return False
        
    except Exception as e:
        print("❌ ERRO INESPERADO!\n")
        print("📝 Detalhes do erro:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        print("\n" + "=" * 70)
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)