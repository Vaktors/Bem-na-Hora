-- ==========================================================
-- 1. PREPARAÇÃO DO AMBIENTE (Limpeza e Criação)
-- ==========================================================
DROP SCHEMA IF EXISTS BemNaHora;
CREATE SCHEMA BemNaHora;
USE BemNaHora;

-- Desativa travas de segurança temporariamente para permitir updates em massa no final
SET SQL_SAFE_UPDATES = 0;

-- ==========================================================
-- 2. TABELAS DE CATÁLOGO (Opções fixas do sistema)
-- ==========================================================

-- Convênios
CREATE TABLE convenios (
    idConvenio INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE
);

-- Modalidades de Atendimento (Presencial, Telemedicina...)
CREATE TABLE modalidades (
    idModalidade INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL UNIQUE,
    icone VARCHAR(50) DEFAULT 'fa-user-doctor'
);

-- Infraestrutura e Comodidades (Wi-Fi, Estacionamento...)
CREATE TABLE comodidades (
    idComodidade INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL UNIQUE,
    icone VARCHAR(50) DEFAULT 'fa-check'
);

-- Especialidades Médicas
CREATE TABLE especialidades (
    idEspecialidade INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE
);

-- ==========================================================
-- 3. ENTIDADES PRINCIPAIS (Usuário, Clínica, Profissional)
-- ==========================================================

-- Paciente/Usuário
CREATE TABLE usuario (
    idUsuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    cpf VARCHAR(20) NOT NULL UNIQUE, 
    genero ENUM('M', 'F', 'O') NOT NULL,
    dataNasc DATE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    foto_perfil VARCHAR(255), 
    cep VARCHAR(10),
    rua VARCHAR(150),
    bairro VARCHAR(50),
    cidade VARCHAR(50),
    estado CHAR(2),
    idConvenio INT,
    FOREIGN KEY (idConvenio) REFERENCES convenios(idConvenio)
);

-- Clínica
CREATE TABLE clinica (
    idClinica INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,           -- Razão Social
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    cnpj VARCHAR(20) NOT NULL UNIQUE,     
    nomeExibicao VARCHAR(100),            -- Nome Fantasia
    tipo VARCHAR(50),                     -- Ex: Multidisciplinar
    ano_fundacao INT,
    diretor_tecnico VARCHAR(100),
    registroTecnico VARCHAR(30),          -- CRM/CNES
    foto_perfil VARCHAR(255),             
    site_url VARCHAR(150),
    instagram VARCHAR(100),
    historia TEXT,
    endereco VARCHAR(200),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado CHAR(2) DEFAULT 'SP',
    telefone VARCHAR(20),                 
    horario_semana VARCHAR(100),
    horario_fim_sem VARCHAR(100)
);

-- Profissional Independente
CREATE TABLE profissional (
    idProfissional INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    cpf VARCHAR(20) NOT NULL UNIQUE,       
    telefone VARCHAR(20),                  
    registro_conselho VARCHAR(50),         -- Ex: CRM-SP 123456
    foto_perfil VARCHAR(255),              
    biografia TEXT,
    formacao_academica TEXT,               
    site_url VARCHAR(150),
    instagram VARCHAR(100),
    endereco VARCHAR(200),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado CHAR(2) DEFAULT 'SP',                        
    horario_atendimento VARCHAR(150)       
);

-- ==========================================================
-- 4. TABELAS FILHAS (1:N) - Serviços, Equipes, Fotos
-- ==========================================================

-- Equipe da Clínica
CREATE TABLE equipe_medica (
    idEquipe INT PRIMARY KEY AUTO_INCREMENT,
    idClinica INT NOT NULL,
    nome VARCHAR(100),
    especialidade VARCHAR(100),
    experiencia VARCHAR(50),
    FOREIGN KEY (idClinica) REFERENCES clinica(idClinica) ON DELETE CASCADE
);

-- Procedimentos da Clínica
CREATE TABLE procedimentos (
    idProcedimento INT PRIMARY KEY AUTO_INCREMENT,
    idClinica INT NOT NULL,
    nome VARCHAR(100),
    preco VARCHAR(50), 
    FOREIGN KEY (idClinica) REFERENCES clinica(idClinica) ON DELETE CASCADE
);

-- Galeria da Clínica
CREATE TABLE galeria_clinica (
    idFoto INT PRIMARY KEY AUTO_INCREMENT,
    idClinica INT NOT NULL,
    caminho_foto VARCHAR(255),
    legenda VARCHAR(45),
    FOREIGN KEY (idClinica) REFERENCES clinica(idClinica) ON DELETE CASCADE
);

-- Serviços do Profissional
CREATE TABLE servicos_profissional (
    idServico INT PRIMARY KEY AUTO_INCREMENT,
    idProfissional INT NOT NULL,
    nome VARCHAR(100),              
    preco VARCHAR(50),              
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE
);

-- Galeria do Profissional
CREATE TABLE galeria_profissional (
    idFoto INT PRIMARY KEY AUTO_INCREMENT,
    idProfissional INT NOT NULL,
    caminho_foto VARCHAR(255),
    legenda VARCHAR(100),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE
);

-- ==========================================================
-- 5. TABELAS DE LIGAÇÃO (Muitos para Muitos) - FILTROS
-- ==========================================================

-- Filtros da Clínica
CREATE TABLE clinica_convenios (
    idClinica INT, idConvenio INT, PRIMARY KEY (idClinica, idConvenio),
    FOREIGN KEY (idClinica) REFERENCES clinica(idClinica) ON DELETE CASCADE,
    FOREIGN KEY (idConvenio) REFERENCES convenios(idConvenio)
);
CREATE TABLE clinica_comodidades (
    idClinica INT, idComodidade INT, PRIMARY KEY (idClinica, idComodidade),
    FOREIGN KEY (idClinica) REFERENCES clinica(idClinica) ON DELETE CASCADE,
    FOREIGN KEY (idComodidade) REFERENCES comodidades(idComodidade)
);
CREATE TABLE clinica_modalidades (
    idClinica INT, idModalidade INT, PRIMARY KEY (idClinica, idModalidade),
    FOREIGN KEY (idClinica) REFERENCES clinica(idClinica) ON DELETE CASCADE,
    FOREIGN KEY (idModalidade) REFERENCES modalidades(idModalidade)
);

