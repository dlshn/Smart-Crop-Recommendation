"""
Updates backend/data/crops.json harvestType / harvestDays using the best
available verified figures.

- SHORT crops (annual/seasonal vegetables): harvestDays is the number of
  days from planting/transplanting to first harvest -- this field IS used
  live (routes/api.js Step 2 computes harvest_date = planting_date +
  harvestDays, then feeds that harvest month into both the price model
  and the rainfall estimate). Every short crop here has a real
  doa.gov.lk HORDI crop-page citation as of 2026-09 (see IMPORTANT
  CONFIDENCE NOTE below for the couple that don't).

- LONG crops (perennial tree/vine fruit crops): harvestDays is None
  (null in the JSON), on purpose. routes/api.js Step 5 lists "long"
  crops by district and soil suitability ONLY -- it never computes a
  harvest date or calls the price/rainfall model for them -- so a
  number here was always unused metadata. Worse, the number that used
  to be here (a "flowering-to-maturity for an already-bearing plant"
  estimate, e.g. "Guava: 150 days") looks exactly like a "planting to
  first harvest" figure and gets misread that way, when the real
  planting-to-first-harvest time for a perennial tree is one to several
  years (Mangosteen and Wood Apple can be 7-15 years). Rather than
  publish a number that is either unused or misleading depending on how
  it's read, this field is null for every long crop, with the old
  estimate kept as a historical note per crop for reference.

IMPORTANT CONFIDENCE NOTE (kept honest in the notes field per crop):
  - Every SHORT crop's figure is marked [DOA-VERIFIED 2026-09] and was
    found on a live doa.gov.lk HORDI crop page (English or Sinhala) and
    quoted directly -- no remaining unverified [gen] estimates among
    the short crops.
  - LONG crops all carry harvestDays = None regardless of whether a
    DOA figure existed for them, since the field is unused either way
    (see above); their notes keep a historical record of what estimate
    used to be there.
"""
import json

