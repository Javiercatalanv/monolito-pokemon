from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.core.pokemon_repository import pokemon_repo
from app.services.counter_engine import counter_engine
from app.schemas.counter import CounterRequest, CounterResponse, OpponentAnalysis

router = APIRouter()

# Presets de equipos famosos para pruebas rápidas
PRESET_TEAMS = [
    {
        "name": "Equipo Campeona Cynthia (Sinnoh)",
        "description": "Garchomp, Lucario, Togekiss, Spiritomb, Milotic, Roserade",
        "pokemon_ids": [445, 448, 468, 442, 350, 407]
    },
    {
        "name": "Equipo Entrenador Red (Mt. Silver)",
        "description": "Pikachu, Charizard, Blastoise, Venusaur, Snorlax, Lapras",
        "pokemon_ids": [25, 6, 9, 3, 143, 131]
    },
    {
        "name": "Equipo Dragones / Pseudo-Legendarios",
        "description": "Dragonite, Tyranitar, Salamence, Metagross, Garchomp, Dragapult",
        "pokemon_ids": [149, 248, 373, 376, 445, 887]
    },
    {
        "name": "Equipo Competitivo Clima Lluvia (Rain Team)",
        "description": "Pelipper, Kingdra, Swampert, Ferrothorn, Zapdos, Barraskewda",
        "pokemon_ids": [279, 230, 260, 598, 145, 834]
    }
]


@router.get("/presets", summary="Obtener equipos predefinidos de prueba")
def get_presets():
    """
    Retorna una lista de equipos preconfigurados con sus datos e imágenes.
    """
    enriched_presets = []
    for pr in PRESET_TEAMS:
        p_list = [pokemon_repo.get_by_id(pid) for pid in pr["pokemon_ids"] if pokemon_repo.get_by_id(pid)]
        enriched_presets.append({
            "name": pr["name"],
            "description": pr["description"],
            "pokemon": p_list
        })
    return enriched_presets


@router.post("/analyze", response_model=OpponentAnalysis, summary="Analizar debilidades de un equipo rival")
def analyze_opponent_team(request: CounterRequest):
    """
    Calcula debilidades grupales, amenazas ofensivas y resumen de cada integrante del equipo rival.
    """
    opponent_pokemon = [pokemon_repo.get_by_id(pid) for pid in request.opponent_pokemon_ids if pokemon_repo.get_by_id(pid)]
    if not opponent_pokemon:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se encontraron Pokémon válidos con esos IDs")

    return counter_engine.analyze_team(opponent_pokemon)


@router.post("/generate", response_model=CounterResponse, summary="Generar el Counter Team óptimo")
def generate_counter_team(request: CounterRequest):
    """
    Ejecuta el algoritmo multi-estrategia (balanced, offensive, defensive) para recomendar los 6 mejores counter Pokémon.
    """
    opponent_pokemon = [pokemon_repo.get_by_id(pid) for pid in request.opponent_pokemon_ids if pokemon_repo.get_by_id(pid)]
    if not opponent_pokemon:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se encontraron Pokémon válidos con esos IDs")

    return counter_engine.generate_counter_team(
        opponent_team=opponent_pokemon,
        strategy=request.strategy,
        include_legendaries=request.include_legendaries
    )