-- Filtros do Profissional
CREATE TABLE profissional_especialidade (
    idProfissional INT, idEspecialidade INT, PRIMARY KEY (idProfissional, idEspecialidade),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idEspecialidade) REFERENCES especialidades(idEspecialidade)
);
CREATE TABLE profissional_convenios (
    idProfissional INT, idConvenio INT, PRIMARY KEY (idProfissional, idConvenio),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idConvenio) REFERENCES convenios(idConvenio)
);
CREATE TABLE profissional_modalidades (
    idProfissional INT, idModalidade INT, PRIMARY KEY (idProfissional, idModalidade),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idModalidade) REFERENCES modalidades(idModalidade)
);
CREATE TABLE profissional_comodidades (
    idProfissional INT, idComodidade INT, PRIMARY KEY (idProfissional, idComodidade),
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idComodidade) REFERENCES comodidades(idComodidade)
);

-- ==========================================================
-- 6. AGENDAMENTOS E AVALIAÇÕES
-- ==========================================================

CREATE TABLE agendamento (
    idAgendamento INT PRIMARY KEY AUTO_INCREMENT,
    idUsuario INT NOT NULL,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME NOT NULL,    
    status ENUM('Agendado', 'Confirmado', 'Concluido', 'Cancelado', 'Faltou') DEFAULT 'Agendado',
    observacoes TEXT,
    idClinica INT, idEquipe INT, idProcedimento INT,
    idProfissional INT, idServico INT,
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario) ON DELETE CASCADE,
    FOREIGN KEY (idClinica) REFERENCES clinica(idClinica) ON DELETE CASCADE,
    FOREIGN KEY (idEquipe) REFERENCES equipe_medica(idEquipe) ON DELETE SET NULL,
    FOREIGN KEY (idProcedimento) REFERENCES procedimentos(idProcedimento) ON DELETE SET NULL,
    FOREIGN KEY (idProfissional) REFERENCES profissional(idProfissional) ON DELETE CASCADE,
    FOREIGN KEY (idServico) REFERENCES servicos_profissional(idServico) ON DELETE SET NULL
);

CREATE TABLE avaliacoes (
    idAvaliacao INT PRIMARY KEY AUTO_INCREMENT,
    idAgendamento INT NOT NULL UNIQUE, 
    nota INT NOT NULL CHECK (nota >= 1 AND nota <= 5),
    comentario TEXT,
    data_avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idAgendamento) REFERENCES agendamento(idAgendamento) ON DELETE CASCADE
);

-- ==========================================================
-- 7. POVOAR CATÁLOGOS
-- ==========================================================
INSERT INTO especialidades (nome) VALUES 
('Clínica Geral'), ('Cardiologia'), ('Dermatologia'), ('Ginecologia'), 
('Pediatria'), ('Ortopedia'), ('Psicologia'), ('Nutrição'), ('Odontologia'), ('Fisioterapia');

INSERT INTO convenios (nome) VALUES 
('Particular'), ('Unimed'), ('Amil'), ('Bradesco Saúde'), ('SulAmérica');

INSERT INTO modalidades (nome, icone) VALUES 
('Presencial', 'fa-hospital-user'), ('Telemedicina', 'fa-video'), ('Domiciliar', 'fa-house-medical');

INSERT INTO comodidades (nome, icone) VALUES 
('Wi-Fi', 'fa-wifi'), ('Estacionamento', 'fa-parking'), ('Acessibilidade', 'fa-wheelchair');

