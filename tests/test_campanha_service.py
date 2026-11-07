from datetime import date
from decimal import Decimal

import pytest

from app.services.campanha_service import (
    COMBO,
    PONTUACAO,
    Campanha,
    Venda,
    calcular_bonus,
    calcular_bonus_total,
)

SERVICOS, ACESSORIOS = 3, 2
INICIO, FIM = date(2026, 10, 1), date(2026, 10, 31)


def venda(dia, categoria=SERVICOS, pontos=0, mes=10):
    return Venda(data=date(2026, mes, dia), categoria_id=categoria, valor=Decimal("100"), pontos=pontos)


def pontuacao(meta=500, bonus="150.00", **kw):
    return Campanha(PONTUACAO, meta, Decimal(bonus), INICIO, FIM, **kw)


def combo(meta=3, bonus="100.00", categoria=SERVICOS, **kw):
    return Campanha(COMBO, meta, Decimal(bonus), INICIO, FIM, categoria_id=categoria, **kw)


# ---------- pontuação ----------
def test_pontuacao_atinge_a_meta():
    vendas = [venda(2, pontos=300), venda(10, pontos=250)]
    assert calcular_bonus(pontuacao(), vendas) == Decimal("150.00")


def test_pontuacao_exatamente_na_meta_ganha():
    assert calcular_bonus(pontuacao(), [venda(5, pontos=500)]) == Decimal("150.00")


def test_pontuacao_abaixo_da_meta_nao_ganha():
    assert calcular_bonus(pontuacao(), [venda(5, pontos=499)]) == Decimal("0.00")


def test_pontuacao_paga_uma_vez_mesmo_com_o_dobro_de_pontos():
    assert calcular_bonus(pontuacao(), [venda(5, pontos=1000)]) == Decimal("150.00")


def test_pontuacao_ignora_vendas_fora_do_periodo():
    vendas = [venda(30, pontos=400, mes=9), venda(5, pontos=300, mes=11), venda(3, pontos=100)]
    assert calcular_bonus(pontuacao(), vendas) == Decimal("0.00")


def test_pontuacao_conta_primeiro_e_ultimo_dia():
    vendas = [venda(1, pontos=250), venda(31, pontos=250)]
    assert calcular_bonus(pontuacao(), vendas) == Decimal("150.00")


def test_pontuacao_campanha_inativa():
    assert calcular_bonus(pontuacao(ativa=False), [venda(5, pontos=900)]) == Decimal("0.00")


# ---------- combo ----------
def test_combo_tres_vendas_da_categoria():
    vendas = [venda(2), venda(9), venda(20)]
    assert calcular_bonus(combo(), vendas) == Decimal("100.00")


def test_combo_duas_vendas_nao_ganha():
    assert calcular_bonus(combo(), [venda(2), venda(9)]) == Decimal("0.00")


def test_combo_ignora_outras_categorias():
    vendas = [venda(2), venda(9), venda(20, categoria=ACESSORIOS)]
    assert calcular_bonus(combo(), vendas) == Decimal("0.00")


def test_combo_ignora_vendas_fora_do_periodo():
    vendas = [venda(2), venda(9), venda(30, mes=9)]
    assert calcular_bonus(combo(), vendas) == Decimal("0.00")


def test_combo_paga_uma_vez_mesmo_com_seis_vendas():
    vendas = [venda(d) for d in (1, 2, 3, 4, 5, 6)]
    assert calcular_bonus(combo(), vendas) == Decimal("100.00")


def test_combo_campanha_inativa():
    vendas = [venda(2), venda(9), venda(20)]
    assert calcular_bonus(combo(ativa=False), vendas) == Decimal("0.00")


def test_combo_sem_categoria_e_erro():
    camp = Campanha(COMBO, 3, Decimal("100"), INICIO, FIM, categoria_id=None)
    with pytest.raises(ValueError):
        calcular_bonus(camp, [venda(2)])


# ---------- despacho e total ----------
def test_tipo_desconhecido():
    camp = Campanha("OUTRO", 1, Decimal("10"), INICIO, FIM)
    with pytest.raises(ValueError):
        calcular_bonus(camp, [])


def test_bonus_total_soma_as_campanhas():
    vendas = [venda(2, pontos=300), venda(9, pontos=250), venda(20, pontos=0)]
    # pontuação (550 pts >= 500) = 150 + combo de 3 vendas de serviços = 100
    assert calcular_bonus_total([pontuacao(), combo()], vendas) == Decimal("250.00")


def test_bonus_total_sem_campanhas():
    assert calcular_bonus_total([], [venda(2)]) == Decimal("0.00")