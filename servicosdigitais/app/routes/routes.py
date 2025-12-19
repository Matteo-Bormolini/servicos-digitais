







#
# -------------------------
# Avaliações
# -------------------------
'''
@bp.route('/avaliar/<int:prestador_id>', methods=['POST'])
@login_required
def avaliar(prestador_id):
    nota = int(request.form.get('nota', 5))
    comentario = request.form.get('comentario', '')
    aval = Avaliacao(
        usuario_id=current_user.id,
        prestador_id=prestador_id,
        nota=nota,
        comentario=comentario,
        created_at=datetime.now(timezone.utc)
    )
    bancodedados.session.add(aval)
    bancodedados.session.commit()
    flash("Avaliação enviada. Obrigado!", "alert-success")
    return redirect(url_for('ver_prestador', prestador_id=prestador_id))

'''

# -------------------------
# Uploads estáticos (se necessário)
# -------------------------
'''
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    pasta = os.path.join(current_app.root_path, 'static/fotos_perfil', 'uploads')
    return send_from_directory(pasta, filename)
'''

# -------------------------
# Busca simples / filtros
# -------------------------
'''
@bp.route('/buscar')
def buscar():
    termo = request.args.get('q', '').strip()
    prestadores = []
    if termo:
        prestadores = PrestadorServico.query.filter(
            PrestadorServico.nome.ilike(f'%{termo}%') | PrestadorServico.descricao.ilike(f'%{termo}%')
        ).all()
    return render_template('buscar.html', prestadores=prestadores, termo=termo)
'''

# -------------------------
# Erros
# -------------------------
'''
@bp.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('404.html'), 404


@bp.errorhandler(500)
def erro_servidor(e):
    bancodedados.session.rollback()
    return render_template('500.html'), 500

'''
# -------------------------
# Utilitários e comandos extra
# -------------------------
'''
@bp.route('/meu_dashboard')
@login_required
def dashboard_usuario():
    """
    Página inicial do usuário logado (diferenciar por tipo: admin, prestador, cliente).
    """
    if getattr(current_user, 'tipo', None) == 'admin':
        return redirect(url_for('admin_home'))
    if getattr(current_user, 'tipo', None) == 'prestador':
        # carregar dados do prestador
        prest = PrestadorServico.query.filter_by(usuario_id=current_user.id).first()
        servicos = ServicoPrestado.query.filter_by(prestador_id=prest.id).all() if prest else []
        return render_template('dashboard_prestador.html', prestador=prest, servicos=servicos)
    # cliente
    return render_template('dashboard_cliente.html')
'''

# -------------------------
# Fim do arquivo
# -------------------------