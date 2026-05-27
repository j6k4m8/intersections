from __future__ import annotations

from collections import defaultdict

import numpy as np
from sklearn.cluster import DBSCAN

from intersections.models import Intersection, Signal


EARTH_RADIUS_M = 6_371_008.8


def signals_from_overpass_payload(payload: dict[str, object]) -> list[Signal]:
    elements = payload.get("elements", [])
    if not isinstance(elements, list):
        return []

    seen: set[int] = set()
    signals: list[Signal] = []
    for element in elements:
        if not isinstance(element, dict):
            continue
        if element.get("type") != "node":
            continue
        if "lat" not in element or "lon" not in element or "id" not in element:
            continue
        osm_id = int(element["id"])
        if osm_id in seen:
            continue
        seen.add(osm_id)
        signals.append(
            Signal(
                osm_id=osm_id,
                latitude=float(element["lat"]),
                longitude=float(element["lon"]),
            )
        )
    return signals


def cluster_signal_nodes(
    signals: list[Signal],
    radius_m: float = 100.0,
    min_cluster_size: int = 2,
) -> list[Intersection]:
    if len(signals) < min_cluster_size:
        return []

    coords = np.radians(np.array([[signal.latitude, signal.longitude] for signal in signals], dtype=float))
    labels = DBSCAN(
        eps=radius_m / EARTH_RADIUS_M,
        min_samples=min_cluster_size,
        metric="haversine",
        algorithm="ball_tree",
    ).fit_predict(coords)

    grouped: defaultdict[int, list[Signal]] = defaultdict(list)
    for label, signal in zip(labels, signals, strict=True):
        if label >= 0:
            grouped[int(label)].append(signal)

    intersections: list[Intersection] = []
    for cluster_index, (_, cluster_signals) in enumerate(
        sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
    ):
        cluster_coords = np.array([[signal.latitude, signal.longitude] for signal in cluster_signals], dtype=float)
        centroid = cluster_coords.mean(axis=0)
        intersections.append(
            Intersection(
                cluster_id=cluster_index,
                latitude=float(centroid[0]),
                longitude=float(centroid[1]),
                signal_ids=tuple(sorted(signal.osm_id for signal in cluster_signals)),
            )
        )
    return intersections
