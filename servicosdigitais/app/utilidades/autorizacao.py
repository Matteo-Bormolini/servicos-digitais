# ========================
# Utilidades - Decorators de Permissões
# ========================
from flask_login import  current_user
from flask import (
     flash, redirect, url_for, session
    )
from functools import wraps


# =========================
# BLOQUEAR TIPOS ESPECÍFICOS
# =========================
def bloquear_tipos(*tipos_bloqueados, redirect_endpoint='home'):
    """
    Bloqueia acesso para os tipos listados em tipos_bloqueados.
    - Se NÃO autenticado: redireciona para 'login' com flash.
    - Admin sempre tem acesso.
    - Se o tipo do usuário estiver em tipos_bloqueados:
        - flash e redirect para redirect_endpoint (padrão: 'home').
    """
    def decorator(funcao):
        @wraps(funcao)
        def wrapper(*args, **kwargs):

            # 1) Não logado → bloquear e mandar para login
            if not current_user.is_authenticated:
                flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
                return redirect(url_for('autenticacao.login'))

            usuario = current_user  # agora garantido

            # 2) Admin sempre entra
            if getattr(usuario, "is_admin", False):
                return funcao(*args, **kwargs)

            # 3) Bloqueio por tipo
            if getattr(usuario, "tipo", None) in tipos_bloqueados:
                flash("Acesso negado: sua conta não tem permissão para esta página.", "danger")
                return redirect(url_for(redirect_endpoint))

            # 4) Liberado
            return funcao(*args, **kwargs)

        return wrapper
    return decorator

# ==================
# SOMENTE ADMIN
# ==================
def somente_admin(funcao):
    """
    Permite acesso apenas para administradores.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('autenticacao.login'))

        if not getattr(current_user, "is_admin", False):
            flash("Acesso restrito: apenas administradores podem acessar.", "danger")
            return redirect(url_for('servicos.home'))

        return funcao(*args, **kwargs)
    return wrapper


# ==================
# SOMENTE PRESTADOR
# ==================
def somente_prestador(funcao):
    """
    Permite acesso apenas para usuários do tipo 'prestador' ou admin.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('autenticacao.login'))

        # Admin sempre tem acesso
        if getattr(current_user, "is_admin", False):
            return funcao(*args, **kwargs)

        if getattr(current_user, "tipo", None) != "prestador":
            flash("Acesso negado: esta página é apenas para prestadores.", "danger")
            return redirect(url_for('servicos.home'))

        return funcao(*args, **kwargs)
    return wrapper


# ==================
# SOMENTE CPF
# ==================
def somente_cpf(funcao):
    """
    Permite acesso apenas para usuários do tipo 'cpf' ou admin.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('autenticacao.login'))

        if getattr(current_user, "is_admin", False):
            return funcao(*args, **kwargs)

        if getattr(current_user, "tipo", None) != "cpf":
            flash("Acesso negado: esta área é apenas para usuários CPF.", "danger")
            return redirect(url_for('servicos.home'))

        return funcao(*args, **kwargs)
    return wrapper


# ==================
# SOMENTE CNPJ
# ==================
def somente_cnpj(funcao):
    """
    Permite acesso apenas para usuários do tipo 'cnpj' ou admin.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('autenticacao.login'))

        if getattr(current_user, "is_admin", False):
            return funcao(*args, **kwargs)

        if getattr(current_user, "tipo", None) != "cnpj":
            flash("Acesso negado: esta área é apenas para usuários CNPJ.", "danger")
            return redirect(url_for('servicos.home'))

        return funcao(*args, **kwargs)
    return wrapper


# logout forçado, expiração, erro crítico.
def limpar_sessao():
    session.clear()
