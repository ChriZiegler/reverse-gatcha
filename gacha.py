import json
import random
from datetime import datetime, timezone
from pathlib import Path

PROMPTS_FILE = Path(__file__).parent / "prompts.json"


def _load_prompts() -> dict:
    return json.loads(PROMPTS_FILE.read_text())


def _pick_weighted(items: list[dict]) -> str:
    """Pick an item using weights. Default weight is 0, higher = more likely."""
    weights = [max(1, 10 + item.get("weight", 0)) for item in items]
    return random.choices(items, weights=weights, k=1)[0]["name"]


def _pick_rarity(rarities: list[dict]) -> dict:
    """Pick a rarity using explicit weights. Returns {name, time}."""
    weights = [r["weight"] for r in rarities]
    picked = random.choices(rarities, weights=weights, k=1)[0]
    return {"name": picked["name"], "time": picked["time"]}


def roll() -> dict:
    prompts = _load_prompts()

    species = _pick_weighted(prompts["species"])
    element = _pick_weighted(prompts["elements"])
    rarity = _pick_rarity(prompts["rarities"])

    return {
        "id": str(int(datetime.now(timezone.utc).timestamp() * 1000)),
        "prompt": f"{element} {species}",
        "rarity": rarity["name"],
        "time": rarity["time"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "image_path": None,
    }


if __name__ == "__main__":
    for _ in range(5):
        print(roll())
