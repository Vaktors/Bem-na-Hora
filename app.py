from flask import Flask, render_template

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
# Pasta onde as fotos de perfil e uploads serão salvos
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# --- ROTAS PRINCIPAIS ---

@app.route('/')
def index():
    # Antigo 'lp', agora é a página inicial
    return render_template('index.html')

@app.route('/vitrine')
def vitrine():
    # Página de busca/listagem (Vitrine)
    return render_template('vitrine.html')

@app.route('/agenda')
def agenda():
    # Página de Agendamentos
    return render_template('agenda.html')

# --- ROTAS DE AUTENTICAÇÃO E CADASTRO ---

@app.route('/login')
def login():
    # Se você tiver um html separado de login, coloque aqui.
    # Se for um modal na home, essa rota pode não ser necessária agora.
    # Vou assumir que você vai criar ou usar um login.html simples
    return render_template('login.html') 

@app.route('/cadastro/usuario')
def cadastro_usuario():
    # Cadastro de pacientes (pasta 'cadastro')
    return render_template('cadastro.html')

@app.route('/cadastro/parceiro')
def cadastro_parceiro():
    # Cadastro de clínicas ou médicos (pasta 'parceiroCadastro')
    return render_template('parceiroCadastro.html')

@app.route('/recuperar-senha')
def redefinir_senha():
    # Pasta 'redefinirSenha'
    return render_template('redefinirSenha.html')

@app.route('/confirma-email')
def confirma_email():
    # Pasta 'confirmaEmail'
    return render_template('confirmaEmail.html')

# --- ROTAS DA CLÍNICA ---

@app.route('/clinica/editar')
def clinica_editar():
    # Edição do perfil da clínica (pasta 'clinicaEditar')
    return render_template('clinicaEditar.html')

@app.route('/clinica/perfil')
def clinica_perfil():
    # Visualização pública da clínica (pasta 'clinicaPerfil')
    return render_template('clinicaPerfil.html')

# --- ROTAS DO PROFISSIONAL (DOUTOR) ---

@app.route('/profissional/editar')
def doutor_editar():
    # Edição do perfil do médico (pasta 'doutorEditar')
    return render_template('doutorEditar.html')

@app.route('/profissional/perfil')
def doutor_perfil():
    # Visualização pública do médico (pasta 'doutorPerfil')
    return render_template('doutorPerfil.html')

# --- ROTAS DO USUÁRIO (PACIENTE) ---

@app.route('/perfil')
def perfil_usuario():
    # Perfil do paciente (pasta 'perfil')
    return render_template('perfil.html')

# --- INICIALIZAÇÃO ---
if __name__ == '__main__':
    # O debug=True faz o site recarregar sozinho quando você salva o código
    app.run(debug=True)