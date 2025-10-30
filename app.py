# app.py
import os
from flask import Flask, render_template, redirect, request, flash, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ---------------------------------------------
# 🧭 ETAPA 1 — Configuração do Flask e Banco
# ---------------------------------------------

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-dev-secreta')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estoque.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------------------------
# 🗃️ ETAPA 2 — Modelos do Banco de Dados
# ---------------------------------------------

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'data_criacao': self.data_criacao.isoformat()
        }

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    minimo = db.Column(db.Integer, default=5)
    preco = db.Column(db.Float, default=0.0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'quantidade': self.quantidade,
            'minimo': self.minimo,
            'preco': self.preco,
            'status_estoque': 'CRÍTICO' if self.quantidade <= 0 else 'BAIXO' if self.quantidade <= self.minimo else 'NORMAL'
        }

# ---------------------------------------------
# 🔐 ETAPA 6 — Sistema de Autenticação e Segurança
# ---------------------------------------------

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login_init'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_nome' not in session or session['user_nome'] != 'Administrador':
            flash('Acesso restrito para administradores.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------
# 📦 ETAPA 3 — Funções de Controle de Estoque
# ---------------------------------------------

def verificar_estoque():
    """Verifica produtos com estoque baixo ou crítico"""
    try:
        produtos = Produto.query.all()
        alertas = {
            'critico': [p for p in produtos if p.quantidade <= 0],
            'baixo': [p for p in produtos if 0 < p.quantidade <= p.minimo],
            'total_alertas': 0
        }
        alertas['total_alertas'] = len(alertas['critico']) + len(alertas['baixo'])
        return alertas
    except Exception as e:
        logger.error(f"Erro ao verificar estoque: {e}")
        return {'critico': [], 'baixo': [], 'total_alertas': 0}

def atualizar_quantidade_produto(produto_id, nova_quantidade):
    """Atualiza quantidade do produto com validação"""
    try:
        produto = Produto.query.get(produto_id)
        if produto:
            produto.quantidade = max(0, nova_quantidade)  # Não permite quantidade negativa
            produto.data_atualizacao = datetime.utcnow()
            db.session.commit()
            return True, "Quantidade atualizada com sucesso!"
        return False, "Produto não encontrado."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar produto {produto_id}: {e}")
        return False, "Erro ao atualizar produto."

# ---------------------------------------------
# 🌐 Rotas Principais
# ---------------------------------------------

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/login', methods=['GET'])
def login_init():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        
        # Validações
        if not nome or not senha:
            flash('Preencha todos os campos.', 'danger')
            return render_template('registro.html')
        
        if len(senha) < 4:
            flash('A senha deve ter pelo menos 4 caracteres.', 'danger')
            return render_template('registro.html')
        
        if senha != confirmar_senha:
            flash('Senhas não coincidem.', 'danger')
            return render_template('registro.html')
        
        if Usuario.query.filter_by(nome=nome).first():
            flash('Nome de usuário já existe.', 'danger')
            return render_template('registro.html')
        
        # Criar novo usuário
        try:
            novo_usuario = Usuario(nome=nome)
            novo_usuario.set_senha(senha)
            
            db.session.add(novo_usuario)
            db.session.commit()
            
            flash('Registro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login_init'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro no registro: {e}")
            flash('Erro ao registrar usuário.', 'danger')
    
    return render_template('registro.html')

@app.route('/login', methods=['POST'])
def login():
    nome = request.form.get('nome', '').strip()
    senha = request.form.get('senha', '')
    
    if not nome or not senha:
        flash('Preencha todos os campos.', 'danger')
        return redirect(url_for('login_init'))
    
    # Usuário administrativo
    if nome == 'adm' and senha == '000':
        session['user_id'] = 'admin'
        session['user_nome'] = 'Administrador'
        flash('Login administrativo realizado!', 'success')
        return redirect(url_for('administrador'))
    
    # Buscar usuário no banco
    usuario = Usuario.query.filter_by(nome=nome).first()
    
    if usuario and usuario.check_senha(senha):
        session['user_id'] = usuario.id
        session['user_nome'] = usuario.nome
        flash(f'Bem-vindo, {usuario.nome}!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Credenciais inválidas.', 'danger')
        return redirect(url_for('login_init'))

@app.route('/dashboard')
@login_required
def dashboard():
    alertas_estoque = verificar_estoque()
    produtos = Produto.query.order_by(Produto.nome).all()
    
    return render_template('dashboard.html', 
                         alertas=alertas_estoque,
                         produtos=produtos)

@app.route('/administrador')
@login_required
@admin_required
def administrador():
    usuarios = Usuario.query.all()
    produtos = Produto.query.all()
    alertas_estoque = verificar_estoque()
    
    return render_template('administrador.html',
                         usuarios=usuarios,
                         produtos=produtos,
                         alertas=alertas_estoque)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('home'))

# ---------------------------------------------
# 🌐 ETAPA 5 — APIs REST
# ---------------------------------------------

@app.route('/api/produtos')
@login_required
def listar_produtos():
    try:
        produtos = Produto.query.all()
        return jsonify([p.to_dict() for p in produtos])
    except Exception as e:
        logger.error(f"Erro na API produtos: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/produtos/<int:produto_id>')
@login_required
def obter_produto(produto_id):
    try:
        produto = Produto.query.get(produto_id)
        if produto:
            return jsonify(produto.to_dict())
        return jsonify({'error': 'Produto não encontrado'}), 404
    except Exception as e:
        logger.error(f"Erro ao obter produto {produto_id}: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/produtos', methods=['POST'])
@login_required
@admin_required
def criar_produto():
    try:
        data = request.get_json()
        if not data or not data.get('nome'):
            return jsonify({'error': 'Nome do produto é obrigatório'}), 400
        
        novo_produto = Produto(
            nome=data['nome'],
            descricao=data.get('descricao', ''),
            quantidade=data.get('quantidade', 0),
            minimo=data.get('minimo', 5),
            preco=data.get('preco', 0.0)
        )
        
        db.session.add(novo_produto)
        db.session.commit()
        
        return jsonify(novo_produto.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar produto: {e}")
        return jsonify({'error': 'Erro ao criar produto'}), 500

@app.route('/api/estoque/alertas')
@login_required
def obter_alertas_estoque():
    try:
        alertas = verificar_estoque()
        return jsonify(alertas)
    except Exception as e:
        logger.error(f"Erro ao obter alertas: {e}")
        return jsonify({'error': 'Erro interno'}), 500

# ---------------------------------------------
# 🛠️ Rotas de Gerenciamento (Admin)
# ---------------------------------------------

@app.route('/admin/produto/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_produto():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        quantidade = request.form.get('quantidade', 0, type=int)
        minimo = request.form.get('minimo', 5, type=int)
        
        if not nome:
            flash('Nome do produto é obrigatório.', 'danger')
            return render_template('novo_produto.html')
        
        try:
            produto = Produto(
                nome=nome,
                descricao=request.form.get('descricao', ''),
                quantidade=quantidade,
                minimo=minimo,
                preco=request.form.get('preco', 0.0, type=float)
            )
            
            db.session.add(produto)
            db.session.commit()
            
            flash('Produto cadastrado com sucesso!', 'success'),app,
            return redirect(url_for('administrador'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar produto: {e}")
            flash('Erro ao cadastrar produto.', 'danger')
    
    return render_template('novo_produto.html')

# ---------------------------------------------
# Inicialização do Banco
# ---------------------------------------------

first_request_done = False

@app.before_request
def create_tables():
    global first_request_done
    if not first_request_done:
        try:
            db.create_all()
            logger.info("Tabelas criadas/verificadas com sucesso")
            first_request_done = True
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
    
if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=os.environ.get('FLASK_DEBUG', True))