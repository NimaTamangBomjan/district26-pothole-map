#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/raw/dot-office-potholes.csv"
OUTPUT = ROOT / "data/processed/dot-office-potholes.geojson"
REVIEW = ROOT / "data/audits/dot-geocoding-review.csv"
HOLD = ROOT / "data/audits/dot-geocoding-hold.csv"
CACHE = ROOT / "data/audits/dot-geocoding-cache.json"

SETTINGS_URL = "https://portal.311.nyc.gov/get-site-settings/"
GEOCLIENT_URL = "https://api.nyc.gov/geoclient/v2/search.json"
BOUNDARY_URL = "https://data.cityofnewyork.us/resource/mkqi-d8x3.geojson?$limit=100"
USER_AGENT = "District26PotholeTracker/1.0"

MANUAL_HOLD_IDS = {
    "DQ2026201036": "Only a street name was supplied; a cross street or address is required.",
    "DQ2026203048": "No location was supplied.",
    "DQ2026204056": "Underpass level must be checked manually before publishing.",
    "DQ2026208018": "The Queens house number is incomplete or malformed and must be verified.",
    "DQ2026208059": "Playground result would be a place centroid, not the exact pothole location.",
}


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def normalize_dq(value: Any) -> str:
    text = re.sub(r"[^A-Z0-9]", "", clean_text(value).upper())
    return text if re.fullmatch(r"DQ\d+", text) else ""


def normalize_location(value: Any) -> str:
    text = clean_text(value).upper()
    replacements = {
        "BROOKLYN QUEENS EXPRESSWAY": "BROOKLYN-QUEENS EXPRESSWAY",
        "BQE": "BROOKLYN-QUEENS EXPRESSWAY",
        " BLVD": " BOULEVARD",
        " AVE": " AVENUE",
        " RD": " ROAD",
        " DR": " DRIVE",
        " PL": " PLACE",
        " ST": " STREET",
    }
    text = text.replace("/", " ")
    text = re.sub(r"\((?:CROSSWALK|BIKE LANE)\)", "", text)
    for old, new in replacements.items():
        text = re.sub(re.escape(old) + r"\b", new, text)
    text = re.sub(r"\b(\d+)(?:ST|ND|RD|TH)\b", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip(" ,")
    return text


def build_query(row: dict[str, str]) -> tuple[str, str]:
    original = clean_text(row.get("Original Location"))
    map_address = clean_text(row.get("Map Address"))
    note = clean_text(row.get("Address Note")).lower()

    if "segment" in note or "between-block" in note or "street range" in note:
        raw = original.upper().strip()
        raw = re.sub(r"\bIN QUEENS,?\s*", " ", raw)
        raw = re.sub(r"\s+", " ", raw).strip(" ,")

        patterns = [
            r"^(.*?)\s+FROM\s+(.*?)\s+TO\s+(.*?)$",
            r"^(.*?)/?\s*BETWEEN\s+(.*?)\s+AND\s+(.*?)$",
            r"^(.*?)/\s*(.*?)\s+TO\s+(.*?)$",
            r"^(.*?)/\s*(.*?)\s+-\s+(.*?)$",
        ]
        parts = None
        for pattern in patterns:
            match = re.match(pattern, raw, flags=re.I)
            if match:
                parts = match.groups()
                break

        if parts:
            on_street, first_cross, second_cross = [normalize_location(part) for part in parts]
            return f"{on_street} BETWEEN {first_cross} AND {second_cross} QUEENS", "street-segment"

        source = normalize_location(raw)
        return f"{source} QUEENS", "street-segment"

    query = normalize_location(map_address or original)
    query = re.sub(r",?\s+QUEENS,?\s+NY(?:\s+\d{5})?$", "", query)
    query = re.sub(r",?\s+(?:LONG ISLAND CITY|MASPETH|WOODSIDE|SUNNYSIDE|FLUSHING),?\s+NY(?:\s+\d{5})?$", "", query)
    return f"{query} QUEENS", "intersection-or-address"


def request_json(url: str, headers: dict[str, str] | None = None, retries: int = 4) -> Any:
    final_headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if headers:
        final_headers.update(headers)

    error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers=final_headers)
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8", errors="replace"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            error = exc
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Request failed after {retries} attempts: {error}")


