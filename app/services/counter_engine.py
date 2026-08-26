from typing import Any

from app.core.pokemon_repository import pokemon_repo
from app.core.type_chart import (
    POKEMON_TYPES,
    TYPE_COLORS,
    get_attack_multiplier,
    get_defensive_profile,
)


class CounterEngine:
    def analyze_team(self, team_pokemon: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Analyze an opponent team's type weaknesses, resistances, and offensive threats.
        """
        if not team_pokemon:
            return {"error": "Team is empty"}

        type_weakness_counts: dict[str, int] = dict.fromkeys(POKEMON_TYPES, 0)
        type_resistance_counts: dict[str, int] = dict.fromkeys(POKEMON_TYPES, 0)
        offensive_stabs: dict[str, int] = dict.fromkeys(POKEMON_TYPES, 0)

        pokemon_summaries = []

        for p in team_pokemon:
            p_types = p["types"]
            def_profile = get_defensive_profile(p_types)

            weak_to = []
            resists = []
            immune_to = []

            for atk_type, mult in def_profile.items():
                if mult > 1.0:
                    type_weakness_counts[atk_type] += 1
                    weak_to.append({"type": atk_type, "multiplier": mult})
                elif mult == 0.0:
                    immune_to.append(atk_type)
                    type_resistance_counts[atk_type] += 1
                elif mult < 1.0:
                    resists.append({"type": atk_type, "multiplier": mult})
                    type_resistance_counts[atk_type] += 1

            for st in p_types:
                offensive_stabs[st] = offensive_stabs.get(st, 0) + 1

            pokemon_summaries.append(
                {
                    "id": p["id"],
                    "name": p["name"],
                    "types": p_types,
                    "sprite": p["sprite"],
                    "artwork": p["artwork"],
                    "weak_to": sorted(weak_to, key=lambda x: x["multiplier"], reverse=True),
                    "resists": resists,
                    "immune_to": immune_to,
                }
            )

        # Top team weaknesses (types that hit 2+ members super effectively)
        sorted_weaknesses = sorted(
            [
                {"type": t, "count": c, "color": TYPE_COLORS.get(t, "#888")}
                for t, c in type_weakness_counts.items()
                if c > 0
            ],
            key=lambda x: x["count"],
            reverse=True,
        )

        # Top offensive threats from opponent
        sorted_threats = sorted(
            [
                {"type": t, "count": c, "color": TYPE_COLORS.get(t, "#888")}
                for t, c in offensive_stabs.items()
                if c > 0
            ],
            key=lambda x: x["count"],
            reverse=True,
        )

        return {
            "team_size": len(team_pokemon),
            "pokemon": pokemon_summaries,
            "top_team_weaknesses": sorted_weaknesses,
            "top_offensive_threats": sorted_threats,
        }

    def generate_counter_team(
        self,
        opponent_team: list[dict[str, Any]],
        strategy: str = "balanced",
        include_legendaries: bool = True,
    ) -> dict[str, Any]:
        """
        Generates an optimal 6-Pokémon counter team against the given opponent team.
        Strategies: 'balanced', 'offensive', 'defensive'
        """
        if not opponent_team:
            return {"error": "No opponent Pokémon provided"}

        pool = pokemon_repo.get_pool_for_counters(min_bst=430)
        opp_ids = {p["id"] for p in opponent_team}

        scored_candidates = []

        for cand in pool:
            # Avoid picking Pokémon that are already in opponent's team
            if cand["id"] in opp_ids:
                continue

            cand_types = cand["types"]
            cand_stats = cand["stats"]

            total_score = 0.0
            targets_countered = []

            for opp in opponent_team:
                opp_types = opp["types"]
                opp_stats = opp["stats"]

                # 1. Offensive STAB calculation
                max_offensive_mult = max(
                    [get_attack_multiplier(c_type, opp_types) for c_type in cand_types]
                )

                # 2. Defensive Incoming STAB calculation
                max_incoming_mult = max(
                    [get_attack_multiplier(o_type, cand_types) for o_type in opp_types]
                )

                # Score per matchup
                matchup_score = 0.0

                # Offensive scoring
                if max_offensive_mult >= 4.0:
                    matchup_score += 70.0
                elif max_offensive_mult >= 2.0:
                    matchup_score += 40.0
                elif max_offensive_mult <= 0.5:
                    matchup_score -= 20.0

                # Defensive scoring
                if max_incoming_mult == 0.0:
                    matchup_score += 50.0  # Total immunity
                elif max_incoming_mult <= 0.25:
                    matchup_score += 35.0
                elif max_incoming_mult <= 0.5:
                    matchup_score += 25.0
                elif max_incoming_mult >= 4.0:
                    matchup_score -= 50.0
                elif max_incoming_mult >= 2.0:
                    matchup_score -= 25.0

                # Speed advantage
                if cand_stats["speed"] > opp_stats["speed"]:
                    matchup_score += 10.0

                # Strategy modifiers
                if strategy == "offensive":
                    offensive_power = max(cand_stats["attack"], cand_stats["sp_attack"])
                    matchup_score += offensive_power / 10.0
                    if max_offensive_mult >= 2.0:
                        matchup_score += 25.0
                elif strategy == "defensive":
                    bulk = (
                        cand_stats["hp"] + cand_stats["defense"] + cand_stats["sp_defense"]
                    ) / 3.0
                    matchup_score += bulk / 10.0
                    if max_incoming_mult <= 0.5:
                        matchup_score += 25.0

                total_score += matchup_score

                # Record if this candidate effectively counters this specific opponent
                if max_offensive_mult >= 2.0 or max_incoming_mult <= 0.5:
                    reason = []
                    if max_offensive_mult >= 4.0:
                        reason.append("4x Super Effective STAB")
                    elif max_offensive_mult >= 2.0:
                        reason.append("2x Super Effective STAB")

                    if max_incoming_mult == 0.0:
                        reason.append("Inmune a ataques del rival")
                    elif max_incoming_mult <= 0.5:
                        reason.append("Resiste ataques del rival")

                    targets_countered.append(
                        {
                            "opponent_id": opp["id"],
                            "opponent_name": opp["name"],
                            "advantage_type": (
                                "Hard Counter"
                                if (max_offensive_mult >= 2.0 and max_incoming_mult <= 0.5)
                                else "Advantage"
                            ),
                            "notes": " & ".join(reason) if reason else "Ventaja de Stats/Tipo",
                        }
                    )

            # Base Stat Total baseline bonus
            bst_bonus = (cand_stats["bst"] - 430) * 0.1
            final_score = total_score + bst_bonus

            scored_candidates.append(
                {
                    "pokemon": cand,
                    "score": round(final_score, 1),
                    "targets_countered": targets_countered,
                    "counter_count": len(targets_countered),
                }
            )

        # Sort candidates by score
        scored_candidates.sort(key=lambda x: (x["counter_count"], x["score"]), reverse=True)

        # Team Selection with Diversity Algorithm (select top 6 with diverse types)
        selected_team = []
        covered_opponents = set()
        seen_primary_types = set()

        for cand_data in scored_candidates:
            if len(selected_team) >= 6:
                break

            p = cand_data["pokemon"]
            primary_type = p["types"][0]

            # Promote type diversity in the counter team
            if primary_type in seen_primary_types and len(selected_team) < 5:
                # Allow only if it counters an uncovered opponent
                new_counters = {
                    t["opponent_id"] for t in cand_data["targets_countered"]
                } - covered_opponents
                if not new_counters and len(selected_team) < 4:
                    continue

            selected_team.append(cand_data)
            seen_primary_types.add(primary_type)
            for t in cand_data["targets_countered"]:
                covered_opponents.add(t["opponent_id"])

        # Format output
        counter_members = []
        for rank, item in enumerate(selected_team, 1):
            p = item["pokemon"]
            counter_members.append(
                {
                    "rank": rank,
                    "id": p["id"],
                    "name": p["name"],
                    "types": p["types"],
                    "stats": p["stats"],
                    "sprite": p["sprite"],
                    "artwork": p["artwork"],
                    "score": item["score"],
                    "targets_countered": item["targets_countered"],
                    "role": self._determine_role(p, strategy),
                }
            )

        analysis = self.analyze_team(opponent_team)

        return {
            "strategy": strategy,
            "team_coverage_percentage": round(
                min(100.0, (len(covered_opponents) / max(1, len(opponent_team))) * 100), 1
            ),
            "opponent_analysis": analysis,
            "counter_team": counter_members,
        }

    def _determine_role(self, pokemon: dict[str, Any], strategy: str) -> str:
        stats = pokemon["stats"]
        atk = stats["attack"]
        spa = stats["sp_attack"]
        df = stats["defense"]
        spd = stats["sp_defense"]
        spe = stats["speed"]

        if spe >= 105 and max(atk, spa) >= 110:
            return "Fast Sweeper / Revenge Killer"
        elif df >= 100 and spd >= 100:
            return "Mixed Wall / Tank"
        elif df >= 110:
            return "Physical Wall"
        elif spd >= 110:
            return "Special Wall"
        elif atk >= 120:
            return "Physical Wallbreaker"
        elif spa >= 120:
            return "Special Wallbreaker"
        else:
            return "Balanced Pivot"


counter_engine = CounterEngine()
