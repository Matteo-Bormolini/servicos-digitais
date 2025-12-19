# ========================
# Routes - Login/ Logout e sessão
# ========================

''' O que tem dentro da página de autenticação (login/logout)
    - Rota de login
    - Rota de logout
'''

from flask import Blueprint, session
from flask_login import current_user, login_required, login_user
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_, and_

from servicosdigitais.app import bcrypt
from servicosdigitais.app.models.usuario import Usuario
from servicosdigitais.app.forms.login_forms import FormLogin
from servicosdigitais.app.utilidades.validadores import (
    parece_email, apenas_numeros, detectar_tipo_por_numeros
    )
from servicosdigitais.app.utilidades.autenticacao import (
    verificar_bloqueio, registrar_sucesso, registrar_falha, logout_user
    )
from servicosdigitais.app.utilidades.normalizadores import esta_ativo


autenticacao_bp = Blueprint(
    "autenticacao",
    __name__,
    template_folder="templates",
    url_prefix="/auth"
)

# -------------------------
# Autenticação: login / logout
# -------------------------
@autenticacao_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = FormLogin()

    # Variável inicia fora do bloco, mas só será usada se houver submit
    usuario = None

    # ==========================
    # PROCESSAMENTO DO LOGIN
    # (só entra aqui se o formulário tiver sido enviado)
    # ==========================
    if form.validate_on_submit():

        identificador = None

        # Captura campo correto (identificador / login / email)
        for nome_campo in ('identificador', 'login', 'email'):
            if hasattr(form, nome_campo):
                valor = getattr(form, nome_campo).data
                if valor:
                    identificador = valor.strip()
                    break

        if not identificador:
            flash("Informe e-mail, CPF ou CNPJ.", "alert-warning")
            return render_template('login.html', form=form)

        # ==========================
        # BUSCA DO USUÁRIO
        # ==========================
        if parece_email(identificador):
            # Login via email
            usuario = Usuario.query.filter_by(email=identificador.lower()).first()

        else:
            # Login via CPF/CNPJ (apenas dígitos)
            numeros = apenas_numeros(identificador)
            tipo_detectado = detectar_tipo_por_numeros(numeros)

            filtros = []

            if tipo_detectado:
                # Detectou CPF ou CNPJ
                if hasattr(Usuario, 'cpf') and tipo_detectado == 'cpf':
                    if hasattr(Usuario, 'tipo'):
                        filtros.append(and_(Usuario.cpf == numeros, Usuario.tipo == 'cpf'))
                    else:
                        filtros.append(Usuario.cpf == numeros)

                if hasattr(Usuario, 'cnpj') and tipo_detectado == 'cnpj':
                    if hasattr(Usuario, 'tipo'):
                        filtros.append(and_(Usuario.cnpj == numeros, Usuario.tipo == 'cnpj'))
                    else:
                        filtros.append(Usuario.cnpj == numeros)

            else:
                # Não detectou → busca nos dois
                if hasattr(Usuario, 'cpf'):
                    filtros.append(Usuario.cpf == numeros)
                if hasattr(Usuario, 'cnpj'):
                    filtros.append(Usuario.cnpj == numeros)

            # Executa consulta OR
            if filtros:
                try:
                    usuario = Usuario.query.filter(or_(*filtros)).first()
                except Exception:
                    usuario = None
            else:
                usuario = Usuario.query.filter_by(email=identificador).first()

        # ==========================
        # BLOQUEIO DE LOGIN
        # ==========================
        if usuario and verificar_bloqueio(usuario):
            return render_template('login.html', form=form)

        # ==========================
        # VALIDAÇÃO DA SENHA
        # ==========================
        if usuario and bcrypt.check_password_hash(usuario.senha_hash, form.senha.data):

            # Conta ativa?
            if hasattr(usuario, 'ativo') and not esta_ativo(usuario.ativo):
                flash("Conta desativada ou pendente de ativação.", "alert-warning")
                return redirect(url_for('servicos.home'))

            # Resetar tentativas
            registrar_sucesso(usuario)

            # "Lembrar de mim"
            lembrar = False
            if hasattr(form, 'lembrar'):
                try:
                    lembrar = bool(form.lembrar.data)
                except Exception:
                    lembrar = False
            else:
                lembrar_raw = request.form.get('lembrar', '')
                lembrar = str(lembrar_raw).lower() in ('1', 'true', 'on', 'yes')

            # Login efetivo
            login_user(usuario, remember=lembrar)
            flash("Login realizado com sucesso.", "alert-success")

            destino = request.args.get('next')
            return redirect(destino) if destino else redirect(url_for('servicos.home'))

        # ==========================
        # FALHA NO LOGIN
        # ==========================
        if usuario:
            registrar_falha(usuario)

        flash("Login ou senha incorretos.", "alert-danger")
        return render_template('login.html', form=form)

    # ==========================
    # GET → só renderiza a página limpa
    # ==========================
    return render_template('login.html', form=form)


@autenticacao_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    nome = (
        getattr(current_user, 'nome', None)
        or getattr(current_user, 'email', None)
        or 'Usuário'
    )

    logout_user()

    try:
        session.clear()
    except Exception:
        for chave in list(session.keys()):
            session.pop(chave, None)

    flash(f"{nome}, você foi desconectado com sucesso.", "alert-info")

    return redirect(url_for('servicos.home'))

# Falta: Recuperar senha