def get_geoclient_headers() -> dict[str, str]:
    settings = request_json(SETTINGS_URL)
    api_headers = settings.get("GIS_ADDRESS_SEARCH_API_HEADER") or {}
    key = api_headers.get("ocp-apim-subscription-key") or api_headers.get("Ocp-Apim-Subscription-Key")
    if not key:
        raise RuntimeError("The NYC311 settings did not provide a Geoclient subscription key.")
    return {"Ocp-Apim-Subscription-Key": key}


def find_district_26_geometry(boundary_data: dict[str, Any]) -> dict[str, Any]:
    for feature in boundary_data.get("features", []):
        props = {str(k).lower(): clean_text(v) for k, v in (feature.get("properties") or {}).items()}
        candidates = [
            props.get("coun_dist"),
            props.get("coundist"),
            props.get("council_district"),
            props.get("district"),
        ]
        if any(v and v.lstrip("0") == "26" for v in candidates):
            geometry = feature.get("geometry")
            if geometry:
                return geometry
    raise RuntimeError("Council District 26 was not found in the official boundary response.")


def point_in_ring(lon: float, lat: float, ring: list[list[float]]) -> bool:
    inside = False
    if len(ring) < 3:
        return False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)):
            cross_lon = (xj - xi) * (lat - yi) / ((yj - yi) or 1e-30) + xi
            if lon < cross_lon:
                inside = not inside
        j = i
    return inside


def point_in_polygon(lon: float, lat: float, polygon: list[list[list[float]]]) -> bool:
    if not polygon or not point_in_ring(lon, lat, polygon[0]):
        return False
    return not any(point_in_ring(lon, lat, hole) for hole in polygon[1:])


def point_in_geometry(lon: float, lat: float, geometry: dict[str, Any]) -> bool:
    typ = geometry.get("type")
    coords = geometry.get("coordinates") or []
    if typ == "Polygon":
        return point_in_polygon(lon, lat, coords)
    if typ == "MultiPolygon":
        return any(point_in_polygon(lon, lat, polygon) for polygon in coords)
    return False


def result_type(result: dict[str, Any]) -> str:
    return clean_text(result.get("request")).split(" ", 1)[0].lower()


def parse_candidate(result: dict[str, Any]) -> dict[str, Any] | None:
    response = result.get("response") or {}
    try:
        lat = float(response.get("latitude"))
        lon = float(response.get("longitude"))
    except (TypeError, ValueError):
        return None

    district = clean_text(response.get("cityCouncilDistrict")).lstrip("0")
    borough = clean_text(response.get("firstBoroughName")).upper()
    typ = result_type(result)

    if typ == "intersection":
        official_location = " & ".join(
            part for part in [clean_text(response.get("streetName1")), clean_text(response.get("streetName2"))] if part
        )
        precision = "official-intersection-node"
    elif typ == "blockface":
        official_location = " BETWEEN ".join(
            part for part in [clean_text(response.get("firstStreetNameNormalized")), " AND ".join(
                p for p in [clean_text(response.get("secondStreetNameNormalized")), clean_text(response.get("thirdStreetNameNormalized"))] if p
            )] if part
        )
        precision = "official-blockface-point"
    else:
        house = clean_text(response.get("houseNumber"))
        street = clean_text(response.get("firstStreetNameNormalized") or response.get("giStreetName1"))
        official_location = clean_text(f"{house} {street}")
        precision = "official-address-point" if house else "official-place-point"

    return {
        "latitude": lat,
        "longitude": lon,
        "district": district,
        "borough": borough,
        "result_type": typ,
        "result_status": clean_text(result.get("status")),
        "level": clean_text(result.get("level")),
        "official_location": official_location,
        "location_precision": precision,
        "geosupport_return_code": clean_text(response.get("geosupportReturnCode")),
        "lion_node_id": clean_text(response.get("lionNodeNumber") or response.get("lionNodeId")),
        "segment_id": clean_text(response.get("segmentIdentifier") or response.get("segmentId") or response.get("genericId")),
        "zip_code": clean_text(response.get("zipCode") or response.get("leftSegmentZipCode")),
    }


