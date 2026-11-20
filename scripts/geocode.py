"""Fill in missing lat/lng in comps.csv (Census geocoder first, Nominatim fallback).
Run by .github/workflows/geocode.yml whenever comps.csv changes. Standard library only.
Rows it can't place are listed in geocode_failures.csv so they can be fixed by hand."""
import csv, json, re, time, urllib.parse, urllib.request

CSV_PATH, FAIL_PATH = "comps.csv", "geocode_failures.csv"
UA = "CompTrack/1.0 (github.com/kevin1992-ui/salecomps)"

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def census(addr):
    q = urllib.parse.urlencode({"address": addr, "benchmark": "Public_AR_Current", "format": "json"})
    m = get_json("https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?" + q)["result"]["addressMatches"]
    return (m[0]["coordinates"]["y"], m[0]["coordinates"]["x"]) if m else None

def nominatim(addr):
    q = urllib.parse.urlencode({"q": addr, "format": "json", "limit": 1, "countrycodes": "us"})
    time.sleep(1.1)  # Nominatim usage policy: max 1 request/second
    d = get_json("https://nominatim.openstreetmap.org/search?" + q)
    return (float(d[0]["lat"]), float(d[0]["lon"])) if d else None

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)

filled, failures = 0, []
for r in rows:
    if r.get("lat", "").strip() and r.get("lng", "").strip():
        continue
    addr = r.get("address", "").strip()
    # A street address needs a house number; city-only addresses geocode to the city center
    if not re.search(r"\d", addr.split(",")[0]):
        failures.append({"id": r["id"], "name": r["name"], "address": addr, "reason": "needs a street address"})
        continue
    hit, source = None, ""
    for fn in (census, nominatim):
        try:
            hit = fn(addr)
        except Exception as e:
            print(f"  {fn.__name__} error for {addr}: {e}")
        if hit:
            source = fn.__name__
            break
    if hit:
        r["lat"], r["lng"] = f"{hit[0]:.6f}", f"{hit[1]:.6f}"
        filled += 1
        print(f"OK   [{source}] {r['id']} {r['name']} -> {r['lat']},{r['lng']}")
    else:
        failures.append({"id": r["id"], "name": r["name"], "address": addr, "reason": "no geocoder match"})
        print(f"FAIL {r['id']} {r['name']} ({addr})")

if filled:
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)

with open(FAIL_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "name", "address", "reason"], lineterminator="\n")
    w.writeheader(); w.writerows(failures)

print(f"\nFilled {filled} coordinate(s); {len(failures)} need manual coordinates (see {FAIL_PATH}).")
