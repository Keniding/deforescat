"""Pruebas de lógica con datos sintéticos mínimos (solo verifican el código, no son resultados científicos)."""
import pandas as pd

from deforescat.dataset import build, to_cells


def test_label_is_future_fire():
    fires = pd.DataFrame({"acq_date": ["2024-01-03"], "latitude": [-12.1], "longitude": [-70.1]})
    panel = build(to_cells(fires), horizon=1, start="2024-01-01", end="2024-01-05")
    row = panel[panel["date"] == "2024-01-02"].iloc[0]
    assert row["y"] == 1.0 and row["fires_1d"] == 0
    assert "2024-01-05" not in set(panel["date"].astype(str))
