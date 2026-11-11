from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.models import Meta, Vendedora
from app.repositories.periodo import primeiro_dia_do_mes


def buscar(s: Session, vendedora_id: int, mes: date) -> Optional[Meta]:
    q = select(Meta).where(
        Meta.vendedora_id == vendedora_id,
        Meta.mes_referencia == primeiro_dia_do_mes(mes),
    )
    return s.scalars(q).first()


def definir(s: Session, vendedora_id: int, mes: date, valor: Decimal) -> Meta:
    meta = buscar(s, vendedora_id, mes)
    if meta is None:
        meta = Meta(
            vendedora_id=vendedora_id,
            mes_referencia=primeiro_dia_do_mes(mes),
            valor_meta=valor,
        )
        s.add(meta)
    else:
        meta.valor_meta = valor
    s.flush()
    return meta


def listar_do_mes(s: Session, mes: date) -> list[Meta]:
    q = (
        select(Meta)
        .join(Vendedora)
        .options(joinedload(Meta.vendedora))
        .where(Meta.mes_referencia == primeiro_dia_do_mes(mes))
        .order_by(Vendedora.nome)
    )
    return list(s.scalars(q))


def total_do_mes(s: Session, mes: date) -> Decimal:
    q = select(func.coalesce(func.sum(Meta.valor_meta), 0)).where(
        Meta.mes_referencia == primeiro_dia_do_mes(mes)
    )
    return Decimal(str(s.scalar(q)))


def historico_da_unidade(s: Session) -> list[tuple[date, Decimal]]:
    q = (
        select(Meta.mes_referencia, func.sum(Meta.valor_meta))
        .group_by(Meta.mes_referencia)
        .order_by(Meta.mes_referencia.desc())
    )
    return [(mes, Decimal(str(total))) for mes, total in s.execute(q)]