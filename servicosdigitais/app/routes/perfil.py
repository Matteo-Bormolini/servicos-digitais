# ========================
# Routes - Área do usuário / Perfil
# ========================

''' O que tem dentro da Área do Usuário / Perfil:
- Visualizar perfil público (com regras de visibilidade)
- Editar perfil (formulário dinâmico por tipo de usuário)
- Alternar preferência de ocultar dados sensíveis no perfil público
- Upload de foto de perfil
- Alteração de senha (com verificação da senha atual)
- Validação de email único ao editar perfil
- Tratamento de erros ao salvar alterações
- Uso de Flask-Login para controle de acesso
- Uso de Flash para feedback ao usuário
'''

from flask_login import current_user, login_required
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, current_app
    )

from servicosdigitais.app import bancodedados, bcrypt
from servicosdigitais.app.models.usuario import Usuario
from servicosdigitais.app.forms.perfil_forms import (
    FormEditarCPF, FormEditarCNPJ, FormEditarPrestador
    )
from servicosdigitais.app.utilidades.upload_imagem import trocar_imagem_usuario
from servicosdigitais.app.utilidades.validadores import email_existe


perfil_bp = Blueprint(
    "perfil",
    __name__,
    template_folder="templates"
)

# ======================================================
# PERFIL DO USUÁRIO LOGADO (USADO NO NAVBAR)
# ======================================================
@perfil_bp.route('/perfil')
@login_required
def meu_perfil():
    """
    Perfil do usuário autenticado (usado no navbar).
    Nunca recebe ID na URL.
    """
    return redirect(
        url_for(
            'perfil.perfil_publico',
            user_id=current_user.id
        )
    )


# ======================================================
# PERFIL PÚBLICO (VISITANTES / OUTROS USUÁRIOS)
# ======================================================
@perfil_bp.route('/perfil/<int:user_id>')
def perfil_publico(user_id):
    """
    Exibe perfil público do usuário.

    Regras:
    - visitante: blur ativo
    - logado:
        - dono/admin: sem blur
        - respeita ocultar_dados
    """
    usuario = Usuario.query.get_or_404(user_id)

    # =============================
    # CONTEXTO DE QUEM VISUALIZA
    # =============================
    eh_logado = current_user.is_authenticated
    eh_dono = eh_logado and current_user.id == usuario.id
    eh_admin = eh_logado and getattr(current_user, 'is_admin', False)
    ocultar = bool(getattr(usuario, 'ocultar_dados', False))

    usar_blur = (
        not eh_logado or
        (ocultar and not (eh_dono or eh_admin))
    )

    # =============================
    # NOME E DOCUMENTO
    # =============================
    nome_completo = f"{usuario.nome}{(' ' + usuario.sobrenome) if usuario.sobrenome else ''}"

    documento = None
    tipo_doc = None

    if usuario.tipo == 'cpf' and hasattr(usuario, 'cpf'):
        documento, tipo_doc = usuario.cpf, 'CPF'
    elif usuario.tipo == 'cnpj' and hasattr(usuario, 'cnpj'):
        documento, tipo_doc = usuario.cnpj, 'CNPJ'

    # =============================
    # DADOS VISÍVEIS
    # =============================
    if usar_blur:
        email_display = 'Informação protegida'
        documento_display = 'Informação protegida' if documento else '—'
        telefone_display = 'Informação protegida' if usuario.telefone else '—'
    else:
        email_display = usuario.email or '—'
        documento_display = documento or '—'
        telefone_display = usuario.telefone or '—'

    # =============================
    # FOTO
    # =============================
    foto = usuario.foto_perfil or 'default.jpg'
    foto_url = url_for('static', filename=f'fotos_perfil/perfil/{foto}')

    return render_template(
        'perfil.html',
        usuario=usuario,
        nome_completo=nome_completo,
        tipo_doc=tipo_doc,
        documento_display=documento_display,
        email_display=email_display,
        telefone_display=telefone_display,
        foto_url=foto_url,
        usar_blur=usar_blur,
        eh_dono=eh_dono,
        eh_admin=eh_admin
    )


# ===== BLUR ======
@perfil_bp.route('/perfil/<int:user_id>/toggle_ocultar', methods=['POST'])
@login_required
def toggle_ocultar(user_id):
    usuario = Usuario.query.get_or_404(user_id)

    if current_user.id != usuario.id:
        flash("Apenas o dono do perfil pode alterar essa configuração.", "alert-danger")
        return redirect(url_for('perfil.perfil_publico', user_id=user_id))

    usuario.ocultar_dados = not bool(usuario.ocultar_dados)

    try:
        bancodedados.session.commit()
        estado = "ativado" if usuario.ocultar_dados else "desativado"
        flash(f"Preferência de ocultar dados {estado}.", "alert-success")
    except Exception:
        bancodedados.session.rollback()
        current_app.logger.exception("Erro ao alternar ocultar_dados")
        flash("Erro ao alterar preferência.", "alert-danger")

    return redirect(url_for('perfil.perfil_publico', user_id=user_id))


