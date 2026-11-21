from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories import bonus_campanha, meta_repository, venda_repository
from app.repositories.periodo_repository import limites_do_mes
from app.services.comissao_service import ZERO, arredondar, para_decimal
from app.services.meta_service import calcular_atingimento, calcular_valor_por_dia, calcular_valor_restante


@dataclass(frozen=True)
class LinhaVendedora:
    vendedora_id: int
    nome: str
    meta: Decimal
    vendido: Decimal
    atingimento: Decimal
    comissao: Decimal  # comissão das vendas
    bonus: Decimal  # bônus de campanhas

    @property
    def total(self) -> Decimal:
        return self.comissao + self.bonus


@dataclass(frozen=True)
class Dashboard:
    mes: date
    meta: Decimal
    vendido: Decimal
    atingimento: Decimal
    restante: Decimal
    valor_por_dia: Optional[Decimal]  # None se o mês já terminou
    dias_restantes: int
    comissao_vendas: Decimal
    bonus: Decimal
    variacao_vs_mes_anterior: Optional[Decimal]  # em %, None se o mês anterior não teve vendas
    comparativo: list[tuple[date, Decimal]]  # últimos 6 meses, do mais antigo ao atual
    por_vendedora: list[LinhaVendedora]

    @property
    def comissao_total(self) -> Decimal:
        return self.comissao_vendas + self.bonus


def linhas_por_vendedora(s: Session, mes: date) -> list[LinhaVendedora]:
    inicio, fim = limites_do_mes(mes)
    metas = {m.vendedora_id: m.valor_meta for m in meta_repository.listar_do_mes(s, mes)}
    bonus = bonus_campanha.totais_por_vendedora(s, mes)
    linhas = []
    for vendedora_id, nome, vendido, comissao in venda_repository.resumo_por_vendedora(s, inicio, fim):
        meta = arredondar(para_decimal(metas.get(vendedora_id, ZERO)))
        vendido = arredondar(vendido)
        linhas.append(
            LinhaVendedora(
                vendedora_id=vendedora_id,
                nome=nome,
                meta=meta,
                vendido=vendido,
                atingimento=calcular_atingimento(meta, vendido),
                comissao=arredondar(comissao),
                bonus=arredondar(bonus.get(vendedora_id, ZERO)),
            )
        )
    return linhas


def montar_dashboard(s: Session, mes: date, hoje: Optional[date] = None) -> Dashboard:
    hoje = hoje or date.today()
    inicio, fim = limites_do_mes(mes)

    meta = arredondar(meta_repository.total_do_mes(s, mes))
    vendido = arredondar(venda_repository.total_vendido(s, inicio, fim))
    restante = calcular_valor_restante(meta, vendido)

    if hoje > fim:
        valor_por_dia, dias_restantes = None, 0
    else:
        referencia = max(hoje, inicio)
        dias_restantes = (fim - referencia).days + 1
        valor_por_dia = calcular_valor_por_dia(meta, vendido, referencia, fim)

    fim_anterior = inicio - timedelta(days=1)
    inicio_anterior = fim_anterior.replace(day=1)
    vendido_anterior = venda_repository.total_vendido(s, inicio_anterior, fim_anterior)
    variacao = (
        arredondar((vendido - vendido_anterior) / vendido_anterior * 100)
        if vendido_anterior > 0
        else None
    )

    comparativo = []
    ini, fi = inicio, fim
    for _ in range(6):
        comparativo.append((ini, arredondar(venda_repository.total_vendido(s, ini, fi))))
        fi = ini - timedelta(days=1)
        ini = fi.replace(day=1)
    comparativo.reverse()

    return Dashboard(
        mes=inicio,
        meta=meta,
        vendido=vendido,
        atingimento=calcular_atingimento(meta, vendido),
        restante=restante,
        valor_por_dia=valor_por_dia,
        dias_restantes=dias_restantes,
        comissao_vendas=arredondar(venda_repository.total_comissao(s, inicio, fim)),
        bonus=arredondar(bonus_campanha.total_do_mes(s, mes)),
        variacao_vs_mes_anterior=variacao,
        comparativo=comparativo,
        por_vendedora=linhas_por_vendedora(s, mes),
    )