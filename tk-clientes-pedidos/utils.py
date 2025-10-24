import re

def validar_cliente(c):
    if not c["nome"]:
        return "Nome é obrigatório."
    if c["email"] and not re.match(r"[^@]+@[^@]+\.[^@]+", c["email"]):
        return "E-mail inválido."
    if c["telefone"] and not re.match(r"^\d{8,15}$", c["telefone"]):
        return "Telefone deve ter entre 8 e 15 dígitos."
    return None