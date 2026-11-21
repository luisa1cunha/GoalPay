import calendar
from datetime import date


def primeiro_dia_do_mes(dia: date) -> date:
    return dia.replace(day=1)


def limites_do_mes(dia: date) -> tuple[date, date]:
    """Primeiro e último dia do mês de `dia`."""
    ultimo = calendar.monthrange(dia.year, dia.month)[1]
    return dia.replace(day=1), dia.replace(day=ultimo)