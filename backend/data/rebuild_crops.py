"""
Rebuilds backend/data/crops.json with defensible, non-fabricated data:

1. District suitability: derived from Sri Lanka's Wet / Intermediate / Dry
   agro-climatic zone classification (Dept. of Agriculture, Sri Lanka),
   matched against each crop's known typical growing zone(s). This
   replaces the previous version where every crop listed all 25
   districts as "suitable" -- which made the district-suitability filter
   a no-op.
2. Soil types: differentiated per crop based on common horticultural
   soil-texture preference (not a generic 2-4 item set repeated for
   every crop).

This uses the SAME zone methodology already used to generate
backend/data/recommendations.json, so the two datasets stay consistent
with each other.
"""
import json

DISTRICT_ZONE = {
    "Colombo": "Wet", "Gampaha": "Wet", "Kalutara": "Wet",
    "Galle": "Wet", "Matara": "Wet", "Ratnapura": "Wet", "Kegalle": "Wet",
    "Kandy": "Intermediate", "Matale": "Intermediate",
    "Nuwara Eliya": "Intermediate", "Badulla": "Intermediate",
    "Jaffna": "Dry", "Kilinochchi": "Dry", "Mannar": "Dry",
    "Vavuniya": "Dry", "Mullaitivu": "Dry", "Trincomalee": "Dry",
    "Batticaloa": "Dry", "Ampara": "Dry", "Anuradhapura": "Dry",
    "Polonnaruwa": "Dry", "Hambantota": "Dry", "Puttalam": "Dry",
    "Kurunegala": "Dry", "Monaragala": "Dry",
}

CROP_SUITABLE_ZONES = {
    "Banana": ["Wet", "Intermediate", "Dry"],
    "Papaya": ["Wet", "Intermediate", "Dry"],
    "Mango": ["Dry", "Intermediate"],
    "Pineapple": ["Wet", "Intermediate"],
    "Wood Apple": ["Dry"],
    "Beli Fruit": ["Dry", "Intermediate"],
    "Guava": ["Wet", "Intermediate", "Dry"],
    "Passion Fruit": ["Wet", "Intermediate"],
    "Rambutan": ["Wet"],
    "Mangosteen": ["Wet"],
    "Avocado": ["Wet", "Intermediate"],
    "Rose Apple": ["Wet", "Intermediate"],
    "Soursop": ["Wet", "Intermediate"],
    "Custard Apple": ["Dry", "Intermediate"],
    "Gooseberry": ["Dry", "Intermediate"],
    "Pomegranate": ["Dry"],
    "Orange": ["Intermediate"],
    "Winged Bean": ["Wet", "Intermediate"],
    "Bitter Melon": ["Wet", "Intermediate", "Dry"],
    "Brinjal": ["Wet", "Intermediate", "Dry"],
    "Long Purple Eggplant": ["Wet", "Intermediate", "Dry"],
    "Asiatic Pennywort": ["Wet", "Intermediate"],
    "Pennywort": ["Wet", "Intermediate"],
    "Red Spinach": ["Wet", "Intermediate", "Dry"],
    "Leeks": ["Intermediate"],
    "Carrot": ["Intermediate"],
    "Beetroot": ["Intermediate"],
    "Cabbage": ["Intermediate"],
    "Knol-Khol": ["Intermediate"],
    "Pumpkin": ["Dry", "Intermediate"],
    "Onion": ["Dry"],
    "Potato": ["Intermediate"],
    "Drumsticks": ["Dry", "Intermediate"],
    "Jackfruit": ["Wet", "Intermediate"],
    "Breadfruit": ["Wet"],
    "Taro": ["Wet", "Intermediate"],
    "Manioc": ["Dry", "Intermediate"],
}

