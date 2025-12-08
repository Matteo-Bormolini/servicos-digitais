"""
seguranca.py
Decorators e utilitários de autorização para as rotas.
Mantém toda a lógica de permissão centralizada e reutilizável.

Comportamento:
- Usuário NÃO autenticado -> sempre redireciona para a rota de login ('login')
  e exibe um flash avisando que precisa fazer login.
- Usuário autenticado mas sem permissão -> redireciona para 'home' e exibe
  flash de erro (alerta vermelho).
- Admin sempre tem acesso a todas as páginas.
"""
# ------
from functools import wraps
from flask import flash, redirect, url_for, current_app, flash
from flask_login import current_user
from werkzeug.utils import secure_filename
# ------
import os
import secrets
import time
from io import BytesIO
from PIL import Image
from typing import Optional, List, Type
# ------
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from servicosdigitais.app import bancodedados
from servicosdigitais.app.models import (
    Usuario,
    ClienteCPF, ClienteCNPJ, PrestadorServico
    )

# =========================
# SEGURANÇA DE ENTRADA
# =========================
MAX_TENTATIVAS = 5
TEMPO_BLOQUEIO_MIN = 15
RESET_TENTATIVAS_MIN = 30

def verificar_bloqueio(usuario):
    """
    Retorna True se o login deve ser bloqueado agora.
    Caso contrário, retorna False.
    Também já mostra o flash de aviso.
    """
    agora = datetime.now(timezone.utc)

    # Se bloqueado até um tempo no futuro
    if usuario.bloqueado_ate and usuario.bloqueado_ate > agora:
        minutos = int((usuario.bloqueado_ate - agora).total_seconds() // 60) + 1
        flash(f"Conta bloqueada por muitas tentativas. Tente novamente em {minutos} minuto(s).", "alert-danger")
        return True

    return False


#Se acertar
def registrar_sucesso(usuario):
    """Reseta tentativas ao logar com sucesso."""
    try:
        usuario.tentativas_falhas = 0
        usuario.ultima_falha = None
        usuario.bloqueado_ate = None
        bancodedados.session.commit()
    except SQLAlchemyError:
        bancodedados.session.rollback()


# Se falhar
def registrar_falha(usuario):
    """Incrementa falha e bloqueia se passar do limite."""
    agora = datetime.now(timezone.utc)

    try:
        # Se última falha for antiga → pode resetar
        if usuario.ultima_falha:
            if (agora - usuario.ultima_falha) > timedelta(minutes=RESET_TENTATIVAS_MIN):
                usuario.tentativas_falhas = 0

        usuario.tentativas_falhas = (usuario.tentativas_falhas or 0) + 1
        usuario.ultima_falha = agora

        # Se atingiu limite
        if usuario.tentativas_falhas >= MAX_TENTATIVAS:
            usuario.bloqueado_ate = agora + timedelta(minutes=TEMPO_BLOQUEIO_MIN)
            bancodedados.session.commit()
            flash(f"Conta bloqueada por {TEMPO_BLOQUEIO_MIN} minutos.", "alert-danger")
        else:
            restam = MAX_TENTATIVAS - usuario.tentativas_falhas
            bancodedados.session.commit()
            flash(f"Senha incorreta. Restam {restam} tentativa(s).", "alert-danger")

    except SQLAlchemyError:
        bancodedados.session.rollback()
        flash("Erro ao registrar tentativa. Tente novamente.", "alert-danger")


# ============================================================
# Função Verificação de Segurança de Senha (ainda em implementação)
# ============================================================
def senha_segura(senha):
    """
    Verifica se a senha atende aos critérios de segurança:
    - Pelo menos 6 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial
    """
    if len(senha) < 6:
        return False
    has_upper = any(c.isupper() for c in senha)
    has_lower = any(c.islower() for c in senha)
    has_digit = any(c.isdigit() for c in senha)
    has_special = any(not c.isalnum() for c in senha)
    return has_upper and has_lower and has_digit and has_special


# =========================
# BLOQUEAR TIPOS ESPECÍFICOS
# =========================
def bloquear_tipos(*tipos_bloqueados, redirect_endpoint='home'):
    """
    Bloqueia acesso para os tipos listados em tipos_bloqueados.
    - Se NÃO autenticado: redireciona para 'login' com flash.
    - Admin sempre tem acesso.
    - Se o tipo do usuário estiver em tipos_bloqueados:
        - flash e redirect para redirect_endpoint (padrão: 'home').
    """
    def decorator(funcao):
        @wraps(funcao)
        def wrapper(*args, **kwargs):

            # 1) Não logado → bloquear e mandar para login
            if not current_user.is_authenticated:
                flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
                return redirect(url_for('login'))

            usuario = current_user  # agora garantido

            # 2) Admin sempre entra
            if getattr(usuario, "is_admin", False):
                return funcao(*args, **kwargs)

            # 3) Bloqueio por tipo
            if getattr(usuario, "tipo", None) in tipos_bloqueados:
                flash("Acesso negado: sua conta não tem permissão para esta página.", "danger")
                return redirect(url_for(redirect_endpoint))

            # 4) Liberado
            return funcao(*args, **kwargs)

        return wrapper
    return decorator



# ==================
# SOMENTE ADMIN
# ==================
def somente_admin(funcao):
    """
    Permite acesso apenas para administradores.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('login'))

        if not getattr(current_user, "is_admin", False):
            flash("Acesso restrito: apenas administradores podem acessar.", "danger")
            return redirect(url_for('home'))

        return funcao(*args, **kwargs)
    return wrapper


# ==================
# SOMENTE PRESTADOR
# ==================
def somente_prestador(funcao):
    """
    Permite acesso apenas para usuários do tipo 'prestador' ou admin.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('login'))

        # Admin sempre tem acesso
        if getattr(current_user, "is_admin", False):
            return funcao(*args, **kwargs)

        if getattr(current_user, "tipo", None) != "prestador":
            flash("Acesso negado: esta página é apenas para prestadores.", "danger")
            return redirect(url_for('home'))

        return funcao(*args, **kwargs)
    return wrapper


