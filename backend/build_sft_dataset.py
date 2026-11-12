"""Build DRAFT supervised fine-tuning data for Atlas from data/processed/travel.jsonl.

Teaches BEHAVIOUR, not facts:
  - exactly N days, pace-aware number of activities
  - only use what the travel notes say; no invented venues, prices or hours
  - say what the dataset does not cover
  - apply revisions without losing the original constraints
  - say so when the destination is not in the notes

Outputs (chat "messages" format, split BY CITY to limit leakage):
  data/training/sft_train.jsonl, sft_validation.jsonl, sft_test.jsonl

Run from backend/:  python build_sft_dataset.py
These are template-generated drafts: read ~20 random lines before training.
"""
import copy
import json
import random
import re
from pathlib import Path

from prompts import (
    SYSTEM_PROMPT,
    REVISE_PROMPT,
    trip_request,
    itinerary_user_message,
    revise_user_message,
)

SRC = Path("data/processed/travel.jsonl")
OUT_DIR = Path("data/training")
random.seed(42)

ACTIVITIES = {
    "history": "Visit the main historic sites and landmarks",
    "culture": "Take a cultural walk through local neighbourhoods",
    "museums": "Spend time at a museum or gallery",
    "art": "Browse art galleries and creative districts",
    "food": "Try local dishes at a neighbourhood eatery",
    "shopping": "Browse local shops and markets",
    "nightlife": "Enjoy the local nightlife",
    "nature": "Spend time outdoors in nature",
    "beaches": "Relax by the water",
    "landmarks": "See the best-known landmarks",
    "romance": "Take a slow, scenic evening stroll",
    "adventure": "Try an outdoor adventure activity",
    "architecture": "Admire the local architecture",
    "religion": "Visit notable religious or spiritual sites",
    "ancient ruins": "Explore the ancient ruins",
    "wildlife": "Look for local wildlife",
    "hiking": "Go for a hike",
    "relaxation": "Take it easy with a relaxing activity",
}
FREE = "Free time to rest or wander at your own pace"
SLOTS = {
    "Relaxed": ["Morning", "Evening"],
    "Balanced": ["Morning", "Afternoon", "Evening"],
    "Busy": ["Morning", "Afternoon", "Evening", "Night"],
}
BUDGETS = ["", "budget", "moderate", "luxury", "around $100 per day"]
EXTRAS = ["", "", "avoid long walks", "include local food", "travelling with kids"]
OFF_TOPIC_INTERESTS = ["skiing", "surfing", "safari"]
UNLISTED_CITIES = ["Lisbon", "Hanoi", "Cusco", "Reykjavik", "Tallinn", "Nairobi",
                   "Oslo", "Porto", "Krakow", "Lima", "Kyoto", "Bergen"]

CHANGES = {
    "less_busy": ["Make day {n} less busy", "Day {n} feels too packed, please lighten it",
                  "Can you relax day {n}?"],
    "food": ["Add more food", "I want more local food experiences", "More food please"],
    "outdoor": ["More outdoor activities", "Can we spend more time outdoors?"],
    "cheaper": ["Reduce the budget", "Make it cheaper", "Keep costs lower"],
}


def load():
    with SRC.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def best_months(rec):
    m = re.search(r"Best time to travel:\s*(.+?)\.?$", rec["description"])
    return m.group(1) if m else ""


def matches(interest, tag):
    return interest in tag or tag in interest


def pick_notes(rec, pool):
    same = [r for r in pool if r["country"] == rec["country"] and r["id"] != rec["id"]]
    others = [r for r in pool if r["country"] != rec["country"]]
    random.shuffle(same)
    random.shuffle(others)
    notes = [rec] + (same + others)[:3]
    if random.random() < 0.3:
        random.shuffle(notes)
    return notes


def pick_interests(rec):
    r = random.random()
    if r < 0.1:
        return []
    chosen = random.sample(rec["tags"], k=min(len(rec["tags"]), random.randint(1, 3)))
    if r > 0.85:
        chosen[-1] = random.choice(OFF_TOPIC_INTERESTS)
    return chosen


def activity(tag, city, used):
    if tag in used:
        return f"Explore more of {city}'s {tag} side"
    used.add(tag)
    return f"{ACTIVITIES.get(tag, 'Explore the ' + tag + ' highlights')} in {city}"


def build_plan(rec, days, pace, interests):
    tags = rec["tags"]
    pref = [t for t in tags if any(matches(i, t) for i in interests)]
    order = pref + [t for t in tags if t not in pref] or [rec["category"] or "sightseeing"]
    used, plan, k = set(), [], 0
    for _ in range(days):
        items, day_tags = [], []
        for slot in SLOTS[pace]:
            tag = order[k % len(order)]
            k += 1
            day_tags.append(tag)
            items.append((slot, activity(tag, rec["city"], used)))
        if pace == "Relaxed":
            items.insert(1, ("Afternoon", FREE))
        theme = " and ".join(t.title() for t in dict.fromkeys(day_tags[:2]))
        plan.append({"theme": theme, "items": items})
    return plan


def render(plan, rec, budget, missing, extra, header="", revision_notes=()):
    lines = [header, ""] if header else []
    for i, day in enumerate(plan, 1):
        lines.append(f"Day {i}: {day['theme']}")
        lines += [f"- {slot}: {text}" for slot, text in day["items"]]
        lines.append("")
    lines.append("Notes:")
    lines.append(f"- Based on dataset entry [{rec['id']}]: {rec['city']} is known for {', '.join(rec['tags'])}.")
    months = best_months(rec)
    if months:
        lines.append(f"- Best time to travel: {months}.")
    lines.append("- Opening hours, prices and transport times are not in the dataset, so check them before you go.")
    if budget:
        lines.append(f"- Budget ({budget}): the dataset has no price data, so costs need checking.")
    if missing:
        lines.append(f"- The dataset does not list {', '.join(missing)} for {rec['city']}; check local sources.")
    if extra:
        lines.append(f"- Noted your preference: {extra}. Check distances and suitability locally.")
    lines += [f"- {n}" for n in revision_notes]
    return "\n".join(lines)


