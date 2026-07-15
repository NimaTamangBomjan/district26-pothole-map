#!/usr/bin/env python3

import csv
import json
from datetime import date, datetime
from pathlib import Path

INPUT_CSV = Path("data/prepared/potholes.csv")
OUTPUT_GEOJSON = Path("data/processed/potholes.geojson")

STATUS_MAP = {
    "open": "Open",
    "reported": "Open",
    "in progress": "In Progress",
    "in-progress": "In Progress",
    "pending": "In Progress",
    "assigned": "In Progress",
    "closed": "Closed",
    "completed": "Closed",
    "repaired": "Closed",
}

PRIORITY_MAP = {
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}

def clean(value):
    return (value or "").strip()

def normalize_status(value):
    raw = clean(value).lower()
    return STATUS_MAP.get(raw, clean(value) or "Open")

def normalize_priority(value):
    raw = clean(value).lower()
    return PRIORITY_MAP.get(raw, clean(value) or "Medium")

def parse_date(value):
    value = clean(value)
    if not value:
        return None

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None

def days_between(start_value, end_value):
    start = parse_date(start_value)
    end = parse_date(end_value) or date.today()

    if not start:
        return ""

    return max((end - start).days, 0)

def require_float(row, field):
    value = clean(row.get(field))
    if not value:
        raise ValueError(f"Missing {field} for row id={row.get('id') or row.get('sr_number')}")
    return float(value)

def main():
    if not INPUT_CSV.exists():
        raise SystemExit(f"Missing input file: {INPUT_CSV}")

    features = []

    with INPUT_CSV.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for index, row in enumerate(reader, start=1):
            row_id = clean(row.get("id")) or f"PH-{index:03d}"
            lat = require_float(row, "latitude")
            lon = require_float(row, "longitude")

            status = normalize_status(row.get("status") or row.get("city_status"))
            priority = normalize_priority(row.get("priority"))

            office_reported_date = clean(row.get("office_reported_date"))
            city_closed_date = clean(row.get("city_closed_date"))
            closed_date = city_closed_date if status == "Closed" else ""

            properties = {
                "id": row_id,
                "status": status,
                "priority": priority,
                "address": clean(row.get("address")),
                "sr_number": clean(row.get("sr_number")),
                "reported_date": office_reported_date,
                "office_reported_date": office_reported_date,
                "city_status": clean(row.get("city_status")) or status,
                "closed_date": closed_date,
                "city_closed_date": city_closed_date,
                "source": clean(row.get("source")) or "Office tracker",
                "notes_public": clean(row.get("notes_public")),
                "photo_url": clean(row.get("photo_url")),
                "days_open": days_between(office_reported_date, closed_date),
            }

            features.append({
                "type": "Feature",
                "properties": properties,
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    OUTPUT_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_GEOJSON.write_text(json.dumps(geojson, indent=2) + "\n", encoding="utf-8")

    print(f"Created {OUTPUT_GEOJSON} with {len(features)} potholes.")

if __name__ == "__main__":
    main()
