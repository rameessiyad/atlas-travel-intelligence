import csv, json, re
from pathlib import Path

SRC = Path("data/raw/travel_destinations.csv")
OUT = Path("data/processed/travel.jsonl")
URL = "https://www.kaggle.com/datasets/leondesilva1/travel-destinations"

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

OUT.parent.mkdir(parents=True, exist_ok=True)
count = 0
with SRC.open(encoding="utf-8-sig", newline="") as f, OUT.open("w", encoding="utf-8") as out:
    for row in csv.DictReader(f):
        city = row["City"].strip()
        country = row["Country"].strip()
        tags = [t.strip().lower() for t in row["Category"].split(",") if t.strip()]
        months = row["Best_Time_to_Travel"].strip()
        if not city or not tags:
            continue
        rec = {
            "id": f"city-{slug(city)}-{slug(country)}",
            "place_name": city,
            "city": city,
            "country": country,
            "category": tags[0],
            "description": (
                f"{city}, {country} is known for {', '.join(tags)}. "
                f"Best time to travel: {months}."
            ),
            "tags": tags,
            "source": URL,
        }
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        count += 1
print(f"Wrote {count} records to {OUT}")