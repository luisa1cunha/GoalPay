from datetime import date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models import Campanha


def listar(s: Session, apenas_ativas: bool = False) -> list[Campanha]:
    q = select(Campanha).options(joinedload(Campanha.categoria)).order_by(Campanha.data_inicio.desc())
    if apenas_ativas:
        q = q.where(Campanha.ativa.is_(True))
    return list(s.scalars(q))


def listar_vigentes(s: Session, dia: date) -> list[Campanha]:
    q = select(Campanha).where(
        Campanha.ativa.is_(True),
        Campanha.data_inicio <= dia,
        Campanha.data_fim >= dia,
    )
    return list(s.scalars(q))


def buscar_por_id(s: Session, campanha_id: int) -> Optional[Campanha]:
    return s.get(Campanha, campanha_id)


def salvar(s: Session, campanha: Campanha) -> Campanha:
    s.add(campanha)
    s.flush()
    return campanha