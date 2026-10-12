"""Profile schema and validation for the personalization engine.

The profile is the only input to the planner. Validation is strict so that a
missing field can never silently become a default recommendation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Required fields. A missing value here is an error, never a silent default.
PROFILE_FIELDS = (
    "hearing_aid",
    "hearing_aid_streaming",
    "tv_setup",
    "tv_can_configure",
    "favourite_program",
    "favourite_time",
    "living",
    "caregiver_hours_per_day",
    "top_complaints",
    "medications_ototoxic",
    "walk_minutes_per_day",
)

# Optional fields that refine the plan; safe defaults apply when absent.
OPTIONAL_FIELDS = (
    "uses_captions",
    "tinnitus",
    "falls_last_year",
    "cognitive_impairment",
)

COMPLAINTS = (
    "tv",
    "noise",
    "group",
    "phone",
    "quick_speech",
    "female_voice",
    "fatigue",
)

STREAMING = ("none", "bluetooth", "tv_adapter", "remote_mic", "unknown")

TV_SETUPS = ("smart_tv", "cable_box", "old_tv", "streaming_stick", "unknown")

LIVING = ("alone", "with_family", "care_facility")


class ProfileError(ValueError):
    """Raised when a profile is missing fields or holds invalid values."""


@dataclass
class Profile:
    """Validated participant profile."""

    hearing_aid: str
    hearing_aid_streaming: str
    tv_setup: str
    tv_can_configure: bool
    favourite_program: str
    favourite_time: str
    living: str
    caregiver_hours_per_day: float
    top_complaints: list[str]
    medications_ototoxic: bool
    walk_minutes_per_day: int
    uses_captions: bool = False
    tinnitus: bool = False
    falls_last_year: int = 0
    cognitive_impairment: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Profile":
        missing = [f for f in PROFILE_FIELDS if f not in data]
        if missing:
            raise ProfileError("missing profile fields: " + ", ".join(missing))

        streaming = str(data["hearing_aid_streaming"]).lower()
        if streaming not in STREAMING:
            raise ProfileError(f"hearing_aid_streaming must be one of {STREAMING}")

        tv_setup = str(data["tv_setup"]).lower()
        if tv_setup not in TV_SETUPS:
            raise ProfileError(f"tv_setup must be one of {TV_SETUPS}")

        living = str(data["living"]).lower()
        if living not in LIVING:
            raise ProfileError(f"living must be one of {LIVING}")

        complaints = data["top_complaints"]
        if not isinstance(complaints, list) or not complaints:
            raise ProfileError("top_complaints must be a non-empty list")
        unknown = [c for c in complaints if c not in COMPLAINTS]
        if unknown:
            raise ProfileError("unknown complaints: " + ", ".join(map(str, unknown)))

        try:
            caregiver_hours = float(data["caregiver_hours_per_day"])
            walk_minutes = int(data["walk_minutes_per_day"])
            falls = int(data.get("falls_last_year", 0))
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise ProfileError(f"numeric field invalid: {exc}") from exc

        if caregiver_hours < 0 or walk_minutes < 0 or falls < 0:
            raise ProfileError("numeric fields must be non-negative")

        known = set(PROFILE_FIELDS)
        extra = {k: v for k, v in data.items() if k not in known}

        return cls(
            hearing_aid=str(data["hearing_aid"]),
            hearing_aid_streaming=streaming,
            tv_setup=tv_setup,
            tv_can_configure=bool(data["tv_can_configure"]),
            favourite_program=str(data["favourite_program"]),
            favourite_time=str(data["favourite_time"]),
            living=living,
            caregiver_hours_per_day=caregiver_hours,
            top_complaints=list(complaints),
            medications_ototoxic=bool(data["medications_ototoxic"]),
            walk_minutes_per_day=walk_minutes,
            uses_captions=bool(data.get("uses_captions", False)),
            tinnitus=bool(data.get("tinnitus", False)),
            falls_last_year=falls,
            cognitive_impairment=bool(data.get("cognitive_impairment", False)),
            extra=extra,
        )
