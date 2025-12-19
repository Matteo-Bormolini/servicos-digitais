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

@perfil_bp.route('/perfil/<int:user_id>')
def perfil(user_id):
    """
    Exibe perfil público do usuário.
    Regras de vizualização:
    - visitante anônimo: blur ativo em campos sensíveis.
    - usuário logado: se o dono ativou 'ocultar_dados'
    - dono e admin sempre veem sem blur.
    """
    usuario = Usuario.query.get_or_404(user_id)

    # quem está vendo
    eh_logado = current_user.is_authenticated
    eh_dono = eh_logado and (current_user.id == usuario.id)
    eh_admin = eh_logado and getattr(current_user, 'is_admin', False)
    preferencia_ocultar = getattr(usuario, 'ocultar_dados', False)

    usar_blur = False
    if not eh_logado:
        usar_blur = True
    elif preferencia_ocultar and not (eh_dono or eh_admin):
        usar_blur = True
    else:
        usar_blur = False

    # preparar dados básicos para a view
    nome_completo = f"{usuario.nome}{(' ' + usuario.sobrenome) if usuario.sobrenome else ''}"
    tipo_usuario = getattr(usuario, 'tipo', None)

    # documento (cpf/cnpj) usando seu campo tipo (forçando a procura)
    documento = None
    tipo_doc = None
    if tipo_usuario == 'cpf' and hasattr(usuario, 'cpf'):
        documento = usuario.cpf; tipo_doc = 'CPF'
    elif tipo_usuario == 'cnpj' and hasattr(usuario, 'cnpj'):
        documento = usuario.cnpj; tipo_doc = 'CNPJ'
    elif hasattr(usuario, 'cpf') and usuario.cpf:
        documento = usuario.cpf; tipo_doc = 'CPF'
    elif hasattr(usuario, 'cnpj') and usuario.cnpj:
        documento = usuario.cnpj; tipo_doc = 'CNPJ'

    if usar_blur:
        email_display = 'Informação protegida'
        documento_display = 'Informação protegida' if documento else '—'
        telefone_display = 'Informação protegida' if usuario.telefone else '—'
    else:
        email_display = usuario.email or '—'
        documento_display = documento or '—'
        telefone_display = usuario.telefone or '—'

    # foto (usa default se não tiver)
    foto = usuario.foto_perfil or 'default.jpg'
    foto_url = url_for('static', filename=f'fotos_perfil/perfil/{foto}')

    contexto = {
        'usuario': usuario,
        'nome_completo': f"{usuario.nome}{(' ' + usuario.sobrenome) if usuario.sobrenome else ''}",
        'tipo_doc': tipo_doc,
        'documento_display': documento_display,
        'email_display': email_display,
        'telefone_display': telefone_display,
        'foto_url': foto_url,
        'usar_blur': usar_blur,
        'eh_dono': eh_dono,
        'eh_admin': eh_admin,
    }
    return render_template('perfil.html', **contexto)

# ===== BLUR ======
@perfil_bp.route('/perfil/<int:user_id>/toggle_ocultar', methods=['POST'])
@login_required
def toggle_ocultar(user_id):
    usuario = Usuario.query.get_or_404(user_id)

    # só o dono pode alterar sua preferência
    if current_user.id != usuario.id:
        flash("Apenas o dono do perfil pode alterar essa configuração.", "alert-danger")
        return redirect(url_for('perfil', user_id=user_id))

    # alterna valor
    usuario.ocultar_dados = not bool(getattr(usuario, 'ocultar_dados', False))
    try:
        bancodedados.session.commit()
        estado = "ativado" if usuario.ocultar_dados else "desativado"
        flash(f"Preferência de ocultar dados {estado}.", "alert-success")
    except Exception:
        bancodedados.session.rollback()
        current_app.logger.exception("Erro ao alterar preferência ocultar_dados")
        flash("Erro ao alterar preferência. Tente novamente.", "alert-danger")

    return redirect(url_for('perfil', user_id=user_id))


