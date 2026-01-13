# textos padrão
# ========================
# TEMPLATES DE E-MAIL
# ========================

def email_reset_senha(nome_usuario, senha_temporaria):
    """
    Template de e-mail para reset de senha.
    """

    assunto = "Redefinição de senha - Serviços Digitais"

    corpo = f"""
Olá, {nome_usuario}.

Sua senha foi redefinida pelo suporte do sistema.

Senha temporária:
{senha_temporaria}

Por segurança, altere sua senha imediatamente após o login.

Se você não solicitou essa ação, entre em contato com o suporte.

Atenciosamente,
Equipe Serviços Digitais
"""

    return assunto, corpo
