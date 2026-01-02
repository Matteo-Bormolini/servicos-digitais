from flask_wtf import FlaskForm

class FormLogout(FlaskForm):
    """
    Formulário vazio apenas para garantir CSRF no logout
    """
    pass
