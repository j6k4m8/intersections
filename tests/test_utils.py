from intersections.utils import clean_road_name, format_road_label, rank_road_names, slugify


def test_slugify_normalizes_strings():
    assert slugify("Baltimore, Maryland, USA") == "baltimore-maryland-usa"


def test_clean_road_name_strips_common_suffixes():
    assert clean_road_name("North Avenue") == ["North"]
    assert clean_road_name(["West Road", "Main St."]) == ["West", "Main"]


def test_rank_road_names_prefers_frequent_names():
    ranked = rank_road_names(["Main Street", "Main St.", "Falls Road"])
    assert ranked == ["Main", "Falls"]


def test_format_road_label_handles_single_and_multiple_roads():
    assert format_road_label(["Main"]) == "Main & Main"
    assert format_road_label(["Main", "Falls", "North", "South"]) == "Main, Falls, North & South"
