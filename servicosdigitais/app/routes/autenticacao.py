# ========================
# Routes - Login / Logout e Sessão
# ========================

'''
Conteúdo deste arquivo:
- Rota de login
- Rota de logout
'''

from flask import (
    render_template, redirect, url_for, flash, request, Blueprint
)
from flask_login import login_required, login_user

from sqlalchemy.exc import SQLAlchemyError

from servicosdigitais.app import bcrypt

from servicosdigitais.app.models.usuario import Usuario
from servicosdigitais.app.models.clientes import ClienteCPF, ClienteCNPJ
from servicosdigitais.app.models.prestador import PrestadorServico

from servicosdigitais.app.forms.login_forms import FormLogin

from servicosdigitais.app.utilidades.normalizadores import esta_ativo
from servicosdigitais.app.utilidades.validadores import (
    parece_email, apenas_numeros, detectar_tipo_por_numeros
)
from servicosdigitais.app.utilidades.autenticacao import (
    verificar_bloqueio, registrar_sucesso, registrar_falha, logout_user
)

# ========================
# Blueprint de autenticação
# ========================

autenticacao_bp = Blueprint(
    "autenticacao",
    __name__,
    template_folder="templates",
    url_prefix="/auth"
)

# ======================================================
# LOGIN
# ======================================================
@autenticacao_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login unificado:
    - E-mail
    - CPF
    - CNPJ (cliente ou prestador)
    """

    form = FormLogin()
    usuario = None

    # ==========================
    # SUBMIT DO FORMULÁRIO
    # ==========================
    if form.validate_on_submit():

        identificador = form.email.data.strip().lower()
        senha_informada = form.senha.data

        # ==========================
        # BUSCA DO USUÁRIO
        # ==========================
        try:
            # --- LOGIN POR E-MAIL ---
            if parece_email(identificador):
                usuario = Usuario.query.filter_by(email=identificador).first()

            # --- LOGIN POR CPF / CNPJ ---
            else:
                numeros = apenas_numeros(identificador)
                tipo_documento = detectar_tipo_por_numeros(numeros)

                if tipo_documento == 'cpf':
                    usuario = ClienteCPF.query.filter_by(cpf=numeros).first()

                elif tipo_documento == 'cnpj':
                    cliente = ClienteCNPJ.query.filter_by(cnpj=numeros).first()
                    prestador = PrestadorServico.query.filter_by(cnpj=numeros).first()
                    usuario = cliente or prestador

        except SQLAlchemyError:
            flash("Erro interno ao processar o login.", "alert-danger")
            return render_template('login.html', form=form)

        # ==========================
        # USUÁRIO NÃO ENCONTRADO
        # ==========================
        if not usuario:
            flash("Login ou senha incorretos.", "alert-danger")
            return render_template('login.html', form=form)

        # ==========================
        # BLOQUEIO DE CONTA
        # ==========================
        if verificar_bloqueio(usuario):
            return render_template('login.html', form=form)

        # ==========================
        # VALIDAÇÃO DE SENHA
        # ==========================
        if not bcrypt.check_password_hash(usuario.senha_hash, senha_informada):
            registrar_falha(usuario)
            flash("Login ou senha incorretos.", "alert-danger")
            return render_template('login.html', form=form)

        # ==========================
        # CONTA ATIVA?
        # ==========================
        if hasattr(usuario, 'ativo') and not esta_ativo(usuario.ativo):
            flash(
                "Conta desativada ou pendente de ativação.",
                "alert-warning"
            )
            return redirect(url_for('servicos.home'))

        # ==========================
        # LOGIN BEM-SUCEDIDO
        # ==========================
        registrar_sucesso(usuario)

        # ==================================================
        # SENHA TEMPORÁRIA → TROCA OBRIGATÓRIA
        # ==================================================
        if hasattr(usuario, 'senha_temp') and usuario.senha_temp:
            login_user(usuario, remember=False)

            flash(
                "Por segurança, você deve alterar sua senha antes de continuar.",
                "alert-warning"
            )

            return redirect(
                url_for('perfil.alterar_senha_obrigatoria')
            )

        # ==========================
        # LOGIN NORMAL
        # ==========================
        lembrar = bool(form.lembrar_dados.data)
        login_user(usuario, remember=lembrar)

        flash("Login realizado com sucesso.", "alert-success")

        destino = request.args.get('next')
        return redirect(destino) if destino else redirect(
            url_for('servicos.home')
        )

    # ==========================
    # GET → TELA DE LOGIN
    # ==========================
    return render_template('login.html', form=form)


# ======================================================
# LOGOUT
# ======================================================
@autenticacao_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado com sucesso.", "alert-info")
    return redirect(url_for('servicos.home'))
