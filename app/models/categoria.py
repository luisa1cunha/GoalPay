from decimal import Decimal
from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

TIPO_VENDA = "VENDA"
TIPO_SERVICO = "SERVICO"


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)
    tipo: Mapped[str] = mapped_column(String(10))  # VENDA ou SERVICO
    percentual_comissao: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)

    vendas: Mapped[list["Venda"]] = relationship(back_populates="categoria")
    campanhas: Mapped[list["Campanha"]] = relationship(back_populates="categoria")

    def __repr__(self) -> str:
        return f"<Categoria {self.id} {self.nome} {self.percentual_comissao}%>"