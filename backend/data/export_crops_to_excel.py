"""
Exports backend/data/crops.json to an Excel workbook for supervisor
review: backend/data/crops_export.xlsx

Four sheets:
  1. "Crops" - one row per crop: category, harvest type/days, the real
     Sri Lankan Great Soil Group(s) (only -- texture/drainage
     descriptors were removed from the data on request, so this is the
     full soilTypes value now), and district count with the full
     district list.
  2. "Sources & Notes" - one row per crop with the FULL notes text
     (district/soil/harvest sourcing), for the supervisor to check the
     citations in full without truncation.
  3. "Soil Types Summary" - the 4 Great Soil Groups actually USED in
     this project's 37 crops, with crop counts and names.
  4. "Sri Lanka Soil Groups (Reference)" - the FULL official list of
     all 14 Great Soil Groups recognised nationally (not just the 4
     used here), with zone, a short description and the source
     citation, for the supervisor to see the complete authoritative
     classification this project's soil field is drawn from.
"""
import json
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill(start_color="6E1220", end_color="6E1220", fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
TOP = Alignment(vertical="top")


def style_header(ws, ncols):
    for col in range(1, ncols + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"


def autosize(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def main():
    with open("backend/data/crops.json", "r", encoding="utf-8") as f:
        crops = json.load(f)

    wb = Workbook()

    # ---- Sheet 1: Crops summary ----
    ws1 = wb.active
    ws1.title = "Crops"
    headers1 = [
        "Crop", "Category", "Harvest Type", "Harvest Days",
        "Real Sri Lankan Soil Group(s)",
        "District Count", "Suitable Districts",
    ]
    ws1.append(headers1)

    for c in crops:
        ws1.append([
            c["crop"],
            c["category"],
            c["harvestType"],
            c["harvestDays"] if c["harvestDays"] is not None else "N/A (unused for long crops)",
            ", ".join(c["soilTypes"]) if c["soilTypes"] else "(not yet classified)",
            len(c["districts"]),
            ", ".join(c["districts"]),
        ])

    for row in ws1.iter_rows(min_row=2, max_row=ws1.max_row):
        for cell in row:
            cell.alignment = TOP
        row[6].alignment = WRAP  # Suitable Districts column wraps

    style_header(ws1, len(headers1))
    autosize(ws1, [20, 11, 12, 12, 34, 12, 55])
    ws1.auto_filter.ref = ws1.dimensions

    # ---- Sheet 2: Full sources / notes ----
    ws2 = wb.create_sheet("Sources & Notes")
    headers2 = ["Crop", "Full Notes (district / soil / harvest sourcing)"]
    ws2.append(headers2)
    for c in crops:
        ws2.append([c["crop"], c["notes"]])

    for row in ws2.iter_rows(min_row=2, max_row=ws2.max_row):
        row[0].alignment = TOP
        row[1].alignment = WRAP

    style_header(ws2, len(headers2))
    autosize(ws2, [20, 140])

    # ---- Sheet 3: Soil Types Summary ----
    ws3 = wb.create_sheet("Soil Types Summary")
    headers3 = ["Real Sri Lankan Soil Group", "Crop Count", "Crops"]
    ws3.append(headers3)

    soil_to_crops = defaultdict(list)
    for c in crops:
        for s in c["soilTypes"]:
            soil_to_crops[s].append(c["crop"])

    for soil in sorted(soil_to_crops, key=lambda s: (-len(soil_to_crops[s]), s)):
        crop_list = soil_to_crops[soil]
        ws3.append([soil, len(crop_list), ", ".join(sorted(crop_list))])

    for row in ws3.iter_rows(min_row=2, max_row=ws3.max_row):
        for cell in row:
            cell.alignment = TOP
        row[2].alignment = WRAP

    style_header(ws3, len(headers3))
    autosize(ws3, [30, 12, 95])
    ws3.auto_filter.ref = ws3.dimensions

    # ---- Sheet 4: Sri Lanka Soil Groups (Reference) ----
    # Sri Lanka's official soil classification: 14 Great Soil Groups,
    # from the Land and Water Use Division, Department of Agriculture,
    # Peredeniya (the Moormann & Panabokke classification, 1961/1979),
    # as reported via the Sri Lanka Biodiversity portal (lk.chm-cbd.net)
    # and corroborated by agrifarming.in -- checked live 2026-09. This
    # is the FULL national list; the "Crop Count" column is computed
    # live from crops.json (soil_to_crops, built above for Sheet 3), not
    # hardcoded, so it always reflects the current data.
    SOURCE = "Land and Water Use Division, Dept. of Agriculture, Peredeniya (Moormann & Panabokke classification); lk.chm-cbd.net/biodiversity, agrifarming.in -- checked 2026-09"
    REFERENCE_GROUPS = [
        ("Reddish Brown Earths", "Dry Zone (dominant, largest area)", "Occupies the largest area of any soil group nationally; named districts include Anuradhapura, Polonnaruwa, Ampara, Monaragala, Hambantota."),
        ("Low Humic Gley Soils", "Dry Zone", "Poorly-drained lowland/valley-bottom soils within the Dry Zone."),
        ("Non-Calcic Brown Soils", "Dry Zone", "Found within the Dry Zone, alongside Reddish Brown Earths."),
        ("Red-Yellow Latosols", "Dry Zone", "A Dry Zone latosolic (highly weathered) soil group."),
        ("Alluvial Soils", "Flood plains of the larger rivers (all zones)", "River-deposited soils on the flood plains of major rivers."),
        ("Soils of the Old Alluvium", "Dry Zone", "Older river-terrace deposits, no longer subject to regular flooding."),
        ("Solodized Solonetz", "Dry Zone, arid areas", "Found in the more arid pockets of the Dry Zone."),
        ("Regosols", "Coastal areas", "Young, weakly-developed sandy soils of the coastal belt."),
        ("Grumusols", "Dry Zone (small extent)", "Dark, cracking clay soils; a minor-extent Dry Zone group."),
        ("Rendzinas", "Dry Zone (small extent)", "Shallow soils typically over limestone; a minor-extent Dry Zone group."),
        ("Red-Yellow Podzolic Soils", "Wet Zone and wetter Intermediate Zone (dominant)", "The most widespread Wet Zone soil group; deep, with sandy loam / sandy clay loam / loam surface texture."),
        ("Reddish Brown Latosolic Soils", "Wet Zone", "Relatively young soils on terrain incised by geological erosion; mostly sandy clay loam texture."),
        ("Immature Brown Loams", "Wet Zone, upcountry hill areas", "The documented soil group of the upcountry vegetable belt (Nuwara Eliya / Badulla / Matale)."),
        ("Bog and Half-Bog Soils", "Wet Zone tidal marshes", "Waterlogged organic soils found mainly in Wet Zone tidal marsh areas."),
    ]

    ws4 = wb.create_sheet("SL Soil Groups (Reference)")
    headers4 = ["#", "Great Soil Group", "Zone / Region", "Used in this project?", "Crop Count", "Description", "Source"]
    ws4.append(headers4)
    for i, (name, zone, desc) in enumerate(REFERENCE_GROUPS, start=1):
        crop_count = len(soil_to_crops.get(name, []))
        used = "USED" if crop_count > 0 else "-"
        ws4.append([i, name, zone, used, crop_count, desc, SOURCE])

    for row in ws4.iter_rows(min_row=2, max_row=ws4.max_row):
        for cell in row:
            cell.alignment = TOP
        row[5].alignment = WRAP
        row[6].alignment = WRAP

    style_header(ws4, len(headers4))
    autosize(ws4, [4, 28, 34, 18, 11, 60, 55])
    ws4.auto_filter.ref = ws4.dimensions

    out_path = "backend/data/crops_export.xlsx"
    wb.save(out_path)
    print(f"Wrote {out_path} ({len(crops)} crops, 4 sheets).")


if __name__ == "__main__":
    main()
