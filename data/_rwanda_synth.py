"""
Shared synthetic-data generator for the Rwanda-shaped sample dataset used
throughout both tracks. Every number here is fabricated (numpy.random) and
every P-code uses an obviously-fake "SIM-" prefix — see data/README.md.

This module exists so that Track 1's raw, multi-source practice files
(data/make_track1_sources.py) and Track 2's ready-to-use processed dataset
(data/make_sample_data.py) are generated from the exact same seeded values.
Track 1's integration pipeline, run correctly, reconstructs the identical
numbers Track 2 ships out of the box — a real, checkable Track1 -> Track2
handoff, not just a narrative one.

Do not reorder the random calls below: Track 2's notebooks were executed
against this exact sequence, and reordering would silently change every
downstream number and chart.
"""
import random

import numpy as np
import pandas as pd

# Real Rwandan province/district names (geography is a fact, not a
# statistic) — paired with an obviously-synthetic P-code and a made-up
# bounding box cell so geopandas/sf have real-looking polygons to draw
# without claiming to be the real HDX boundary file.
DISTRICTS = [
    # province,       district,      pcode,        lon_min, lon_max, lat_min, lat_max
    ("Kigali City", "Gasabo",     "SIM-GAS", 30.05, 30.20, -1.95, -1.80),
    ("Kigali City", "Kicukiro",   "SIM-KIC", 30.05, 30.15, -2.05, -1.95),
    ("Kigali City", "Nyarugenge", "SIM-NYA", 29.95, 30.05, -2.02, -1.92),
    ("Northern",     "Musanze",    "SIM-MUS", 29.55, 29.70, -1.55, -1.40),
    ("Northern",     "Gicumbi",    "SIM-GIC", 29.85, 30.05, -1.55, -1.35),
    ("Southern",     "Huye",       "SIM-HUY", 29.68, 29.80, -2.65, -2.55),
    ("Southern",     "Nyanza",     "SIM-NYZ", 29.65, 29.78, -2.40, -2.30),
    ("Eastern",      "Rwamagana",  "SIM-RWA", 30.35, 30.50, -1.98, -1.88),
    ("Eastern",      "Nyagatare",  "SIM-NYG", 30.20, 30.45, -1.35, -1.15),
    ("Western",      "Rubavu",     "SIM-RUB", 29.28, 29.40, -1.75, -1.62),
]

N_MONTHS = 24


def generate_rows(seed=7):
    """Returns the list-of-dicts row set behind track2_dataset.csv, and
    only that set — deterministic given `seed`. Track 2 uses this
    directly; Track 1's raw sources are this same set, split apart."""
    random.seed(seed)
    np.random.seed(seed)
    dates = pd.date_range("2023-01-01", periods=N_MONTHS, freq="MS")

    rows = []
    for province, district, pcode, *_ in DISTRICTS:
        base = np.random.uniform(35, 65)
        trend = np.random.uniform(-0.15, 0.35)
        seasonal_amp = np.random.uniform(2, 6)
        for i, d in enumerate(dates):
            seasonal = seasonal_amp * np.sin(2 * np.pi * (d.month / 12))
            noise = np.random.normal(0, 2.2)
            value = max(0, base + trend * i + seasonal + noise)
            feature_1 = np.random.normal(50, 10)
            feature_2 = np.random.normal(20, 5)
            logit = 0.09 * (feature_1 - 50) - 0.13 * (feature_2 - 20) + np.random.normal(0, 0.8)
            outcome = int(logit > 0)
            rows.append({
                "date": d.strftime("%Y-%m-%d"),
                "province": province,
                "district": district,
                "district_pcode": pcode,
                "indicator": "sample_wellbeing_index",
                "value": round(value, 2),
                "feature_1": round(feature_1, 2),
                "feature_2": round(feature_2, 2),
                "outcome": outcome,
            })
    return rows


def generate_dataframe(seed=7):
    return pd.DataFrame(generate_rows(seed=seed))
