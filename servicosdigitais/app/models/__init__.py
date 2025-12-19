"""
Modelos do banco de dados da aplicação.

Este módulo centraliza os models para facilitar importações
e manter a organização do sistema.
"""

from .usuario import Usuario
from .clientes import ClienteCPF, ClienteCNPJ
from .prestador import PrestadorServico, ServicoPrestado
from .midia import FotoPerfil
from .conteudo import TextosEntrada, ImagensSite
from .suporte import SupportTicket



''' Não irei usar ainda no banco de dados:  
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
'''