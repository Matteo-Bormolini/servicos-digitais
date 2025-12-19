# ========================
# Utilidades - limpar, mascarar, converter
# ========================

# Funções que transformam dados, sem validar se estão certos ou errados.


def _mask_email(email: str):
    if not email or '@' not in email:
        return email or ''
    local, dominio = email.split('@', 1)
    if len(local) <= 1:
        local_mask = '*'
    elif len(local) == 2:
        local_mask = local[0] + '*'
    else:
        local_mask = local[0] + '*' * (len(local) - 2) + local[-1]
    # manter domínio visível
    return f"{local_mask}@{dominio}"


def _mask_doc(doc: str) -> str:
    """Mascarar CPF/CNPJ (apenas dígitos esperados). Ex.: 11122233344 -> 111.***.***-44"""
    if not doc:
        return ''
    s = ''.join(ch for ch in str(doc) if ch.isdigit())
    l = len(s)
    if l == 11:  # CPF
        return f"{s[0:3]}.{s[3:6]}.***-{s[-2:]}"
    if l == 14:  # CNPJ
        return f"{s[0:2]}.{s[2:5]}.***./{s[8:12]}-{s[-2:]}" 
    # máscara informativa
    # caso genérico, preserva primeiros e últimos
    if l <= 4:
        return '*' * l
    return s[0:2] + '*' * (l - 4) + s[-2:]


def _mask_phone(phone: str) -> str:
    if not phone:
        return ''
    s = ''.join(ch for ch in str(phone) if ch.isdigit())
    l = len(s)
    if l <= 4:
        return '*' * l
    # mostra últimos 4 dígitos
    return '*' * (l - 4) + s[-4:]


def esta_ativo(valor): # TALVEZ mudar
    """Normaliza campo ativo (0/1/bool/str) para booleano."""
    if valor is None:
        return True  # se não houver campo, assumimos ativo
    # tratar ints
    if isinstance(valor, int):
        return bool(valor)
    # tratar strings como '0'/'1'/'true'/'false'
    if isinstance(valor, str):
        v = valor.strip().lower()
        if v in ('0', 'false', 'f', 'no', 'n'):
            return False
        return True
    # tratar booleans
    return bool(valor)
