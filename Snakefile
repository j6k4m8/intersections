from pathlib import Path
import tomllib

from intersections.utils import slugify


CONFIG = tomllib.loads(Path("config/defaults.toml").read_text())
CITY = CONFIG["project"]["city"]
CITY_SLUG = slugify(CITY)
COUNT = int(CONFIG["project"]["count"])

RAW_PAYLOAD = f"data/raw/osm/{CITY_SLUG}/traffic_signals.json"
INTERMEDIATE_JSON = f"data/generated/intersections/{CITY_SLUG}/intersections.json"
FIGURES_DIR = f"results/figures/{CITY_SLUG}"
CITY_MANIFEST = f"results/data/{CITY_SLUG}/manifest.json"
LATEST_MANIFEST = "results/data/latest_manifest.json"


rule all:
    input:
        CITY_MANIFEST,
        LATEST_MANIFEST


rule fetch_traffic_signals:
    output:
        RAW_PAYLOAD
    params:
        city=CITY,
        timeout=CONFIG["overpass"]["timeout_seconds"],
        endpoint=CONFIG["overpass"]["endpoint"],
    shell:
        "python analysis/fetch_traffic_signals/run.py "
        "--city {params.city:q} "
        "--output {output:q} "
        "--timeout {params.timeout} "
        "--endpoint {params.endpoint:q}"


rule cluster_intersections:
    input:
        RAW_PAYLOAD
    output:
        INTERMEDIATE_JSON
    params:
        city=CITY,
        radius=CONFIG["clustering"]["signal_cluster_radius_m"],
        min_cluster_size=CONFIG["clustering"]["min_cluster_size"],
    shell:
        "python analysis/cluster_intersections/run.py "
        "--city {params.city:q} "
        "--input {input:q} "
        "--output {output:q} "
        "--radius-m {params.radius} "
        "--min-cluster-size {params.min_cluster_size}"


rule render_gallery:
    input:
        INTERMEDIATE_JSON
    output:
        directory(FIGURES_DIR),
        CITY_MANIFEST,
        LATEST_MANIFEST,
    params:
        city=CITY,
        image_count=COUNT,
        network_distance=CONFIG["rendering"]["network_distance_m"],
        network_type=CONFIG["rendering"]["network_type"],
        edge_color=CONFIG["rendering"]["edge_color"],
        background_color=CONFIG["rendering"]["background_color"],
        figure_facecolor=CONFIG["rendering"]["figure_facecolor"],
        road_half_width=CONFIG["rendering"]["road_half_width_m"],
        outline_width=CONFIG["rendering"]["outline_width_m"],
    shell:
        "python analysis/render_gallery/run.py "
        "--city {params.city:q} "
        "--input {input:q} "
        "--figures-dir {output[0]:q} "
        "--manifest-output {output[1]:q} "
        "--latest-manifest-output {output[2]:q} "
        "--count {params.image_count} "
        "--network-distance-m {params.network_distance} "
        "--network-type {params.network_type:q} "
        "--edge-color {params.edge_color:q} "
        "--background-color {params.background_color:q} "
        "--figure-facecolor {params.figure_facecolor:q} "
        "--road-half-width-m {params.road_half_width} "
        "--outline-width-m {params.outline_width}"
