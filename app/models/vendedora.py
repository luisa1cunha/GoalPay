from typing import Optional
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Vendedora(Base):
    __tablename__ = "vendedoras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    contato: Mapped[Optional[str]] = mapped_column(String(120))
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)

    metas: Mapped[list["Meta"]] = relationship(back_populates="vendedora")
    vendas: Mapped[list["Venda"]] = relationship(back_populates="vendedora")
    bonus: Mapped[list["BonusCampanha"]] = relationship(back_populates="vendedora")

    def __repr__(self) -> str:
        return f"<Vendedora {self.id} {self.nome}>"