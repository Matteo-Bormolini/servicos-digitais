
"""
Funções utilitárias da aplicação.

Agrupa lógica reutilizável de:
- autenticação e autorização
- validação e normalização de dados
- envio de e-mails e geração de tokens
- upload e remoção de arquivos

Centraliza funções auxiliares reutilizáveis como:
- Segurança (hash de senha, verificação)
- Validações
- Decoradores
"""


'''Não irei usar ainda no de segurança:
# ==================
# SOMENTE FORNECEDOR
# ==================
def somente_fornecedor(funcao):
    """
    Permite acesso apenas para usuários do tipo 'fornecedor' ou admin.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Acesso negado: você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for('autenticacao.login'))

        if getattr(current_user, "is_admin", False):
            return funcao(*args, **kwargs)

        if getattr(current_user, "tipo", None) != "fornecedor":
            flash("Acesso negado: esta página é apenas para fornecedores.", "danger")
            return redirect(url_for('servicos.home'))

        return funcao(*args, **kwargs)
    return wrapper

'''