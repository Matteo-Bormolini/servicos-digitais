"""
Formulários da aplicação.

Organiza os formulários de:
- autenticação
- cadastro
- edição de perfil
- suporte e contato
"""
from .login_forms import *
from .cadastro_forms import *
from .perfil_forms import *
from .suporte_forms import *


# Validadores Comuns
# DataRequired - O campo de usuário não pode estar vazio;
# Length - Tem que ter um limite mínimo e máximo de caracteres;
# Email - Verifica se o formato do email está correto;
# EqualTo - Verifica se dois campos são iguais (útil para confirmação de senha).