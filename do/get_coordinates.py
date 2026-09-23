# Gets coordinates (lon/lat) for all communes in the Paris and Lyon regions
# from API Geo and saves them to input/coordinates.csv.
# We need the coordinates to calculate the distance to the city centre.

import pandas as pd
import requests

departments = ["75", "77", "78", "91", "92", "93", "94", "95", "69"]  # Paris region + Lyon (69)


def get_json(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


rows = []
for dep in departments:
    communes = get_json(f"https://geo.api.gouv.fr/departements/{dep}/communes?fields=code,centre")
    for c in communes:
        if c.get("centre") is None:  # Some communes have no centre point
            continue
        lon, lat = c["centre"]["coordinates"]
        rows.append({"CODGEO": c["code"], "lon": lon, "lat": lat})
    print(dep, "-", len(communes), "communes")

# Paris is one commune in the API (75056), but the INSEE data
# has Paris split into 20 districts (75101-75120), so we need these too
districts = get_json("https://geo.api.gouv.fr/communes?codeParent=75056"
                     "&type=arrondissement-municipal&fields=code,centre")
for d in districts:
    lon, lat = d["centre"]["coordinates"]
    rows.append({"CODGEO": d["code"], "lon": lon, "lat": lat})
print("Paris -", len(districts), "districts")

coords = pd.DataFrame(rows).drop_duplicates("CODGEO")
coords.to_csv("input/coordinates.csv", index=False)
print("saved", len(coords), "rows to input/coordinates.csv")