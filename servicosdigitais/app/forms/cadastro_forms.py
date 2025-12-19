# ========================
# Formulário de Cadastros
# ========================
from flask_wtf import FlaskForm
from flask_wtf.file import (
    FileField, FileAllowed
)
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField, FloatField
    )
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, Optional, ValidationError
    )
from servicosdigitais.app.utilidades.validadores import email_existe

# ========================
# Formulário de CPF
# ========================
# - Nome, Sobrenome, CPF, Telefone, Email, Senha, Confirmação de Senha
class FormCadastroCPF(FlaskForm):
    foto_perfil = FileField('Foto', validators=[FileAllowed(['jpg','jpeg','png'])])
    username = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[Optional()])
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=14)])
    telefone = StringField('Telefone', validators=[Optional(), Length(min=8, max=20)]) #apenas números
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit = SubmitField('Criar Conta CPF')

    # Validação verificar email
    def validate_email(self, field):
        if email_existe(field.data):
            raise ValidationError('Já existe conta com esse email. Cadastre-se com outro email ou faça login.')


# ========================
# Formulário de CNPJ
# ========================
# - Razão Social, CNPJ, Telefone, Email, Senha, Confirmação de Senha
class FormCadastroCNPJ(FlaskForm):
    foto_perfil = FileField('Foto/Logo Empresa', validators=[FileAllowed(['jpg','jpeg','png','webp'])])
    razao_social = StringField('Razão Social', validators=[DataRequired()])
    cnpj = StringField('CNPJ', validators=[DataRequired(), Length(min=14, max=18)])
    telefone = StringField('Telefone', validators=[Optional(), Length(min=8, max=20)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit = SubmitField('Criar Conta CNPJ')

    # Validação verificar email
    def validate_email(self, field):
        if email_existe(field.data):
            raise ValidationError('Já existe conta com esse email. Cadastre-se com outro email ou faça login.')


# ========================
# Formulário de Prestador
# ========================
# - Nome Fantasia, CNPJ, Telefone, Especialidade, Email, Senha, Confirmação de Senha
class FormCadastroPrestador(FlaskForm):
    foto_perfil = FileField('Foto', validators=[FileAllowed(['jpg','jpeg','png'])])
    username = StringField('Nome Fantasia', validators=[DataRequired()])
    cnpj = StringField('CNPJ', validators=[DataRequired(), Length(min=14, max=18)])
    telefone = StringField('Telefone', validators=[Optional(), Length(min=8, max=20)])
    especialidade = StringField('Especialidade', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit = SubmitField('Criar Conta Prestador')

    # Validação verificar email
    def validate_email(self, field):
        if email_existe(field.data):
            raise ValidationError('Já existe conta com esse email. Cadastre-se com outro email ou faça login.')


# ========================
# Formulário de Serviço
# ========================
# Nome (do/s Serviço/s), preco, descricao (multiplos serviços em um Id são aceitos)
class FormCadastroServico(FlaskForm):
    nome = StringField("Nome do serviço", validators=[DataRequired(), Length(max=100)])
    preco = FloatField("Preço", validators=[DataRequired()])
    descricao = TextAreaField("Descrição", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Cadastrar Serviço")