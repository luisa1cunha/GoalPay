from decimal import Decimal
import pytest
from app.services.validacao import ErroDeNegocio, decimal_ou_erro, inteiro_ou_erro, texto_obrigatorio


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("1.250,00", "1250.00"),   # formato brasileiro
        ("8,5", "8.5"),
        ("R$ 890,00", "890.00"),
        ("12%", "12"),
        ("100", "100"),
        ("8.5", "8.5"),            # sem vírgula, o ponto é decimal
        (10, "10"),
        (10.1, "10.1"),
        (Decimal("7.25"), "7.25"),
    ],
)
def test_decimal_aceita_varios_formatos(entrada, esperado):
    assert decimal_ou_erro(entrada, "valor") == Decimal(esperado)


@pytest.mark.parametrize("entrada", ["abc", "", "NaN", "1,2,3a"])
def test_decimal_invalido(entrada):
    with pytest.raises(ErroDeNegocio):
        decimal_ou_erro(entrada, "valor")


def test_inteiro():
    assert inteiro_ou_erro(" 3 ", "meta") == 3
    with pytest.raises(ErroDeNegocio):
        inteiro_ou_erro("3,5", "meta")


def test_texto_obrigatorio():
    assert texto_obrigatorio("  Ana  ", "o nome") == "Ana"
    with pytest.raises(ErroDeNegocio):
        texto_obrigatorio("   ", "o nome")
    with pytest.raises(ErroDeNegocio):
        texto_obrigatorio("a" * 11, "o nome", 10)