-- ==========================================================
-- 8. POVOAR CLÍNICAS (30 Registros)
-- ==========================================================
INSERT INTO clinica (nome, nomeExibicao, email, senha_hash, cnpj, tipo, telefone, registroTecnico, endereco, bairro, cidade, horario_semana, horario_fim_sem, historia) VALUES
('Hospital Santa Vida Ltda', 'Hospital Santa Vida', 'contato@santavida.com.br', 'pbkdf2:sha256:600000$dummy', '10000000000101', 'Hospital Geral', '11999990001', 'CNES 123456', 'Av. Paulista, 1000', 'Bela Vista', 'São Paulo - SP', '24 Horas', '24 Horas', 'Referência em atendimento de emergência.'),
('Clínica Bem Estar Total', 'Clínica Bem Estar', 'atendimento@bemestar.com', 'pbkdf2:sha256:600000$dummy', '10000000000102', 'Multidisciplinar', '11999990002', 'CRM-SP 9876', 'Rua Augusta, 500', 'Consolação', 'São Paulo - SP', '08:00 - 18:00', '08:00 - 12:00', 'Focada em saúde preventiva.'),
('Laboratório Diagnóstico Preciso', 'Lab Preciso', 'exames@labpreciso.com.br', 'pbkdf2:sha256:600000$dummy', '10000000000103', 'Laboratório', '11999990003', 'CRBM 5544', 'Rua Vergueiro, 200', 'Liberdade', 'São Paulo - SP', '06:00 - 17:00', '06:00 - 11:00', 'Tecnologia de ponta em análises clínicas.'),
('Centro de Ortopedia Avançada', 'OrtoCenter', 'contato@ortocenter.com', 'pbkdf2:sha256:600000$dummy', '10000000000104', 'Especializada', '11999990004', 'CRM-SP 1122', 'Av. Brasil, 1500', 'Jardins', 'São Paulo - SP', '09:00 - 19:00', 'Fechado', 'Especialistas em coluna e joelho.'),
('Clínica da Mulher Moderna', 'Femina Care', 'ola@feminacare.com', 'pbkdf2:sha256:600000$dummy', '10000000000105', 'Ginecologia', '11999990005', 'CRM-SP 3344', 'Rua dos Pinheiros, 700', 'Pinheiros', 'São Paulo - SP', '08:00 - 20:00', '09:00 - 13:00', 'Saúde integral da mulher.'),
('Instituto do Coração Saudável', 'CardioLife', 'agenda@cardiolife.com', 'pbkdf2:sha256:600000$dummy', '10000000000106', 'Cardiologia', '11999990006', 'CRM-SP 5566', 'Av. Ibirapuera, 2000', 'Moema', 'São Paulo - SP', '08:00 - 18:00', 'Fechado', 'Cuidando do seu coração com carinho.'),
('Clínica Pediátrica Sorriso', 'Kids Health', 'contato@kidshealth.com', 'pbkdf2:sha256:600000$dummy', '10000000000107', 'Pediatria', '11999990007', 'CRM-SP 7788', 'Rua Clélia, 400', 'Lapa', 'São Paulo - SP', '08:00 - 19:00', '08:00 - 12:00', 'Ambiente lúdico para os pequenos.'),
('Centro Dermatológico Pelle', 'Pelle Derma', 'dermato@pelle.com', 'pbkdf2:sha256:600000$dummy', '10000000000108', 'Dermatologia', '11999990008', 'CRM-SP 9900', 'Av. Faria Lima, 3000', 'Itaim Bibi', 'São Paulo - SP', '10:00 - 20:00', '10:00 - 14:00', 'Estética e saúde da pele.'),
('Clínica de Olhos Visão', 'Eye Clinic', 'visao@eyeclinic.com', 'pbkdf2:sha256:600000$dummy', '10000000000109', 'Oftalmologia', '11999990009', 'CRM-SP 2211', 'Rua Domingos de Morais, 800', 'Vila Mariana', 'São Paulo - SP', '09:00 - 18:00', 'Fechado', 'Cirurgias e consultas oftalmológicas.'),
('Centro de Fisioterapia Movimento', 'Physio Move', 'contato@physiomove.com', 'pbkdf2:sha256:600000$dummy', '10000000000110', 'Fisioterapia', '11999990010', 'CREFITO 4433', 'Rua Tuiuti, 500', 'Tatuapé', 'São Paulo - SP', '07:00 - 21:00', '08:00 - 12:00', 'Reabilitação esportiva e motora.'),
('Odonto Prime', 'Odonto Prime', 'sorriso@odontoprime.com', 'pbkdf2:sha256:600000$dummy', '10000000000111', 'Odontologia', '11999990011', 'CRO-SP 1234', 'Av. Jabaquara, 100', 'Saúde', 'São Paulo - SP', '08:00 - 20:00', '08:00 - 14:00', 'Implantes e ortodontia.'),
('Psicologia & Mente', 'Psyche Center', 'terapia@psyche.com', 'pbkdf2:sha256:600000$dummy', '10000000000112', 'Psicologia', '11999990012', 'CRP 06/1234', 'Rua Pamplona, 900', 'Jardim Paulista', 'São Paulo - SP', '08:00 - 22:00', 'Fechado', 'Terapia cognitivo-comportamental.'),
('Clínica de Nutrição Leve', 'NutriLeve', 'dieta@nutrileve.com', 'pbkdf2:sha256:600000$dummy', '10000000000113', 'Nutrição', '11999990013', 'CRN 5678', 'Av. Angélica, 200', 'Higienópolis', 'São Paulo - SP', '09:00 - 18:00', 'Fechado', 'Reeducação alimentar e emagrecimento.'),
('Hospital Dia Saúde', 'Hospital Dia', 'sac@hospitaldia.com', 'pbkdf2:sha256:600000$dummy', '10000000000114', 'Hospital Dia', '11999990014', 'CNES 654321', 'Rua Voluntários da Pátria, 1500', 'Santana', 'São Paulo - SP', '06:00 - 22:00', '06:00 - 22:00', 'Cirurgias de pequeno porte.'),
('Clínica Popular do Brás', 'Saúde Popular', 'bras@saudepop.com', 'pbkdf2:sha256:600000$dummy', '10000000000115', 'Clínica Popular', '11999990015', 'CRM-SP 7777', 'Rua da Alfândega, 50', 'Brás', 'São Paulo - SP', '07:00 - 19:00', '07:00 - 13:00', 'Preços acessíveis para todos.'),
('Laboratório Blood Test', 'Blood Test', 'exames@bloodtest.com', 'pbkdf2:sha256:600000$dummy', '10000000000116', 'Laboratório', '11999990016', 'CRBM 8899', 'Av. Santo Amaro, 4000', 'Brooklin', 'São Paulo - SP', '06:00 - 16:00', '06:00 - 12:00', 'Coleta domiciliar disponível.'),
('Centro de Vacinação Imune', 'Imune Vacinas', 'vacinas@imune.com', 'pbkdf2:sha256:600000$dummy', '10000000000117', 'Vacinação', '11999990017', 'CRM-SP 1010', 'Rua Heitor Penteado, 600', 'Sumarezinho', 'São Paulo - SP', '08:00 - 18:00', '08:00 - 13:00', 'Todas as vacinas do calendário.'),
('Clínica de Estética Bella', 'Bella Estética', 'contato@bella.com', 'pbkdf2:sha256:600000$dummy', '10000000000118', 'Estética', '11999990018', 'Biomedicina', 'Rua Oscar Freire, 100', 'Jardins', 'São Paulo - SP', '10:00 - 21:00', '10:00 - 18:00', 'Botox, preenchimento e laser.'),
('Hospital Veterinário PetCare', 'PetCare Hospital', 'vet@petcare.com', 'pbkdf2:sha256:600000$dummy', '10000000000119', 'Veterinária', '11999990019', 'CRMV 2233', 'Av. Morumbi, 3000', 'Morumbi', 'São Paulo - SP', '24 Horas', '24 Horas', 'UTI e cirurgia veterinária.'),
('Clínica de Otorrino Audio', 'Audio Clinic', 'ouvido@audio.com', 'pbkdf2:sha256:600000$dummy', '10000000000120', 'Otorrinolaringologia', '11999990020', 'CRM-SP 4455', 'Rua Pedroso de Morais, 500', 'Pinheiros', 'São Paulo - SP', '09:00 - 18:00', 'Fechado', 'Especialistas em audição e rinite.'),
('Centro de Gastro Digest', 'Digest Center', 'gastro@digest.com', 'pbkdf2:sha256:600000$dummy', '10000000000121', 'Gastroenterologia', '11999990021', 'CRM-SP 6677', 'Av. Rebouças, 2500', 'Pinheiros', 'São Paulo - SP', '08:00 - 18:00', 'Fechado', 'Endoscopia e Colonoscopia.'),
('Clínica de Urologia Homem', 'Uro Clinic', 'contato@uro.com', 'pbkdf2:sha256:600000$dummy', '10000000000122', 'Urologia', '11999990022', 'CRM-SP 8899', 'Rua Verbo Divino, 300', 'Santo Amaro', 'São Paulo - SP', '09:00 - 19:00', 'Fechado', 'Saúde do homem.'),
('Centro de Oncologia Esperança', 'Onco Hope', 'atendimento@oncohope.com', 'pbkdf2:sha256:600000$dummy', '10000000000123', 'Oncologia', '11999990023', 'CRM-SP 1100', 'Av. Pacaembu, 1000', 'Pacaembu', 'São Paulo - SP', '08:00 - 20:00', 'Fechado', 'Tratamento humanizado.'),
('Clínica de Neurologia Neuro', 'Neuro Center', 'cerebro@neuro.com', 'pbkdf2:sha256:600000$dummy', '10000000000124', 'Neurologia', '11999990024', 'CRM-SP 3322', 'Rua Itapeva, 400', 'Bela Vista', 'São Paulo - SP', '09:00 - 18:00', 'Fechado', 'Especialistas em enxaqueca.'),
('Centro de Alergia e Imuno', 'Alergo Clinic', 'alergia@alergo.com', 'pbkdf2:sha256:600000$dummy', '10000000000125', 'Alergologia', '11999990025', 'CRM-SP 5544', 'Av. Lavandisca, 200', 'Moema', 'São Paulo - SP', '08:00 - 18:00', '08:00 - 12:00', 'Testes alérgicos.'),
('Clínica de Endocrino Metabólica', 'Endo Meta', 'hormonio@endo.com', 'pbkdf2:sha256:600000$dummy', '10000000000126', 'Endocrinologia', '11999990026', 'CRM-SP 7766', 'Rua Estados Unidos, 1000', 'Jardins', 'São Paulo - SP', '09:00 - 19:00', 'Fechado', 'Diabetes e tireoide.'),
('Centro de Geriatria Melhor Idade', 'Geriatria Vida', 'idoso@geriatria.com', 'pbkdf2:sha256:600000$dummy', '10000000000127', 'Geriatria', '11999990027', 'CRM-SP 9988', 'Rua dos Três Irmãos, 400', 'Vila Sônia', 'São Paulo - SP', '08:00 - 18:00', 'Fechado', 'Envelhecimento saudável.'),
('Clínica de Reumatologia Articolar', 'Articolar', 'dor@articolar.com', 'pbkdf2:sha256:600000$dummy', '10000000000128', 'Reumatologia', '11999990028', 'CRM-SP 1212', 'Av. Pompeia, 600', 'Pompeia', 'São Paulo - SP', '09:00 - 18:00', 'Fechado', 'Artrite e artrose.'),
('Centro de Pneumologia Respire', 'Respire Bem', 'pulmao@respire.com', 'pbkdf2:sha256:600000$dummy', '10000000000129', 'Pneumologia', '11999990029', 'CRM-SP 3434', 'Rua Cardoso de Almeida, 800', 'Perdizes', 'São Paulo - SP', '08:00 - 19:00', 'Fechado', 'Asma e bronquite.'),
('Clínica de Psiquiatria Equilíbrio', 'Mente Sã', 'psiq@mentesa.com', 'pbkdf2:sha256:600000$dummy', '10000000000130', 'Psiquiatria', '11999990030', 'CRM-SP 5656', 'Rua Tabapuã, 500', 'Itaim Bibi', 'São Paulo - SP', '09:00 - 20:00', 'Fechado', 'Saúde mental integrada.');

