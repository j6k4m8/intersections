from __future__ import annotations

import re
import unicodedata
from collections import Counter
from collections.abc import Iterable


_STREET_SUFFIXES = (
    "avenue",
    "ave",
    "boulevard",
    "blvd",
    "court",
    "ct",
    "drive",
    "dr",
    "highway",
    "hwy",
    "lane",
    "ln",
    "parkway",
    "pkwy",
    "place",
    "pl",
    "road",
    "rd",
    "street",
    "st",
    "terrace",
    "ter",
    "way",
)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "intersection"


def _coerce_name_iter(value: object) -> Iterable[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(item) for item in value if item]
    return [str(value)]


def clean_road_name(value: object) -> list[str]:
    names: list[str] = []
    suffix_pattern = rf"\b(?:{'|'.join(_STREET_SUFFIXES)})\.?$"
    for raw_name in _coerce_name_iter(value):
        compact = " ".join(raw_name.replace("_", " ").split()).strip()
        if not compact:
            continue
        trimmed = re.sub(suffix_pattern, "", compact, flags=re.IGNORECASE).strip(" ,")
        cleaned = trimmed or compact
        names.append(cleaned.title())
    return names


def rank_road_names(edge_name_values: Iterable[object]) -> list[str]:
    counts: Counter[str] = Counter()
    for edge_name in edge_name_values:
        counts.update(clean_road_name(edge_name))
    return [name for name, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def format_road_label(road_names: list[str], max_names: int = 4) -> str:
    visible = road_names[:max_names]
    if not visible:
        return "Unnamed Intersection"
    if len(visible) == 1:
        return f"{visible[0]} & {visible[0]}"
    if len(visible) == 2:
        return f"{visible[0]} & {visible[1]}"
    return f"{', '.join(visible[:-1])} & {visible[-1]}"
