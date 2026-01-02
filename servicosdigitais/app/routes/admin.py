# ========================
# Routes - Página Admin
# ========================
''' O que tem dentro da página de admin:
- Blueprint admin (admin_bp)

'''
import os

from sqlalchemy import func

from flask_login import current_user, login_required
from flask import current_app
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, send_file
    )

from servicosdigitais.app.utilidades.seguranca import (
    gerar_senha_hash, verificar_senha_hash
    )

from servicosdigitais.app.utilidades.autenticacao import verifica_inatividade, get_caminho_log
from servicosdigitais.app.utilidades.autorizacao import somente_admin
from servicosdigitais.app.utilidades.validadores import apenas_numeros
from servicosdigitais.app.extensoes import bancodedados, bcrypt
from servicosdigitais.app.models import Usuario
from servicosdigitais.app.forms.perfil_forms import (
    FormEditarCPF, FormEditarCNPJ, FormEditarPrestador
    )

admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="templates",
    url_prefix="/admin"
)

# ADMIN - painel principal
@admin_bp.route('/')
@login_required
@somente_admin
@verifica_inatividade
def admin():
    """
    Painel inicial administrativo.
    """

    total_usuarios = Usuario.query.count()
    usuarios_ativos = Usuario.query.filter_by(ativo=True).count()

    return render_template(
        'admin/painel.html',
        total_usuarios=total_usuarios,
        usuarios_ativos=usuarios_ativos
    )


# LISTAR USUÁRIOS - Base do CRUD
@admin_bp.route('/usuarios', methods=['GET'])
@login_required
@somente_admin
def listar_usuarios():
    """
    Lista TODOS os usuários do sistema,
    inclusive inativos e administradores.
    """

    tipos = ['CPF', 'CNPJ', 'Prestador']
    tipo_selecionado = request.args.get('tipo', 'CPF')

    usuarios = (
        Usuario.query
        .filter(func.upper(func.trim(Usuario.tipo)) == tipo_selecionado.upper())
        .order_by(Usuario.nome.asc())
        .all()
    )

    lista_nomes = [
        {
            'id': u.id,
            'nome': u.nome or u.username or u.email
        }
        for u in usuarios
    ]

    user_id = request.args.get('user_id', type=int)
    usuario_detalhe = Usuario.query.get(user_id) if user_id else None

    return render_template(
        'usuarios/usuarios.html',
        tipos=tipos,
        tipo_selecionado=tipo_selecionado,
        lista_nomes=lista_nomes,
        usuario_detalhe=usuario_detalhe
    )


@admin_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
@login_required
@somente_admin
@verifica_inatividade
def detalhe_usuario(usuario_id):
    """
    Exibe os detalhes do usuário (somente visualização).
    As ações de CRUD ficam em rotas separadas.
    """

    usuario = Usuario.query.get_or_404(usuario_id)

    return render_template(
        'usuarios/detalhes_usuario.html',
        usuario=usuario
    )


@admin_bp.route('/usuario/<int:usuario_id>/editar', methods=['POST'])
@login_required
@somente_admin
@verifica_inatividade
def editar_usuario(usuario_id):
    """
    Atualiza dados básicos do usuário.
    """

    usuario = Usuario.query.get_or_404(usuario_id)

    email = (request.form.get('email') or '').strip().lower()
    telefone = request.form.get('telefone')

    # valida e-mail duplicado
    if email and email != usuario.email:
        existe = Usuario.query.filter(
            Usuario.email == email,
            Usuario.id != usuario.id
        ).first()

        if existe:
            flash('Este e-mail já está em uso.', 'warning')
            return redirect(url_for('admin.detalhe_usuario', usuario_id=usuario.id))

        usuario.email = email

    if hasattr(usuario, 'telefone'):
        usuario.telefone = telefone or None

    try:
        bancodedados.session.commit()
        flash('Dados atualizados com sucesso.', 'success')
    except Exception:
        bancodedados.session.rollback()
        flash('Erro ao atualizar dados.', 'danger')

    return redirect(url_for('admin.detalhe_usuario', usuario_id=usuario.id))


