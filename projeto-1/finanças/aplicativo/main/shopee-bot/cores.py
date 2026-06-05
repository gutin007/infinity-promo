"""
def variacao_de_preco(variacao: float) -> int:
    if variacao >= 30:
        return 0x00FF00   # 🟢— desconto excelente
    elif variacao >= 20:
        return 0x7CFC00   # 🟢 — desconto ótimo
    elif variacao >= 10:
        return 0xFFFF00   # 🟡 — desconto bom
    elif variacao >= 5:
        return 0xFF8C00   # 🟠— desconto razoável
    else:
        return 0xFF2400   # 🔴— desconto pequeno
"""