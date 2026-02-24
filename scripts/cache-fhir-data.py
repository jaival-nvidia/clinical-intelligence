"""
Pre-caches FHIR responses to local JSON files as a fallback
in case the FHIR test server is slow or unreachable during the demo.

Run: python scripts/cache-fhir-data.py

Saves to: fallback-data/
"""

import json
import os
import sys

import requests

BASE = "https://r4.smarthealthit.org"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "fallback-data")


def cache(path, filename):
    url = f"{BASE}{path}"
    print(f"  Fetching {url} ...")
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    filepath = os.path.join(OUT_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    count = len(data.get("entry", []))
    print(f"    -> {filepath} ({count} entries)")
    return data


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Caching FHIR data from {BASE}\n")

    patients = cache("/Patient?_count=20", "patients.json")

    if not patients.get("entry"):
        print("No patients found.")
        sys.exit(1)

    pid = patients["entry"][0]["resource"]["id"]
    name = patients["entry"][0]["resource"].get("name", [{}])[0]
    display = f"{name.get('given', ['?'])[0]} {name.get('family', '?')}"
    print(f"\nCaching data for: {display} (ID: {pid})\n")

    cache(f"/Condition?patient={pid}&_count=100", "conditions.json")
    cache(f"/Observation?patient={pid}&_count=100", "observations.json")
    cache(f"/MedicationRequest?patient={pid}&_count=100", "medications.json")
    cache(f"/Encounter?patient={pid}&_count=100", "encounters.json")

    # Cache broader condition searches for cohort analysis
    print("\nCaching cohort data...\n")
    cache("/Condition?code=44054006&_count=200", "diabetic-patients.json")
    cache("/Condition?code=38341003&_count=200", "hypertensive-patients.json")

    info = {"patient_id": pid, "patient_name": display, "base_url": BASE}
    with open(os.path.join(OUT_DIR, "demo-info.json"), "w") as f:
        json.dump(info, f, indent=2)

    print(f"\nDone. Fallback data saved to {OUT_DIR}/")
    print(f"Demo patient: {display} (ID: {pid})")


if __name__ == "__main__":
    main()
