
# Deois mexer
def formatar_cnpj(cnpj):
    cnpj = str(cnpj)
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def formatar_telefone(tel):
    tel = str(tel)

    if len(tel) == 10:
        # telefone fixo
        return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
    
    # telefone celular
    return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
