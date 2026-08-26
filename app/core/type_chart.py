"""
Pokémon 18-Type Effectiveness Chart (Generations 6 - 9)
Includes Fairy type and full weakness, resistance, and immunity multipliers.
"""
from typing import Dict, List, Tuple

# List of all 18 standard Pokémon types
POKEMON_TYPES = [
    "normal", "fire", "water", "grass", "electric", "ice",
    "fighting", "poison", "ground", "flying", "psychic", "bug",
    "rock", "ghost", "dragon", "steel", "dark", "fairy"
]

# Type color codes for UI/Visual reference
TYPE_COLORS: Dict[str, str] = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "grass": "#7AC74C",
    "electric": "#F7D02C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "steel": "#B7B7CE",
    "dark": "#705746",
    "fairy": "#D685AD"
}

# Attacking Type -> Defending Type effectiveness multiplier
# Format: { attacker: { defender: multiplier } }
TYPE_CHART: Dict[str, Dict[str, float]] = {
    "normal": {
        "rock": 0.5, "ghost": 0.0, "steel": 0.5
    },
    "fire": {
        "fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 2.0,
        "bug": 2.0, "rock": 0.5, "dragon": 0.5, "steel": 2.0
    },
    "water": {
        "fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0,
        "rock": 2.0, "dragon": 0.5
    },
    "grass": {
        "fire": 0.5, "water": 2.0, "grass": 0.5, "poison": 0.5,
        "ground": 2.0, "flying": 0.5, "bug": 0.5, "rock": 2.0,
        "dragon": 0.5, "steel": 0.5
    },
    "electric": {
        "water": 2.0, "grass": 0.5, "electric": 0.5, "ground": 0.0,
        "flying": 2.0, "dragon": 0.5
    },
    "ice": {
        "fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 0.5,
        "ground": 2.0, "flying": 2.0, "dragon": 2.0, "steel": 0.5
    },
    "fighting": {
        "normal": 2.0, "ice": 2.0, "poison": 0.5, "flying": 0.5,
        "psychic": 0.5, "bug": 0.5, "rock": 2.0, "ghost": 0.0,
        "dark": 2.0, "steel": 2.0, "fairy": 0.5
    },
    "poison": {
        "grass": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5,
        "ghost": 0.5, "steel": 0.0, "fairy": 2.0
    },
    "ground": {
        "fire": 2.0, "electric": 2.0, "grass": 0.5, "poison": 2.0,
        "flying": 0.0, "bug": 0.5, "rock": 2.0, "steel": 2.0
    },
    "flying": {
        "grass": 2.0, "electric": 0.5, "fighting": 2.0, "bug": 2.0,
        "rock": 0.5, "steel": 0.5
    },
    "psychic": {
        "fighting": 2.0, "poison": 2.0, "psychic": 0.5, "steel": 0.5,
        "dark": 0.0
    },
    "bug": {
        "fire": 0.5, "grass": 2.0, "fighting": 0.5, "poison": 0.5,
        "flying": 0.5, "psychic": 2.0, "ghost": 0.5, "dark": 2.0,
        "steel": 0.5, "fairy": 0.5
    },
    "rock": {
        "fire": 2.0, "ice": 2.0, "fighting": 0.5, "ground": 0.5,
        "flying": 2.0, "bug": 2.0, "steel": 0.5
    },
    "ghost": {
        "normal": 0.0, "psychic": 2.0, "ghost": 2.0, "dark": 0.5
    },
    "dragon": {
        "dragon": 2.0, "steel": 0.5, "fairy": 0.0
    },
    "steel": {
        "fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2.0,
        "rock": 2.0, "steel": 0.5, "fairy": 2.0
    },
    "dark": {
        "fighting": 0.5, "psychic": 2.0, "ghost": 2.0, "dark": 0.5,
        "fairy": 0.5
    },
    "fairy": {
        "fire": 0.5, "fighting": 2.0, "poison": 0.5, "dragon": 2.0,
        "dark": 2.0, "steel": 0.5
    }
}


def get_attack_multiplier(attack_type: str, defending_types: List[str]) -> float:
    """
    Calculate the damage multiplier of an attack type against a defending Pokémon with 1 or 2 types.
    """
    attack_type = attack_type.lower()
    multiplier = 1.0
    
    chart_for_attack = TYPE_CHART.get(attack_type, {})
    for def_type in defending_types:
        def_type = def_type.lower()
        eff = chart_for_attack.get(def_type, 1.0)
        multiplier *= eff
        
    return multiplier


def get_defensive_profile(defending_types: List[str]) -> Dict[str, float]:
    """
    Calculates the damage multiplier from each of the 18 attacking types against the defending types.
    Returns: { "fire": 2.0, "water": 0.5, "grass": 1.0, ... }
    """
    profile: Dict[str, float] = {}
    for atk_type in POKEMON_TYPES:
        profile[atk_type] = get_attack_multiplier(atk_type, defending_types)
    return profile
