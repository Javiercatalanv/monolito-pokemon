import urllib.request
import json
import os

GEN9_EXTRAS = [
    {
        "id": 906, "name": {"english": "Sprigatito"}, "type": ["Grass"],
        "base": {"HP": 40, "Attack": 61, "Defense": 54, "Sp. Attack": 45, "Sp. Defense": 45, "Speed": 65},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/906.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/906.png"}
    },
    {
        "id": 908, "name": {"english": "Meowscarada"}, "type": ["Grass", "Dark"],
        "base": {"HP": 76, "Attack": 110, "Defense": 70, "Sp. Attack": 81, "Sp. Defense": 70, "Speed": 123},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/908.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/908.png"}
    },
    {
        "id": 909, "name": {"english": "Fuecoco"}, "type": ["Fire"],
        "base": {"HP": 67, "Attack": 45, "Defense": 59, "Sp. Attack": 63, "Sp. Defense": 40, "Speed": 36},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/909.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/909.png"}
    },
    {
        "id": 911, "name": {"english": "Skeledirge"}, "type": ["Fire", "Ghost"],
        "base": {"HP": 104, "Attack": 75, "Defense": 100, "Sp. Attack": 110, "Sp. Defense": 75, "Speed": 66},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/911.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/911.png"}
    },
    {
        "id": 912, "name": {"english": "Quaxly"}, "type": ["Water"],
        "base": {"HP": 55, "Attack": 65, "Defense": 45, "Sp. Attack": 50, "Sp. Defense": 45, "Speed": 50},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/912.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/912.png"}
    },
    {
        "id": 914, "name": {"english": "Quaquaval"}, "type": ["Water", "Fighting"],
        "base": {"HP": 85, "Attack": 120, "Defense": 80, "Sp. Attack": 85, "Sp. Defense": 75, "Speed": 85},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/914.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/914.png"}
    },
    {
        "id": 979, "name": {"english": "Annihilape"}, "type": ["Fighting", "Ghost"],
        "base": {"HP": 110, "Attack": 115, "Defense": 80, "Sp. Attack": 50, "Sp. Defense": 90, "Speed": 90},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/979.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/979.png"}
    },
    {
        "id": 983, "name": {"english": "Kingambit"}, "type": ["Dark", "Steel"],
        "base": {"HP": 100, "Attack": 135, "Defense": 120, "Sp. Attack": 60, "Sp. Defense": 85, "Speed": 50},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/983.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/983.png"}
    },
    {
        "id": 987, "name": {"english": "Flutter Mane"}, "type": ["Ghost", "Fairy"],
        "base": {"HP": 55, "Attack": 55, "Defense": 55, "Sp. Attack": 135, "Sp. Defense": 135, "Speed": 135},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/987.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/987.png"}
    },
    {
        "id": 991, "name": {"english": "Iron Bundle"}, "type": ["Ice", "Water"],
        "base": {"HP": 56, "Attack": 80, "Defense": 114, "Sp. Attack": 124, "Sp. Defense": 60, "Speed": 136},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/991.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/991.png"}
    },
    {
        "id": 998, "name": {"english": "Baxcalibur"}, "type": ["Dragon", "Ice"],
        "base": {"HP": 115, "Attack": 145, "Defense": 92, "Sp. Attack": 75, "Sp. Defense": 86, "Speed": 87},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/998.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/998.png"}
    },
    {
        "id": 1000, "name": {"english": "Gholdengo"}, "type": ["Steel", "Ghost"],
        "base": {"HP": 87, "Attack": 60, "Defense": 95, "Sp. Attack": 133, "Sp. Defense": 91, "Speed": 84},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1000.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1000.png"}
    },
    {
        "id": 1002, "name": {"english": "Chien-Pao"}, "type": ["Dark", "Ice"],
        "base": {"HP": 80, "Attack": 120, "Defense": 80, "Sp. Attack": 90, "Sp. Defense": 65, "Speed": 135},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1002.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1002.png"}
    },
    {
        "id": 1003, "name": {"english": "Ting-Lu"}, "type": ["Dark", "Ground"],
        "base": {"HP": 155, "Attack": 110, "Defense": 125, "Sp. Attack": 55, "Sp. Defense": 80, "Speed": 45},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1003.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1003.png"}
    },
    {
        "id": 1005, "name": {"english": "Roaring Moon"}, "type": ["Dragon", "Dark"],
        "base": {"HP": 105, "Attack": 139, "Defense": 71, "Sp. Attack": 55, "Sp. Defense": 101, "Speed": 119},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1005.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1005.png"}
    },
    {
        "id": 1006, "name": {"english": "Iron Valiant"}, "type": ["Fairy", "Fighting"],
        "base": {"HP": 74, "Attack": 130, "Defense": 90, "Sp. Attack": 120, "Sp. Defense": 60, "Speed": 116},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1006.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1006.png"}
    },
    {
        "id": 1007, "name": {"english": "Koraidon"}, "type": ["Fighting", "Dragon"],
        "base": {"HP": 100, "Attack": 135, "Defense": 115, "Sp. Attack": 85, "Sp. Defense": 100, "Speed": 135},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1007.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1007.png"}
    },
    {
        "id": 1008, "name": {"english": "Miraidon"}, "type": ["Electric", "Dragon"],
        "base": {"HP": 100, "Attack": 85, "Defense": 100, "Sp. Attack": 135, "Sp. Defense": 115, "Speed": 135},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1008.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1008.png"}
    },
    {
        "id": 1017, "name": {"english": "Ogerpon"}, "type": ["Grass"],
        "base": {"HP": 80, "Attack": 120, "Defense": 84, "Sp. Attack": 60, "Sp. Defense": 96, "Speed": 110},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1017.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1017.png"}
    },
    {
        "id": 1024, "name": {"english": "Terapagos"}, "type": ["Normal"],
        "base": {"HP": 90, "Attack": 65, "Defense": 85, "Sp. Attack": 65, "Sp. Defense": 85, "Speed": 60},
        "image": {"hires": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1024.png", "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1024.png"}
    }
]

def build_database():
    print("Downloading National Pokédex dataset...")
    url = "https://raw.githubusercontent.com/Purukitto/pokemon-data.json/master/pokedex.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw_data = json.loads(urllib.request.urlopen(req).read())
    
    clean_list = []
    seen_ids = set()

    for item in raw_data:
        p_id = item["id"]
        seen_ids.add(p_id)
        name = item["name"]["english"]
        types = [t.lower() for t in item["type"]]
        base = item.get("base", {})
        
        hp = base.get("HP", 50)
        atk = base.get("Attack", 50)
        df = base.get("Defense", 50)
        spa = base.get("Sp. Attack", 50)
        spd = base.get("Sp. Defense", 50)
        spe = base.get("Speed", 50)
        bst = hp + atk + df + spa + spd + spe

        # Always use official artwork CDN fallback
        hires_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{p_id}.png"
        sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{p_id}.png"

        clean_list.append({
            "id": p_id,
            "name": name,
            "types": types,
            "stats": {
                "hp": hp,
                "attack": atk,
                "defense": df,
                "sp_attack": spa,
                "sp_defense": spd,
                "speed": spe,
                "bst": bst
            },
            "sprite": sprite_url,
            "artwork": hires_url
        })

    # Add Gen 9 extras
    for g9 in GEN9_EXTRAS:
        p_id = g9["id"]
        if p_id not in seen_ids:
            base = g9["base"]
            bst = sum(base.values())
            clean_list.append({
                "id": p_id,
                "name": g9["name"]["english"],
                "types": [t.lower() for t in g9["type"]],
                "stats": {
                    "hp": base["HP"],
                    "attack": base["Attack"],
                    "defense": base["Defense"],
                    "sp_attack": base["Sp. Attack"],
                    "sp_defense": base["Sp. Defense"],
                    "speed": base["Speed"],
                    "bst": bst
                },
                "sprite": g9["image"]["sprite"],
                "artwork": g9["image"]["hires"]
            })

    app_dir = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(app_dir, "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "pokedex.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clean_list, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved {len(clean_list)} Pokémon to {output_path}")

if __name__ == "__main__":
    build_database()
