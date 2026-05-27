from __future__ import annotations

import argparse
from pathlib import Path

from intersections.clustering import cluster_signal_nodes, signals_from_overpass_payload
from intersections.io import read_json, write_json
from intersections.overpass import fetch_traffic_signals
from intersections.rendering import render_gallery
from intersections.utils import slugify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate stylized maps of complex intersections.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch", help="Fetch raw traffic signal data from Overpass.")
    fetch_parser.add_argument("--city", required=True)
    fetch_parser.add_argument("--output", type=Path, required=True)
    fetch_parser.add_argument("--timeout", type=int, default=180)
    fetch_parser.add_argument("--endpoint", default="https://overpass-api.de/api/interpreter")

    cluster_parser = subparsers.add_parser("cluster", help="Cluster nearby traffic signals into intersections.")
    cluster_parser.add_argument("--city", required=True)
    cluster_parser.add_argument("--input", type=Path, required=True)
    cluster_parser.add_argument("--output", type=Path, required=True)
    cluster_parser.add_argument("--radius-m", type=float, default=100.0)
    cluster_parser.add_argument("--min-cluster-size", type=int, default=2)

    render_parser = subparsers.add_parser("render", help="Render gallery images and manifests.")
    render_parser.add_argument("--city", required=True)
    render_parser.add_argument("--input", type=Path, required=True)
    render_parser.add_argument("--figures-dir", type=Path, required=True)
    render_parser.add_argument("--manifest-output", type=Path, required=True)
    render_parser.add_argument("--latest-manifest-output", type=Path)
    render_parser.add_argument("--count", type=int, default=24)
    render_parser.add_argument("--network-distance-m", type=float, default=100.0)
    render_parser.add_argument("--network-type", default="drive")
    render_parser.add_argument("--edge-color", default="#b7fff8")
    render_parser.add_argument("--background-color", default="#0f1618")
    render_parser.add_argument("--figure-facecolor", default="#0d1b1e00")
    render_parser.add_argument("--road-half-width-m", type=float, default=7.5)
    render_parser.add_argument("--outline-width-m", type=float, default=1.75)

    run_parser = subparsers.add_parser("run", help="Run the full pipeline using repository-standard paths.")
    run_parser.add_argument("--city", default="Baltimore, Maryland, USA")
    run_parser.add_argument("--count", type=int, default=24)
    run_parser.add_argument("--timeout", type=int, default=180)
    run_parser.add_argument("--radius-m", type=float, default=100.0)
    run_parser.add_argument("--min-cluster-size", type=int, default=2)
    run_parser.add_argument("--network-distance-m", type=float, default=100.0)
    run_parser.add_argument("--network-type", default="drive")

    return parser


def _run_fetch(args: argparse.Namespace) -> int:
    payload = fetch_traffic_signals(args.city, timeout_seconds=args.timeout, endpoint=args.endpoint)
    write_json(args.output, payload)
    return 0


def _run_cluster(args: argparse.Namespace) -> int:
    payload = read_json(args.input)
    signals = signals_from_overpass_payload(payload)
    intersections = cluster_signal_nodes(
        signals,
        radius_m=args.radius_m,
        min_cluster_size=args.min_cluster_size,
    )
    output_payload = {
        "city": args.city,
        "source_path": args.input.as_posix(),
        "signal_count": len(signals),
        "cluster_radius_m": args.radius_m,
        "min_cluster_size": args.min_cluster_size,
        "intersections": [intersection.to_dict() for intersection in intersections],
    }
    write_json(args.output, output_payload)
    return 0


def _run_render(args: argparse.Namespace) -> int:
    payload = read_json(args.input)
    intersections = [
        _intersection_from_dict(item)
        for item in payload.get("intersections", [])
        if isinstance(item, dict)
    ]
    render_gallery(
        city=args.city,
        intersections=intersections,
        figures_dir=args.figures_dir,
        manifest_output=args.manifest_output,
        latest_manifest_output=args.latest_manifest_output,
        count=args.count,
        network_distance_m=args.network_distance_m,
        network_type=args.network_type,
        edge_color=args.edge_color,
        background_color=args.background_color,
        figure_facecolor=args.figure_facecolor,
        road_half_width_m=args.road_half_width_m,
        outline_width_m=args.outline_width_m,
    )
    return 0


def _run_pipeline(args: argparse.Namespace) -> int:
    city_slug = slugify(args.city)
    raw_path = Path(f"data/raw/osm/{city_slug}/traffic_signals.json")
    clustered_path = Path(f"data/generated/intersections/{city_slug}/intersections.json")
    figures_dir = Path(f"results/figures/{city_slug}")
    manifest_path = Path(f"results/data/{city_slug}/manifest.json")
    latest_manifest = Path("results/data/latest_manifest.json")

    fetch_args = argparse.Namespace(
        city=args.city,
        output=raw_path,
        timeout=args.timeout,
        endpoint="https://overpass-api.de/api/interpreter",
    )
    cluster_args = argparse.Namespace(
        city=args.city,
        input=raw_path,
        output=clustered_path,
        radius_m=args.radius_m,
        min_cluster_size=args.min_cluster_size,
    )
    render_args = argparse.Namespace(
        city=args.city,
        input=clustered_path,
        figures_dir=figures_dir,
        manifest_output=manifest_path,
        latest_manifest_output=latest_manifest,
        count=args.count,
        network_distance_m=args.network_distance_m,
        network_type=args.network_type,
        edge_color="#b7fff8",
        background_color="#0f1618",
        figure_facecolor="#0d1b1e00",
        road_half_width_m=7.5,
        outline_width_m=1.75,
    )

    _run_fetch(fetch_args)
    _run_cluster(cluster_args)
    _run_render(render_args)
    return 0


def _intersection_from_dict(payload: dict[str, object]):
    from intersections.models import Intersection

    signal_ids = payload.get("signal_ids", [])
    return Intersection(
        cluster_id=int(payload["cluster_id"]),
        latitude=float(payload["latitude"]),
        longitude=float(payload["longitude"]),
        signal_ids=tuple(int(item) for item in signal_ids),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "fetch":
            return _run_fetch(args)
        if args.command == "cluster":
            return _run_cluster(args)
        if args.command == "render":
            return _run_render(args)
        if args.command == "run":
            return _run_pipeline(args)
    except Exception as exc:
        parser.exit(1, f"error: {exc}\n")

    parser.error(f"Unknown command: {args.command}")
    return 2
