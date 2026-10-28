"""Grilla espacio-temporal, variables y etiquetas t+h a partir de focos de calor y clima."""
from __future__ import annotations

import numpy as np
import pandas as pd

CELL = 0.5  # grados
WEATHER = ["T2M_MAX", "PRECTOTCORR", "WS10M_MAX", "RH2M"]


def to_cells(fires: pd.DataFrame) -> pd.DataFrame:
    """Cuenta de focos por celda y día.

    Acepta el archivo anual (confidence n/l/h, columna `type`) y el NRT de 7 días
    (confidence nominal/low/high, sin `type`). Se excluye confianza baja y, si existe
    `type`, todo lo que no sea vegetación presunta (type==0).
    """
    keep = fires["confidence"].astype(str).str[0].str.lower() != "l"
    if "type" in fires.columns:
        keep &= fires["type"] == 0
    fires = fires[keep]
    df = pd.DataFrame({
        "date": pd.to_datetime(fires["acq_date"]),
        "lat": np.floor(fires["latitude"] / CELL) * CELL,
        "lon": np.floor(fires["longitude"] / CELL) * CELL,
    })
    return df.groupby(["lat", "lon", "date"]).size().rename("n_fires").reset_index()


def panel(cells: pd.DataFrame, keys: pd.DataFrame, start, end) -> pd.DataFrame:
    """Panel diario (celda, día) para las celdas `keys`, con variables de focos y estacionalidad."""
    days = pd.DataFrame({"date": pd.date_range(start, end, freq="D")})
    p = keys[["lat", "lon"]].drop_duplicates().merge(days, how="cross")
    p = p.merge(cells, on=["lat", "lon", "date"], how="left").fillna({"n_fires": 0})
    p = p.sort_values(["lat", "lon", "date"]).reset_index(drop=True)
    g = p.groupby(["lat", "lon"])["n_fires"]
    for w in (1, 3, 7, 14):
        p[f"fires_{w}d"] = g.transform(lambda s, w=w: s.rolling(w, min_periods=1).sum())
    p["doy"] = p["date"].dt.day_of_year
    return p


def add_label(p: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """y = 1 si hay foco en la celda en t+horizon. Se descartan los días sin futuro conocido."""
    fut = p.groupby(["lat", "lon"])["n_fires"].shift(-horizon)
    out = p.assign(y=(fut > 0).astype(float))
    return out[fut.notna()]


def add_weather(p: pd.DataFrame, w: pd.DataFrame, lag: int = 0) -> pd.DataFrame:
    """Une clima y lluvia acumulada 7/30 días. `lag`>0 usa el clima de t-lag (clima realmente disponible)."""
    w = w.sort_values(["lat", "lon", "date"]).copy()
    g = w.groupby(["lat", "lon"])
    w["rain_7d"] = g["PRECTOTCORR"].transform(lambda s: s.rolling(7, min_periods=1).sum())
    w["rain_30d"] = g["PRECTOTCORR"].transform(lambda s: s.rolling(30, min_periods=1).sum())
    cols = WEATHER + ["rain_7d", "rain_30d"]
    if lag:
        w[cols] = w.groupby(["lat", "lon"])[cols].shift(lag)
    return p.merge(w[["lat", "lon", "date", *cols]], on=["lat", "lon", "date"], how="left")


def build(cells: pd.DataFrame, horizon: int, start, end) -> pd.DataFrame:
    """Panel de las celdas con focos en `cells` más etiqueta t+horizon (sin clima)."""
    return add_label(panel(cells, cells[["lat", "lon"]], start, end), horizon)