-- Popular vínculos da clínica (aleatório)
INSERT IGNORE INTO clinica_comodidades (idClinica, idComodidade) SELECT idClinica, 1 FROM clinica;
INSERT IGNORE INTO clinica_comodidades (idClinica, idComodidade) SELECT idClinica, 2 FROM clinica WHERE idClinica % 2 = 0;
INSERT IGNORE INTO clinica_modalidades (idClinica, idModalidade) SELECT idClinica, 1 FROM clinica;
INSERT IGNORE INTO clinica_convenios (idClinica, idConvenio) SELECT idClinica, 1 FROM clinica;
INSERT IGNORE INTO equipe_medica (idClinica, nome, especialidade, experiencia) SELECT idClinica, 'Dr. Plantonista', 'Clínico Geral', '5 anos' FROM clinica;
INSERT IGNORE INTO procedimentos (idClinica, nome, preco) SELECT idClinica, 'Consulta', 'R$ 150,00' FROM clinica;

-- ==========================================================
-- 9. POVOAR PROFISSIONAIS (80 Registros)
-- ==========================================================
-- 2.1 Clínica Geral
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Dr. Roberto Almeida', 'roberto.almeida@email.com', '11122233301', 'hash_teste', '11988880001', 'CRM-SP 1001', 'Médico atencioso.', 'USP', 'Rua A, 100', 'Centro', 'São Paulo', 'SP', '08h-18h'),
('Dra. Fernanda Costa', 'fernanda.costa@email.com', '11122233302', 'hash_teste', '11988880002', 'CRM-SP 1002', 'Check-ups.', 'UNIFESP', 'Rua B, 200', 'Vila Mariana', 'São Paulo', 'SP', '09h-17h'),
('Dr. Carlos Silva', 'carlos.silva@email.com', '11122233303', 'hash_teste', '11988880003', 'CRM-SP 1003', 'Idosos.', 'UNICAMP', 'Rua C, 300', 'Moema', 'São Paulo', 'SP', '08h-19h'),
('Dra. Juliana Lima', 'juliana.lima@email.com', '11122233304', 'hash_teste', '11988880004', 'CRM-SP 1004', 'Integrativa.', 'Santa Casa', 'Rua D, 400', 'Pinheiros', 'São Paulo', 'SP', '10h-16h'),
('Dr. Marcos Souza', 'marcos.souza@email.com', '11122233305', 'hash_teste', '11988880005', 'CRM-SP 1005', 'Urgências.', 'USP', 'Rua E, 500', 'Lapa', 'São Paulo', 'SP', '13h-20h'),
('Dra. Patricia Rocha', 'patricia.rocha@email.com', '11122233306', 'hash_teste', '11988880006', 'CRM-SP 1006', 'Crônicas.', 'UNESP', 'Rua F, 600', 'Tatuapé', 'São Paulo', 'SP', '08h-12h'),
('Dr. Lucas Mendes', 'lucas.mendes@email.com', '11122233307', 'hash_teste', '11988880007', 'CRM-SP 1007', 'Holística.', 'FMABC', 'Rua G, 700', 'Santana', 'São Paulo', 'SP', '09h-18h'),
('Dra. Beatriz Santos', 'beatriz.santos@email.com', '11122233308', 'hash_teste', '11988880008', 'CRM-SP 1008', 'Domiciliar.', 'USP', 'Rua H, 800', 'Morumbi', 'São Paulo', 'SP', 'Flexível'),
('Dr. Gabriel Oliveira', 'gabriel.oliveira@email.com', '11122233309', 'hash_teste', '11988880009', 'CRM-SP 1009', 'Corporativa.', 'Einstein', 'Rua I, 900', 'Itaim', 'São Paulo', 'SP', '08h-17h'),
('Dra. Mariana Dias', 'mariana.dias@email.com', '11122233310', 'hash_teste', '11988880010', 'CRM-SP 1010', 'Bem-estar.', 'UNIFESP', 'Rua J, 1000', 'Perdizes', 'São Paulo', 'SP', '10h-19h');

