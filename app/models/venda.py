from datetime import date
from decimal import Decimal
from sqlalchemy import Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Venda(Base):
    
    __tablename__ = "vendas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendedora_id: Mapped[int] = mapped_column(ForeignKey("vendedoras.id"))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    data_venda: Mapped[date] = mapped_column(Date)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    percentual_aplicado: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    valor_comissao: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    pontos: Mapped[int] = mapped_column(Integer, default=0)

    vendedora: Mapped["Vendedora"] = relationship(back_populates="vendas")
    categoria: Mapped["Categoria"] = relationship(back_populates="vendas")

    @property
    def data(self) -> date:
        """Apelido usado por campanha_service (que espera v.data)."""
        return self.data_venda

    def __repr__(self) -> str:
        return f"<Venda {self.id} {self.data_venda} {self.valor}>"