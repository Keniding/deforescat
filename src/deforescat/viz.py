"""Figuras del pipeline (matplotlib). Cada función guarda un PNG y devuelve la ruta."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import precision_recall_curve, roc_curve

from .dataset import CELL

OUT = Path("docs/figures")
C = {"operacional": "#d95f02", "investigacion": "#1b9e77", "solo_focos": "#7570b3", "persistencia": "#666666"}


def _save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def _outline(ax, geojson="data/raw/peru.geojson"):
    p = Path(geojson)
    if not p.exists():
        return
    geom = json.loads(p.read_text())["features"][0]["geometry"]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        xy = np.array(poly[0])
        ax.plot(xy[:, 0], xy[:, 1], color="black", lw=0.8)


def _map_axes(ax, title):
    _outline(ax)
    ax.set_xlim(-82, -68)
    ax.set_ylim(-19, 0.5)
    ax.set_aspect("equal")
    ax.set_xlabel("longitud")
    ax.set_ylabel("latitud")
    ax.set_title(title, fontsize=10)


def _cells_scatter(ax, df, col, cmap, vmin=None, vmax=None, norm=None):
    s = ax.scatter(df["lon"] + CELL / 2, df["lat"] + CELL / 2, c=df[col], s=34, marker="s", cmap=cmap,
                   vmin=vmin, vmax=vmax, norm=norm, edgecolors="none", zorder=3)
    return s


def mapa_focos(cells, keys):
    tot = cells.groupby(["lat", "lon"])["n_fires"].sum().reset_index()
    sel = tot.merge(keys[["lat", "lon"]])
    fig, ax = plt.subplots(figsize=(6, 7))
    ax.scatter(tot["lon"] + CELL / 2, tot["lat"] + CELL / 2, s=10, marker="s", color="#cccccc", label="todas las celdas con focos")
    s = _cells_scatter(ax, sel, "n_fires", "YlOrRd", norm=matplotlib.colors.LogNorm())
    fig.colorbar(s, ax=ax, shrink=0.6, label="focos 2021-2025 (escala log)")
    _map_axes(ax, "Focos VIIRS en Perú y las 100 celdas modeladas")
    ax.legend(loc="lower left", fontsize=8)
    return _save(fig, "01_mapa_focos.png")


def serie_mensual(cells, keys):
    m = cells.assign(mes=cells["date"].dt.to_period("M").dt.to_timestamp())
    allm = m.groupby("mes")["n_fires"].sum()
    selm = m.merge(keys[["lat", "lon"]]).groupby("mes")["n_fires"].sum()
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.plot(allm.index, allm.values, color="#999999", label="todo Perú")
    ax.plot(selm.index, selm.values, color="#d95f02", label="100 celdas modeladas")
    ax.set_ylabel("focos / mes")
    ax.set_title("Estacionalidad: la temporada de fuegos se concentra en agosto-octubre", fontsize=10)
    ax.legend()
    return _save(fig, "02_serie_mensual.png")


def comparar_folds(res: pd.DataFrame):
    r = res[res["horizonte"] == 1]
    years = sorted(r["anio_test"].unique())
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, metric, ttl in zip(axes, ["ap", "auc"], ["Precisión promedio (AP), t+1", "AUC, t+1"], strict=True):
        w = 0.2
        for i, v in enumerate(["solo_focos", "investigacion", "operacional"]):
            vals = [r[(r["variante"] == v) & (r["anio_test"] == y)][metric].item() for y in years]
            ax.bar(np.arange(len(years)) + (i - 1.5) * w, vals, w, label=v, color=C[v])
        if metric == "ap":
            pers = [r[(r["variante"] == "operacional") & (r["anio_test"] == y)]["ap_persistencia"].item() for y in years]
            prev = [r[(r["variante"] == "operacional") & (r["anio_test"] == y)]["prevalencia"].item() for y in years]
            ax.bar(np.arange(len(years)) + 1.5 * w, pers, w, label="persistencia", color=C["persistencia"])
            ax.plot(np.arange(len(years)), prev, "k_", ms=24, label="prevalencia (azar)")
        ax.set_xticks(np.arange(len(years)), [f"test {y}" for y in years])
        ax.set_title(ttl, fontsize=10)
        ax.set_ylim(0, 1.0)
    axes[0].legend(fontsize=7, ncol=3, loc="upper center")
    return _save(fig, "03_validacion_por_anios.png")


def curvas(preds: dict, title_year):
    """preds: {'operacional': (y, p), ..., 'persistencia': (y, p)} del año de test."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    for k, (y, p) in preds.items():
        pr, rc, _ = precision_recall_curve(y, p)
        a1.plot(rc, pr, label=k, color=C[k])
        fpr, tpr, _ = roc_curve(y, p)
        a2.plot(fpr, tpr, label=k, color=C[k])
    y0 = next(iter(preds.values()))[0]
    a1.axhline(np.mean(y0), color="k", ls=":", lw=0.8)
    a1.set(xlabel="recall", ylabel="precisión", title=f"Precisión-recall, t+1, test {title_year}")
    a2.plot([0, 1], [0, 1], "k:", lw=0.8)
    a2.set(xlabel="falsos positivos", ylabel="verdaderos positivos", title="ROC")
    a1.legend(fontsize=8)
    return _save(fig, "04_curvas_pr_roc.png")


