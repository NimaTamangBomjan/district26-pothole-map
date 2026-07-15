#!/usr/bin/env python3

import json
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

output_geojson = Path("data/processed/potholes.geojson")

nyc_311_endpoint = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

west = -73.96262
south = 40.71999
east = -73.8877
north = 40.76424

limit = 100

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

def fetch_d26_potholes():
    where = (
        "complaint_type='Street Condition' "
        "AND descriptor='Pothole' "
        "AND borough='QUEENS' "
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

def main():
    records = fetch_d26_potholes()
    features = []
    warnings = []

    for record in records:
        sr_number = clean(record.get("unique_key"))
        lat = clean(record.get("latitude"))
        lon = clean(record.get("longitude"))

        if not sr_number or not lat or not lon:
            warnings.append(f"Skipped record missing sr number or coordinates: {record}")
            continue

        city_status = clean(record.get("status"))
        status = normalize_status(city_status)

        city_created_date = date_only(record.get("created_date"))
        city_closed_date = date_only(record.get("closed_date"))

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

            "office_tracked": False,
            "office_source": "",
            "office_role": "",
            "office_added_date": "",

            "notes_public": "District 26-area pothole 311 request",
            "photo_url": "",
        }

        features.append({
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": "Point",
                "coordinates": [float(lon), float(lat)],
            },
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    output_geojson.parent.mkdir(parents=True, exist_ok=True)
    output_geojson.write_text(json.dumps(geojson, indent=2) + "\n", encoding="utf-8")

    print(f"Created {output_geojson} with {len(features)} D26-area potholes.")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

if __name__ == "__main__":
    main()