@perfil_bp.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """
    Página para o usuário autenticado visualizar e editar seus dados.
    - Seleciona o formulário apropriado pelo tipo.
    - Preenche todos os campos com os valores atuais (automaticamente)
    - Valida e aplica somente as alterações solicitadas.
    - Troca de senha exige informar a senha atual.
    - Troca de imagem usa   para salvar e apagar a anterior.
    """

    # Determinar tipo do usuário e instanciar o form correto
    tipo = getattr(current_user, 'tipo', None)
    if tipo == 'cpf':
        form = FormEditarCPF()
    elif tipo == 'cnpj':
        form = FormEditarCNPJ()
    else:
        form = FormEditarPrestador()

    # --- Preenchimento inicial (GET) ---
    if request.method == 'GET':
        # Campos comuns
        try:
            form.email.data = current_user.email
        except Exception:
            form.email.data = ''

        try:
            # telefone é opcional em alguns modelos
            form.telefone.data = getattr(current_user, 'telefone', None)
        except Exception:
            pass

        # Campos específicos por tipo
        if tipo == 'cpf':
            form.nome.data = current_user.nome
            form.sobrenome.data = getattr(current_user, 'sobrenome', None)
        elif tipo == 'cnpj':
            # usar razao_social se existir, senão usar nome
            form.razao_social.data = getattr(current_user, 'razao_social', getattr(current_user, 'nome', None))
        else:  # prestador
            form.nome_empresa.data = getattr(current_user, 'nome', None)
            form.descricao.data = getattr(current_user, 'descricao', None)

    # --- Submissão do formulário (POST) ---
    if form.validate_on_submit():
        # 1) Email: alterar apenas se mudou e não estiver em uso
        novo_email = (form.email.data or '').strip().lower()
        if novo_email and novo_email != (current_user.email or '').strip().lower():
            if email_existe(novo_email, exclude_user_id=current_user.id):
                flash("Este e-mail já está em uso por outro usuário.", "alert-warning")
                return render_template('editar_perfil.html', form=form)
            current_user.email = novo_email

        # 2) Telefone (campo opcional)
        if hasattr(current_user, 'telefone'):
            current_user.telefone = form.telefone.data or None

        # 3) Campos por tipo — atualizar somente os permitidos
        if tipo == 'cpf':
            # não alterar CPF (campo imutável), apenas nome/sobrenome
            current_user.nome = form.nome.data or current_user.nome
            current_user.sobrenome = form.sobrenome.data or getattr(current_user, 'sobrenome', None)
        elif tipo == 'cnpj':
            # não alterar CNPJ, apenas razão social
            current_user.razao_social = form.razao_social.data or getattr(current_user, 'razao_social', getattr(current_user, 'nome', None))
        else:  # prestador
            current_user.nome = form.nome_empresa.data or current_user.nome
            current_user.descricao = form.descricao.data or getattr(current_user, 'descricao', None)
            # NOTE: serviços do prestador devem ser gerenciados em rota separada (/meus_servicos)

        # 4) Alteração de senha (opcional e segura)
        # - se o usuário forneceu nova senha, exigimos senha atual correta
        if getattr(form, 'senha_nova', None) and form.senha_nova.data:
            if not getattr(form, 'senha_atual', None) or not form.senha_atual.data:
                flash("Para alterar a senha, informe sua senha atual.", "alert-warning")
                return render_template('editar_perfil.html', form=form)
            # checar senha atual
            if not bcrypt.check_password_hash(current_user.senha_hash, form.senha_atual.data):
                flash("Senha atual incorreta.", "alert-danger")
                return render_template('editar_perfil.html', form=form)
            # gerar novo hash e gravar
            novo_hash = bcrypt.generate_password_hash(form.senha_nova.data).decode('utf-8')
            current_user.senha_hash = novo_hash

        # 5) Foto de perfil (opcional) — se o form tiver campo foto_perfil
        if getattr(form, 'foto_perfil', None) and form.foto_perfil.data:
            try:
                trocou = trocar_imagem_usuario(current_user, form.foto_perfil.data, prefix='user')
                if not trocou:
                    # trocar_imagem_usuario já loga exceção; apenas notifica o usuário
                    flash("Não foi possível salvar a imagem enviada. Tente novamente.", "alert-warning")
            except Exception:
                current_app.logger.exception("Erro ao processar upload da foto no editar_perfil")
                flash("Erro ao processar a imagem. Tente novamente.", "alert-warning")

        # 6) Commit das alterações (com tratamento)
        try:
            bancodedados.session.commit()
            flash("Perfil atualizado com sucesso.", "alert-success")
            return redirect(url_for('perfil', user_id=current_user.id))
        except Exception:
            bancodedados.session.rollback()
            current_app.logger.exception("Erro ao salvar alterações do perfil")
            flash("Erro ao atualizar perfil. Tente novamente mais tarde.", "alert-danger")
            return render_template('editar_perfil.html', form=form)

    # GET ou validação falhou -> renderizar o template (form preenchido com dados atuais)
    return render_template('editar_perfil.html', form=form)

