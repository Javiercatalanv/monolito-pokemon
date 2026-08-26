"""Pokemon y su relacion N:M con los tipos."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.type import Type


class Pokemon(Base):
    """
    Un Pokemon con sus stats base. `bst` se guarda materializado en vez de
    calcularse en cada consulta porque el pool de candidatos se filtra por ese
    valor en cada ejecucion del optimizador.
    """

    __tablename__ = "pokemon"
    __table_args__ = (
        CheckConstraint("bst > 0", name="ck_pokemon_bst_positive"),
        Index("ix_pokemon_bst", "bst"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pokeapi_id: Mapped[int] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    generation: Mapped[int | None] = mapped_column(default=None)
    is_legendary: Mapped[bool] = mapped_column(default=False)

    hp: Mapped[int]
    attack: Mapped[int]
    defense: Mapped[int]
    sp_attack: Mapped[int]
    sp_defense: Mapped[int]
    speed: Mapped[int]
    bst: Mapped[int] = mapped_column(doc="Base stat total, suma de las 6 stats")

    sprite_url: Mapped[str | None] = mapped_column(String(255), default=None)
    artwork_url: Mapped[str | None] = mapped_column(String(255), default=None)
    synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        doc="Ultima sincronizacion desde PokeAPI",
    )

    type_links: Mapped[list[PokemonType]] = relationship(
        back_populates="pokemon",
        cascade="all, delete-orphan",
        order_by="PokemonType.slot",
    )
    @property
    def types(self) -> list[str]:
        """Nombres de tipo en orden de slot, la forma en que los consume el motor."""
        return [link.type.name for link in self.type_links]

    def __repr__(self) -> str:
        return f"<Pokemon #{self.pokeapi_id} {self.name}>"


class PokemonType(Base):
    """
    Relacion N:M entre Pokemon y Type. `slot` distingue tipo primario (1) de
    secundario (2), que importa para el desempate por diversidad del equipo.
    """

    __tablename__ = "pokemon_types"
    __table_args__ = (CheckConstraint("slot IN (1, 2)", name="ck_pokemon_types_slot"),)

    pokemon_id: Mapped[int] = mapped_column(
        ForeignKey("pokemon.id", ondelete="CASCADE"), primary_key=True
    )
    type_id: Mapped[int] = mapped_column(
        ForeignKey("types.id", ondelete="CASCADE"), primary_key=True
    )
    slot: Mapped[int] = mapped_column(doc="1 = tipo primario, 2 = secundario")

    pokemon: Mapped[Pokemon] = relationship(back_populates="type_links")
    type: Mapped[Type] = relationship(back_populates="pokemon_links")

    def __repr__(self) -> str:
        return f"<PokemonType p{self.pokemon_id} t{self.type_id} slot{self.slot}>"
