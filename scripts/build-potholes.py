#!/usr/bin/env python3

import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

input_csv = Path("data/prepared/pothole-sr-numbers.csv")
output_geojson = Path("data/processed/potholes.geojson")

nyc_311_endpoint = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
office_source = "Julie Won Office"

fields = [
    "unique_key",
    "created_date",
    "closed_date",
    "status",
    "agency",
    "agency_name",
    "complaint_type",
    "descriptor",
    "incident_address",
    "street_name",
    "cross_street_1",
    "cross_street_2",
    "borough",
    "resolution_description",
    "latitude",
    "longitude",
]

status_map = {
    "open": "Open",
    "assigned": "In Progress",
    "pending": "In Progress",
    "started": "In Progress",
    "in progress": "In Progress",
    "closed": "Closed",
}

def clean(value):
    return (value or "").strip()

def is_true(value):
    return clean(value).lower() in {"true", "yes", "y", "1", "x", "checked"}

def clean_sr_number(value):
    raw = clean(value)
    digits = "".join(ch for ch in raw if ch.isdigit())

    # Some office records may write the number like 31127454484.
    # NYC Open Data usually stores that as 27454484.
    if digits.startswith("311") and len(digits) > 8:
        digits = digits[3:]

    return digits or raw

def parse_date(value):
    value = clean(value)
    if not value:
        return None

    value = value.replace("Z", "")

    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value[:26], fmt).date()
        except ValueError:
            pass

    return None

def date_only(value):
    parsed = parse_date(value)
    return parsed.isoformat() if parsed else ""

def days_between(start_value, end_value=None):
    start = parse_date(start_value)
    end = parse_date(end_value) or date.today()

    if not start:
        return ""

    return max((end - start).days, 0)

def normalize_status(value):
    raw = clean(value).lower()
    return status_map.get(raw, clean(value) or "Open")

def fetch_311_record(sr_number):
    query = {
        "$select": ",".join(fields),
        "$limit": "1",
        "unique_key": sr_number,
    }

    url = nyc_311_endpoint + "?" + urllib.parse.urlencode(query)

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "District26PotholeTracker/1.0",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data[0] if data else None

def make_address(record):
    address = clean(record.get("incident_address"))
    if address:
        return address

    street = clean(record.get("street_name"))
    cross1 = clean(record.get("cross_street_1"))
    cross2 = clean(record.get("cross_street_2"))

    if street and cross1:
        return f"{street} & {cross1}"

    if cross1 and cross2:
        return f"{cross1} & {cross2}"

    if street:
        return street

    return ""

def main():
    if not input_csv.exists():
        raise SystemExit(f"Missing input file: {input_csv}")

    features = []
    warnings = []

    with input_csv.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            include_value = row.get("include_on_map")

            if include_value is not None and not is_true(include_value):
                continue

            sr_number = clean_sr_number(row.get("sr_number"))

            if not sr_number:
                warnings.append("Skipped one blank SR number row.")
                continue

            try:
                record = fetch_311_record(sr_number)
                time.sleep(0.15)
            except Exception as error:
                warnings.append(f"{sr_number}: API error: {error}")
                continue

            if not record:
                warnings.append(f"{sr_number}: not found in NYC 311 API.")
                continue

            lat = clean(record.get("latitude"))
            lon = clean(record.get("longitude"))

            if not lat or not lon:
                warnings.append(f"{sr_number}: found, but missing latitude/longitude.")
                continue

            city_status = clean(record.get("status"))
            status = normalize_status(city_status)

            city_created_date = date_only(record.get("created_date"))
            city_closed_date = date_only(record.get("closed_date"))

            office_added_date = clean(row.get("office_added_date"))
            tracking_start_date = office_added_date or city_created_date

            properties = {
                "id": sr_number,
                "sr_number": sr_number,
                "status": status,
                "city_status": city_status,
                "priority": "Medium",
                "address": make_address(record),
                "borough": clean(record.get("borough")),
                "agency": clean(record.get("agency")),
                "agency_name": clean(record.get("agency_name")),
                "complaint_type": clean(record.get("complaint_type")),
                "descriptor": clean(record.get("descriptor")),
                "resolution_description": clean(record.get("resolution_description")),
                "reported_date": tracking_start_date,
                "office_added_date": office_added_date,
                "office_role": clean(row.get("office_role")) or "Tracked",
                "office_source": office_source,
                "city_created_date": city_created_date,
                "closed_date": city_closed_date if status == "Closed" else "",
                "city_closed_date": city_closed_date,
                "days_open": days_between(tracking_start_date, city_closed_date if status == "Closed" else None),
                "notes_public": clean(row.get("notes_public")),
                "source": office_source,
                "photo_url": clean(row.get("photo_url")),
            }

            features.append({
                "type": "Feature",
                "properties": properties,
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(lon), float(lat)],
                },
            })

    output_geojson.parent.mkdir(parents=True, exist_ok=True)

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    output_geojson.write_text(json.dumps(geojson, indent=2) + "\n", encoding="utf-8")

    print(f"Created {output_geojson} with {len(features)} potholes.")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

if __name__ == "__main__":
    main()
