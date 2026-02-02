"""
Arquivo Principal da API FastAPI
Contém configuração do app, seed de dados e rotas
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal

from app.core.database import engine, Base, get_db
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from app.models.conta import Conta
from app.models.categoria import Categoria
from app.models.transacao import Transacao
from app.routers import auth, usuarios, contas, categorias, transacoes
from app.schemas.schemas import MessageResponse
from app.core.seed import seed_database as seed_db_function

# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Configuração do Swagger para autenticação JWT
app = FastAPI(
    title="API de Controle Financeiro",
    description="""
    ## API RESTful completa para controle financeiro pessoal
    
    ### Funcionalidades:
    * 🔐 **Autenticação JWT** - Login seguro com tokens
    * 👤 **Gerenciamento de Usuários** - CRUD completo
    * 💰 **Contas** - Gerencie suas contas bancárias
    * 📑 **Categorias** - Organize receitas e despesas
    * 💸 **Transações** - Registre e acompanhe movimentações financeiras
    
    ### Como usar a autenticação no Swagger:
    1. Execute o endpoint `POST /seed` para criar dados de teste
    2. Faça login em `POST /auth/login` (email: joao@example.com, senha: senha123)
    3. Copie o `access_token` retornado
    4. Clique no botão **Authorize** 🔓 (canto superior direito)
    5. Cole o token e clique em **Authorize**
    6. Agora você pode acessar as rotas protegidas! 🎉
    
    ### Estrutura do Sistema:
    - **Usuário** possui várias **Contas** e **Categorias**
    - Cada **Transação** está vinculada a uma Conta e Categoria
    - Saldo das contas é atualizado automaticamente com as transações
    """,
    version="2.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
)

# Registra os routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(contas.router)
app.include_router(categorias.router)
app.include_router(transacoes.router)


@app.get("/", tags=["Root"])
def root():
    """
    Endpoint raiz da API
    """
    return {
        "message": "Bem-vindo à API de Controle Financeiro!",
        "docs": "/docs",
        "version": "2.0.0",
        "seed": "/seed - Execute para criar dados de teste",
        "endpoints": {
            "auth": "/auth/login",
            "usuarios": "/usuarios",
            "contas": "/contas",
            "categorias": "/categorias",
            "transacoes": "/transacoes"
        }
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Verifica se a API está funcionando
    """
    return {"status": "healthy", "message": "API está online"}


# ============================================================================
# ENDPOINT PARA LIMPAR DADOS
# ============================================================================

@app.delete("/limpar-dados", response_model=MessageResponse, tags=["Utilitários"])
def limpar_dados(db: Session = Depends(get_db)):
    """
    ⚠️ CUIDADO! Este endpoint deleta TODOS os dados do banco!
    
    Use apenas em ambiente de desenvolvimento/teste.
    Útil para limpar e reexecutar o seed.
    """
    try:
        print("🗑️ Iniciando limpeza de dados...")
        
        # Deleta na ordem correta (por causa das foreign keys)
        trans_count = db.query(Transacao).delete()
        cat_count = db.query(Categoria).delete()
        conta_count = db.query(Conta).delete()
        user_count = db.query(Usuario).delete()
        
        db.commit()
        
        print(f"✅ Deletados: {user_count} usuários, {conta_count} contas, {cat_count} categorias, {trans_count} transações")
        
        return {
            "message": "🗑️ Todos os dados foram deletados com sucesso!",
            "detail": f"Removidos: {user_count} usuários, {conta_count} contas, {cat_count} categorias, {trans_count} transações. Você pode executar /seed novamente."
        }
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao limpar dados: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar dados: {str(e)}"
        )


# ============================================================================
# FUNÇÃO DE SEED - DADOS FICTÍCIOS PARA TESTE
# ============================================================================

# ... (mantenha todos os imports existentes) ...