# Differentiated soil-texture preference per crop, based on common
# horticultural knowledge (well-drained vs moisture-retentive, sandy vs
# clay-rich, pH tolerance where relevant to texture selection).
CROP_SOIL_TYPES = {
    "Banana": ["Loam", "Alluvial"],
    "Papaya": ["Sandy Loam"],
    "Mango": ["Loam", "Laterite"],
    "Pineapple": ["Sandy Loam"],
    "Wood Apple": ["Sandy Loam", "Poor/Dry Soils"],
    "Beli Fruit": ["Sandy Loam", "Poor/Dry Soils"],
    "Guava": ["Loam", "Sandy Loam"],
    "Passion Fruit": ["Sandy Loam", "Loam"],
    "Rambutan": ["Loam", "High Organic Matter"],
    "Mangosteen": ["Loam", "High Organic Matter"],
    "Avocado": ["Loam"],
    "Rose Apple": ["Loam", "Clay Loam"],
    "Soursop": ["Sandy Loam", "Loam"],
    "Custard Apple": ["Sandy Loam", "Poor/Dry Soils"],
    "Gooseberry": ["Sandy Loam", "Poor/Dry Soils"],
    "Pomegranate": ["Sandy Loam", "Saline-Tolerant"],
    "Orange": ["Loam"],
    "Winged Bean": ["Loam", "Moisture-Retentive"],
    "Bitter Melon": ["Sandy Loam", "Loam"],
    "Brinjal": ["Loam", "Sandy Loam"],
    "Long Purple Eggplant": ["Loam", "Sandy Loam"],
    "Asiatic Pennywort": ["Moist Loam"],
    "Pennywort": ["Moist Loam"],
    "Red Spinach": ["Moist Loam"],
    "Leeks": ["Loam"],
    "Carrot": ["Sandy Loam", "Loose/Deep Soil"],
    "Beetroot": ["Sandy Loam"],
    "Cabbage": ["Loam", "Fertile Soil"],
    "Knol-Khol": ["Loam"],
    "Pumpkin": ["Sandy Loam", "Loam"],
    "Onion": ["Sandy Loam", "Loam"],
    "Potato": ["Loam", "Loose/Deep Soil"],
    "Drumsticks": ["Sandy Loam", "Poor/Dry Soils"],
    "Jackfruit": ["Loam", "Clay Loam"],
    "Breadfruit": ["Loam"],
    "Taro": ["Clay Loam", "Wet/Waterlogged Tolerant"],
    "Manioc": ["Sandy Loam", "Poor/Dry Soils"],
}


def main():
    with open("backend/data/crops.json", "r", encoding="utf-8") as f:
        crops = json.load(f)

    for crop in crops:
        name = crop["crop"]
        zones = CROP_SUITABLE_ZONES.get(name)
        soils = CROP_SOIL_TYPES.get(name)

        if zones is None or soils is None:
            raise ValueError(f"No verified zone/soil data for crop: {name}")

        suitable_districts = sorted(
            d for d, z in DISTRICT_ZONE.items() if z in zones
        )
        if not suitable_districts:
            raise ValueError(f"Zero districts matched for crop: {name} (zones={zones})")

        crop["districts"] = suitable_districts
        crop["soilTypes"] = soils
        crop["notes"] = (
            f"Suitable districts derived from Sri Lanka's Wet/Intermediate/Dry "
            f"agro-climatic zone classification (Dept. of Agriculture, Sri Lanka), "
            f"matched to this crop's typical growing zone(s): {', '.join(zones)}. "
            f"Soil type preferences based on common horticultural texture "
            f"requirements for this crop."
        )

    with open("backend/data/crops.json", "w", encoding="utf-8") as f:
        json.dump(crops, f, indent=2, ensure_ascii=False)

    # sanity check output
    counts = [len(c["districts"]) for c in crops]
    print(f"Rewrote {len(crops)} crop records.")
    print(f"District-count per crop: min={min(counts)}, max={max(counts)}, "
          f"all-25 count={sum(1 for c in counts if c == 25)}")


if __name__ == "__main__":
    main()