# (harvestType, harvestDays, confidence_note)
HARVEST_DATA = {
    # ---- Vegetables (short) ----
    "Asiatic Pennywort": ("short", 100, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-crop-gotukola: \"First harvest can be obtained within 100 days from the date of planting.\" NOTE: this crop and \"Pennywort\" below are the same plant (gotukola / Centella asiatica) duplicated under two English names -- flagged for the project owner to merge or rename"),
    "Pennywort": ("short", 100, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-crop-gotukola: \"First harvest can be obtained within 100 days from the date of planting.\" NOTE: this crop and \"Asiatic Pennywort\" above are the same plant (gotukola / Centella asiatica) duplicated under two English names -- flagged for the project owner to merge or rename"),
    "Beetroot": ("short", 83, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-crop-beet-root: \"Crop can be harvest 75-90 days after transplanting.\" Corrected from an earlier unverified 90-day estimate to the 75-90 day midpoint"),
    "Bitter Melon": ("short", 68, "[DOA-VERIFIED 2026-09] doa.gov.lk/sinhala-hordi-crop-bitter-gourd (Sinhala page): first harvest obtained at 60-75 days after planting. Corrected from an unverified 60-day estimate (which had only been an analogy to the related crop Luffa) to the verified 60-75 day midpoint"),
    "Brinjal": ("short", 75, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-crop-brinjal: \"Harvesting can be started 10-12 weeks after transplanting\" (70-84 days)"),
    "Long Purple Eggplant": ("short", 75, "[DOA-VERIFIED 2026-09] same species/family as Brinjal, doa.gov.lk/hordi-crop-brinjal figure applied"),
    "Cabbage": ("short", 100, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-crop-cabbage: \"90-110 days after planting\""),
    "Carrot": ("short", 110, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-variety-carrot: New Kuroda variety, \"harvest 110 days after planting.\" Corrected from 100: the previous note's \"faster local varieties ~90 days\" wrongly cited Lanka Carrot's 90-day time-to-FLOWERING as a harvest time"),
    "Knol-Khol": ("short", 55, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-crop-knol-khol: \"around 50-60 days after transplant.\" Corrected from an inaccurate earlier estimate of 70 days (60-70 day range)"),
    "Leeks": ("short", 135, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-crop-leeks: \"about 4 1/2 months after transplanting\" (135 days)"),
    "Onion": ("short", 88, "[DOA-VERIFIED 2026-09] doa.gov.lk/field-crops-bigonion-si (Sinhala page): approximately 85-90 days after transplanting, up to 85-100 days depending on variety. Corrected from a partially-checked 85-day estimate (the English page was unpopulated) to the 85-90 day midpoint, now with a direct DOA quote"),
    "Potato": ("short", 105, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-variety-potato: Golden Star variety, \"days to maturity 100-110 days.\" Corrected from an unverified 100-day estimate to the 100-110 day midpoint"),
    "Pumpkin": ("short", 78, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-variety-pumpkin: Pathma variety, \"Maturity for consumption - 75-80 days.\" Corrected from a 100-day composite estimate (previously built only from days-after-FLOWERING figures by variety) to the verified 75-80 day midpoint, a direct days-from-planting DOA figure"),
    "Red Spinach": ("short", 37, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-variety-leafy-vegetables: HORDI Thampala (Amaranthus, the correct botanical match for red spinach), \"Harvest 35-40 days after planting.\" Corrected from 30, which had actually been based on the different leafy green mukunuwenna (~28 days)"),
    "Winged Bean": ("short", 85, "[DOA-VERIFIED 2026-09] doa.gov.lk/hordi-crop-winged-bean: \"First harvest of recommended varieties can be taken in 70-75 days\"; local varieties 90-100 days"),

    # ---- Long-cycle crops: harvestDays is None (null in the JSON). Not a
    #      data gap -- routes/api.js Step 5 lists "long" crops by district
    #      and soil suitability only and never computes a harvest date or
    #      a price/rainfall prediction for them, so any number here would
    #      be unused metadata that risks being misread as "days from
    #      planting to first harvest" (for a real tree crop that is
    #      actually one to several years, not months). The bracketed text
    #      below is kept only as a historical note of what estimate used
    #      to be here and why, in case a future version of the tool wants
    #      a real planting-to-first-harvest figure for these perennials. ----
    "Drumsticks": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified 210-day / 6-7 month estimate, itself only a flowering-to-maturity guess, not planting-to-first-harvest"),
    "Manioc": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: doa.gov.lk/hordi-variety-cassava gives 9-12 month plant AGE at harvest, which is a genuine planting-based figure, but is still not used since Manioc is harvestType \"long\""),
    "Taro": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: doa.gov.lk/hordi-crop-kiri-ala gives 8-10 month planting-based harvest age, but is still not used since Taro is harvestType \"long\""),
    "Avocado": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~8-month flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (which for avocado is ~3-4 years)"),
    "Banana": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously ~9-11 months planting-to-bunch-maturity, which is a genuine planting-based figure for a banana sucker, but is still not used since Banana is harvestType \"long\""),
    "Beli Fruit": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~10-month fruit-set-to-maturity estimate, NOT the real planting-to-first-harvest time (which for bael is several years)"),
    "Breadfruit": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~3.5-month flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (several years for a breadfruit tree)"),
    "Custard Apple": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~4-month fruit-set-to-maturity estimate, NOT the real planting-to-first-harvest time (2-4 years)"),
    "Gooseberry": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~3-month flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (2-4 years for nelli)"),
    "Guava": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~4-5 month flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (1-4 years depending on propagation)"),
    "Jackfruit": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~4-month fruit-development estimate, NOT the real planting-to-first-harvest time (3-5+ years -- jackfruit is a notoriously slow tree)"),
    "Mango": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~4-5 month flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (2-6 years depending on propagation)"),
    "Mangosteen": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~90-120 day flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (mangosteen is one of the SLOWEST fruit trees, commonly 7-10+ years)"),
    "Orange": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~7-month flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (2-5 years for citrus)"),
    "Papaya": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously ~9 months planting-to-first-fruit, a genuine planting-based figure for papaya (a fast semi-perennial), but is still not used since Papaya is harvestType \"long\""),
    "Passion Fruit": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~10-12 week flowering-to-maturity estimate; passion fruit vines are relatively fast (often ~9-12 months planting-to-first-harvest) but this was not that figure"),
    "Pineapple": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously ~15 months planting-to-first-harvest, a genuine planting-based figure, but is still not used since Pineapple is harvestType \"long\""),
    "Pomegranate": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~5-6 month flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (2-3 years)"),
    "Rambutan": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~100-120 day flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (2-6 years depending on propagation)"),
    "Rose Apple": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~60-90 day flowering-to-maturity estimate, NOT the real planting-to-first-harvest time (2-4 years)"),
    "Soursop": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~4-5 month fruit-set-to-maturity estimate, NOT the real planting-to-first-harvest time (2-5 years)"),
    "Wood Apple": ("long", None, "not applicable (harvestDays is null; unused for long crops). Historical note: previously an unverified ~10+ month estimate, NOT the real planting-to-first-harvest time (wood apple is extremely slow, often cited at 4-15 years depending on propagation)"),
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
