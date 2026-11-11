
CREATE TABLE vendedoras (
    id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome      VARCHAR(120) NOT NULL,
    contato   VARCHAR(120),
    ativa     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE categorias (
    id                   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome                 VARCHAR(80) NOT NULL UNIQUE,
    tipo                 VARCHAR(10) NOT NULL
                         CHECK (tipo IN ('VENDA', 'SERVICO')),
    percentual_comissao  NUMERIC(5,2) NOT NULL
                         CHECK (percentual_comissao >= 0 AND percentual_comissao <= 100),
    ativa                BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE metas (
    id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vendedora_id   INTEGER NOT NULL REFERENCES vendedoras (id),
    mes_referencia DATE NOT NULL
                   CHECK (EXTRACT(DAY FROM mes_referencia) = 1),
    valor_meta     NUMERIC(12,2) NOT NULL CHECK (valor_meta >= 0),
    UNIQUE (vendedora_id, mes_referencia)
);


CREATE TABLE vendas (
    id                   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vendedora_id         INTEGER NOT NULL REFERENCES vendedoras (id),
    categoria_id         INTEGER NOT NULL REFERENCES categorias (id),
    data_venda           DATE NOT NULL,
    valor                NUMERIC(12,2) NOT NULL CHECK (valor > 0),
    percentual_aplicado  NUMERIC(5,2) NOT NULL
                         CHECK (percentual_aplicado >= 0 AND percentual_aplicado <= 100),
    valor_comissao       NUMERIC(12,2) NOT NULL CHECK (valor_comissao >= 0),
    pontos               INTEGER NOT NULL DEFAULT 0 CHECK (pontos >= 0)
);


CREATE TABLE campanhas (
    id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    categoria_id     INTEGER REFERENCES categorias (id),
    nome             VARCHAR(120) NOT NULL,
    tipo             VARCHAR(10) NOT NULL
                     CHECK (tipo IN ('PONTUACAO', 'COMBO')),
    meta_quantidade  INTEGER NOT NULL CHECK (meta_quantidade > 0),
    valor_bonus      NUMERIC(12,2) NOT NULL CHECK (valor_bonus > 0),
    data_inicio      DATE NOT NULL,
    data_fim         DATE NOT NULL,
    ativa            BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (data_fim >= data_inicio),
    CHECK (tipo <> 'COMBO' OR categoria_id IS NOT NULL)
);


CREATE TABLE bonus_campanha (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    campanha_id     INTEGER NOT NULL REFERENCES campanhas (id),
    vendedora_id    INTEGER NOT NULL REFERENCES vendedoras (id),
    mes_referencia  DATE NOT NULL
                    CHECK (EXTRACT(DAY FROM mes_referencia) = 1),
    valor_bonus     NUMERIC(12,2) NOT NULL CHECK (valor_bonus > 0)
);

CREATE INDEX idx_vendas_data       ON vendas (data_venda);
CREATE INDEX idx_vendas_vendedora  ON vendas (vendedora_id, data_venda);
CREATE INDEX idx_vendas_categoria  ON vendas (categoria_id);
CREATE INDEX idx_bonus_vendedora   ON bonus_campanha (vendedora_id, mes_referencia);
CREATE INDEX idx_bonus_campanha    ON bonus_campanha (campanha_id);


