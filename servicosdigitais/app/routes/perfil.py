# ======================================================
# Routes - Perfil do Usuário
# ======================================================
''' Responsável por:
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
from servicosdigitais.app.utilidades.normalizadores import obter_documento_exibicao


# ======================================================
# Blueprint do perfil
# ======================================================
perfil_bp = Blueprint(
    "perfil",
    __name__,
    template_folder="templates"
)


# ======================================================
# ALTERNAR OCULTAÇÃO DE DADOS
# ======================================================
@perfil_bp.route('/toggle-ocultar/<int:user_id>', methods=['POST'])
@login_required
def toggle_ocultar(user_id):

    if current_user.id != user_id:
        flash('Ação não permitida.', 'danger')
        return redirect(url_for('perfil.meu_perfil'))

    current_user.ocultar_dados = not current_user.ocultar_dados
    bancodedados.session.commit()

    if current_user.ocultar_dados:
        flash('Seus dados agora estão ocultos.', 'warning')
    else:
        flash('Seus dados agora estão visíveis.', 'success')

    return redirect(url_for('perfil.meu_perfil'))


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

    # ============================
    # USUÁRIO BASE
    # ============================
    usuario = Usuario.query.get_or_404(user_id)

    # ============================
    # CONTEXTO DE VISUALIZAÇÃO
    # ============================
    eh_logado = current_user.is_authenticated
    eh_dono = eh_logado and current_user.id == usuario.id
    eh_admin = eh_logado and getattr(current_user, 'is_admin', False)

    # ============================
    # REGRA GLOBAL DE BLUR
    # ============================
    usar_blur = (
        usuario.ocultar_dados
        and not eh_dono
        and not eh_admin
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
    documento_tipo, documento_raw = obter_documento_exibicao(usuario)
    if documento_raw:
        documento_display = 'Informação protegida' if usar_blur else documento_raw
    else:
        documento_display = 'Documento não disponível'
        documento_tipo = 'Documento'

    # ============================
    # EMAIL (OPCIONAL)
    # ============================
    if usuario.email:
        email_display = 'Informação protegida' if usar_blur else usuario.email
    else:
        email_display = None

    # ============================
    # TELEFONE (OPCIONAL)
    # ============================
    if usuario.telefone:
        telefone_display = 'Informação protegida' if usar_blur else usuario.telefone
    else:
        telefone_display = 'Informação protegida' if usar_blur else 'Nenhum telefone cadastrado'

    # ============================
    # FORMULÁRIO POR TIPO DE USUÁRIO
    # ============================
    tipo_usuario = usuario.tipo if eh_dono else None
    form = None

    if eh_dono:
        if tipo_usuario == 'cpf':
            form = FormEditarCPF()
        elif tipo_usuario == 'cnpj':
            form = FormEditarCNPJ()
        else:
            form = FormEditarPrestador()

        # preenchimento inicial do form
        if form:
            form.email.data = usuario.email
            if hasattr(form, 'telefone'):
                form.telefone.data = usuario.telefone
            if hasattr(form, 'nome'):
                form.nome.data = getattr(usuario, 'nome', '')
            if hasattr(form, 'sobrenome'):
                form.sobrenome.data = getattr(usuario, 'sobrenome', '')
            if hasattr(form, 'username'):
                form.username.data = getattr(usuario, 'username', '')
            if hasattr(form, 'nome_empresa'):
                form.nome_empresa.data = getattr(usuario, 'nome_empresa', '')
            if hasattr(form, 'razao_social'):
                form.razao_social.data = getattr(usuario, 'razao_social', '')
            if hasattr(form, 'descricao'):
                form.descricao.data = getattr(usuario, 'descricao', '')

    return render_template(
        'perfil.html',
        usuario=usuario,
        foto_url=foto_url,
        documento_label=documento_tipo,
        documento_display=documento_display,
        email_display=email_display,
        telefone_display=telefone_display,
        usar_blur=usar_blur,
        eh_dono=eh_dono,
        eh_admin=eh_admin,
        form=form
    )


# ======================================================
# EDITAR PERFIL
# ======================================================
@perfil_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    tipo_usuario = current_user.tipo

    if tipo_usuario == 'cpf':
        form = FormEditarCPF()
    elif tipo_usuario == 'cnpj':
        form = FormEditarCNPJ()
    else:
        form = FormEditarPrestador()

    # preenchimento inicial
    if request.method == 'GET':
        form.email.data = current_user.email
        if hasattr(form, 'telefone'):
            form.telefone.data = current_user.telefone
        if hasattr(form, 'nome'):
            form.nome.data = getattr(current_user, 'nome', '')
        if hasattr(form, 'sobrenome'):
            form.sobrenome.data = getattr(current_user, 'sobrenome', '')
        if hasattr(form, 'username'):
            form.username.data = getattr(current_user, 'username', '')
        if hasattr(form, 'nome_empresa'):
            form.nome_empresa.data = getattr(current_user, 'nome_empresa', '')
        if hasattr(form, 'razao_social'):
            form.razao_social.data = getattr(current_user, 'razao_social', '')
        if hasattr(form, 'descricao'):
            form.descricao.data = getattr(current_user, 'descricao', '')

    # processamento do formulário
    if form.validate_on_submit():
        # EMAIL
        if form.email.data != current_user.email:
            if email_existe(form.email.data, exclude_user_id=current_user.id):
                flash("E-mail já em uso.", "warning")
                return redirect(url_for('perfil.editar_perfil'))
            current_user.email = form.email.data

        # TELEFONE
        if hasattr(form, 'telefone'):
            current_user.telefone = form.telefone.data

        # SENHA
        if form.senha_nova.data:
            if not bcrypt.check_password_hash(current_user.senha_hash, form.senha_atual.data):
                flash("Senha atual incorreta.", "danger")
                return redirect(url_for('perfil.editar_perfil'))
            current_user.senha_hash = bcrypt.generate_password_hash(form.senha_nova.data).decode('utf-8')

        # FOTO
        if form.foto_perfil.data:
            trocar_imagem_usuario(current_user, form.foto_perfil.data)

        # SALVAR
        try:
            bancodedados.session.commit()
            flash("Perfil atualizado.", "success")
        except Exception:
            bancodedados.session.rollback()
            current_app.logger.exception("Erro ao salvar perfil")
            flash("Erro ao salvar alterações.", "danger")

        return redirect(url_for('perfil.meu_perfil'))

    return render_template('editarperfil.html', usuario=current_user, form=form)
