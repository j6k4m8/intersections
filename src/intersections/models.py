from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Signal:
    osm_id: int
    latitude: float
    longitude: float

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass(frozen=True)
class Intersection:
    cluster_id: int
    latitude: float
    longitude: float
    signal_ids: tuple[int, ...]

    @property
    def signal_count(self) -> int:
        return len(self.signal_ids)

    def to_dict(self) -> dict[str, float | int | tuple[int, ...]]:
        payload = asdict(self)
        payload["signal_count"] = self.signal_count
        return payload


@dataclass(frozen=True)
class GalleryImage:
    filename: str
    image_path: str
    roads: str
    latitude: float
    longitude: float
    signal_count: int

    def to_dict(self) -> dict[str, str | float | int]:
        return asdict(self)
