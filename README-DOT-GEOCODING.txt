District 26 DOT Pothole Geocoding

1. Unzip this package into ~/Desktop/district26
2. Run: python3 scripts/build-dot-potholes.py

Outputs:
- data/processed/dot-office-potholes.geojson
- data/audits/dot-geocoding-review.csv
- data/audits/dot-geocoding-hold.csv

The script accepts only records confirmed by both NYC Geoclient/Geosupport and the official Council District 26 boundary.
