#!/usr/bin/env python3

import csv
import json
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

output_geojson = Path("data/processed/potholes.geojson")
office_csv = Path("data/prepared/office-potholes.csv")

nyc_311_endpoint = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

west = -73.96262
south = 40.71999
east = -73.8877
north = 40.76424

days_back = 30
limit = 5000
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

false_values = {"", "false", "no", "n", "0", "exclude", "hide"}

def clean(value):
    return (str(value) if value is not None else "").strip()

def clean_sr_number(value):
    raw = clean(value)
    digits = "".join(ch for ch in raw if ch.isdigit())

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

def inside_d26_bounds(record):
    try:
        lat = float(clean(record.get("latitude")))
        lon = float(clean(record.get("longitude")))
    except ValueError:
        return False

    return south <= lat <= north and west <= lon <= east

def is_valid_pothole(record):
    return (
        clean(record.get("complaint_type")).lower() == "street condition"
        and clean(record.get("descriptor")).lower() == "pothole"
        and clean(record.get("borough")).lower() == "queens"
        and inside_d26_bounds(record)
    )

def load_office_records():
    office_records = {}

    if not office_csv.exists():
        return office_records

    with office_csv.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            sr_number = clean_sr_number(row.get("sr_number"))

            if not sr_number:
                continue

            include_on_map = clean(row.get("include_on_map")).lower()

            if include_on_map in false_values:
                continue

            office_records[sr_number] = {
                "office_added_date": date_only(row.get("office_added_date")) or clean(row.get("office_added_date")),
                "office_role": clean(row.get("office_role")) or "Tracked",
                "notes_public": clean(row.get("notes_public")),
            }

    return office_records

def request_json(query):
    url = nyc_311_endpoint + "?" + urllib.parse.urlencode(query)

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "District26PotholeTracker/1.0",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def fetch_d26_potholes():
    start_date = (date.today() - timedelta(days=days_back)).isoformat()

    where = (
        "complaint_type='Street Condition' "
        "AND descriptor='Pothole' "
        "AND borough='QUEENS' "
        f"AND created_date >= '{start_date}T00:00:00' "
        f"AND latitude >= {south} "
        f"AND latitude <= {north} "
        f"AND longitude >= {west} "
        f"AND longitude <= {east} "
        "AND latitude IS NOT NULL "
        "AND longitude IS NOT NULL"
    )

    query = {
        "$select": ",".join(fields),
        "$where": where,
        "$order": "created_date DESC",
        "$limit": str(limit),
    }

    return request_json(query)

def fetch_by_sr_number(sr_number):
    where = f"unique_key='{sr_number}'"

    query = {
        "$select": ",".join(fields),
        "$where": where,
        "$limit": "1",
    }

    records = request_json(query)

    return records[0] if records else None

def build_feature(record, office_entry=None):
    sr_number = clean(record.get("unique_key"))
    lat = clean(record.get("latitude"))
    lon = clean(record.get("longitude"))

    city_status = clean(record.get("status"))
    status = normalize_status(city_status)

    city_created_date = date_only(record.get("created_date"))
    city_closed_date = date_only(record.get("closed_date"))

    office_tracked = office_entry is not None

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

        "reported_date": city_created_date,
        "city_created_date": city_created_date,
        "closed_date": city_closed_date if status == "Closed" else "",
        "city_closed_date": city_closed_date,
        "days_open": days_between(city_created_date, city_closed_date if status == "Closed" else None),

        "data_source": "NYC 311 Open Data",
        "source": "NYC 311 Open Data",

        "office_tracked": office_tracked,
        "office_source": office_source if office_tracked else "",
        "office_role": office_entry.get("office_role", "Tracked") if office_tracked else "",
        "office_added_date": office_entry.get("office_added_date", "") if office_tracked else "",

        "notes_public": office_entry.get("notes_public") if office_tracked and office_entry.get("notes_public") else "District 26-area pothole 311 request",
        "photo_url": "",
    }

    return {
        "type": "Feature",
        "properties": properties,
        "geometry": {
            "type": "Point",
            "coordinates": [float(lon), float(lat)],
        },
    }

def main():
    office_records = load_office_records()
    records = fetch_d26_potholes()

    features = []
    warnings = []
    seen = set()

    for record in records:
        sr_number = clean_sr_number(record.get("unique_key"))
        lat = clean(record.get("latitude"))
        lon = clean(record.get("longitude"))

        if not sr_number or not lat or not lon:
            warnings.append(f"Skipped record missing SR number or coordinates: {record}")
            continue

        office_entry = office_records.get(sr_number)

        features.append(build_feature(record, office_entry))
        seen.add(sr_number)

    for sr_number, office_entry in office_records.items():
        if sr_number in seen:
            continue

        record = fetch_by_sr_number(sr_number)

        if not record:
            warnings.append(f"Office SR {sr_number}: not found in NYC 311 API.")
            continue

        if not is_valid_pothole(record):
            warnings.append(f"Office SR {sr_number}: found, but skipped because it is not a Queens pothole inside the D26 map area.")
            continue

        features.append(build_feature(record, office_entry))
        seen.add(sr_number)

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    output_geojson.parent.mkdir(parents=True, exist_ok=True)
    output_geojson.write_text(json.dumps(geojson, indent=2) + "\n", encoding="utf-8")

    office_count = sum(1 for feature in features if feature["properties"].get("office_tracked") is True)

    print(f"Created {output_geojson} with {len(features)} potholes.")
    print(f"Office-tracked potholes matched: {office_count}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

if __name__ == "__main__":
    main()
