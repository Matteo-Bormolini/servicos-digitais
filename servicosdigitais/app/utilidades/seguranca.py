from servicosdigitais.app.extensoes import bcrypt
import secrets
import string


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


def gerar_senha_temp(tamanho=6):
    """
    Gera uma senha temporária curta e difícil.
    Ideal para suporte e usuários com dificuldade de digitação.

    Regras:
    - Letras maiúsculas e minúsculas
    - Números
    - Pelo menos 1 símbolo
    """

    if tamanho < 6:
        raise ValueError("O tamanho mínimo recomendado é 6 caracteres.")

    letras = string.ascii_letters
    numeros = string.digits
    simbolos = "!@#$%&*"

    base = letras + numeros + simbolos

    # Garante diversidade mínima
    senha = [
        secrets.choice(letras),
        secrets.choice(numeros),
        secrets.choice(simbolos),
    ]

    # Completa o restante
    senha += [secrets.choice(base) for _ in range(tamanho - len(senha))]

    # Embaralha
    secrets.SystemRandom().shuffle(senha)

    return ''.join(senha)
