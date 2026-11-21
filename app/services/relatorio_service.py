from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import BonusCampanha, Venda, Vendedora
from app.repositories import bonus_campanha, meta_repository, venda_repository, vendedora_repository
from app.repositories.periodo_repository import limites_do_mes
from app.services.comissao_service import ZERO, arredondar, para_decimal, somar_valores
from app.services.dashboard_service import LinhaVendedora, linhas_por_vendedora
from app.services.meta_service import calcular_atingimento
from app.services.validacao import ErroDeNegocio


@dataclass(frozen=True)
class RelatorioMensal:
    mes: date
    linhas: list[LinhaVendedora]
    meta: Decimal
    vendido: Decimal
    atingimento: Decimal
    comissao_vendas: Decimal
    bonus: Decimal

    @property
    def comissao_total(self) -> Decimal:
        return self.comissao_vendas + self.bonus


@dataclass(frozen=True)
class RelatorioIndividual:
    vendedora: Vendedora
    mes: date
    meta: Decimal
    vendido: Decimal
    atingimento: Decimal
    comissao_vendas: Decimal
    bonus: Decimal
    vendas: list[Venda]
    bonus_conquistados: list[BonusCampanha]

    @property
    def comissao_total(self) -> Decimal:
        return self.comissao_vendas + self.bonus


def relatorio_mensal(s: Session, mes: date) -> RelatorioMensal:
    linhas = linhas_por_vendedora(s, mes)
    meta = somar_valores(l.meta for l in linhas)
    vendido = somar_valores(l.vendido for l in linhas)
    return RelatorioMensal(
        mes=limites_do_mes(mes)[0],
        linhas=linhas,
        meta=meta,
        vendido=vendido,
        atingimento=calcular_atingimento(meta, vendido),
        comissao_vendas=somar_valores(l.comissao for l in linhas),
        bonus=somar_valores(l.bonus for l in linhas),
    )


def relatorio_individual(s: Session, vendedora_id: int, mes: date) -> RelatorioIndividual:
    vendedora = vendedora_repository.buscar_por_id(s, vendedora_id)
    if vendedora is None:
        raise ErroDeNegocio("Vendedora não encontrada.")
    inicio, fim = limites_do_mes(mes)
    meta_obj = meta_repository.buscar(s, vendedora_id, mes)
    meta = arredondar(para_decimal(meta_obj.valor_meta)) if meta_obj else ZERO
    vendido = arredondar(venda_repository.total_vendido(s, inicio, fim, vendedora_id))
    return RelatorioIndividual(
        vendedora=vendedora,
        mes=inicio,
        meta=meta,
        vendido=vendido,
        atingimento=calcular_atingimento(meta, vendido),
        comissao_vendas=arredondar(venda_repository.total_comissao(s, inicio, fim, vendedora_id)),
        bonus=arredondar(bonus_campanha.total_do_mes(s, mes, vendedora_id)),
        vendas=venda_repository.listar_por_periodo(s, inicio, fim, vendedora_id),
        bonus_conquistados=bonus_campanha.listar_do_mes(s, mes, vendedora_id),
    )