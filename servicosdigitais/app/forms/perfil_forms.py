# ========================
# Formulário de Perfil
# ========================
from flask_wtf import FlaskForm
from flask_wtf.file import (
    FileField, FileAllowed
    )
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField
    )
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, Optional
    )

# ================================
# Base Editar Perfil
# ================================
class _BaseEditarPerfil(FlaskForm):
    """
        Formulário base para edição de perfil.
        Campos comuns a todos os tipos de usuário.
    """

    # ==========================
    # FOTO DE PERFIL
    # ==========================
    foto_perfil = FileField('Foto / Logo (opcional)', validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Formato de imagem inválido.')
            ])

    # ==========================
    # DADOS DE CONTATO
    # ==========================
    email = StringField('E-mail', validators=[
                                    DataRequired(),
                                    Email()
                                    ])

    telefone = StringField('Telefone', validators=[
                                    Optional(), Length(min=8, max=20)])

    # ==========================
    # ALTERAÇÃO DE SENHA
    # ==========================
    nova_senha = PasswordField('Nova senha', validators=[
            Optional(),
            Length(min=6, max=64, message='A nova senha deve ter no mínimo 6 caracteres.')
            ])

    confirmacao_senha = PasswordField('Confirmar nova senha', validators=[
                    Optional(),
                    EqualTo('nova_senha', message='As senhas devem coincidir.')
                    ])

    botao_submit = SubmitField('Salvar alterações')


# ================================
# Editar Perfil — CPF
# ================================
class FormEditarCPF(_BaseEditarPerfil):

    nome = StringField('Nome', validators=[
                                DataRequired(),
                                Length(max=100)
                                ])

    sobrenome = StringField('Sobrenome', validators=[
                                        Optional(),
                                        Length(max=100)
                                        ])


# ================================
# Editar Perfil — CNPJ
# ================================
class FormEditarCNPJ(_BaseEditarPerfil):

    razao_social = StringField('Razão Social', validators=[
                                            DataRequired(),
                                            Length(max=200)
                                            ])

# ================================
# Editar Perfil — Prestador
# ================================
class FormEditarPrestador(_BaseEditarPerfil):

    nome_empresa = StringField('Nome / Fantasia', validators=[
                                                DataRequired(),
                                                Length(max=150)
                                                ])
    descricao = TextAreaField('Descrição curta', validators=[
                                                Optional(),
                                                Length(max=600)
                                                ])

'''
Mas futuramente pode entrar aqui:

trocar senha
alterar e-mail
upload de foto (se não estiver em outro form)
excluir conta (form simples de confirmação)
'''