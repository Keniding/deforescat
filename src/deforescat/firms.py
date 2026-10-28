"""Ingesta de focos de calor NASA FIRMS (API area, CSV).

Formato documentado: /api/area/csv/[MAP_KEY]/[SOURCE]/[west,south,east,north]/[DAY_RANGE]/[DATE]
DAY_RANGE admite 1..10; límite 5000 transacciones / 10 min por MAP_KEY.
"""
from __future__ import annotations

import io
import os
from datetime import date, timedelta

import pandas as pd
import requests

BASE = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
MAX_DAYS = 10


def fetch_chunk(map_key: str, source: str, bbox: tuple[float, float, float, float],
                start: date, days: int) -> pd.DataFrame:
    w, s, e, n = bbox
    url = f"{BASE}/{map_key}/{source}/{w},{s},{e},{n}/{days}/{start.isoformat()}"
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))


def fetch_range(source: str, bbox: tuple[float, float, float, float],
                start: date, end: date, map_key: str | None = None) -> pd.DataFrame:
    """Descarga [start, end] en bloques de 10 días."""
    map_key = map_key or os.environ["FIRMS_MAP_KEY"]
    frames, cur = [], start
    while cur <= end:
        days = min(MAX_DAYS, (end - cur).days + 1)
        frames.append(fetch_chunk(map_key, source, bbox, cur, days))
        cur += timedelta(days=days)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
