"""Baseline LightGBM con validación temporal y comparación con persistencia."""
from __future__ import annotations

import lightgbm as lgb
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

NON_FEATURES = {"date", "y", "n_fires"}


def temporal_split(df: pd.DataFrame, test_frac: float = 0.25):
    cut = df["date"].sort_values().iloc[int(len(df) * (1 - test_frac))]
    return df[df["date"] < cut], df[df["date"] >= cut]


def evaluate(df: pd.DataFrame, seed: int = 0) -> dict:
    train, test = temporal_split(df)
    feats = [c for c in df.columns if c not in NON_FEATURES]
    clf = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, random_state=seed, verbose=-1)
    clf.fit(train[feats], train["y"])
    p = clf.predict_proba(test[feats])[:, 1]
    persist = (test["fires_1d"] > 0).astype(float)
    return {
        "prevalence_test": float(test["y"].mean()),
        "ap_model": float(average_precision_score(test["y"], p)),
        "auc_model": float(roc_auc_score(test["y"], p)),
        "ap_persistence": float(average_precision_score(test["y"], persist)),
        "n_train": len(train), "n_test": len(test),
    }