-- 2.2 Cardiologia
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Dr. Ricardo Coração', 'ricardo@cardio.com', '22233344401', 'hash_teste', '11977770001', 'CRM-SP 2001', 'Arritmias.', 'INCOR', 'Av. Paulista, 200', 'Bela Vista', 'São Paulo', 'SP', '08h-18h'),
('Dra. Amanda Vascular', 'amanda@cardio.com', '22233344402', 'hash_teste', '11977770002', 'CRM-SP 2002', 'Infartos.', 'Dante', 'Rua K, 1100', 'Moema', 'São Paulo', 'SP', '09h-19h'),
('Dr. Pedro Valvula', 'pedro@cardio.com', '22233344403', 'hash_teste', '11977770003', 'CRM-SP 2003', 'Exames.', 'USP', 'Rua L, 1200', 'Pinheiros', 'São Paulo', 'SP', '08h-12h'),
('Dra. Sofia Pressão', 'sofia@cardio.com', '22233344404', 'hash_teste', '11977770004', 'CRM-SP 2004', 'Hipertensão.', 'UNIFESP', 'Rua M, 1300', 'Vila Mariana', 'São Paulo', 'SP', '14h-20h'),
('Dr. Andre Stent', 'andre@cardio.com', '22233344405', 'hash_teste', '11977770005', 'CRM-SP 2005', 'Intervencionista.', 'UNICAMP', 'Rua N, 1400', 'Jardins', 'São Paulo', 'SP', '08h-18h'),
('Dra. Laura Ritmo', 'laura@cardio.com', '22233344406', 'hash_teste', '11977770006', 'CRM-SP 2006', 'Marcapassos.', 'USP', 'Rua O, 1500', 'Saúde', 'São Paulo', 'SP', '09h-17h'),
('Dr. Tiago Aorta', 'tiago@cardio.com', '22233344407', 'hash_teste', '11977770007', 'CRM-SP 2007', 'Cirurgia.', 'Santa Casa', 'Rua P, 1600', 'Higienópolis', 'São Paulo', 'SP', '10h-18h'),
('Dra. Clara Veia', 'clara@cardio.com', '22233344408', 'hash_teste', '11977770008', 'CRM-SP 2008', 'Reabilitação.', 'FMABC', 'Rua Q, 1700', 'Ipiranga', 'São Paulo', 'SP', '08h-16h');

-- 2.3 Dermatologia
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Dra. Ana Pele', 'ana@dermato.com', '33344455501', 'hash_teste', '11966660001', 'CRM-SP 3001', 'Estética.', 'USP', 'Rua R, 1800', 'Itaim', 'São Paulo', 'SP', '10h-19h'),
('Dr. Bruno Derma', 'bruno@dermato.com', '33344455502', 'hash_teste', '11966660002', 'CRM-SP 3002', 'Acne.', 'UNIFESP', 'Rua S, 1900', 'Pinheiros', 'São Paulo', 'SP', '09h-18h'),
('Dra. Carla Laser', 'carla@dermato.com', '33344455503', 'hash_teste', '11966660003', 'CRM-SP 3003', 'Laser.', 'UNICAMP', 'Rua T, 2000', 'Moema', 'São Paulo', 'SP', '08h-14h'),
('Dr. Daniel Cabelo', 'daniel@dermato.com', '33344455504', 'hash_teste', '11966660004', 'CRM-SP 3004', 'Cabelo.', 'Santa Casa', 'Rua U, 2100', 'Jardins', 'São Paulo', 'SP', '08h-18h'),
('Dra. Elisa Skin', 'elisa@dermato.com', '33344455505', 'hash_teste', '11966660005', 'CRM-SP 3005', 'Clínica.', 'USP', 'Rua V, 2200', 'Vila Mariana', 'São Paulo', 'SP', '13h-20h'),
('Dr. Fabio Unha', 'fabio@dermato.com', '33344455506', 'hash_teste', '11966660006', 'CRM-SP 3006', 'Unhas.', 'UNESP', 'Rua W, 2300', 'Lapa', 'São Paulo', 'SP', '08h-12h'),
('Dra. Gabriela Sol', 'gabriela@dermato.com', '33344455507', 'hash_teste', '11966660007', 'CRM-SP 3007', 'Câncer.', 'FMABC', 'Rua X, 2400', 'Santana', 'São Paulo', 'SP', '09h-17h'),
('Dr. Hugo Poro', 'hugo@dermato.com', '33344455508', 'hash_teste', '11966660008', 'CRM-SP 3008', 'Harmonização.', 'Einstein', 'Rua Y, 2500', 'Morumbi', 'São Paulo', 'SP', '10h-20h');

