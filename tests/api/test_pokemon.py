"""Tests del catalogo Pokedex: listado, filtros, tipos y detalle."""

import pytest
from fastapi.testclient import TestClient

from app.core.type_chart import POKEMON_TYPES


class TestListPokemon:
    def test_returns_default_page_of_50(self, client: TestClient, api_prefix: str):
        response = client.get(f"{api_prefix}/pokemon")

        assert response.status_code == 200
        body = response.json()
        assert len(body) == 50
        assert body[0]["name"] == "Bulbasaur"

    def test_summary_exposes_the_full_contract(self, client: TestClient, api_prefix: str):
        response = client.get(f"{api_prefix}/pokemon", params={"limit": 1})

        pokemon = response.json()[0]
        assert set(pokemon) == {"id", "name", "types", "stats", "sprite", "artwork"}
        assert set(pokemon["stats"]) == {
            "hp",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
            "speed",
            "bst",
        }

    def test_filters_by_name(self, client: TestClient, api_prefix: str):
        response = client.get(f"{api_prefix}/pokemon", params={"query": "pikachu"})

        assert response.status_code == 200
        assert [p["name"] for p in response.json()] == ["Pikachu"]

    def test_filters_by_type(self, client: TestClient, api_prefix: str):
        response = client.get(f"{api_prefix}/pokemon", params={"type": "dragon", "limit": 200})

        body = response.json()
        assert body, "el filtro por tipo dragon no deberia venir vacio"
        assert all("dragon" in p["types"] for p in body)

    def test_pagination_does_not_overlap(self, client: TestClient, api_prefix: str):
        first = client.get(f"{api_prefix}/pokemon", params={"limit": 10, "skip": 0}).json()
        second = client.get(f"{api_prefix}/pokemon", params={"limit": 10, "skip": 10}).json()

        assert {p["id"] for p in first}.isdisjoint({p["id"] for p in second})

    @pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 201}, {"skip": -1}])
    def test_rejects_out_of_range_pagination(
        self, client: TestClient, api_prefix: str, params: dict
    ):
        response = client.get(f"{api_prefix}/pokemon", params=params)

        assert response.status_code == 422


class TestGetTypes:
    def test_returns_the_18_types_with_colors(self, client: TestClient, api_prefix: str):
        response = client.get(f"{api_prefix}/pokemon/types")

        assert response.status_code == 200
        body = response.json()
        assert len(body) == 18
        assert [t["name"] for t in body] == POKEMON_TYPES
        assert all(t["color"].startswith("#") for t in body)


class TestPokemonDetail:
    def test_resolves_by_numeric_id(self, client: TestClient, api_prefix: str):
        response = client.get(f"{api_prefix}/pokemon/25")

        assert response.status_code == 200
        assert response.json()["name"] == "Pikachu"

    def test_resolves_by_name_case_insensitive(self, client: TestClient, api_prefix: str):
        response = client.get(f"{api_prefix}/pokemon/ChArIzArD")

        assert response.status_code == 200
        assert response.json()["id"] == 6

    def test_computes_stacked_weakness(self, client: TestClient, api_prefix: str):
        """Charizard es fire/flying: roca pega 2x a fire y 2x a flying -> 4x."""
        body = client.get(f"{api_prefix}/pokemon/charizard").json()

        weaknesses = {w["type"]: w["multiplier"] for w in body["weaknesses"]}
        assert weaknesses["rock"] == 4.0
        assert body["weaknesses"][0]["multiplier"] == 4.0, "deben venir de mayor a menor"

    def test_computes_immunities(self, client: TestClient, api_prefix: str):
        """Ground no afecta a los tipos flying."""
        body = client.get(f"{api_prefix}/pokemon/charizard").json()

        assert "ground" in body["immunities"]

    def test_effectiveness_buckets_are_disjoint(self, client: TestClient, api_prefix: str):
        body = client.get(f"{api_prefix}/pokemon/garchomp").json()

        weak = {w["type"] for w in body["weaknesses"]}
        resist = {r["type"] for r in body["resistances"]}
        immune = set(body["immunities"])
        assert weak.isdisjoint(resist)
        assert weak.isdisjoint(immune)
        assert resist.isdisjoint(immune)

    def test_unknown_pokemon_returns_404(self, client: TestClient, api_prefix: str):
        response = client.get(f"{api_prefix}/pokemon/missingno")

        assert response.status_code == 404
        assert response.json()["detail"] == "Pokémon no encontrado"
