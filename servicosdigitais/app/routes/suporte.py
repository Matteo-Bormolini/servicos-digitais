# ========================
# Routes - Página Suporte
# ========================

''' O que tem dentro da página de suporte:
- Formulário de contato/suporte (FormSuporte)
- Contatos de suporte (e-mail, telefone, WhatsApp) vindos do banco de dados (model Contact)
- Ao enviar o formulário:
    - Tenta salvar um SupportTicket no banco de dados
    - Se falhar, grava em um arquivo de log na instância
    - Envia um e-mail para a equipe de suporte com os detalhes
    - Se o usuário estiver autenticado e fornecer um e-mail, gera um token de prioridade e envia para o usuário
    - Usa session para armazenar o resultado e mostrar um popup/flash na próxima renderização da página 
'''

from flask import (
    Blueprint ,render_template, flash, redirect, url_for, current_app, session
    )
from flask_login import current_user
from datetime import datetime, timezone
import os
from servicosdigitais.app import  bancodedados
from servicosdigitais.app.utilidades.notificacoes import enviar_email_smtp
from servicosdigitais.app.forms.suporte_forms import FormSuporte


# Criação do Blueprint
suporte_bp = Blueprint(
    "suporte",
    __name__,
    template_folder="templates"
)

@suporte_bp.route('/suporte', methods=['GET', 'POST'])
def suporte():
    form = FormSuporte()
    try:
        contatos = None
        from servicosdigitais.app.models import Contact
        contatos = Contact.query.order_by(Contact.ordem).all()
        contatos_emails = [(c.valor, c.nome) for c in contatos if c.tipo == 'email']
        contatos_telefones = [(c.valor, c.nome) for c in contatos if c.tipo == 'telefone']
        contatos_whatsapp = [(c.valor, c.nome) for c in contatos if c.tipo == 'whatsapp']
    except Exception:
        contatos_emails = [('emailum@enderco.com', 'Suporte')]
        contatos_telefones = [('(19) 9 8265-6051', 'Matteo')]
        contatos_whatsapp = contatos_telefones

    if form.validate_on_submit():
        nome = form.nome.data.strip() if form.nome.data else None
        email = form.email.data.strip().lower() if form.email.data else None
        assunto = form.assunto.data
        mensagem = form.mensagem.data.strip()
        criado_em_iso = datetime.now(timezone.utc).isoformat()

        # payload para salvar/log
        payload = {
            'nome': nome,
            'email': email,
            'assunto': assunto,
            'mensagem': mensagem,
            'criado_em': criado_em_iso
        }

        ticket_id = None
        token_gerado = None
        try:
            # tenta usar model SupportTicket
            from servicosdigitais.app.models import SupportTicket
            ticket = SupportTicket(
                nome=nome,
                email=email,
                assunto=assunto,
                mensagem=mensagem,
                criado_em=datetime.now(timezone.utc)
            )

            # se usuário autenticado e email presente, gera token de prioridade
            if current_user.is_authenticated and email:
                token_gerado = ticket.gerar_token(size=6)  # salva no objeto
            bancodedados.session.add(ticket)
            bancodedados.session.commit()
            ticket_id = ticket.id
            current_app.logger.info("Support ticket saved id=%s", ticket_id)
        except Exception as e:
            bancodedados.session.rollback()
            # fallback: grava em arquivo
            try:
                instance_dir = current_app.instance_path
                os.makedirs(instance_dir, exist_ok=True)
                log_path = os.path.join(instance_dir, 'suporte_logs.txt')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(f"{criado_em_iso} | {email or 'anon'} | {assunto} | {mensagem}\n")
                current_app.logger.info("Support fallback logged at %s", log_path)
            except Exception:
                current_app.logger.exception("Falha no fallback de suporte: %s", e)

        # ===== enviar email para a equipe de suporte =====
        suporte_to = [current_app.config.get('MAIL_USERNAME') or 'suporteservicosdigitais@gmail.com']
        assunto_email = f"[Suporte] {assunto}"
        corpo = f"Novo chamado de suporte:\n\nNome: {nome or 'Anonimo'}\nEmail: {email or '—'}\nAssunto: {assunto}\n\nMensagem:\n{mensagem}\n\nTicket ID: {ticket_id or 'fallback'}\nCriado em: {criado_em_iso}\n"
        enviar_ok, err = enviar_email_smtp(suporte_to, assunto_email, corpo)

        # ===== se usuário autenticado e email informado, enviar token para o cliente =====
        if token_gerado and email:
            assunto_usuario = "Seu chamado foi recebido — token de prioridade"
            corpo_user = f"Recebemos sua solicitação. Token: {token_gerado}\n\nUse esse token em futuras comunicações para priorizar seu atendimento.\n\nAtenciosamente,\nSuporte Serviços Digitais"
            enviar_ok2, err2 = enviar_email_smtp([email], assunto_usuario, corpo_user)

        # ===== preparar popup/flash com resultado =====
        # vamos usar session para manter dados após redirect (PRG)
        result = {
            'ticket_id': ticket_id,
            'email': email,
            'token': token_gerado,
            'anonimo': not bool(email)
        }
        session['support_result'] = result

        flash("Sua ocorrência foi registrada com sucesso.", "alert-success")
        if not current_app.config.get('VALIDAR_PRESTADOR', True) or not current_app.config.get('VALIDAR_CPF', True) or not current_app.config.get('VALIDAR_CNPJ', True):
            flash("MODO TESTE: operação registrada em ambiente de testes (não enviamos e-mails externos).", "alert-info")

        return redirect(url_for('suporte'))

    # GET -> renderiza. O template vai checar session['support_result'] para mostrar popup
    return render_template(
        'suporte.html',
        form=form,
        contatos_emails=contatos_emails,
        contatos_telefones=contatos_telefones,
        contatos_whatsapp=contatos_whatsapp
    )

