# ========================
# ENVIO DE E-MAILS
# ========================

def enviar_email_senha_temporaria(email_destino, nome_usuario, senha):
    """
    Envia e-mail com senha temporária após reset administrativo.
    """

    assunto = "Redefinição de senha - Serviços Digitais"

    corpo = f"""
Olá, {nome_usuario}.

Sua senha foi redefinida pelo suporte do sistema.

Senha temporária:
{senha}

Por segurança, altere sua senha imediatamente após o login.

Atenciosamente,
Equipe Serviços Digitais
"""

    # Aqui você conecta com o seu serviço real de envio
    # Exemplo:
    # send_email(email_destino, assunto, corpo)

    print("EMAIL ENVIADO")
    print("Para:", email_destino)
    print(corpo)
