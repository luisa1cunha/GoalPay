from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Categoria
from app.models.categoria import TIPO_SERVICO, TIPO_VENDA
from app.repositories import categoria_repository as repo
from app.services.validacao import ErroDeNegocio, texto_obrigatorio, decimal_ou_erro, inteiro_ou_erro
from app.services.comissao_service import arredondar

TIPOS = (TIPO_VENDA, TIPO_SERVICO)

def _validar(s: Session, nome, tipo, percentual, ignorar_id: Optional[int] = None) -> tuple[str, str, Decimal]:
    nome = texto_obrigatorio(nome, "nome da categoria", 80)
    if tipo not in TIPOS:
        raise ErroDeNegocio(f"Tipo inválido: {tipo}.")
    percentual = arredondar(decimal_ou_erro(percentual, "percentual"))
    if percentual < 0 or percentual > 100:
        raise ErroDeNegocio(f"Percentual inválido: {percentual}.")
    if repo.existe_nome(s, nome, ignorar_id=ignorar_id):
        raise ErroDeNegocio(f"Categoria '{nome}' já cadastrada.")
    return nome, tipo, percentual

def listar(s: Session, apenas_ativas: bool = False) -> list[Categoria]:
    return repo.listar(s, apenas_ativas)

def cadastrar(s: Session, nome, tipo, percentual) -> Categoria:
    nome, tipo, percentual = _validar(s, nome, tipo, percentual)
    categoria = Categoria(nome=nome, tipo=tipo, percentual_comissao=percentual)
    return repo.salvar(s, categoria)

def editar(s: Session, categoria_id: int, nome, tipo, percentual, ativa: bool = True) -> Categoria:
    categoria = repo.buscar_por_id(s, categoria_id)
    if categoria is None:
        raise ErroDeNegocio(f"Categoria {categoria_id} não encontrada.")
    nome, tipo, percentual = _validar(s, nome, tipo, percentual, ignorar_id=categoria.id)
    categoria.nome = nome
    categoria.tipo = tipo
    categoria.percentual_comissao = percentual
    categoria.ativa = ativa
    return repo.salvar(s, categoria)

