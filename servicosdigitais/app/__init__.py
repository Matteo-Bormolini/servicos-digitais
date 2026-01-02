from flask import Flask

from servicosdigitais.app.config import ConfigPadrao
from servicosdigitais.app.extensoes import (
    bancodedados,
    bcrypt,
    login_manager,
    csrf
)


def criar_app():
    """
    Fábrica da aplicação Flask.

    Responsável por:
    - Criar o app
    - Carregar configurações
    - Inicializar extensões
    - Registrar user_loader
    - Registrar blueprints
    """

    # ===========================
    # Criar aplicação
    # ===========================
    app = Flask(__name__)

    # ===========================
    # Configurações
    # ===========================
    app.config.from_object(ConfigPadrao)

    # ===========================
    # Inicializar extensões
    # ===========================
    bancodedados.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ===========================
    # Registrar user_loader
    # ===========================
    registrar_user_loader()

    registrar_contexto_global(app)

    # ===========================
    # Registrar blueprints
    # ===========================
    from servicosdigitais.app.routes import (
        servicos_bp, admin_bp, autenticacao_bp,
        perfil_bp, suporte_bp, cadastros_bp
        )
    app.register_blueprint(autenticacao_bp)
    app.register_blueprint(cadastros_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(servicos_bp)
    app.register_blueprint(suporte_bp)
    app.register_blueprint(admin_bp)

    return app

def registrar_contexto_global(app):
    from servicosdigitais.app.forms.autenticacao_forms import FormLogout

    @app.context_processor
    def injetar_forms_globais():
        return {
            'form_logout': FormLogout()
        }


def registrar_user_loader():
    """
    Registra o carregador de usuários do Flask-Login.
    """

    from servicosdigitais.app.models import (
        Usuario,
        ClienteCPF,
        ClienteCNPJ,
        PrestadorServico
    )

    @login_manager.user_loader
    def load_usuario(data):
        if not data:
            return None

        try:
            tipo, usuario_id = data.split(":")
            usuario_id = int(usuario_id)
        except ValueError:
            return None

        if tipo == "usuario":
            return Usuario.query.get(usuario_id)
        if tipo == "cpf":
            return ClienteCPF.query.get(usuario_id)
        if tipo == "cnpj":
            return ClienteCNPJ.query.get(usuario_id)
        if tipo == "prestador":
            return PrestadorServico.query.get(usuario_id)

        return None