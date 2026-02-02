"""
Módulo de Seed de Dados para Teste
"""
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from app.models.conta import Conta
from app.models.categoria import Categoria
from app.models.transacao import Transacao


def seed_database(db: Session) -> dict:
    """
    Popula o banco de dados com dados fictícios para teste
    
    Returns:
        dict: Informações sobre o que foi criado
    """
    # Verifica se já existem dados
    existing_users = db.query(Usuario).count()
    if existing_users > 0:
        raise ValueError(f"Banco já contém {existing_users} usuários. Use limpar-dados primeiro.")
    
    print("🌱 Iniciando seed do banco de dados...")
    
    # ========================================
    # PASSO 1: CRIAR USUÁRIOS
    # ========================================
    print("👤 Criando usuários...")
    
    # Cria hash das senhas ANTES de criar os objetos
    # Senhas curtas: exatamente 8 caracteres
    hash_joao = get_password_hash("senha123")
    hash_maria = get_password_hash("senha456")
    
    print(f"   Hash João (tamanho): {len(hash_joao)} caracteres")
    print(f"   Hash Maria (tamanho): {len(hash_maria)} caracteres")
    
    usuario1 = Usuario(
        nome="João Silva",
        email="joao@example.com",
        senha=hash_joao
    )
    usuario2 = Usuario(
        nome="Maria Santos",
        email="maria@example.com",
        senha=hash_maria
    )
    
    db.add(usuario1)
    db.add(usuario2)
    db.flush()  # Gera os IDs
    
    print(f"   ✅ {usuario1.nome} (ID: {usuario1.id_usuario})")
    print(f"   ✅ {usuario2.nome} (ID: {usuario2.id_usuario})")
    
    # ========================================
    # PASSO 2: CRIAR CONTAS
    # ========================================
    print("💰 Criando contas...")
    
    contas = [
        Conta(nome="Conta Corrente", saldo=Decimal("5000.00"), tipo="corrente", id_usuario=usuario1.id_usuario),
        Conta(nome="Poupança", saldo=Decimal("10000.00"), tipo="poupanca", id_usuario=usuario1.id_usuario),
        Conta(nome="Investimentos", saldo=Decimal("25000.00"), tipo="investimento", id_usuario=usuario1.id_usuario),
        Conta(nome="Conta Corrente", saldo=Decimal("3000.00"), tipo="corrente", id_usuario=usuario2.id_usuario),
        Conta(nome="Carteira Digital", saldo=Decimal("500.00"), tipo="digital", id_usuario=usuario2.id_usuario),
    ]
    
    for conta in contas:
        db.add(conta)
    
    db.flush()
    
    for conta in contas:
        print(f"   ✅ {conta.nome} (ID: {conta.id_conta}, Saldo: R$ {conta.saldo})")
    
    # ========================================
    # PASSO 3: CRIAR CATEGORIAS
    # ========================================
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
    
    for cat in categorias:
        print(f"   ✅ {cat.nome} - {cat.tipo} (ID: {cat.id_categoria})")
    
    # ========================================
    # PASSO 4: CRIAR TRANSAÇÕES
    # ========================================
    print("💸 Criando transações...")
    
    conta_corrente = contas[0]
    
    transacoes_lista = [
        Transacao(
            valor=Decimal("5000.00"),
            data=date(2025, 1, 1),
            descricao="Salário Janeiro",
            tipo="receita",
            id_usuario=usuario1.id_usuario,
            id_conta=conta_corrente.id_conta,
            id_categoria=categorias[0].id_categoria
        ),
        Transacao(
            valor=Decimal("1500.00"),
            data=date(2025, 1, 15),
            descricao="Projeto Freelance",
            tipo="receita",
            id_usuario=usuario1.id_usuario,
            id_conta=conta_corrente.id_conta,
            id_categoria=categorias[1].id_categoria
        ),
        Transacao(
            valor=Decimal("800.00"),
            data=date(2025, 1, 5),
            descricao="Aluguel",
            tipo="despesa",
            id_usuario=usuario1.id_usuario,
            id_conta=conta_corrente.id_conta,
            id_categoria=categorias[5].id_categoria
        ),
        Transacao(
            valor=Decimal("250.00"),
            data=date(2025, 1, 8),
            descricao="Mercado",
            tipo="despesa",
            id_usuario=usuario1.id_usuario,
            id_conta=conta_corrente.id_conta,
            id_categoria=categorias[3].id_categoria
        ),
        Transacao(
            valor=Decimal("150.00"),
            data=date(2025, 1, 10),
            descricao="Gasolina",
            tipo="despesa",
            id_usuario=usuario1.id_usuario,
            id_conta=conta_corrente.id_conta,
            id_categoria=categorias[4].id_categoria
        ),
    ]
    
    for trans in transacoes_lista:
        db.add(trans)
    
    db.flush()
    
    for trans in transacoes_lista:
        print(f"   ✅ {trans.descricao} - {trans.tipo} R$ {trans.valor} (ID: {trans.id_transacao})")
    
    # ========================================
    # COMMIT FINAL - IMPORTANTE!
    # ========================================
    print("💾 Salvando no banco de dados...")
    db.commit()
    print("✅ Commit realizado com sucesso!")
    
    return {
        "usuarios": 2,
        "contas": 5,
        "categorias": 6,
        "transacoes": 5,
        "login_teste": {
            "email": "joao@example.com",
            "senha": "senha123"
        }
    }