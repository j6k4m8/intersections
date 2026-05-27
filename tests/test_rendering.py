from shapely.geometry import LineString, Point

from intersections.rendering import build_outline_geometry


def test_build_outline_geometry_creates_hollow_road_shape():
    centerlines = [
        LineString([(0, 0), (10, 0)]),
        LineString([(5, -5), (5, 5)]),
    ]

    outline = build_outline_geometry(centerlines, road_half_width_m=2.0, outline_width_m=0.5)

    assert not outline.is_empty
    assert outline.area > 0
    assert not outline.contains(Point(5, 0))
    assert outline.contains(Point(1, 1.75))
