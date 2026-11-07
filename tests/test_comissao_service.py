from decimal import Decimal

import pytest

from app.services.comissao_service import calcular_comissao, somar_valores


@pytest.mark.parametrize(
    "valor, percentual, esperado",
    [
        ("1250.00", "8", "100.00"),    # venda de aparelhos
        ("890.00", "15", "133.50"),    # serviço técnico
        ("980.00", "12", "117.60"),    # seguros e garantias
        ("1780.00", "10", "178.00"),   # acessórios
        ("500.00", "0", "0.00"),       # categoria sem comissão
        ("500.00", "100", "500.00"),
    ],
)
def test_comissao_por_categoria(valor, percentual, esperado):
    assert calcular_comissao(valor, percentual) == Decimal(esperado)


def test_arredonda_meio_centavo_para_cima():
    # 10,10 x 5% = 0,505 -> 0,51 (float daria 0,50)
    assert calcular_comissao("10.10", "5") == Decimal("0.51")


def test_arredonda_para_baixo_abaixo_de_meio_centavo():
    # 10,05 x 5% = 0,5025 -> 0,50
    assert calcular_comissao("10.05", "5") == Decimal("0.50")


def test_aceita_float_e_int_sem_erro_de_precisao():
    assert calcular_comissao(10.10, 5) == Decimal("0.51")
    assert calcular_comissao(1000, 8) == Decimal("80.00")


@pytest.mark.parametrize("valor", ["0", "-10"])
def test_valor_invalido(valor):
    with pytest.raises(ValueError):
        calcular_comissao(valor, "8")


@pytest.mark.parametrize("percentual", ["-1", "100.01"])
def test_percentual_invalido(percentual):
    with pytest.raises(ValueError):
        calcular_comissao("100", percentual)


def test_somar_valores():
    assert somar_valores(["100.00", "133.50", "187.20"]) == Decimal("420.70")


def test_somar_lista_vazia():
    assert somar_valores([]) == Decimal("0.00")