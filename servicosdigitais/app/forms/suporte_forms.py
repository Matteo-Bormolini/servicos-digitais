# ========================
# Formulário de Suporte
# ========================

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField
    )
from wtforms.validators import (
    DataRequired, Length, Email, Optional
    )

class FormSuporte(FlaskForm):
    """
    Formulário de contato/suporte.
    Pode ser usado por usuários autenticados ou visitantes.
    """

    nome = StringField(
        'Nome (opcional)',
        validators=[Optional(), Length(max=120)]
    )

    email = StringField(
        'E-mail (opcional)',
        validators=[Optional(), Email(), Length(max=120)]
    )

    tipo = SelectField(
        'Tipo',
        choices=[
            ('elogio', 'Elogio'),
            ('duvida', 'Dúvida'),
            ('sugestao', 'Sugestão'),
            ('critica', 'Crítica'),
            ('erro', 'Erro na plataforma')
        ],
        validators=[DataRequired()]
    )

    assunto = StringField(
        'Assunto',
        validators=[DataRequired(), Length(max=200)]
    )

    mensagem = TextAreaField(
        'Mensagem',
        validators=[DataRequired(), Length(min=10, max=5000)]
    )
