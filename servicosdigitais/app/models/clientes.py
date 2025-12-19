# ========================
# Banco de dados - Clientes
# ========================
from servicosdigitais.app.models.usuario import Usuario
from servicosdigitais.app.extensoes import bancodedados

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