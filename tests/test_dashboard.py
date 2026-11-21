from datetime import date
from decimal import Decimal
import pytest
from app.services import (
    campanha_gestao_service as campanhas,
    categoria_service,
    dashboard_service,
    meta_gestao_service,
    relatorio_service,
    venda_service,
    vendedora_service,
)
from app.services.validacao import ErroDeNegocio

OUT = date(2026, 10, 1)
HOJE_VENDAS = date(2026, 10, 25)


@pytest.fixture
def cenario(s):
    ana = vendedora_service.cadastrar(s, "Ana")
    bia = vendedora_service.cadastrar(s, "Bia")
    cat = categoria_service.cadastrar(s, "Aparelhos", "VENDA", "8")
    meta_gestao_service.definir_metas_do_mes(s, OUT, {ana.id: "20000", bia.id: "20000"})

    def vender(vendedora, mes, dia, valor):
        venda_service.registrar_venda(s, vendedora.id, cat.id, date(2026, mes, dia), valor, hoje=HOJE_VENDAS)
        
    vender(ana, 10, 5, "1000")
    vender(ana, 10, 20, "3000")
    vender(bia, 10, 10, "2000")
    vender(ana, 9, 10, "2000")  # mês anterior
    return ana, bia


def test_numeros_principais(s, cenario):
    d = dashboard_service.montar_dashboard(s, OUT, hoje=date(2026, 10, 24))
    assert d.meta == Decimal("40000.00")
    assert d.vendido == Decimal("6000.00")
    assert d.atingimento == Decimal("15.00")
    assert d.restante == Decimal("34000.00")
    assert d.dias_restantes == 8
    assert d.valor_por_dia == Decimal("4250.00")  # 34000 / 8 dias
    assert d.comissao_vendas == Decimal("480.00")
    assert d.bonus == Decimal("0.00")
    assert d.comissao_total == Decimal("480.00")


def test_comparativo_com_meses_anteriores(s, cenario):
    d = dashboard_service.montar_dashboard(s, OUT, hoje=date(2026, 10, 24))
    assert d.variacao_vs_mes_anterior == Decimal("200.00")  # 6000 vs 2000
    assert len(d.comparativo) == 6
    assert d.comparativo[-1] == (date(2026, 10, 1), Decimal("6000.00"))
    assert d.comparativo[-2] == (date(2026, 9, 1), Decimal("2000.00"))
    assert d.comparativo[0][0] == date(2026, 5, 1)


def test_sem_mes_anterior_nao_ha_variacao(s, cenario):
    d = dashboard_service.montar_dashboard(s, date(2026, 9, 1), hoje=date(2026, 10, 24))
    assert d.variacao_vs_mes_anterior is None


def test_mes_encerrado_nao_tem_valor_por_dia(s, cenario):
    d = dashboard_service.montar_dashboard(s, OUT, hoje=date(2026, 11, 2))
    assert d.valor_por_dia is None
    assert d.dias_restantes == 0


def test_desempenho_por_vendedora(s, cenario):
    d = dashboard_service.montar_dashboard(s, OUT, hoje=date(2026, 10, 24))
    ana, bia = d.por_vendedora
    assert (ana.nome, ana.vendido, ana.atingimento, ana.comissao) == (
        "Ana", Decimal("4000.00"), Decimal("20.00"), Decimal("320.00"))
    assert (bia.nome, bia.vendido, bia.atingimento, bia.comissao) == (
        "Bia", Decimal("2000.00"), Decimal("10.00"), Decimal("160.00"))


def test_bonus_entra_no_total_da_vendedora(s, cenario):
    ana, _ = cenario
    camp = campanhas.cadastrar(s, "Pontos", "PONTUACAO", 100, "150", OUT, date(2026, 10, 31))
    venda_service.registrar_venda(
        s, ana.id, 1, date(2026, 10, 22), "100", 100, hoje=HOJE_VENDAS
    )
    d = dashboard_service.montar_dashboard(s, OUT, hoje=date(2026, 10, 24))
    linha_ana = d.por_vendedora[0]
    assert linha_ana.bonus == Decimal("150.00")
    assert linha_ana.total == linha_ana.comissao + Decimal("150.00")
    assert d.bonus == Decimal("150.00")


def test_historico_de_metas(s, cenario):
    em_andamento = meta_gestao_service.historico(s, hoje=date(2026, 10, 24))
    assert em_andamento[0].situacao == meta_gestao_service.EM_ANDAMENTO
    encerrado = meta_gestao_service.historico(s, hoje=date(2026, 11, 2))
    linha = encerrado[0]
    assert (linha.mes, linha.meta, linha.realizado) == (OUT, Decimal("40000.00"), Decimal("6000.00"))
    assert linha.situacao == meta_gestao_service.NAO_ATINGIDA


def test_definir_metas_valida_antes_de_gravar(s, cenario):
    ana, _ = cenario
    with pytest.raises(ErroDeNegocio):
        meta_gestao_service.definir_metas_do_mes(s, date(2026, 11, 1), {ana.id: "5000", 999: "100"})
    assert meta_gestao_service.meta_da_unidade(s, date(2026, 11, 1)) == Decimal("0.00")


def test_relatorio_mensal(s, cenario):
    r = relatorio_service.relatorio_mensal(s, OUT)
    assert (r.meta, r.vendido, r.atingimento) == (Decimal("40000.00"), Decimal("6000.00"), Decimal("15.00"))
    assert r.comissao_total == Decimal("480.00")
    assert [l.nome for l in r.linhas] == ["Ana", "Bia"]


def test_relatorio_individual(s, cenario):
    ana, _ = cenario
    r = relatorio_service.relatorio_individual(s, ana.id, OUT)
    assert r.vendedora.nome == "Ana"
    assert (r.meta, r.vendido, r.atingimento) == (Decimal("20000.00"), Decimal("4000.00"), Decimal("20.00"))
    assert r.comissao_vendas == Decimal("320.00")
    assert len(r.vendas) == 2
    assert r.bonus_conquistados == []


def test_relatorio_individual_vendedora_inexistente(s, cenario):
    with pytest.raises(ErroDeNegocio):
        relatorio_service.relatorio_individual(s, 999, OUT)