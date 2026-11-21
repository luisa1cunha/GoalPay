from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Vendedora

def listar(s: Session, apenas_ativas: bool = False) -> list[Vendedora]:
    q = select(Vendedora).order_by(Vendedora.nome)

    if apenas_ativas:
        q = q.where(Vendedora.ativa.is_(True))
    
    return list(s.scalars(q))

def buscar_por_id(s: Session, vendedora_id: int) -> Optional[Vendedora]:
    return s.get(Vendedora, vendedora_id)  

def salvar(s: Session, vendedora: Vendedora) -> Vendedora:
    s.add(vendedora)
    s.flush()
    return vendedora