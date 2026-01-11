# ======================================================
# Routes - Perfil do Usuário
# ======================================================
''' Responsável por:
    - Exibir perfil público
    - Exibir perfil do usuário logado
    - Alternar ocultação de dados sensíveis
    - Editar dados do perfil
'''

from wtforms import PasswordField
from wtforms.validators import EqualTo, Optional, Length

from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request, current_app
)
from flask_login import login_required, current_user

from servicosdigitais.app.utilidades.upload_imagem import trocar_imagem_usuario
from servicosdigitais.app.utilidades.validadores import email_existe
from servicosdigitais.app.utilidades.normalizadores import obter_documento_exibicao
from servicosdigitais.app import bancodedados, bcrypt
from servicosdigitais.app.models.usuario import Usuario
from servicosdigitais.app.forms.perfil_forms import (
    FormEditarCPF, FormEditarCNPJ, FormEditarPrestador
)
from servicosdigitais.app.utilidades.seguranca import (
    gerar_senha_hash, verificar_senha_hash
)

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
        'perfils/perfil.html',
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
@perfil_bp.route('/perfil/editar', methods=['POST'])
@login_required
def editar_perfil():
    """
    Edita dados do perfil do usuário logado.
    Permite alterar dados básicos e senha (opcional),
    sem exigir senha atual.
    """

    tipo_usuario = current_user.tipo

    # ==========================================================
    # SELEÇÃO DO FORMULÁRIO CORRETO
    # ==========================================================
    if tipo_usuario == 'cpf':
        form = FormEditarCPF(obj=current_user)
    elif tipo_usuario == 'cnpj':
        form = FormEditarCNPJ(obj=current_user)
    elif tipo_usuario == 'prestador':
        form = FormEditarPrestador(obj=current_user)
    else:
        # Admin ou fallback
        form = FormEditarCPF(obj=current_user)

    # ==========================================================
    # VALIDAÇÃO DO FORMULÁRIO
    # ==========================================================
    if not form.validate_on_submit():
        flash("Erro ao validar o formulário.", "danger")
        return redirect(url_for('perfil.meu_perfil'))

    alterou_algo = False

    # ==========================================================
    # NOME
    # ==========================================================
    if hasattr(form, 'nome'):
        nome_novo = (form.nome.data or '').strip()
        nome_atual = (current_user.nome or '').strip()

        if nome_novo != nome_atual:
            current_user.nome = nome_novo if nome_novo else None
            alterou_algo = True

    # ==========================================================
    # SOBRENOME
    # ==========================================================
    if hasattr(form, 'sobrenome'):
        sobrenome_novo = (form.sobrenome.data or '').strip()
        sobrenome_atual = (current_user.sobrenome or '').strip()

        if sobrenome_novo != sobrenome_atual:
            current_user.sobrenome = sobrenome_novo if sobrenome_novo else None
            alterou_algo = True

    # ==========================================================
    # EMAIL
    # ==========================================================
    if hasattr(form, 'email'):
        email_novo = form.email.data.strip()

        if email_novo != current_user.email:
            if email_existe(email_novo, exclude_user_id=current_user.id):
                flash("E-mail já está em uso.", "warning")
                return redirect(url_for('perfil.meu_perfil'))

            current_user.email = email_novo
            alterou_algo = True

    # ==========================================================
    # TELEFONE
    # ==========================================================
    if hasattr(form, 'telefone'):
        telefone_novo = (form.telefone.data or '').strip()
        telefone_atual = (current_user.telefone or '').strip()

        if telefone_novo != telefone_atual:
            current_user.telefone = telefone_novo if telefone_novo else None
            alterou_algo = True

    # ==========================================================
    # ALTERAÇÃO DE SENHA (SEM SENHA ATUAL)
    # ==========================================================
    if form.nova_senha.data:
        current_user.senha = gerar_senha_hash(form.nova_senha.data)
        alterou_algo = True

    # ==========================================================
    # FOTO DE PERFIL
    # ==========================================================
    if hasattr(form, 'foto_perfil') and form.foto_perfil.data:
        trocar_imagem_usuario(current_user, form.foto_perfil.data)
        alterou_algo = True

    # ==========================================================
    # SALVAR ALTERAÇÕES
    # ==========================================================
    if alterou_algo:
        try:
            bancodedados.session.commit()
            flash("Perfil atualizado com sucesso.", "success")
        except Exception:
            bancodedados.session.rollback()
            flash("Erro ao salvar alterações.", "danger")
    else:
        flash("Nenhuma alteração foi detectada.", "info")

    return redirect(url_for('perfil.meu_perfil'))
