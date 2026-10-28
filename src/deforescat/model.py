"""Modelos LightGBM, variantes de variables y métricas."""
from __future__ import annotations

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

FIRE = ["fires_1d", "fires_3d", "fires_7d", "doy"]
WX = ["T2M_MAX", "PRECTOTCORR", "WS10M_MAX", "RH2M", "rain_7d", "rain_30d"]
# lag = días de retraso del clima. POWER tenía ~7 días de latencia al medirlo (2026-10-28),
# por eso el modelo "operacional" solo usa clima de t-7 y focos de ventanas <=7 días
# (el archivo NRT de FIRMS solo cubre 7 días).
VARIANTS = {
    "operacional": {"lag": 7, "feats": FIRE + WX},
    "investigacion": {"lag": 0, "feats": FIRE + ["fires_14d"] + WX},
    "solo_focos": {"lag": 0, "feats": FIRE + ["fires_14d"]},
}


def fit(train: pd.DataFrame, feats: list[str], seed: int = 0) -> lgb.LGBMClassifier:
    clf = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, random_state=seed, verbose=-1)
    return clf.fit(train[feats], train["y"])


def top_frac_precision(y: np.ndarray, p: np.ndarray, frac: float = 0.1) -> float:
    """Precisión entre el `frac` de casos con mayor riesgo predicho."""
    k = max(1, int(len(y) * frac))
    return float(np.asarray(y)[np.argsort(-p)[:k]].mean())


def score(y, p, persistence) -> dict:
    return {
        "prevalencia": float(np.mean(y)),
        "ap": float(average_precision_score(y, p)),
        "auc": float(roc_auc_score(y, p)),
        "precision_top10": top_frac_precision(y, p),
        "ap_persistencia": float(average_precision_score(y, persistence)),
    }
