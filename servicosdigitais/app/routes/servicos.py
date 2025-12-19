# ========================
# Routes - Página Serviços
# ========================

''' O que tem dentro da Página Serviços:
- Rota '/servicos' → lista automática e alfabética de serviços (nomes únicos)
- Rota '/prestadores' → lista de prestadores de uma especialidade
- Rota '/prestador/<int:prestador_id>' → detalhes completos de um prestador
- HTML final divide a tela em 20% | 20% | 60%
- Cada rota bloqueia o acesso de usuários do tipo 'prestador'
- Tratamento de erros com logging
- Uso de SQLAlchemy para consultas ao banco de dados
- Templates Jinja2 para renderização das páginas
- Comentários explicativos em cada função
- Uso de Blueprint para organização das rotas
'''

from flask_login import current_user
from flask import (
    Blueprint, render_template, request, abort, current_app
    )

from sqlalchemy import func

from servicosdigitais.app.extensoes import bancodedados
from servicosdigitais.app.utilidades.autorizacao import bloquear_tipos
from servicosdigitais.app.models.usuario import Usuario
from servicosdigitais.app.models.prestador import PrestadorServico, ServicoPrestado


servicos_bp = Blueprint(
    "servicos",
    __name__,
    template_folder="templates",
    url_prefix=""
)

TextosEntrada = "Olá Mundo!"
Localizacao = ""

# -------------------------
# Páginas Home
# -------------------------

# rota home - ServicosDigitais
# Teóricamente foi feita 90%
@servicos_bp.route('/')
def home():
    """
    Página inicial:
    - lista textos de entrada (tabela: TextosEntrada, coluna: textos_entrada);
    - lista cidades cadastradas (tabela Localizacao, coluna: cidade);
    - lista especialidades (tabela PrestadorServico, coluna: especialidade)
    - mini-painel de sugestão para cadastro:
       - linha 1: "Você ainda não tem cadastro?"
       - linha 2: texto vindo de TextosEntrada.texto_cadastro (se existir)
       - linha 3: links para cadastro CPF, prestador e CNPJ (usando nomes de rota padrão)
    """
    texto_entrada_manual = "Olá Mundo"
    texto_cadastro_manual = "Vamos te guiar o melhor para você!"

    # ===========================
    # TEXTOS DE ENTRADA
    # ===========================
    try:
        textos = TextosEntrada.query.first()
    except Exception:
        textos = None

    texto_entrada = (
        textos.texto_entrada
        if textos and getattr(textos, "texto_entrada", None)
        else texto_entrada_manual
    )

    texto_cadastro = (
        textos.texto_cadastro
        if textos and getattr(textos, "texto_cadastro", None)
        else texto_cadastro_manual
    )
    # ===========================
    # CIDADES (Tabela localizacao)
    # ===========================
    regioes_manuais = ["Indaiatuba", "Itu", "Salto"]

    try:
        cidades_q = (
            Localizacao.query.with_entities(Localizacao.cidade)
            .distinct()
            .order_by(Localizacao.cidade)
            .all()
        )
        regioes = [c.cidade for c in cidades_q if c.cidade]
        if not regioes:
            regioes = regioes_manuais
    except Exception:
        regioes = regioes_manuais

    # ===========================
    # SERVIÇOS
    # ===========================
    try:
        servicos_q = (
            PrestadorServico.query.with_entities(PrestadorServico.especialidade)
            .distinct()
            .order_by(PrestadorServico.especialidade)
            .all()
        )
        servicos = [
            s.especialidade for s in servicos_q
            if s.especialidade and s.especialidade.strip()
        ]
    except Exception:
        servicos = []

    # ===========================
    # USUÁRIO LOGADO
    # ===========================
    try:
        usuario_logado = current_user.is_authenticated
    except Exception:
        usuario_logado = False

    return render_template(
        'home.html',
        texto_entrada=texto_entrada,
        texto_cadastro=texto_cadastro,
        regioes=regioes,
        servicos=servicos,
        usuario_logado=usuario_logado
    )

