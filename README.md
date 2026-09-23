# Are Paris and Lyon monocentric cities?

Group project for the course Urban and Real Estate Economics.

We look at whether jobs are more concentrated near the city centre than
employed residents are. If they are, this supports the monocentric city
model. If jobs and residents are spread out in a similar way, the city
may be more polycentric. 
We compare the share of jobs and employed residents within different distances from the centre (Chatelet for Paris, Bellecour for Lyon), for different years from 1968 to 2022.


## Data

| File | Content | Source |
|---|---|---|
| `pop-act2554-empl-csp-cd-trav-6822.xlsx` | Jobs per commune (by workplace), ages 25-54, 1968-2022 | [INSEE](https://www.insee.fr/fr/statistiques/1893185) |
| `pop-act2554-empl-sexe-cd-6822.xlsx` | Employed residents per commune (by home), ages 25-54, 1968-2022 | [INSEE](https://www.insee.fr/fr/statistiques/1893185) |
| `coordinates.csv` | Coordinates of each commune, made by `get_coordinates.py` | [API Geo](https://geo.api.gouv.fr) |
| `paris_boundaries.geojson`, `lyon_boundaries.geojson` | Commune borders for the maps, made by `fetch_map_boundaries.py` | [IGN GEOFLA](https://geoservices.ign.fr/geofla) |

We only use ages 25-54 because it is the only age group INSEE has made
comparable across all 9 censuses.

## Folders

- `do/` : the scripts
- `input/` : the data
- `output/` : graphs and result tables

## How to run

Run everything from the main project folder (not from inside `do/`):

```
pip install -r do/requirements.txt
python do/get_coordinates.py
python do/paris_analysis.py
python do/lyon_analysis.py
python do/fetch_map_boundaries.py
python do/map_job_density.py
```

The order matters. The analysis scripts need `coordinates.csv` from
`get_coordinates.py`, and the map script needs the `.geojson` files from
`fetch_map_boundaries.py`. 

## What each script does

- `get_coordinates.py` : downloads the coordinates of all communes
- `paris_analysis.py` : Paris: share of jobs and residents within 5 and
  10 km of the centre for each census year, plus a cumulative curve for 2022
- `lyon_analysis.py` : the same for Lyon (Lyon is only one row in the
  data, so we can't look inside the city, only Lyon vs. its suburbs)
- `fetch_map_boundaries.py` : downloads commune borders for the maps
- `map_job_density.py` : maps of jobs per km2 in 2022

## Output

- `*_cumulative_2022.png` : share of jobs and residents reached as you move
  away from the centre. If the jobs line is above the residents line, jobs
  are more concentrated.
- `*_trend.png` : share within 5 km of the centre, 1968-2022
- `*_trend_data.csv` : the numbers behind the trend graph (5 and 10 km)
- `*_job_density_map.png` : jobs per km2, on a log scale since the centre
  has far more jobs than everywhere else