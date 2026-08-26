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
    types: list[str]
    stats: PokemonStats
    sprite: str
    artwork: str


class TypeEffectiveness(BaseModel):
    type: str
    multiplier: float


class PokemonDetail(PokemonSummary):
    weaknesses: list[TypeEffectiveness]
    resistances: list[TypeEffectiveness]
    immunities: list[str]
