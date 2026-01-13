"""
Script para verificar quais tabelas existem no banco SQLite
Usa exatamente a mesma configuração da aplicação Flask
"""

from servicosdigitais.app import criar_app
from sqlalchemy import inspect

# cria a aplicação
aplicacao = criar_app()

with aplicacao.app_context():
    engine = aplicacao.extensions["sqlalchemy"].engine
    inspetor = inspect(engine)

    tabelas = inspetor.get_table_names()

    print("\nTabelas encontradas no banco:")
    for tabela in tabelas:
        print("-", tabela)