-- 2.4 Ginecologia
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Dra. Isabela Mulher', 'isabela@gino.com', '44455566601', 'hash_teste', '11955550001', 'CRM-SP 4001', 'Obstetrícia.', 'USP', 'Av. Z, 2600', 'Vila Madalena', 'São Paulo', 'SP', '08h-18h'),
('Dr. João Parto', 'joao@gino.com', '44455566602', 'hash_teste', '11955550002', 'CRM-SP 4002', 'Cirurgia.', 'UNIFESP', 'Rua AA, 2700', 'Pinheiros', 'São Paulo', 'SP', '09h-19h'),
('Dra. Karen Hormonio', 'karen@gino.com', '44455566603', 'hash_teste', '11955550003', 'CRM-SP 4003', 'Menopausa.', 'UNICAMP', 'Rua AB, 2800', 'Moema', 'São Paulo', 'SP', '08h-14h'),
('Dr. Leonardo Ultra', 'leo@gino.com', '44455566604', 'hash_teste', '11955550004', 'CRM-SP 4004', 'Ultrassom.', 'Santa Casa', 'Rua AC, 2900', 'Jardins', 'São Paulo', 'SP', '08h-18h'),
('Dra. Maria Gestante', 'maria@gino.com', '44455566605', 'hash_teste', '11955550005', 'CRM-SP 4005', 'Pré-natal.', 'USP', 'Rua AD, 3000', 'Vila Mariana', 'São Paulo', 'SP', '13h-20h'),
('Dr. Nelson Gineco', 'nelson@gino.com', '44455566606', 'hash_teste', '11955550006', 'CRM-SP 4006', 'Video.', 'UNESP', 'Rua AE, 3100', 'Tatuapé', 'São Paulo', 'SP', '08h-12h'),
('Dra. Olivia Fertile', 'olivia@gino.com', '44455566607', 'hash_teste', '11955550007', 'CRM-SP 4007', 'Reprodução.', 'FMABC', 'Rua AF, 3200', 'Santana', 'São Paulo', 'SP', '09h-17h'),
('Dr. Paulo Colpo', 'paulo@gino.com', '44455566608', 'hash_teste', '11955550008', 'CRM-SP 4008', 'Preventivo.', 'Einstein', 'Rua AG, 3300', 'Morumbi', 'São Paulo', 'SP', '10h-20h');

-- 2.5 Pediatria
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Dra. Renata Kids', 'renata@pedia.com', '55566677701', 'hash_teste', '11944440001', 'CRM-SP 5001', 'Puericultura.', 'USP', 'Rua AH, 3400', 'Perdizes', 'São Paulo', 'SP', '08h-18h'),
('Dr. Sergio Baby', 'sergio@pedia.com', '55566677702', 'hash_teste', '11944440002', 'CRM-SP 5002', 'Neonatologia.', 'UNIFESP', 'Rua AI, 3500', 'Vila Mariana', 'São Paulo', 'SP', '09h-19h'),
('Dra. Tatiana Vacina', 'tati@pedia.com', '55566677703', 'hash_teste', '11944440003', 'CRM-SP 5003', 'Alergia.', 'UNICAMP', 'Rua AJ, 3600', 'Moema', 'São Paulo', 'SP', '08h-14h'),
('Dr. Ulisses Teen', 'ulisses@pedia.com', '55566677704', 'hash_teste', '11944440004', 'CRM-SP 5004', 'Adolescentes.', 'Santa Casa', 'Rua AK, 3700', 'Jardins', 'São Paulo', 'SP', '08h-18h'),
('Dra. Vania Crescer', 'vania@pedia.com', '55566677705', 'hash_teste', '11944440005', 'CRM-SP 5005', 'Endócrino.', 'USP', 'Rua AL, 3800', 'Pinheiros', 'São Paulo', 'SP', '13h-20h'),
('Dr. Wagner Pulmao', 'wagner@pedia.com', '55566677706', 'hash_teste', '11944440006', 'CRM-SP 5006', 'Pneumo.', 'UNESP', 'Rua AM, 3900', 'Lapa', 'São Paulo', 'SP', '08h-12h'),
('Dra. Xuxa Neuro', 'xuxa@pedia.com', '55566677707', 'hash_teste', '11944440007', 'CRM-SP 5007', 'Neuro.', 'FMABC', 'Rua AN, 4000', 'Santana', 'São Paulo', 'SP', '09h-17h'),
('Dr. Yuri Gastro', 'yuri@pedia.com', '55566677708', 'hash_teste', '11944440008', 'CRM-SP 5008', 'Gastro.', 'Einstein', 'Rua AO, 4100', 'Morumbi', 'São Paulo', 'SP', '10h-20h');

-- 2.6 Ortopedia
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Dr. Zeca Osso', 'zeca@orto.com', '66677788801', 'hash_teste', '11933330001', 'CRM-SP 6001', 'Joelho.', 'USP', 'Rua AP, 4200', 'Ibirapuera', 'São Paulo', 'SP', '08h-18h'),
('Dra. Alice Coluna', 'alice@orto.com', '66677788802', 'hash_teste', '11933330002', 'CRM-SP 6002', 'Coluna.', 'UNIFESP', 'Rua AQ, 4300', 'Vila Clementino', 'São Paulo', 'SP', '09h-19h'),
('Dr. Bruno Mao', 'bruno.mao@orto.com', '66677788803', 'hash_teste', '11933330003', 'CRM-SP 6003', 'Mão.', 'UNICAMP', 'Rua AR, 4400', 'Moema', 'São Paulo', 'SP', '08h-14h'),
('Dra. Carla Pe', 'carla.pe@orto.com', '66677788804', 'hash_teste', '11933330004', 'CRM-SP 6004', 'Pé.', 'Santa Casa', 'Rua AS, 4500', 'Jardins', 'São Paulo', 'SP', '08h-18h'),
('Dr. Diego Ombro', 'diego@orto.com', '66677788805', 'hash_teste', '11933330005', 'CRM-SP 6005', 'Ombro.', 'USP', 'Rua AT, 4600', 'Pinheiros', 'São Paulo', 'SP', '13h-20h'),
('Dra. Eliana Sport', 'eliana@orto.com', '66677788806', 'hash_teste', '11933330006', 'CRM-SP 6006', 'Esporte.', 'UNESP', 'Rua AU, 4700', 'Pacaembu', 'São Paulo', 'SP', '08h-12h'),
('Dr. Fabio Quadril', 'fabio.quadril@orto.com', '66677788807', 'hash_teste', '11933330007', 'CRM-SP 6007', 'Quadril.', 'FMABC', 'Rua AV, 4800', 'Santana', 'São Paulo', 'SP', '09h-17h'),
('Dra. Gisele Trauma', 'gisele@orto.com', '66677788808', 'hash_teste', '11933330008', 'CRM-SP 6008', 'Trauma.', 'Einstein', 'Rua AW, 4900', 'Morumbi', 'São Paulo', 'SP', '10h-20h');

