from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.models import BonusCampanha
from app.repositories.periodo import primeiro_dia_do_mes


def salvar(s: Session, bonus: BonusCampanha) -> BonusCampanha:
    s.add(bonus)
    s.flush()
    return bonus


def existe(s: Session, campanha_id: int, vendedora_id: int, mes: date) -> bool:
    q = select(BonusCampanha.id).where(
        BonusCampanha.campanha_id == campanha_id,
        BonusCampanha.vendedora_id == vendedora_id,
        BonusCampanha.mes_referencia == primeiro_dia_do_mes(mes),
    )
    return s.scalars(q).first() is not None


def listar_do_mes(s: Session, mes: date, vendedora_id: Optional[int] = None) -> list[BonusCampanha]:
    q = (
        select(BonusCampanha)
        .options(joinedload(BonusCampanha.campanha), joinedload(BonusCampanha.vendedora))
        .where(BonusCampanha.mes_referencia == primeiro_dia_do_mes(mes))
    )
    if vendedora_id is not None:
        q = q.where(BonusCampanha.vendedora_id == vendedora_id)
    return list(s.scalars(q))


def total_do_mes(s: Session, mes: date, vendedora_id: Optional[int] = None) -> Decimal:
    q = select(func.coalesce(func.sum(BonusCampanha.valor_bonus), 0)).where(
        BonusCampanha.mes_referencia == primeiro_dia_do_mes(mes)
    )
    if vendedora_id is not None:
        q = q.where(BonusCampanha.vendedora_id == vendedora_id)
    return Decimal(str(s.scalar(q)))


def totais_por_vendedora(s: Session, mes: date) -> dict[int, Decimal]:
    q = (
        select(BonusCampanha.vendedora_id, func.sum(BonusCampanha.valor_bonus))
        .where(BonusCampanha.mes_referencia == primeiro_dia_do_mes(mes))
        .group_by(BonusCampanha.vendedora_id)
    )
    return {vid: Decimal(str(total)) for vid, total in s.execute(q)}