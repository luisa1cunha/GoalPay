from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Categoria


def listar(s: Session, apenas_ativas: bool = False) -> list[Categoria]:
    q = select(Categoria).order_by(Categoria.nome)
    if apenas_ativas:
        q = q.where(Categoria.ativa.is_(True))
    return list(s.scalars(q))


def buscar_por_id(s: Session, categoria_id: int) -> Optional[Categoria]:
    return s.get(Categoria, categoria_id)


def buscar_por_nome(s: Session, nome: str) -> Optional[Categoria]:
    return s.scalars(select(Categoria).where(Categoria.nome == nome)).first()


def salvar(s: Session, categoria: Categoria) -> Categoria:
    s.add(categoria)
    s.flush()
    return categoria