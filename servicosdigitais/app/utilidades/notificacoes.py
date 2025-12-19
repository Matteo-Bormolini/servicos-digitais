import smtplib
from email.message import EmailMessage
from flask import current_app
import secrets


def gerar_token_prioridade(nbytes=6):
    # Gera token curto
    return secrets.token_urlsafe(nbytes)


def enviar_email_smtp(destinatarios, assunto, corpo_texto, corpo_html=None, remetente=None):
    """
    Envia email via SMTP simples. Usa config do app (MAIL_*).
    destinatarios: list[str]
    corpo_html opcional
    """
    mail_server = current_app.config.get('MAIL_SERVER')
    if not mail_server:
        current_app.logger.warning("Envio de e-mail desabilitado: MAIL_SERVER não configurado")
        return False, "Mail disabled"

    msg = EmailMessage()
    msg['Subject'] = assunto # alterar
    msg['From'] = remetente or current_app.config.get('MAIL_DEFAULT_SENDER')
    msg['To'] = ', '.join(destinatarios)
    msg.set_content(corpo_texto)
    if corpo_html:
        msg.add_alternative(corpo_html, subtype='html')

    smtp_user = current_app.config.get('MAIL_USERNAME')
    smtp_pass = current_app.config.get('MAIL_PASSWORD')
    smtp_port = current_app.config.get('MAIL_PORT', 587)
    use_tls = current_app.config.get('MAIL_USE_TLS', True)

    try:
        server = smtplib.SMTP(mail_server, smtp_port, timeout=10)
        if use_tls:
            server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True, None
    except Exception as e:
        current_app.logger.exception("Falha ao enviar e-mail de suporte: %s", e)
        return False, str(e)
