from decimal import Decimal, ROUND_HALF_UP

ZERO = Decimal("0.00")
_CENTAVO = Decimal("0.01")


def para_decimal(valor) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def arredondar(valor: Decimal) -> Decimal:
    return valor.quantize(_CENTAVO, rounding=ROUND_HALF_UP)


def calcular_comissao(valor_venda, percentual) -> Decimal:
    valor_venda = para_decimal(valor_venda)
    percentual = para_decimal(percentual)
    if valor_venda <= 0:
        raise ValueError("O valor da venda deve ser maior que zero.")
    if not (0 <= percentual <= 100):
        raise ValueError("O percentual deve estar entre 0 e 100.")
    return arredondar(valor_venda * percentual / 100)


def somar_valores(valores) -> Decimal:
    return arredondar(sum((para_decimal(v) for v in valores), ZERO))