# ==================
# SOMENTE FORNECEDOR
# ==================
def somente_fornecedor(funcao):
    """
    Permite acesso apenas para usuários do tipo 'fornecedor' ou admin.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('login'))

        if getattr(current_user, "is_admin", False):
            return funcao(*args, **kwargs)

        if getattr(current_user, "tipo", None) != "fornecedor":
            flash("Acesso negado: esta página é apenas para fornecedores.", "danger")
            return redirect(url_for('home'))

        return funcao(*args, **kwargs)
    return wrapper


# ==================
# SOMENTE CPF
# ==================
def somente_cpf(funcao):
    """
    Permite acesso apenas para usuários do tipo 'cpf' ou admin.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('login'))

        if getattr(current_user, "is_admin", False):
            return funcao(*args, **kwargs)

        if getattr(current_user, "tipo", None) != "cpf":
            flash("Acesso negado: esta área é apenas para usuários CPF.", "danger")
            return redirect(url_for('home'))

        return funcao(*args, **kwargs)
    return wrapper


# ==================
# SOMENTE CNPJ
# ==================
def somente_cnpj(funcao):
    """
    Permite acesso apenas para usuários do tipo 'cnpj' ou admin.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('login'))

        if getattr(current_user, "is_admin", False):
            return funcao(*args, **kwargs)

        if getattr(current_user, "tipo", None) != "cnpj":
            flash("Acesso negado: esta área é apenas para usuários CNPJ.", "danger")
            return redirect(url_for('home'))

        return funcao(*args, **kwargs)
    return wrapper


# ==================
# Helpers & Decorators
# ==================

# Foto_Perfil
ext_uso = {'.jpg', '.jpeg', '.png'}

def _strip_metadata_and_prepare(img, target_mode=None):
    """
    Remove metadados criando uma nova imagem sem info.
    Se target_mode fornecido, converte antes de criar.
    Retorna Image pronta para salvar.
    """
    if target_mode:
        img = img.convert(target_mode)
    else:
        # criar cópia (Temporária) de segurança
        img = img.copy()

    # Tirar metadata para proteção do usuário;
    base_mode = img.mode
    base = Image.new(base_mode, img.size)
    base.paste(img)
    return base


def salvar_imagem(
    file_storage,
    folder='fotos_perfil',
    prefix=None,
    max_size=(800, 800),
    quality=85,
    gerar_thumb=False,
    thumb_size=(200, 200)
):
    """ Salvar imagem:
    - Limpa, organiza as extensões,
    - Verifica a extensão do arquivo, se não for padrão, será ".jpg";
    - abrir imagem conforme bytes lidos (mais rápido);
    - enviar foto imagem para a pasta correta (fotos_perfil);
    - gerar_thumb -> False (por enquanto até entender);
    - tenta converter  e manter padrão para .webp;
    - se falhar -> salva no formato original;
    - Opicional: tentar salvar em miniatura;
    - se falhar -> salva no formato original;
    -- Retorna: (nome_arquivo, nome_thumb_or_None)
    """

    # leitura segura do stream (para poder reabrir para thumb)
    data = file_storage.read()
    if not data:
        raise ValueError("Arquivo inválido ou vazio.")
    # sempre resetar o cursor do stream para não quebrar usos futuros
    try:
        file_storage.stream.seek(0)
    except Exception:
        pass

    original = secure_filename(file_storage.filename or '')
    _, ext = os.path.splitext(original)
    ext = ext.lower()
    if ext not in ext_uso:
        ext = '.jpg' # padrão caso não seja uma das extensões !mudar!

    # criação de nome único
    hashcode = secrets.token_hex(8)
    ts = int(time.time())
    nome_base = f"{prefix + '_' if prefix else ''}{hashcode}_{ts}"

    # pastas
    pasta = os.path.join(current_app.root_path, 'static/fotos_perfil', folder)
    os.makedirs(pasta, exist_ok=True)

    # preparações: abrir imagem principal a partir dos bytes lidos
    bio_main = BytesIO(data)
    img = Image.open(bio_main)
    img.thumbnail(max_size)

    # tentativa de salvar em WEBP
    nome_webp = f"{nome_base}.webp"
    caminho_webp = os.path.join(pasta, nome_webp)
    saved_name = None

    try:
        # preparar imagem para webp: webp aceita RGB ou RGBA
        # remover metadata criando nova imagem
        target_mode = 'RGBA' if img.mode in ('RGBA', 'LA') else 'RGB'
        foto_limpa = _strip_metadata_and_prepare(img, target_mode=target_mode)
        # salvar webp
        foto_limpa.save(caminho_webp, format='WEBP', quality=quality, method=6)
        saved_name = nome_webp
    except Exception:
        nome_padrao = f"{nome_base}{ext}"
        caminho_fallback = os.path.join(pasta, nome_padrao)

        if ext in ('.jpg', '.jpeg'):
            # converter e remover metadata
            foto_limpa = _strip_metadata_and_prepare(img, target_mode='RGB')
            foto_limpa.save(caminho_fallback, format='JPEG', optimize=True, quality=quality)
        else:  # .png
            foto_limpa = _strip_metadata_and_prepare(img, target_mode='RGBA' if img.mode in ('RGBA','LA') else None)
            foto_limpa.save(caminho_fallback, format='PNG', optimize=True)
        saved_name = nome_padrao

    # --- miniatura (opcional) ---
    nome_thumb_ret = None
    if gerar_thumb:
        bio_thumb = BytesIO(data)        # reabrir da melhor qualidade da thumb
        thumb_img = Image.open(bio_thumb)
        thumb_img.thumbnail(thumb_size)

        # tentar salvar thumb em webp também
        nome_webp_thumb = f"{nome_base}_thumb.webp"
        caminho_webp_thumb = os.path.join(pasta, nome_webp_thumb)
        try:
            target_mode = 'RGBA' if thumb_img.mode in ('RGBA', 'LA') else 'RGB'
            thumb_limpa = _strip_metadata_and_prepare(thumb_img, target_mode=target_mode)
            thumb_limpa.save(caminho_webp_thumb, format='WEBP', quality=quality, method=6) # O que é este method: 
            nome_thumb_ret = nome_webp_thumb
        except Exception:
            if saved_name.endswith('.webp'):
                thumb_ext = ext  # usar extensão original
            else:
                thumb_ext = os.path.splitext(saved_name)[1]  #Re-usa a extensão
            nome_thumb = f"{nome_base}_thumb{thumb_ext}"
            caminho_thumb = os.path.join(pasta, nome_thumb)
            if thumb_ext in ('.jpg', '.jpeg'):
                thumb_limpa = _strip_metadata_and_prepare(thumb_img, target_mode='RGB')
                thumb_limpa.save(caminho_thumb, format='JPEG', optimize=True, quality=quality)
            else:
                thumb_limpa = _strip_metadata_and_prepare(thumb_img, target_mode='RGBA' if thumb_img.mode in ('RGBA','LA') else None)
                thumb_limpa.save(caminho_thumb, format='PNG', optimize=True)
            nome_thumb_ret = nome_thumb

    try:
        file_storage.stream.seek(0)
    except Exception:
        pass
    return saved_name, nome_thumb_ret


def apagar_imagem_arquivo(filename, folder='fotos_perfil'):
    """
    Remove arquivo do disco se existir. Não toca no DB.
    Evita remover o arquivo padrão 'default.jpg'.
    Retorna True se apagou, False caso contrário.
    """
    if not filename:
        return False
    if filename == 'default.jpg':
        return False
    caminho = os.path.join(current_app.root_path, 'static/fotos_perfil', folder, filename)
    if os.path.exists(caminho):
        try:
            os.remove(caminho)
            return True
        except Exception:
            return False
    return False


def _mask_email(email: str):
    if not email or '@' not in email:
        return email or ''
    local, dominio = email.split('@', 1)
    if len(local) <= 1:
        local_mask = '*'
    elif len(local) == 2:
        local_mask = local[0] + '*'
    else:
        local_mask = local[0] + '*' * (len(local) - 2) + local[-1]
    # manter domínio visível
    return f"{local_mask}@{dominio}"


def _mask_doc(doc: str) -> str:
    """Mascarar CPF/CNPJ (apenas dígitos esperados). Ex.: 11122233344 -> 111.***.***-44"""
    if not doc:
        return ''
    s = ''.join(ch for ch in str(doc) if ch.isdigit())
    l = len(s)
    if l == 11:  # CPF
        return f"{s[0:3]}.{s[3:6]}.***-{s[-2:]}"
    if l == 14:  # CNPJ
        return f"{s[0:2]}.{s[2:5]}.***./{s[8:12]}-{s[-2:]}" 
    # máscara informativa
    # caso genérico, preserva primeiros e últimos
    if l <= 4:
        return '*' * l
    return s[0:2] + '*' * (l - 4) + s[-2:]


def _mask_phone(phone: str) -> str:
    if not phone:
        return ''
    s = ''.join(ch for ch in str(phone) if ch.isdigit())
    l = len(s)
    if l <= 4:
        return '*' * l
    # mostra últimos 4 dígitos
    return '*' * (l - 4) + s[-4:]


# ==================
# Validação de Números
# ==================
def apenas_numeros(valor: str):
    """Remove tudo que não for dígito e retorna só os números."""
    if not valor:
        return ''
    return ''.join(ch for ch in str(valor) if ch.isdigit())


def parece_email(valor: str):
    """Checa de forma simples se o valor parece um e-mail."""
    if not valor:
        return False
    v = valor.strip()
    return ('@' in v) and ('.' in v.split('@')[-1])


def detectar_tipo_por_numeros(numeros: str):
    """
    Decide se a string numérica é CPF (11 dígitos) ou CNPJ (14 dígitos).
    Retorna 'cpf', 'cnpj' ou None.
    """
    if not numeros:
        return None
    l = len(numeros)
    if l == 11:
        return 'cpf'
    if l == 14:
        return 'cnpj'
    return None


def esta_ativo(valor): # TALVEZ mudar
    """Normaliza campo ativo (0/1/bool/str) para booleano."""
    if valor is None:
        return True  # se não houver campo, assumimos ativo
    # tratar ints
    if isinstance(valor, int):
        return bool(valor)
    # tratar strings como '0'/'1'/'true'/'false'
    if isinstance(valor, str):
        v = valor.strip().lower()
        if v in ('0', 'false', 'f', 'no', 'n'):
            return False
        return True
    # tratar booleans
    return bool(valor)


# ==================
# Validação Conta (Substituir por API)
# ==================
def validar_cpf(cpf: str):
    """
    Valida CPF checando os dois dígitos verificadores.
    cpf: string com apenas dígitos (11 chars).
    """
    if not cpf or len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc_dig(nums):
        soma = 0
        for i, n in enumerate(nums, start=2):
            soma += int(n) * (len(nums) + 2 - i)
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    # primeiros 9 dígitos
    n1 = cpf[:9]
    d1 = calc_dig(n1)
    d2 = calc_dig(n1 + d1)
    return cpf[-2:] == d1 + d2


def validar_cnpj(cnpj: str):
    """
    Valida CNPJ localmente checando os dígitos verificadores.
    - cnpj: string contendo APENAS dígitos (deve usar apenas_numeros antes).
    Retorna True se válido, False se inválido.
    """
    if not cnpj:
        return False

    # garante string e só dígitos
    c = ''.join(ch for ch in str(cnpj) if ch.isdigit())

    # tem que ter 14 dígitos
    if len(c) != 14:
        return False

    # rejeitar sequências óbvias (todos iguais)
    if c == c[0] * 14:
        return False

    def calcula_digito(base: str):
        """Calcula um dígito verificador (retorna str) dado a base (12 ou 13 dígitos)."""
        pesos = [6,5,4,3,2,9,8,7,6,5,4,3,2]
        # pesos para 13 posições (usamos slice)
        soma = 0
        # alinhamos pesos à direita da base
        inicio = len(pesos) - len(base)
        for i, dig in enumerate(base):
            soma += int(dig) * pesos[inicio + i]
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    # primeiros 12 dígitos
    base12 = c[:12]
    d1 = calcula_digito(base12)
    d2 = calcula_digito(base12 + d1)

    return c[-2:] == (d1 + d2)


# ==================
# Edição de Perfil
# ==================
# Se existe email
def email_existe(
    email: str,
    exclude_user_id: Optional[int] = None,
    modelos: Optional[List[Type]] = None):
    """
    Verifica se um e-mail já existe nas tabelas informadas.
    - exclude_user_id: se fornecido, ignora um usuário com esse id (aplicável quando checando Usuario)
    - modelos: lista de modelos SQLAlchemy a verificar. Se None, verifica [ClienteCPF, ClienteCNPJ, PrestadorServico, Usuario].

    Retorna True se o e-mail já existir em alguma tabela (exceto o usuário excluído), senão False.
    """
    if not email:
        return False
    email_norm = email.strip().lower() #email@emai.com

    if modelos is None:
        modelos = [ClienteCPF, ClienteCNPJ, PrestadorServico, Usuario]

    for modelo in modelos:
        # pular modelos que não tenham atributo 'email'
        if not hasattr(modelo, 'email'):
            continue

        # constrói a query (comparação case-insensitive)
        coluna = getattr(modelo, 'email')
        q = modelo.query.filter(func.lower(coluna) == email_norm)

        # se o modelo for Usuario e existe exclude_user_id, aplicar filtro
        if modelo is Usuario and exclude_user_id:
            q = q.filter(modelo.id != exclude_user_id)

        # usar exists() para ser eficiente
        exists = bancodedados.session.query(q.exists()).scalar()
        if exists:
            return True

    return False


def trocar_imagem_usuario(usuario, file_storage, prefix='user'):
    """
    Salva a nova imagem e apaga a antiga (se não for default.jpg).
    Retorna nome_salvo (string) ou None.
    """
    try:
        saved_name, _thumb = salvar_imagem(file_storage, folder='perfil', prefix=f"{prefix}{usuario.id}", gerar_thumb=False)
        # apagar antiga (preservando default.jpg)
        apagar_imagem_arquivo(usuario.foto_perfil, folder='perfil')
        usuario.foto_perfil = saved_name
        return saved_name
    except Exception:
        current_app.logger.exception("Erro ao salvar imagem do usuário")
        return None