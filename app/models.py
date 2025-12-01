# models.py (trecho principal modificado)
from servicosdigitais.app import bancodedados, login_manager, bcrypt
from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy import func
import secrets


@login_manager.user_loader
def load_usuario(data):
    """
    Carrega o usuário correto baseado no tipo e ID salvos na sessão.
    Espera algo como: "usuario:5", "cpf:10", "cnpj:3", "prestador:7"
    """
    if not data:
        return None

    try:
        tipo, user_id = data.split(":")
        user_id = int(user_id)
    except:
        return None

    if tipo == "usuario":
        return Usuario.query.get(user_id)
    elif tipo == "cpf":
        return ClienteCPF.query.get(user_id)
    elif tipo == "cnpj":
        return ClienteCNPJ.query.get(user_id)
    elif tipo == "prestador":
        return PrestadorServico.query.get(user_id)

    return None

# ===========================
# Tabela Usuario e subclasses
# ===========================
# - id, nome, sobrenome, telefone, email, senha_hash, foto_perfil, tipo, created_at, ativo
class Usuario(bancodedados.Model, UserMixin):

    __tablename__ = "usuario"

    id = bancodedados.Column(bancodedados.Integer, primary_key=True, autoincrement=True)
    nome = bancodedados.Column(bancodedados.String(100), nullable=False)
    sobrenome = bancodedados.Column(bancodedados.String(100), nullable=True) 
    telefone = bancodedados.Column(bancodedados.String(20), nullable=True)
    email = bancodedados.Column(bancodedados.String(100), nullable=False, index=True)
    senha_hash = bancodedados.Column(bancodedados.String(200), nullable=False)
    foto_perfil = bancodedados.Column(bancodedados.String(200), default='default.jpg')

    # 'cliente_cpf', 'cliente_cnpj', 'prestador'
    tipo = bancodedados.Column(bancodedados.String(20), nullable=False)

    # ====== SEGURANÇA ======

    ocultar_dados = bancodedados.Column(bancodedados.Boolean, default=False, nullable=False)
    # contador de tentativas de senha falhas
    tentativas_falhas = bancodedados.Column(bancodedados.Integer, default=0, nullable=False)
    # timestamp da última tentativa falha
    ultima_falha = bancodedados.Column(bancodedados.DateTime(timezone=True), nullable=True)
    # se definido e > agora => conta bloqueada até esse horário
    bloqueado_ate = bancodedados.Column(bancodedados.DateTime(timezone=True), nullable=True)
    # 1=ativo, 0=desativado
    ativo = bancodedados.Column(bancodedados.Boolean, default=True, nullable=False)
    # Se o usuário é administrador
    is_admin = bancodedados.Column(bancodedados.Boolean, default=False, nullable=False)
# Criação da conta
    created_at = bancodedados.Column(
        bancodedados.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )


    # Pegar o ID pois pode ter nomes iguais
    def get_id(self):
        return f"usuario:{self.id}"


    # Criptografação da senha
    def set_senha(self, raw_password):
        hashed = bcrypt.generate_password_hash(raw_password)
        if isinstance(hashed, (bytes, bytearray)):
            hashed = hashed.decode('utf-8')
        self.senha_hash = hashed


    # Verificar senha no login (True ou False)
    def checar_senha(self, raw_password):
        return bcrypt.check_password_hash(self.senha_hash, raw_password)


