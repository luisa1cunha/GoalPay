from datetime import date
from decimal import Decimal

from app.services.comissao_service import ZERO, arredondar, para_decimal


def calcular_atingimento(meta, vendido) -> Decimal:
    meta = para_decimal(meta)
    vendido = para_decimal(vendido)
    if meta <= 0:
        return ZERO
    return arredondar(vendido / meta * 100)


def calcular_valor_restante(meta, vendido) -> Decimal:
    restante = para_decimal(meta) - para_decimal(vendido)
    return arredondar(max(restante, ZERO))


def calcular_valor_por_dia(meta, vendido, hoje: date, fim_periodo: date) -> Decimal:
    restante = calcular_valor_restante(meta, vendido)
    if restante == 0:
        return ZERO
    dias = (fim_periodo - hoje).days + 1
    if dias <= 0:
        raise ValueError("O período já terminou e a meta não foi atingida.")
    return arredondar(restante / dias)