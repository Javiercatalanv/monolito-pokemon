from typing import List, Optional, Dict
from pydantic import BaseModel


class PokemonStats(BaseModel):
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    bst: int


class PokemonSummary(BaseModel):
    id: int
    name: str
    types: List[str]
    stats: PokemonStats
    sprite: str
    artwork: str


class TypeEffectiveness(BaseModel):
    type: str
    multiplier: float


class PokemonDetail(PokemonSummary):
    weaknesses: List[TypeEffectiveness]
    resistances: List[TypeEffectiveness]
    immunities: List[str]
