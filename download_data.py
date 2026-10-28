"""Descarga los archivos anuales de focos VIIRS S-NPP de Peru (FIRMS, sin clave) a data/raw/."""
from pathlib import Path

import requests

URL = "https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/{y}/viirs-snpp_{y}_Peru.csv"
OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)
for y in range(2021, 2025):
    dest = OUT / f"viirs_peru_{y}.csv"
    if dest.exists():
        continue
    r = requests.get(URL.format(y=y), timeout=300)
    r.raise_for_status()
    dest.write_bytes(r.content)
    print(dest, len(r.content))
