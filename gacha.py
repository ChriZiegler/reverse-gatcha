import random
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROMPTS_FILE = Path(__file__).parent / "prompts.yaml"


def _load_prompts() -> dict:
    return yaml.safe_load(PROMPTS_FILE.read_text())


def _pick_aspects(aspects: list[dict]) -> list[dict]:
    """Pick 1 or 2 aspects at random. No two aspects may share a category."""
    first = random.choice(aspects)
    if random.random() < 0.5:
        return [first]

    first_category = first.get("category")
    eligible = [
        a for a in aspects
        if a is not first and (first_category is None or a.get("category") != first_category)
    ]
    if not eligible:
        return [first]
    return [first, random.choice(eligible)]


def _resolve_rarity(rarities: list[dict], total_price: int) -> dict:
    """Find the highest rarity whose price threshold is <= total_price."""
    # Sort descending by price so we match the highest qualifying tier
    for r in sorted(rarities, key=lambda r: r["price"], reverse=True):
        if total_price >= r["price"]:
            return r
    return rarities[0]


def roll() -> dict:
    prompts = _load_prompts()

    aspects = _pick_aspects(prompts["aspects"])
    total_price = sum(a["price"] for a in aspects)
    rarity = _resolve_rarity(prompts["rarities"], total_price)

    prompt = " ".join(a["name"] for a in aspects)

    return {
        "id": str(int(datetime.now(timezone.utc).timestamp() * 1000)),
        "prompt": prompt,
        "rarity": rarity["name"],
        "time": rarity["time"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "image_path": None,
    }


if __name__ == "__main__":
    for _ in range(10):
        r = roll()
        print(f"{r['rarity']}  {r['prompt']}")
