from intersections.overpass import DEFAULT_USER_AGENT, build_traffic_signal_query


def test_build_traffic_signal_query_targets_city_area():
    query = build_traffic_signal_query("Baltimore", 180)

    assert '[out:json][timeout:180];' in query
    assert 'area["name"="Baltimore"]->.searchArea;' in query
    assert 'node["highway"="traffic_signals"](area.searchArea);' in query


def test_default_user_agent_is_specific():
    assert DEFAULT_USER_AGENT.startswith("intersections/")
    assert "github.com/j6k4m8/intersections" in DEFAULT_USER_AGENT
