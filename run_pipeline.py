"""Pipeline completo: focos FIRMS Perú 2021-2025 + clima NASA POWER -> validación por años,
modelos finales, métricas (docs/resultados.json) y figuras (docs/figures/)."""
import json
from pathlib import Path

import joblib
import pandas as pd

from deforescat import dataset, model, viz, weather

RAW, DATA = Path("data/raw"), Path("data")
TOP_CELLS = 100
START, END = "2021-01-01", "2025-12-31"
TEST_YEARS = (2023, 2024, 2025)  # cada año se prueba con un modelo entrenado solo con años anteriores
HORIZONS = (1, 2)


def top_keys(cells, before=None):
    c = cells if before is None else cells[cells["date"] < before]
    return c.groupby(["lat", "lon"])["n_fires"].sum().nlargest(TOP_CELLS).reset_index()[["lat", "lon"]]


def main():
    f = pd.concat(pd.read_csv(p, usecols=["latitude", "longitude", "acq_date", "type", "confidence"])
                  for p in sorted(RAW.glob("viirs_peru_*.csv")))
    cells = dataset.to_cells(f)
    final_keys = top_keys(cells)
    fold_keys = {y: top_keys(cells, f"{y}-01-01") for y in TEST_YEARS}  # solo años previos al test
    all_keys = pd.concat([final_keys, *fold_keys.values()]).drop_duplicates()
    print(f"focos filtrados: {int(cells['n_fires'].sum())}; celdas modeladas (unión): {len(all_keys)}")

    wx = weather.fetch_cells(all_keys, START.replace("-", ""), END.replace("-", ""), DATA / "weather")
    base = dataset.panel(cells, all_keys, START, END)

    rows, last_preds = [], {}
    for h in HORIZONS:
        lab = dataset.add_label(base, h)
        for vname, v in model.VARIANTS.items():
            df = dataset.add_weather(lab, wx, v["lag"])
            for ty in TEST_YEARS:
                keys = fold_keys[ty]
                d = df.merge(keys)
                cut = pd.Timestamp(f"{ty}-01-01")
                train = d[d["date"] < cut - pd.Timedelta(days=h)]  # purga: la etiqueta no puede mirar al test
                test = d[(d["date"] >= cut) & (d["date"] < pd.Timestamp(f"{ty + 1}-01-01"))]
                clf = model.fit(train, v["feats"])
                p = clf.predict_proba(test[v["feats"]])[:, 1]
                res = model.score(test["y"], p, (test["fires_1d"] > 0).astype(float))
                res.update(horizonte=h, variante=vname, anio_test=ty, n_train=len(train), n_test=len(test))
                rows.append(res)
                print(json.dumps({k: round(x, 3) if isinstance(x, float) else x for k, x in res.items()}))
                if ty == TEST_YEARS[-1] and h == 1:
                    last_preds[vname] = test.assign(p=p)

    results = pd.DataFrame(rows)
    Path("docs").mkdir(exist_ok=True)
    results.to_json("docs/resultados.json", orient="records", indent=2)

    # Modelos finales (operacional) con todos los años, para predecir datos nuevos
    Path("models").mkdir(exist_ok=True)
    v = model.VARIANTS["operacional"]
    for h in HORIZONS:
        d = dataset.add_weather(dataset.add_label(base, h), wx, v["lag"]).merge(final_keys)
        clf = model.fit(d, v["feats"])
        joblib.dump({"model": clf, "feats": v["feats"], "lag": v["lag"], "keys": final_keys,
                     "horizon": h, "trained_until": d["date"].max()}, f"models/operacional_h{h}.joblib")
        if h == 1:
            final_h1 = clf

    # Figuras
    viz.mapa_focos(cells, final_keys)
    viz.serie_mensual(cells, final_keys)
    viz.comparar_folds(results)
    ty = TEST_YEARS[-1]
    curves = {k: (p["y"].values, p["p"].values) for k, p in last_preds.items()}
    op = last_preds["operacional"]
    curves["persistencia"] = (op["y"].values, (op["fires_1d"] > 0).astype(float).values)
    viz.curvas(curves, ty)
    viz.calibracion(op["y"].values, op["p"].values, ty)
    viz.importancia(final_h1, v["feats"])
    busy = op.groupby("date")["y"].sum().idxmax()  # día con más celdas en llamas al día siguiente
    viz.mapa_riesgo(op[op["date"] == busy][["lat", "lon", "p", "y"]], busy)
    print("listo: docs/resultados.json, docs/figures/, models/")


if __name__ == "__main__":
    main()
