from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.models import BonusCampanha
from app.models import Campanha as CampanhaDB
from app.repositories import bonus_campanha, campanha_repository, categoria_repository, venda_repository
from app.repositories.periodo_repository import primeiro_dia_do_mes
from app.services.campanha_service import COMBO, PONTUACAO, calcular_bonus
from app.services.comissao_service import arredondar
from app.services.validacao import ErroDeNegocio, decimal_ou_erro, inteiro_ou_erro, texto_obrigatorio


def listar(s: Session, apenas_ativas: bool = False) -> list[CampanhaDB]:
    return campanha_repository.listar(s, apenas_ativas)


def cadastrar(s: Session, nome, tipo: str, meta_quantidade, valor_bonus, data_inicio: date, data_fim: date, categoria_id: Optional[int] = None) -> CampanhaDB:
    nome = texto_obrigatorio(nome, "o nome da campanha", 120)
    if tipo not in (PONTUACAO, COMBO):
        raise ErroDeNegocio("Tipo de campanha inválido.")
    meta = inteiro_ou_erro(meta_quantidade, "a meta")
    if meta <= 0:
        raise ErroDeNegocio("A meta deve ser maior que zero.")
    bonus = arredondar(decimal_ou_erro(valor_bonus, "o bônus"))
    if bonus <= 0:
        raise ErroDeNegocio("O bônus deve ser maior que zero.")
    if data_fim < data_inicio:
        raise ErroDeNegocio("A data final não pode ser anterior à inicial.")
    if tipo == COMBO:
        if categoria_id is None:
            raise ErroDeNegocio("Campanha de combo precisa de uma categoria.")
        if categoria_repository.buscar_por_id(s, categoria_id) is None:
            raise ErroDeNegocio("Categoria não encontrada.")
    else:
        categoria_id = None  # campanha de pontuação vale para todas as categorias
    return campanha_repository.salvar(
        s,
        CampanhaDB(
            nome=nome, tipo=tipo, meta_quantidade=meta, valor_bonus=bonus,
            data_inicio=data_inicio, data_fim=data_fim, categoria_id=categoria_id,
        ),
    )


def definir_ativa(s: Session, campanha_id: int, ativa: bool) -> CampanhaDB:
    campanha = campanha_repository.buscar_por_id(s, campanha_id)
    if campanha is None:
        raise ErroDeNegocio("Campanha não encontrada.")
    campanha.ativa = ativa
    return campanha_repository.salvar(s, campanha)


def conceder_bonus_pendentes(s: Session, vendedora_id: int, dia: date) -> list[BonusCampanha]:
    #Confere as campanhas vigentes em `dia` e grava o bônus das que a vendedora atingiu. Cada campanha paga uma única vez por vendedora
    concedidos = []
    for campanha in campanha_repository.listar_vigentes(s, dia):
        if bonus_campanha.ja_concedido(s, campanha.id, vendedora_id):
            continue
        vendas = venda_repository.listar_por_periodo(
            s, campanha.data_inicio, campanha.data_fim, vendedora_id
        )
        valor = calcular_bonus(campanha, vendas)
        if valor > 0:
            concedidos.append(
                bonus_campanha.salvar(
                    s,
                    BonusCampanha(
                        campanha_id=campanha.id,
                        vendedora_id=vendedora_id,
                        mes_referencia=primeiro_dia_do_mes(dia),
                        valor_bonus=valor,
                    ),
                )
            )
    return concedidos