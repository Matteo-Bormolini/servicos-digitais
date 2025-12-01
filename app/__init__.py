"""
__init__.py -> Inicialização do programa
Este arquivo roda automaticamente quando a aplicação é iniciada.

Aqui são configuradas:
- Extensões instaladas
- Configurações do app e banco de dados
- Importações dos módulos de forms, models e routes
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect

# ===========================
# Instância principal do Flask
# ===========================
app = Flask(__name__)

# ===========================
# Configurações gerais
# ===========================
app.config['SECRET_KEY'] = 'a55ae4f347ea5ced4862634a56f527e9daad'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdservicosdigitais.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ===========================
# Proteção CSRF
# ===========================
csrf = CSRFProtect(app)

# ===========================
# Proteção Testes
# ===========================
app.config['VALIDAR_CPF'] = False
app.config['VALIDAR_CNPJ'] = False
app.config['VALIDAR_PRESTADOR'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'suporteservicosdigitais@gmail.com'   # sua conta
app.config['MAIL_PASSWORD'] = 'SUA_SENHA_APP_OU_SENHA' # use App Password Gmail
app.config['MAIL_DEFAULT_SENDER'] = ('Suporte Serviços Digitais', 'suporteservicosdigitais@gmail.com')

# ===========================
# Banco de dados
# ===========================
bancodedados = SQLAlchemy(app)

# ===========================
# Criptografia de senhas
# ===========================
bcrypt = Bcrypt(app)  # Apenas o site consegue descriptografar

# ===========================
# Gerenciamento de login
# ===========================
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redireciona para login caso não autenticado
login_manager.login_message_category = 'alert-info'  # Categoria de flash padrão

# ===========================
# Importações dos módulos
# ===========================
from servicosdigitais.app import forms, models
from servicosdigitais.app.routes import bp
app.register_blueprint(bp)

