"""Ingesta de clima histórico (Open-Meteo archive, basado en ERA5).

Los nombres de variables diarias deben verificarse contra la documentación
oficial cuando haya acceso a open-meteo.com (ver docs/FUENTES.md).
"""
from __future__ import annotations

import pandas as pd
import requests

URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY = ["temperature_2m_max", "precipitation_sum", "wind_speed_10m_max",
         "et0_fao_evapotranspiration"]


def fetch_point(lat: float, lon: float, start: str, end: str) -> pd.DataFrame:
    r = requests.get(URL, params={
        "latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
        "daily": ",".join(DAILY), "timezone": "UTC"}, timeout=120)
    r.raise_for_status()
    df = pd.DataFrame(r.json()["daily"]).rename(columns={"time": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df["lat"], df["lon"] = lat, lon
    return df
