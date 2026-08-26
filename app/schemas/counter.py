from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.pokemon import PokemonSummary


class CounterRequest(BaseModel):
    opponent_pokemon_ids: List[int] = Field(..., min_length=1, max_length=6)
    strategy: str = "balanced"  # 'balanced', 'offensive', 'defensive'
    include_legendaries: bool = True


class TargetCountered(BaseModel):
    opponent_id: int
    opponent_name: str
    advantage_type: str
    notes: str


class CounterMember(BaseModel):
    rank: int
    id: int
    name: str
    types: List[str]
    stats: Dict[str, int]
    sprite: str
    artwork: str
    score: float
    role: str
    targets_countered: List[TargetCountered]


class TeamWeakness(BaseModel):
    type: str
    count: int
    color: str


class OpponentAnalysis(BaseModel):
    team_size: int
    pokemon: List[Dict[str, Any]]
    top_team_weaknesses: List[TeamWeakness]
    top_offensive_threats: List[TeamWeakness]


class CounterResponse(BaseModel):
    strategy: str
    team_coverage_percentage: float
    opponent_analysis: OpponentAnalysis
    counter_team: List[CounterMember]
