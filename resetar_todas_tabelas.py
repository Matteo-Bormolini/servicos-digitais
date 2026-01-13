"""
RESET CONTROLADO DE TODAS AS TABELAS DO PROJETO

- Apaga todas as tabelas existentes
- Cria novamente TODAS com base nos models
- Usar APENAS agora para alinhar o banco
"""

from servicosdigitais.app import criar_app
from servicosdigitais.app.extensoes import bancodedados

# IMPORTANTE: importa TODOS os models
from servicosdigitais.app.models import *  # noqa

# cria a aplicação
app = criar_app()

with app.app_context():
    print("Removendo todas as tabelas...")
    bancodedados.drop_all()

    print("Criando todas as tabelas...")
    bancodedados.create_all()

    print("BANCO DE DADOS RECRIADO COM SUCESSO.")
