# UN Regional Hub E-Learning Program — Track 1 & Track 2

One repository, two tracks, one way to use it: a readable course site
(served by GitHub Pages from `docs/`, with a Track 1 / Track 2 switcher in
the topbar) and the runnable companion notebooks for both tracks (a
Python + R pair per module, twenty pairs total) that a participant gets with
a single `git clone`. Point people at the site; the site's "Run it" links
and its Chapter 2 setup steps bring them straight back into this same repo.

- **Track 1 — Data Integration, Standards, Metadata & Quality.** Builds the
  discipline and the pipeline: ingest three inconsistent partner-style
  sources, harmonize them on P-codes and HXL tags, document, validate, and
  publish. Its Module 9 notebook writes `data/processed/track2_dataset.csv`
  directly — the literal input Track 2 assumes, not a narrated one.
- **Track 2 — Visualization, Analytic Hubs & Responsible AI.** Takes that
  published dataset from chart to interactive map to dashboard to forecast
  to a Responsible AI-governed analytic hub.

**Course site (GitHub Pages):** `https://seknewna.github.io/Capacity-Building-and-Sustainability/`
*(live once you push and enable Pages — see "Publishing the site" below)*

```
track2-course/
  docs/
    index.html              # the course site — Track 1 / Track 2 switcher, GitHub Pages serves this folder
  notebooks/
    track1/
      module-01-principles-data-integration/
        python.ipynb
        r.ipynb
      module-02-connecting-extracting-sources/ ...  # ten Track 1 modules
    module-01-visual-grammar-chart-selection/  ...  # ten Track 2 modules
  apps/
    streamlit_app.py        # Track 2 Python dashboard, Modules 5-6
    shiny_app.R              # Track 2 R dashboard, Modules 5-6
  data/
    make_sample_data.py      # fast path: straight to the processed dataset
    make_track1_sources.py    # slow path: Track 1's raw practice sources
    _rwanda_synth.py           # shared seeded generator both paths call
    README.md                   # what the data is, and how to swap in the real thing
  environment/
    requirements.txt          # pip install -r environment/requirements.txt (both tracks)
    install.R                  # Rscript environment/install.R (both tracks)
  generate_repo.py             # regenerates Track 2's notebooks from source
  generate_track1_notebooks.py  # regenerates Track 1's notebooks from source
```

## Quickstart

```bash
git clone https://github.com/seknewna/Capacity-Building-and-Sustainability.git
cd Capacity-Building-and-Sustainability

# 1. Python environment (one venv, both tracks)
python3 -m venv track2-env && source track2-env/bin/activate
pip install -r environment/requirements.txt
python3 -m ipykernel install --user --name track2 --display-name "Python (track2)"

# 2. R environment (optional — only needed for the r.ipynb notebooks and the dashboard apps)
Rscript environment/install.R

# 3a. Fast path — Track 2 only, straight to the processed dataset
python3 data/make_sample_data.py

# 3b. Slow path — do Track 1 first, the way a real cohort would
python3 data/make_track1_sources.py
# then work notebooks/track1/module-01... through module-09... in order;
# Module 9 publishes data/processed/track2_dataset.csv itself

# 4. Launch
jupyter lab notebooks/
```

Open any `python.ipynb` or `r.ipynb` and run top to bottom — every Track 2
module notebook loads `data/processed/track2_dataset.csv`, however you got
there in step 3. The course site's Chapter 2 (in either track) shows this
same sequence alongside required-package tables and a project-structure
reference.

## Publishing the site

1. Push this repo to `github.com/seknewna/Capacity-Building-and-Sustainability`
   (already the repo this checkout points at — no URL edits needed).
2. In **Settings → Pages**, set *Source* to **Deploy from a branch**, branch
   **main**, folder **`/docs`**. Save.
3. GitHub builds the site at
   `https://seknewna.github.io/Capacity-Building-and-Sustainability/` within
   a minute or two.

Every "Open on GitHub" / "Open in Colab" link in both tracks, the
`git clone` commands in both Chapter 2s, the topbar GitHub icon, and the
footer link are all templated from the single `REPO` config object near the
top of `docs/index.html`'s `<script>` block (`REPO.owner`, `REPO.name`,
`REPO.branch`) — already set to this repo. If you fork or rename the repo,
that's the one place to edit; every generated link updates from it.

## What's already run, and what isn't

