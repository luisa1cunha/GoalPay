
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Optional

from app.services.comissao_service import ZERO, arredondar, para_decimal, somar_valores

PONTUACAO = "PONTUACAO"
COMBO = "COMBO"


@dataclass(frozen=True)
class Venda:
    data: date
    categoria_id: int
    valor: Decimal
    pontos: int = 0


@dataclass(frozen=True)
class Campanha:
    tipo: str
    meta_quantidade: int  # pontos (PONTUACAO) ou nº de vendas (COMBO)
    valor_bonus: Decimal
    data_inicio: date
    data_fim: date
    categoria_id: Optional[int] = None  # obrigatória no COMBO
    ativa: bool = True


def _vendas_do_periodo(campanha, vendas: Iterable) -> list:
    return [v for v in vendas if campanha.data_inicio <= v.data <= campanha.data_fim]


def calcular_bonus_pontuacao(campanha, vendas: Iterable) -> Decimal:
    #Ganha o bônus quando soma `meta_quantidade` pontos ou mais no período
    if not campanha.ativa:
        return ZERO
    pontos = sum(v.pontos for v in _vendas_do_periodo(campanha, vendas))
    if pontos >= campanha.meta_quantidade:
        return arredondar(para_decimal(campanha.valor_bonus))
    return ZERO


def calcular_bonus_combo(campanha, vendas: Iterable) -> Decimal:
    #Ganha o bônus ao fazer `meta_quantidade` vendas da categoria no período
    if campanha.categoria_id is None:
        raise ValueError("Campanha de combo precisa de uma categoria.")
    if not campanha.ativa:
        return ZERO
    quantidade = sum(
        1 for v in _vendas_do_periodo(campanha, vendas)
        if v.categoria_id == campanha.categoria_id
    )
    if quantidade >= campanha.meta_quantidade:
        return arredondar(para_decimal(campanha.valor_bonus))
    return ZERO


def calcular_bonus(campanha, vendas: Iterable) -> Decimal:
    #Escolhe a regra pelo tipo da campanha.
    if campanha.tipo == PONTUACAO:
        return calcular_bonus_pontuacao(campanha, vendas)
    if campanha.tipo == COMBO:
        return calcular_bonus_combo(campanha, vendas)
    raise ValueError(f"Tipo de campanha desconhecido: {campanha.tipo}")


def calcular_bonus_total(campanhas: Iterable, vendas: Iterable) -> Decimal:
    #Soma o bônus de todas as campanhas para uma vendedora.
    vendas = list(vendas)
    return somar_valores(calcular_bonus(c, vendas) for c in campanhas)