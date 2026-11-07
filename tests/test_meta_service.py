from datetime import date
from decimal import Decimal

import pytest

from app.services.meta_service import (
    calcular_atingimento,
    calcular_valor_por_dia,
    calcular_valor_restante,
)


def test_atingimento_exemplo_do_mockup():
    assert calcular_atingimento("80000", "52400") == Decimal("65.50")


def test_atingimento_pode_passar_de_100():
    assert calcular_atingimento("70000", "70500") == Decimal("100.71")


def test_atingimento_sem_vendas():
    assert calcular_atingimento("20000", "0") == Decimal("0.00")


def test_atingimento_com_meta_zero_nao_divide_por_zero():
    assert calcular_atingimento("0", "500") == Decimal("0.00")


def test_valor_restante():
    assert calcular_valor_restante("80000", "52400") == Decimal("27600.00")


def test_valor_restante_nunca_negativo():
    assert calcular_valor_restante("70000", "70500") == Decimal("0.00")


def test_valor_por_dia_exemplo_do_mockup():
    # faltam 27.600 e restam 8 dias (24/10 a 31/10, contando o dia de hoje)
    r = calcular_valor_por_dia("80000", "52400", date(2026, 10, 24), date(2026, 10, 31))
    assert r == Decimal("3450.00")


def test_ultimo_dia_do_periodo_conta_um_dia():
    r = calcular_valor_por_dia("1000", "400", date(2026, 10, 31), date(2026, 10, 31))
    assert r == Decimal("600.00")


def test_valor_por_dia_arredonda_centavos():
    r = calcular_valor_por_dia("1000", "900", date(2026, 10, 29), date(2026, 10, 31))
    assert r == Decimal("33.33")  # 100 / 3


def test_meta_batida_nao_precisa_vender_mais():
    r = calcular_valor_por_dia("1000", "1200", date(2026, 10, 20), date(2026, 10, 31))
    assert r == Decimal("0.00")


def test_meta_batida_com_periodo_encerrado_devolve_zero():
    r = calcular_valor_por_dia("1000", "1200", date(2026, 11, 5), date(2026, 10, 31))
    assert r == Decimal("0.00")


def test_periodo_encerrado_sem_meta_batida():
    with pytest.raises(ValueError):
        calcular_valor_por_dia("1000", "400", date(2026, 11, 1), date(2026, 10, 31))