# ========================
# Routes - Criação de Contas/ Cadastros
# ========================

''' O que tem dentro da página de cadastros:
    - Rota de cadastro de Cliente (CPF)
    - Rota de cadastro de Cliente (CNPJ)
    - Rota de cadastro de Prestador de Serviços
    - Cada rota tem validações específicas, tratamento de foto de perfil,
      verificação de duplicidade, e salvamento no banco de dados.
'''

from flask import (
    render_template, redirect, url_for, flash, current_app
    )
from servicosdigitais.app import app, bancodedados, bcrypt
from servicosdigitais.app.models.usuario import Usuario
from servicosdigitais.app.models.clientes import ClienteCPF, ClienteCNPJ
from servicosdigitais.app.models.prestador import PrestadorServico
from servicosdigitais.app.forms.cadastro_forms import (
    FormCadastroCPF, FormCadastroCNPJ, FormCadastroPrestador
    )
from servicosdigitais.app.utilidades.validadores import (
    validar_cpf, validar_cnpj, detectar_tipo_por_numeros, apenas_numeros
    )
from servicosdigitais.app.utilidades.upload_imagem import (
    salvar_imagem, apagar_imagem_arquivo
    )


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

        # --- tentar salvar no bancodedados com cleanup se falhar ---
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

         # --- tentar salvar no bancodedados com cleanup se falhar ---
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
            current_app.logger.exception("Erro ao criar conta CNPJ - commit do bancodedados falhou")
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
