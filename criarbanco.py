
import re
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

from app.database import _montar_url

url = _montar_url()
nome = url.database
if not re.fullmatch(r"[A-Za-z0-9_]+", nome):
    sys.exit(f"DB_NAME inválido: {nome!r} (use só letras, números e _)")

arquivo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("goalpay_schema.sql")
if not arquivo.exists():
    sys.exit(f"Arquivo não encontrado: {arquivo.resolve()}")

admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
with admin.connect() as c:
    existe = c.execute(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": nome}).scalar()
    if existe:
        print(f"O banco '{nome}' já existe.")
    else:
        c.execute(text(f'CREATE DATABASE "{nome}"'))
        print(f"Banco '{nome}' criado.")

engine = create_engine(url)
with engine.begin() as c:
    tem_tabelas = c.execute(text("SELECT to_regclass('public.vendas')")).scalar()
    if tem_tabelas:
        print("As tabelas já existem. Nada foi alterado.")
    else:
        c.exec_driver_sql(arquivo.read_text(encoding="utf-8"))
        print("Tabelas criadas.")