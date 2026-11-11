from datetime import date
from decimal import Decimal
from sqlalchemy import Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Meta(Base):

    __tablename__ = "metas"
    __table_args__ = (UniqueConstraint("vendedora_id", "mes_referencia"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendedora_id: Mapped[int] = mapped_column(ForeignKey("vendedoras.id"))
    mes_referencia: Mapped[date] = mapped_column(Date)
    valor_meta: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    vendedora: Mapped["Vendedora"] = relationship(back_populates="metas")

    def __repr__(self) -> str:
        return f"<Meta vendedora={self.vendedora_id} {self.mes_referencia} {self.valor_meta}>"