from .autenticacao import autenticacao_bp
from .cadastros import cadastros_bp
from .perfil import perfil_bp
from .servicos import servicos_bp
from .suporte import suporte_bp
from .admin import admin_bp

__all__ = [
    "autenticacao_bp",
    "cadastros_bp",
    "perfil_bp",
    "servicos_bp",
    "suporte_bp",
    "admin_bp",
]
