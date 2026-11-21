from typing import Optional
from sqlalchemy.orm import Session
from app.models import Vendedora
from app.repositories import vendedora_repository as repo
from app.services.validacao import ErroDeNegocio, texto_obrigatorio

def _obter(s: Session, vendedora_id: int) -> Optional[Vendedora]:
    vendedora = repo.buscar_por_id(s, vendedora_id)
    if vendedora is None:
        raise ErroDeNegocio(f"Vendedora {vendedora_id} não encontrada.")
    return vendedora

def _nome_repetido(s: Session, nome: str, ignorar_id: Optional[int] = None) -> bool:
    return any(v.nome.casefold() == nome.casefold() for v in repo.listar(s) if v.id != ignorar_id)

def listar(s: Session, apenas_ativas: bool = False) -> list[Vendedora]:
    return repo.listar(s, apenas_ativas=apenas_ativas)

def cadastrar(s: Session, nome: str, contato: Optional[str] = None) -> Vendedora:
    nome = texto_obrigatorio(nome, "nome", 100)
    if _nome_repetido(s, nome):
        raise ErroDeNegocio(f"Vendedora '{nome}' já cadastrada.")
    contato = (contato or "").strip() or None
    vendedora = Vendedora(nome=nome, contato=contato)
    return repo.salvar(s, vendedora)

def editar(s: Session, vendedora_id: int, nome: str, contato: Optional[str] = None, ativa: bool = True) -> Vendedora:
    vendedora = _obter(s, vendedora_id)
    nome = texto_obrigatorio(nome, "nome", 100)
    if _nome_repetido(s, nome, ignorar_id=vendedora.id):
        raise ErroDeNegocio(f"Vendedora '{nome}' já cadastrada.")
    contato = (contato or "").strip() or None
    vendedora.nome = nome
    vendedora.contato = contato
    vendedora.ativa = ativa
    return repo.salvar(s, vendedora)

def definir_ativa(s: Session, vendedora_id: int, ativa: bool) -> Vendedora:
    vendedora = _obter(s, vendedora_id)
    vendedora.ativa = ativa
    return repo.salvar(s, vendedora)