@servicos_bp.route('/servicos')
@bloquear_tipos('prestador') # Prestador não entra na página
def listar_servicos():
    """
    Lista automática e alfabética de serviços (nomes únicos)
    - se vazio: frase "No momento ainda não tem serviços cadastrados"
    - cada nome linka para a rota '/prestadores' com ?especialidade=<nome>
    """
    servicos_unicos = []
    try:
        if PrestadorServico is not None:
            q = (
bancodedados.session.query(func.trim(PrestadorServico.especialidade).label('esp'))
                .filter(PrestadorServico.especialidade != None)
                .filter(func.trim(PrestadorServico.especialidade) != '')
                .distinct()
            .order_by(func.upper(func.trim(PrestadorServico.especialidade)))
            )
            servicos_unicos = [row.esp for row in q.all()]
        else:
            # fallback: tenta obter das especialidades dos prestadores
            if PrestadorServico is not None:
                q = (
bancodedados.session.query(func.trim(PrestadorServico.especialidade).label('esp'))
                    .filter(PrestadorServico.especialidade != None)
                    .filter(func.trim(PrestadorServico.especialidade) != '')
                    .distinct()
            .order_by(func.upper(func.trim(PrestadorServico.especialidade)))
            )
                servicos_unicos = [row.esp for row in q.all()]
    except Exception as e:
        # registra no logger da aplicação e devolve lista vazia (evita 500)
        current_app.logger.exception("Erro ao listar serviços únicos: %s", e)
        servicos_unicos = []

    return render_template(
        'servicos/lista_servicos.html',
        servicos=servicos_unicos
    )


@servicos_bp.route('/prestadores')
@bloquear_tipos('prestador') # Prestador não entra na página
def listar_prestadores():
    """
    Segunda coluna (20%) — Lista de prestadores de uma especialidade.
    Também envia a lista de serviços (coluna 1), pois o layout é fixo.
    """
    especialidade = request.args.get('especialidade', None)

    # --- Coluna 1: lista de serviços únicos ---
    try:
        q = (
            bancodedados.session.query(func.trim(PrestadorServico.especialidade).label('esp'))
            .filter(PrestadorServico.especialidade != None)
            .filter(func.trim(PrestadorServico.especialidade) != '')
            .distinct()
            .order_by(func.upper(func.trim(PrestadorServico.especialidade)))
        )
        todos_servicos = [row.esp for row in q.all()]
    except Exception as e:
        current_app.logger.exception("Erro ao listar serviços únicos: %s", e)
        todos_servicos = []

    # --- Coluna 2: lista de prestadores daquela especialidade ---
    try:
        if especialidade:
            prestadores = (
                PrestadorServico.query
                .filter(PrestadorServico.especialidade == especialidade)
                .order_by(PrestadorServico.nome)
                .all()
            )
        else:
            prestadores = (
                PrestadorServico.query
                .order_by(PrestadorServico.nome)
                .all()
            )
    except Exception as e:
        current_app.logger.exception("Erro ao buscar prestadores: %s", e)
        prestadores = []

    return render_template(
        'servicos/lista_prestadores.html',
        todos_servicos=todos_servicos,   # coluna 1
        prestadores=prestadores,         # coluna 2
        especialidade=especialidade or 'Todos'
    )


@servicos_bp.route('/prestador/<int:prestador_id>')
@bloquear_tipos('prestador') # Prestador não entra na página
def detalhes_prestador(prestador_id):
    """
    Exibe detalhes completos de um prestador.
    • Primeira sessão → dados básicos (Usuario)
    • Segunda sessão → serviços extras cadastrados (ServicoPrestado)
    
    O HTML final divide a tela em 20% | 20% | 60%
    """

    if Usuario is None or PrestadorServico is None:
        abort(500)

    # ========== 1) Buscar dados básicos do prestador ==========
    prestador = (
        bancodedados.session.query(Usuario)
        .filter(Usuario.id == prestador_id)
        .first()
    )

    if prestador is None:
        abort(404, description="Prestador não encontrado.")

    # ========== 2) Buscar registro de PrestadorServico ==========
    registro_servico = (
        PrestadorServico.query
        .filter_by(usuario_id=prestador.id)
        .first()
    )

    if registro_servico is None:
        # não impede exibir página — apenas indica que não há serviços extras
        servicos_extras = []
    else:
        # ========== 3) Buscar serviços extras ==========
        servicos_extras = (
            ServicoPrestado.query
            .filter_by(prestador_id=registro_servico.id)
            .order_by(ServicoPrestado.nome_servico)
            .all()
        )

    # Renderização final
    return render_template(
        'servicos/detalhes_prestador.html',
        prestador=prestador,                    # dados básicos
        registro_servico=registro_servico,      # contém especialidade principal
        servicos_extras=servicos_extras         # lista de serviços extras
    )