# ========================================
# Tabela ClienteCPF - Subclasse de Usuario
# ========================================
# - id (FK), cpf
class ClienteCPF(Usuario):
    __tablename__ = "cliente_cpf"

    id = bancodedados.Column(
        bancodedados.Integer,
        bancodedados.ForeignKey("usuario.id"),
        primary_key=True
    )

    cpf = bancodedados.Column(bancodedados.String(11), unique=True, index=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tipo = "cpf" # Tipo automático


    # Campos herdados: nome, sobrenome, telefone, email, senha_hash, tipo, foto_perfil, ativo
    # Métodos herdados: get_id, set_senha, checar_senha


# =========================================
# Tabela ClienteCNPJ - Subclasse de Usuario
# =========================================
# - id (FK), razao_social, cnpj
class ClienteCNPJ(Usuario):
    __tablename__ = "cliente_cnpj"

    id = bancodedados.Column(
        bancodedados.Integer,
        bancodedados.ForeignKey("usuario.id"),
        primary_key=True
    )

    razao_social = bancodedados.Column(bancodedados.String(200), nullable=False)
    cnpj = bancodedados.Column(bancodedados.Integer, nullable=False, unique=True, index=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tipo = "cnpj" # Tipo automático

    # Herdado: nome, telefone, email, senha_hash, tipo, foto_perfil, ativo
    # Métodos herdados: get_id, set_senha, checar_senha


# ==============================================
# Tabela PrestadorServico - Subclasse de Usuario
# ==============================================
# - id (FK), especialidade, cnpj
class PrestadorServico(Usuario):
    __tablename__ = "prestador_servico"

    id = bancodedados.Column(
        bancodedados.Integer,
        bancodedados.ForeignKey("usuario.id"),
        primary_key=True
    )

    especialidade = bancodedados.Column(bancodedados.String(120), nullable=True)

    cnpj = bancodedados.Column(bancodedados.Integer, nullable=False, unique=True, index=True)
    # relacionamento PARA a tabela de serviços
    servicos = bancodedados.relationship(
        "ServicoPrestado",
        back_populates="prestador",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tipo = "prestador" # Tipo automático

    # Herdado: nome, telefone, email, senha_hash, tipo, foto_perfil, ativo
    # Métodos herdados: get_id, set_senha, checar_senha


# ======================
# Tabela ServicoPrestado
# ======================
# - id, nome_servico, preco_servico, descricao, criado_em, prestador_id (FK)
class ServicoPrestado(bancodedados.Model):
    __tablename__ = "servico_prestado"

    id = bancodedados.Column(bancodedados.Integer, primary_key=True, autoincrement=True)

    nome_servico = bancodedados.Column(bancodedados.String(150), nullable=False, index=True)
    preco_servico = bancodedados.Column(bancodedados.Numeric(10, 2), nullable=False, default=0)
    descricao = bancodedados.Column(bancodedados.Text, nullable=True)
    criado_em = bancodedados.Column(
        bancodedados.datetime(timezone.now),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # FK para a tabela prestador_servico (cada serviço pertence a um prestador)
    prestador_id = bancodedados.Column(
        bancodedados.Integer,
        bancodedados.ForeignKey('prestador_servico.id'),
        nullable=False,
        index=True
    )

    # relacionamento com PrestadorServico (back_populates deve bater com o nome em PrestadorServico)
    prestador = bancodedados.relationship('PrestadorServico', back_populates='servicos')


# ================================
# Tabela Fornecedor - Subclasse de Usuario
# ================================
class Fornecedor(Usuario):
    __tablename__ = "fornecedor"

    id = bancodedados.Column(
        bancodedados.Integer,
        bancodedados.ForeignKey("usuario.id"),
        primary_key=True
    )

    razao_social = bancodedados.Column(bancodedados.String(200), nullable=False)
    nome_fantasia = bancodedados.Column(bancodedados.String(200), nullable=False)

    cnpj = bancodedados.Column(
        bancodedados.String(18),
        nullable=False,
        unique=True,
        index=True
    )

    # Herdado: nome (não será usado), email, senha_hash, tipo, foto_perfil, ativo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tipo = "fornecedor"  # AUTOMÁTICO


# =================
# Tabela FotoPerfil
# =================
# - id, usuario_id (FK), nome_arquivo, carregado_em
class FotoPerfil(bancodedados.Model):
    __tablename__ = "foto_perfil"

    id = bancodedados.Column(bancodedados.Integer, primary_key=True, autoincrement=True)
    usuario_id = bancodedados.Column(
        bancodedados.Integer,
        bancodedados.ForeignKey('usuario.id'),
        nullable=False,
        unique=True,
        index=True
    )
    nome_arquivo = bancodedados.Column(bancodedados.String(200), nullable=False)

    carregado_em = bancodedados.Column(
        bancodedados.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # relacionamento com Usuario
    usuario = bancodedados.relationship('Usuario', backref=bancodedados.backref('foto_perfil_rel', uselist=False))


# ==============================
# Tabela Textos de Página do Site
# ==============================
# Mudar os textos da página de entrada (depois todas as páginas)
class TextosEntrada(bancodedados.Model):
    __tablename__ = "textos_entrada"

    id = bancodedados.Column(bancodedados.Integer, primary_key=True, autoincrement=True)
    titulo = bancodedados.Column(bancodedados.String(200), nullable=False)
    corpo_texto = bancodedados.Column(bancodedados.Text, nullable=False)

    criado_em = bancodedados.Column(
        bancodedados.datetime(timezone.now),
        server_default=func.now(),
        nullable=False,
        index=True
    )


# ======================
# Tabela Textos de Login
# ======================
# Mudar os texto para login e cadastro
class TextoLogin(bancodedados.Model):
    __tablename__ = "texto_login"

    id = bancodedados.Column(bancodedados.Integer, primary_key=True, autoincrement=True)
    titulo = bancodedados.Column(bancodedados.String(200), nullable=False)
    corpo_texto = bancodedados.Column(bancodedados.Text, nullable=False)

    criado_em = bancodedados.Column(
        bancodedados.datetime(timezone.now),
        server_default=func.now(),
        nullable=False,
        index=True
    )


# ======================
# Tabela Imagens do Site
# ======================
# Mostrar as imagens do site
class ImagensSite(bancodedados.Model):
    __tablename__ = "imagens"

    id = bancodedados.Column(bancodedados.Integer, primary_key=True, autoincrement=True)
    nome_arquivo = bancodedados.Column(bancodedados.String(200), nullable=False)
    descricao = bancodedados.Column(bancodedados.String(300), nullable=True)

    carregado_em = bancodedados.Column(
        bancodedados.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )


# ======================
# Tabela Suporte
# ======================
class SupportTicket(bancodedados.Model):
    __tablename__ = 'support_tickets'

    id = bancodedados.Column(bancodedados.Integer, primary_key=True)
    nome = bancodedados.Column(bancodedados.String(120), nullable=True)
    email = bancodedados.Column(bancodedados.String(180), nullable=True, index=True)
    assunto = bancodedados.Column(bancodedados.String(60), nullable=False)
    mensagem = bancodedados.Column(bancodedados.Text, nullable=False)
    criado_em = bancodedados.Column(bancodedados.DateTime, default=datetime.now(timezone.utc), nullable=False)

    status = bancodedados.Column(bancodedados.String(30), default='novo', nullable=False)  # exemplo: novo, em_progresso, resolvido
    token_prioridade = bancodedados.Column(bancodedados.String(64), nullable=True, index=True)
    prioridade = bancodedados.Column(bancodedados.Integer, default=0)  # usa se quiser priorizar
    
    resposta = bancodedados.Column(bancodedados.Text, nullable=True)
    respondido_em = bancodedados.Column(bancodedados.DateTime, nullable=True)
    responsavel_id = bancodedados.Column(bancodedados.Integer, nullable=True)

    def gerar_token(self, size=8):
        # token URL-safe curto
        token = secrets.token_urlsafe(size)
        self.token_prioridade = token
        return token