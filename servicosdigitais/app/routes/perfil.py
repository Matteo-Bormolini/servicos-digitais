# ======================================================
# Routes - Perfil do Usuário
# ======================================================
'''  Responsável por:
    - Exibir perfil público
    - Exibir perfil do usuário logado
    - Alternar ocultação de dados sensíveis
    - Editar dados do perfil
'''


from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request, current_app
)
from flask_login import login_required, current_user

from servicosdigitais.app import bancodedados, bcrypt
from servicosdigitais.app.models.usuario import Usuario
from servicosdigitais.app.forms.perfil_forms import (
    FormEditarCPF, FormEditarCNPJ, FormEditarPrestador
)
from servicosdigitais.app.utilidades.upload_imagem import trocar_imagem_usuario
from servicosdigitais.app.utilidades.validadores import email_existe


# Blueprint do perfil
perfil_bp = Blueprint(
    "perfil",
    __name__,
    template_folder="templates"
)

# ======================================================
# ALTERNAR OCULTAÇÃO DE DADOS
# ======================================================
@perfil_bp.route('/perfil/<int:user_id>/toggle_ocultar', methods=['POST'])
@login_required
def toggle_ocultar(user_id):
    ''' Permite ao dono do perfil ativar/desativar
    a ocultação de dados sensíveis
    '''
    # Busca usuário alvo
    usuario = Usuario.query.get_or_404(user_id)

    # Apenas o dono pode alterar
    if current_user.id != usuario.id:
        flash("Ação não permitida.", "danger")
        return redirect(
            url_for(
                'perfil.perfil_publico',
                user_id=user_id
            )
        )

    # Inverte estado da ocultação
    usuario.ocultar_dados = not usuario.ocultar_dados

    try:
        bancodedados.session.commit()
        flash("Preferência atualizada.", "success")
    except Exception:
        bancodedados.session.rollback()
        current_app.logger.exception("Erro ao alternar ocultar dados")
        flash("Erro ao salvar alteração.", "danger")

    return redirect(
        url_for(
            'perfil.perfil_publico',
            user_id=user_id
        )
    )


# ======================================================
# PERFIL DO USUÁRIO LOGADO
# ======================================================
@perfil_bp.route('/perfil')
@login_required
def meu_perfil():
    """
    Redireciona sempre para o perfil público
    do próprio usuário logado.
    """
    return redirect(
        url_for(
            'perfil.perfil_publico',
            user_id=current_user.id
        )
    )


# ======================================================
# PERFIL PÚBLICO
# ======================================================
@perfil_bp.route('/perfil/<int:user_id>')
def perfil_publico(user_id):
    """
    Exibe o perfil público de um usuário.
    Aplica regras de visibilidade para dados sensíveis.
    """

    # Busca usuário ou retorna 404
    usuario = Usuario.query.get_or_404(user_id)

    # Contexto de quem visualiza
    eh_logado = current_user.is_authenticated
    eh_dono = eh_logado and current_user.id == usuario.id
    eh_admin = eh_logado and getattr(current_user, 'is_admin', False)

    # Regra clara de blur
    if eh_dono or eh_admin:
        usar_blur = False
    else:
        usar_blur = usuario.ocultar_dados

    # Nome completo (evita None)
    nome_completo = " ".join(
        parte for parte in [usuario.nome, usuario.sobrenome] if parte
    )

    # ============================
    # FOTO DE PERFIL
    # ============================
    foto_url = url_for(
        'static',
        filename=f'fotos_perfil/{usuario.foto_perfil or "default.png"}'
    )

    # ============================
    # DOCUMENTO (CPF / CNPJ)
    # ============================
    documento = None

    if usuario.tipo == 'cpf' and hasattr(usuario, 'cliente_cpf'):
        documento = usuario.cliente_cpf.cpf

    elif usuario.tipo == 'cnpj' and hasattr(usuario, 'cliente_cnpj'):
        documento = usuario.cliente_cnpj.cnpj

    documento_display = (
        'Informação protegida'
        if usar_blur else (documento or '—')
    )


    # ============================
    # EMAIL E TELEFONE
    # ============================
    email_display = (
        'Informação protegida'
        if usar_blur else usuario.email
    )

    telefone_display = (
        'Informação protegida'
        if usar_blur else (usuario.telefone or '—')
    )

    return render_template(
        'perfil.html',
        usuario=usuario,
        nome_completo=nome_completo,
        email_display=email_display,
        telefone_display=telefone_display,
        documento_display=documento_display,
        foto_url=foto_url,
        usar_blur=usar_blur,
        eh_dono=eh_dono,
        eh_admin=eh_admin
    )


# ======================================================
# EDITAR PERFIL
# ======================================================
@perfil_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """
    Permite ao usuário editar seus dados pessoais,
    trocar senha e alterar foto de perfil.
    """

    # Define formulário conforme o tipo de usuário
    tipo_usuario = current_user.tipo

    if tipo_usuario == 'cpf':
        form = FormEditarCPF()
    elif tipo_usuario == 'cnpj':
        form = FormEditarCNPJ()
    else:
        form = FormEditarPrestador()

    # Preenchimento inicial
    if request.method == 'GET':
        form.email.data = current_user.email

        if hasattr(form, 'telefone'):
            form.telefone.data = current_user.telefone

    # Processamento
    if form.validate_on_submit():

        # ---------- EMAIL ----------
        if form.email.data != current_user.email:
            if email_existe(
                form.email.data,
                exclude_user_id=current_user.id
            ):
                flash("E-mail já em uso.", "warning")
                return render_template(
                    'editar_perfil.html',
                    form=form
                )
            current_user.email = form.email.data

        # ---------- TELEFONE ----------
        if hasattr(form, 'telefone'):
            current_user.telefone = form.telefone.data

        # ---------- SENHA ----------
        if form.senha_nova.data:
            if not bcrypt.check_password_hash(
                current_user.senha_hash,
                form.senha_atual.data
            ):
                flash("Senha atual incorreta.", "danger")
                return render_template(
                    'editar_perfil.html',
                    form=form
                )

            current_user.senha_hash = bcrypt.generate_password_hash(
                form.senha_nova.data
            ).decode('utf-8')

        # ---------- FOTO ----------
        if form.foto_perfil.data:
            trocar_imagem_usuario(
                current_user,
                form.foto_perfil.data
            )

        # ---------- SALVAR ----------
        try:
            bancodedados.session.commit()
            flash("Perfil atualizado.", "success")
            return redirect(
                url_for('perfil.meu_perfil')
            )
        except Exception:
            bancodedados.session.rollback()
            current_app.logger.exception("Erro ao salvar perfil")
            flash("Erro ao salvar alterações.", "danger")

    return render_template(
        'editar_perfil.html',
        form=form
    )