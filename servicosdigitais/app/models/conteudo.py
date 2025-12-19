# ========================
# Banco de dados - Conteúdo do Site
# ========================
from servicosdigitais.app.extensoes import bancodedados
from sqlalchemy import func

# ==============================
# Tabela Textos de Página do Site
# ==============================
class TextosEntrada(bancodedados.Model):
    __tablename__ = "textos_entrada"

    id_texto = bancodedados.Column(
        bancodedados.Integer,
        primary_key=True,
        autoincrement=True
    )

    # Identifica onde o texto será usado (login_titulo, home_banner, etc.)
    chave = bancodedados.Column(
        bancodedados.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    titulo = bancodedados.Column(
        bancodedados.String(200),
        nullable=True
    )

    conteudo = bancodedados.Column(
        bancodedados.Text,
        nullable=False
    )

    criado_em = bancodedados.Column(
        bancodedados.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
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
