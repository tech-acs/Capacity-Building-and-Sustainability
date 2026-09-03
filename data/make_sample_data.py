#!/usr/bin/env python3
"""
Builds SYNTHETIC sample data so every notebook in this repo runs with no
downloads and no registration. It is shaped like the real NISR/HDX handoff
described in the course site's Chapter 3 (province/district/date/value +
model features), but every number is randomly generated and every P-code
uses an obviously-fake "SIM-" prefix so it can never be mistaken for a real
HDX ADM2_PCODE.

This is the fast path: one command, straight to the processed dataset every
Track 2 notebook reads. For the slower, more realistic path — three messy
raw source files reconciled through an actual Track 1 integration pipeline,
producing this exact same dataset — see make_track1_sources.py and Track 1
Module 9. Both paths are seeded identically, so they agree on every number.

Run once from the repo root:  python3 data/make_sample_data.py
Then swap in real data by following data/README.md.
"""
import json
import os

import pandas as pd

from _rwanda_synth import DISTRICTS, generate_dataframe

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(ROOT, "raw")
PROCESSED_DIR = os.path.join(ROOT, "processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

df = generate_dataframe(seed=7)
raw_path = os.path.join(RAW_DIR, "synthetic_eicv_extract.csv")
df.to_csv(raw_path, index=False)

# "Cleaned" processed copy — mirrors what Module 1's load-and-clean step does
# to a real extract (rename, dedupe, coerce dates, drop unkeyed rows).
processed = df.copy()
processed["date"] = pd.to_datetime(processed["date"])
processed = processed.drop_duplicates().dropna(subset=["district_pcode", "date"])
processed.to_csv(os.path.join(PROCESSED_DIR, "track2_dataset.csv"), index=False)

# A tiny synthetic "admin boundary" layer: one rectangle per district, inside
# a made-up bounding box, tagged with the same SIM- pcode. Real geometry,
# fabricated shapes — good enough to prove the join and mapping code, not to
# be mistaken for the real HDX file.
features = []
for province, district, pcode, lon_min, lon_max, lat_min, lat_max in DISTRICTS:
    ring = [
        [lon_min, lat_min], [lon_max, lat_min],
        [lon_max, lat_max], [lon_min, lat_max], [lon_min, lat_min],
    ]
    features.append({
        "type": "Feature",
        "properties": {"province": province, "district": district, "pcode_sim": pcode},
        "geometry": {"type": "Polygon", "coordinates": [ring]},
    })
geojson = {"type": "FeatureCollection", "features": features}
with open(os.path.join(PROCESSED_DIR, "admin_boundaries_synthetic.geojson"), "w") as f:
    json.dump(geojson, f, indent=1)

print(f"Wrote {len(df):,} rows to {raw_path}")
print("Wrote processed/track2_dataset.csv and processed/admin_boundaries_synthetic.geojson")
print("This is SYNTHETIC data. See data/README.md before treating any number here as real.")
