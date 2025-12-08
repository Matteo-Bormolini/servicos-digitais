# routes.py - ServicosDigitais
from flask import (
    render_template, redirect, url_for, flash, request, abort,
    current_app, send_from_directory, session, jsonify, Blueprint
)
from flask_login import (
    login_user, logout_user, current_user, login_required,
    UserMixin, LoginManager, fresh_login_required, login_fresh,
    confirm_login
)
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, and_, func
from werkzeug.utils import secure_filename
import os

from servicosdigitais.app import bancodedados, bcrypt, app
from servicosdigitais.app.utils import enviar_email_smtp, gerar_token_prioridade
from servicosdigitais.app.models import (
    Usuario, ClienteCPF, ClienteCNPJ, PrestadorServico,
    ServicoPrestado, #Fornecedor, Avaliacao, Categoria
)
from servicosdigitais.app.forms import (
    FormSupport,
    FormLogin,
    FormCadastroCPF, FormCadastroCNPJ, FormCadastroPrestador, FormCadastroServico,
    FormEditarCPF, FormEditarCNPJ, FormEditarPrestador
)
from servicosdigitais.app.seguranca import (
    bloquear_tipos, somente_admin, somente_prestador,
    somente_fornecedor, somente_cpf, somente_cnpj,
    salvar_imagem, apagar_imagem_arquivo, email_existe,
    parece_email, apenas_numeros, detectar_tipo_por_numeros,
    esta_ativo, validar_cpf, validar_cnpj, verificar_bloqueio,
    registrar_falha, registrar_sucesso, trocar_imagem_usuario,
    _mask_doc, _mask_email, _mask_phone
)

bp = Blueprint('servicos', __name__, template_folder='templates', url_prefix='')


TextosEntrada = "Olá Mundo!"
Localizacao = ""

# -------------------------
# Páginas Home
# -------------------------

# rota home - ServicosDigitais
# Teóricamente foi feita 90%
@app.route('/')
def home():
    """
    Página inicial:
    - lista textos de entrada (tabela: TextosEntrada, coluna: textos_entrada);
    - lista cidades cadastradas (tabela Localizacao, coluna: cidade);
    - lista especialidades (tabela PrestadorServico, coluna: especialidade)
    - mini-painel de sugestão para cadastro:
       - linha 1: "Você ainda não tem cadastro?"
       - linha 2: texto vindo de TextosEntrada.texto_cadastro (se existir)
       - linha 3: links para cadastro CPF, prestador e CNPJ (usando nomes de rota padrão)
    """
    texto_entrada_manual = "Olá Mundo"
    texto_cadastro_manual = "Vamos te guiar o melhor para você!"

    # ===========================
    # TEXTOS DE ENTRADA
    # ===========================
    try:
        textos = TextosEntrada.query.first()
    except Exception:
        textos = None

    texto_entrada = (
        textos.texto_entrada
        if textos and getattr(textos, "texto_entrada", None)
        else texto_entrada_manual
    )

    texto_cadastro = (
        textos.texto_cadastro
        if textos and getattr(textos, "texto_cadastro", None)
        else texto_cadastro_manual
    )
    # ===========================
    # CIDADES (Tabela localizacao)
    # ===========================
    regioes_manuais = ["Indaiatuba", "Itu", "Salto"]

    try:
        cidades_q = (
            Localizacao.query.with_entities(Localizacao.cidade)
            .distinct()
            .order_by(Localizacao.cidade)
            .all()
        )
        regioes = [c.cidade for c in cidades_q if c.cidade]
        if not regioes:
            regioes = regioes_manuais
    except Exception:
        regioes = regioes_manuais

    # ===========================
    # SERVIÇOS
    # ===========================
    try:
        servicos_q = (
            PrestadorServico.query.with_entities(PrestadorServico.especialidade)
            .distinct()
            .order_by(PrestadorServico.especialidade)
            .all()
        )
        servicos = [
            s.especialidade for s in servicos_q
            if s.especialidade and s.especialidade.strip()
        ]
    except Exception:
        servicos = []

    # ===========================
    # USUÁRIO LOGADO
    # ===========================
    try:
        usuario_logado = current_user.is_authenticated
    except Exception:
        usuario_logado = False

    return render_template(
        'home.html',
        texto_entrada=texto_entrada,
        texto_cadastro=texto_cadastro,
        regioes=regioes,
        servicos=servicos,
        usuario_logado=usuario_logado
    )


