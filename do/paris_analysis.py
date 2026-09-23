"""
Paris: jobs vs. employed residents near the centre, 1968-2022.

Compares how concentrated jobs are around the centre against how
concentrated employed residents are, using INSEE's historical census
series (ages 25-54 - the only group comparable across all 9 censuses
since 1968). https://www.insee.fr/fr/statistiques/1893185

pop-act2554-empl-csp-cd-trav-6822.xlsx = jobs, by workplace commune
pop-act2554-empl-sexe-cd-6822.xlsx     = employed residents, by home commune
Coordinates: input/coordinates.csv, from get_coordinates.py.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

JOBS_FILE = "input/pop-act2554-empl-csp-cd-trav-6822.xlsx"
RESIDENTS_FILE = "input/pop-act2554-empl-sexe-cd-6822.xlsx"

CENSUS_YEARS = [1968, 1975, 1982, 1990, 1999, 2006, 2011, 2016, 2022]
RADIUS_TO_PLOT_KM = 5
ALL_RADII_KM = [5, 10]  # both saved to the CSV, only one plotted
PARIS_DEPARTMENTS = ["75", "77", "78", "91", "92", "93", "94", "95"]
CENTRE_LAT, CENTRE_LON = 48.8583, 2.3470  # Chatelet


def haversine_km(lat1, lon1, lat2, lon2):
    # Calculate distance between two points in km
    R = 6371
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlmb = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def load_jobs(year):
    # Load jobs for one census year
    df = pd.read_excel(JOBS_FILE, sheet_name=f"COM_{year}", skiprows=14)
    df["DLT"] = df["DLT"].astype(str).str.zfill(2)
    df["CLT"] = df["CLT"].astype(str).str.zfill(3)
    df = df[df["DLT"].isin(PARIS_DEPARTMENTS)].copy()

    # Add the 6 job categories to get total jobs
    job_category_columns = [c for c in df.columns if str(c).startswith("csx_rec")]
    df["jobs"] = df[job_category_columns].sum(axis=1, skipna=False)

    # Create the commune ID used to merge the datasets
    df["CODGEO"] = df["DLT"] + df["CLT"]
    return df[["CODGEO", "jobs"]].dropna()


def load_residents(year):
    # Load employed residents for one census year
    df = pd.read_excel(RESIDENTS_FILE, sheet_name=f"COM_{year}", skiprows=15)
    df["DR"] = df["DR"].astype(str).str.zfill(2)
    df["CR"] = df["CR"].astype(str).str.zfill(3)
    df = df[df["DR"].isin(PARIS_DEPARTMENTS)].copy()

    # Select the columns for employed residents
    employed_columns = [c for c in df.columns if "taxtypac_rec1" in str(c)]
    df["residents"] = df[employed_columns].sum(axis=1, skipna=False)

    df["CODGEO"] = df["DR"] + df["CR"]
    return df[["CODGEO", "residents"]].dropna()


coordinates = pd.read_csv(
    "input/coordinates.csv",
    dtype={"CODGEO": str}
)[["CODGEO", "lon", "lat"]].drop_duplicates("CODGEO")

os.makedirs("output", exist_ok=True)

results = []
data_by_year = {}

for year in CENSUS_YEARS:
    # Combine jobs, residents and coordinates
    df = (
        load_jobs(year)
        .merge(load_residents(year), on="CODGEO")
        .merge(coordinates, on="CODGEO", how="left")
    )

    # Calculate distance from each commune to Chatelet
    df = df.dropna(subset=["lat", "lon"])
    df["distance_km"] = haversine_km(
        CENTRE_LAT, CENTRE_LON, df["lat"], df["lon"]
    )
    data_by_year[year] = df

    total_jobs = df["jobs"].sum()
    total_residents = df["residents"].sum()

    for radius in ALL_RADII_KM:
        # Select communes within 5 or 10 km of the centre
        nearby = df[df["distance_km"] <= radius]

        results.append({
            "year": year,
            "radius_km": radius,
            "jobs_pct": round(100 * nearby["jobs"].sum() / total_jobs, 1),
            "residents_pct": round(100 * nearby["residents"].sum() / total_residents, 1),
        })


results_df = pd.DataFrame(results)
results_df.to_csv("output/paris_trend_data.csv", index=False)
print(results_df.to_string(index=False))


# Graph 1: share within 5 km across all census years
subset = results_df[results_df["radius_km"] == RADIUS_TO_PLOT_KM].sort_values("year")

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(subset["year"], subset["jobs_pct"], marker="o", linewidth=2, label="Jobs")
ax.plot(subset["year"], subset["residents_pct"], marker="s", linewidth=2, label="Employed residents")
ax.set_xlabel("Year")
ax.set_ylabel(f"Share within {RADIUS_TO_PLOT_KM} km of centre (%)")
ax.set_title("Paris: jobs vs. residents near the centre, 1968-2022")
ax.legend()
ax.grid(True, alpha=0.3)

plt.savefig("output/paris_trend.png", dpi=150, bbox_inches="tight")
plt.close()


# Graph 2: cumulative share by distance for 2022
latest = data_by_year[2022].sort_values("distance_km").copy()
latest["cumulative_jobs_pct"] = 100 * latest["jobs"].cumsum() / latest["jobs"].sum()
latest["cumulative_residents_pct"] = 100 * latest["residents"].cumsum() / latest["residents"].sum()

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(latest["distance_km"], latest["cumulative_jobs_pct"], label="Jobs")
ax.plot(latest["distance_km"], latest["cumulative_residents_pct"], label="Employed residents")
ax.set_xlabel("Distance from centre (km)")
ax.set_ylabel("Cumulative share (%)")
ax.set_title("Paris 2022: cumulative share of jobs vs. employed residents, by distance from centre")
ax.legend()
ax.grid(True, alpha=0.3)

plt.savefig("output/paris_cumulative_2022.png", dpi=150, bbox_inches="tight")

print("Saved: output/paris_trend.png")
print("Saved: output/paris_cumulative_2022.png")
