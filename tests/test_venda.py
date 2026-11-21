from datetime import date
from decimal import Decimal
import pytest
from app.repositories import bonus_campanha
from app.services import campanha_gestao_service as campanhas, categoria_service, venda_service, vendedora_service
from app.services.validacao import ErroDeNegocio

HOJE = date(2026, 10, 25)
OUT_INI, OUT_FIM = date(2026, 10, 1), date(2026, 10, 31)


@pytest.fixture
def base(s):
    ana = vendedora_service.cadastrar(s, "Ana")
    aparelhos = categoria_service.cadastrar(s, "Aparelhos", "VENDA", "8")
    servicos = categoria_service.cadastrar(s, "Serviços técnicos", "SERVICO", "15")
    return ana, aparelhos, servicos


def vender(s, ana, categoria, dia, valor="100", pontos=0):
    return venda_service.registrar_venda(
        s, ana.id, categoria.id, date(2026, 10, dia), valor, pontos, hoje=HOJE
    )


# ---------- comissão ----------
def test_comissao_pelo_percentual_da_categoria(s, base):
    ana, aparelhos, servicos = base
    r1 = vender(s, ana, aparelhos, 5, "1250")
    r2 = vender(s, ana, servicos, 6, "890")
    assert r1.venda.valor_comissao == Decimal("100.00")
    assert r1.venda.percentual_aplicado == Decimal("8.00")
    assert r2.venda.valor_comissao == Decimal("133.50")


def test_valor_no_formato_brasileiro(s, base):
    ana, aparelhos, _ = base
    assert vender(s, ana, aparelhos, 5, "1.250,00").venda.valor == Decimal("1250.00")


def test_mudar_percentual_nao_altera_vendas_antigas(s, base):
    ana, aparelhos, _ = base
    antiga = vender(s, ana, aparelhos, 5, "1250").venda
    categoria_service.editar(s, aparelhos.id, "Aparelhos", "VENDA", "20", ativa=True)
    nova = vender(s, ana, aparelhos, 6, "1250").venda
    assert antiga.valor_comissao == Decimal("100.00")
    assert nova.valor_comissao == Decimal("250.00")


# ---------- validações ----------
def test_vendedora_inativa_nao_vende(s, base):
    ana, aparelhos, _ = base
    vendedora_service.definir_ativa(s, ana.id, False)
    with pytest.raises(ErroDeNegocio):
        vender(s, ana, aparelhos, 5)


def test_categoria_inativa_nao_vende(s, base):
    ana, aparelhos, _ = base
    categoria_service.editar(s, aparelhos.id, "Aparelhos", "VENDA", "8", ativa=False)
    with pytest.raises(ErroDeNegocio):
        vender(s, ana, aparelhos, 5)


def test_vendedora_inexistente(s, base):
    _, aparelhos, _ = base
    with pytest.raises(ErroDeNegocio):
        venda_service.registrar_venda(s, 999, aparelhos.id, date(2026, 10, 5), "100", hoje=HOJE)


@pytest.mark.parametrize("valor", ["0", "-5", "abc"])
def test_valor_invalido(s, base, valor):
    ana, aparelhos, _ = base
    with pytest.raises(ErroDeNegocio):
        vender(s, ana, aparelhos, 5, valor)


def test_data_futura(s, base):
    ana, aparelhos, _ = base
    with pytest.raises(ErroDeNegocio):
        vender(s, ana, aparelhos, 28)  # HOJE é dia 25


def test_listar_vendas_e_totais(s, base):
    ana, aparelhos, _ = base
    vender(s, ana, aparelhos, 5, "100")
    vender(s, ana, aparelhos, 6, "200")
    vendas = venda_service.listar_vendas(s, OUT_INI, OUT_FIM)
    assert [v.valor for v in vendas] == [Decimal("200.00"), Decimal("100.00")]
    assert venda_service.totais_do_periodo(s, OUT_INI, OUT_FIM) == (Decimal("300.00"), Decimal("24.00"))
    with pytest.raises(ErroDeNegocio):
        venda_service.listar_vendas(s, OUT_FIM, OUT_INI)


# ---------- bônus de campanha ----------
def test_combo_concede_bonus_na_terceira_venda_e_so_uma_vez(s, base):
    ana, aparelhos, servicos = base
    campanhas.cadastrar(s, "Combo", "COMBO", 3, "100", OUT_INI, OUT_FIM, categoria_id=servicos.id)
    assert vender(s, ana, servicos, 2).bonus_concedidos == []
    assert vender(s, ana, servicos, 9).bonus_concedidos == []
    terceira = vender(s, ana, servicos, 20)
    assert [b.valor_bonus for b in terceira.bonus_concedidos] == [Decimal("100.00")]
    assert vender(s, ana, servicos, 21).bonus_concedidos == []  # já pago
    assert bonus_campanha.total_do_mes(s, OUT_INI) == Decimal("100")


def test_combo_ignora_outras_categorias(s, base):
    ana, aparelhos, servicos = base
    campanhas.cadastrar(s, "Combo", "COMBO", 3, "100", OUT_INI, OUT_FIM, categoria_id=servicos.id)
    vender(s, ana, servicos, 2)
    vender(s, ana, servicos, 9)
    assert vender(s, ana, aparelhos, 20).bonus_concedidos == []


def test_pontuacao_concede_ao_cruzar_a_meta(s, base):
    ana, aparelhos, _ = base
    campanhas.cadastrar(s, "Pontos", "PONTUACAO", 500, "150", OUT_INI, date(2026, 12, 31))
    assert vender(s, ana, aparelhos, 2, pontos=300).bonus_concedidos == []
    cruzou = vender(s, ana, aparelhos, 9, pontos=250)
    assert [b.valor_bonus for b in cruzou.bonus_concedidos] == [Decimal("150.00")]
    assert vender(s, ana, aparelhos, 10, pontos=500).bonus_concedidos == []


def test_pontuacao_nao_repete_em_outro_mes(s, base):
    ana, aparelhos, _ = base
    campanhas.cadastrar(s, "Pontos", "PONTUACAO", 500, "150", OUT_INI, date(2026, 12, 31))
    vender(s, ana, aparelhos, 2, pontos=600)  # ganha em outubro
    novembro = venda_service.registrar_venda(
        s, ana.id, aparelhos.id, date(2026, 11, 5), "100", 600, hoje=date(2026, 11, 10)
    )
    assert novembro.bonus_concedidos == []


def test_campanha_inativa_nao_concede(s, base):
    ana, aparelhos, _ = base
    c = campanhas.cadastrar(s, "Pontos", "PONTUACAO", 500, "150", OUT_INI, OUT_FIM)
    campanhas.definir_ativa(s, c.id, False)
    assert vender(s, ana, aparelhos, 2, pontos=900).bonus_concedidos == []