def make_trip(rec):
    return {
        "days": random.randint(1, 7),
        "pace": random.choice(list(SLOTS)),
        "budget": random.choice(BUDGETS),
        "extra": random.choice(EXTRAS),
        "interests": pick_interests(rec),
    }


def example(system, user, assistant):
    return {"messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}


def make_itinerary(rec, pool):
    t = make_trip(rec)
    notes = pick_notes(rec, pool)
    request = trip_request(rec["city"], t["days"], t["budget"], ", ".join(t["interests"]), t["pace"], t["extra"])
    plan = build_plan(rec, t["days"], t["pace"], t["interests"])
    missing = [i for i in t["interests"] if not any(matches(i, tag) for tag in rec["tags"])]
    answer = render(plan, rec, t["budget"], missing, t["extra"])
    return example(SYSTEM_PROMPT, itinerary_user_message(request, notes), answer)


def revise_plan(plan, rec, kind, n):
    plan = copy.deepcopy(plan)
    tags, city = rec["tags"], rec["city"]
    notes = []
    if kind == "less_busy":
        day = plan[n - 1]
        day["items"] = [day["items"][0], ("Afternoon", FREE),
                        ("Evening", "A relaxed evening with no fixed plans")]
        notes.append(f"Day {n} now has fewer activities and more free time.")
    elif kind == "food":
        for day in plan:
            day["items"][-1] = (day["items"][-1][0], f"{ACTIVITIES['food']} in {city}")
        notes.append("Added a local food stop to each day." if "food" in tags
                     else f"The dataset does not list food for {city}; look for local recommendations.")
    elif kind == "outdoor":
        for day in plan:
            day["items"][-1] = (day["items"][-1][0], f"Spend time outdoors in {city}")
        if not any(matches("nature", t) or matches("outdoor", t) for t in tags):
            notes.append(f"The dataset does not list outdoor activities for {city}; check local sources.")
        else:
            notes.append("Added outdoor time to each day.")
    elif kind == "cheaper":
        for day in plan:
            day["items"] = [
                (s, f"Explore {city}'s public spaces on foot")
                if any(w in text.lower() for w in ("shop", "nightlife")) else (s, text)
                for s, text in day["items"]
            ]
        notes.append("Budget lowered: the dataset has no price data, so check costs for each activity.")
    return plan, notes


def make_revision(rec, pool):
    t = make_trip(rec)
    t["days"] = max(2, t["days"])
    notes = pick_notes(rec, pool)
    request = trip_request(rec["city"], t["days"], t["budget"], ", ".join(t["interests"]), t["pace"], t["extra"])
    plan = build_plan(rec, t["days"], t["pace"], t["interests"])
    missing = [i for i in t["interests"] if not any(matches(i, tag) for tag in rec["tags"])]
    current = render(plan, rec, t["budget"], missing, t["extra"])

    kind = random.choice(list(CHANGES))
    n = random.randint(1, t["days"])
    change = random.choice(CHANGES[kind]).format(n=n)
    new_plan, rev_notes = revise_plan(plan, rec, kind, n)
    answer = render(new_plan, rec, t["budget"], missing, t["extra"],
                    header="Here is your updated itinerary:", revision_notes=rev_notes)
    return example(REVISE_PROMPT, revise_user_message(request, current, change, notes), answer)


def make_uncovered(pool, known_cities):
    city = random.choice([c for c in UNLISTED_CITIES if c.lower() not in known_cities])
    t = {"days": random.randint(1, 7), "pace": random.choice(list(SLOTS)),
         "budget": random.choice(BUDGETS), "extra": random.choice(EXTRAS)}
    notes = random.sample(pool, 3)
    request = trip_request(city, t["days"], t["budget"], "", t["pace"], t["extra"])
    names = ", ".join(n["city"] for n in notes)
    answer = (
        f"The travel notes I have don't cover {city}, so I can't build a plan grounded in the dataset, "
        f"and I don't want to invent details.\n\n"
        f"The closest matches in my notes are: {names}. If one of these interests you, tell me and I'll plan it.\n\n"
        f"Otherwise, check official tourism sources for {city} for sights, opening hours, prices and transport."
    )
    return example(SYSTEM_PROMPT, itinerary_user_message(request, notes), answer)


def write(name, rows):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"sft_{name}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{name}: {len(rows)} examples -> {path}")


def main():
    records = load()
    known = {r["city"].lower() for r in records}
    cities = records[:]
    random.shuffle(cities)
    n_hold = max(1, len(cities) // 10)
    split = {
        "validation": cities[:n_hold],
        "test": cities[n_hold:2 * n_hold],
        "train": cities[2 * n_hold:],
    }
    for name, recs in split.items():
        train = name == "train"
        rows = []
        for rec in recs:
            rows += [make_itinerary(rec, records) for _ in range(4 if train else 2)]
            rows += [make_revision(rec, records) for _ in range(2 if train else 1)]
        rows += [make_uncovered(records, known) for _ in range(30 if train else 4)]
        random.shuffle(rows)
        write(name, rows)


if __name__ == "__main__":
    main()