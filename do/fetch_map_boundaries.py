# Downloads commune borders (shapes) from IGN GEOFLA so we can draw maps.
# coordinates.csv only has one point per commune, not the shape.
# Source: https://geoservices.ign.fr/geofla (2010 version, old but still free)
# The file is big, takes about a minute.

import os
import shutil
import requests
import py7zr
import geopandas as gpd

url = ("https://data.geopf.fr/telechargement/download/GEOFLA/"
       "GEOFLA_1-1_COMMUNES_SHP_LAMB93_FXX_2010-01-01/"
       "GEOFLA_1-1_COMMUNES_SHP_LAMB93_FXX_2010-01-01.7z")

print("downloading...")
r = requests.get(url)
r.raise_for_status()
with open("commune.7z", "wb") as f:
    f.write(r.content)

# it's a .7z file so we need py7zr to unpack it
with py7zr.SevenZipFile("commune.7z", mode="r") as z:
    z.extractall("geofla_temp")

# COMMUNE.SHP is hidden a few folders down, search for it
shp = None
for root, dirs, files in os.walk("geofla_temp"):
    if "COMMUNE.SHP" in files:
        shp = os.path.join(root, "COMMUNE.SHP")
if shp is None:
    raise FileNotFoundError("could not find COMMUNE.SHP in geofla_temp/")

communes = gpd.read_file(shp)
communes["CODGEO"] = communes["INSEE_COM"]

paris = communes[communes["CODE_DEPT"].isin(["75", "77", "78", "91", "92", "93", "94", "95"])]
lyon = communes[communes["CODE_DEPT"] == "69"]

paris.to_file("input/paris_boundaries.geojson", driver="GeoJSON")
lyon.to_file("input/lyon_boundaries.geojson", driver="GeoJSON")
print("saved", len(paris), "Paris communes and", len(lyon), "Lyon communes")

# remove the temporary files
shutil.rmtree("geofla_temp", ignore_errors=True)
os.remove("commune.7z")