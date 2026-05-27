from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_USER_AGENT = "intersections/0.2.0 (+https://github.com/j6k4m8/intersections)"


def build_traffic_signal_query(city: str, timeout_seconds: int) -> str:
    return f"""
[out:json][timeout:{timeout_seconds}];
area["name"="{city}"]->.searchArea;
(
  node["highway"="traffic_signals"](area.searchArea);
);
out;
""".strip()


def fetch_traffic_signals(
    city: str,
    timeout_seconds: int = 180,
    endpoint: str = "https://overpass-api.de/api/interpreter",
) -> dict[str, object]:
    query = build_traffic_signal_query(city, timeout_seconds)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept": "application/json",
        "User-Agent": DEFAULT_USER_AGENT,
    }
    request = Request(
        endpoint,
        data=urlencode({"data": query}).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds + 30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 406:
            raise RuntimeError(
                "Overpass returned HTTP 406. The public instances now expect requests to carry "
                "a unique User-Agent or Referer. "
                f"Currently using User-Agent={DEFAULT_USER_AGENT!r} via {endpoint}."
            ) from exc
        raise RuntimeError(f"Overpass returned HTTP {exc.code} for {city!r} via {endpoint}.") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach Overpass endpoint {endpoint} for {city!r}: {exc.reason}.") from exc
