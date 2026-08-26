"""Tipos elementales y la matriz de efectividad 18x18."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.pokemon import PokemonType


class Type(Base):
    """Uno de los 18 tipos elementales. Tabla de 18 filas, estable."""

    __tablename__ = "types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    color: Mapped[str] = mapped_column(String(7), doc="Color hexadecimal para la UI")

    pokemon_links: Mapped[list[PokemonType]] = relationship(back_populates="type")

    def __repr__(self) -> str:
        return f"<Type {self.name}>"


class TypeEffectiveness(Base):
    """
    Una celda de la matriz 18x18: cuanto multiplica un tipo atacante contra un
    tipo defensor. Son 324 filas y es la fuente de verdad del algoritmo de
    cobertura; `core/type_chart.py` queda como seed y fallback offline.
    """

    __tablename__ = "type_effectiveness"
    __table_args__ = (
        CheckConstraint(
            "multiplier IN (0, 0.5, 1, 2)",
            name="ck_type_effectiveness_multiplier",
        ),
    )

    attacking_type_id: Mapped[int] = mapped_column(
        ForeignKey("types.id", ondelete="CASCADE"), primary_key=True
    )
    defending_type_id: Mapped[int] = mapped_column(
        ForeignKey("types.id", ondelete="CASCADE"), primary_key=True
    )
    multiplier: Mapped[float] = mapped_column(Float, doc="0, 0.5, 1 o 2")

    attacking_type: Mapped[Type] = relationship(foreign_keys=[attacking_type_id])
    defending_type: Mapped[Type] = relationship(foreign_keys=[defending_type_id])

    def __repr__(self) -> str:
        return (
            f"<TypeEffectiveness {self.attacking_type_id}->"
            f"{self.defending_type_id} x{self.multiplier}>"
        )