# -------------------------
# Autenticação: login / logout
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
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
                return redirect(url_for('home'))

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
            return redirect(destino) if destino else redirect(url_for('home'))

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


@app.route('/logout', methods=['POST'])
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

    return redirect(url_for('home'))


# -------------------------
# Cadastros
# -------------------------

# Cadastro de Cliente (CPF)
@app.route('/cadastrar_cpf', methods=['GET', 'POST'])
def cadastrar_cpf():
    form = FormCadastroCPF()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        cpf_digits = apenas_numeros(form.cpf.data)

        # validação opcional de CNPJ (controlado por config)
        if app.config.get('VALIDAR_CPF', True):
            if detectar_tipo_por_numeros(cpf_digits) != 'cpf' or not validar_cpf(cpf_digits):
                flash('CPF inválido. Verifique os números e tente novamente.', 'alert-danger')
                return redirect(url_for('rota_cadastrar_cpf'))

        # Evitar duplicidade
        if Usuario.query.filter_by(email=email).first() or ClienteCPF.query.filter_by(cpf=cpf_digits).first():
            flash("Já existe conta com esse e-mail ou CPF.", "alert-warning")
            return redirect(url_for('login'))

        senha_hash = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')

        novo = ClienteCPF(
            nome=form.username.data,
            telefone=form.telefone.data or None,
            email=email,
            senha_hash=senha_hash,
            cpf=cpf_digits,
            tipo='cpf'
        )

        # --- salvar foto ---
        saved_name = None
        if getattr(form, 'foto_perfil', None) and form.foto_perfil.data:
            try:
                saved_name, _thumb = salvar_imagem(
                    form.foto_perfil.data,
                    folder='perfil',
                    prefix='user',
                    gerar_thumb=False
                )
                novo.foto_perfil = saved_name
            except Exception:
                current_app.logger.exception("Erro ao salvar foto de perfil no cadastro CPF")
                flash("Não foi possível processar a foto enviada. Conta criada sem foto.", "alert-warning")

        # --- tentar salvar no DB com cleanup se falhar ---
        try:
            bancodedados.session.add(novo)
            bancodedados.session.commit()
        except Exception:
            # se falhou e salvamos arquivo, tentar apagar para não deixar lixo
            if saved_name:
                try:
                    apagar_imagem_arquivo(saved_name, folder='perfil')
                except Exception:
                    current_app.logger.exception("Falha ao apagar imagem após erro no commit")
            current_app.logger.exception("Erro ao criar conta CPF - Salvamento falhou")
            flash("Erro interno ao criar conta. Tente novamente mais tarde.", "alert-danger")
            return redirect(url_for('rota_cadastrar_cpf'))

        # Se deu certo:
        return redirect(url_for('login', show_edit_prompt=1))

    return render_template('cadastros/cadastrocpf.html', form=form)


