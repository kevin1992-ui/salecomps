# CompTrack — multifamily sale comps

Live site: https://kevin1992-ui.github.io/salecomps/

- `comps.csv` — **the comp data.** Add or edit comps here; the map reads it on every page load.
- `index.html` — the map app. No data inside; only change it for features or design.
- `scripts/geocode.py` + `.github/workflows/geocode.yml` — whenever `comps.csv` changes, GitHub fills in any blank `lat`/`lng` from the address (Census, then Nominatim) and commits the result.
- `geocode_failures.csv` — comps the geocoder couldn't place. Fix by giving a full street address, or paste coordinates from Google Maps (right-click the spot → click the numbers to copy).

Columns in `comps.csv`:
`id, name, address, market, submarket, sale_date, class, units, year_built, sf, avg_sf, sale_price, cap_rate, ppu, psf, buyer, seller, notes, lat, lng`
