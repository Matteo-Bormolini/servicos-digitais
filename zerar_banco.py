from servicosdigitais.app import criar_app, bancodedados

# cria o app
app = criar_app()

# entra no contexto da aplicação
with app.app_context():
    bancodedados.drop_all()
    bancodedados.create_all()
    print("Banco resetado!")
