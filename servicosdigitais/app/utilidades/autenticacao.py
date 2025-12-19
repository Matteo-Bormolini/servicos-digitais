# ========================
# Utilidades - login, sessão, bloqueio
# ========================
from servicosdigitais.app.extensoes import bancodedados
from servicosdigitais.app.extensoes import login_manager
from servicosdigitais.app.models import (
    Usuario,
    ClienteCPF,
    ClienteCNPJ,
    PrestadorServico
)
from sqlalchemy.exc import SQLAlchemyError
from flask_login import  logout_user
from flask import (
    current_app, session, flash, redirect, url_for
    )
from datetime import datetime, timezone, timedelta
from functools import wraps

INATIVIDADE_MINUTOS = 30
_TEMPO_INATIVIDADE_MIN = globals().get('INATIVIDADE_MINUTOS', 30)

MAX_TENTATIVAS = 5
TEMPO_BLOQUEIO_MIN = 15
RESET_TENTATIVAS_MIN = 30

def get_caminho_log():
    from flask import current_app
    return current_app.config.get('CAMINHO_LOG', 'instance/erros.log')

def atualiza_atividade():
    """Grava timestamp ISO na sessão quando há atividade do usuário."""
    session['ultima_atividade'] = datetime.now(timezone.utc).isoformat()


def verifica_inatividade(func):
    """
    Decorator: derruba o usuário se estiver inativo por mais que _TEMPO_INATIVIDADE_MIN.
    Ao derrubar faz logout_user() e redireciona para 'login' com flash.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        ultima = session.get('ultima_atividade')
        agora = datetime.now(timezone.utc)
        if ultima:
            try:
                ts = datetime.fromisoformat(ultima)
            except Exception:
                ts = agora
        else:
            ts = agora
        if (agora - ts) > timedelta(minutes=_TEMPO_INATIVIDADE_MIN):
            # expira sessão
            logout_user()
            session.pop('ultima_atividade', None)
            flash(f'Logout automático por inatividade ({_TEMPO_INATIVIDADE_MIN} minutos).', 'alert-warning')
            return redirect(url_for('autenticacao.login'))  # ajuste se sua rota de login tiver outro nome
        # se ainda válido, atualiza o timestamp e segue
        session['ultima_atividade'] = agora.isoformat()
        return func(*args, **kwargs)
    return wrapper


def verificar_bloqueio(usuario):
    """
    Retorna True se o login deve ser bloqueado agora.
    Caso contrário, retorna False.
    Também já mostra o flash de aviso.
    """
    agora = datetime.now(timezone.utc)

    # Se bloqueado até um tempo no futuro
    if usuario.bloqueado_ate and usuario.bloqueado_ate > agora:
        minutos = int((usuario.bloqueado_ate - agora).total_seconds() // 60) + 1
        flash(f"Conta bloqueada por muitas tentativas. Tente novamente em {minutos} minuto(s).", "alert-danger")
        return True

    return False


#Se acertar
def registrar_sucesso(usuario):
    """Reseta tentativas ao logar com sucesso."""
    try:
        usuario.tentativas_falhas = 0
        usuario.ultima_falha = None
        usuario.bloqueado_ate = None
        bancodedados.session.commit()
    except SQLAlchemyError:
        bancodedados.session.rollback()


# Se falhar
def registrar_falha(usuario):
    """Incrementa falha e bloqueia se passar do limite."""
    agora = datetime.now(timezone.utc)

    try:
        # Se última falha for antiga → pode resetar
        if usuario.ultima_falha:
            if (agora - usuario.ultima_falha) > timedelta(minutes=RESET_TENTATIVAS_MIN):
                usuario.tentativas_falhas = 0

        usuario.tentativas_falhas = (usuario.tentativas_falhas or 0) + 1
        usuario.ultima_falha = agora

        # Se atingiu limite
        if usuario.tentativas_falhas >= MAX_TENTATIVAS:
            usuario.bloqueado_ate = agora + timedelta(minutes=TEMPO_BLOQUEIO_MIN)
            bancodedados.session.commit()
            flash(f"Conta bloqueada por {TEMPO_BLOQUEIO_MIN} minutos.", "alert-danger")
        else:
            restam = MAX_TENTATIVAS - usuario.tentativas_falhas
            bancodedados.session.commit()
            flash(f"Senha incorreta. Restam {restam} tentativa(s).", "alert-danger")

    except SQLAlchemyError:
        bancodedados.session.rollback()
        flash("Erro ao registrar tentativa. Tente novamente.", "alert-danger")


@login_manager.user_loader
def carregar_usuario(data):
    if not data:
        return None

    try:
        tipo, usuario_id = data.split(":")
        usuario_id = int(usuario_id)
    except ValueError:
        return None

    mapa = {
        "usuario": Usuario,
        "cpf": ClienteCPF,
        "cnpj": ClienteCNPJ,
        "prestador": PrestadorServico,
    }

    modelo = mapa.get(tipo)
    if not modelo:
        return None

    return modelo.query.get(usuario_id)