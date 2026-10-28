"""Grilla espacio-temporal y etiquetas t+h a partir de focos de calor."""
from __future__ import annotations

import numpy as np
import pandas as pd

CELL = 0.5  # grados


def to_cells(fires: pd.DataFrame) -> pd.DataFrame:
    """Cuenta de focos por celda y día (usa columnas FIRMS latitude, longitude, acq_date)."""
    fires = fires[(fires["type"] == 0) & (fires["confidence"] != "l")]  # vegetación, sin baja confianza
    df = pd.DataFrame({
        "date": pd.to_datetime(fires["acq_date"]),
        "lat": np.floor(fires["latitude"] / CELL) * CELL,
        "lon": np.floor(fires["longitude"] / CELL) * CELL,
    })
    return df.groupby(["lat", "lon", "date"]).size().rename("n_fires").reset_index()


def build(cells: pd.DataFrame, horizon: int, start, end) -> pd.DataFrame:
    """Panel (celda, día) para celdas con algún foco; etiqueta = foco en t+horizon."""
    days = pd.date_range(start, end, freq="D")
    keys = cells[["lat", "lon"]].drop_duplicates()
    panel = keys.merge(pd.DataFrame({"date": days}), how="cross")
    panel = panel.merge(cells, on=["lat", "lon", "date"], how="left").fillna({"n_fires": 0})
    panel = panel.sort_values(["lat", "lon", "date"]).reset_index(drop=True)
    g = panel.groupby(["lat", "lon"])["n_fires"]
    for w in (1, 3, 7, 14):
        panel[f"fires_{w}d"] = g.transform(lambda s, w=w: s.rolling(w, min_periods=1).sum())
    panel["doy"] = panel["date"].dt.dayofyear
    panel["y"] = (g.shift(-horizon) > 0).astype("float")
    panel.loc[g.shift(-horizon).isna(), "y"] = np.nan
    return panel.dropna(subset=["y"])
