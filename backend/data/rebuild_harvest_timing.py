"""
Updates backend/data/crops.json harvestType / harvestDays using the best
available verified figures:

- VEGETABLES: days from planting/transplanting to first harvest, sourced
  from the Department of Agriculture Sri Lanka's HORDI crop pages
  (doa.gov.lk) where a specific figure was published, otherwise a
  well-established general horticultural estimate for that crop family.
  Source notes are recorded per crop below.

- FRUITS (perennial tree/vine crops): re-classified as "long" harvestType
  (single cycle takes noticeably longer than an annual vegetable) with
  harvestDays representing the typical flowering-to-fruit-maturity
  period for an already-bearing plant -- this is the figure that's
  actually usable for a seasonal recommendation tool (a farmer isn't
  asking "how long until my newly-planted mango tree bears fruit for
  the first time in 4 years", they're asking "if I'm entering/near a
  harvest window now, how long until it matures"). Three previously
  mis-classified crops (Jackfruit, Papaya, Pineapple) are corrected
  from "short" to "long" -- all three are genuinely multi-month-to-
  multi-year perennial crops, not fast annual vegetables.

IMPORTANT CONFIDENCE NOTE (kept honest in the notes field per crop):
  - Vegetable figures marked [DOA] were found on doa.gov.lk HORDI crop
    pages directly.
  - Vegetable figures marked [gen] are general, widely-corroborated
    horticultural estimates for that crop (DOA page did not state an
    explicit day figure at time of writing).
  - Fruit figures are general international horticultural estimates
    for flowering-to-maturity duration, not Sri-Lanka-specific DOA
    figures -- treat these as reasonable approximations, not verified
    facts, and flag to your supervisor if precision matters here.
"""
import json