# Cadastro de Cliente (CNPJ)
@app.route('/cadastrar_cnpj', methods=['GET', 'POST'])
def cadastrar_cnpj():
    """
    Rota para cadastro de clientes pessoa jurídica (CNPJ).
    - Normaliza o CNPJ (salva só dígitos).
    - Verifica duplicidade de e-mail e CNPJ.
    - Foto de perfil é opcional 
    """
    form_cnpj = FormCadastroCNPJ()

    if form_cnpj.validate_on_submit():
        email = form_cnpj.email.data.strip().lower()
        cnpj_digits = apenas_numeros(form_cnpj.cnpj.data)

        # validação opcional de CNPJ (controlado por config)
        validar = current_app.config.get('VALIDAR_CNPJ', True)
        if validar:
            tipo = detectar_tipo_por_numeros(cnpj_digits)
            if tipo != 'cnpj':
                flash("CNPJ inválido ou formato incorreto. Verifique e tente novamente.", "alert-danger")
                return redirect(url_for('cadastro_cnpj'))
            if 'validar_cnpj' in globals() and not validar_cnpj(cnpj_digits):
                flash("CNPJ inválido (dígitos verificadores).", "alert-danger")
                return redirect(url_for('cadastro_cnpj'))
            
        # Checagem de duplicidade (e-mail ou cnpj já cadastrados)
        if Usuario.query.filter_by(email=email).first() or ClienteCNPJ.query.filter_by(cnpj=cnpj_digits).first():
            flash("Já existe conta com esse e-mail ou CNPJ.", "alert-warning")
            return redirect(url_for('login'))

        # Senha
        senha_hash = bcrypt.generate_password_hash(form_cnpj.senha.data).decode('utf-8')

        # Cria objeto ClienteCNPJ
        novo = ClienteCNPJ(
            razao_social=form_cnpj.razao_social.data if hasattr(form_cnpj, 'razao_social') else form_cnpj.username.data,
            email=email,
            senha_hash=senha_hash,
            cnpj=cnpj_digits,
            # se seu form tiver campo 'telefone' ou 'empresa', ajuste aqui
            telefone=(form_cnpj.telefone.data or None) if hasattr(form_cnpj, 'telefone') else None,
            tipo='cnpj'
        )

        # --- salvar foto ---
        nome_salvo = None
        if getattr(form_cnpj, 'foto_perfil', None) and form_cnpj.foto_perfil.data:
            try:
                nome_salvo, _thumb = salvar_imagem(
                    form_cnpj.foto_perfil.data,
                    folder='perfil',
                    prefix='cnpj',
                    gerar_thumb=False
                )
                novo.foto_perfil = nome_salvo
            except Exception:
                current_app.logger.exception("Erro ao salvar foto no cadastro CNPJ")
                flash("Não foi possível processar a foto enviada. Conta será criada sem foto.", "alert-warning")
                nome_salvo = None

         # --- tentar salvar no DB com cleanup se falhar ---
        try:
            bancodedados.session.add(novo)
            bancodedados.session.commit()
        except Exception:
            # se falhou e salvamos arquivo, tentar apagar para não deixar lixo
            if nome_salvo:
                try:
                    apagar_imagem_arquivo(nome_salvo, folder='perfil')
                except Exception:
                    current_app.logger.exception("Falha ao apagar imagem após erro no commit (CNPJ)")
            bancodedados.session.rollback()
            current_app.logger.exception("Erro ao criar conta CNPJ - commit do DB falhou")
            flash("Erro interno ao criar conta. Tente novamente mais tarde.", "alert-danger")
            return redirect(url_for('cadastro_cnpj'))

        # Se deu certo:
        flash("Conta empresarial criada. Faça login.", "alert-success")
        return redirect(url_for('login', show_edit_prompt=1))
    return render_template('cadastros/cadastrocnpj.html', form_cnpj=form_cnpj)


