# ========================
# Routes - Página Admin
# ========================
''' O que tem dentro da página de admin:
- Blueprint admin (admin_bp)

'''
import os

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


@admin_bp.route('/', methods=['GET'])
@login_required
@somente_admin
@verifica_inatividade
def admin():
    """
    Dashboard de quantos usuários possuem, dividos em 4 itens:
    - Usuários Totais: | - CPF: | - CNPJ: | Prestadores: |
    """
    qtd_cpf = Usuario.query.filter_by(tipo='CPF').count()
    qtd_cnpj = Usuario.query.filter_by(tipo='CNPJ').count()
    qtd_prestadores = Usuario.query.filter_by(tipo='Prestador').count()
    qtd_usuarios = qtd_cpf + qtd_cnpj + qtd_prestadores

    # passe ao template os dados para o resumo
    return render_template('admin/index.html',
                           qtd_usuarios=qtd_usuarios,
                           qtd_cpf=qtd_cpf,
                           qtd_cnpj=qtd_cnpj,
                           qtd_prestadores=qtd_prestadores)


# ROTA: /admin/usuarios  (lista em 3 colunas conforme solicitado)
@admin_bp.route('/usuarios', methods=['GET'])
@login_required
@somente_admin
@verifica_inatividade
def listar_usuarios():
    """
    Lista de usuários:
    - tipos:['CPF','CNPJ','Prestador'] - (10%)
    - nomes: todos os nomes do tipo selecionado para coluna 2 (20%)
    - detalhe: se user_id for passado, carrega detalhe para coluna 3
    """
    # Lista coluna 1 (apenas tipos)
    tipos = ['CPF', 'CNPJ', 'Prestador']
    tipo_selecionado = request.args.get('tipo') or tipos[0]
    usuarios_nomes = Usuario.query.filter_by(tipo=tipo_selecionado).order_by(Usuario.nome.asc()).all()
    # Lista coluna 2 (apenas nomes)
    lista_nomes = [{'id': u.id, 'nome': getattr(u, 'nome_fantasia', u.nome or u.username)} for u in usuarios_nomes] #!! Acho que está errado!

    # detalhe (coluna 3)
    user_id = request.args.get('user_id', type=int) #!! Acho que está errado!
    usuario_detalhe = None
    if user_id:
        usuario_detalhe = Usuario.query.get(user_id)

    return render_template('admin/usuarios.html',
                           tipos=tipos,
                           tipo_selecionado=tipo_selecionado,
                           lista_nomes=lista_nomes,
                           usuario_detalhe=usuario_detalhe)


