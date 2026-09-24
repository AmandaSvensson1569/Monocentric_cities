"""
Same analysis as paris_analysis.py but for Lyon (see that file for comments).
Note: Lyon is only one row per year in this data (no districts), so we
only see Lyon vs. its suburbs, not differences inside the city.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

JOBS_FILE = "input/pop-act2554-empl-csp-cd-trav-6822.xlsx"
RESIDENTS_FILE = "input/pop-act2554-empl-sexe-cd-6822.xlsx"

YEARS = [1968, 1975, 1982, 1990, 1999, 2006, 2011, 2016, 2022]
CENTRE = (45.7640, 4.8357)  # CENTRE = (45.7640, 4.8357)  # central point in Lyon, about 700 m north of Place Bellecour


def distance_km(lat, lon):
    # Calculate distance from the Lyon centre point in km
    lat0, lon0 = np.radians(CENTRE[0]), np.radians(CENTRE[1])
    lat, lon = np.radians(lat), np.radians(lon)
    a = np.sin((lat - lat0) / 2) ** 2 + np.cos(lat0) * np.cos(lat) * np.sin((lon - lon0) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def load_jobs(year):
    # Load jobs by workplace commune
    df = pd.read_excel(JOBS_FILE, sheet_name=f"COM_{year}", skiprows=14)
    df = df[df["DLT"].astype(str) == "69"].copy()
    df["CODGEO"] = "69" + df["CLT"].astype(str).str.zfill(3)
    cols = [c for c in df.columns if str(c).startswith("csx_rec")]
    df["jobs"] = df[cols].sum(axis=1, skipna=False)
    return df[["CODGEO", "jobs"]].dropna()


def load_residents(year):
    # Load employed residents by home commune
    df = pd.read_excel(RESIDENTS_FILE, sheet_name=f"COM_{year}", skiprows=15)
    df = df[df["DR"].astype(str) == "69"].copy()
    df["CODGEO"] = "69" + df["CR"].astype(str).str.zfill(3)
    cols = [c for c in df.columns if "taxtypac_rec1" in str(c)]  # employed only
    df["residents"] = df[cols].sum(axis=1, skipna=False)
    return df[["CODGEO", "residents"]].dropna()


# Load commune coordinates
coords = pd.read_csv("input/coordinates.csv", dtype={"CODGEO": str})
os.makedirs("output", exist_ok=True)

rows = []

for year in YEARS:
    # Combine jobs, residents and coordinates
    df = load_jobs(year).merge(load_residents(year), on="CODGEO").merge(coords, on="CODGEO")
    df["dist"] = distance_km(df["lat"], df["lon"])

    # Calculate the share of jobs and residents within 5 and 10 km
    for r in [5, 10]:
        near = df[df["dist"] <= r]
        rows.append([year, r,
                     round(100 * near["jobs"].sum() / df["jobs"].sum(), 1),
                     round(100 * near["residents"].sum() / df["residents"].sum(), 1)])

    if year == 2022:
        df_2022 = df.sort_values("dist")

res = pd.DataFrame(rows, columns=["year", "radius_km", "jobs_pct", "residents_pct"])
res.to_csv("output/lyon_trend_data.csv", index=False)
print(res.to_string(index=False))

# Trend graph for the 5 km radius
r5 = res[res["radius_km"] == 5]
plt.figure(figsize=(7, 5))
plt.plot(r5["year"], r5["jobs_pct"], "o-", label="Jobs")
plt.plot(r5["year"], r5["residents_pct"], "s-", label="Employed residents")
plt.xlabel("Year")
plt.ylabel("Share within 5 km of centre (%)")
plt.title("Lyon: jobs vs. residents near the centre, 1968-2022")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("output/lyon_trend.png", dpi=150, bbox_inches="tight")
plt.close()

# Cumulative graph for 2022
plt.figure(figsize=(7, 5))
plt.plot(df_2022["dist"], 100 * df_2022["jobs"].cumsum() / df_2022["jobs"].sum(), label="Jobs")
plt.plot(df_2022["dist"], 100 * df_2022["residents"].cumsum() / df_2022["residents"].sum(), label="Employed residents")
plt.xlabel("Distance from centre (km)")
plt.ylabel("Cumulative share (%)")
plt.title("Lyon 2022: cumulative share of jobs vs. employed residents")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("output/lyon_cumulative_2022.png", dpi=150, bbox_inches="tight")

print("done, graphs saved in output/")