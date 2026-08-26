import json
import os
from typing import List, Optional, Dict, Any

class PokemonRepository:
    _instance = None
    _pokemon_list: List[Dict[str, Any]] = []
    _pokemon_by_id: Dict[int, Dict[str, Any]] = {}
    _pokemon_by_name: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PokemonRepository, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pokedex.json")
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                self._pokemon_list = json.load(f)
                for p in self._pokemon_list:
                    self._pokemon_by_id[p["id"]] = p
                    self._pokemon_by_name[p["name"].lower()] = p

    def get_all(self, query: Optional[str] = None, type_filter: Optional[str] = None, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        results = self._pokemon_list
        if query:
            q = query.lower().strip()
            results = [p for p in results if q in p["name"].lower() or str(p["id"]) == q]
        if type_filter:
            t = type_filter.lower().strip()
            results = [p for p in results if t in p["types"]]
        
        return results[skip : skip + limit]

    def get_by_id(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        return self._pokemon_by_id.get(pokemon_id)

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return self._pokemon_by_name.get(name.lower().strip())

    def get_pool_for_counters(self, min_bst: int = 430) -> List[Dict[str, Any]]:
        """
        Returns a competitive/fully-evolved pool for counter recommendations.
        """
        return [p for p in self._pokemon_list if p["stats"]["bst"] >= min_bst]


pokemon_repo = PokemonRepository()