-- 2.7 Psicologia
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Psic. Ana Freud', 'ana@psi.com', '77788899901', 'hash_teste', '11922220001', 'CRP 06/7001', 'Psicanálise.', 'USP', 'Rua AX, 5000', 'Vila Madalena', 'São Paulo', 'SP', '08h-20h'),
('Psic. Beto Jung', 'beto@psi.com', '77788899902', 'hash_teste', '11922220002', 'CRP 06/7002', 'Analítica.', 'PUC', 'Rua AY, 5100', 'Perdizes', 'São Paulo', 'SP', '09h-19h'),
('Psic. Carla TCC', 'carla@psi.com', '77788899903', 'hash_teste', '11922220003', 'CRP 06/7003', 'TCC.', 'Mackenzie', 'Rua AZ, 5200', 'Higienópolis', 'São Paulo', 'SP', '08h-14h'),
('Psic. Davi Human', 'davi@psi.com', '77788899904', 'hash_teste', '11922220004', 'CRP 06/7004', 'Humanista.', 'UNIP', 'Rua BA, 5300', 'Jardins', 'São Paulo', 'SP', '08h-18h'),
('Psic. Eva Infantil', 'eva@psi.com', '77788899905', 'hash_teste', '11922220005', 'CRP 06/7005', 'Infantil.', 'USP', 'Rua BB, 5400', 'Pinheiros', 'São Paulo', 'SP', '13h-20h'),
('Psic. Fabio Casal', 'fabio.psi@psi.com', '77788899906', 'hash_teste', '11922220006', 'CRP 06/7006', 'Casal.', 'UNESP', 'Rua BC, 5500', 'Lapa', 'São Paulo', 'SP', '08h-12h'),
('Psic. Gabi Luto', 'gabi@psi.com', '77788899907', 'hash_teste', '11922220007', 'CRP 06/7007', 'Luto.', 'FMU', 'Rua BD, 5600', 'Santana', 'São Paulo', 'SP', '09h-17h'),
('Psic. Hugo Sport', 'hugo.psi@psi.com', '77788899908', 'hash_teste', '11922220008', 'CRP 06/7008', 'Esporte.', 'Einstein', 'Rua BE, 5700', 'Morumbi', 'São Paulo', 'SP', '10h-20h');

-- 2.8 Nutrição
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Nutri. Iara Fit', 'iara@nutri.com', '88899900001', 'hash_teste', '11911110001', 'CRN 8001', 'Esportiva.', 'USP', 'Rua BF, 5800', 'Itaim', 'São Paulo', 'SP', '08h-18h'),
('Nutri. Joao Lowcarb', 'joao@nutri.com', '88899900002', 'hash_teste', '11911110002', 'CRN 8002', 'Emagrecimento.', 'São Camilo', 'Rua BG, 5900', 'Vila Mariana', 'São Paulo', 'SP', '09h-19h'),
('Nutri. Kelly Veg', 'kelly@nutri.com', '88899900003', 'hash_teste', '11911110003', 'CRN 8003', 'Vegana.', 'UNICAMP', 'Rua BH, 6000', 'Moema', 'São Paulo', 'SP', '08h-14h'),
('Nutri. Leo Clinico', 'leo@nutri.com', '88899900004', 'hash_teste', '11911110004', 'CRN 8004', 'Clínica.', 'Santa Casa', 'Rua BI, 6100', 'Jardins', 'São Paulo', 'SP', '08h-18h'),
('Nutri. Mara Materno', 'mara@nutri.com', '88899900005', 'hash_teste', '11911110005', 'CRN 8005', 'Materno.', 'USP', 'Rua BJ, 6200', 'Pinheiros', 'São Paulo', 'SP', '13h-20h'),
('Nutri. Nuno Idoso', 'nuno@nutri.com', '88899900006', 'hash_teste', '11911110006', 'CRN 8006', 'Idosos.', 'UNESP', 'Rua BK, 6300', 'Lapa', 'São Paulo', 'SP', '08h-12h'),
('Nutri. Olga Funcional', 'olga@nutri.com', '88899900007', 'hash_teste', '11911110007', 'CRN 8007', 'Funcional.', 'FMU', 'Rua BL, 6400', 'Santana', 'São Paulo', 'SP', '09h-17h'),
('Nutri. Paulo Hospital', 'paulo.nutri@nutri.com', '88899900008', 'hash_teste', '11911110008', 'CRN 8008', 'Hospitalar.', 'Einstein', 'Rua BM, 6500', 'Morumbi', 'São Paulo', 'SP', '10h-20h');

-- 2.9 Odontologia
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Dr. Quintino Dente', 'quintino@odonto.com', '99900011101', 'hash_teste', '11900000001', 'CRO-SP 9001', 'Implanto.', 'USP', 'Rua BN, 6600', 'Saúde', 'São Paulo', 'SP', '08h-18h'),
('Dra. Rita Canal', 'rita@odonto.com', '99900011102', 'hash_teste', '11900000002', 'CRO-SP 9002', 'Canal.', 'UNESP', 'Rua BO, 6700', 'Vila Mariana', 'São Paulo', 'SP', '09h-19h'),
('Dr. Silas Sorriso', 'silas@odonto.com', '99900011103', 'hash_teste', '11900000003', 'CRO-SP 9003', 'Ortodontia.', 'UNICAMP', 'Rua BP, 6800', 'Moema', 'São Paulo', 'SP', '08h-14h'),
('Dra. Tania Clareamento', 'tania@odonto.com', '99900011104', 'hash_teste', '11900000004', 'CRO-SP 9004', 'Estética.', 'UNIP', 'Rua BQ, 6900', 'Jardins', 'São Paulo', 'SP', '08h-18h'),
('Dr. Ugo Cirurgia', 'ugo@odonto.com', '99900011105', 'hash_teste', '11900000005', 'CRO-SP 9005', 'Buco.', 'USP', 'Rua BR, 7000', 'Pinheiros', 'São Paulo', 'SP', '13h-20h'),
('Dra. Vera Kids', 'vera@odonto.com', '99900011106', 'hash_teste', '11900000006', 'CRO-SP 9006', 'Odontoped.', 'UNESP', 'Rua BS, 7100', 'Lapa', 'São Paulo', 'SP', '08h-12h'),
('Dr. Wilson Gengiva', 'wilson@odonto.com', '99900011107', 'hash_teste', '11900000007', 'CRO-SP 9007', 'Perio.', 'FMU', 'Rua BT, 7200', 'Santana', 'São Paulo', 'SP', '09h-17h'),
('Dra. Ximena Harmoniza', 'ximena@odonto.com', '99900011108', 'hash_teste', '11900000008', 'CRO-SP 9008', 'Harmonização.', 'Einstein', 'Rua BU, 7300', 'Morumbi', 'São Paulo', 'SP', '10h-20h');