@perfil_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """
    Página para o usuário autenticado visualizar e editar seus dados.

    Regras:
    - Usa formulário conforme o tipo do usuário (cpf, cnpj, prestador)
    - Campos sensíveis são controlados
    - Alteração de senha exige senha atual
    - Foto de perfil é opcional
    """

    # =====================================
    # DEFINIR FORMULÁRIO PELO TIPO
    # =====================================
    tipo_usuario = getattr(current_user, 'tipo', None)

    if tipo_usuario == 'cpf':
        form = FormEditarCPF()
    elif tipo_usuario == 'cnpj':
        form = FormEditarCNPJ()
    else:
        form = FormEditarPrestador()

    # =====================================
    # PREENCHIMENTO INICIAL
    # =====================================
    if request.method == 'GET':
        form.email.data = current_user.email
        if hasattr(form, 'telefone'):
            form.telefone.data = getattr(current_user, 'telefone', None)

        if tipo_usuario == 'cpf':
            form.nome.data = current_user.nome
            form.sobrenome.data = getattr(current_user, 'sobrenome', None)

        elif tipo_usuario == 'cnpj':
            form.razao_social.data = getattr(
                current_user,
                'razao_social',
                current_user.nome
            )

        else:  # prestador
            form.nome_empresa.data = current_user.nome
            form.descricao.data = getattr(current_user, 'descricao', None)

    # =====================================
    # SUBMISSÃO DO FORMULÁRIO
    # =====================================
    if form.validate_on_submit():

        # ---------- EMAIL ----------
        novo_email = (form.email.data or '').strip().lower()
        email_atual = (current_user.email or '').strip().lower()

        if novo_email and novo_email != email_atual:
            if email_existe(novo_email, exclude_user_id=current_user.id):
                flash("Este e-mail já está em uso.", "alert-warning")
                return render_template('editar_perfil.html', form=form)
            current_user.email = novo_email

        # ---------- TELEFONE ----------
        if hasattr(current_user, 'telefone') and hasattr(form, 'telefone'):
            current_user.telefone = form.telefone.data or None

        # ---------- CAMPOS POR TIPO ----------
        if tipo_usuario == 'cpf':
            current_user.nome = form.nome.data or current_user.nome
            current_user.sobrenome = form.sobrenome.data or current_user.sobrenome

        elif tipo_usuario == 'cnpj':
            current_user.razao_social = (
                form.razao_social.data or current_user.razao_social
            )

        else:  # prestador
            current_user.nome = form.nome_empresa.data or current_user.nome
            current_user.descricao = form.descricao.data or current_user.descricao

        # ---------- ALTERAÇÃO DE SENHA ----------
        if hasattr(form, 'senha_nova') and form.senha_nova.data:
            if not form.senha_atual.data:
                flash("Informe sua senha atual para alterá-la.", "alert-warning")
                return render_template('editar_perfil.html', form=form)

            if not bcrypt.check_password_hash(
                current_user.senha_hash,
                form.senha_atual.data
            ):
                flash("Senha atual incorreta.", "alert-danger")
                return render_template('editar_perfil.html', form=form)

            novo_hash = bcrypt.generate_password_hash(
                form.senha_nova.data
            ).decode('utf-8')
            current_user.senha_hash = novo_hash

        # ---------- FOTO DE PERFIL ----------
        if hasattr(form, 'foto_perfil') and form.foto_perfil.data:
            try:
                sucesso = trocar_imagem_usuario(
                    current_user,
                    form.foto_perfil.data,
                    prefix='user'
                )
                if not sucesso:
                    flash("Não foi possível salvar a imagem.", "alert-warning")
            except Exception:
                current_app.logger.exception("Erro ao trocar foto de perfil")
                flash("Erro ao processar a imagem.", "alert-warning")

        # ---------- COMMIT ----------
        try:
            bancodedados.session.commit()
            flash("Perfil atualizado com sucesso.", "alert-success")
            return redirect(url_for('perfil.meu_perfil'))
        except Exception:
            bancodedados.session.rollback()
            current_app.logger.exception("Erro ao salvar edição de perfil")
            flash("Erro ao atualizar perfil.", "alert-danger")

    return render_template('editar_perfil.html', form=form)
