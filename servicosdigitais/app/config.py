import os

class ConfigPadrao:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-insegura")

    SQLALCHEMY_DATABASE_URI = "sqlite:///bdservicosdigitais.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Proteções / Flags
    VALIDAR_CPF = False
    VALIDAR_CNPJ = False
    VALIDAR_PRESTADOR = False

    # E-mail
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "suporteservicosdigitais@gmail.com"
    MAIL_PASSWORD = "SUA_SENHA_APP"
    MAIL_DEFAULT_SENDER = (
        "Suporte Serviços Digitais",
        "suporteservicosdigitais@gmail.com"
    )