# Cadastro Prestador (versão padronizada, similar ao cadastro CNPJ)
@app.route('/cadastrar_prestador', methods=['GET', 'POST'])
def cadastrar_prestador():
    """
    - Form parecido com CNPJ.
    - Normaliza CNPJ (apenas dígitos).
    - Verifica duplicidade de e-mail e cnpj.
    - Validação do CNPJ é opcional via config VALIDAR_PRESTADOR.
    - Foto/logo opcional (se o Form tiver foto_perfil).
    - Novo prestador é criado com ativo=False (aguarda aprovação).
    - Precisa de Aprovação Manual
    """
    form  = FormCadastroPrestador()

    if form .validate_on_submit():
        email = form .email.data.strip().lower()
        cnpj_digits = apenas_numeros(form .cnpj.data)

        # validação opcional de CNPJ (controlado por config)
        validar = current_app.config.get('VALIDAR_PRESTADOR', True)
        if validar:
            tipo = detectar_tipo_por_numeros(cnpj_digits)
            if tipo != 'cnpj':
                flash("CNPJ inválido ou formato incorreto. Verifique e tente novamente.", "alert-danger")
                return redirect(url_for('cadastrar_prestador'))
            if 'validar_cnpj' in globals() and not validar_cnpj(cnpj_digits):
                flash("CNPJ inválido (dígitos verificadores).", "alert-danger")
                return redirect(url_for('cadastrar_prestador'))

        # Checagem de duplicidade (e-mail ou cnpj já cadastrados)
        existe_email = Usuario.query.filter_by(email=email).first()
        existe_cnpj_cliente = ClienteCNPJ.query.filter_by(cnpj=cnpj_digits).first() if 'ClienteCNPJ' in globals() else None
        existe_cnpj_prest = PrestadorServico.query.filter_by(cnpj=cnpj_digits).first()

        if existe_email or existe_cnpj_cliente or existe_cnpj_prest:
            flash("Já existe conta com esse e-mail ou CNPJ.", "alert-warning")
            return redirect(url_for('login'))

        # gerar senha
        senha_hash = bcrypt.generate_password_hash(form .senha.data).decode('utf-8')

        # Cria objeto Prestador
        novo = PrestadorServico(
            nome = form .username.data if hasattr(form , 'username') else (form .nome.data if hasattr(form , 'nome') else None),
            telefone = (form .telefone.data or None) if hasattr(form , 'telefone') else None,
            email = email,
            senha_hash = senha_hash,
            cnpj = cnpj_digits,
            especialidade = form .especialidade.data if hasattr(form , 'especialidade') else None,
            tipo = 'prestador',
            ativo = False  # precisa aprovação manual/admin
        )

        # --- salvar foto ---
        nome_salvo = None
        if getattr(form , 'foto_perfil', None) and form .foto_perfil.data:
            try:
                nome_salvo, _ = salvar_imagem(
                    form .foto_perfil.data,
                    folder='perfil',
                    prefix='prestador',
                    gerar_thumb=False
                )
                novo.foto_perfil = nome_salvo
            except Exception:
                
                current_app.logger.exception("Erro ao salvar foto do prestador")
                flash("Não foi possível processar a imagem enviada. Cadastro seguirá sem foto.", "alert-warning")
                nome_salvo = None

        # tentar salvar no banco com tratamento e cleanup de arquivo salvo em caso de falha
        try:
            bancodedados.session.add(novo)
            bancodedados.session.commit()
        except Exception:
            # se falhou e salvamos arquivo, tentar apagar para não deixar lixo
            bancodedados.session.rollback()
            if nome_salvo:
                try:
                    apagar_imagem_arquivo(nome_salvo, folder='perfil')
                except Exception:
                    current_app.logger.exception("Falha ao apagar imagem após erro no commit (prestador)")
            current_app.logger.exception("Erro ao criar cadastro de prestador (commit falhou)")
            flash("Erro interno ao criar cadastro. Tente novamente mais tarde.", "alert-danger")
            return redirect(url_for('cadastros/cadastroprestador.html'))

        # Se deu certo:
        flash("Cadastro enviado. Aguardando aprovação do administrador.", "alert-info")
        return redirect(url_for('home'))
    return render_template('cadastros/cadastroprestador.html', form=form )


# -------------------------
# Área do usuário / Perfil
# -------------------------

@app.route('/perfil/<int:user_id>')
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
@app.route('/perfil/<int:user_id>/toggle_ocultar', methods=['POST'])
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


@app.route('/editar_perfil', methods=['GET', 'POST'])
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


# -------------------------
# Prestadores / Serviços
# -------------------------

@bp.route('/servicos')
@bloquear_tipos('prestador') # Prestador não entra na página
def listar_servicos():
    """
    Lista automática e alfabética de serviços (nomes únicos)
    - se vazio: frase "No momento ainda não tem serviços cadastrados"
    - cada nome linka para a rota '/prestadores' com ?especialidade=<nome>
    """
    servicos_unicos = []
    try:
        if PrestadorServico is not None:
            q = (
bancodedados.session.query(func.trim(PrestadorServico.especialidade).label('esp'))
                .filter(PrestadorServico.especialidade != None)
                .filter(func.trim(PrestadorServico.especialidade) != '')
                .distinct()
            .order_by(func.upper(func.trim(PrestadorServico.especialidade)))
            )
            servicos_unicos = [row.esp for row in q.all()]
        else:
            # fallback: tenta obter das especialidades dos prestadores
            if PrestadorServico is not None:
                q = (
bancodedados.session.query(func.trim(PrestadorServico.especialidade).label('esp'))
                    .filter(PrestadorServico.especialidade != None)
                    .filter(func.trim(PrestadorServico.especialidade) != '')
                    .distinct()
            .order_by(func.upper(func.trim(PrestadorServico.especialidade)))
            )
                servicos_unicos = [row.esp for row in q.all()]
    except Exception as e:
        # registra no logger da aplicação e devolve lista vazia (evita 500)
        current_app.logger.exception("Erro ao listar serviços únicos: %s", e)
        servicos_unicos = []

    return render_template(
        'servicos/lista_servicos.html',
        servicos=servicos_unicos
    )


