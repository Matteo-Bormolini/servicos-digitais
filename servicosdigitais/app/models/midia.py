# ========================
# Banco de dados - Fotos de Perfil
# ========================
from servicosdigitais.app.extensoes import bancodedados
from sqlalchemy import func

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
