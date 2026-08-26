from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.core.pokemon_repository import pokemon_repo
from app.core.type_chart import get_defensive_profile, TYPE_COLORS, POKEMON_TYPES
from app.schemas.pokemon import PokemonSummary, PokemonDetail, TypeEffectiveness

router = APIRouter()


@router.get("", response_model=List[PokemonSummary], summary="Buscar y listar Pokémon")
def list_pokemon(
    query: Optional[str] = Query(None, description="Búsqueda por nombre o ID"),
    type: Optional[str] = Query(None, description="Filtrar por tipo (fire, water, dragon...)"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """
    Retorna la lista de Pokémon con soporte para búsqueda en tiempo real y filtrado por tipo.
    """
    return pokemon_repo.get_all(query=query, type_filter=type, limit=limit, skip=skip)


@router.get("/types", summary="Obtener lista de tipos y colores")
def get_types():
    """
    Retorna los 18 tipos elementales y sus colores oficiales.
    """
    return [{"name": t, "color": TYPE_COLORS[t]} for t in POKEMON_TYPES]


@router.get("/{id_or_name}", response_model=PokemonDetail, summary="Detalle de un Pokémon con sus debilidades")
def get_pokemon_detail(id_or_name: str):
    """
    Retorna el detalle completo de un Pokémon incluyendo cálculo de debilidades y resistencias.
    """
    if id_or_name.isdigit():
        p = pokemon_repo.get_by_id(int(id_or_name))
    else:
        p = pokemon_repo.get_by_name(id_or_name)

    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokémon no encontrado")

    def_profile = get_defensive_profile(p["types"])
    weaknesses = []
    resistances = []
    immunities = []

    for atk_type, mult in def_profile.items():
        if mult > 1.0:
            weaknesses.append({"type": atk_type, "multiplier": mult})
        elif mult == 0.0:
            immunities.append(atk_type)
        elif mult < 1.0:
            resistances.append({"type": atk_type, "multiplier": mult})

    return {
        **p,
        "weaknesses": sorted(weaknesses, key=lambda x: x["multiplier"], reverse=True),
        "resistances": sorted(resistances, key=lambda x: x["multiplier"]),
        "immunities": immunities
    }
