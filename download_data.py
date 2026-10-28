"""Descarga a data/raw/: focos VIIRS S-NPP de Perú 2021-2025 (FIRMS, sin clave) y el contorno de Perú."""
from pathlib import Path

import requests

FIRMS = "https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/{y}/viirs-snpp_{y}_Peru.csv"
OUTLINE = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/PER.geo.json"
OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)


def get(url, dest):
    if dest.exists():
        return
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    dest.write_bytes(r.content)
    print(dest, len(r.content))


for y in range(2021, 2026):
    get(FIRMS.format(y=y), OUT / f"viirs_peru_{y}.csv")
get(OUTLINE, OUT / "peru.geojson")  # contorno simplificado, solo para dibujar mapas
