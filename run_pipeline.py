"""Pipeline: focos reales FIRMS Bolivia 2021-2024 + clima NASA POWER -> LightGBM."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from deforescat import dataset, model, weather

RAW, OUT = Path("data/raw"), Path("data")
TOP_CELLS = 100
START, END = "2021-01-01", "2024-12-31"


def load_cells():
    f = pd.concat(pd.read_csv(p, usecols=["latitude", "longitude", "acq_date", "type", "confidence"])
                  for p in sorted(RAW.glob("viirs_bolivia_*.csv")))
    return dataset.to_cells(f)


def load_weather(keys):
    cache = OUT / "weather.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    # POWER devuelve el centro de celda MERRA-2; consultamos el centro de nuestra celda
    def get(k):
        return weather.fetch_point(k.lat + dataset.CELL / 2, k.lon + dataset.CELL / 2, "20210101", "20241231") \
            .assign(lat=k.lat, lon=k.lon)
    with ThreadPoolExecutor(4) as ex:
        w = pd.concat(ex.map(get, keys.itertuples()))
    w.to_parquet(cache)
    return w


def main(horizon):
    cells = load_cells()
    top = cells.groupby(["lat", "lon"])["n_fires"].sum().nlargest(TOP_CELLS).reset_index()
    cells = cells.merge(top[["lat", "lon"]])
    panel = dataset.build(cells, horizon, START, END)
    w = load_weather(top[["lat", "lon"]])
    w = w.sort_values(["lat", "lon", "date"])
    g = w.groupby(["lat", "lon"])
    w["rain_7d"] = g["PRECTOTCORR"].transform(lambda s: s.rolling(7, min_periods=1).sum())
    w["rain_30d"] = g["PRECTOTCORR"].transform(lambda s: s.rolling(30, min_periods=1).sum())
    df = panel.merge(w, on=["lat", "lon", "date"], how="left")
    res = model.evaluate(df)
    res["horizon_days"] = horizon
    print(json.dumps(res))
    return res


if __name__ == "__main__":
    out = [main(h) for h in (1, 2)]
    Path("docs/resultados.json").write_text(json.dumps(out, indent=2))
