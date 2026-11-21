from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from app.models import BonusCampanha, Venda
from app.repositories import categoria_repository, venda_repository, vendedora_repository
from app.services import campanha_gestao_service
from app.services.comissao_service import arredondar, calcular_comissao
from app.services.validacao import ErroDeNegocio, decimal_ou_erro, inteiro_ou_erro

@dataclass(frozen=True)
class ResultadoVenda:
    venda: Venda
    bonus_concedidos : list[BonusCampanha]

def registrar_venda(s: Session, vendedora_id: int, categoria_id: int, data_venda: date, valor, pontos = 0, hoje: Optional[date] = None) -> ResultadoVenda:
    hoje = hoje or date.today()

    vendedora = vendedora_repository.buscar_por_id(s, vendedora_id)
    if vendedora is None or not vendedora.ativa:
        raise ErroDeNegocio("Selecione uma vendedora ativa.")
    categoria = categoria_repository.buscar_por_id(s, categoria_id)

    if categoria is None or not categoria.ativa:
        raise ErroDeNegocio("Selecione uma categoria ativa.")
    
    valor = arredondar(decimal_ou_erro(valor, "o valor"))
    if valor <= 0:
        raise ErroDeNegocio("O valor da venda deve ser maior que zero")
    
    pontos = inteiro_ou_erro(pontos, "os pontos")
    if pontos < 0:
        raise ErroDeNegocio("Os pontos não podem ser negativos")
    if data_venda > hoje:
        raise ErroDeNegocio("A data da venda nao pode ser futura") 
    
    percentual = categoria.percentual_comissao
    venda = venda_repository.salvar(s, Venda(                         
        vendedora_id = vendedora_id,
        categoria_id = categoria_id,
        data_venda = data_venda,
        valor = valor,
        percentual_aplicado = percentual,
        valor_comissao = calcular_comissao(valor, percentual),
        pontos = pontos
    ))
    
    bonus = campanha_gestao_service.conceder_bonus_pendentes(s, vendedora_id, data_venda)
    return ResultadoVenda(venda=venda, bonus_concedidos=bonus)

def listar_vendas(s: Session, inicio: date, fim: date, vendedora_id: Optional[int] = None, categoria_id: Optional[int] = None) -> list[Venda]:
    if inicio > fim:
        raise ErroDeNegocio("A data de inicio não pode ser posterior à final.")
    
    return venda_repository.listar_por_periodo(s, inicio, fim, vendedora_id, categoria_id)

def total_por_periodo(s: Session, inicio: date, fim: date) -> tuple[Decimal, Decimal]:
    if inicio > fim:
        raise ErroDeNegocio("A data de inicio não pode ser posterior à final.")
    
    return arredondar(venda_repository.total_vendido(s, inicio, fim)), arredondar(venda_repository.total_comissao(s, inicio, fim))


def totais_do_periodo(s: Session, inicio: date, fim: date) -> tuple[Decimal, Decimal]:
    return total_por_periodo(s, inicio, fim)