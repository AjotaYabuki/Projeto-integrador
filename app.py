from flask import Flask, render_template, redirect, request, flash, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import random

# --------------------------
# 🔧 Configuração Base
# --------------------------
load_dotenv()

# Força o Flask a reconhecer a pasta 'static' corretamente
import os
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")

# --------------------------
# 🗄️ Banco de Dados
# --------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------------
# 👥 Modelos
# --------------------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    cargo = db.Column(db.String(50), default="Usuário")

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    telefone = db.Column(db.String(20))

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    marca = db.Column(db.String(120), nullable=True) # NOVO CAMPO
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    validade = db.Column(db.Date, nullable=True)
    limite_minimo = db.Column(db.Integer, default=5)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    quantidade = db.Column(db.Integer, nullable=False)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow)
    cliente = db.relationship("Cliente")
    produto = db.relationship("Produto")

# --------------------------
# 🌐 Rotas
# --------------------------
@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/login')
def login_init():
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        cargo = request.form.get('cargo', 'Usuário')

        if not nome or not senha:
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for('registro'))

        usuario_existente = Usuario.query.filter_by(nome=nome).first()
        if usuario_existente:
            flash("Usuário já existe.", "warning")
            return redirect(url_for('registro'))

        novo_usuario = Usuario(nome=nome, senha=senha, cargo=cargo)
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Usuário registrado com sucesso! Faça login.", "success")
        return redirect(url_for('login_init'))

    return render_template('registro.html')

@app.route('/login', methods=['POST'])
def login():
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    if nome == 'adm' and senha == '000':
        session['usuario_nome'] = 'Administrador'
        session['usuario_cargo'] = 'Admin'
        return redirect(url_for('dashboard'))

    usuario = Usuario.query.filter_by(nome=nome).first()
    if usuario and usuario.senha == senha:
        session['usuario_nome'] = usuario.nome
        session['usuario_cargo'] = usuario.cargo
        return redirect(url_for('dashboard'))
    else:
        flash('Usuário ou senha incorretos.', 'danger')
        return redirect(url_for('login_init'))

