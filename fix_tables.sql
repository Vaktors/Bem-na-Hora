USE BemNaHora;

CREATE TABLE IF NOT EXISTS profissional_modalidades (
    idProfissional INT,
    idModalidade INT,
    PRIMARY KEY (idProfissional, idModalidade),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idModalidade) REFERENCES modalidades(idModalidade)
);

CREATE TABLE IF NOT EXISTS profissional_comodidades (
    idProfissional INT,
    idComodidade INT,
    PRIMARY KEY (idProfissional, idComodidade),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idComodidade) REFERENCES comodidades(idComodidade)
);

USE BemNaHora;

-- ==========================================================
-- 1. CRIAR A TABELA DE LIGAÇÃO (Profissional <-> Comodidades)
-- ==========================================================
CREATE TABLE IF NOT EXISTS profissional_comodidades (
    idProfissional INT,
    idComodidade INT,
    PRIMARY KEY (idProfissional, idComodidade),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idComodidade) REFERENCES comodidades(idComodidade)
);

-- ==========================================================
-- 2. GARANTIR QUE AS OPÇÕES EXISTEM NO CATÁLOGO
-- ==========================================================
INSERT IGNORE INTO comodidades (nome, icone) VALUES 
('Wi-Fi', 'fa-wifi'),
('Estacionamento', 'fa-square-parking'),
('Acessibilidade', 'fa-wheelchair'),
('Cafeteria', 'fa-mug-hot'),
('Espaço Kids', 'fa-child');

-- ==========================================================
-- 3. INSERTS AUTOMÁTICOS (Popular os médicos)
-- ==========================================================

-- Lógica 1: Dar "Estacionamento" para todos os médicos com ID PAR
INSERT IGNORE INTO profissional_comodidades (idProfissional, idComodidade)
SELECT p.idProfissional, c.idComodidade
FROM profissional p
JOIN comodidades c ON c.nome = 'Estacionamento' -- Busca o ID correto do Estacionamento
WHERE p.idProfissional % 2 = 0;

-- Lógica 2: Dar "Acessibilidade" para todos os médicos com ID Múltiplo de 3
INSERT IGNORE INTO profissional_comodidades (idProfissional, idComodidade)
SELECT p.idProfissional, c.idComodidade
FROM profissional p
JOIN comodidades c ON c.nome = 'Acessibilidade' -- Busca o ID correto da Acessibilidade
WHERE p.idProfissional % 3 = 0;

-- Lógica 3: Dar "Wi-Fi" para TODOS (Só pra ter volume)
INSERT IGNORE INTO profissional_comodidades (idProfissional, idComodidade)
SELECT p.idProfissional, c.idComodidade
FROM profissional p
JOIN comodidades c ON c.nome = 'Wi-Fi';

USE BemNaHora;

-- ==========================================================
-- 1. CRIAR A TABELA MÃE (Opções de Atendimento)
-- ==========================================================
CREATE TABLE IF NOT EXISTS modalidades (
    idModalidade INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL UNIQUE
);

-- Inserir as opções que aparecem no seu filtro
INSERT IGNORE INTO modalidades (nome) VALUES ('Presencial'), ('Telemedicina'), ('Domiciliar');

-- ==========================================================
-- 2. TABELAS DE LIGAÇÃO (Quem atende o quê)
-- ==========================================================

-- Vínculo Profissional <-> Modalidade
CREATE TABLE IF NOT EXISTS profissional_modalidades (
    idProfissional INT,
    idModalidade INT,
    PRIMARY KEY (idProfissional, idModalidade),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idModalidade) REFERENCES modalidades(idModalidade)
);

-- Vínculo Clínica <-> Modalidade
CREATE TABLE IF NOT EXISTS clinica_modalidades (
    idClinica INT,
    idModalidade INT,
    PRIMARY KEY (idClinica, idModalidade),
    FOREIGN KEY (idClinica) REFERENCES clinica(idClinica) ON DELETE CASCADE,
    FOREIGN KEY (idModalidade) REFERENCES modalidades(idModalidade)
);

-- ==========================================================
-- 3. PREENCHER DADOS AUTOMATICAMENTE
-- (Sem isso, o filtro funciona mas não traz ninguém)
-- ==========================================================

-- Todo mundo atende Presencial (ID 1)
INSERT IGNORE INTO profissional_modalidades (idProfissional, idModalidade) 
SELECT idProfissional, 1 FROM profissional;

INSERT IGNORE INTO clinica_modalidades (idClinica, idModalidade) 
SELECT idClinica, 1 FROM clinica;

-- Médicos com ID PAR atendem Telemedicina (ID 2)
INSERT IGNORE INTO profissional_modalidades (idProfissional, idModalidade) 
SELECT idProfissional, 2 FROM profissional WHERE idProfissional % 2 = 0;

-- Médicos com ID ÍMPAR atendem Domiciliar (ID 3)
INSERT IGNORE INTO profissional_modalidades (idProfissional, idModalidade) 
SELECT idProfissional, 3 FROM profissional WHERE idProfissional % 2 != 0;

CREATE TABLE IF NOT EXISTS profissional_comodidades (
    idProfissional INT,
    idComodidade INT,
    PRIMARY KEY (idProfissional, idComodidade),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idComodidade) REFERENCES comodidades(idComodidade)
);