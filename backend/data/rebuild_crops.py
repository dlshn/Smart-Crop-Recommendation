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

HONEST LIMITATION (checked against web sources, 2026-09): Sri Lanka's
official Wet/Intermediate/Dry zone classification (Land and Water Use
Division, Dept. of Agriculture, Peredeniya, 1979) is defined by rainfall
isohyets and terrain, NOT by district boundaries -- the Wet Zone, for
example, "covers the south-western region including the central hill
country", cutting across districts rather than following their borders.
Several districts genuinely straddle more than one zone in reality
(e.g. Kandy, Kurunegala, Ratnapura, Monaragala, Nuwara Eliya, Puttalam,
Hambantota all contain areas of more than one zone). DISTRICT_ZONE below
assigns each WHOLE district to a single dominant zone as a practical,
disclosed simplification -- it is NOT a per-division/per-farm-accurate
mapping, and no single official "list of districts per crop" document
exists to validate this against more precisely. This is the same
district-level granularity limitation the project thesis (Section 5.3)
already discusses for rainfall data; it applies equally here. Do not
present this district list as more precise than it is.
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

# Soil type per crop: the FULL set of real Sri Lankan Great Soil Groups
# documented for each zone the crop grows in (Dept. of Agriculture /
# Land Use Division's 14 nationally-recognised groups -- checked live
# 2026-09), NOT narrowed to one "dominant" group per zone (an earlier
# version of this file did that; the project owner asked for the full
# set instead, since a district can't be resolved to just one of a
# zone's several real soil groups without finer, sub-district survey
# data). A crop spanning more than one zone gets the UNION of those
# zones' groups, derived directly from CROP_SUITABLE_ZONES above so the
# two never drift out of sync.
#
#   Dry Zone (10 groups): Reddish Brown Earths (largest area), Low
#   Humic Gley Soils, Non-Calcic Brown Soils, Red-Yellow Latosols,
#   Alluvial Soils (river flood plains), Soils of the Old Alluvium,
#   Solodized Solonetz (arid areas), Regosols (coastal areas),
#   Grumusols, Rendzinas (small extents).
#
#   Wet Zone (4 groups): Red-Yellow Podzolic Soils (dominant), Reddish
#   Brown Latosolic Soils, Immature Brown Loams, Bog and Half-Bog Soils
#   (tidal marshes).
#
#   Intermediate Zone: documented as "a transition from reddish brown
#   earths to red yellow podzolic soils", so it contributes both of
#   those plus Immature Brown Loams (the upcountry vegetable-belt
#   group: Nuwara Eliya / Badulla / Matale).
ZONE_SOIL_GROUPS = {
    "Dry": [
        "Reddish Brown Earths", "Low Humic Gley Soils", "Non-Calcic Brown Soils",
        "Red-Yellow Latosols", "Alluvial Soils", "Soils of the Old Alluvium",
        "Solodized Solonetz", "Regosols", "Grumusols", "Rendzinas",
    ],
    "Wet": [
        "Red-Yellow Podzolic Soils", "Reddish Brown Latosolic Soils",
        "Immature Brown Loams", "Bog and Half-Bog Soils",
    ],
    "Intermediate": ["Reddish Brown Earths", "Red-Yellow Podzolic Soils", "Immature Brown Loams"],
}


def soil_groups_for_zones(zones):
    groups = []
    for z in zones:
        for g in ZONE_SOIL_GROUPS[z]:
            if g not in groups:
                groups.append(g)
    return groups


def main():
    with open("backend/data/crops.json", "r", encoding="utf-8") as f:
        crops = json.load(f)

    for crop in crops:
        name = crop["crop"]
        zones = CROP_SUITABLE_ZONES.get(name)

        if zones is None:
            raise ValueError(f"No verified zone data for crop: {name}")

        suitable_districts = sorted(
            d for d, z in DISTRICT_ZONE.items() if z in zones
        )
        if not suitable_districts:
            raise ValueError(f"Zero districts matched for crop: {name} (zones={zones})")

        crop["districts"] = suitable_districts
        crop["soilTypes"] = soil_groups_for_zones(zones)
        crop["notes"] = (
            f"Suitable districts derived from Sri Lanka's Wet/Intermediate/Dry "
            f"agro-climatic zone classification (Dept. of Agriculture, Sri Lanka), "
            f"matched to this crop's typical growing zone(s): {', '.join(zones)}. "
            f"Soil type: ALL real Sri Lankan Great Soil Groups documented for "
            f"this crop's zone(s) (not narrowed to one dominant group per "
            f"zone). [FULL-14-BASIS, sourced 2026-09] Dry Zone groups: "
            f"Reddish Brown Earths, Low Humic Gley Soils, Non-Calcic Brown "
            f"Soils, Red-Yellow Latosols, Alluvial Soils, Soils of the Old "
            f"Alluvium, Solodized Solonetz, Regosols, Grumusols, Rendzinas. "
            f"Wet Zone groups: Red-Yellow Podzolic Soils, Reddish Brown "
            f"Latosolic Soils, Immature Brown Loams, Bog and Half-Bog Soils. "
            f"Intermediate Zone (a documented transition between Reddish "
            f"Brown Earths and Red-Yellow Podzolic Soils) additionally "
            f"carries Immature Brown Loams for the upcountry belt. A crop "
            f"spanning more than one zone lists the union of those zones' "
            f"groups."
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
