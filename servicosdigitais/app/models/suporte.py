# ========================
# Banco de dados - Suporte
# ========================
from servicosdigitais.app.extensoes import bancodedados
from datetime import datetime, timezone
from sqlalchemy import func
import secrets


# ======================
# Tabela Suporte
# ======================
class SupportTicket(bancodedados.Model):
    __tablename__ = 'support_tickets'

    id = bancodedados.Column(bancodedados.Integer, primary_key=True)

    # Quem enviou (opcional)
    usuario_id = bancodedados.Column(bancodedados.Integer, nullable=True)
    nome = bancodedados.Column(bancodedados.String(120), nullable=True)
    email = bancodedados.Column(bancodedados.String(180), nullable=True, index=True)

    # Conteúdo
    tipo = bancodedados.Column(bancodedados.String(30), nullable=False)
    assunto = bancodedados.Column(bancodedados.String(200), nullable=False)
    mensagem = bancodedados.Column(bancodedados.Text, nullable=False)

    # Controle
    status = bancodedados.Column(
        bancodedados.String(30),
        default='novo',
        nullable=False,
        index=True
    )

    prioridade = bancodedados.Column(
        bancodedados.Integer,
        default=0,
        nullable=False
    )

    token_prioridade = bancodedados.Column(
        bancodedados.String(64),
        nullable=True,
        index=True
    )

    # Resposta admin
    resposta = bancodedados.Column(bancodedados.Text, nullable=True)
    respondido_em = bancodedados.Column(bancodedados.DateTime, nullable=True)
    responsavel_id = bancodedados.Column(bancodedados.Integer, nullable=True)

    criado_em = bancodedados.Column(
        bancodedados.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    def gerar_token_prioridade(self, tamanho=8):
        """
        Gera token curto para identificação ou priorização do chamado.
        """
        token = secrets.token_urlsafe(tamanho)
        self.token_prioridade = token
        return token