The **Python notebooks are pre-executed**, in both tracks — clone the repo
and open one, and the output (tables, charts, maps, model results, or for
Track 1's Module 9, the actual published dataset) is already there. Re-run
them yourself to confirm, or after you've swapped in real data. They also
render with their output intact directly in GitHub's file browser and in
Colab (via the "Open in Colab" link on the course site), with no local setup
at all.

The **R notebooks are not pre-executed** (this repo was built in an
environment without a full R + tidyverse + sf + shiny + pointblank stack
installed). Every R cell has been syntax-checked with `Rscript` and mirrors
the equivalent, already-working Python cell line for line, but you'll want
to run them yourself the first time. If a folium/leaflet map doesn't render
in your notebook viewer, use `File → Trust Notebook`, a standard Jupyter
prompt for notebooks executed elsewhere.

## The dataset, and the handoff between tracks

Every Track 2 notebook runs out of the box against **synthetic** data —
real Rwandan province and district names, in a schema shaped like the real
NISR/HDX handoff, but every number is `numpy.random` output and every
P-code uses an obviously-fake `SIM-` prefix. There are two ways to produce
it, and they agree on every number because both are generated from the same
seeded source (`data/_rwanda_synth.py`):

- **Fast path**: `python3 data/make_sample_data.py` writes
  `data/processed/track2_dataset.csv` directly.
- **Slow path**: `python3 data/make_track1_sources.py` writes three
  inconsistent raw exports plus a P-code gazetteer; working through Track 1's
  ten notebooks culminates in Module 9's pipeline, which publishes that
  exact same file itself. Module 9's notebook even diffs its own output
  against the fast path's to prove it.

See `data/README.md` for exactly what's fabricated in both paths, and how
to point either one at a real NISR extract and the real HDX boundary file
instead — the join keys and column names are written against the schema,
not the specific source, so that swap doesn't touch the notebook code. For
the full list of African data sources this dataset generalizes to (other
national statistics offices, WorldPop, World Bank, Afrobarometer, and a
guide to responsible web scraping), see Track 2's Chapter 3 on the course
site.

## Module map

**Track 1 — Data Integration, Standards, Metadata & Quality**

| # | Module | Unit | Week |
|---|---|---|---|
| 1 | Principles of Data Integration & the Regional Data Landscape | A | 1 |
| 2 | Connecting to and Extracting Data from Multiple Sources (+ Extension) | A | 2 |
| 3 | Core Data Standards Used Across the UN System | B | 3 |
| 4 | Applying Standards in Practice — Harmonizing Multi-Source Regional Data | B | 4 |
| 5 | Metadata Fundamentals — Why Document Data | C | 5 |
| 6 | Building Metadata Catalogs & Data Dictionaries | C | 6 |
| 7 | Data Quality Frameworks & Dimensions | D | 7 |
| 8 | Automated Data Validation & Profiling in Python and R | D | 8 |
| 9 | Designing a Reproducible Data Integration Pipeline | E | 9 (part 1) |
| 10 | Data Governance, Responsibility & Sustainability of Integration Pipelines | E | 9 (part 2) |

**Track 2 — Visualization, Analytic Hubs & Responsible AI**

| # | Module | Unit | Week |
|---|---|---|---|
| 1 | Visual Grammar & Chart Selection | A | 1 |
| 2 | Static Charts in Python & R | A | 2 |
| 3 | Interactive Visualization | B | 3 |
| 4 | Geospatial Analysis & Mapping on P-codes | B | 4 |
| 5 | Dashboard Foundations | C | 5 |
| 6 | AI-Assisted Analytics Pattern | C | 6 |
| 7 | Forecasting Regional Time Series | D | 7 |
| 8 | Interpretable First Models | D | 7 |
| 9 | UN/UNESCO Responsible AI Frameworks & Ethical Impact Assessment | E | 8 |
| 10 | Bias, Fairness & Sustainability Audit | E | 8 |

Each notebook carries its own learning objectives, a "Your turn" exercise
matching the course site, and, where the module calls for it, a Responsible
AI or governance callback. In each track, two modules are template/
discussion-led rather than code-led (Track 1: Modules 3, 5, 7, 10; Track 2:
Modules 1, 9), in line with the course site. The site's Chapter 4 in each
track lists every module with a "Run it" link straight to its notebook pair.

## Word documents

Each track also has a standalone Word curriculum document (the original
competency-framework-style deliverable), generated separately and not part
of this git history — see the two `.docx` files delivered alongside this
repo, or regenerate them from `build.js` (Track 2) / `build1.js` (Track 1)
if you have the `docx` npm package installed.

## Regenerating everything

The whole `notebooks/` tree for each track is generated from source, so a
wording fix or a new module doesn't mean hand-editing JSON files directly:

```bash
python3 generate_repo.py                 # rewrites Track 2's 20 notebooks from the MODULES list
python3 generate_track1_notebooks.py     # rewrites Track 1's 20 notebooks from the MODULES list
python3 data/make_sample_data.py         # rebuild the fast-path sample data if you changed its shape
python3 data/make_track1_sources.py      # rebuild Track 1's raw sources if you changed their shape
```

Re-execute the Python notebooks after regenerating:

```bash
jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.kernel_name=track2 \
  notebooks/module-*/python.ipynb notebooks/track1/module-*/python.ipynb
```

If you edit `docs/index.html`'s module content, keep the module `num`
fields in its `UNITS` (Track 2) / `UNITS_T1` (Track 1) arrays in sync with
the matching `generate_*.py` script's `MODULES` list — the site's
`SLUG_BY_NUM` / `SLUG_BY_NUM_T1` maps rely on the same numbering to link to
the right notebook folder.

## License

MIT — see `LICENSE`. Course content adapted from the UN Regional Hub
E-Learning Program, Tracks 1 and 2.
