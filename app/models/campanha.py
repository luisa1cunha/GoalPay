from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Campanha(Base):
    """PONTUACAO: meta_quantidade = pontos. COMBO: meta_quantidade = nº de vendas
    da categoria_id (obrigatória no combo)."""

    __tablename__ = "campanhas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    categoria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categorias.id"))
    nome: Mapped[str] = mapped_column(String(120))
    tipo: Mapped[str] = mapped_column(String(10))  # PONTUACAO ou COMBO
    meta_quantidade: Mapped[int] = mapped_column(Integer)
    valor_bonus: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    data_inicio: Mapped[date] = mapped_column(Date)
    data_fim: Mapped[date] = mapped_column(Date)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)

    categoria: Mapped[Optional["Categoria"]] = relationship(back_populates="campanhas")
    bonus: Mapped[list["BonusCampanha"]] = relationship(back_populates="campanha")

    def __repr__(self) -> str:
        return f"<Campanha {self.id} {self.nome} ({self.tipo})>"