def score_candidate(candidate: dict[str, Any], desired_type: str) -> tuple[int, int, int]:
    exact = 1 if candidate["result_status"].upper() == "EXACT_MATCH" else 0
    in_queens = 1 if candidate["borough"] in {"QUEENS", "4"} else 0
    type_match = 1
    if desired_type == "street-segment":
        type_match = 1 if candidate["result_type"] == "blockface" else 0
    return exact, type_match, in_queens


def choose_candidate(payload: dict[str, Any], desired_type: str, boundary: dict[str, Any]) -> tuple[dict[str, Any] | None, str, int]:
    parsed: list[dict[str, Any]] = []
    for result in payload.get("results") or []:
        candidate = parse_candidate(result)
        if not candidate:
            continue
        candidate["inside_boundary"] = point_in_geometry(candidate["longitude"], candidate["latitude"], boundary)
        if candidate["district"] == "26" and candidate["inside_boundary"]:
            parsed.append(candidate)

    if not parsed:
        return None, "no-candidate-confirmed-in-district-26", 0

    parsed.sort(key=lambda c: score_candidate(c, desired_type), reverse=True)
    best_score = score_candidate(parsed[0], desired_type)
    best = [c for c in parsed if score_candidate(c, desired_type) == best_score]
    unique_points = {(round(c["longitude"], 7), round(c["latitude"], 7)) for c in best}

    if len(unique_points) != 1:
        return None, "multiple-district-26-candidates", len(parsed)

    selected = best[0]
    if desired_type == "street-segment" and selected["result_type"] != "blockface":
        return None, "segment-did-not-resolve-as-blockface", len(parsed)

    return selected, "accepted", len(parsed)


def geocode(query: str, headers: dict[str, str]) -> dict[str, Any]:
    params = {
        "Input": query,
        "exactMatchForSingleSuccess": "true",
        "returnPossiblesWithExact": "true",
        "returnRejections": "true",
    }
    url = GEOCLIENT_URL + "?" + urllib.parse.urlencode(params)
    return request_json(url, headers=headers)


