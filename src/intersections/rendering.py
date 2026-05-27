from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
from shapely import BufferCapStyle, BufferJoinStyle
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from intersections.io import write_json
from intersections.models import GalleryImage, Intersection
from intersections.utils import format_road_label, rank_road_names, slugify


def _graph_road_names(graph: Any) -> list[str]:
    edge_names = [data.get("name") for _, _, data in graph.edges(data=True)]
    return rank_road_names(edge_names)


def build_outline_geometry(
    centerlines: list[BaseGeometry],
    road_half_width_m: float,
    outline_width_m: float,
) -> BaseGeometry:
    merged_centerlines = unary_union([geometry for geometry in centerlines if geometry is not None and not geometry.is_empty])
    if merged_centerlines.is_empty:
        return merged_centerlines

    outer = merged_centerlines.buffer(
        road_half_width_m,
        cap_style=BufferCapStyle.round,
        join_style=BufferJoinStyle.round,
    )
    inner_half_width = max(road_half_width_m - outline_width_m, 0.0)
    if inner_half_width <= 0:
        return outer

    inner = merged_centerlines.buffer(
        inner_half_width,
        cap_style=BufferCapStyle.round,
        join_style=BufferJoinStyle.round,
    )
    return outer.difference(inner)


def render_outline_image(
    graph: Any,
    image_path: Path,
    edge_color: str,
    figure_facecolor: str,
    road_half_width_m: float,
    outline_width_m: float,
) -> bool:
    projected_graph = ox.project_graph(graph)
    edges = ox.convert.graph_to_gdfs(projected_graph, nodes=False, fill_edge_geometry=True)
    outline_geometry = build_outline_geometry(
        centerlines=list(edges.geometry),
        road_half_width_m=road_half_width_m,
        outline_width_m=outline_width_m,
    )
    if outline_geometry.is_empty:
        return False

    fig, ax = plt.subplots(figsize=(3, 3), facecolor=figure_facecolor)
    ax.set_facecolor(figure_facecolor)

    gpd.GeoSeries([outline_geometry], crs=edges.crs).plot(
        ax=ax,
        color=edge_color,
        edgecolor="none",
    )

    minx, miny, maxx, maxy = outline_geometry.bounds
    span = max(maxx - minx, maxy - miny)
    if span == 0:
        span = 1.0
    padding = span * 0.08
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2
    half_span = span / 2 + padding
    ax.set_xlim(cx - half_span, cx + half_span)
    ax.set_ylim(cy - half_span, cy + half_span)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.savefig(
        image_path,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0,
        transparent=True,
        facecolor=figure_facecolor,
    )
    plt.close(fig)
    return True


def render_gallery(
    city: str,
    intersections: list[Intersection],
    figures_dir: Path,
    manifest_output: Path,
    latest_manifest_output: Path | None,
    count: int,
    network_distance_m: float,
    network_type: str,
    edge_color: str,
    background_color: str,
    figure_facecolor: str,
    road_half_width_m: float,
    outline_width_m: float,
) -> dict[str, object]:
    figures_dir.mkdir(parents=True, exist_ok=True)

    gallery_images: list[GalleryImage] = []
    for intersection in intersections:
        if len(gallery_images) >= count:
            break

        center = (intersection.latitude, intersection.longitude)
        try:
            graph = ox.graph_from_point(
                center,
                dist=network_distance_m,
                network_type=network_type,
                simplify=True,
                truncate_by_edge=True,
            )
        except Exception:
            continue

        roads = _graph_road_names(graph)
        road_label = format_road_label(roads)
        primary_name = roads[0] if roads else f"intersection-{intersection.cluster_id + 1}"
        filename = f"{len(gallery_images) + 1:03d}_{slugify(primary_name)}.png"
        image_path = figures_dir / filename

        if not render_outline_image(
            graph=graph,
            image_path=image_path,
            edge_color=edge_color,
            figure_facecolor=figure_facecolor,
            road_half_width_m=road_half_width_m,
            outline_width_m=outline_width_m,
        ):
            continue

        gallery_images.append(
            GalleryImage(
                filename=filename,
                image_path=image_path.as_posix(),
                roads=road_label,
                latitude=intersection.latitude,
                longitude=intersection.longitude,
                signal_count=intersection.signal_count,
            )
        )

    payload: dict[str, object] = {
        "city": city,
        "generated_at": datetime.now(UTC).isoformat(),
        "background_color": background_color,
        "images": [item.to_dict() for item in gallery_images],
    }
    write_json(manifest_output, payload)
    if latest_manifest_output is not None:
        write_json(latest_manifest_output, payload)
    return payload
