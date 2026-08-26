"""Equipos, sus miembros y el registro de ejecuciones del optimizador."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.pokemon import Pokemon


class TeamKind(StrEnum):
    """Origen de un equipo: cargado por el usuario o producido por el optimizador."""

    RIVAL = "rival"
    GENERATED = "generated"


class Algorithm(StrEnum):
    """
    Algoritmos seleccionables por API. Los cinco entran en la tabla de
    benchmark del informe, por eso los baselines son ciudadanos de primera.
    """

    RANDOM = "random"
    HEURISTIC_V1 = "heuristic_v1"
    GREEDY = "greedy"
    GREEDY_LOCAL_SEARCH = "greedy_local_search"
    MULTISTART_LOCAL_SEARCH = "multistart_local_search"


class Team(Base):
    """Un equipo de hasta 6 Pokemon."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(120), default=None)
    kind: Mapped[TeamKind] = mapped_column(String(16), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    members: Mapped[list[TeamMember]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
        order_by="TeamMember.slot",
    )

    def __repr__(self) -> str:
        return f"<Team {self.id} {self.kind} ({len(self.members)})>"


class TeamMember(Base):
    """
    Pertenencia de un Pokemon a un equipo. La PK compuesta (team_id, slot)
    impide dos Pokemon en la misma posicion, y el unique (team_id, pokemon_id)
    impide repetir un Pokemon dentro del mismo equipo.
    """

    __tablename__ = "team_members"
    __table_args__ = (
        CheckConstraint("slot BETWEEN 1 AND 6", name="ck_team_members_slot"),
        UniqueConstraint("team_id", "pokemon_id", name="uq_team_members_no_duplicates"),
    )

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True
    )
    slot: Mapped[int] = mapped_column(primary_key=True, doc="Posicion 1..6")
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.id", ondelete="RESTRICT"))

    team: Mapped[Team] = relationship(back_populates="members")
    pokemon: Mapped[Pokemon] = relationship(back_populates="team_memberships")

    def __repr__(self) -> str:
        return f"<TeamMember t{self.team_id} slot{self.slot} p{self.pokemon_id}>"


class OptimizationRun(Base):
    """
    Traza persistida de una ejecucion del optimizador.

    Es la tabla que hace que PostgreSQL deje de ser decorativo: alimenta el
    endpoint de historial y la tabla de benchmark del informe, y permite
    comparar algoritmos sobre los mismos equipos rivales.
    """

    __tablename__ = "optimization_runs"
    __table_args__ = (
        CheckConstraint("coverage_pct BETWEEN 0 AND 100", name="ck_optimization_runs_coverage"),
        CheckConstraint("elapsed_ms >= 0", name="ck_optimization_runs_elapsed"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    rival_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    result_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))

    algorithm: Mapped[Algorithm] = mapped_column(String(32), index=True)
    objective_value: Mapped[float] = mapped_column(Float, doc="J(T) del equipo elegido")
    coverage_pct: Mapped[float] = mapped_column(Float, doc="Cobertura defensiva 0-100")
    iterations: Mapped[int] = mapped_column(default=0, doc="Iteraciones de busqueda local")
    elapsed_ms: Mapped[int] = mapped_column(default=0)
    params: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(String, "sqlite"),
        default=dict,
        doc="Pesos alfa/beta/gamma/delta, semilla y demas parametros de la request",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    rival_team: Mapped[Team] = relationship(foreign_keys=[rival_team_id])
    result_team: Mapped[Team] = relationship(foreign_keys=[result_team_id])

    def __repr__(self) -> str:
        return f"<OptimizationRun {self.id} {self.algorithm} J={self.objective_value:.3f}>"
