"""
Modelos SQLAlchemy del dominio.

Importarlos aqui es lo que hace que queden registrados en `Base.metadata`,
que es de donde Alembic lee el esquema para autogenerar las migraciones.
"""

from app.models.pokemon import Pokemon, PokemonType
from app.models.team import (
    Algorithm,
    OptimizationRun,
    Team,
    TeamKind,
    TeamMember,
)
from app.models.type import Type, TypeEffectiveness

__all__ = [
    "Algorithm",
    "OptimizationRun",
    "Pokemon",
    "PokemonType",
    "Team",
    "TeamKind",
    "TeamMember",
    "Type",
    "TypeEffectiveness",
]
