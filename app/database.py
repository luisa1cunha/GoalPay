import os
import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    # Classe base de todos os modelos
    pass


class ErroConfiguracao(Exception):
    #O .env está ausente ou incompleto
    pass


_VARIAVEIS = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")


def _pasta_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def _montar_url() -> URL:
    arquivo_env = _pasta_base() / ".env"
    load_dotenv(arquivo_env)

    faltando = [v for v in _VARIAVEIS if not os.getenv(v)]
    if faltando:
        raise ErroConfiguracao(
            f"Configuração do banco incompleta. Faltam: {', '.join(faltando)}. "
            f"Verifique o arquivo {arquivo_env}."
        )
    try:
        porta = int(os.environ["DB_PORT"])
    except ValueError:
        raise ErroConfiguracao("DB_PORT deve ser um número") from None

    return URL.create(
        "postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=porta,
        database=os.environ["DB_NAME"],
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(_montar_url(), pool_pre_ping=True)


@lru_cache(maxsize=1)
def _fabrica_sessoes() -> sessionmaker:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


@contextmanager
def sessao() -> Iterator[Session]:
    s = _fabrica_sessoes()()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def testar_conexao() -> tuple[bool, str]:
    try:
        with get_engine().connect() as conexao:
            conexao.execute(text("SELECT 1"))
        return True, "Conectado ao banco de dados."
    except ErroConfiguracao as e:
        return False, str(e)
    except Exception as e:  # senha errada, banco desligado, host inválido
        return False, f"Não foi possível conectar ao banco: {e.__class__.__name__}"


if __name__ == "__main__":
    ok, mensagem = testar_conexao()
    print(("OK: " if ok else "ERRO: ") + mensagem)