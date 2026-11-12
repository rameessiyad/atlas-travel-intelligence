"""Convert a raw Kaggle travel dataset (CSV / JSON / JSONL) into Atlas travel.jsonl.

Usage (run from the backend folder):

    python convert_dataset.py \
        --input data/raw/attractions.csv \
        --output data/processed/travel.jsonl \
        --source-name kaggle-attractions \
        --source-url https://www.kaggle.com/datasets/OWNER/NAME

If your column names are unusual, map them manually:

    --map place_name=Name --map description=About --map city=Location

Run with --inspect first to see your columns and sample rows.
"""
import argparse
import csv
import json
import re
from pathlib import Path

# Atlas field -> column names we will try automatically (case-insensitive)
ALIASES = {
    "place_name": ["place_name", "name", "title", "attraction", "attraction_name", "place", "poi"],
    "city": ["city", "town", "destination", "location_city"],
    "country": ["country", "nation", "country_name"],
    "category": ["category", "type", "categories", "kind", "attraction_type"],
    "description": ["description", "desc", "about", "summary", "details", "overview", "text"],
    "tags": ["tags", "keywords", "themes", "labels"],
    "source_id": ["id", "place_id", "poi_id", "uid"],
}

MIN_DESC_CHARS = 20


def clean(value) -> str:
    """Strip, collapse whitespace, treat nulls as empty."""
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return "" if text.lower() in {"nan", "none", "null", "n/a", "na", "-"} else text


def read_rows(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".csv":
        for enc in ("utf-8-sig", "latin-1"):
            try:
                with path.open("r", encoding=enc, newline="") as f:
                    return list(csv.DictReader(f))
            except UnicodeDecodeError:
                continue
        raise ValueError("Could not decode CSV file")
    if suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            # {"records": [...]} style, otherwise a single object
            for value in data.values():
                if isinstance(value, list):
                    return value
            return [data]
        return data
    raise ValueError(f"Unsupported file type: {suffix}")


def build_mapping(columns, overrides):
    lower = {c.lower().strip(): c for c in columns}
    mapping = {}
    for field, names in ALIASES.items():
        for name in names:
            if name in lower:
                mapping[field] = lower[name]
                break
    for item in overrides:
        field, _, col = item.partition("=")
        if col not in columns:
            raise SystemExit(f"--map: column '{col}' not found. Columns: {list(columns)}")
        mapping[field.strip()] = col
    return mapping


def to_tags(raw_tags: str, category: str):
    parts = re.split(r"[;,|]", raw_tags) if raw_tags else []
    if category:
        parts.append(category)
    seen, tags = set(), []
    for p in parts:
        p = p.strip().lower()
        if p and p not in seen:
            seen.add(p)
            tags.append(p)
    return tags[:8]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default="data/processed/travel.jsonl")
    ap.add_argument("--source-name", default="kaggle-dataset")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--map", action="append", default=[], help="field=ColumnName")
    ap.add_argument("--limit", type=int, default=0, help="max records (0 = all)")
    ap.add_argument("--inspect", action="store_true", help="show columns + samples, then exit")
    args = ap.parse_args()

    rows = read_rows(Path(args.input))
    if not rows:
        raise SystemExit("No rows found in input file.")

    columns = list(rows[0].keys())
    print(f"Rows: {len(rows)}")
    print(f"Columns: {columns}")

    if args.inspect:
        for row in rows[:3]:
            print(json.dumps(row, ensure_ascii=False, indent=2)[:800])
        return

    mapping = build_mapping(columns, args.map)
    print(f"Mapping used: {mapping}")
    for required in ("place_name", "description"):
        if required not in mapping:
            raise SystemExit(f"Could not find a column for '{required}'. Use --map {required}=YourColumn")

    prefix = re.sub(r"[^a-z0-9]+", "-", args.source_name.lower()).strip("-")
    source = args.source_url or args.source_name
    stats = {"missing_name": 0, "short_description": 0, "duplicate": 0}
    seen, records = set(), []

    for row in rows:
        def get(field):
            col = mapping.get(field)
            return clean(row.get(col)) if col else ""

        name, desc = get("place_name"), get("description")
        city, country, category = get("city"), get("country"), get("category")

        if not name:
            stats["missing_name"] += 1
            continue
        if len(desc) < MIN_DESC_CHARS:
            stats["short_description"] += 1
            continue
        key = (name.lower(), city.lower(), country.lower())
        if key in seen:
            stats["duplicate"] += 1
            continue
        seen.add(key)

        source_id = get("source_id")
        records.append({
            "id": f"{prefix}-{source_id or len(records) + 1}",
            "place_name": name,
            "city": city,
            "country": country,
            "category": category.lower(),
            "description": desc,
            "tags": to_tags(get("tags"), category),
            "source": source,
        })
        if args.limit and len(records) >= args.limit:
            break

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(records)} records to {out}")
    print(f"Dropped: {stats}")
    print("Next: open the file and manually review ~20 random lines before ingesting.")


if __name__ == "__main__":
    main()