-- 2.10 Fisioterapia
INSERT INTO profissional (nome, email, cpf, senha_hash, telefone, registro_conselho, biografia, formacao_academica, endereco, bairro, cidade, estado, horario_atendimento) VALUES
('Dr. Yago Fisio', 'yago@fisio.com', '00011122201', 'hash_teste', '11912340001', 'CREFITO 10001', 'Esportiva.', 'USP', 'Rua BV, 7400', 'Ibirapuera', 'São Paulo', 'SP', '07h-17h'),
('Dra. Zaira Pilates', 'zaira@fisio.com', '00011122202', 'hash_teste', '11912340002', 'CREFITO 10002', 'Pilates.', 'UNIFESP', 'Rua BW, 7500', 'Vila Mariana', 'São Paulo', 'SP', '08h-18h'),
('Dr. Alan Costas', 'alan@fisio.com', '00011122203', 'hash_teste', '11912340003', 'CREFITO 10003', 'RPG.', 'UNICAMP', 'Rua BX, 7600', 'Moema', 'São Paulo', 'SP', '07h-13h'),
('Dra. Bia Neuro', 'bia.fisio@fisio.com', '00011122204', 'hash_teste', '11912340004', 'CREFITO 10004', 'Neuro.', 'Santa Casa', 'Rua BY, 7700', 'Jardins', 'São Paulo', 'SP', '08h-18h'),
('Dr. Caio Respire', 'caio@fisio.com', '00011122205', 'hash_teste', '11912340005', 'CREFITO 10005', 'Respiratória.', 'USP', 'Rua BZ, 7800', 'Pinheiros', 'São Paulo', 'SP', '13h-20h'),
('Dra. Dani Dermato', 'dani@fisio.com', '00011122206', 'hash_teste', '11912340006', 'CREFITO 10006', 'Dermato.', 'UNESP', 'Rua CA, 7900', 'Lapa', 'São Paulo', 'SP', '08h-12h'),
('Dr. Edu Acupuntura', 'edu@fisio.com', '00011122207', 'hash_teste', '11912340007', 'CREFITO 10007', 'Acupuntura.', 'FMU', 'Rua CB, 8000', 'Santana', 'São Paulo', 'SP', '09h-17h'),
('Dra. Fabi Pelvica', 'fabi@fisio.com', '00011122208', 'hash_teste', '11912340008', 'CREFITO 10008', 'Pélvica.', 'Einstein', 'Rua CC, 8100', 'Morumbi', 'São Paulo', 'SP', '10h-20h');

-- ==========================================================
-- 10. VINCULAR FILTROS E PREÇOS (Lógica Automática)
-- ==========================================================

-- Especialidades
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 1 FROM profissional WHERE idProfissional BETWEEN 1 AND 10;
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 2 FROM profissional WHERE idProfissional BETWEEN 11 AND 18;
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 3 FROM profissional WHERE idProfissional BETWEEN 19 AND 26;
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 4 FROM profissional WHERE idProfissional BETWEEN 27 AND 34;
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 5 FROM profissional WHERE idProfissional BETWEEN 35 AND 42;
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 6 FROM profissional WHERE idProfissional BETWEEN 43 AND 50;
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 7 FROM profissional WHERE idProfissional BETWEEN 51 AND 58;
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 8 FROM profissional WHERE idProfissional BETWEEN 59 AND 66;
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 9 FROM profissional WHERE idProfissional BETWEEN 67 AND 74;
INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) SELECT idProfissional, 10 FROM profissional WHERE idProfissional BETWEEN 75 AND 82;

-- Modalidades
INSERT IGNORE INTO profissional_modalidades (idProfissional, idModalidade) SELECT idProfissional, 1 FROM profissional; -- Todos Presencial
INSERT IGNORE INTO profissional_modalidades (idProfissional, idModalidade) SELECT idProfissional, 2 FROM profissional WHERE idProfissional % 2 = 0; -- Pares Telemedicina
INSERT IGNORE INTO profissional_modalidades (idProfissional, idModalidade) SELECT idProfissional, 3 FROM profissional WHERE idProfissional % 3 = 0; -- Múltiplos 3 Domiciliar

-- Comodidades (Estacionamento/Acessibilidade)
INSERT IGNORE INTO profissional_comodidades (idProfissional, idComodidade) SELECT idProfissional, 2 FROM profissional WHERE idProfissional % 2 = 0; -- Pares tem Estacionamento
INSERT IGNORE INTO profissional_comodidades (idProfissional, idComodidade) SELECT idProfissional, 3 FROM profissional WHERE idProfissional % 3 = 0; -- Multiplos 3 tem Acessibilidade

-- Convênios
INSERT IGNORE INTO profissional_convenios (idProfissional, idConvenio) SELECT idProfissional, 1 FROM profissional;
INSERT IGNORE INTO profissional_convenios (idProfissional, idConvenio) SELECT idProfissional, 2 FROM profissional WHERE idProfissional % 2 = 0;

-- Serviços com Preços Reais (Para média funcionar)
INSERT INTO servicos_profissional (idProfissional, nome, preco) SELECT idProfissional, 'Consulta Particular', 'R$ 200,00' FROM profissional;
INSERT INTO servicos_profissional (idProfissional, nome, preco) SELECT idProfissional, 'Retorno', 'R$ 100,00' FROM profissional; -- Retorno com valor pra não zerar a média

-- ==========================================================
-- 11. REATIVAR TRAVAS DE SEGURANÇA
-- ==========================================================
SET SQL_SAFE_UPDATES = 1; 