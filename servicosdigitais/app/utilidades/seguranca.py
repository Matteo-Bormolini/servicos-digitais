from servicosdigitais.app.extensoes import bcrypt


def gerar_senha_hash(senha: str) -> str:
    """
    Gera hash seguro da senha usando bcrypt.
    """
    return bcrypt.generate_password_hash(senha).decode("utf-8")


def verificar_senha_hash(senha_digitada: str, senha_hash: str) -> bool:
    """
    Verifica se a senha digitada corresponde ao hash armazenado.
    """
    return bcrypt.check_password_hash(senha_hash, senha_digitada)
