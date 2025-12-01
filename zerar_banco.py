from servicosdigitais.app import app, bancodedados
from servicosdigitais.app.models import *

with app.app_context():
    bancodedados.drop_all()
    bancodedados.create_all()
    print("Banco resetado!")
