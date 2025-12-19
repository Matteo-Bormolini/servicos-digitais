# ========================
# Utilidades - CPF, CNPJ, senha
# ========================

from typing import Optional, List, Type
from sqlalchemy.sql import func
from servicosdigitais.app.extensoes import bancodedados
from servicosdigitais.app.models import (
    Usuario,
    ClienteCPF,
    ClienteCNPJ,
    PrestadorServico
)


# Validação CPF
def validar_cpf(cpf: str):
    """
    Valida CPF checando os dois dígitos verificadores.
    cpf: string com apenas dígitos (11 chars).
    """
    if not cpf or len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc_dig(nums):
        soma = 0
        for i, n in enumerate(nums, start=2):
            soma += int(n) * (len(nums) + 2 - i)
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    # primeiros 9 dígitos
    n1 = cpf[:9]
    d1 = calc_dig(n1)
    d2 = calc_dig(n1 + d1)
    return cpf[-2:] == d1 + d2


# Validação CNPJ
def validar_cnpj(cnpj: str):
    """
    Valida CNPJ localmente checando os dígitos verificadores.
    - cnpj: string contendo APENAS dígitos (deve usar apenas_numeros antes).
    Retorna True se válido, False se inválido.
    """
    if not cnpj:
        return False

    # garante string e só dígitos
    c = ''.join(ch for ch in str(cnpj) if ch.isdigit())

    # tem que ter 14 dígitos
    if len(c) != 14:
        return False

    # rejeitar sequências óbvias (todos iguais)
    if c == c[0] * 14:
        return False

    def calcula_digito(base: str):
        """Calcula um dígito verificador (retorna str) dado a base (12 ou 13 dígitos)."""
        pesos = [6,5,4,3,2,9,8,7,6,5,4,3,2]
        # pesos para 13 posições (usamos slice)
        soma = 0
        # alinhamos pesos à direita da base
        inicio = len(pesos) - len(base)
        for i, dig in enumerate(base):
            soma += int(dig) * pesos[inicio + i]
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    # primeiros 12 dígitos
    base12 = c[:12]
    d1 = calcula_digito(base12)
    d2 = calcula_digito(base12 + d1)

    return c[-2:] == (d1 + d2)


def senha_segura(senha):
    """
    Verifica se a senha atende aos critérios de segurança:
    - Pelo menos 6 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial
    """
    if len(senha) < 6:
        return False
    has_upper = any(c.isupper() for c in senha)
    has_lower = any(c.islower() for c in senha)
    has_digit = any(c.isdigit() for c in senha)
    has_special = any(not c.isalnum() for c in senha)
    return has_upper and has_lower and has_digit and has_special


def detectar_tipo_por_numeros(numeros: str):
    """
    Decide se a string numérica é CPF (11 dígitos) ou CNPJ (14 dígitos).
    Retorna 'cpf', 'cnpj' ou None.
    """
    if not numeros:
        return None
    l = len(numeros)
    if l == 11:
        return 'cpf'
    if l == 14:
        return 'cnpj'
    return None


# Se existe email
def email_existe(
    email: str,
    exclude_user_id: Optional[int] = None,
    modelos: Optional[List[Type]] = None):
    """
    Verifica se um e-mail já existe nas tabelas informadas.
    - exclude_user_id: se fornecido, ignora um usuário com esse id (aplicável quando checando Usuario)
    - modelos: lista de modelos SQLAlchemy a verificar. Se None, verifica [ClienteCPF, ClienteCNPJ, PrestadorServico, Usuario].

    Retorna True se o e-mail já existir em alguma tabela (exceto o usuário excluído), senão False.
    """
    if not email:
        return False
    email_norm = email.strip().lower() #email@emai.com

    if modelos is None:
        modelos = [ClienteCPF, ClienteCNPJ, PrestadorServico, Usuario]

    for modelo in modelos:
        # pular modelos que não tenham atributo 'email'
        if not hasattr(modelo, 'email'):
            continue

        # constrói a query (comparação case-insensitive)
        coluna = getattr(modelo, 'email')
        q = modelo.query.filter(func.lower(coluna) == email_norm)

        # se o modelo for Usuario e existe exclude_user_id, aplicar filtro
        if modelo is Usuario and exclude_user_id:
            q = q.filter(modelo.id != exclude_user_id)

        # usar exists() para ser eficiente
        exists = bancodedados.session.query(q.exists()).scalar()
        if exists:
            return True

    return False


def apenas_numeros(valor: str):
    """Remove tudo que não for dígito e retorna só os números."""
    if not valor:
        return ''
    return ''.join(ch for ch in str(valor) if ch.isdigit())


def parece_email(valor: str):
    """Checa de forma simples se o valor parece um e-mail."""
    if not valor:
        return False
    v = valor.strip()
    return ('@' in v) and ('.' in v.split('@')[-1])