@admin_bp.route('/usuarios/<int:usuario_id>/ativacao', methods=['POST'])
@login_required
@somente_admin
def ativacao_usuario(usuario_id):
    """
    Ativa ou desativa um usuário.
    Protege contra desativar o próprio admin.
    """

    usuario = Usuario.query.get_or_404(usuario_id)

    # Impede que o admin se desative
    if usuario.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'danger')
        return redirect(url_for('admin.listar_usuarios'))

    usuario.ativo = not usuario.ativo
    bancodedados.session.commit()

    flash('Status do usuário atualizado com sucesso.', 'success')
    return redirect(url_for(
        'admin.listar_usuarios',
        tipo=usuario.tipo,
        user_id=usuario.id
    ))


# --== PROMOVER / REMOVER ADMINISTRADOR ==--
@admin_bp.route('/usuario/<int:usuario_id>/admin', methods=['POST'])
@login_required
@somente_admin
def alternar_admin_usuario(usuario_id):
    """
    Alterna o status de administrador do usuário.
    """

    usuario = Usuario.query.get_or_404(usuario_id)

    # Impede que o admin remova o próprio privilégio
    if usuario.id == current_user.id:
        flash('Você não pode remover seu próprio privilégio de administrador.', 'danger')
        return redirect(url_for(
            'admin.listar_usuarios',
            tipo=usuario.tipo,
            user_id=usuario.id
        ))

    usuario.is_admin = not usuario.is_admin

    try:
        bancodedados.session.commit()
        flash('Permissão de administrador atualizada com sucesso.', 'success')
    except Exception:
        bancodedados.session.rollback()
        flash('Erro ao alterar permissão de administrador.', 'danger')

    return redirect(url_for(
        'admin.listar_usuarios',
        tipo=usuario.tipo,
        user_id=usuario.id
    ))


@admin_bp.route('/usuario/<int:usuario_id>/excluir', methods=['POST'])
@login_required
@somente_admin
@verifica_inatividade
def excluir_usuario(usuario_id):
    """
    Exclui usuário do sistema.

    Regras:
    - Admin NÃO pode excluir outro admin
    - Soft delete é o padrão (desativa usuário)
    - Hard delete é opcional
    """

    usuario = Usuario.query.get_or_404(usuario_id)
    metodo = request.form.get('metodo', 'soft')

    # ------------------------------------------------------
    # REGRA DE SEGURANÇA: ADMIN NÃO EXCLUI ADMIN
    # ------------------------------------------------------
    if usuario.is_admin:
        flash(
            'Administradores não podem ser excluídos. '
            'Utilize a desativação da conta.',
            'warning'
        )
        return redirect(url_for(
            'admin.listar_usuarios',
            tipo=usuario.tipo,
            user_id=usuario.id
        ))

    try:
        # --------------------------------------------------
        # HARD DELETE (remoção definitiva)
        # --------------------------------------------------
        if metodo == 'hard':
            bancodedados.session.delete(usuario)
            flash('Usuário excluído permanentemente.', 'success')

        # --------------------------------------------------
        # SOFT DELETE (desativação)
        # --------------------------------------------------
        else:
            usuario.ativo = False

            if hasattr(usuario, 'excluido'):
                usuario.excluido = True

            flash('Usuário desativado com sucesso.', 'warning')

        bancodedados.session.commit()

    except Exception:
        bancodedados.session.rollback()
        flash('Erro ao excluir usuário.', 'danger')

    return redirect(url_for('admin.listar_usuarios'))


# RESETAR SENHAS - Suporte real
@admin_bp.route('/usuarios/<int:usuario_id>/resetar_senha', methods=['POST'])
@login_required
@somente_admin
def resetar_senha_usuario(usuario_id):
    """
    Reseta a senha do usuário para uma senha temporária.
    """

    usuario = Usuario.query.get_or_404(usuario_id)

    # Senha temporária simples (ajustável depois)
    senha_temporaria = 'Senha@123'

    usuario.senha_hash = gerar_senha_hash(senha_temporaria)
    bancodedados.session.commit()

    flash(
        f'Senha redefinida com sucesso. Senha temporária: {senha_temporaria}',
        'warning'
    )

    return redirect(url_for(
        'admin.listar_usuarios',
        tipo=usuario.tipo,
        user_id=usuario.id
    ))