@bp.route('/prestadores')
@bloquear_tipos('prestador') # Prestador não entra na página
def listar_prestadores():
    """
    Segunda coluna (20%) — Lista de prestadores de uma especialidade.
    Também envia a lista de serviços (coluna 1), pois o layout é fixo.
    """
    especialidade = request.args.get('especialidade', None)

    # --- Coluna 1: lista de serviços únicos ---
    try:
        q = (
            bancodedados.session.query(func.trim(PrestadorServico.especialidade).label('esp'))
            .filter(PrestadorServico.especialidade != None)
            .filter(func.trim(PrestadorServico.especialidade) != '')
            .distinct()
            .order_by(func.upper(func.trim(PrestadorServico.especialidade)))
        )
        todos_servicos = [row.esp for row in q.all()]
    except Exception as e:
        current_app.logger.exception("Erro ao listar serviços únicos: %s", e)
        todos_servicos = []

    # --- Coluna 2: lista de prestadores daquela especialidade ---
    try:
        if especialidade:
            prestadores = (
                PrestadorServico.query
                .filter(PrestadorServico.especialidade == especialidade)
                .order_by(PrestadorServico.nome)
                .all()
            )
        else:
            prestadores = (
                PrestadorServico.query
                .order_by(PrestadorServico.nome)
                .all()
            )
    except Exception as e:
        current_app.logger.exception("Erro ao buscar prestadores: %s", e)
        prestadores = []

    return render_template(
        'servicos/lista_prestadores.html',
        todos_servicos=todos_servicos,   # coluna 1
        prestadores=prestadores,         # coluna 2
        especialidade=especialidade or 'Todos'
    )


@bp.route('/prestador/<int:prestador_id>')
@bloquear_tipos('prestador') # Prestador não entra na página
def detalhes_prestador(prestador_id):
    """
    Exibe detalhes completos de um prestador.
    • Primeira sessão → dados básicos (Usuario)
    • Segunda sessão → serviços extras cadastrados (ServicoPrestado)
    
    O HTML final divide a tela em 20% | 20% | 60%
    """

    if Usuario is None or PrestadorServico is None:
        abort(500)

    # ========== 1) Buscar dados básicos do prestador ==========
    prestador = (
        bancodedados.session.query(Usuario)
        .filter(Usuario.id == prestador_id)
        .first()
    )

    if prestador is None:
        abort(404, description="Prestador não encontrado.")

    # ========== 2) Buscar registro de PrestadorServico ==========
    registro_servico = (
        PrestadorServico.query
        .filter_by(usuario_id=prestador.id)
        .first()
    )

    if registro_servico is None:
        # não impede exibir página — apenas indica que não há serviços extras
        servicos_extras = []
    else:
        # ========== 3) Buscar serviços extras ==========
        servicos_extras = (
            ServicoPrestado.query
            .filter_by(prestador_id=registro_servico.id)
            .order_by(ServicoPrestado.nome_servico)
            .all()
        )

    # Renderização final
    return render_template(
        'servicos/detalhes_prestador.html',
        prestador=prestador,                    # dados básicos
        registro_servico=registro_servico,      # contém especialidade principal
        servicos_extras=servicos_extras         # lista de serviços extras
    )


# -------------------------
# Página Suporte #PAREI AQUI
# -------------------------