@app.post("/seed", response_model=MessageResponse, tags=["Utilitários"])
def seed_database(db: Session = Depends(get_db)):
    """
    Popula o banco de dados com dados fictícios para teste
    """
    try:
        # VERIFICAÇÃO 1: Verifica se já existem dados
        existing_count = db.query(Usuario).count()
        if existing_count > 0:
            return {
                "message": "⚠️ Banco já contém dados!",
                "detail": f"Encontrados {existing_count} usuários. Use DELETE /limpar-dados primeiro."
            }
        
        print("🌱 Iniciando seed...")
        
        # PASSO 1: Criar usuários com SHA256 (64 caracteres fixos)
        print("👤 Criando usuários...")
        
        senha_joao = get_password_hash("senha123")
        senha_maria = get_password_hash("senha456")
        
        usuario1 = Usuario(
            nome="João Silva",
            email="joao@example.com",
            senha=senha_joao
        )
        usuario2 = Usuario(
            nome="Maria Santos",
            email="maria@example.com",
            senha=senha_maria
        )
        
        db.add(usuario1)
        db.add(usuario2)
        db.flush()  # Gera IDs sem commit ainda
        
        print(f"✅ Usuários criados: {usuario1.id_usuario}, {usuario2.id_usuario}")
        
        # PASSO 2: Criar contas
        print("💰 Criando contas...")
        contas = [
            Conta(nome="Conta Corrente", saldo=Decimal("5000.00"), tipo="corrente", id_usuario=usuario1.id_usuario),
            Conta(nome="Poupança", saldo=Decimal("10000.00"), tipo="poupanca", id_usuario=usuario1.id_usuario),
            Conta(nome="Investimentos", saldo=Decimal("25000.00"), tipo="investimento", id_usuario=usuario1.id_usuario),
            Conta(nome="Conta Corrente", saldo=Decimal("3000.00"), tipo="corrente", id_usuario=usuario2.id_usuario),
            Conta(nome="Carteira Digital", saldo=Decimal("500.00"), tipo="digital", id_usuario=usuario2.id_usuario),
        ]
        
        for c in contas:
            db.add(c)
        db.flush()
        print(f"✅ {len(contas)} contas criadas")
        
        # PASSO 3: Criar categorias
        print("📑 Criando categorias...")
        categorias = [
            Categoria(nome="Salário", tipo="receita", id_usuario=usuario1.id_usuario),
            Categoria(nome="Freelance", tipo="receita", id_usuario=usuario1.id_usuario),
            Categoria(nome="Investimentos", tipo="receita", id_usuario=usuario1.id_usuario),
            Categoria(nome="Alimentação", tipo="despesa", id_usuario=usuario1.id_usuario),
            Categoria(nome="Transporte", tipo="despesa", id_usuario=usuario1.id_usuario),
            Categoria(nome="Moradia", tipo="despesa", id_usuario=usuario1.id_usuario),
        ]
        
        for cat in categorias:
            db.add(cat)
        db.flush()
        print(f"✅ {len(categorias)} categorias criadas")
        
        # PASSO 4: Criar transações
        print("💸 Criando transações...")
        conta_cc = contas[0]  # Conta corrente do João
        
        transacoes = [
            Transacao(valor=Decimal("5000.00"), data=date(2025, 1, 1), descricao="Salário Janeiro", tipo="receita", id_usuario=usuario1.id_usuario, id_conta=conta_cc.id_conta, id_categoria=categorias[0].id_categoria),
            Transacao(valor=Decimal("1500.00"), data=date(2025, 1, 15), descricao="Projeto Freelance", tipo="receita", id_usuario=usuario1.id_usuario, id_conta=conta_cc.id_conta, id_categoria=categorias[1].id_categoria),
            Transacao(valor=Decimal("800.00"), data=date(2025, 1, 5), descricao="Aluguel", tipo="despesa", id_usuario=usuario1.id_usuario, id_conta=conta_cc.id_conta, id_categoria=categorias[5].id_categoria),
            Transacao(valor=Decimal("250.00"), data=date(2025, 1, 8), descricao="Mercado", tipo="despesa", id_usuario=usuario1.id_usuario, id_conta=conta_cc.id_conta, id_categoria=categorias[3].id_categoria),
            Transacao(valor=Decimal("150.00"), data=date(2025, 1, 10), descricao="Gasolina", tipo="despesa", id_usuario=usuario1.id_usuario, id_conta=conta_cc.id_conta, id_categoria=categorias[4].id_categoria),
        ]
        
        for t in transacoes:
            db.add(t)
        db.flush()
        print(f"✅ {len(transacoes)} transações criadas")
        
        # COMMIT FINAL
        print("💾 Fazendo commit...")
        db.commit()
        print("✅ Commit realizado!")
        
        # VERIFICAÇÃO FINAL
        total_users = db.query(Usuario).count()
        total_contas = db.query(Conta).count()
        total_cat = db.query(Categoria).count()
        total_trans = db.query(Transacao).count()
        
        return {
            "message": "🎉 Seed executado com sucesso!",
            "detail": (
                f"Criados: {total_users} usuários, {total_contas} contas, "
                f"{total_cat} categorias, {total_trans} transações. "
                f"Login: joao@example.com / senha123"
            )
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        erro_completo = traceback.format_exc()
        print(f"❌ ERRO: {erro_completo}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro: {str(e)} | Verifique o console do servidor para detalhes"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)