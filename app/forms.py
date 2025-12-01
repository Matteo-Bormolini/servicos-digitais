'''
forms -> TODOS Formulários de criação (conta, login, ...)

Para ser mais direto -> O forms são todos formulários do site.
'''
# Criar tabelas do banco de dados:
# tabela: localizacao
# colunas: país | estado | municipio | cidade | bairro |

# tabela: TextosEntrada
# colunas: textos_entrada | texto_cadastro |

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user

from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    TextAreaField, FloatField, SelectField
    )
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError, Optional
    )

from servicosdigitais.app.seguranca import email_existe, senha_segura
from servicosdigitais.app.models import (
    Usuario, ClienteCPF, PrestadorServico, ClienteCNPJ
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


# ========================
# Formulário de Cadastros
# ========================
# Formulário de Cadastro CPF
# - Nome, Sobrenome, CPF, Telefone, Email, Senha, Confirmação de Senha
class FormCadastroCPF(FlaskForm):
    foto_perfil = FileField('Foto (opcional)', validators=[FileAllowed(['jpg','jpeg','png'])])
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


# Formulário de Cadastro Prestador
# - Nome Fantasia, CNPJ, Telefone, Especialidade, Email, Senha, Confirmação de Senha
class FormCadastroPrestador(FlaskForm):
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


# Formulário de Cadastro CNPJ
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


# Formulário de Cadastro de Serviço
# Nome (do/s Serviço/s), preco, descricao (multiplos serviços em um Id são aceitos)
class FormCadastroServico(FlaskForm):
    nome = StringField("Nome do serviço", validators=[DataRequired(), Length(max=100)])
    preco = FloatField("Preço", validators=[DataRequired()])
    descricao = TextAreaField("Descrição", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Cadastrar Serviço")


# ================================
# Formulário de Editar Perfil
# ================================
class _BaseEditarPerfil(FlaskForm):
    foto_perfil = FileField('Foto/Logo (opcional)', validators=[Optional(), FileAllowed(['jpg','jpeg','png','webp'])])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    telefone = StringField('Telefone', validators=[Optional(), Length(min=8, max=20)])
    senha_atual = PasswordField('Senha atual (necessária para alterar senha)', validators=[Optional()])
    senha_nova = PasswordField('Nova senha', validators=[Optional(), Length(min=6, max=64)])
    confirmacao_senha = PasswordField('Confirmar nova senha', validators=[Optional(), EqualTo('senha_nova', message='As senhas devem coincidir')])
    botao_submit = SubmitField('Salvar alterações')


# Editar perfil para CPF
class FormEditarCPF(_BaseEditarPerfil):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    sobrenome = StringField('Sobrenome', validators=[Optional(), Length(max=100)])


# Editar perfil para CNPJ
class FormEditarCNPJ(_BaseEditarPerfil):
    razao_social = StringField('Razão Social', validators=[DataRequired(), Length(max=200)])


# Editar perfil para Prestador
class FormEditarPrestador(_BaseEditarPerfil):
    nome_empresa = StringField('Nome / Fantasia', validators=[DataRequired(), Length(max=150)])
    descricao = TextAreaField('Descrição curta', validators=[Optional(), Length(max=600)])
    # para gerenciar serviços recomendamos rota separada /meus_servicos



class FormSupport(FlaskForm):
    """
    Formulário simples de suporte (usamos FlaskForm para CSRF + validação).
    Campos fáceis de estender/modificar.
    """
    nome = StringField('Nome (opcional)', validators=[Optional(), Length(max=120)])
    email = StringField('E-mail (opcional)', validators=[Optional(), Email(), Length(max=120)])
    assunto = SelectField('Assunto', choices=[
        ('erro', 'Erro na plataforma'),
        ('duvida', 'Dúvida / Uso'),
        ('sugestao', 'Sugestão'),
        ('outro', 'Outro')
    ], validators=[DataRequired()])
    mensagem = TextAreaField('Mensagem', validators=[DataRequired(), Length(min=10, max=5000)])

# Validadores Comuns
# DataRequired - O campo de usuário não pode estar vazio;
# Length - Tem que ter um limite mínimo e máximo de caracteres;
# Email - Verifica se o formato do email está correto;
# EqualTo - Verifica se dois campos são iguais (útil para confirmação de senha).