@app.route('/suporte', methods=['GET', 'POST'])
def suporte():
    form = FormSupport()
    try:
        contatos = None
        from servicosdigitais.app.models import Contact
        contatos = Contact.query.order_by(Contact.ordem).all()
        contatos_emails = [(c.valor, c.nome) for c in contatos if c.tipo == 'email']
        contatos_telefones = [(c.valor, c.nome) for c in contatos if c.tipo == 'telefone']
        contatos_whatsapp = [(c.valor, c.nome) for c in contatos if c.tipo == 'whatsapp']
    except Exception:
        contatos_emails = [('emailum@enderco.com', 'Suporte')]
        contatos_telefones = [('(19) 9 8265-6051', 'Matteo')]
        contatos_whatsapp = contatos_telefones

    if form.validate_on_submit():
        nome = form.nome.data.strip() if form.nome.data else None
        email = form.email.data.strip().lower() if form.email.data else None
        assunto = form.assunto.data
        mensagem = form.mensagem.data.strip()
        criado_em_iso = datetime.now(timezone.utc).isoformat()

        # payload para salvar/log
        payload = {
            'nome': nome,
            'email': email,
            'assunto': assunto,
            'mensagem': mensagem,
            'criado_em': criado_em_iso
        }

        ticket_id = None
        token_gerado = None
        try:
            # tenta usar model SupportTicket
            from servicosdigitais.app.models import SupportTicket
            ticket = SupportTicket(
                nome=nome,
                email=email,
                assunto=assunto,
                mensagem=mensagem,
                criado_em=datetime.now(timezone.utc)
            )

            # se usuário autenticado e email presente, gera token de prioridade
            if current_user.is_authenticated and email:
                token_gerado = ticket.gerar_token(size=6)  # salva no objeto
            bancodedados.session.add(ticket)
            bancodedados.session.commit()
            ticket_id = ticket.id
            current_app.logger.info("Support ticket saved id=%s", ticket_id)
        except Exception as e:
            bancodedados.session.rollback()
            # fallback: grava em arquivo
            try:
                instance_dir = current_app.instance_path
                os.makedirs(instance_dir, exist_ok=True)
                log_path = os.path.join(instance_dir, 'suporte_logs.txt')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(f"{criado_em_iso} | {email or 'anon'} | {assunto} | {mensagem}\n")
                current_app.logger.info("Support fallback logged at %s", log_path)
            except Exception:
                current_app.logger.exception("Falha no fallback de suporte: %s", e)

        # ===== enviar email para a equipe de suporte =====
        suporte_to = [current_app.config.get('MAIL_USERNAME') or 'suporteservicosdigitais@gmail.com']
        assunto_email = f"[Suporte] {assunto}"
        corpo = f"Novo chamado de suporte:\n\nNome: {nome or 'Anonimo'}\nEmail: {email or '—'}\nAssunto: {assunto}\n\nMensagem:\n{mensagem}\n\nTicket ID: {ticket_id or 'fallback'}\nCriado em: {criado_em_iso}\n"
        enviar_ok, err = enviar_email_smtp(suporte_to, assunto_email, corpo)

        # ===== se usuário autenticado e email informado, enviar token para o cliente =====
        if token_gerado and email:
            assunto_usuario = "Seu chamado foi recebido — token de prioridade"
            corpo_user = f"Recebemos sua solicitação. Token: {token_gerado}\n\nUse esse token em futuras comunicações para priorizar seu atendimento.\n\nAtenciosamente,\nSuporte Serviços Digitais"
            enviar_ok2, err2 = enviar_email_smtp([email], assunto_usuario, corpo_user)

        # ===== preparar popup/flash com resultado =====
        # vamos usar session para manter dados após redirect (PRG)
        result = {
            'ticket_id': ticket_id,
            'email': email,
            'token': token_gerado,
            'anonimo': not bool(email)
        }
        session['support_result'] = result

        flash("Sua ocorrência foi registrada com sucesso.", "alert-success")
        if not current_app.config.get('VALIDAR_PRESTADOR', True) or not current_app.config.get('VALIDAR_CPF', True) or not current_app.config.get('VALIDAR_CNPJ', True):
            flash("MODO TESTE: operação registrada em ambiente de testes (não enviamos e-mails externos).", "alert-info")

        return redirect(url_for('suporte'))

    # GET -> renderiza. O template vai checar session['support_result'] para mostrar popup
    return render_template(
        'suporte.html',
        form=form,
        contatos_emails=contatos_emails,
        contatos_telefones=contatos_telefones,
        contatos_whatsapp=contatos_whatsapp
    )


