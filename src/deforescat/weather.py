"""Clima diario NASA POWER (MERRA-2, sin clave). Verificado: endpoint daily/point responde 200."""
from __future__ import annotations

import pandas as pd
import requests

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = ["T2M_MAX", "PRECTOTCORR", "WS10M_MAX", "RH2M"]


def fetch_point(lat: float, lon: float, start: str, end: str) -> pd.DataFrame:
    """start/end en formato YYYYMMDD. Valor de relleno -999 -> NaN."""
    r = requests.get(URL, params={
        "parameters": ",".join(PARAMS), "community": "AG", "latitude": lat,
        "longitude": lon, "start": start, "end": end, "format": "JSON"}, timeout=180)
    r.raise_for_status()
    p = r.json()["properties"]["parameter"]
    df = pd.DataFrame(p).reset_index(names="date")
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.replace(-999.0, float("nan"))
    df["lat"], df["lon"] = lat, lon
    return df
