import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
PULLS_FILE = DATA_DIR / "pulls.json"
IMAGES_DIR = DATA_DIR / "images"


def resolve_image_path(rel: str | None) -> Path | None:
    """Convert a stored relative path string to an absolute Path."""
    if rel is None:
        return None
    return PROJECT_ROOT / rel


def _ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)
    if not PULLS_FILE.exists() or PULLS_FILE.read_text().strip() == "":
        PULLS_FILE.write_text("[]")


def load_pulls() -> list[dict]:
    _ensure_dirs()
    return json.loads(PULLS_FILE.read_text())


def save_pull(pull: dict) -> None:
    pulls = load_pulls()
    pulls.append(pull)
    PULLS_FILE.write_text(json.dumps(pulls, indent=2))


def update_pull(pull_id: str, updates: dict) -> dict | None:
    pulls = load_pulls()
    for pull in pulls:
        if pull["id"] == pull_id:
            pull.update(updates)
            PULLS_FILE.write_text(json.dumps(pulls, indent=2))
            return pull
    return None


def delete_pull(pull_id: str) -> dict | None:
    pulls = load_pulls()
    for i, pull in enumerate(pulls):
        if pull["id"] == pull_id:
            removed = pulls.pop(i)
            PULLS_FILE.write_text(json.dumps(pulls, indent=2))
            if removed["image_path"]:
                path = resolve_image_path(removed["image_path"])
                if path.exists():
                    path.unlink()
            return removed
    return None


def get_pull(pull_id: str) -> dict | None:
    for pull in load_pulls():
        if pull["id"] == pull_id:
            return pull
    return None
