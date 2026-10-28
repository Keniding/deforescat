"""Clima diario NASA POWER (MERRA-2, sin clave). Verificado: endpoint daily/point responde 200.

Latencia observada (2026-10-28): el último día con datos fue 2026-10-21, es decir ~7 días;
los días posteriores devuelven -999 (relleno).
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

from .dataset import CELL, WEATHER

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def fetch_point(lat: float, lon: float, start: str, end: str) -> pd.DataFrame:
    """start/end en formato YYYYMMDD. Valor de relleno -999 -> NaN."""
    r = requests.get(URL, params={
        "parameters": ",".join(WEATHER), "community": "AG", "latitude": lat,
        "longitude": lon, "start": start, "end": end, "format": "JSON"}, timeout=180)
    r.raise_for_status()
    df = pd.DataFrame(r.json()["properties"]["parameter"]).reset_index(names="date")
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    return df.replace(-999.0, float("nan"))


def fetch_cells(keys: pd.DataFrame, start: str, end: str, cache_dir: Path | None = None) -> pd.DataFrame:
    """Clima en el centro de cada celda (lat,lon = esquina SO). Con `cache_dir` reutiliza descargas."""
    def get(k):
        f = cache_dir / f"{k.lat}_{k.lon}_{start}_{end}.parquet" if cache_dir else None
        if f is not None and f.exists():
            return pd.read_parquet(f)
        df = fetch_point(k.lat + CELL / 2, k.lon + CELL / 2, start, end).assign(lat=k.lat, lon=k.lon)
        if f is not None:
            f.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(f)
        return df
    with ThreadPoolExecutor(4) as ex:
        return pd.concat(ex.map(get, keys.drop_duplicates().itertuples()), ignore_index=True)
