"""Pruebas de lógica con datos sintéticos mínimos (solo verifican el código, no son resultados científicos)."""
import pandas as pd

from deforescat.dataset import add_weather, build, panel, to_cells


def test_label_is_future_fire():
    fires = pd.DataFrame({"acq_date": ["2024-01-03"], "latitude": [-12.1], "longitude": [-70.1],
                          "type": [0], "confidence": ["n"]})
    p = build(to_cells(fires), horizon=1, start="2024-01-01", end="2024-01-05")
    row = p[p["date"] == "2024-01-02"].iloc[0]
    assert row["y"] == 1.0 and row["fires_1d"] == 0
    assert "2024-01-05" not in set(p["date"].astype(str))


def test_nrt_confidence_words_and_no_type_column():
    fires = pd.DataFrame({"acq_date": ["2024-01-03"] * 2, "latitude": [-12.1, -12.2],
                          "longitude": [-70.1, -70.2], "confidence": ["nominal", "low"]})
    assert to_cells(fires)["n_fires"].sum() == 1


def test_weather_lag_uses_past_values():
    keys = pd.DataFrame({"lat": [0.0], "lon": [0.0]})
    empty = pd.DataFrame({"lat": [], "lon": [], "date": pd.to_datetime([]), "n_fires": []})
    p = panel(empty, keys, "2024-01-01", "2024-01-10")
    w = pd.DataFrame({"date": pd.date_range("2024-01-01", "2024-01-10"), "lat": 0.0, "lon": 0.0,
                      "T2M_MAX": range(10), "PRECTOTCORR": 0.0, "WS10M_MAX": 0.0, "RH2M": 0.0})
    out = add_weather(p, w, lag=3)
    assert out.loc[out["date"] == "2024-01-08", "T2M_MAX"].item() == 4  # valor del 2024-01-05