# (harvestType, harvestDays, confidence_note)
HARVEST_DATA = {
    # ---- Vegetables (short) ----
    "Asiatic Pennywort": ("short", 100, "[DOA] doa.gov.lk/hordi-crop-gotukola: first harvest ~100 days from planting"),
    "Pennywort": ("short", 100, "[DOA] doa.gov.lk/hordi-crop-gotukola: first harvest ~100 days from planting"),
    "Beetroot": ("short", 90, "[gen] typical upcountry root-vegetable cycle, 85-100 days"),
    "Bitter Melon": ("short", 60, "[gen] bitter gourd/melon first harvest ~55-70 days from sowing, consistent with DOA Luffa (related cucurbit) at 60-70 days"),
    "Brinjal": ("short", 75, "[DOA] doa.gov.lk/hordi-crop-brinjal: harvest starts 10-12 weeks (70-84 days) after transplanting"),
    "Long Purple Eggplant": ("short", 75, "[DOA] same species/family as Brinjal, doa.gov.lk/hordi-crop-brinjal figure applied"),
    "Cabbage": ("short", 100, "[DOA] doa.gov.lk/hordi-crop-cabbage: harvest 90-110 days after planting"),
    "Carrot": ("short", 100, "[DOA] doa.gov.lk/hordi-variety-carrot: medium-maturity variety ~110 days; faster local varieties ~90 days"),
    "Knol-Khol": ("short", 70, "[gen] fast-maturing brassica root crop, typically 60-70 days"),
    "Leeks": ("short", 135, "[DOA] doa.gov.lk/hordi-crop-leeks: harvest about 4.5 months (~135 days) after transplanting"),
    "Onion": ("short", 100, "[gen] typical big/red onion bulb maturation, 90-110 days"),
    "Potato": ("short", 100, "[gen] typical upcountry potato cycle, 90-110 days"),
    "Pumpkin": ("short", 100, "[gen] typical cucurbit maturation, 90-120 days"),
    "Red Spinach": ("short", 30, "[gen] fast leafy green (mukunuwenna/amaranth), 25-35 days"),
    "Winged Bean": ("short", 85, "[DOA] doa.gov.lk/hordi-crop-winged-bean: recommended varieties 70-75 days, common local varieties 90-100 days"),

    # ---- Long-cycle root/tuber crops ----
    "Drumsticks": ("long", 210, "[gen] Moringa tree, first pod harvest typically 6-7 months (180-210 days) after planting"),
    "Manioc": ("long", 300, "[DOA] doa.gov.lk/hordi-variety-cassava: harvested at 9-12 months age; lower-mid estimate used"),
    "Taro": ("long", 210, "[gen] Kiri Ala corm crop, typically 6-7 months (180-210 days) to maturity"),

    # ---- Perennial fruit crops (flowering-to-maturity estimate; see module docstring) ----
    "Avocado": ("long", 240, "[gen] ~8 months from flowering to fruit maturity"),
    "Banana": ("long", 300, "[gen] ~9-11 months from planting to bunch maturity"),
    "Beli Fruit": ("long", 300, "[gen] bael fruit is notably slow-ripening, ~10+ months after fruit set"),
    "Breadfruit": ("long", 105, "[gen] ~3.5 months from flowering to maturity"),
    "Custard Apple": ("long", 120, "[gen] ~4 months from fruit set to maturity"),
    "Gooseberry": ("long", 90, "[gen] nelli fruit matures relatively quickly, ~3 months from flowering"),
    "Guava": ("long", 150, "[gen] ~4-5 months from flowering to fruit maturity"),
    "Jackfruit": ("long", 120, "[gen] ~4 months fruit development; re-classified from 'short' -- jackfruit is a multi-year tree crop, not a fast annual"),
    "Mango": ("long", 120, "[gen] ~4-5 months from flowering to fruit maturity"),
    "Mangosteen": ("long", 105, "[gen] ~90-120 days from flowering to maturity"),
    "Orange": ("long", 210, "[gen] citrus is notably slow to mature, ~7 months from flowering"),
    "Papaya": ("long", 270, "[gen] ~9 months from planting to first fruit maturity; re-classified from 'short' -- papaya is a semi-perennial crop, not a fast annual"),
    "Passion Fruit": ("long", 80, "[gen] ~10-12 weeks from flowering to fruit maturity"),
    "Pineapple": ("long", 450, "[gen] ~15 months from planting to first harvest; re-classified from 'short' -- pineapple has an unusually long single cycle among the crops in this dataset"),
    "Pomegranate": ("long", 165, "[gen] ~5-6 months from flowering to maturity"),
    "Rambutan": ("long", 110, "[gen] ~100-120 days from flowering to maturity"),
    "Rose Apple": ("long", 75, "[gen] fast-maturing among tree fruits, ~60-90 days from flowering"),
    "Soursop": ("long", 135, "[gen] ~4-5 months from fruit set to maturity"),
    "Wood Apple": ("long", 300, "[gen] notably slow-ripening like Beli Fruit, ~10+ months"),
}


def main():
    with open("backend/data/crops.json", "r", encoding="utf-8") as f:
        crops = json.load(f)

    if set(HARVEST_DATA.keys()) != {c["crop"] for c in crops}:
        missing = {c["crop"] for c in crops} - set(HARVEST_DATA.keys())
        extra = set(HARVEST_DATA.keys()) - {c["crop"] for c in crops}
        raise ValueError(f"Mismatch. Missing: {missing}, Extra: {extra}")

    for crop in crops:
        harvest_type, harvest_days, source_note = HARVEST_DATA[crop["crop"]]
        crop["harvestType"] = harvest_type
        crop["harvestDays"] = harvest_days
        # Append harvest-timing source info to the existing zone/soil notes
        crop["notes"] = crop["notes"] + f" Harvest timing: {source_note}."

    with open("backend/data/crops.json", "w", encoding="utf-8") as f:
        json.dump(crops, f, indent=2, ensure_ascii=False)

    reclassified = ["Jackfruit", "Papaya", "Pineapple"]
    print(f"Updated harvestType/harvestDays for {len(crops)} crops.")
    print(f"Re-classified short -> long: {reclassified}")
    short_count = sum(1 for c in crops if c["harvestType"] == "short")
    long_count = sum(1 for c in crops if c["harvestType"] == "long")
    print(f"short: {short_count}, long: {long_count}")


if __name__ == "__main__":
    main()
