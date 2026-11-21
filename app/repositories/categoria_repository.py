from typing import Optional
from sqlalchemy import func, select
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


def existe_nome(s: Session, nome: str, ignorar_id: Optional[int] = None) -> bool:
    q = select(Categoria.id).where(func.lower(Categoria.nome) == func.lower(nome))
    if ignorar_id is not None:
        q = q.where(Categoria.id != ignorar_id)
    return s.scalars(q).first() is not None


def salvar(s: Session, categoria: Categoria) -> Categoria:
    s.add(categoria)
    s.flush()
    return categoria