# -------------------------
# Avaliações
# -------------------------
'''
@bp.route('/avaliar/<int:prestador_id>', methods=['POST'])
@login_required
def avaliar(prestador_id):
    nota = int(request.form.get('nota', 5))
    comentario = request.form.get('comentario', '')
    aval = Avaliacao(
        usuario_id=current_user.id,
        prestador_id=prestador_id,
        nota=nota,
        comentario=comentario,
        created_at=datetime.now(timezone.utc)
    )
    bancodedados.session.add(aval)
    bancodedados.session.commit()
    flash("Avaliação enviada. Obrigado!", "alert-success")
    return redirect(url_for('ver_prestador', prestador_id=prestador_id))

'''
# -------------------------
# Área Admin
# -------------------------
'''
@bp.route('/admin')
@login_required
@somente_admin
def admin_home():
    qtd_prestadores = PrestadorServico.query.count() if 'PrestadorServico' in globals() else 0
    qtd_usuarios = Usuario.query.count() if 'Usuario' in globals() else 0
    aguardando = PrestadorServico.query.filter_by(ativo=False).all() if 'PrestadorServico' in globals() else []
    return render_template('admin/home.html', qtd_prestadores=qtd_prestadores, qtd_usuarios=qtd_usuarios, aguardando=aguardando)


@bp.route('/admin/aprovar_prestador/<int:prestador_id>')
@login_required
@somente_admin
def aprovar_prestador(prestador_id):
    prestador = PrestadorServico.query.get_or_404(prestador_id)
    prestador.ativo = True
    bancodedados.session.commit()
    flash("Prestador aprovado.", "alert-success")
    return redirect(url_for('admin_home'))


@bp.route('/admin/remover_prestador/<int:prestador_id>')
@login_required
@somente_admin
def remover_prestador(prestador_id):
    prestador = PrestadorServico.query.get_or_404(prestador_id)
    bancodedados.session.delete(prestador)
    bancodedados.session.commit()
    flash("Prestador removido.", "alert-info")
    return redirect(url_for('admin_home'))

'''
# -------------------------
# Uploads estáticos (se necessário)
# -------------------------
'''
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    pasta = os.path.join(current_app.root_path, 'static/fotos_perfil', 'uploads')
    return send_from_directory(pasta, filename)
'''

# -------------------------
# Busca simples / filtros
# -------------------------
'''
@bp.route('/buscar')
def buscar():
    termo = request.args.get('q', '').strip()
    prestadores = []
    if termo:
        prestadores = PrestadorServico.query.filter(
            PrestadorServico.nome.ilike(f'%{termo}%') | PrestadorServico.descricao.ilike(f'%{termo}%')
        ).all()
    return render_template('buscar.html', prestadores=prestadores, termo=termo)
'''

# -------------------------
# Erros
# -------------------------
'''
@bp.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('404.html'), 404


@bp.errorhandler(500)
def erro_servidor(e):
    bancodedados.session.rollback()
    return render_template('500.html'), 500

'''
# -------------------------
# Utilitários e comandos extra
# -------------------------
'''
@bp.route('/meu_dashboard')
@login_required
def dashboard_usuario():
    """
    Página inicial do usuário logado (diferenciar por tipo: admin, prestador, cliente).
    """
    if getattr(current_user, 'tipo', None) == 'admin':
        return redirect(url_for('admin_home'))
    if getattr(current_user, 'tipo', None) == 'prestador':
        # carregar dados do prestador
        prest = PrestadorServico.query.filter_by(usuario_id=current_user.id).first()
        servicos = ServicoPrestado.query.filter_by(prestador_id=prest.id).all() if prest else []
        return render_template('dashboard_prestador.html', prestador=prest, servicos=servicos)
    # cliente
    return render_template('dashboard_cliente.html')
'''

# -------------------------
# Fim do arquivo
# -------------------------