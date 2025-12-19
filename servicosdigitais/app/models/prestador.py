# ========================
# Banco de dados - Prestador de Serviço e Serviços
# ========================
from servicosdigitais.app.models.usuario import Usuario
from servicosdigitais.app.extensoes import bancodedados
from sqlalchemy import func

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
        bancodedados.DateTime(timezone=True),
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