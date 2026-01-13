import os

# Caminho absoluto da raiz do projeto (onde está o main.py)
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

# Caminho absoluto da pasta instance
INSTANCIA_DIR = os.path.join(BASE_DIR, "instance")

# Garante que a pasta exista (CRÍTICO para SQLite)
os.makedirs(INSTANCIA_DIR, exist_ok=True)


class ConfigPadrao:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-insegura")

    # ===========================
    # Banco de dados SQLite
    # ===========================
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" +
        os.path.join(INSTANCIA_DIR, "banco_de_dados.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ===========================
    # Proteções / Flags
    # ===========================
    VALIDAR_CPF = False
    VALIDAR_CNPJ = False
    VALIDAR_PRESTADOR = False

    # ===========================
    # E-mail
    # ===========================
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "suporteservicosdigitais@gmail.com"
    MAIL_PASSWORD = "SUA_SENHA_APP"
    MAIL_DEFAULT_SENDER = (
        "Suporte Serviços Digitais",
        "suporteservicosdigitais@gmail.com"
    )