def calibracion(y, p, title_year):
    fr, mp = calibration_curve(y, p, n_bins=10, strategy="quantile")
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.plot(mp, fr, "o-", color=C["operacional"])
    ax.plot([0, 1], [0, 1], "k:")
    ax.set(xlabel="probabilidad predicha", ylabel="frecuencia observada",
           title=f"Calibración (operacional, t+1, test {title_year})")
    return _save(fig, "05_calibracion.png")


def importancia(model, feats):
    imp = pd.Series(model.booster_.feature_importance("gain"), index=feats).sort_values()
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.barh(imp.index, imp.values / imp.sum(), color=C["operacional"])
    ax.set_title("Importancia de variables (ganancia), modelo operacional t+1", fontsize=10)
    return _save(fig, "06_importancia.png")


def mapa_riesgo(day_df, day):
    """day_df: columnas lat, lon, p (riesgo t+1) y y (foco real en t+1) para un día."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 6))
    s = _cells_scatter(axes[0], day_df, "p", "YlOrRd", vmin=0, vmax=1)
    fig.colorbar(s, ax=axes[0], shrink=0.6, label="riesgo predicho")
    _map_axes(axes[0], f"Riesgo predicho para {day + pd.Timedelta(days=1):%Y-%m-%d}")
    _cells_scatter(axes[1], day_df, "y", matplotlib.colors.ListedColormap(["#dddddd", "#b30000"]), vmin=0, vmax=1)
    _map_axes(axes[1], "Foco realmente observado (rojo)")
    return _save(fig, "07_mapa_riesgo_vs_real.png")


def mapa_pronostico(fc, fires_recent, as_of, name="08_pronostico_ultimo.png"):
    fig, axes = plt.subplots(1, 2, figsize=(10, 6))
    for ax, col, h in zip(axes, ["p_t1", "p_t2"], [1, 2], strict=True):
        s = _cells_scatter(ax, fc, col, "YlOrRd", vmin=0, vmax=1)
        if fires_recent is not None and len(fires_recent):
            ax.scatter(fires_recent["longitude"], fires_recent["latitude"], s=2, color="blue", alpha=0.4, zorder=2,
                       label="focos NRT 7 días (sin filtrar)")
        fig.colorbar(s, ax=ax, shrink=0.6, label="riesgo predicho")
        _map_axes(ax, f"Pronóstico para {as_of + pd.Timedelta(days=h):%Y-%m-%d} (t+{h})")
    axes[0].legend(loc="lower left", fontsize=7, markerscale=4)
    return _save(fig, name)
