
-- Configurar encoding UTF-8
SET CLIENT_ENCODING TO 'UTF8';

-- Ativar extensão para criptografia
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================
-- CRIAÇÃO DAS TABELAS
-- ============================================

-- TABELA USUARIO
CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nome_usuario VARCHAR(50) NOT NULL,
    email_usuario VARCHAR(50) NOT NULL UNIQUE,
    senha_usuario VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_email_formato CHECK (email_usuario ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- TABELA CATEGORIA
CREATE TABLE categoria (
    id_categoria SERIAL PRIMARY KEY,
    nome_categoria VARCHAR(50) NOT NULL,
    tipo_categoria VARCHAR(20) NOT NULL,
    usuario_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    CONSTRAINT check_tipo_categoria CHECK (tipo_categoria IN ('ENTRADA', 'SAIDA'))
);

-- TABELA CONTA
CREATE TABLE conta (
    id_conta SERIAL PRIMARY KEY,
    nome_conta VARCHAR(50) NOT NULL,
    saldo_conta DECIMAL(10,2) DEFAULT 0 CHECK (saldo_conta >= 0),
    tipo_conta VARCHAR(20) NOT NULL,
    usuario_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    CONSTRAINT check_tipo_conta CHECK (tipo_conta IN ('Corrente', 'Poupança', 'Salário', 'Investimento'))
);

-- TABELA TRANSACAO
CREATE TABLE transacao (
    id_transacao SERIAL PRIMARY KEY,
    valor_transacao DECIMAL(10,2) NOT NULL CHECK (valor_transacao > 0),
    data_transacao DATE NOT NULL DEFAULT CURRENT_DATE,
    descricao_transacao VARCHAR(100),
    tipo_transacao VARCHAR(20) NOT NULL,
    usuario_id INT NOT NULL,
    conta_id INT NOT NULL,
    categoria_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (conta_id) REFERENCES conta (id_conta) ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categoria (id_categoria) ON DELETE CASCADE,
    CONSTRAINT check_tipo_transacao CHECK (tipo_transacao IN ('ENTRADA', 'SAIDA'))
);

-- ============================================
-- ÍNDICES PARA PERFORMANCE DA API
-- ============================================

-- Índice para login (busca por email)
CREATE INDEX idx_usuario_email ON usuario(email_usuario);

-- Índices para consultas por usuário
CREATE INDEX idx_conta_usuario ON conta(usuario_id);
CREATE INDEX idx_categoria_usuario ON categoria(usuario_id);
CREATE INDEX idx_transacao_usuario ON transacao(usuario_id);

-- Índices para filtros e ordenação
CREATE INDEX idx_transacao_data ON transacao(data_transacao);
CREATE INDEX idx_transacao_conta ON transacao(conta_id);
CREATE INDEX idx_transacao_categoria ON transacao(categoria_id);

-- Índice composto para relatórios mensais (otimização)
CREATE INDEX idx_transacao_data_usuario ON transacao(usuario_id, data_transacao);

-- ============================================
-- FUNÇÃO PARA VALIDAR COMPATIBILIDADE CATEGORIA X TRANSAÇÃO
-- ============================================

CREATE OR REPLACE FUNCTION validar_categoria_transacao()
RETURNS TRIGGER AS $$
DECLARE
    tipo_cat VARCHAR(20);
BEGIN
    -- Buscar o tipo da categoria
    SELECT tipo_categoria INTO tipo_cat
    FROM categoria
    WHERE id_categoria = NEW.categoria_id;
    
    -- Verificar compatibilidade
    IF (NEW.tipo_transacao = 'ENTRADA' AND tipo_cat != 'ENTRADA') THEN
        RAISE EXCEPTION 'Categoria incompatível: Transação do tipo ENTRADA deve usar categoria do tipo ENTRADA. Categoria fornecida é do tipo %', tipo_cat;
    END IF;
    
    IF (NEW.tipo_transacao = 'SAIDA' AND tipo_cat != 'SAIDA') THEN
        RAISE EXCEPTION 'Categoria incompatível: Transação do tipo SAIDA deve usar categoria do tipo SAIDA. Categoria fornecida é do tipo %', tipo_cat;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- TRIGGER PARA VALIDAR CATEGORIA ANTES DE INSERIR/ATUALIZAR
CREATE TRIGGER trigger_validar_categoria_transacao
BEFORE INSERT OR UPDATE ON transacao
FOR EACH ROW
EXECUTE FUNCTION validar_categoria_transacao();

-- ============================================
-- FUNÇÃO PARA ATUALIZAR SALDO COM VALIDAÇÃO
-- ============================================

CREATE OR REPLACE FUNCTION atualizar_saldo_conta()
RETURNS TRIGGER AS $$
DECLARE
    saldo_atual DECIMAL(10,2);
BEGIN
    -- INSERT: adiciona transação
    IF (TG_OP = 'INSERT') THEN
        -- Verificar saldo antes de permitir SAIDA
        IF (NEW.tipo_transacao = 'SAIDA') THEN
            SELECT saldo_conta INTO saldo_atual 
            FROM conta WHERE id_conta = NEW.conta_id;
            
            IF (saldo_atual < NEW.valor_transacao) THEN
                RAISE EXCEPTION 'Saldo insuficiente. Saldo disponível: R$ %, Valor solicitado: R$ %', 
                              saldo_atual, NEW.valor_transacao;
            END IF;
            
            UPDATE conta 
            SET saldo_conta = saldo_conta - NEW.valor_transacao,
                updated_at = CURRENT_TIMESTAMP
            WHERE id_conta = NEW.conta_id;
        ELSE
            UPDATE conta 
            SET saldo_conta = saldo_conta + NEW.valor_transacao,
                updated_at = CURRENT_TIMESTAMP
            WHERE id_conta = NEW.conta_id;
        END IF;
        RETURN NEW;
    END IF;
    
    -- UPDATE: recalcula saldo
    IF (TG_OP = 'UPDATE') THEN
        -- Reverte transação antiga
        IF (OLD.tipo_transacao = 'ENTRADA') THEN
            UPDATE conta SET saldo_conta = saldo_conta - OLD.valor_transacao WHERE id_conta = OLD.conta_id;
        ELSE
            UPDATE conta SET saldo_conta = saldo_conta + OLD.valor_transacao WHERE id_conta = OLD.conta_id;
        END IF;
        
        -- Valida nova transação se for SAIDA
        IF (NEW.tipo_transacao = 'SAIDA') THEN
            SELECT saldo_conta INTO saldo_atual 
            FROM conta WHERE id_conta = NEW.conta_id;
            
            IF (saldo_atual < NEW.valor_transacao) THEN
                -- Reverte a reversão antes de dar erro
                IF (OLD.tipo_transacao = 'ENTRADA') THEN
                    UPDATE conta SET saldo_conta = saldo_conta + OLD.valor_transacao WHERE id_conta = OLD.conta_id;
                ELSE
                    UPDATE conta SET saldo_conta = saldo_conta - OLD.valor_transacao WHERE id_conta = OLD.conta_id;
                END IF;
                
                RAISE EXCEPTION 'Saldo insuficiente. Saldo disponível: R$ %, Valor solicitado: R$ %', 
                              saldo_atual, NEW.valor_transacao;
            END IF;
        END IF;
        
        -- Aplica nova transação
        IF (NEW.tipo_transacao = 'ENTRADA') THEN
            UPDATE conta SET saldo_conta = saldo_conta + NEW.valor_transacao, updated_at = CURRENT_TIMESTAMP WHERE id_conta = NEW.conta_id;
        ELSE
            UPDATE conta SET saldo_conta = saldo_conta - NEW.valor_transacao, updated_at = CURRENT_TIMESTAMP WHERE id_conta = NEW.conta_id;
        END IF;
        RETURN NEW;
    END IF;
    
    -- DELETE: reverte transação
    IF (TG_OP = 'DELETE') THEN
        IF (OLD.tipo_transacao = 'ENTRADA') THEN
            UPDATE conta SET saldo_conta = saldo_conta - OLD.valor_transacao, updated_at = CURRENT_TIMESTAMP WHERE id_conta = OLD.conta_id;
        ELSE
            UPDATE conta SET saldo_conta = saldo_conta + OLD.valor_transacao, updated_at = CURRENT_TIMESTAMP WHERE id_conta = OLD.conta_id;
        END IF;
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGER PARA ATUALIZAÇÃO AUTOMÁTICA DE SALDO
-- ============================================

CREATE TRIGGER trigger_atualizar_saldo
AFTER INSERT OR UPDATE OR DELETE ON transacao
FOR EACH ROW
EXECUTE FUNCTION atualizar_saldo_conta();

-- ============================================
-- VIEW PARA RELATÓRIO MENSAL
-- ============================================

CREATE OR REPLACE VIEW relatorio_mensal AS
SELECT 
    t.usuario_id,
    u.nome_usuario,
    EXTRACT(MONTH FROM t.data_transacao)::INTEGER as mes,
    EXTRACT(YEAR FROM t.data_transacao)::INTEGER as ano,
    t.tipo_transacao,
    c.nome_categoria,
    SUM(t.valor_transacao) as total,
    COUNT(t.id_transacao) as quantidade_transacoes
FROM transacao t
JOIN usuario u ON t.usuario_id = u.id_usuario
JOIN categoria c ON t.categoria_id = c.id_categoria
GROUP BY t.usuario_id, u.nome_usuario, mes, ano, t.tipo_transacao, c.nome_categoria
ORDER BY ano DESC, mes DESC, t.tipo_transacao, total DESC;

-- ============================================
-- VIEW PARA RESUMO DE CONTAS
-- ============================================

CREATE OR REPLACE VIEW resumo_contas AS
SELECT 
    c.id_conta,
    c.nome_conta,
    c.tipo_conta,
    c.saldo_conta,
    c.usuario_id,
    u.nome_usuario,
    COUNT(t.id_transacao) as total_transacoes,
    COALESCE(SUM(CASE WHEN t.tipo_transacao = 'ENTRADA' THEN t.valor_transacao ELSE 0 END), 0) as total_entradas,
    COALESCE(SUM(CASE WHEN t.tipo_transacao = 'SAIDA' THEN t.valor_transacao ELSE 0 END), 0) as total_saidas
FROM conta c
JOIN usuario u ON c.usuario_id = u.id_usuario
LEFT JOIN transacao t ON c.id_conta = t.conta_id
GROUP BY c.id_conta, c.nome_conta, c.tipo_conta, c.saldo_conta, c.usuario_id, u.nome_usuario;
