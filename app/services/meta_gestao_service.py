from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Meta
from app.repositories import meta_repository, venda_repository, vendedora_repository
from app.repositories.periodo_repository import limites_do_mes
from app.services.comissao_service import arredondar
from app.services.meta_service import calcular_atingimento
from app.services.validacao import ErroDeNegocio, decimal_ou_erro

EM_ANDAMENTO = "EM_ANDAMENTO"
ATINGIDA = "ATINGIDA"
NAO_ATINGIDA = "NAO_ATINGIDA"


@dataclass(frozen=True)
class LinhaHistorico:
    mes: date
    meta: Decimal
    realizado: Decimal
    atingimento: Decimal
    situacao: str


def definir_metas_do_mes(s: Session, mes: date, valores: dict) -> list[Meta]:
    # valores são o vendedora_id e a meta de cada vendedora 
    if not valores:
        raise ErroDeNegocio("Informe ao menos uma meta.")
    convertidos = {}
    for vendedora_id, valor in valores.items():
        meta = arredondar(decimal_ou_erro(valor, "a meta"))
        if meta < 0:
            raise ErroDeNegocio("A meta não pode ser negativa.")
        if vendedora_repository.buscar_por_id(s, vendedora_id) is None:
            raise ErroDeNegocio("Vendedora não encontrada.")
        convertidos[vendedora_id] = meta
    return [meta_repository.definir(s, vid, mes, valor) for vid, valor in convertidos.items()]


def meta_da_unidade(s: Session, mes: date) -> Decimal:
    return arredondar(meta_repository.total_do_mes(s, mes))


def historico(s: Session, hoje: Optional[date] = None) -> list[LinhaHistorico]:
    #Meta x realizado, do mês mais recente para o mais antigo
    hoje = hoje or date.today()
    linhas = []
    for mes, meta in meta_repository.historico_da_unidade(s):
        inicio, fim = limites_do_mes(mes)
        meta = arredondar(meta)
        realizado = arredondar(venda_repository.total_vendido(s, inicio, fim))
        if hoje <= fim:
            situacao = EM_ANDAMENTO
        elif realizado >= meta:
            situacao = ATINGIDA
        else:
            situacao = NAO_ATINGIDA
        linhas.append(
            LinhaHistorico(mes, meta, realizado, calcular_atingimento(meta, realizado), situacao)
        )
    return linhas