from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload
from app.models import Venda, Vendedora

def salvar(s: Session, venda: Venda) -> Venda:
    s.add(venda)
    s.flush()
    return venda

def _filtrar(q, inicio: date, fim: date, vendedora_id : Optional[int], categoria_id: Optional[int] = None): 
    q = q.where(Venda.data_venda.between(inicio, fim))
    if vendedora_id is not None:
        q = q.where(Venda.vendedora_id == vendedora_id)

    if categoria_id is not None:
        q = q.where(Venda.categoria_id == categoria_id)

    return q    

def listar_por_periodo(s: Session, inicio: date, fim: date, vendedora_id : Optional[int] = None, categoria_id: Optional[int] = None) -> list[Venda]:
    q = select(Venda).options(joinedload(Venda.vendedora), joinedload(Venda.categoria))
    q = _filtrar(q, inicio, fim, vendedora_id, categoria_id)
    q = q.order_by(Venda.data_venda.desc(), Venda.id.desc())
    return list(s.scalars(q))
 
 
def total_vendido(s: Session, inicio: date, fim: date, vendedora_id: Optional[int] = None) -> Decimal:
    q = _filtrar(select(func.coalesce(func.sum(Venda.valor), 0)), inicio, fim, vendedora_id)
    return Decimal(str(s.scalar(q)))
 
 
def total_comissao(s: Session, inicio: date, fim: date, vendedora_id: Optional[int] = None) -> Decimal:
    q = _filtrar(select(func.coalesce(func.sum(Venda.valor_comissao), 0)), inicio, fim, vendedora_id)
    return Decimal(str(s.scalar(q)))
 
 
def resumo_por_vendedora(s: Session, inicio: date, fim: date) -> list[tuple[int, str, Decimal, Decimal]]:
    
    q = (
        select(
            Vendedora.id,
            Vendedora.nome,
            func.coalesce(func.sum(Venda.valor), 0),
            func.coalesce(func.sum(Venda.valor_comissao), 0),
        )
        .select_from(Vendedora)
        .outerjoin(
            Venda,
            and_(Venda.vendedora_id == Vendedora.id, Venda.data_venda.between(inicio, fim)),
        )
        .group_by(Vendedora.id, Vendedora.nome)
        .having(or_(Vendedora.ativa.is_(True), func.count(Venda.id) > 0))
        .order_by(Vendedora.nome)
    )
    return [(i, nome, Decimal(str(v)), Decimal(str(c))) for i, nome, v, c in s.execute(q)]