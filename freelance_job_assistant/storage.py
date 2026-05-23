from __future__ import annotations

import json
from pathlib import Path

from .models import SkillProfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = PROJECT_ROOT / "data" / "profile.json"


def load_profile() -> SkillProfile:
    if not PROFILE_PATH.exists():
        return SkillProfile()

    try:
        return SkillProfile.model_validate_json(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return SkillProfile()


def save_profile(profile: SkillProfile) -> None:
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(
        json.dumps(profile.model_dump(), indent=2),
        encoding="utf-8",
    )