# --------------------------
# 🚪 LOGOUT - Rota Funcional
# --------------------------
@app.route('/logout')
def logout():
    """
    Rota de logout que limpa a sessão do usuário
    e redireciona para a página de login
    """
    session.clear()
    flash("Você saiu da conta com sucesso.", "info")
    return redirect(url_for('login_init'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_nome' not in session:
        flash("Faça login para acessar o painel.", "warning")
        return redirect(url_for('login_init'))

    produtos = Produto.query.all()
    vendas = Venda.query.all()
    clientes = Cliente.query.all()

    alertas = []
    for produto in produtos:
        if produto.estoque <= produto.limite_minimo:
            alertas.append(f"⚠️ Estoque baixo de {produto.nome}")
        if produto.validade and produto.validade <= datetime.now().date() + timedelta(days=5):
            alertas.append(f"⏰ {produto.nome} perto da validade ({produto.validade})")

    usuario_nome = session.get('usuario_nome', 'Usuário')
    usuario_cargo = session.get('usuario_cargo', 'Padrão')

    return render_template('dashboard.html',
                           produtos=produtos,
                           clientes=clientes,
                           vendas=vendas,
                           alertas=alertas,
                           usuario_nome=usuario_nome,
                           usuario_cargo=usuario_cargo)

# --------------------------
# 📊 API para gráficos
# --------------------------
@app.route('/api/graficos')
def api_graficos():
    # Dados simulados para o gráfico de vendas mensais (últimos 6 meses)
    vendas_meses = ["Jun", "Jul", "Ago", "Set", "Out", "Nov"]
    vendas_valores = [random.randint(7000, 12000) for _ in range(6)]
    
    # Dados simulados para o gráfico de crescimento de clientes
    clientes_novos = [random.randint(5, 15) for _ in range(6)]

    # Dados simulados para o gráfico de vendas por canal
    vendas_canais = {"Online": 45, "Loja Física": 35, "Marketplace": 20}

    return jsonify({
        "vendas_mensais": {
            "labels": vendas_meses,
            "data": vendas_valores
        },
        "clientes_crescimento": {
            "labels": vendas_meses,
            "data": clientes_novos
        },
        "vendas_canais": {
            "labels": list(vendas_canais.keys()),
            "data": list(vendas_canais.values())
        },
        "clientes_count": Cliente.query.count(),
        "produtos_count": Produto.query.count(),
        "vendas_total": sum(v.quantidade * v.produto.preco for v in Venda.query.all() if v.produto)
    })

# --------------------------
# ➕ CRUD BÁSICO
# --------------------------
@app.route('/add_cliente', methods=['POST'])
def add_cliente():
    if 'usuario_nome' not in session:
        flash("Faça login para adicionar clientes.", "warning")
        return redirect(url_for('login_init'))
        
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    
    # Verifica se o cliente já existe
    if Cliente.query.filter_by(email=email).first():
        flash("Cliente com este e-mail já existe.", "danger")
        return redirect(url_for('dashboard'))
        
    novo = Cliente(nome=nome, email=email, telefone=telefone)
    db.session.add(novo)
    db.session.commit()
    flash("Cliente adicionado com sucesso!", "success")
    return redirect(url_for('dashboard'))

@app.route('/add_produto', methods=['POST'])
def add_produto():
    if 'usuario_nome' not in session:
        flash("Faça login para adicionar produtos.", "warning")
        return redirect(url_for('login_init'))
        
    try:
        nome = request.form['nome']
        marca = request.form.get('marca')
        preco = float(request.form['preco'])
        estoque = int(request.form['estoque'])
        validade = request.form.get('validade')
        validade_data = datetime.strptime(validade, "%Y-%m-%d").date() if validade else None
        
        # Verifica se o produto já existe
        if Produto.query.filter_by(nome=nome).first():
            flash("Produto com este nome já existe.", "danger")
            return redirect(url_for('dashboard'))
            
        novo = Produto(nome=nome, marca=marca, preco=preco, estoque=estoque, validade=validade_data)
        db.session.add(novo)
        db.session.commit()
        flash("Produto adicionado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao adicionar produto: {e}", "danger")
        
    return redirect(url_for('dashboard'))

@app.route('/add_venda', methods=['POST'])
def add_venda():
    if 'usuario_nome' not in session:
        flash("Faça login para registrar vendas.", "warning")
        return redirect(url_for('login_init'))
        
    cliente_id = int(request.form['cliente_id'])
    produto_id = int(request.form['produto_id'])
    quantidade = int(request.form['quantidade'])
    
    produto = Produto.query.get(produto_id)
    if not produto or produto.estoque < quantidade:
        flash("Estoque insuficiente ou produto não encontrado.", "danger")
        return redirect(url_for('dashboard'))
        
    venda = Venda(cliente_id=cliente_id, produto_id=produto_id, quantidade=quantidade)
    db.session.add(venda)

    produto.estoque -= quantidade
    db.session.commit()
    flash("Venda registrada com sucesso!", "success")
    return redirect(url_for('dashboard'))

# --------------------------
# 🩺 Ping
# --------------------------
@app.route('/ping')
def ping():
    return {"status": "ok", "mensagem": "API funcionando corretamente!"}

# --------------------------
# 🚀 Inicialização
# --------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Gera dados fictícios só uma vez
        if not Cliente.query.first():
            for i in range(5):
                db.session.add(Cliente(
                    nome=f"Cliente {i+1}",
                    email=f"cliente{i+1}@teste.com",
                    telefone=f"(11) 9000{i+1}-0000"
                ))
            for i in range(5):
                db.session.add(Produto(
                    nome=f"Produto {i+1}",
                    marca=f"Marca {i+1}",
                    preco=random.uniform(10, 100),
                    estoque=random.randint(2, 20),
                    validade=datetime.now().date() + timedelta(days=random.randint(2, 30))
                ))
            db.session.commit()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)