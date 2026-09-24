"""
Maps of job density (jobs per km2) in the Paris and Lyon regions, 2022.
Needs the borders from fetch_map_boundaries.py.
"""

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

os.makedirs("output", exist_ok=True)

# jobs per commune in 2022 (same file and same steps as in paris_analysis.py)
jobs = pd.read_excel("input/pop-act2554-empl-csp-cd-trav-6822.xlsx", sheet_name="COM_2022", skiprows=14)
jobs["CODGEO"] = jobs["DLT"].astype(str).str.zfill(2) + jobs["CLT"].astype(str).str.zfill(3)
jobs["jobs"] = jobs[[c for c in jobs.columns if str(c).startswith("csx_rec")]].sum(axis=1, skipna=False)
jobs = jobs[["CODGEO", "jobs"]].dropna()


def draw_map(city, borders_file):
    gdf = gpd.read_file(borders_file)
    gdf["CODGEO"] = gdf["CODGEO"].astype(str)

    # Lyon is 9 districts on the map but only one row (69123) in the jobs file,
    # so we join the 9 district shapes into one before matching
    if city == "lyon":
        is_lyon = gdf["CODGEO"].between("69381", "69389")
        lyon_whole = gdf[is_lyon].dissolve()
        lyon_whole["CODGEO"] = "69123"
        lyon_whole["SUPERFICIE"] = gdf.loc[is_lyon, "SUPERFICIE"].sum()
        gdf = pd.concat([gdf[~is_lyon], lyon_whole], ignore_index=True)

    gdf = gdf.merge(jobs, on="CODGEO", how="left")
    gdf["jobs_per_km2"] = gdf["jobs"] / (gdf["SUPERFICIE"] / 100)  # SUPERFICIE is in hectares

    print(city, ":", gdf["jobs_per_km2"].isna().sum(), "communes without job data (grey)")

    # log scale, otherwise the centre is so much higher that everything else looks the same
    ax = gdf.plot(column="jobs_per_km2", cmap="OrRd", legend=True, figsize=(8, 8),
                  norm=LogNorm(vmin=1, vmax=gdf["jobs_per_km2"].max()),
                  legend_kwds={"label": "Jobs per km2 (log scale)"},
                  missing_kwds={"color": "lightgrey"})
    ax.set_title(f"Job density: {city.capitalize()} region (2022)")
    ax.set_axis_off()
    plt.savefig(f"output/{city}_job_density_map.png", dpi=150, bbox_inches="tight")
    plt.close()


draw_map("paris", "input/paris_boundaries.geojson")
draw_map("lyon", "input/lyon_boundaries.geojson")
print("maps saved in output/")