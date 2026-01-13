from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate

# ===========================
# Banco de dados
# ===========================
bancodedados = SQLAlchemy()

# ===========================
# Criptografia de senhas
# ===========================
bcrypt = Bcrypt()

# ===========================
# Gerenciamento de login
# ===========================
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

# ===========================
# Proteção CSRF
# ===========================
csrf = CSRFProtect()

# ===========================
# Migrações de banco
# ===========================
migrate = Migrate()
