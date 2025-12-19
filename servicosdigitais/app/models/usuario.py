# ========================
# Banco de dados - Usuario
# ========================
from servicosdigitais.app.extensoes import bancodedados, bcrypt
from flask_login import UserMixin
from sqlalchemy import func

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