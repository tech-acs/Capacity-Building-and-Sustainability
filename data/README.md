# Data

Every notebook in this repo runs against **synthetic** data by default, so a
new clone works with no downloads, no registration, and no waiting on a data
request. There are two ways to get it, and they agree on every number
because both are generated from the same seeded source (`_rwanda_synth.py`).

**Fast path — straight to the processed dataset**, for working through
Track 2 without first doing Track 1:

```bash
python3 data/make_sample_data.py
```

**Slow path — the realistic one**, three messy raw sources reconciled
through an actual Track 1 integration pipeline (notebooks
`notebooks/track1/module-01...` through `module-09...`), which is what a
real regional hub's data actually looks like before it's usable:

```bash
python3 data/make_track1_sources.py
# then work through the Track 1 notebooks in order; Module 9 publishes
# data/processed/track2_dataset.csv itself, from those raw files
```

Either path writes:

- `data/raw/synthetic_eicv_extract.csv` — a fabricated household-survey-shaped
  extract: 10 real Rwandan districts (across all 5 provinces), 24 months,
  a wellbeing-style `value`, and `feature_1`/`feature_2`/`outcome` columns
  for the Unit D modeling exercises. (Fast path only.)
- `data/raw/partner_a_finance_export.csv`, `partner_b_survey_export.csv`,
  `partner_c_hdx_pull.csv`, `cod_ab_gazetteer.csv` — the same underlying
  values, split into three inconsistently-shaped exports plus the P-code
  gazetteer that reconciles them, for Track 1 to integrate. Two rows carry a
  deliberately misspelled district name so Track 1 Module 4 has something
  real to catch. (Slow path only.)
- `data/processed/track2_dataset.csv` — the dataset every Track 2 notebook
  reads. Produced directly by the fast path, or published by Track 1's
  Module 9 pipeline from the raw sources above — numerically identical
  either way.
- `data/processed/admin_boundaries_synthetic.geojson` — one rectangle per
  district, in roughly the right part of the country, for Module 4's join
  and mapping exercises. (Fast path only; Track 1 doesn't currently
  regenerate this file.)

**None of the numbers here are real**, and the `district_pcode` values use an
obviously-fake `SIM-` prefix specifically so they can never be mistaken for a
real HDX `ADM2_PCODE`. Province and district names are real Rwandan
geography (that's just a fact, not a statistic); everything numeric is
`numpy.random` output.

## Swapping in real data

When you're ready to run this against the real thing, see Chapter 3 of the
course site for the full list of sources and access notes. Shortest path:

1. **Tabular data** — pull an extract from the [NISR Central Data
   Catalog](https://microdata.statistics.gov.rw/) (EICV, LFS, or census
   indicators), save it to `data/raw/`, and re-run the Module 1 notebook's
   load-and-clean cell against that file instead of
   `synthetic_eicv_extract.csv`. Rename its columns to match the schema
   above (`date`, `province`, `district`, `district_pcode`, `value`, ...) —
   the exact column names in a real extract depend on the survey round's own
   codebook, so this rename step is expected, not a bug.
2. **Boundaries** — download the real Rwanda administrative boundaries
   (COD-AB) from [HDX](https://data.humdata.org/dataset/2768bdfd-6486-4963-8e3d-e63149478eb4),
   save the GeoJSON/shapefile to `data/raw/`, and join on the real
   `ADM2_PCODE` column instead of this repo's `pcode_sim`.
3. Every notebook after that point is unchanged — the join key, column
   names, and chart code are all written against the schema, not the
   specific (synthetic) source.

For other African countries, other NSOs, WorldPop, World Bank, Afrobarometer,
and a guide to responsible web scraping as a last resort, see Chapter 3 of
the course site in full.