# CRIAR USUÁRIO - Útil para testes
@admin_bp.route('/criar_usuario', methods=['GET', 'POST'])
@login_required
@somente_admin
@verifica_inatividade
def criar_usuario():
    """
    Criação de usuário.
    - Primeiro escolha do tipo (CPF/CNPJ/Prestador),
    depois os campos necessários:
    - request.form['tipo'] espera 'CPF'|'CNPJ'|'Prestador'
    - campos básicos: nome, email, senha, ativo (checkbox)
    - para campos específicos (CPF/CNPJ) você pode redirecionar para templates próprios de cadastro
    """
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        nome = request.form.get('nome') or ''
        email = request.form.get('email') or ''
        senha = request.form.get('senha') or ''
        ativo = True if request.form.get('ativo') == 'on' else False

        # validações básicas
        if not tipo or tipo not in ('CPF', 'CNPJ', 'Prestador'):
            flash('Tipo inválido.', 'erro')
            return redirect(url_for('admin.criar_usuario'))

        # criar modelo usuário (ajustar campos conforme seu modelo Usuario)
        novo = Usuario()
        novo.tipo = tipo
        novo.nome = nome.strip()
        novo.email = email.strip()
        novo.ativo = ativo
        # garantir hash de senha: usar util do seu projeto
        novo.senha_hash = gerar_senha_hash(senha) if senha else ''
        # campos específicos (ex.: documento) se vierem no form
        documento = request.form.get('documento')
        if documento:
            if tipo == 'CPF':
                novo.cpf = apenas_numeros(documento)
            elif tipo == 'CNPJ':
                novo.cnpj = apenas_numeros(documento)
        bancodedados.session.add(novo)
        bancodedados.session.commit()
        current_app.logger.info(f"Admin {current_user.id} criou usuario {novo.id} tipo {tipo}")
        flash('Usuário criado com sucesso.', 'sucesso')
        return redirect(url_for('admin.listar_usuarios', tipo=tipo, user_id=novo.id))

    # GET -> render template com formulário simples (ou modal)
    tipos = ['CPF', 'CNPJ', 'Prestador']
    return render_template('admin/criar_usuario.html', tipos=tipos)


'''# ROTA: /admin/avaliacoes  (placeholder)
@admin_bp.route('/avaliacoes', methods=['GET'])
@login_required
@somente_admin
@verifica_inatividade
def avaliacoes_admin():
    # Modificar futuramente
    flash('Área de avaliações em implementação.', 'info')
    return render_template('admin/avaliacoes.html')
'''

'''# ROTA: /admin/logs
@admin_bp.route('/logs', methods=['GET', 'POST'])
@login_required
@somente_admin
@verifica_inatividade
def visualizar_logs():
    """
    Visualização dos logs. Mantida como read-only / limpar / download.
    """

    caminho_log = get_caminho_log()

    if request.method == 'POST':
        acao = request.form.get('acao')

        if acao == 'limpar':
            open(caminho_log, 'w').close()
            flash('Logs limpos.', 'sucesso')
            return redirect(url_for('admin.visualizar_logs'))

        if acao == 'download':
            if os.path.exists(caminho_log):
                return send_file(caminho_log, as_attachment=True, download_name='erros.log')
            flash('Arquivo de logs não encontrado.', 'erro')
            return redirect(url_for('admin.visualizar_logs'))

    # leitura simples: últimas linhas (pode ser otimizado)
    conteudo = ''
    if os.path.exists(caminho_log):
        with open(caminho_log, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()[-20000:]  # pega último bloco (ajustável)
    else:
        conteudo = 'Arquivo de log não encontrado.'

    return render_template('admin/logs.html', logs=conteudo)
'''