# ROTA: /admin/usuario/<id> (detalhe + ações POST)
@admin_bp.route('/usuario/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
@somente_admin
@verifica_inatividade
def detalhe_usuario(usuario_id):
    """
    Mostra e processa:
    - editar_perfil_admin (form completo apropriado ao tipo)
    - salvar_edicao
    - toggle_ativo
    - excluir_perfil
    """
    
    # Obter usuário alvo
    usuario = Usuario.query.get_or_404(usuario_id)
    tipo = usuario.tipo  # 'cpf', 'cnpj', 'prestador', 'fornecedor'

    if tipo == 'cpf':
        form = FormEditarCPF()
    elif tipo == 'cnpj':
        form = FormEditarCNPJ()
    elif tipo == 'prestador':
        form = FormEditarPrestador()
    # elif tipo == 'fornecedor':
        #form = FormEditarFornecedor()
    else:
        flash("Tipo de usuário desconhecido.", "alert-danger")
        return redirect(url_for('admin.listar_usuarios'))

    # 3) GET → preencher campos
    if request.method == 'GET':
        form.email.data = usuario.email
        if hasattr(usuario, 'telefone'):
            form.telefone.data = usuario.telefone

        # Campos por tipo
        if tipo == 'cpf':
            form.nome.data = usuario.nome
            form.sobrenome.data = usuario.sobrenome
        elif tipo == 'cnpj':
            form.razao_social.data = usuario.razao_social
            form.cnpj.data = usuario.cnpj
        elif tipo == 'prestador':
            form.nome_empresa.data = usuario.nome
            form.descricao.data = getattr(usuario, 'descricao', None)
            form.cnpj.data = usuario.cnpj
        elif tipo == 'fornecedor':
            form.razao_social.data = usuario.razao_social
            form.nome_fantasia.data = usuario.nome_fantasia
            form.cnpj.data = usuario.cnpj

    # AÇÃO: Alternar ativo/inativo
    if request.form.get('acao') == 'toggle_ativo':
        usuario.ativo = not bool(usuario.ativo)
        try:
            bancodedados.session.commit()
            flash(f"Conta {'ativada' if usuario.ativo else 'desativada'}.", "alert-success")
        except Exception:
            bancodedados.session.rollback()
            flash("Erro ao alterar status da conta.", "alert-danger")

        return redirect(url_for('admin.usuario_detalhe', usuario_id=usuario.id))
    
    # AÇÃO: Salvar edição (editar_perfil_admin)
    if request.form.get('acao') == 'salvar_edicao' and form.validate_on_submit():

        # ----- Email -----
        novo_email = (form.email.data or "").strip().lower()
        if novo_email != (usuario.email or "").strip().lower():
            # validar duplicidade
            existente = Usuario.query.filter(
                Usuario.email == novo_email,
                Usuario.id != usuario.id
            ).first()
            if existente:
                flash("Este e-mail já está em uso por outro usuário.", "alert-warning")
                return render_template('admin/usuario_detalhe.html', usuario=usuario, form=form)
            usuario.email = novo_email

        # ----- Telefone -----
        if hasattr(usuario, 'telefone'):
            usuario.telefone = form.telefone.data or None

        # ----- Campos por tipo -----
        if tipo == 'cpf':
            usuario.nome = form.nome.data or usuario.nome
            usuario.sobrenome = form.sobrenome.data or usuario.sobrenome
            # CPF não deve ser alterado

        elif tipo == 'cnpj':
            usuario.razao_social = form.razao_social.data
            # CNPJ não deve ser alterado

        elif tipo == 'prestador':
            usuario.nome = form.nome_empresa.data or usuario.nome
            usuario.descricao = form.descricao.data or usuario.descricao
            # CNPJ não deve ser alterado

        elif tipo == 'fornecedor':
            usuario.razao_social = form.razao_social.data
            usuario.nome_fantasia = form.nome_fantasia.data
            # CNPJ não deve ser alterado

        # AÇÃO: Excluir Perfil
        # ----- Alterar senha (admin PODE trocar sem pedir senha atual) -----
        if getattr(form, 'senha_nova', None) and form.senha_nova.data:
            novo_hash = bcrypt.generate_password_hash(form.senha_nova.data).decode('utf-8')
            usuario.senha_hash = novo_hash

        # Salvar tudo
        try:
            bancodedados.session.commit()
            flash("Dados atualizados com sucesso.", "alert-success")
            return redirect(url_for('admin.usuario_detalhe', usuario_id=usuario.id))
        except Exception:
            bancodedados.session.rollback()
            flash("Erro ao salvar alterações.", "alert-danger")

    # AÇÃO: Excluir perfil (soft delete ou hard delete)
    if request.form.get('acao') == 'excluir_perfil':
        metodo = request.form.get('metodo', 'soft')

        # remoção permanente
        if metodo == 'hard':
            try:
                bancodedados.session.delete(usuario)
                bancodedados.session.commit()
                flash("Usuário excluído permanentemente.", "alert-success")
            except Exception:
                bancodedados.session.rollback()
                flash("Erro ao excluir usuário.", "alert-danger")
            return redirect(url_for('admin.listar_usuarios'))

        # soft delete
        usuario.ativo = False
        if hasattr(usuario, 'excluido'):
            usuario.excluido = True
        try:
            bancodedados.session.commit()
            flash("Usuário marcado como excluído (soft delete).", "alert-warning")
        except Exception:
            bancodedados.session.rollback()
            flash("Erro ao executar soft delete.", "alert-danger")

        return redirect(url_for('admin.listar_usuarios')) # URL TA CERTA?

    return render_template('admin/usuario_detalhe.html', usuario=usuario, form=form)


# ROTA: /admin/criar_usuario  (botão +Usuário abre modal/form)
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


# ROTA: /admin/alterar_senha (botão fixo canto inferior direito)
@admin_bp.route('/alterar_senha', methods=['GET', 'POST'])
@login_required
@somente_admin
@verifica_inatividade
def alterar_senha_admin():
    """
    Alterar a própria senha do admin.
    Requer: senha_atual, nova_senha, confirma.
    Usa função gerar_senha_hash/verificar_senha_hash do seu projeto.
    """
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual', '')
        nova_senha = request.form.get('nova_senha', '')
        confirma = request.form.get('confirma', '')
        if not senha_atual or not nova_senha or not confirma:
            flash('Preencha todos os campos.', 'erro')
            return redirect(url_for('admin.alterar_senha_admin'))
        if nova_senha != confirma:
            flash('Confirmação diferente.', 'erro')
            return redirect(url_for('admin.alterar_senha_admin'))
        if not verificar_senha_hash(senha_atual, current_user.senha_hash):
            flash('Senha atual incorreta.', 'erro')
            return redirect(url_for('admin.alterar_senha_admin'))
        current_user.senha_hash = gerar_senha_hash(nova_senha)
        bancodedados.session.commit()
        flash('Senha alterada com sucesso.', 'sucesso')
        return redirect(url_for('admin.admin'))
    return render_template('admin/alterar_senha.html')


# ROTA: /admin/logs
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


# ROTA: /admin/avaliacoes  (placeholder)
@admin_bp.route('/avaliacoes', methods=['GET'])
@login_required
@somente_admin
@verifica_inatividade
def avaliacoes_admin():
    # Modificar futuramente
    flash('Área de avaliações em implementação.', 'info')
    return render_template('admin/avaliacoes.html')