def load_cache() -> dict[str, Any]:
    if not CACHE.exists():
        return {}
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache: dict[str, Any]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def read_source() -> tuple[list[dict[str, str]], int]:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT}")

    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))

    unique: dict[str, dict[str, str]] = {}
    duplicates = 0
    for row in source_rows:
        dq = normalize_dq(row.get("DQ Number"))
        if not dq:
            continue
        if dq in unique:
            duplicates += 1
            continue
        row = dict(row)
        row["DQ Number"] = dq
        unique[dq] = row
    return list(unique.values()), duplicates


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows, duplicate_count = read_source()
    headers = get_geoclient_headers()
    boundary = find_district_26_geometry(request_json(BOUNDARY_URL))
    cache = load_cache()

    accepted_features: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    counters: Counter[str] = Counter()

    for index, row in enumerate(rows, start=1):
        dq = row["DQ Number"]
        original = clean_text(row.get("Original Location"))
        map_address = clean_text(row.get("Map Address"))
        reported = clean_text(row.get("Date"))
        source_status = clean_text(row.get("Status"))
        note = clean_text(row.get("Address Note"))

        if dq in MANUAL_HOLD_IDS:
            reason = MANUAL_HOLD_IDS[dq]
            hold_rows.append({
                "dq_number": dq,
                "reported": reported,
                "original_location": original,
                "map_address": map_address,
                "reason": reason,
            })
            counters["manual_hold"] += 1
            print(f"[{index}/{len(rows)}] HOLD {dq}: {reason}")
            continue

        query, desired_type = build_query(row)
        cache_key = query.upper()
        try:
            payload = cache.get(cache_key)
            if payload is None:
                payload = geocode(query, headers)
                cache[cache_key] = payload
                save_cache(cache)
                time.sleep(0.12)

            candidate, decision, candidate_count = choose_candidate(payload, desired_type, boundary)
        except Exception as exc:
            candidate = None
            decision = f"api-error: {exc}"
            candidate_count = 0

        base_review = {
            "dq_number": dq,
            "reported": reported,
            "original_location": original,
            "map_address": map_address,
            "query": query,
            "desired_type": desired_type,
            "decision": decision,
            "candidate_count": candidate_count,
            "source_note": note,
        }

        if not candidate:
            hold_rows.append({
                **base_review,
                "reason": decision,
            })
            counters[decision.split(":", 1)[0]] += 1
            print(f"[{index}/{len(rows)}] HOLD {dq}: {decision}")
            continue

        properties = {
            "id": f"dot-{dq}",
            "dq_number": dq,
            "reference_number": dq,
            "reference_type": "DOT Defect ID",
            "source_system": "NYC DOT",
            "source": "District 26 office DOT submissions",
            "location": map_address or candidate["official_location"],
            "official_location": candidate["official_location"],
            "original_location": original,
            "reported": reported or None,
            "status": source_status or "Reported to DOT",
            "office_tracked": True,
            "city_council_district": "26",
            "location_precision": candidate["location_precision"],
            "geocoding_method": "NYC Geoclient / Geosupport",
            "geoclient_result_type": candidate["result_type"],
            "geoclient_result_status": candidate["result_status"],
            "geoclient_level": candidate["level"],
            "geosupport_return_code": candidate["geosupport_return_code"],
            "lion_node_id": candidate["lion_node_id"] or None,
            "segment_id": candidate["segment_id"] or None,
            "zip_code": candidate["zip_code"] or None,
        }

        accepted_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [candidate["longitude"], candidate["latitude"]],
            },
            "properties": properties,
        })

        review_rows.append({
            **base_review,
            "latitude": candidate["latitude"],
            "longitude": candidate["longitude"],
            "official_location": candidate["official_location"],
            "district": candidate["district"],
            "inside_boundary": candidate["inside_boundary"],
            "location_precision": candidate["location_precision"],
            "result_type": candidate["result_type"],
            "result_status": candidate["result_status"],
            "geosupport_return_code": candidate["geosupport_return_code"],
        })
        counters["accepted"] += 1
        print(f"[{index}/{len(rows)}] OK   {dq}: {candidate['official_location']}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    feature_collection = {
        "type": "FeatureCollection",
        "name": "District 26 DOT Office Potholes",
        "metadata": {
            "source": "District 26 office DOT submissions",
            "geocoder": "NYC Geoclient / Geosupport",
            "district_validation": "Official NYC Council District 26 boundary and Geoclient district field",
            "records": len(accepted_features),
            "held_for_review": len(hold_rows),
        },
        "features": accepted_features,
    }
    OUTPUT.write_text(json.dumps(feature_collection, indent=2, ensure_ascii=False), encoding="utf-8")

    review_fields = [
        "dq_number", "reported", "original_location", "map_address", "query",
        "desired_type", "decision", "candidate_count", "latitude", "longitude",
        "official_location", "district", "inside_boundary", "location_precision",
        "result_type", "result_status", "geosupport_return_code", "source_note",
    ]
    hold_fields = [
        "dq_number", "reported", "original_location", "map_address", "query",
        "desired_type", "decision", "candidate_count", "reason", "source_note",
    ]
    write_csv(REVIEW, review_rows, review_fields)
    write_csv(HOLD, hold_rows, hold_fields)

    coordinate_groups: dict[tuple[float, float], list[str]] = defaultdict(list)
    for feature in accepted_features:
        lon, lat = feature["geometry"]["coordinates"]
        coordinate_groups[(round(lon, 7), round(lat, 7))].append(feature["properties"]["dq_number"])
    shared_coordinate_groups = sum(1 for ids in coordinate_groups.values() if len(ids) > 1)

    print()
    print("DOT GEOCODING COMPLETE")
    print("Unique DQ records read:", len(rows))
    print("Duplicate DQ rows removed:", duplicate_count)
    print("Accepted in District 26:", len(accepted_features))
    print("Held for review:", len(hold_rows))
    print("Shared-coordinate groups:", shared_coordinate_groups)
    print("GeoJSON:", OUTPUT)
    print("Accepted audit:", REVIEW)
    print("Held audit:", HOLD)
    if counters:
        print("Decision counts:", dict(counters))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
