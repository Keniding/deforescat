"""Predicción sobre datos NUEVOS: focos NRT de FIRMS (últimos 7 días) + clima NASA POWER.

    uv run python predict.py                    # pronóstico t+1 y t+2 desde el último día disponible
    uv run python predict.py --verify outputs/pronostico_AAAA-MM-DD.csv   # compara con lo ocurrido después

Limitaciones: solo las celdas con las que se entrenó el modelo (100 celdas más activas 2021-2025);
el archivo NRT no trae `type` y su procesamiento difiere ligeramente del archivo anual.
"""
import argparse
import io
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd
import requests
from sklearn.metrics import average_precision_score

from deforescat import dataset, viz, weather

NRT = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_America_7d.csv"
BBOX = (-81.4, -18.4, -68.6, 0.0)  # oeste, sur, este, norte (Perú)
OUT = Path("outputs")


def load_nrt() -> pd.DataFrame:
    r = requests.get(NRT, timeout=300)
    r.raise_for_status()
    snap = Path("data/nrt")
    snap.mkdir(parents=True, exist_ok=True)
    (snap / f"nrt_{datetime.now(UTC):%Y%m%dT%H%M}.csv").write_text(r.text)  # snapshot reproducible
    f = pd.read_csv(io.StringIO(r.text))
    w, s, e, n = BBOX
    return f[f["longitude"].between(w, e) & f["latitude"].between(s, n)]


def forecast(fires: pd.DataFrame, as_of: pd.Timestamp, models: dict) -> pd.DataFrame:
    keys = models[1]["keys"]
    lag = models[1]["lag"]
    cells = dataset.to_cells(fires[pd.to_datetime(fires["acq_date"]) <= as_of])
    p = dataset.panel(cells, keys, as_of - pd.Timedelta(days=6), as_of)
    # clima: 40 días hasta as_of; la lluvia a 30 días termina en as_of-lag
    wx = weather.fetch_cells(keys, f"{(as_of - pd.Timedelta(days=40)):%Y%m%d}", f"{as_of:%Y%m%d}")
    p = dataset.add_weather(p, wx, lag)
    last = p[p["date"] == as_of].copy()
    n_nan = int(last[models[1]["feats"]].isna().any(axis=1).sum())
    if n_nan:
        print(f"AVISO: {n_nan} celdas con variables faltantes (clima aún no publicado); LightGBM las maneja como NaN")
    for h, m in models.items():
        last[f"p_t{h}"] = m["model"].predict_proba(last[m["feats"]])[:, 1]
    return last[["lat", "lon", "fires_1d", "fires_3d", "fires_7d", "p_t1", "p_t2"]]


def verify(path: str, fires: pd.DataFrame):
    fc = pd.read_csv(path)
    as_of = pd.Timestamp(Path(path).stem.split("_")[-1])
    cells = dataset.to_cells(fires)
    for h in (1, 2):
        day = as_of + pd.Timedelta(days=h)
        obs = cells[cells["date"] == day][["lat", "lon"]].assign(y=1.0)
        if day > pd.to_datetime(fires["acq_date"]).max():
            print(f"t+{h} ({day:%Y-%m-%d}): todavía no hay datos NRT de ese día")
            continue
        m = fc.merge(obs, how="left", on=["lat", "lon"]).fillna({"y": 0.0})
        print(f"t+{h} ({day:%Y-%m-%d}): celdas con foco {int(m['y'].sum())}/{len(m)}, "
              f"AP={average_precision_score(m['y'], m[f'p_t{h}']):.3f} (azar≈{m['y'].mean():.3f}), "
              f"AP persistencia={average_precision_score(m['y'], (m['fires_1d'] > 0)):.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", help="AAAA-MM-DD; por defecto el último día con focos NRT")
    ap.add_argument("--verify", help="CSV de pronóstico previo a comparar con focos observados")
    a = ap.parse_args()
    fires = load_nrt()
    if a.verify:
        verify(a.verify, fires)
        raise SystemExit
    as_of = pd.Timestamp(a.as_of) if a.as_of else pd.to_datetime(fires["acq_date"]).max()
    models = {h: joblib.load(f"models/operacional_h{h}.joblib") for h in (1, 2)}
    fc = forecast(fires, as_of, models)
    OUT.mkdir(exist_ok=True)
    dest = OUT / f"pronostico_{as_of:%Y-%m-%d}.csv"
    fc.sort_values("p_t1", ascending=False).to_csv(dest, index=False)
    recent = fires[pd.to_datetime(fires["acq_date"]) <= as_of]
    viz.mapa_pronostico(fc, recent, as_of)
    print(f"as_of={as_of:%Y-%m-%d} -> {dest}; figura docs/figures/08_pronostico_ultimo.png")
    print(fc.sort_values("p_t1", ascending=False).head(10).round(3).to_string(index=False))
