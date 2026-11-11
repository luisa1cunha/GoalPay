from datetime import date
from decimal import Decimal
from sqlalchemy import Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class BonusCampanha(Base):

    __tablename__ = "bonus_campanha"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campanha_id: Mapped[int] = mapped_column(ForeignKey("campanhas.id"))
    vendedora_id: Mapped[int] = mapped_column(ForeignKey("vendedoras.id"))
    mes_referencia: Mapped[date] = mapped_column(Date)
    valor_bonus: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    campanha: Mapped["Campanha"] = relationship(back_populates="bonus")
    vendedora: Mapped["Vendedora"] = relationship(back_populates="bonus")

    def __repr__(self) -> str:
        return f"<BonusCampanha campanha={self.campanha_id} vendedora={self.vendedora_id} {self.valor_bonus}>"