from datetime import date
from decimal import Decimal

from app.models import BonusCampanha, Campanha, Categoria, Venda, Vendedora
from app.repositories import (
    bonus_campanha as bonus_repo,
    campanha as campanha_repo,
    categoria as categoria_repo,
    meta as meta_repo,
    venda as venda_repo,
    vendedora as vendedora_repo,
)

OUT_INI, OUT_FIM = date(2026, 10, 1), date(2026, 10, 31)


def _venda(vendedora, categoria, dia, valor, mes=10):
    valor = Decimal(valor)
    return Venda(
        vendedora_id=vendedora.id,
        categoria_id=categoria.id,
        data_venda=date(2026, mes, dia),
        valor=valor,
        percentual_aplicado=Decimal("8"),
        valor_comissao=valor * Decimal("0.08"),
    )


def _cenario(s):
    ana = vendedora_repo.salvar(s, Vendedora(nome="Ana"))
    bia = vendedora_repo.salvar(s, Vendedora(nome="Bia"))
    cat = categoria_repo.salvar(
        s, Categoria(nome="Aparelhos", tipo="VENDA", percentual_comissao=Decimal("8"))
    )
    return ana, bia, cat


def test_salvar_gera_id_e_listar_filtra_inativas(s):
    ana = vendedora_repo.salvar(s, Vendedora(nome="Ana"))
    vendedora_repo.salvar(s, Vendedora(nome="Carla", ativa=False))
    assert ana.id is not None
    assert [v.nome for v in vendedora_repo.listar(s)] == ["Ana", "Carla"]
    assert [v.nome for v in vendedora_repo.listar(s, apenas_ativas=True)] == ["Ana"]


def test_buscar_categoria_por_nome(s):
    _cenario(s)
    assert categoria_repo.buscar_por_nome(s, "Aparelhos").tipo == "VENDA"
    assert categoria_repo.buscar_por_nome(s, "Inexistente") is None


def test_vendas_e_totais_do_periodo(s):
    ana, _, cat = _cenario(s)
    venda_repo.salvar(s, _venda(ana, cat, 5, "100"))
    venda_repo.salvar(s, _venda(ana, cat, 20, "200"))
    venda_repo.salvar(s, _venda(ana, cat, 5, "50", mes=11))  # fora do período

    vendas = venda_repo.listar_por_periodo(s, OUT_INI, OUT_FIM)
    assert [v.valor for v in vendas] == [Decimal("200"), Decimal("100")]  # mais recente primeiro
    assert vendas[0].vendedora.nome == "Ana"
    assert venda_repo.total_vendido(s, OUT_INI, OUT_FIM) == Decimal("300")
    assert venda_repo.total_comissao(s, OUT_INI, OUT_FIM) == Decimal("24")


def test_resumo_inclui_vendedora_sem_vendas(s):
    ana, _, cat = _cenario(s)
    venda_repo.salvar(s, _venda(ana, cat, 5, "300"))
    resumo = venda_repo.resumo_por_vendedora(s, OUT_INI, OUT_FIM)
    assert [(nome, vendido) for _, nome, vendido, _ in resumo] == [
        ("Ana", Decimal("300")),
        ("Bia", Decimal("0")),
    ]


def test_definir_meta_atualiza_em_vez_de_duplicar(s):
    ana, _, _ = _cenario(s)
    meta_repo.definir(s, ana.id, date(2026, 10, 15), Decimal("20000"))
    meta_repo.definir(s, ana.id, date(2026, 10, 3), Decimal("25000"))
    metas = meta_repo.listar_do_mes(s, OUT_INI)
    assert len(metas) == 1
    assert metas[0].mes_referencia == OUT_INI  # sempre dia 1
    assert meta_repo.total_do_mes(s, OUT_INI) == Decimal("25000")


def test_campanhas_vigentes(s):
    def camp(nome, ini, fim, ativa=True):
        return Campanha(nome=nome, tipo="PONTUACAO", meta_quantidade=500,
                        valor_bonus=Decimal("150"), data_inicio=ini, data_fim=fim, ativa=ativa)

    campanha_repo.salvar(s, camp("vigente", date(2026, 10, 1), date(2026, 12, 31)))
    campanha_repo.salvar(s, camp("encerrada", date(2026, 9, 1), date(2026, 9, 30)))
    campanha_repo.salvar(s, camp("inativa", date(2026, 10, 1), date(2026, 12, 31), ativa=False))
    nomes = [c.nome for c in campanha_repo.listar_vigentes(s, date(2026, 10, 24))]
    assert nomes == ["vigente"]


def test_bonus_existe_e_totais(s):
    ana, bia, _ = _cenario(s)
    camp = campanha_repo.salvar(
        s, Campanha(nome="Combo", tipo="COMBO", meta_quantidade=3, valor_bonus=Decimal("100"),
                    data_inicio=OUT_INI, data_fim=OUT_FIM, categoria_id=1))
    bonus_repo.salvar(s, BonusCampanha(campanha_id=camp.id, vendedora_id=ana.id,
                                       mes_referencia=OUT_INI, valor_bonus=Decimal("100")))
    assert bonus_repo.existe(s, camp.id, ana.id, date(2026, 10, 20)) is True
    assert bonus_repo.existe(s, camp.id, bia.id, OUT_INI) is False
    assert bonus_repo.existe(s, camp.id, ana.id, date(2026, 11, 1)) is False
    assert bonus_repo.total_do_mes(s, OUT_INI) == Decimal("100")
    assert bonus_repo.totais_por_vendedora(s, OUT_INI) == {ana.id: Decimal("100")}