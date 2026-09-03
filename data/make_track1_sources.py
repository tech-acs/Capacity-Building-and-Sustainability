#!/usr/bin/env python3
"""
Builds the RAW, multi-source practice files Track 1's notebooks work with:
three partner-style exports with inconsistent column names, date formats,
and a couple of deliberately misspelled district names, plus the P-code
gazetteer used to reconcile them. This is the "before" picture; Track 1's
Module 9 pipeline is the "after" — and because these files are generated
from the exact same seeded values as Track 2's dataset (see
_rwanda_synth.py), a correctly-run Track 1 pipeline reconstructs
data/processed/track2_dataset.csv exactly, not just approximately.

Run once from the repo root:  python3 data/make_track1_sources.py
Then work through notebooks/track1/module-01.../ onward.
"""
import os

import pandas as pd

from _rwanda_synth import DISTRICTS, generate_dataframe

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(ROOT, "raw")
os.makedirs(RAW_DIR, exist_ok=True)

df = generate_dataframe(seed=7)  # identical values to Track 2's dataset
df["date"] = pd.to_datetime(df["date"])

# A couple of raw-world misspellings, injected on a handful of rows so the
# Module 4 harmonization step has real (small, recoverable) unmatched rows
# to flag and fix, per the "reviewed, not dropped" lesson. Deliberately
# small and deterministic — same rows every run: the 5th and 12th month
# of one district's run in each file.
MESSY_DISTRICT = {"Nyarugenge": "Nyarugenge Dist.", "Rwamagana": "Rwamagana "}
month_in_district = df.groupby("district").cumcount()

# ---------------------------------------------------------------------
# Partner A — ERP/financial-style export: region + revenue figure + a
# European DD/MM/YYYY date. Mirrors Module 1's "reg"/"rev" example.
# ---------------------------------------------------------------------
a = df[["district", "date", "value"]].copy()
a["reg"] = a["district"].where(
    ~((a["district"] == "Nyarugenge") & (month_in_district == 4)),
    MESSY_DISTRICT["Nyarugenge"],
)
a["date"] = a["date"].dt.strftime("%d/%m/%Y")
a = a.rename(columns={"value": "rev"})[["reg", "rev", "date"]]
a.to_csv(os.path.join(RAW_DIR, "partner_a_finance_export.csv"), index=False)

# ---------------------------------------------------------------------
# Partner B — survey-platform-style export (KoBo/ODK shape): region_name +
# collection_date in "D-Mon-YY" form + the two model features.
# ---------------------------------------------------------------------
b = df[["district", "date", "feature_1", "feature_2"]].copy()
b["region_name"] = b["district"].where(
    ~((b["district"] == "Rwamagana") & (month_in_district == 11)),
    MESSY_DISTRICT["Rwamagana"],
)
b["collection_date"] = b["date"].dt.strftime("%-d-%b-%y")
b = b[["region_name", "collection_date", "feature_1", "feature_2"]]
b.to_csv(os.path.join(RAW_DIR, "partner_b_survey_export.csv"), index=False)

# ---------------------------------------------------------------------
# Partner C — an already-tidy HDX/API-style pull: P-code-keyed, ISO
# dates, carries the indicator name and the outcome flag.
# ---------------------------------------------------------------------
c = df[["district_pcode", "date", "indicator", "outcome"]].copy()
c["date"] = c["date"].dt.strftime("%Y-%m-%d")
c.to_csv(os.path.join(RAW_DIR, "partner_c_hdx_pull.csv"), index=False)

# ---------------------------------------------------------------------
# COD-AB-style gazetteer — the authoritative district name -> P-code
# lookup used to join A and B onto a common key, per Module 4.
# ---------------------------------------------------------------------
gaz = pd.DataFrame(
    [{"district_name": d, "province": p, "district_pcode": pc} for p, d, pc, *_ in DISTRICTS]
)
gaz.to_csv(os.path.join(RAW_DIR, "cod_ab_gazetteer.csv"), index=False)

print("Wrote raw/partner_a_finance_export.csv, partner_b_survey_export.csv,")
print("      partner_c_hdx_pull.csv, and raw/cod_ab_gazetteer.csv")
print(f"Injected {int(((a['reg']==MESSY_DISTRICT['Nyarugenge']).sum()))} misspelled row(s) in Partner A")
print(f"Injected {int(((b['region_name']==MESSY_DISTRICT['Rwamagana']).sum()))} misspelled row(s) in Partner B")
print("This is SYNTHETIC practice data — see data/README.md.")
