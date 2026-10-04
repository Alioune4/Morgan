import os
import re
from pathlib import Path
from typing import List


DEFAULT_PROFILE_PATH = Path(__file__).resolve().parent.parent / "profile.md"


def load_profile() -> str:
    path = Path(os.getenv("PROFILE_PATH", DEFAULT_PROFILE_PATH))
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}. Copy profile.example.md to profile.md and fill it in.")
    return path.read_text(encoding="utf-8")


def get_sources(profile: str) -> List[str]:
    match = re.search(r"^##\s*Sources\s*$(.*?)(?=^##\s|\Z)", profile, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if match is None:
        return []
    return re.findall(r"https?://\S+", match.group(1))
