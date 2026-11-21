from datetime import date
from decimal import Decimal
import pytest
from app.services import campanha_gestao_service as campanhas, categoria_service, vendedora_service
from app.services.validacao import ErroDeNegocio

# ---------- vendedoras ----------
def test_cadastrar_vendedora(s):
    v = vendedora_service.cadastrar(s, "  Ana Souza ", "  ")
    assert v.id is not None
    assert v.nome == "Ana Souza"
    assert v.contato is None
    assert v.ativa is True


def test_vendedora_exige_nome(s):
    with pytest.raises(ErroDeNegocio):
        vendedora_service.cadastrar(s, "   ")


def test_vendedora_nome_repetido_ignora_maiusculas(s):
    vendedora_service.cadastrar(s, "Ana")
    with pytest.raises(ErroDeNegocio):
        vendedora_service.cadastrar(s, "ana")


def test_editar_permite_manter_o_proprio_nome(s):
    v = vendedora_service.cadastrar(s, "Ana")
    v = vendedora_service.editar(s, v.id, "Ana", "9999-0000", True)
    assert v.contato == "9999-0000"


def test_inativar_tira_da_lista_de_ativas(s):
    ana = vendedora_service.cadastrar(s, "Ana")
    vendedora_service.cadastrar(s, "Bia")
    vendedora_service.definir_ativa(s, ana.id, False)
    assert [v.nome for v in vendedora_service.listar(s, apenas_ativas=True)] == ["Bia"]
    assert [v.nome for v in vendedora_service.listar(s)] == ["Ana", "Bia"]


def test_vendedora_inexistente(s):
    with pytest.raises(ErroDeNegocio):
        vendedora_service.definir_ativa(s, 999, False)


# ---------- categorias ----------
def test_cadastrar_categoria_com_virgula(s):
    c = categoria_service.cadastrar(s, "Serviços", "SERVICO", "12,5")
    assert c.percentual_comissao == Decimal("12.50")


def test_categoria_tipo_invalido(s):
    with pytest.raises(ErroDeNegocio):
        categoria_service.cadastrar(s, "X", "OUTRO", "5")


@pytest.mark.parametrize("percentual", ["101", "-1", "abc"])
def test_categoria_percentual_invalido(s, percentual):
    with pytest.raises(ErroDeNegocio):
        categoria_service.cadastrar(s, "X", "VENDA", percentual)


def test_categoria_nome_repetido(s):
    categoria_service.cadastrar(s, "Aparelhos", "VENDA", "8")
    with pytest.raises(ErroDeNegocio):
        categoria_service.cadastrar(s, "aparelhos", "VENDA", "9")


def test_editar_categoria(s):
    c = categoria_service.cadastrar(s, "Aparelhos", "VENDA", "8")
    c = categoria_service.editar(s, c.id, "Aparelhos", "VENDA", "9", ativa=False)
    assert c.percentual_comissao == Decimal("9.00")
    assert c.ativa is False


# ---------- campanhas ----------
INI, FIM = date(2026, 10, 1), date(2026, 10, 31)


def test_cadastrar_campanha_de_combo(s):
    cat = categoria_service.cadastrar(s, "Serviços", "SERVICO", "15")
    c = campanhas.cadastrar(s, "Combo", "COMBO", 3, "100,00", INI, FIM, categoria_id=cat.id)
    assert c.valor_bonus == Decimal("100.00")
    assert c.categoria_id == cat.id


def test_campanha_de_pontuacao_ignora_categoria(s):
    cat = categoria_service.cadastrar(s, "Serviços", "SERVICO", "15")
    c = campanhas.cadastrar(s, "Pontos", "PONTUACAO", 500, "150", INI, FIM, categoria_id=cat.id)
    assert c.categoria_id is None


def test_combo_exige_categoria(s):
    with pytest.raises(ErroDeNegocio):
        campanhas.cadastrar(s, "Combo", "COMBO", 3, "100", INI, FIM)


def test_campanha_data_final_antes_da_inicial(s):
    with pytest.raises(ErroDeNegocio):
        campanhas.cadastrar(s, "Pontos", "PONTUACAO", 500, "150", FIM, INI)


@pytest.mark.parametrize("meta, bonus", [(0, "100"), (3, "0"), ("x", "100")])
def test_campanha_meta_e_bonus_invalidos(s, meta, bonus):
    with pytest.raises(ErroDeNegocio):
        campanhas.cadastrar(s, "Pontos", "PONTUACAO", meta, bonus, INI, FIM)