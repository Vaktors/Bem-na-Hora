# routes.py
from flask import (
    render_template, session, redirect, url_for,
    request, jsonify
)
from flask_mail import Message
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random
import re
import os
import mysql.connector
from collections import defaultdict
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="senac",
        database="BemNaHora",
        port=3307
    )
from utils import (
    gerar_codigo, limpar_cpf, limpar_cnpj, converter_data, formatar_data,
    formatar_cpf, allowed_file, MAPEAMENTO_CONVENIOS
)
def register_routes(app, mail):
    # ----------------------------- --
    # ROTAS PRINCIPAIS
    # -------------------------------
    @app.route('/')
    def index():
        return render_template('index.html')
    @app.route('/vitrine')
    def vitrine():
        return render_template('vitrine.html')
    @app.route('/agenda')
    def agenda():
        # Redirecionar baseado no tipo de usuário
        if 'profissional_id' in session:
            return redirect(url_for('agenda_profissional'))
        elif 'clinica_id' in session:
            return redirect(url_for('agenda_clinica'))
        elif 'user_id' in session:
            return render_template('agenda.html')  # Agenda do usuário comum
        else:
            return redirect(url_for('cadastro_usuario'))
    
    @app.route('/agenda/profissional')
    def agenda_profissional():
        if 'profissional_id' not in session:
            return redirect(url_for('cadastro_usuario'))
        return render_template('agenda.html')  # Mesmo template, mas com dados do profissional
    
    @app.route('/agenda/clinica')
    def agenda_clinica():
        if 'clinica_id' not in session:
            return redirect(url_for('cadastro_usuario'))
        return render_template('agenda.html')  # Mesmo template, mas com dados da clínica
    # -------------------------------
    # ROTAS DE CADASTRO / LOGIN
    # -------------------------------
    @app.route('/cadastro/usuario')
    def cadastro_usuario():
        return render_template('cadastro.html')
    @app.route('/cadastro/parceiro')
    def cadastro_parceiro():
        return render_template('medico.html')
    @app.route('/recuperar-senha')
    def redefinir_senha():
        return render_template('redefinirSenha.html')
    @app.route('/confirma-email')
    def confirma_email():
        if 'dados_cadastro' not in session:
            return redirect(url_for('cadastro_usuario'))
        email = session.get('dados_cadastro', {}).get('email', 'email@exemplo.com')
        return render_template('confirmaEmail.html', email=email)
    # -------------------------------
    # FUNÇÃO: Buscar usuário logado
    # -------------------------------
    def get_usuario_logado():
        if 'user_id' not in session:
            return None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.*, c.nome as convenio_nome
                FROM usuario u
                LEFT JOIN convenios c ON u.idConvenio = c.idConvenio
                WHERE u.idUsuario = %s
            """, (session['user_id'],))
            usuario = cursor.fetchone()
            cursor.close()
            conn.close()
            if usuario:
                if usuario.get('dataNasc'):
                    usuario['dataNasc_formatada'] = formatar_data(usuario['dataNasc'])
                if usuario.get('cpf'):
                    usuario['cpf_formatado'] = formatar_cpf(usuario['cpf'])
                # Formatar telefone
                tel = usuario.get('telefone')
                if tel and len(tel) in [10, 11]:
                    if len(tel) == 11:
                        usuario['telefone_formatado'] = f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
                    else:
                        usuario['telefone_formatado'] = f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
                else:
                    usuario['telefone_formatado'] = tel
            return usuario
        except Exception as e:
            print("Erro ao buscar usuário:", e)
            return None
    # -------------------------------
    # API: Cadastro
    # -------------------------------
    @app.route('/api/cadastro', methods=['POST'])
    def api_cadastro():
        try:
            dados = request.get_json()
            nome = dados.get('nome', '').strip()
            email = dados.get('email', '').strip().lower()
            cpf = limpar_cpf(dados.get('cpf', ''))
            genero = dados.get('genero', '')
            data_nasc = dados.get('data_nasc', '')
            telefone = dados.get('telefone', '').strip()
            senha = dados.get('senha', '')
            convenio = dados.get('convenio', '')
            if not all([nome, email, cpf, genero, data_nasc, telefone, senha]):
                return jsonify({'success': False, 'message': 'Preencha todos os campos obrigatórios'}), 400
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                return jsonify({'success': False, 'message': 'Email inválido'}), 400
            if len(cpf) != 11:
                return jsonify({'success': False, 'message': 'CPF inválido'}), 400
            if genero not in ['M', 'F', 'O']:
                return jsonify({'success': False, 'message': 'Gênero inválido'}), 400
            data_nasc_formatada = converter_data(data_nasc)
            if not data_nasc_formatada:
                return jsonify({'success': False, 'message': 'Data inválida'}), 400
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT idUsuario FROM usuario WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Email já cadastrado'}), 400
            cursor.execute("SELECT idUsuario FROM usuario WHERE cpf = %s", (cpf,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'CPF já cadastrado'}), 400
            cursor.close()
            conn.close()
            codigo = gerar_codigo()
            session['dados_cadastro'] = {
                'nome': nome,
                'email': email,
                'cpf': cpf,
                'genero': genero,
                'data_nasc': data_nasc_formatada,
                'telefone': telefone,
                'senha_hash': generate_password_hash(senha),
                'convenio': convenio,
                'codigo': codigo,
                'data_expiracao': (datetime.now() + timedelta(minutes=10)).isoformat()
            }
            try:
                msg = Message(
                    subject="Confirmação de Email - Bem Na Hora",
                    recipients=[email],
                    html=f"""
                        <h2>Bem-vindo!</h2>
                        <p>Seu código de confirmação:</p>
                        <h1>{codigo}</h1>
                        <p>Válido por 10 minutos.</p>
                    """
                )
                mail.send(msg)
            except Exception as e:
                print("Erro ao enviar email:", e)
                return jsonify({'success': False, 'message': 'Erro ao enviar email'}), 500
            return jsonify({
                'success': True,
                'message': 'Código enviado!',
                'redirect': url_for('confirma_email')
            })
        except Exception as e:
            print("Erro no cadastro:", e)
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Confirmar Email
    # -------------------------------
    @app.route('/api/confirmar-email', methods=['POST'])
    def api_confirmar_email():
        try:
            dados = request.get_json()
            codigo_digitado = dados.get('codigo', '').strip()
            if 'dados_cadastro' not in session:
                return jsonify({'success': False, 'message': 'Sessão expirada'}), 400
            dados_cadastro = session['dados_cadastro']
            if codigo_digitado != dados_cadastro['codigo']:
                return jsonify({'success': False, 'message': 'Código incorreto'}), 400
            if datetime.now() > datetime.fromisoformat(dados_cadastro['data_expiracao']):
                session.pop('dados_cadastro', None)
                return jsonify({'success': False, 'message': 'Código expirado'}), 400
            # Convênio
            id_convenio = None
            conv = dados_cadastro['convenio']
            if conv and conv != "Nenhum":
                nome_banco = MAPEAMENTO_CONVENIOS.get(conv)
                if nome_banco:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT idConvenio FROM convenios WHERE nome = %s", (nome_banco,))
                    r = cursor.fetchone()
                    if r:
                        id_convenio = r[0]
                    cursor.close()
                    conn.close()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuario (nome, email, cpf, genero, dataNasc, senha_hash, telefone, idConvenio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dados_cadastro['nome'],
                dados_cadastro['email'],
                dados_cadastro['cpf'],
                dados_cadastro['genero'],
                dados_cadastro['data_nasc'],
                dados_cadastro['senha_hash'],
                dados_cadastro['telefone'],
                id_convenio
            ))
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            conn.close()
            session.pop('dados_cadastro', None)
            session['user_id'] = user_id
            session['user_email'] = dados_cadastro['email']
            session['user_nome'] = dados_cadastro['nome']
            return jsonify({'success': True, 'redirect': url_for('perfil_usuario')})
        except Exception as e:
            print("Erro confirmar email:", e)
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Login
    # -------------------------------
    @app.route('/api/login', methods=['POST'])
    def api_login():
        try:
            dados = request.get_json()
            email = dados.get('email', '').lower()
            senha = dados.get('senha', '')
            if not email or not senha:
                return jsonify({'success': False, 'message': 'Preencha email e senha'}), 400
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Prioridade: profissional > clínica > usuário comum
            # Tentar login como profissional primeiro
            cursor.execute("SELECT * FROM profissional WHERE email = %s", (email,))
            profissional = cursor.fetchone()
            
            if profissional and check_password_hash(profissional['senha_hash'], senha):
                session['profissional_id'] = profissional['idProfissional']
                session['profissional_email'] = profissional['email']
                session['profissional_nome'] = profissional['nome']
                # Limpar outras sessões
                session.pop('user_id', None)
                session.pop('clinica_id', None)
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'redirect': url_for('doutor_editar')})
            
            # Tentar login como clínica
            cursor.execute("SELECT * FROM clinica WHERE email = %s", (email,))
            clinica = cursor.fetchone()
            
            if clinica and check_password_hash(clinica['senha_hash'], senha):
                session['clinica_id'] = clinica['idClinica']
                session['clinica_email'] = clinica['email']
                session['clinica_nome'] = clinica['nomeExibicao'] or clinica['nome']
                # Limpar outras sessões
                session.pop('user_id', None)
                session.pop('profissional_id', None)
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'redirect': url_for('clinica_editar')})
            
            # Tentar login como usuário comum por último
            cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
            usuario = cursor.fetchone()
            
            if usuario and check_password_hash(usuario['senha_hash'], senha):
                session['user_id'] = usuario['idUsuario']
                session['user_email'] = usuario['email']
                session['user_nome'] = usuario['nome']
                # Limpar outras sessões
                session.pop('profissional_id', None)
                session.pop('clinica_id', None)
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'redirect': url_for('perfil_usuario')})
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
        except Exception as e:
            print("Erro login:", e)
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Logout
    # -------------------------------
    @app.route('/api/logout', methods=['POST'])
    def api_logout():
        # Limpar todas as sessões possíveis
        session.pop('user_id', None)
        session.pop('user_email', None)
        session.pop('user_nome', None)
        session.pop('profissional_id', None)
        session.pop('profissional_email', None)
        session.pop('profissional_nome', None)
        session.pop('clinica_id', None)
        session.pop('clinica_email', None)
        session.pop('clinica_nome', None)
        session.clear()
        return jsonify({'success': True, 'redirect': url_for('index')})
    # -------------------------------
    # API: Atualizar Perfil
    # -------------------------------
    @app.route('/api/perfil/atualizar', methods=['POST'])
    def api_atualizar_perfil():
        try:
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Não autenticado'}), 401
            dados = request.get_json()
            user_id = session['user_id']
            campos = {}
            if 'cpf' in dados:
                cpf = limpar_cpf(dados['cpf'])
                if len(cpf) == 11:
                    campos['cpf'] = cpf
            if 'data_nasc' in dados:
                d = converter_data(dados['data_nasc'])
                if d:
                    campos['dataNasc'] = d
            if 'telefone' in dados:
                tel = re.sub(r'\D', '', dados['telefone'])
                campos['telefone'] = tel
            # Endereço
            if 'rua' in dados: campos['rua'] = dados['rua'] or None
            if 'bairro' in dados: campos['bairro'] = dados['bairro'] or None
            if 'cidade' in dados: campos['cidade'] = dados['cidade'] or None
            if 'estado' in dados: campos['estado'] = dados['estado'][:2].upper() or None
            if 'cep' in dados:
                campos['cep'] = re.sub(r'\D', '', dados['cep']) or None
            if not campos:
                return jsonify({'success': False, 'message': 'Nada a atualizar'}), 400
            conn = get_db_connection()
            cursor = conn.cursor()
            sets = ", ".join(f"{k}=%s" for k in campos)
            valores = list(campos.values()) + [user_id]
            cursor.execute(f"UPDATE usuario SET {sets} WHERE idUsuario = %s", valores)
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Atualizado!'})
        except Exception as e:
            print("Erro atualizar:", e)
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Agendamentos do usuário
    # -------------------------------
    @app.route('/api/perfil/agendamentos', methods=['GET'])
    def api_agendamentos_usuario():
        try:
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Não autenticado'}), 401
            user_id = session['user_id']
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    a.*,
                    COALESCE(p.nome, c.nomeExibicao, 'Não especificado') AS nome_profissional,
                    COALESCE(proc.nome, serv.nome, 'Consulta') AS tipo_servico
                FROM agendamento a
                LEFT JOIN profissional p ON a.idProfissional = p.idProfissional
                LEFT JOIN clinica c ON a.idClinica = c.idClinica
                LEFT JOIN procedimentos proc ON a.idProcedimento = proc.idProcedimento
                LEFT JOIN servicos_profissional serv ON a.idServico = serv.idServico
                WHERE idUsuario = %s
                ORDER BY a.data_hora_inicio DESC
                LIMIT 50
            """, (user_id,))
            ags = cursor.fetchall()
            lista = []
            for ag in ags:
                data = ag['data_hora_inicio']
                if isinstance(data, datetime):
                    data = data.strftime('%d/%m/%Y')
                else:
                    data = str(data)
                lista.append({
                    'data': data,
                    'medico_clinica': ag['nome_profissional'],
                    'tipo': ag['tipo_servico'],
                    'status': ag['status']
                })
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'agendamentos': lista})
        except Exception as e:
            print("Erro agendamentos:", e)
            return jsonify({'success': False, 'message': 'Erro interno'}), 500

    from datetime import datetime, timedelta # Importe o timedelta

    @app.route('/api/agendar-consulta', methods=['POST'])
    def api_agendar_consulta():
        try:
            # 1. Verificação de Login
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Você precisa estar logado para agendar.'}), 401
                
            data = request.get_json()
            user_id = session['user_id']
            
            # 2. Coletar dados
            servico_id = data.get('servico_id')
            data_agendamento = data.get('data')   
            horario = data.get('horario')         
            
            # Validação simples
            if not all([servico_id, data_agendamento, horario]):
                return jsonify({'success': False, 'message': 'Dados incompletos.'}), 400

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 3. Validar Serviço e Pegar ID do Profissional
            # Importante: Confirme se a tabela servicos_profissional tem a coluna 'preco'
            cursor.execute("SELECT idProfissional, nome FROM servicos_profissional WHERE idServico = %s", (servico_id,))
            servico_db = cursor.fetchone()
            
            if not servico_db:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Serviço não encontrado.'}), 404
                
            id_profissional = servico_db['idProfissional']
            
            # 4. Calcular Datas (Inicio e Fim)
            # Formato string para datetime
            data_hora_inicio_str = f"{data_agendamento} {horario}:00"
            dt_inicio = datetime.strptime(data_hora_inicio_str, '%Y-%m-%d %H:%M:%S')
            
            # Adiciona 30 minutos para criar a data fim (obrigatória no seu banco)
            dt_fim = dt_inicio + timedelta(minutes=30)
            
            # 5. Inserir na tabela agendamento
            # CORREÇÃO: Adicionado data_hora_fim e removido data_criacao (que não existe no seu SQL)
            cursor.execute("""
                INSERT INTO agendamento 
                (idUsuario, idProfissional, idServico, data_hora_inicio, data_hora_fim, status)
                VALUES (%s, %s, %s, %s, %s, 'Agendado')
            """, (user_id, id_profissional, servico_id, dt_inicio, dt_fim))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Consulta agendada com sucesso!'})

        except Exception as e:
            print(f"Erro ao agendar: {e}")
            return jsonify({'success': False, 'message': 'Erro interno ao processar agendamento.'}), 500
    # -------------------------------
    # API: Upload Foto
    # -------------------------------
    @app.route('/api/perfil/upload-foto', methods=['POST'])
    def api_upload_foto():
        try:
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Não autenticado'}), 401
            if 'foto' not in request.files:
                return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
            file = request.files['foto']
            uid = session['user_id']
            if file.filename == '':
                return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'message': 'Tipo inválido. Use PNG, JPG, JPEG, GIF, WEBP'
                }), 400
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = file.filename.rsplit('.', 1)[1].lower()
            nome_final = f"perfil_{uid}_{timestamp}.{ext}"
            path = os.path.join(app.config['UPLOAD_FOLDER'], nome_final)
            file.save(path)
            # Remover foto antiga
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT foto_perfil FROM usuario WHERE idUsuario = %s", (uid,))
            r = cursor.fetchone()
            if r and r.get('foto_perfil'):
                antigo = os.path.join(app.config['UPLOAD_FOLDER'], r['foto_perfil'])
                if os.path.exists(antigo):
                    try: os.remove(antigo)
                    except: pass
            cursor.execute("UPDATE usuario SET foto_perfil=%s WHERE idUsuario=%s", (nome_final, uid))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({
                'success': True,
                'foto_url': url_for('static', filename=f'uploads/{nome_final}')
            })
        except Exception as e:
            print("Erro upload foto:", e)
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Cadastro Profissional
    # -------------------------------
    @app.route('/api/cadastro/profissional', methods=['POST'])
    def api_cadastro_profissional():
        try:
            dados = request.get_json()
            
            nome = dados.get('nome', '').strip()
            email = dados.get('email', '').strip().lower()
            cpf = limpar_cpf(dados.get('cpf', ''))
            telefone = re.sub(r'\D', '', dados.get('telefone', ''))
            registro_conselho = dados.get('registro', '').strip()
            senha = dados.get('senha', '')
            
            # Validações
            if not all([nome, email, cpf, telefone, registro_conselho, senha]):
                return jsonify({'success': False, 'message': 'Preencha todos os campos obrigatórios'}), 400
            
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                return jsonify({'success': False, 'message': 'Email inválido'}), 400
            
            if len(cpf) != 11:
                return jsonify({'success': False, 'message': 'CPF inválido'}), 400
            
            # Verificar se email já existe
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT idProfissional FROM profissional WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Este email já está cadastrado'}), 400
            
            # Verificar se CPF já existe
            cursor.execute("SELECT idProfissional FROM profissional WHERE cpf = %s", (cpf,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Este CPF já está cadastrado'}), 400
            
            # Inserir profissional
            cursor.execute("""
                INSERT INTO profissional (nome, email, cpf, telefone, registro_conselho, senha_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                nome,
                email,
                cpf,
                telefone,
                registro_conselho,
                generate_password_hash(senha)
            ))
            
            conn.commit()
            profissional_id = cursor.lastrowid
            
            cursor.close()
            conn.close()
            
            # Criar sessão para o profissional
            session['profissional_id'] = profissional_id
            session['profissional_email'] = email
            session['profissional_nome'] = nome
            
            return jsonify({
                'success': True,
                'message': 'Cadastro realizado com sucesso!',
                'redirect': url_for('doutor_editar')
            }), 200
            
        except mysql.connector.IntegrityError as e:
            return jsonify({'success': False, 'message': 'Email ou CPF já cadastrado'}), 400
        except Exception as e:
            print(f"Erro no cadastro profissional: {e}")
            return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
    # -------------------------------
    # API: Cadastro Clínica
    # -------------------------------
    @app.route('/api/cadastro/clinica', methods=['POST'])
    def api_cadastro_clinica():
        try:
            dados = request.get_json()
            
            nome = dados.get('nome', '').strip()  # Razão Social
            email = dados.get('email', '').strip().lower()
            cnpj = limpar_cnpj(dados.get('cnpj', ''))
            telefone = re.sub(r'\D', '', dados.get('telefone', ''))
            registro_tecnico = dados.get('registro', '').strip()
            senha = dados.get('senha', '')
            
            # Validações
            if not all([nome, email, cnpj, telefone, registro_tecnico, senha]):
                return jsonify({'success': False, 'message': 'Preencha todos os campos obrigatórios'}), 400
            
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                return jsonify({'success': False, 'message': 'Email inválido'}), 400
            
            if len(cnpj) != 14:
                return jsonify({'success': False, 'message': 'CNPJ inválido'}), 400
            
            # Verificar se email já existe
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT idClinica FROM clinica WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Este email já está cadastrado'}), 400
            
            # Verificar se CNPJ já existe
            cursor.execute("SELECT idClinica FROM clinica WHERE cnpj = %s", (cnpj,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Este CNPJ já está cadastrado'}), 400
            
            # Inserir clínica
            cursor.execute("""
                INSERT INTO clinica (nome, email, cnpj, telefone, registroTecnico, senha_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                nome,
                email,
                cnpj,
                telefone,
                registro_tecnico,
                generate_password_hash(senha)
            ))
            
            conn.commit()
            clinica_id = cursor.lastrowid
            
            cursor.close()
            conn.close()
            
            # Criar sessão para a clínica
            session['clinica_id'] = clinica_id
            session['clinica_email'] = email
            session['clinica_nome'] = nome
            
            return jsonify({
                'success': True,
                'message': 'Cadastro realizado com sucesso!',
                'redirect': url_for('clinica_editar')
            }), 200
            
        except mysql.connector.IntegrityError as e:
            return jsonify({'success': False, 'message': 'Email ou CNPJ já cadastrado'}), 400
        except Exception as e:
            print(f"Erro no cadastro clínica: {e}")
            return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
    # -------------------------------
    # API: Upload Foto Profissional
    # -------------------------------
    @app.route('/api/profissional/upload-foto', methods=['POST'])
    def api_upload_foto_profissional():
        try:
            if 'profissional_id' not in session:
                return jsonify({'success': False, 'message': 'Não autenticado'}), 401
            
            if 'foto' not in request.files:
                return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
            
            file = request.files['foto']
            prof_id = session['profissional_id']
            
            if file.filename == '':
                return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'Tipo inválido. Use PNG, JPG, JPEG, GIF, WEBP'}), 400
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = file.filename.rsplit('.', 1)[1].lower()
            nome_final = f"prof_{prof_id}_{timestamp}.{ext}"
            
            path = os.path.join(app.config['UPLOAD_FOLDER'], nome_final)
            file.save(path)
            
            # Remover foto antiga
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT foto_perfil FROM profissional WHERE idProfissional = %s", (prof_id,))
            r = cursor.fetchone()
            
            if r and r.get('foto_perfil'):
                antigo = os.path.join(app.config['UPLOAD_FOLDER'], r['foto_perfil'])
                if os.path.exists(antigo):
                    try: os.remove(antigo)
                    except: pass
            
            cursor.execute("UPDATE profissional SET foto_perfil=%s WHERE idProfissional=%s", (nome_final, prof_id))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'foto_url': url_for('static', filename=f'uploads/{nome_final}')
            })
        except Exception as e:
            print(f"Erro upload foto profissional: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Upload Foto Clínica
    # -------------------------------
    @app.route('/api/clinica/upload-foto', methods=['POST'])
    def api_upload_foto_clinica():
        try:
            if 'clinica_id' not in session:
                return jsonify({'success': False, 'message': 'Não autenticado'}), 401
            
            if 'foto' not in request.files:
                return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
            
            file = request.files['foto']
            clinica_id = session['clinica_id']
            
            if file.filename == '':
                return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'Tipo inválido. Use PNG, JPG, JPEG, GIF, WEBP'}), 400
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = file.filename.rsplit('.', 1)[1].lower()
            nome_final = f"clinica_{clinica_id}_{timestamp}.{ext}"
            
            path = os.path.join(app.config['UPLOAD_FOLDER'], nome_final)
            file.save(path)
            
            # Remover foto antiga
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT foto_perfil FROM clinica WHERE idClinica = %s", (clinica_id,))
            r = cursor.fetchone()
            
            if r and r.get('foto_perfil'):
                antigo = os.path.join(app.config['UPLOAD_FOLDER'], r['foto_perfil'])
                if os.path.exists(antigo):
                    try: os.remove(antigo)
                    except: pass
            
            cursor.execute("UPDATE clinica SET foto_perfil=%s WHERE idClinica=%s", (nome_final, clinica_id))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'foto_url': url_for('static', filename=f'uploads/{nome_final}')
            })
        except Exception as e:
            print(f"Erro upload foto clínica: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Atualizar Profissional
    # -------------------------------
    @app.route('/api/profissional/atualizar', methods=['POST'])
    def api_atualizar_profissional():
        try:
            if 'profissional_id' not in session:
                return jsonify({'success': False, 'message': 'Não autenticado'}), 401
            
            dados = request.get_json()
            profissional_id = session['profissional_id']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Atualizar dados básicos
            campos_update = {}
            if 'nome' in dados:
                campos_update['nome'] = dados['nome'].strip()[:100]
            if 'biografia' in dados:
                campos_update['biografia'] = dados['biografia'].strip()[:65535]
            if 'endereco' in dados:
                campos_update['endereco'] = dados['endereco'].strip()[:200]
            if 'bairro' in dados:
                campos_update['bairro'] = dados['bairro'].strip()[:100]
            if 'cidade' in dados:
                campos_update['cidade'] = dados['cidade'].strip()[:100]
            if 'estado' in dados:
                campos_update['estado'] = dados['estado'][:2].upper() or None
            if 'telefone' in dados:
                campos_update['telefone'] = re.sub(r'\D', '', dados['telefone'])[:20]
            if 'horarioSemana' in dados or 'horarioFimSemana' in dados:
                horario = f"{dados.get('horarioSemana', '')} | {dados.get('horarioFimSemana', '')}"
                campos_update['horario_atendimento'] = horario.strip()[:150]
            if 'site' in dados:
                campos_update['site_url'] = dados['site'].strip()[:150]
            if 'instagram' in dados:
                campos_update['instagram'] = dados['instagram'].strip()[:100]
            
            if campos_update:
                sets = ", ".join(f"{k}=%s" for k in campos_update)
                valores = list(campos_update.values()) + [profissional_id]
                cursor.execute(f"UPDATE profissional SET {sets} WHERE idProfissional = %s", valores)
            
            # Atualizar serviços
            if 'servicos' in dados and isinstance(dados['servicos'], list):
                cursor.execute("DELETE FROM servicos_profissional WHERE idProfissional = %s", (profissional_id,))
                for servico in dados['servicos']:
                    if servico.get('nome') and servico.get('preco'):
                        cursor.execute(
                            "INSERT INTO servicos_profissional (idProfissional, nome, preco) VALUES (%s, %s, %s)",
                            (profissional_id, servico['nome'][:100], servico['preco'][:50])
                        )
            
            # Atualizar convênios
            if 'convenios' in dados and isinstance(dados['convenios'], list):
                cursor.execute("DELETE FROM profissional_convenios WHERE idProfissional = %s", (profissional_id,))
                for conv_nome in dados['convenios']:
                    nome_banco = MAPEAMENTO_CONVENIOS.get(conv_nome, conv_nome)
                    cursor.execute("SELECT idConvenio FROM convenios WHERE nome = %s", (nome_banco,))
                    r = cursor.fetchone()
                    if r:
                        cursor.execute(
                            "INSERT INTO profissional_convenios (idProfissional, idConvenio) VALUES (%s, %s)",
                            (profissional_id, r[0])
                        )
            
            # Atualizar especialidades
            if 'especialidade' in dados and dados['especialidade'].strip():
                cursor.execute("DELETE FROM profissional_especialidade WHERE idProfissional = %s", (profissional_id,))
                especialidade_nome = dados['especialidade'].strip()
                cursor.execute("SELECT idEspecialidade FROM especialidades WHERE nome = %s", (especialidade_nome,))
                r = cursor.fetchone()
                if r:
                    cursor.execute(
                        "INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) VALUES (%s, %s)",
                        (profissional_id, r[0])
                    )
                else:
                    # Se não existir, inserir nova especialidade
                    cursor.execute("INSERT INTO especialidades (nome) VALUES (%s)", (especialidade_nome,))
                    nova_id = cursor.lastrowid
                    cursor.execute(
                        "INSERT INTO profissional_especialidade (idProfissional, idEspecialidade) VALUES (%s, %s)",
                        (profissional_id, nova_id)
                    )
            # Atualizar formação acadêmica (salvar como JSON/TEXT)
            if 'formacao' in dados and isinstance(dados['formacao'], list):
                formacao_str = '||'.join([f"{f.get('curso', '')} - {f.get('instituicao', '')}" for f in dados['formacao'] if f.get('curso') and f.get('instituicao')])
                cursor.execute("UPDATE profissional SET formacao_academica = %s WHERE idProfissional = %s", (formacao_str, profissional_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso!'})
        except Exception as e:
            print(f"Erro ao atualizar profissional: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Atualizar Clínica
    # -------------------------------
    @app.route('/api/clinica/atualizar', methods=['POST'])
    def api_atualizar_clinica():
        try:
            if 'clinica_id' not in session:
                return jsonify({'success': False, 'message': 'Não autenticado'}), 401
            
            dados = request.get_json()
            clinica_id = session['clinica_id']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Atualizar dados básicos
            campos_update = {}
            if 'nome' in dados:
                campos_update['nomeExibicao'] = dados['nome'].strip()[:100]
            if 'tipo' in dados:
                campos_update['tipo'] = dados['tipo'].strip()[:50]
            if 'fundacao' in dados:
                try:
                    campos_update['ano_fundacao'] = int(dados['fundacao'])
                except:
                    pass
            if 'diretor' in dados:
                campos_update['diretor_tecnico'] = dados['diretor'].strip()[:100]
            if 'historia' in dados:
                campos_update['historia'] = dados['historia'].strip()[:65535]
            if 'endereco' in dados:
                campos_update['endereco'] = dados['endereco'].strip()[:200]
            if 'bairro' in dados:
                campos_update['bairro'] = dados['bairro'].strip()[:100]
            if 'cidade' in dados:
                campos_update['cidade'] = dados['cidade'].strip()[:100]
            if 'estado' in dados:
                campos_update['estado'] = dados['estado'][:2].upper() or None
            if 'telefone' in dados:
                campos_update['telefone'] = re.sub(r'\D', '', dados['telefone'])[:20]
            if 'horarioSemana' in dados:
                campos_update['horario_semana'] = dados['horarioSemana'].strip()[:100]
            if 'horarioFimSemana' in dados:
                campos_update['horario_fim_sem'] = dados['horarioFimSemana'].strip()[:100]
            if 'site' in dados:
                campos_update['site_url'] = dados['site'].strip()[:150]
            if 'instagram' in dados:
                campos_update['instagram'] = dados['instagram'].strip()[:100]
            
            if campos_update:
                sets = ", ".join(f"{k}=%s" for k in campos_update)
                valores = list(campos_update.values()) + [clinica_id]
                cursor.execute(f"UPDATE clinica SET {sets} WHERE idClinica = %s", valores)
            
            # Atualizar equipe médica
            if 'equipe' in dados and isinstance(dados['equipe'], list):
                cursor.execute("DELETE FROM equipe_medica WHERE idClinica = %s", (clinica_id,))
                for membro in dados['equipe']:
                    if membro.get('nome') and membro.get('especialidade'):
                        cursor.execute(
                            "INSERT INTO equipe_medica (idClinica, nome, especialidade, experiencia) VALUES (%s, %s, %s, %s)",
                            (clinica_id, membro['nome'][:100], membro['especialidade'][:100], membro.get('xp', '')[:50])
                        )
            
            # Atualizar procedimentos
            if 'servicos' in dados and isinstance(dados['servicos'], list):
                cursor.execute("DELETE FROM procedimentos WHERE idClinica = %s", (clinica_id,))
                for servico in dados['servicos']:
                    if servico.get('nome') and servico.get('preco'):
                        cursor.execute(
                            "INSERT INTO procedimentos (idClinica, nome, preco) VALUES (%s, %s, %s)",
                            (clinica_id, servico['nome'][:100], servico['preco'][:50])
                        )
            
            # Atualizar convênios
            if 'convenios' in dados and isinstance(dados['convenios'], list):
                cursor.execute("DELETE FROM clinica_convenios WHERE idClinica = %s", (clinica_id,))
                for conv_nome in dados['convenios']:
                    nome_banco = MAPEAMENTO_CONVENIOS.get(conv_nome, conv_nome)
                    cursor.execute("SELECT idConvenio FROM convenios WHERE nome = %s", (nome_banco,))
                    r = cursor.fetchone()
                    if r:
                        cursor.execute(
                            "INSERT INTO clinica_convenios (idClinica, idConvenio) VALUES (%s, %s)",
                            (clinica_id, r[0])
                        )
            
            # Atualizar comodidades (infraestrutura)
            if 'infraestrutura' in dados and isinstance(dados['infraestrutura'], list):
                cursor.execute("DELETE FROM clinica_comodidades WHERE idClinica = %s", (clinica_id,))
                for infra in dados['infraestrutura']:
                    cursor.execute("SELECT idComodidade FROM comodidades WHERE nome = %s", (infra,))
                    r = cursor.fetchone()
                    if r:
                        cursor.execute(
                            "INSERT INTO clinica_comodidades (idClinica, idComodidade) VALUES (%s, %s)",
                            (clinica_id, r[0])
                        )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Perfil da clínica atualizado com sucesso!'})
        except Exception as e:
            print(f"Erro ao atualizar clínica: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Contar Modalidades (Para os números dinâmicos) - COM FILTROS
    # -------------------------------
    @app.route('/api/vitrine/counts', methods=['GET'])
    def api_vitrine_counts():
        try:
            # ADICIONADO: Todos os filtros incluindo busca textual e localização
            tipo = request.args.get('tipo', 'profissional')
            filtro_especialidade = request.args.get('especialidade')
            filtro_modalidades = request.args.getlist('modalidades[]')
            busca_textual = request.args.get('busca', '').strip()
            busca_localizacao = request.args.get('localizacao', '').strip()
            tem_convenio = request.args.get('aceita_convenio') == 'true'
            tem_estacionamento = request.args.get('estacionamento') == 'true'
            tem_acessibilidade = request.args.get('acessibilidade') == 'true'
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)

            if tipo == 'profissional':
                sql = """
                    SELECT m.nome as modalidade, COUNT(DISTINCT pm.idProfissional) as count
                    FROM modalidades m
                    LEFT JOIN profissional_modalidades pm ON m.idModalidade = pm.idModalidade
                    LEFT JOIN profissional p ON pm.idProfissional = p.idProfissional
                """
                params = []
                joins = []
                where_conditions = ["pm.idProfissional IS NOT NULL"]

                if filtro_especialidade and filtro_especialidade != "Todas as especialidades":
                    joins.append("""
                        LEFT JOIN profissional_especialidade pe ON p.idProfissional = pe.idProfissional
                        LEFT JOIN especialidades e ON pe.idEspecialidade = e.idEspecialidade
                    """)
                    where_conditions.append("e.nome = %s")
                    params.append(filtro_especialidade)

                # ADICIONADO: JOINs e WHERE para convênio e comodidades
                if tem_convenio or tem_estacionamento or tem_acessibilidade:
                    if tem_convenio:
                        joins.append("LEFT JOIN profissional_convenios pc ON p.idProfissional = pc.idProfissional")
                        where_conditions.append("pc.idConvenio IS NOT NULL")
                    if tem_estacionamento or tem_acessibilidade:
                        joins.append("""
                            LEFT JOIN profissional_comodidades pcom ON p.idProfissional = pcom.idProfissional
                            LEFT JOIN comodidades com ON pcom.idComodidade = com.idComodidade
                        """)
                        if tem_estacionamento:
                            where_conditions.append("com.nome LIKE %s")
                            params.append('%Estacionamento%')
                        if tem_acessibilidade:
                            where_conditions.append("com.nome LIKE %s")
                            params.append('%Acessibilidade%')

                # ADICIONADO: WHERE conditions para busca textual e localização
                # Usando subqueries para evitar dependência de JOINs condicionais
                if busca_textual:
                    where_conditions.append("""(p.nome LIKE %s OR
                        (SELECT e.nome FROM especialidades e
                         JOIN profissional_especialidade pe ON e.idEspecialidade = pe.idEspecialidade
                         WHERE pe.idProfissional = p.idProfissional LIMIT 1) LIKE %s OR
                        EXISTS (SELECT 1 FROM profissional_comodidades pc
                               JOIN comodidades c ON pc.idComodidade = c.idComodidade
                               WHERE pc.idProfissional = p.idProfissional AND c.nome LIKE %s))""")
                    params.extend([f'%{busca_textual}%', f'%{busca_textual}%', f'%{busca_textual}%'])
                if busca_localizacao:
                    where_conditions.append("(p.cidade LIKE %s OR p.bairro LIKE %s)")
                    params.extend([f'%{busca_localizacao}%', f'%{busca_localizacao}%'])

                sql += ' '.join(joins)
                sql += " WHERE " + " AND ".join(where_conditions)
                sql += " GROUP BY m.idModalidade, m.nome ORDER BY m.idModalidade"
                cursor.execute(sql, params)
            else:
                sql = """
                    SELECT m.nome as modalidade, COUNT(DISTINCT cm.idClinica) as count
                    FROM modalidades m
                    LEFT JOIN clinica_modalidades cm ON m.idModalidade = cm.idModalidade
                    LEFT JOIN clinica c ON cm.idClinica = c.idClinica
                """
                params = []
                joins = []
                where_conditions = ["cm.idClinica IS NOT NULL"]

                if filtro_especialidade and filtro_especialidade != "Todas as especialidades":
                    where_conditions.append("c.tipo = %s")
                    params.append(filtro_especialidade)

                # ADICIONADO: JOINs e WHERE para convênio e comodidades
                if tem_convenio or tem_estacionamento or tem_acessibilidade:
                    if tem_convenio:
                        joins.append("LEFT JOIN clinica_convenios cc ON c.idClinica = cc.idClinica")
                        where_conditions.append("cc.idConvenio IS NOT NULL")
                    if tem_estacionamento or tem_acessibilidade:
                        joins.append("""
                            LEFT JOIN clinica_comodidades ccom ON c.idClinica = ccom.idClinica
                            LEFT JOIN comodidades com ON ccom.idComodidade = com.idComodidade
                        """)
                        if tem_estacionamento:
                            where_conditions.append("com.nome LIKE %s")
                            params.append('%Estacionamento%')
                        if tem_acessibilidade:
                            where_conditions.append("com.nome LIKE %s")
                            params.append('%Acessibilidade%')

                # ADICIONADO: WHERE conditions para busca textual e localização
                # Usando subqueries para evitar dependência de JOINs condicionais
                if busca_textual:
                    where_conditions.append("""(c.nomeExibicao LIKE %s OR c.tipo LIKE %s OR
                        EXISTS (SELECT 1 FROM clinica_comodidades cc
                               JOIN comodidades com ON cc.idComodidade = com.idComodidade
                               WHERE cc.idClinica = c.idClinica AND com.nome LIKE %s))""")
                    params.extend([f'%{busca_textual}%', f'%{busca_textual}%', f'%{busca_textual}%'])
                if busca_localizacao:
                    where_conditions.append("(c.cidade LIKE %s OR c.bairro LIKE %s)")
                    params.extend([f'%{busca_localizacao}%', f'%{busca_localizacao}%'])

                sql += ' '.join(joins)
                sql += " WHERE " + " AND ".join(where_conditions)
                sql += " GROUP BY m.idModalidade, m.nome ORDER BY m.idModalidade"
                cursor.execute(sql, params)

            counts = cursor.fetchall()
            cursor.close()
            conn.close()
            result = {row['modalidade']: row['count'] for row in counts}
            return jsonify({'success': True, 'counts': result})
        except Exception as e:
            print(f"Erro counts com filtros: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Listar Profissionais e Clínicas (Vitrine) COM FILTROS REAIS
    # -------------------------------
    @app.route('/api/vitrine', methods=['GET'])
    def api_vitrine():
        try:
            # ADICIONADO: Todos os filtros - preço, especialidade, modalidades, convênio, comodidades, localização e busca textual
            tipo = request.args.get('tipo', 'profissional')
            filtro_especialidade = request.args.get('especialidade')
            filtro_modalidades = request.args.getlist('modalidades[]')
            filtro_valor_max = request.args.get('valor_max')
            filtro_ordenar = request.args.get('ordenar', 'relevancia')
            busca_textual = request.args.get('busca', '').strip()
            busca_localizacao = request.args.get('localizacao', '').strip()
            tem_convenio = request.args.get('aceita_convenio') == 'true'
            tem_estacionamento = request.args.get('estacionamento') == 'true'
            tem_acessibilidade = request.args.get('acessibilidade') == 'true'

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)
            resultados = []

            if tipo == 'profissional':
                # ADICIONADO: Filtros por especialidade e modalidades
                sql = """
                    SELECT DISTINCT p.idProfissional as id, p.nome, p.cidade, p.bairro, p.foto_perfil,
                           (SELECT e.nome FROM especialidades e
                            JOIN profissional_especialidade pe ON e.idEspecialidade = pe.idEspecialidade
                            WHERE pe.idProfissional = p.idProfissional LIMIT 1) as especialidade_principal
                    FROM profissional p
                """
                params = []
                joins = []
                where_conditions = []

                # ADICIONADO: JOIN e WHERE para especialidade
                if filtro_especialidade and filtro_especialidade != "Todas as especialidades":
                    joins.append("""
                        JOIN profissional_especialidade pe_filter ON p.idProfissional = pe_filter.idProfissional
                        JOIN especialidades e_filter ON pe_filter.idEspecialidade = e_filter.idEspecialidade
                    """)
                    where_conditions.append("e_filter.nome = %s")
                    params.append(filtro_especialidade)

                # ADICIONADO: JOIN e WHERE para modalidades
                if filtro_modalidades:
                    joins.append("""
                        JOIN profissional_modalidades pm_filter ON p.idProfissional = pm_filter.idProfissional
                        JOIN modalidades m_filter ON pm_filter.idModalidade = m_filter.idModalidade
                    """)
                    placeholders = ','.join(['%s'] * len(filtro_modalidades))
                    where_conditions.append(f"m_filter.nome IN ({placeholders})")
                    params.extend(filtro_modalidades)

                # ADICIONADO: JOINs para convênio e comodidades (sempre, para WHERE opcional)
                if tem_convenio or tem_estacionamento or tem_acessibilidade:
                    if tem_convenio:
                        joins.append("LEFT JOIN profissional_convenios pc_filter ON p.idProfissional = pc_filter.idProfissional")
                    if tem_estacionamento or tem_acessibilidade:
                        joins.append("""
                            LEFT JOIN profissional_comodidades pcom_filter ON p.idProfissional = pcom_filter.idProfissional
                            LEFT JOIN comodidades com_filter ON pcom_filter.idComodidade = com_filter.idComodidade
                        """)

                # ADICIONADO: WHERE conditions para convênio e comodidades
                if tem_convenio:
                    where_conditions.append("pc_filter.idConvenio IS NOT NULL")
                if tem_estacionamento:
                    where_conditions.append("com_filter.nome LIKE %s")
                    params.append('%Estacionamento%')
                if tem_acessibilidade:
                    where_conditions.append("com_filter.nome LIKE %s")
                    params.append('%Acessibilidade%')

                # ADICIONADO: WHERE conditions para busca textual e localização
                # Usando subqueries para evitar dependência de JOINs condicionais
                if busca_textual:
                    where_conditions.append("""(p.nome LIKE %s OR
                        (SELECT e.nome FROM especialidades e
                         JOIN profissional_especialidade pe ON e.idEspecialidade = pe.idEspecialidade
                         WHERE pe.idProfissional = p.idProfissional LIMIT 1) LIKE %s OR
                        EXISTS (SELECT 1 FROM profissional_comodidades pc
                               JOIN comodidades c ON pc.idComodidade = c.idComodidade
                               WHERE pc.idProfissional = p.idProfissional AND c.nome LIKE %s))""")
                    params.extend([f'%{busca_textual}%', f'%{busca_textual}%', f'%{busca_textual}%'])
                if busca_localizacao:
                    where_conditions.append("(p.cidade LIKE %s OR p.bairro LIKE %s)")
                    params.extend([f'%{busca_localizacao}%', f'%{busca_localizacao}%'])

                # Adicionar JOINs
                sql += ' '.join(joins)

                # Adicionar WHERE
                if where_conditions:
                    sql += " WHERE " + " AND ".join(where_conditions)
                else:
                    sql += " WHERE 1=1"

                sql += " LIMIT 50"
                cursor.execute(sql, params)
                rows = cursor.fetchall()

                # ADICIONADO: Calcular preços médios
                sql_preco = "SELECT idProfissional, preco FROM servicos_profissional WHERE preco IS NOT NULL AND preco != ''"
                cursor.execute(sql_preco)
                preco_rows = cursor.fetchall()
                preco_dict = defaultdict(list)
                for pr in preco_rows:
                    try:
                        clean_price = pr['preco'].replace('R$', '').replace(',', '.').strip()
                        price_val = float(clean_price)
                        preco_dict[pr['idProfissional']].append(price_val)
                    except (ValueError, AttributeError):
                        pass
                precos = {pid: round(sum(prices) / len(prices), 2) for pid, prices in preco_dict.items()}

                # ADICIONADO: Filtrar por preço máximo
                if filtro_valor_max:
                    try:
                        max_val = float(filtro_valor_max)
                        rows = [r for r in rows if precos.get(r['id']) is None or precos.get(r['id']) <= max_val]
                    except ValueError:
                        pass

                # ADICIONADO: Ordenação por preço
                for row in rows:
                    row['preco_medio'] = precos.get(row['id'])

                if filtro_ordenar == 'preco_menor':
                    rows.sort(key=lambda x: x['preco_medio'] if x['preco_medio'] is not None else 999999)
                elif filtro_ordenar == 'preco_maior':
                    rows.sort(key=lambda x: x['preco_medio'] if x['preco_medio'] is not None else 0, reverse=True)
                elif filtro_ordenar == 'avaliacao':
                    rows.sort(key=lambda x: (x['media_avaliacao'] if x['media_avaliacao'] is not None else 0, x['preco_medio'] if x['preco_medio'] is not None else 999999), reverse=True)
                else:
                    # Mantém ordenação por ID para outros casos
                    pass

                # ADICIONADO: Buscar modalidades para cada profissional
                modalidade_dict = {}
                if rows:
                    ids = [str(row['id']) for row in rows]
                    ids_str = ','.join(ids)
                    sql_mods = f"""
                        SELECT pm.idProfissional, m.nome
                        FROM profissional_modalidades pm
                        JOIN modalidades m ON pm.idModalidade = m.idModalidade
                        WHERE pm.idProfissional IN ({ids_str})
                    """
                    cursor.execute(sql_mods)
                    mod_rows = cursor.fetchall()
                    for mod in mod_rows:
                        if mod['idProfissional'] not in modalidade_dict:
                            modalidade_dict[mod['idProfissional']] = []
                        modalidade_dict[mod['idProfissional']].append(mod['nome'])

                for row in rows:
                    resultados.append({
                        'id': row['id'],
                        'tipo': 'profissional',
                        'nome': row['nome'],
                        'especialidade': row['especialidade_principal'] or 'Geral',
                        'localizacao': f"{row['bairro'] or ''}, {row['cidade'] or ''}".strip(', '),
                        'preco': row['preco_medio'],
                        'modalidades': modalidade_dict.get(row['id'], []),
                        'foto': row['foto_perfil']
                    })
            else:
                # ADICIONADO: Filtros por especialidade (tipo) e modalidades para clínicas
                sql = """
                    SELECT DISTINCT c.idClinica as id, c.nomeExibicao as nome, c.cidade, c.bairro, c.foto_perfil, c.tipo
                    FROM clinica c
                """
                params = []
                joins = []
                where_conditions = []

                # ADICIONADO: WHERE para tipo (especialidade das clínicas)
                if filtro_especialidade and filtro_especialidade != "Todas as especialidades":
                    where_conditions.append("c.tipo = %s")
                    params.append(filtro_especialidade)

                # ADICIONADO: JOIN e WHERE para modalidades
                if filtro_modalidades:
                    joins.append("""
                        JOIN clinica_modalidades cm_filter ON c.idClinica = cm_filter.idClinica
                        JOIN modalidades m_filter ON cm_filter.idModalidade = m_filter.idModalidade
                    """)
                    placeholders = ','.join(['%s'] * len(filtro_modalidades))
                    where_conditions.append(f"m_filter.nome IN ({placeholders})")
                    params.extend(filtro_modalidades)

                # ADICIONADO: JOINs para convênio e comodidades (sempre, para WHERE opcional)
                if tem_convenio or tem_estacionamento or tem_acessibilidade:
                    if tem_convenio:
                        joins.append("LEFT JOIN clinica_convenios cc_filter ON c.idClinica = cc_filter.idClinica")
                    if tem_estacionamento or tem_acessibilidade:
                        joins.append("""
                            LEFT JOIN clinica_comodidades ccom_filter ON c.idClinica = ccom_filter.idClinica
                            LEFT JOIN comodidades com_filter ON ccom_filter.idComodidade = com_filter.idComodidade
                        """)

                # ADICIONADO: WHERE conditions para convênio e comodidades
                if tem_convenio:
                    where_conditions.append("cc_filter.idConvenio IS NOT NULL")
                if tem_estacionamento:
                    where_conditions.append("com_filter.nome LIKE %s")
                    params.append('%Estacionamento%')
                if tem_acessibilidade:
                    where_conditions.append("com_filter.nome LIKE %s")
                    params.append('%Acessibilidade%')

                # ADICIONADO: WHERE conditions para busca textual e localização
                # Usando subqueries para evitar dependência de JOINs condicionais
                if busca_textual:
                    where_conditions.append("""(c.nomeExibicao LIKE %s OR c.tipo LIKE %s OR
                        EXISTS (SELECT 1 FROM clinica_comodidades cc
                               JOIN comodidades com ON cc.idComodidade = com.idComodidade
                               WHERE cc.idClinica = c.idClinica AND com.nome LIKE %s))""")
                    params.extend([f'%{busca_textual}%', f'%{busca_textual}%', f'%{busca_textual}%'])
                if busca_localizacao:
                    where_conditions.append("(c.cidade LIKE %s OR c.bairro LIKE %s)")
                    params.extend([f'%{busca_localizacao}%', f'%{busca_localizacao}%'])

                # Adicionar JOINs
                sql += ' '.join(joins)

                # Adicionar WHERE
                if where_conditions:
                    sql += " WHERE " + " AND ".join(where_conditions)
                else:
                    sql += " WHERE 1=1"

                sql += " LIMIT 50"
                cursor.execute(sql, params)
                rows = cursor.fetchall()

                # ADICIONADO: Calcular preços médios para clínicas
                sql_preco = "SELECT idClinica, preco FROM procedimentos WHERE preco IS NOT NULL AND preco != ''"
                cursor.execute(sql_preco)
                preco_rows = cursor.fetchall()
                preco_dict = defaultdict(list)
                for pr in preco_rows:
                    try:
                        clean_price = pr['preco'].replace('R$', '').replace(',', '.').strip()
                        price_val = float(clean_price)
                        preco_dict[pr['idClinica']].append(price_val)
                    except (ValueError, AttributeError):
                        pass
                precos = {pid: round(sum(prices) / len(prices), 2) for pid, prices in preco_dict.items()}

                # ADICIONADO: Filtrar por preço máximo
                if filtro_valor_max:
                    try:
                        max_val = float(filtro_valor_max)
                        rows = [r for r in rows if precos.get(r['id']) is None or precos.get(r['id']) <= max_val]
                    except ValueError:
                        pass

                # ADICIONADO: Ordenação por preço
                for row in rows:
                    row['preco_medio'] = precos.get(row['id'])

                if filtro_ordenar == 'preco_menor':
                    rows.sort(key=lambda x: x['preco_medio'] if x['preco_medio'] is not None else 999999)
                elif filtro_ordenar == 'preco_maior':
                    rows.sort(key=lambda x: x['preco_medio'] if x['preco_medio'] is not None else 0, reverse=True)
                elif filtro_ordenar == 'avaliacao':
                    rows.sort(key=lambda x: (x['media_avaliacao'] if x['media_avaliacao'] is not None else 0, x['preco_medio'] if x['preco_medio'] is not None else 999999), reverse=True)
                else:
                    # Mantém ordenação por ID para outros casos
                    pass

                # ADICIONADO: Buscar modalidades para cada clínica
                modalidade_dict = {}
                if rows:
                    ids = [str(row['id']) for row in rows]
                    ids_str = ','.join(ids)
                    sql_mods = f"""
                        SELECT cm.idClinica, m.nome
                        FROM clinica_modalidades cm
                        JOIN modalidades m ON cm.idModalidade = m.idModalidade
                        WHERE cm.idClinica IN ({ids_str})
                    """
                    cursor.execute(sql_mods)
                    mod_rows = cursor.fetchall()
                    for mod in mod_rows:
                        if mod['idClinica'] not in modalidade_dict:
                            modalidade_dict[mod['idClinica']] = []
                        modalidade_dict[mod['idClinica']].append(mod['nome'])

                for row in rows:
                    resultados.append({
                        'id': row['id'],
                        'tipo': 'clinica',
                        'nome': row['nome'] or row['nomeExibicao'],
                        'especialidade': row['tipo'] or 'Clínica',
                        'localizacao': f"{row['bairro'] or ''}, {row['cidade'] or ''}".strip(', '),
                        'preco': row['preco_medio'],
                        'modalidades': modalidade_dict.get(row['id'], []),
                        'foto': row['foto_perfil']
                    })

            cursor.close()
            conn.close()
            return jsonify({'success': True, 'resultados': resultados})
        except Exception as e:
            print(f"ERRO VITRINE COM PREÇO: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Buscar Profissional (Perfil Público)
    # -------------------------------
    # Mantenha o alinhamento igual às outras funções do seu arquivo (ex: api_agendamentos_usuario)

    @app.route('/api/profissional/<int:prof_id>', methods=['GET'])
    def api_get_profissional(prof_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 1. BUSCAR DADOS DO PROFISSIONAL (Sem misturar serviços aqui)
            cursor.execute("""
                SELECT p.*,
                    GROUP_CONCAT(DISTINCT c.nome SEPARATOR ', ') as convenios
                FROM profissional p
                LEFT JOIN profissional_convenios pc ON p.idProfissional = pc.idProfissional
                LEFT JOIN convenios c ON pc.idConvenio = c.idConvenio
                WHERE p.idProfissional = %s
                GROUP BY p.idProfissional
            """, (prof_id,))
            prof = cursor.fetchone()

            if not prof:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Profissional não encontrado'}), 404

            # 2. BUSCAR SERVIÇOS SEPARADAMENTE (CORREÇÃO DO BOTÃO VAZIO)
            # Trazemos explicitamente o idServico, nome e preco
            cursor.execute("""
                SELECT idServico, nome, preco 
                FROM servicos_profissional 
                WHERE idProfissional = %s
            """, (prof_id,))
            servicos_do_banco = cursor.fetchall()
            
            # Atribui a lista correta com os IDs
            prof['servicos_list'] = servicos_do_banco

            # 3. DADOS DE AVALIAÇÃO
            cursor.execute("""
                SELECT AVG(av.nota) as media_avaliacao, COUNT(av.idAvaliacao) as total_avaliacoes
                FROM agendamento a
                LEFT JOIN avaliacoes av ON a.idAgendamento = av.idAgendamento
                WHERE a.idProfissional = %s AND av.idAvaliacao IS NOT NULL
            """, (prof_id,))
            avaliacao_result = cursor.fetchone()
            
            media_avaliacao = round(float(avaliacao_result['media_avaliacao']), 1) if avaliacao_result['media_avaliacao'] else 0.0
            total_avaliacoes = avaliacao_result['total_avaliacoes'] or 0

            # 4. AVALIAÇÕES RECENTES
            cursor.execute("""
                SELECT av.nota, av.comentario, av.data_avaliacao, u.nome as nome_usuario
                FROM avaliacoes av
                JOIN agendamento a ON av.idAgendamento = a.idAgendamento
                JOIN usuario u ON a.idUsuario = u.idUsuario
                WHERE a.idProfissional = %s
                ORDER BY av.data_avaliacao DESC
                LIMIT 3
            """, (prof_id,))
            avaliacoes = cursor.fetchall()

            cursor.close()
            conn.close()

            # Montagem final dos dados
            prof['convenios_list'] = prof['convenios'].split(', ') if prof['convenios'] else []
            prof['media_avaliacao'] = media_avaliacao
            prof['total_avaliacoes'] = total_avaliacoes
            prof['avaliacoes_recentes'] = avaliacoes

            return jsonify({'success': True, 'profissional': prof})

        except Exception as e:
            print(f"Erro ao buscar profissional: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Buscar Clínica (Perfil Público)
    # -------------------------------
    @app.route('/api/clinica/<int:clinica_id>', methods=['GET'])
    def api_get_clinica(clinica_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.*,
                    GROUP_CONCAT(DISTINCT p.nome, ' - ', p.preco SEPARATOR '||') as procedimentos,
                    GROUP_CONCAT(DISTINCT e.nome, ' - ', e.especialidade SEPARATOR '||') as equipe,
                    GROUP_CONCAT(DISTINCT conv.nome SEPARATOR ', ') as convenios
                FROM clinica c
                LEFT JOIN procedimentos p ON c.idClinica = p.idClinica
                LEFT JOIN equipe_medica e ON c.idClinica = e.idClinica
                LEFT JOIN clinica_convenios cc ON c.idClinica = cc.idClinica
                LEFT JOIN convenios conv ON cc.idConvenio = conv.idConvenio
                WHERE c.idClinica = %s
                GROUP BY c.idClinica
            """, (clinica_id,))
            clinica = cursor.fetchone()
            if not clinica:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Clínica não encontrada'}), 404
            # Buscar média de avaliações e algumas avaliações
            cursor.execute("""
                SELECT AVG(av.nota) as media_avaliacao, COUNT(av.idAvaliacao) as total_avaliacoes
                FROM agendamento a
                LEFT JOIN avaliacoes av ON a.idAgendamento = av.idAgendamento
                WHERE a.idClinica = %s AND av.idAvaliacao IS NOT NULL
            """, (clinica_id,))
            avaliacao_result = cursor.fetchone()
            media_avaliacao = round(float(avaliacao_result['media_avaliacao']), 1) if avaliacao_result['media_avaliacao'] else 0.0
            total_avaliacoes = avaliacao_result['total_avaliacoes'] or 0
            # Buscar algumas avaliações recentes
            cursor.execute("""
                SELECT av.nota, av.comentario, av.data_avaliacao, u.nome as nome_usuario
                FROM avaliacoes av
                JOIN agendamento a ON av.idAgendamento = a.idAgendamento
                JOIN usuario u ON a.idUsuario = u.idUsuario
                WHERE a.idClinica = %s
                ORDER BY av.data_avaliacao DESC
                LIMIT 3
            """, (clinica_id,))
            avaliacoes = cursor.fetchall()
            cursor.close()
            conn.close()
            # Processar procedimentos
            procedimentos = []
            if clinica['procedimentos']:
                for p in clinica['procedimentos'].split('||'):
                    if ' - ' in p:
                        nome, preco = p.split(' - ', 1)
                        procedimentos.append({'nome': nome, 'preco': preco})
            # Processar equipe
            equipe = []
            if clinica['equipe']:
                for e in clinica['equipe'].split('||'):
                    if ' - ' in e:
                        nome, especialidade = e.split(' - ', 1)
                        equipe.append({'nome': nome, 'especialidade': especialidade})
            clinica['procedimentos_list'] = procedimentos
            clinica['equipe_list'] = equipe
            clinica['convenios_list'] = clinica['convenios'].split(', ') if clinica['convenios'] else []
            clinica['media_avaliacao'] = media_avaliacao
            clinica['total_avaliacoes'] = total_avaliacoes
            clinica['avaliacoes_recentes'] = avaliacoes
            return jsonify({'success': True, 'clinica': clinica})
        except Exception as e:
            print(f"Erro ao buscar clínica: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # ROTAS: Clínica
    # -------------------------------
    @app.route('/clinica/editar')
    def clinica_editar():
        return render_template('clinicaEditar.html')
    @app.route('/clinica/perfil/<int:clinica_id>')
    def clinica_perfil(clinica_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # ---------------------------------------------------------
            # 1. BUSCAR DADOS PRINCIPAIS DA CLÍNICA
            # ---------------------------------------------------------
            cursor.execute("""
                SELECT c.*,
                    GROUP_CONCAT(DISTINCT p.nome, ' - ', p.preco SEPARATOR '||') as procedimentos,
                    GROUP_CONCAT(DISTINCT e.nome, ' - ', e.especialidade SEPARATOR '||') as equipe,
                    GROUP_CONCAT(DISTINCT conv.nome SEPARATOR ', ') as convenios
                FROM clinica c
                LEFT JOIN procedimentos p ON c.idClinica = p.idClinica
                LEFT JOIN equipe_medica e ON c.idClinica = e.idClinica
                LEFT JOIN clinica_convenios cc ON c.idClinica = cc.idClinica
                LEFT JOIN convenios conv ON cc.idConvenio = conv.idConvenio
                WHERE c.idClinica = %s
                GROUP BY c.idClinica
            """, (clinica_id,))
            
            clinica = cursor.fetchone()
            
            if not clinica:
                cursor.close()
                conn.close()
                return "Clínica não encontrada", 404
            
            # ---------------------------------------------------------
            # 2. BUSCAR ESTATÍSTICAS DE AVALIAÇÃO
            # ---------------------------------------------------------
            cursor.execute("""
                SELECT AVG(av.nota) as media_avaliacao, COUNT(av.idAvaliacao) as total_avaliacoes
                FROM agendamento a
                LEFT JOIN avaliacoes av ON a.idAgendamento = av.idAgendamento
                WHERE a.idClinica = %s AND av.idAvaliacao IS NOT NULL
            """, (clinica_id,))
            avaliacao_result = cursor.fetchone()
            
            if avaliacao_result:
                clinica['media_avaliacao'] = round(float(avaliacao_result['media_avaliacao']), 1) if avaliacao_result['media_avaliacao'] else 0.0
                clinica['total_avaliacoes'] = avaliacao_result['total_avaliacoes'] or 0
            else:
                clinica['media_avaliacao'] = 0.0
                clinica['total_avaliacoes'] = 0
            # ---------------------------------------------------------
            # 3. BUSCAR AVALIAÇÕES RECENTES (DETALHADAS)
            # ---------------------------------------------------------
            cursor.execute("""
                SELECT av.nota, av.comentario, av.data_avaliacao, u.nome as nome_usuario
                FROM avaliacoes av
                JOIN agendamento a ON av.idAgendamento = a.idAgendamento
                JOIN usuario u ON a.idUsuario = u.idUsuario
                WHERE a.idClinica = %s
                ORDER BY av.data_avaliacao DESC
                LIMIT 3
            """, (clinica_id,))
            clinica['avaliacoes_recentes'] = cursor.fetchall()
            # Agora podemos fechar a conexão
            cursor.close()
            conn.close()
            
            # ---------------------------------------------------------
            # 4. PROCESSAR STRINGS EM LISTAS (Python)
            # ---------------------------------------------------------
            
            # Processar Procedimentos
            procedimentos = []
            if clinica['procedimentos']:
                for p in clinica['procedimentos'].split('||'):
                    if ' - ' in p:
                        partes = p.split(' - ', 1)
                        if len(partes) == 2:
                            procedimentos.append({'nome': partes[0], 'preco': partes[1]})
            
            # Processar Equipe
            equipe = []
            if clinica['equipe']:
                for e in clinica['equipe'].split('||'):
                    if ' - ' in e:
                        partes = e.split(' - ', 1)
                        if len(partes) == 2:
                            equipe.append({'nome': partes[0], 'especialidade': partes[1]})
            
            clinica['procedimentos_list'] = procedimentos
            clinica['equipe_list'] = equipe
            clinica['convenios_list'] = clinica['convenios'].split(', ') if clinica['convenios'] else []
            
            return render_template('clinicaPerfil.html', clinica=clinica)
        except Exception as e:
            # Em caso de erro, imprime no terminal e mostra na tela para facilitar o diagnóstico
            print(f"ERRO CRÍTICO NA ROTA DA CLÍNICA: {e}")
            import traceback
            traceback.print_exc()
            return f"<h1>Erro Interno:</h1><p>{str(e)}</p>", 500
    # -------------------------------
    # ROTAS: Profissional
    # -------------------------------
    @app.route('/profissional/editar')
    def doutor_editar():
        if 'profissional_id' not in session:
            return redirect(url_for('cadastro_usuario'))
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Buscar dados do profissional
            cursor.execute("SELECT * FROM profissional WHERE idProfissional = %s", (session['profissional_id'],))
            profissional = cursor.fetchone()
            if not profissional:
                cursor.close()
                conn.close()
                return redirect(url_for('cadastro_usuario'))
            # Buscar especialidades
            cursor.execute("""
                SELECT especialidade FROM profissional_especialidade
                WHERE idProfissional = %s
            """, (profissional['idProfissional'],))
            especialidades = [row['especialidade'] for row in cursor.fetchall()]
            # Buscar serviços
            cursor.execute("""
                SELECT * FROM servicos_profissional
                WHERE idProfissional = %s ORDER BY idServico
            """, (profissional['idProfissional'],))
            servicos = cursor.fetchall()
            # Buscar convênios
            cursor.execute("""
                SELECT c.nome FROM profissional_convenios pc
                JOIN convenios c ON pc.idConvenio = c.idConvenio
                WHERE pc.idProfissional = %s
            """, (profissional['idProfissional'],))
            convenios = [row['nome'] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return render_template('doutorEditar.html',
                                 profissional=profissional,
                                 especialidades=especialidades,
                                 servicos=servicos,
                                 convenios=convenios)
        except Exception as e:
            print(f"Erro ao carregar edição do profissional: {e}")
            return redirect(url_for('cadastro_usuario'))
    # ==============================================================================
    # VERSÃO ANTIGA (COM A LÓGICA DO GROUP_CONCAT QUE CAUSAVA O ERRO)
    # ==============================================================================
    @app.route('/profissional/perfil/<int:prof_id>')
    def perfil_publico_profissional(prof_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 1. TENTA BUSCAR TUDO DE UMA VEZ (AQUI ERA O PROBLEMA)
            # O GROUP_CONCAT cria uma string gigante tipo: "Consulta - 200.00||Retorno - 100.00"
            # O ID do serviço se perde nessa mistura se não for incluído explicitamente na string.
            cursor.execute("""
                SELECT p.*,
                    GROUP_CONCAT(DISTINCT CONCAT(s.nome, ' - R$ ', s.preco) SEPARATOR '||') as servicos_concat,
                    GROUP_CONCAT(DISTINCT c.nome SEPARATOR ', ') as convenios
                FROM profissional p
                LEFT JOIN servicos_profissional s ON p.idProfissional = s.idProfissional
                LEFT JOIN profissional_convenios pc ON p.idProfissional = pc.idProfissional
                LEFT JOIN convenios c ON pc.idConvenio = c.idConvenio
                WHERE p.idProfissional = %s
                GROUP BY p.idProfissional
            """, (prof_id,))
            
            prof = cursor.fetchone()

            if not prof:
                cursor.close()
                conn.close()
                return "Profissional não encontrado", 404

            # --- A "GAMBIARRA" DO PYTHON ---
            # Aqui o código tentava "desmontar" a string que o banco montou.
            # Como o idServico não estava na string acima, ele nunca chegava no HTML.
            
            prof['servicos_list'] = []
            if prof['servicos_concat']:
                for s in prof['servicos_concat'].split('||'):
                    # s agora é algo como "Consulta - R$ 200.00"
                    if ' - R$ ' in s:
                        partes = s.split(' - R$ ')
                        # Cria um dicionário SÓ com nome e preço. O ID ficava de fora!
                        prof['servicos_list'].append({
                            'nome': partes[0], 
                            'preco': partes[1]
                            # Faltava o 'idServico' aqui!
                        })

            # ... (Restante do código de avaliações igual) ...
            
            # Tratamento de convênios
            prof['convenios_list'] = prof['convenios'].split(', ') if prof['convenios'] else []

            # 3. DADOS DE AVALIAÇÃO
            cursor.execute("""
                SELECT AVG(av.nota) as media_avaliacao, COUNT(av.idAvaliacao) as total_avaliacoes
                FROM agendamento a
                LEFT JOIN avaliacoes av ON a.idAgendamento = av.idAgendamento
                WHERE a.idProfissional = %s AND av.idAvaliacao IS NOT NULL
            """, (prof_id,))
            avaliacao_result = cursor.fetchone()

            media_avaliacao = round(float(avaliacao_result['media_avaliacao']), 1) if avaliacao_result['media_avaliacao'] else 0.0
            total_avaliacoes = avaliacao_result['total_avaliacoes'] or 0

            # 4. AVALIAÇÕES RECENTES
            cursor.execute("""
                SELECT av.nota, av.comentario, av.data_avaliacao, u.nome as nome_usuario
                FROM avaliacoes av
                JOIN agendamento a ON av.idAgendamento = a.idAgendamento
                JOIN usuario u ON a.idUsuario = u.idUsuario
                WHERE a.idProfissional = %s
                ORDER BY av.data_avaliacao DESC
                LIMIT 3
            """, (prof_id,))
            avaliacoes = cursor.fetchall()

            cursor.close()
            conn.close()

            # Montagem final dos dados
            prof['media_avaliacao'] = media_avaliacao
            prof['total_avaliacoes'] = total_avaliacoes
            prof['avaliacoes_recentes'] = avaliacoes

            return render_template('doutorPerfil.html',
                                profissional=prof,
                                usuario_logado='user_id' in session)

        except Exception as e:
            return f"Erro: {e}", 500
    # -------------------------------
    # ROTA: Perfil usuário
    # -------------------------------
    @app.route('/perfil')
    def perfil_usuario():
        if 'user_id' not in session:
            return redirect(url_for('cadastro_usuario'))
        usuario = get_usuario_logado()
        if not usuario:
            session.clear()
            return redirect(url_for('cadastro_usuario'))
        return render_template('perfil.html', usuario=usuario)
    # -------------------------------
    # API: Buscar mais avaliações
    # -------------------------------
    @app.route('/api/avaliacoes/<tipo>/<int:id_entidade>', methods=['GET'])
    def api_get_avaliacoes(tipo, id_entidade):
        try:
            offset = int(request.args.get('offset', 0))
            limit = int(request.args.get('limit', 6))
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            if tipo == 'clinica':
                cursor.execute("""
                    SELECT av.nota, av.comentario, av.data_avaliacao, u.nome as nome_usuario
                    FROM avaliacoes av
                    JOIN agendamento a ON av.idAgendamento = a.idAgendamento
                    JOIN usuario u ON a.idUsuario = u.idUsuario
                    WHERE a.idClinica = %s
                    ORDER BY av.data_avaliacao DESC
                    LIMIT %s OFFSET %s
                """, (id_entidade, limit, offset))
            elif tipo == 'profissional':
                cursor.execute("""
                    SELECT av.nota, av.comentario, av.data_avaliacao, u.nome as nome_usuario
                    FROM avaliacoes av
                    JOIN agendamento a ON av.idAgendamento = a.idAgendamento
                    JOIN usuario u ON a.idUsuario = u.idUsuario
                    WHERE a.idProfissional = %s
                    ORDER BY av.data_avaliacao DESC
                    LIMIT %s OFFSET %s
                """, (id_entidade, limit, offset))
            else:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Tipo inválido'}), 400
            avaliacoes = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'avaliacoes': avaliacoes})
        except Exception as e:
            print(f"Erro ao buscar avaliações: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # API: Enviar avaliação
    # -------------------------------
    @app.route('/api/avaliacao/submit', methods=['POST'])
    def api_submit_avaliacao():
        try:
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Não autenticado'}), 401
            dados = request.get_json()
            tipo = dados.get('tipo')  # 'clinica' or 'profissional'
            id_entidade = dados.get('id_entidade')
            nota = dados.get('nota')
            comentario = dados.get('comentario', '').strip()
            if not all([tipo, id_entidade, nota]):
                return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
            if tipo not in ['clinica', 'profissional']:
                return jsonify({'success': False, 'message': 'Tipo inválido'}), 400
            if not (1 <= int(nota) <= 5):
                return jsonify({'success': False, 'message': 'Nota deve ser entre 1 e 5'}), 400
            user_id = session['user_id']
            conn = get_db_connection()
            cursor = conn.cursor()
            # Check if user has completed appointment with this entity
            if tipo == 'clinica':
                cursor.execute("""
                    SELECT idAgendamento FROM agendamento
                    WHERE idUsuario = %s AND idClinica = %s AND status = 'concluido'
                    LIMIT 1
                """, (user_id, id_entidade))
            else:
                cursor.execute("""
                    SELECT idAgendamento FROM agendamento
                    WHERE idUsuario = %s AND idProfissional = %s AND status = 'concluido'
                    LIMIT 1
                """, (user_id, id_entidade))
            agendamento = cursor.fetchone()
            if not agendamento:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Você precisa ter um agendamento concluído para avaliar'}), 400
            id_agendamento = agendamento[0]
            # Insert evaluation
            cursor.execute("""
                INSERT INTO avaliacoes (idAgendamento, nota, comentario, data_avaliacao)
                VALUES (%s, %s, %s, NOW())
            """, (id_agendamento, nota, comentario))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Avaliação enviada com sucesso!'})
        except Exception as e:
            print(f"Erro ao enviar avaliação: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'}), 500
    # -------------------------------
    # CONTEXT PROCESSOR
    # -------------------------------
    @app.context_processor
    def inject_user():
        u = None
        tipo_usuario = None
        foto_perfil = None
        
        # Prioridade: profissional > clinica > usuario
        # Isso permite que se o usuário tiver conta em múltiplas tabelas,
        # a prioridade seja para profissional/clínica
        if 'profissional_id' in session:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT idProfissional, nome, foto_perfil FROM profissional WHERE idProfissional = %s", (session['profissional_id'],))
                prof = cursor.fetchone()
                cursor.close()
                conn.close()
                if prof:
                    u = prof
                    tipo_usuario = 'profissional'
                    foto_perfil = prof.get('foto_perfil')
            except Exception as e:
                print(f"Erro ao buscar profissional no context processor: {e}")
        elif 'clinica_id' in session:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT idClinica, nomeExibicao as nome, foto_perfil FROM clinica WHERE idClinica = %s", (session['clinica_id'],))
                clinica = cursor.fetchone()
                cursor.close()
                conn.close()
                if clinica:
                    u = clinica
                    tipo_usuario = 'clinica'
                    foto_perfil = clinica.get('foto_perfil')
            except Exception as e:
                print(f"Erro ao buscar clínica no context processor: {e}")
        elif 'user_id' in session:
            u = get_usuario_logado()
            tipo_usuario = 'usuario'
            foto_perfil = u.get('foto_perfil') if u else None
        
        return dict(usuario_logado=u, tipo_usuario=tipo_usuario, foto_perfil_usuario=foto_perfil)