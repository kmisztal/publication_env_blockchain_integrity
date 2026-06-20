"""Generate static HTML maps for selected OpenAQ monitoring locations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from experiments.common.paths import MAP_OUTPUT_DIR, ensure_experiment_dirs


LEAFLET_CSS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
LEAFLET_JS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"


def generate_selection_map(*, metadata_file: Path, output_file: Path | None = None) -> Path:
    ensure_experiment_dirs()
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    dataset_id = metadata.get("dataset_id", "openaq_selection")
    output_file = output_file or (MAP_OUTPUT_DIR / f"{dataset_id}_sensor_map.html")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    cities = _cities_from_metadata(metadata)
    html = _render_html(dataset_id=dataset_id, cities=cities)
    output_file.write_text(html, encoding="utf-8")
    return output_file


def _cities_from_metadata(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    full_locations = {
        str(location.get("id")): location
        for location in metadata.get("locations", [])
    }
    reports = metadata.get("city_selection_reports") or []
    if not reports:
        locations = [_location_payload(location, {}, []) for location in metadata.get("locations", [])]
        return [{"name": "OpenAQ selection", "center": _center(locations), "locations": locations}]

    cities = []
    for report in reports:
        city = report.get("city") or {}
        locations = []
        for selected in report.get("selected_locations", []):
            full = full_locations.get(str(selected.get("location_id")), {})
            locations.append(_location_payload(full, selected, selected.get("selected_sensor_ids", [])))
        cities.append(
            {
                "name": city.get("display_name") or city.get("name") or "City",
                "center": {
                    "latitude": city.get("latitude"),
                    "longitude": city.get("longitude"),
                },
                "locations": locations,
            }
        )
    return cities


def _location_payload(
    location: dict[str, Any],
    selected: dict[str, Any],
    sensor_ids: list[Any],
) -> dict[str, Any]:
    coordinates = location.get("coordinates") or {}
    return {
        "id": location.get("id") or selected.get("location_id"),
        "name": location.get("name") or selected.get("location_name"),
        "latitude": coordinates.get("latitude"),
        "longitude": coordinates.get("longitude"),
        "measurement_score": selected.get("measurement_score"),
        "distance_from_center_m": selected.get("distance_from_center_m"),
        "bearing_from_center_degrees": selected.get("bearing_from_center_degrees"),
        "selected_sensor_ids": sensor_ids,
    }


def _center(locations: list[dict[str, Any]]) -> dict[str, float | None]:
    points = [
        (item.get("latitude"), item.get("longitude"))
        for item in locations
        if item.get("latitude") is not None and item.get("longitude") is not None
    ]
    if not points:
        return {"latitude": None, "longitude": None}
    return {
        "latitude": sum(float(point[0]) for point in points) / len(points),
        "longitude": sum(float(point[1]) for point in points) / len(points),
    }


def _render_html(*, dataset_id: str, cities: list[dict[str, Any]]) -> str:
    data_json = json.dumps(cities, sort_keys=True, ensure_ascii=True)
    title = f"OpenAQ selected monitoring locations: {dataset_id}"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="{LEAFLET_CSS}">
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; }}
    header {{ padding: 12px 16px; border-bottom: 1px solid #ddd; }}
    h1 {{ font-size: 18px; margin: 0 0 4px; }}
    p {{ margin: 0; color: #555; font-size: 13px; }}
    #map {{ height: calc(100vh - 64px); min-height: 560px; }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p>Generated from local OpenAQ metadata. This map is an inspection artifact, not an experiment result.</p>
  </header>
  <div id="map"></div>
  <script src="{LEAFLET_JS}"></script>
  <script>
    const cities = {data_json};
    const colors = ["#2563eb", "#dc2626", "#059669", "#7c3aed", "#ea580c"];
    const map = L.map("map");
    const bounds = [];
    L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    cities.forEach((city, cityIndex) => {{
      const color = colors[cityIndex % colors.length];
      const points = [];
      if (city.center.latitude !== null && city.center.longitude !== null) {{
        L.circleMarker([city.center.latitude, city.center.longitude], {{
          radius: 7,
          color,
          fillColor: "#fff",
          fillOpacity: 1,
          weight: 3
        }}).bindPopup(`<strong>${{city.name}} center</strong>`).addTo(map);
        bounds.push([city.center.latitude, city.center.longitude]);
      }}
      city.locations.forEach((location) => {{
        if (location.latitude === null || location.longitude === null) return;
        points.push([location.latitude, location.longitude]);
        bounds.push([location.latitude, location.longitude]);
        const distance = location.distance_from_center_m === null ? "n/a" : Math.round(location.distance_from_center_m);
        const popup = `
          <strong>${{city.name}}: ${{location.name || "location"}}</strong><br>
          location_id: ${{location.id}}<br>
          measurement_score: ${{location.measurement_score ?? "n/a"}}<br>
          distance_from_center_m: ${{distance}}<br>
          selected_sensor_ids: ${{(location.selected_sensor_ids || []).join(", ")}}
        `;
        L.circleMarker([location.latitude, location.longitude], {{
          radius: 8,
          color,
          fillColor: color,
          fillOpacity: 0.8,
          weight: 2
        }}).bindPopup(popup).addTo(map);
      }});
      if (points.length >= 2) {{
        L.polyline(points.concat(points.length >= 3 ? [points[0]] : []), {{
          color,
          weight: 2,
          opacity: 0.75
        }}).addTo(map);
      }}
    }});
    if (bounds.length > 0) {{
      map.fitBounds(bounds, {{ padding: [32, 32] }});
    }} else {{
      map.setView([52.0, 10.0], 4);
    }}
  </script>
</body>
</html>
"""
