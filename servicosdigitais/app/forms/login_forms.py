# ========================
# Formulário de Login e Recuperação de Senha
# ========================
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField
    )
from wtforms.validators import (
    DataRequired, Length
    )

# ========================
# Formulário de Login
# ========================
# email|cpf|cnpj igual a tabla Usuario.email - Se existir, pegar o email ou cpf ou cnpj da tabela Usuario
class FormLogin(FlaskForm):
    email = StringField('E-mail, CPF ou CNPJ', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit = SubmitField('Fazer Login')


'''Alterar o código de recuperação de senha'''
# ========================
# Formulário de Recuperação de Senha
# ========================
class FormRecuperarSenha(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Length(min=6, max=50)])
    botao_submit = SubmitField('Enviar E-mail de Recuperação')  