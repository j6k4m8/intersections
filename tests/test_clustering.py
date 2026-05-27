from intersections.clustering import cluster_signal_nodes
from intersections.models import Signal


def test_cluster_signal_nodes_groups_nearby_points():
    signals = [
        Signal(osm_id=1, latitude=39.2900, longitude=-76.6100),
        Signal(osm_id=2, latitude=39.2904, longitude=-76.6102),
        Signal(osm_id=3, latitude=39.2902, longitude=-76.6101),
        Signal(osm_id=4, latitude=39.3000, longitude=-76.6200),
    ]

    intersections = cluster_signal_nodes(signals, radius_m=100.0, min_cluster_size=2)

    assert len(intersections) == 1
    assert intersections[0].signal_ids == (1, 2, 3)
    assert round(intersections[0].latitude, 4) == 39.2902
    assert round(intersections[0].longitude, 4) == -76.6101
