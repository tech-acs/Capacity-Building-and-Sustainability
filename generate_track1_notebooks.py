#!/usr/bin/env python3
"""
Generates the Track 1 notebooks: notebooks/track1/module-XX.../{python,r}.ipynb
Run once from the repo root:  python3 generate_track1_notebooks.py

Track 1's raw sources are data/raw/partner_a_finance_export.csv,
partner_b_survey_export.csv, partner_c_hdx_pull.csv, and cod_ab_gazetteer.csv
(see data/make_track1_sources.py). Module 9's pipeline notebook publishes
data/processed/track2_dataset.csv directly — the exact file Track 2 reads —
proving the handoff instead of just describing it.
"""
import itertools
import json
import os
import uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
_id_counter = itertools.count(1)

def _cell_id():
    return uuid.uuid5(uuid.NAMESPACE_OID, f"track1-cell-{next(_id_counter)}").hex[:8]

def md(text):
    return {"cell_type": "markdown", "id": _cell_id(), "metadata": {}, "source": text.splitlines(keepends=True)}

def code(text):
    return {"cell_type": "code", "id": _cell_id(), "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}

def notebook(cells, lang):
    if lang == "python":
        kernelspec = {"display_name": "Python (track2)", "language": "python", "name": "track2"}
        language_info = {"name": "python", "pygments_lexer": "ipython3",
                          "codemirror_mode": {"name": "ipython", "version": 3},
                          "file_extension": ".py", "mimetype": "text/x-python",
                          "nbconvert_exporter": "python", "version": "3.11"}
    else:
        kernelspec = {"display_name": "R", "language": "R", "name": "ir"}
        language_info = {"name": "R", "codemirror_mode": "r", "pygments_lexer": "r",
                          "file_extension": ".r", "mimetype": "text/x-r"}
    return {
        "cells": cells,
        "metadata": {"kernelspec": kernelspec, "language_info": language_info},
        "nbformat": 4,
        "nbformat_minor": 5,
    }

def write_nb(path, cells, lang):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(notebook(cells, lang), f, indent=1)
        f.write("\n")

def header(m):
    return md(
f"""# Module {m['num']}: {m['title']}

**Unit {m['unit_letter']} · Week {m['week']}** · Track 1 — Data Integration, Standards, Metadata & Quality

{m['overview']}

## Learning objectives

{chr(10).join(f"- {o}" for o in m['objectives'])}
"""
    )

def footer(m):
    parts = [f"## Your turn\n\n{m['exercise']}\n\n**Formative assessment.** {m['assessment']}"]
    if m.get("governance"):
        parts.append(f"## Governance / responsibility callback\n\n{m['governance']}")
    return md("\n\n".join(parts))

RAW_NOTE = md(
"""## Setup

This notebook reads the raw practice files in `../../../data/raw/`, built by
`data/make_track1_sources.py` — three partner-style exports shaped like a
real regional hub's source-system landscape (an ERP/financial export, a
survey-platform export, and an HDX-style pull), plus the P-code gazetteer
used to reconcile them. All four are **synthetic**; see `data/README.md`.
Run `python3 data/make_track1_sources.py` once from the repo root before
working through this notebook if those files aren't there yet."""
)

# ------------------------------------------------------------------
# MODULE CONTENT
# ------------------------------------------------------------------
MODULES = [
{
    "num": 1, "slug": "01-principles-data-integration", "unit_letter": "A", "week": 1,
    "title": "Principles of Data Integration & the Regional Data Landscape",
    "overview": "Before touching a connector or a merge, this module frames why regional hubs need to integrate data from multiple systems at all, and the vocabulary (ETL/ELT, batch/API) used for the rest of the track.",
    "objectives": [
        "Explain why regional hubs need to integrate data from multiple systems.",
        "Distinguish ETL from ELT, and batch integration from API-based integration.",
        "Map the source systems a typical regional hub relies on, and recognize the risk of parallel, unreconciled copies of the same data.",
    ],
    "needs_raw": False,
    "python": [
        md("## Lesson content\n\n"
           "- **What data integration is.** Consolidating data from multiple systems — ERP/financial exports, survey "
           "platforms (KoBoToolbox, ODK), partner reports, and UN data portals such as HDX — into a single, "
           "analysis-ready store instead of scattered files.\n"
           "- **ETL vs. ELT.** Where the transformation happens, and why it matters for a small regional-hub team "
           "without dedicated data-engineering infrastructure.\n"
           "- **Batch vs. API-based integration.** Periodic file drops and scheduled pulls, versus near-real-time "
           "pulls that depend on source-system uptime and access.\n"
           "- **The \"single source of truth\" problem.** What goes wrong when finance, M&E, and a regional office "
           "each keep their own slightly different copy of the same indicator — and why integration, not just "
           "visualization, is where that gets fixed."),
        code(
"""import pandas as pd

# A minimal, self-contained illustration of the technique this module is
# really teaching: combining exports with inconsistent column names while
# preserving *provenance* — which source every row came from. Module 2
# brings in this course's real multi-source files; this cell keeps the
# technique isolated from that complexity.
partner_a = pd.DataFrame({"reg": ["Gasabo", "Huye"], "rev": [41.2, 38.9]})
partner_b = pd.DataFrame({"region_name": ["Musanze", "Rubavu"], "rev": [44.1, 36.7]})

rename_map = {"reg": "region", "region_name": "region"}
frames = []
for name, part in [("PartnerA", partner_a), ("PartnerB", partner_b)]:
    part = part.rename(columns=rename_map)
    part["source_file"] = name          # provenance: keep track of where every row came from
    frames.append(part)

combined = pd.concat(frames, ignore_index=True)
combined"""
        ),
        md("### Mapping exercise\n\n"
           "A typical regional hub's source-system landscape: an ERP/financial system, a survey platform, partner "
           "Excel submissions, and HDX/OCHA datasets. This track's own practice data (Module 2 onward) mirrors "
           "exactly this landscape — a finance export, a survey export, and an HDX-style pull."),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages."),
        code(
"""library(tidyverse)

# A minimal, self-contained illustration of the technique this module is
# really teaching: combining exports with inconsistent column names while
# preserving *provenance* — which source every row came from.
partner_a <- tibble(reg = c("Gasabo", "Huye"), rev = c(41.2, 38.9))
partner_b <- tibble(region_name = c("Musanze", "Rubavu"), rev = c(44.1, 36.7))

combined <- bind_rows(
  PartnerA = partner_a %>% rename(region = reg),
  PartnerB = partner_b %>% rename(region = region_name),
  .id = "source_file"          # provenance: keep track of where every row came from
)
combined"""
        ),
    ],
    "exercise": "Combine two provided partner exports with inconsistent column names into one dataframe, preserving a `source_file` provenance column, in both Python and R.",
    "assessment": "Short quiz (ETL vs. ELT, batch vs. API scenarios) plus the submitted merged dataframe. Rubric checks no rows were silently dropped and provenance is preserved.",
},
{
    "num": 2, "slug": "02-connecting-extracting-sources", "unit_letter": "A", "week": 2,
    "title": "Connecting to and Extracting Data from Multiple Sources",
    "overview": "Introduces this track's real, three-source practice dataset: a SQL-style extraction from a local database standing in for the hub's ERP system, and a REST/HDX-style pull, run against files instead of the live internet so the notebook is reliable to re-run anywhere. Closes with the reverse pattern — publishing a hub's own dataset as a small API.",
    "objectives": [
        "Query a relational database with SQL from Python and R.",
        "Parse a REST/JSON-shaped extract the way an HDX or HAPI pull would arrive.",
        "Handle extraction failure gracefully instead of letting a script fail silently.",
    ],
    "needs_raw": True,
    "python": [
        md("## Lesson content\n\n"
           "- **SQL basics for extraction.** `SELECT`, `WHERE`, enough to pull exactly the slice of a database "
           "table a hub needs, run from Python via `sqlite3`.\n"
           "- **Calling REST APIs / pulling CODs from HDX.** In production this is `requests` against a live "
           "endpoint (HDX Python API client, or direct HAPI REST calls); this notebook reads the equivalent "
           "already-downloaded JSON/CSV shape so it stays reproducible offline.\n"
           "- **Handling failure gracefully.** Timeouts, rate limits, and expired credentials are the norm once "
           "extraction is automated — always log and surface failures rather than let a script fail silently."),
        code(
"""import sqlite3
import pandas as pd

# --- SQL extraction, simulating the hub's ERP/financial system ---
partner_a = pd.read_csv("../../../data/raw/partner_a_finance_export.csv")
conn = sqlite3.connect(":memory:")
partner_a.to_sql("finance_export", conn, index=False)

db_df = pd.read_sql(
    "SELECT reg, rev, date FROM finance_export WHERE rev >= ?",
    conn, params=[30.0],
)
conn.close()
print(f"{len(db_df):,} rows extracted via SQL (rev >= 30.0)")
db_df.head()"""
        ),
        code(
"""# --- "API" extraction, simulating an HDX/HAPI-style pull ---
# In production: requests.get(HAPI_URL, params=..., timeout=30).json()
# Here: the equivalent already-pulled shape, read the same defensive way.
def fetch_hdx_style(path, timeout_ok=True):
    if not timeout_ok:
        raise TimeoutError("simulated HDX endpoint timeout")
    return pd.read_csv(path)

try:
    api_df = fetch_hdx_style("../../../data/raw/partner_c_hdx_pull.csv")
    print(f"{len(api_df):,} rows extracted via the HDX-style pull")
except TimeoutError as e:
    print(f"Extraction failed, logged for retry: {e}")   # never fail silently
    api_df = pd.DataFrame()

api_df.head()"""
        ),
        md(
"""### Module 2 Extension — worked example: serving integrated data as an API

*Optional advanced pattern, completes the loop with Module 9's "publish" step.* The rest of this module covers
consuming other people's APIs; the reverse is exposing the hub's own harmonized, validated dataset (Module 9's
output) as a small REST API with **FastAPI**, so a Track 2 dashboard, a partner system, or a colleague's
notebook can request exactly the slice it needs, always the latest published version, instead of everyone
keeping their own downloaded CSV that quickly goes stale. This code is illustrative, it starts a server, so it
is shown here rather than executed inline; save it as `api.py` and run it from a terminal with `uvicorn`.

```python
# api.py -- run with: uvicorn api:app --reload
from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI(title="Regional Hub Data API", version="1.0")

def load_latest():
    return pd.read_csv("../../../data/processed/track2_dataset.csv")

@app.get("/districts")
def list_districts():
    df = load_latest()
    return df[["district_pcode", "district"]].drop_duplicates().to_dict(orient="records")

@app.get("/districts/{pcode}")
def get_district(pcode: str):
    df = load_latest()
    result = df[df["district_pcode"] == pcode]
    if result.empty:
        raise HTTPException(status_code=404, detail="P-code not found: " + pcode)
    return result.to_dict(orient="records")

# Interactive docs are generated automatically at /docs
```"""
        ),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages."),
        code(
"""library(DBI)
library(RSQLite)
library(readr)
library(dplyr)

# --- SQL extraction, simulating the hub's ERP/financial system ---
partner_a <- read_csv("../../../data/raw/partner_a_finance_export.csv", show_col_types = FALSE)
con <- dbConnect(SQLite(), ":memory:")
dbWriteTable(con, "finance_export", partner_a)

db_df <- dbGetQuery(con, "SELECT reg, rev, date FROM finance_export WHERE rev >= ?", params = list(30.0))
dbDisconnect(con)
cat(nrow(db_df), "rows extracted via SQL (rev >= 30.0)\\n")
head(db_df)"""
        ),
        code(
"""# --- "API" extraction, simulating an HDX/HAPI-style pull ---
fetch_hdx_style <- function(path, timeout_ok = TRUE) {
  if (!timeout_ok) stop("simulated HDX endpoint timeout")
  read_csv(path, show_col_types = FALSE)
}

api_df <- tryCatch(
  fetch_hdx_style("../../../data/raw/partner_c_hdx_pull.csv"),
  error = function(e) {
    message("Extraction failed, logged for retry: ", conditionMessage(e))  # never fail silently
    tibble()
  }
)
head(api_df)"""
        ),
        md("### Module 2 Extension — worked example: serving integrated data as an API\n\n"
           "The R equivalent of FastAPI is **plumber**: ordinary functions turned into HTTP endpoints via "
           "lightweight `#*` annotations. Illustrative only — run from a terminal, not inline here."),
        code(
'''# api.R — run with: plumber::pr("api.R") |> plumber::pr_run(port = 8000)  (not executed here)
library(plumber)
library(dplyr)
library(readr)

load_latest <- function() {
  read_csv("../../../data/processed/track2_dataset.csv", show_col_types = FALSE)
}

#* List all district P-codes and names currently published
#* @get /districts
function() {
  load_latest() %>% distinct(district_pcode, district)
}

#* Return published records for a single district, looked up by P-code
#* @param pcode The district P-code
#* @get /districts/<pcode>
function(pcode, res) {
  result <- load_latest() %>% filter(district_pcode == pcode)
  if (nrow(result) == 0) {
    res$status <- 404
    return(list(detail = paste0("P-code '", pcode, "' not found")))
  }
  result
}

# Interactive docs are generated automatically at /__docs__/'''
        ),
    ],
    "exercise": "Extract the finance export via a SQL query and the HDX-style pull via the file-based simulation above, in both Python and R, and confirm the failure-handling branch logs rather than crashes when `timeout_ok=False`.",
    "assessment": "Submitted script plus resulting extracted tables, graded on correct filtering, and on graceful (not silent) handling of the simulated timeout.",
    "governance": "The discussion prompt for the API extension: what access control would this API need before it could be exposed outside the hub's internal network — and which Module 10 governance practices (licensing, sensitive-field review, an accountable owner) apply just as much to an API endpoint as to a shared CSV file?",
},
{
    "num": 3, "slug": "03-core-data-standards", "unit_letter": "B", "week": 3,
    "title": "Core Data Standards Used Across the UN System",
    "overview": "A conceptual module: which standard applies to a given regional data type, and a working-level fluency in HXL, P-codes/CODs, IATI, and SDMX before Module 4 applies them.",
    "objectives": [
        "Identify which standard applies to a given regional data type: geographic, humanitarian needs, aid flows, or official statistics.",
        "Explain HXL, P-codes/CODs, IATI, and SDMX at a working level.",
    ],
    "needs_raw": False,
    "python": [
        md("## Lesson content\n\n"
           "**HXL — Humanitarian Exchange Language.** A lightweight hashtag-tagging convention for humanitarian "
           "datasets: a second header row of hashtags (`#adm1`, `#affected`, `#org`, `#sector`, `#date`, and about "
           "30 other core hashtags with optional attributes) that machines can read without requiring the source "
           "organization to change tools or workflows. The most-used hashtags in practice are `#affected`, "
           "`#country`, `#date`, `#meta`, and `#loc`.\n\n"
           "**P-codes and Common Operational Datasets (CODs).** CODs are OCHA-maintained, 'best available' "
           "authoritative reference datasets, most importantly administrative boundaries annotated with place "
           "codes (P-codes) at each level (adm0 country, adm1 region/province, adm2 district, and so on) and "
           "accompanied by a gazetteer. P-codes are the standard join key for combining datasets by location, "
           "replacing fragile name-matching — the same pitfall flagged in the Track 2 geospatial module, solved "
           "properly here at the integration stage.\n\n"
           "**IATI — International Aid Transparency Initiative Standard.** An XML-based standard for publishing "
           "development and humanitarian activity data, objectives, financial flows, sectors, and results, used "
           "by over 1,700 organizations. Relevant to a regional hub tracking donor funding flowing into its "
           "region from multiple agencies.\n\n"
           "**SDMX — Statistical Data and Metadata eXchange.** An ISO standard (17369:2013), endorsed by the UN "
           "Statistical Commission in 2008 as the preferred standard for exchanging statistical data and "
           "metadata. Used for reporting SDG indicators and official statistics in a form that stays comparable "
           "across countries and time.\n\n"
           "**Baseline ISO standards.** ISO 3166 (country codes) and ISO 8601 (date format, `YYYY-MM-DD`) are "
           "small but critical — most cross-source join failures and date-parsing bugs in regional data trace "
           "back to skipping these."),
        code(
"""import pandas as pd
from io import StringIO

# A tiny taste of reading HXL-tagged data: the second row carries the
# hashtags, not the header row — and a well-written reader keys off the
# hashtag, not the column's position, so reordering columns doesn't break it.
hxl_csv = StringIO(
    "district,district_pcode,value\\n"
    "#adm2+name,#adm2+code,#value\\n"
    "Gasabo,SIM-GAS,41.2\\n"
    "Huye,SIM-HUY,38.9\\n"
)
raw = pd.read_csv(hxl_csv)
hashtags = raw.iloc[0].to_dict()
data = raw.iloc[1:].reset_index(drop=True)
print("Column -> hashtag map:", hashtags)
data"""
        ),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages."),
        code(
"""library(readr)

# A tiny taste of reading HXL-tagged data: the second row carries the
# hashtags, not the header row.
hxl_text <- "district,district_pcode,value
#adm2+name,#adm2+code,#value
Gasabo,SIM-GAS,41.2
Huye,SIM-HUY,38.9"

raw <- read_csv(hxl_text, show_col_types = FALSE)
hashtags <- as.list(raw[1, ])
data <- raw[-1, ]
print(hashtags)
data"""
        ),
    ],
    "exercise": "For five provided regional datasets (a needs-assessment export, an admin-boundary shapefile, a donor funding report, an SDG indicator table, and a partner survey), identify which standard(s) apply and why.",
    "assessment": "Standards-matching quiz plus a short written justification per dataset, graded on correct standard identification and reasoning.",
},
{
    "num": 4, "slug": "04-applying-standards-harmonizing", "unit_letter": "B", "week": 4,
    "title": "Applying Standards in Practice — Harmonizing Multi-Source Regional Data",
    "overview": "The first module where all three of this track's raw sources meet: joined on P-codes rather than names, dates normalized to ISO 8601, and a HXL tag row added to the published intermediate file.",
    "objectives": [
        "Add HXL hashtags to a raw dataset.",
        "Join disparate regional datasets using P-codes instead of place names.",
        "Normalize dates and country/district codes to ISO standards, and validate join coverage rather than silently dropping unmatched rows.",
    ],
    "needs_raw": True,
    "python": [
        md("## Lesson content\n\n"
           "- Adding a HXL hashtag row to a dataset programmatically, and reading HXL-tagged data back in a way "
           "that's robust to column reordering (because the hashtag, not the column position, carries the "
           "meaning).\n"
           "- Joining on P-codes instead of district names: looking up the correct P-code for each row from the "
           "gazetteer, then joining as an exact key, eliminating the silent mismatches that name-based joins "
           "produce (the same failure mode flagged, but not yet solved, in the Track 2 mapping module).\n"
           "- Normalizing dates to ISO 8601 before any merge, so a later join doesn't fail because one source "
           "used `01/02/2025` and another used `2-Jan-25` — exactly the two formats Partner A and Partner B use "
           "here.\n"
           "- Validating coverage after every harmonization step: how many rows failed to match a P-code, and "
           "why. A harmonized dataset that silently drops unmatched rows is a data-quality problem masquerading "
           "as a successful join."),
        code(
"""import pandas as pd

gaz = pd.read_csv("../../../data/raw/cod_ab_gazetteer.csv")

a = pd.read_csv("../../../data/raw/partner_a_finance_export.csv")
b = pd.read_csv("../../../data/raw/partner_b_survey_export.csv")

# --- Coverage BEFORE any correction: how many rows fail to match a
#     district name exactly as the source spelled it? ---
unmatched_a_raw = a[~a["reg"].isin(gaz["district_name"])]
unmatched_b_raw = b[~b["region_name"].isin(gaz["district_name"])]
print(f"Partner A: {len(unmatched_a_raw)} row(s) unmatched before correction")
print(f"Partner B: {len(unmatched_b_raw)} row(s) unmatched before correction")
if len(unmatched_a_raw):
    print("  e.g.", unmatched_a_raw['reg'].unique())
if len(unmatched_b_raw):
    print("  e.g.", unmatched_b_raw['region_name'].unique())"""
        ),
        code(
"""# --- Fix: a small, reviewed alias map for known spelling variants,
#     plus whitespace stripping. Flagged and corrected, never dropped. ---
ALIASES = {"Nyarugenge Dist.": "Nyarugenge", "Rwamagana ": "Rwamagana"}

a["reg"] = a["reg"].str.strip().replace(ALIASES)
b["region_name"] = b["region_name"].str.strip().replace(ALIASES)

still_unmatched = pd.concat([
    a[~a["reg"].isin(gaz["district_name"])],
    b[~b["region_name"].isin(gaz["district_name"])],
])
print(f"Still unmatched after alias correction: {len(still_unmatched)} row(s)")"""
        ),
        code(
"""# --- Normalize both sources' dates to ISO 8601 and attach P-codes ---
a["date"] = pd.to_datetime(a["date"], format="%d/%m/%Y")
b["date"] = pd.to_datetime(b["collection_date"], format="%d-%b-%y")

a = a.merge(gaz, left_on="reg", right_on="district_name", how="left")
b = b.merge(gaz, left_on="region_name", right_on="district_name", how="left")

print("Partner A date range:", a["date"].min().date(), "to", a["date"].max().date())
a[["district_name", "district_pcode", "date", "rev"]].head()"""
        ),
        code(
"""# --- Add a HXL tag row and publish the harmonized intermediate file ---
harmonized = a[["district_name", "district_pcode", "date", "rev"]].rename(
    columns={"district_name": "district", "rev": "value"}
)
harmonized["date"] = harmonized["date"].dt.strftime("%Y-%m-%d")

hxl_row = pd.DataFrame([{
    "district": "#adm2+name", "district_pcode": "#adm2+code",
    "date": "#date", "value": "#value+funding",
}])
hxl_tagged = pd.concat([hxl_row, harmonized], ignore_index=True)
hxl_tagged.to_csv("../../../data/processed/harmonized_regional_data.csv", index=False)
print(f"Wrote {len(harmonized):,} rows (plus 1 HXL tag row) to harmonized_regional_data.csv")"""
        ),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages."),
        code(
"""library(tidyverse)

gaz <- read_csv("../../../data/raw/cod_ab_gazetteer.csv", show_col_types = FALSE)
a <- read_csv("../../../data/raw/partner_a_finance_export.csv", show_col_types = FALSE)
b <- read_csv("../../../data/raw/partner_b_survey_export.csv", show_col_types = FALSE)

unmatched_a_raw <- a %>% filter(!reg %in% gaz$district_name)
unmatched_b_raw <- b %>% filter(!region_name %in% gaz$district_name)
cat("Partner A:", nrow(unmatched_a_raw), "row(s) unmatched before correction\\n")
cat("Partner B:", nrow(unmatched_b_raw), "row(s) unmatched before correction\\n")"""
        ),
        code(
"""ALIASES <- c("Nyarugenge Dist." = "Nyarugenge", "Rwamagana " = "Rwamagana")

a <- a %>% mutate(reg = recode(str_trim(reg), !!!ALIASES))
b <- b %>% mutate(region_name = recode(str_trim(region_name), !!!ALIASES))

still_unmatched <- bind_rows(
  a %>% filter(!reg %in% gaz$district_name),
  b %>% filter(!region_name %in% gaz$district_name)
)
cat("Still unmatched after alias correction:", nrow(still_unmatched), "row(s)\\n")"""
        ),
        code(
"""a <- a %>%
  mutate(date = as.Date(date, format = "%d/%m/%Y")) %>%
  left_join(gaz, by = c("reg" = "district_name"))

b <- b %>%
  mutate(date = as.Date(collection_date, format = "%d-%b-%y")) %>%
  left_join(gaz, by = c("region_name" = "district_name"))

head(a %>% select(district_pcode, date, rev))"""
        ),
        code(
"""harmonized <- a %>%
  transmute(district = reg, district_pcode, date = format(date, "%Y-%m-%d"), value = rev)

hxl_row <- tibble(district = "#adm2+name", district_pcode = "#adm2+code",
                   date = "#date", value = "#value+funding")
hxl_tagged <- bind_rows(hxl_row, harmonized)
write_csv(hxl_tagged, "../../../data/processed/harmonized_regional_data.csv")
cat("Wrote", nrow(harmonized), "rows (plus 1 HXL tag row) to harmonized_regional_data.csv\\n")"""
        ),
    ],
    "exercise": "Confirm both misspelled rows (one in Partner A, one in Partner B) are caught by the before/after unmatched-row check, then extend the harmonization to also bring in Partner C's `indicator` and `outcome` columns, joined on `district_pcode` and `date`.",
    "assessment": "Submitted harmonized, HXL-tagged CSV, graded on join correctness (unmatched rows flagged, not dropped), correct hashtags, and ISO-format dates.",
},
{
    "num": 5, "slug": "05-metadata-fundamentals", "unit_letter": "C", "week": 5,
    "title": "Metadata Fundamentals — Why Document Data",
    "overview": "A conceptual module: the three types of metadata, what goes wrong without it, and the core standards (Dublin Core, DDI, DCAT) used to structure it.",
    "objectives": [
        "Define metadata and its three types.",
        "Explain the risks an undocumented regional dataset creates.",
        "Describe the core standards used to structure metadata: Dublin Core, DDI, DCAT.",
    ],
    "needs_raw": False,
    "python": [
        md("## Lesson content\n\n"
           "- **Three types of metadata.** Descriptive (what is this: title, description, keywords), structural "
           "(how is it organized: columns, relationships between files), and administrative (how was it made and "
           "who owns it: source, license, collection method, update frequency, owner).\n"
           "- **What goes wrong without metadata.** Nobody after the original author can assess whether a "
           "dataset is still fit for use, provenance gets lost within a few handovers, and undocumented "
           "sensitive fields go unnoticed until they cause a data-protection incident — a direct link forward to "
           "the Track 2 Responsible AI modules.\n"
           "- **Dublin Core.** 15 general-purpose elements (title, creator, subject, description, date, format, "
           "source, language, and others), a fast, good-enough baseline for describing almost any dataset.\n"
           "- **DDI (Data Documentation Initiative).** A richer standard purpose-built for survey and statistical "
           "microdata, capturing variables, codebooks, and methodology in detail.\n"
           "- **DCAT (Data Catalog Vocabulary).** The standard used to describe datasets in a catalog so they can "
           "be discovered and compared — effectively what HDX itself runs on (HDX is built on CKAN, whose "
           "dataset metadata schema is DCAT-aligned): title, tags, organization, location, license, update "
           "frequency, and methodology notes per dataset.\n"
           "- **HXL's `#meta` hashtag.** The lightest-weight option: inline, per-column metadata for humanitarian "
           "datasets that don't warrant a full separate catalog record."),
        code(
"""# A Dublin-Core-style metadata record for this track's harmonized output —
# the fast baseline described above, filled in by hand.
metadata_record = {
    "title": "Harmonized Regional Wellbeing Indicator",
    "creator": "Regional Hub M&E Unit",
    "subject": ["district wellbeing", "regional monitoring"],
    "description": "Monthly wellbeing indicator by district, harmonized from three partner sources.",
    "date": "2023-01 to 2024-12",
    "format": "text/csv",
    "source": "Partner A finance export; Partner B survey export; Partner C HDX-style pull",
    "language": "en",
}
metadata_record"""
        ),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages."),
        code(
"""metadata_record <- list(
  title = "Harmonized Regional Wellbeing Indicator",
  creator = "Regional Hub M&E Unit",
  subject = c("district wellbeing", "regional monitoring"),
  description = "Monthly wellbeing indicator by district, harmonized from three partner sources.",
  date = "2023-01 to 2024-12",
  format = "text/csv",
  source = "Partner A finance export; Partner B survey export; Partner C HDX-style pull",
  language = "en"
)
metadata_record"""
        ),
    ],
    "exercise": "Given an undocumented CSV, write a metadata record covering the Dublin Core core elements plus source, collection method, and update frequency.",
    "assessment": "Submitted metadata record, peer-reviewed against a completeness checklist.",
},
{
    "num": 6, "slug": "06-metadata-catalogs-dictionaries", "unit_letter": "C", "week": 6,
    "title": "Building Metadata Catalogs & Data Dictionaries",
    "overview": "Turns Module 5's concepts into code: an auto-generated data dictionary as a fast starting point, and a lightweight hub-wide catalog entry, both built from the Module 4 harmonized output.",
    "objectives": [
        "Generate a data dictionary programmatically from a dataframe.",
        "Structure a lightweight dataset catalog for a regional hub.",
        "Read HDX's own dataset metadata fields as a worked real-world example.",
    ],
    "needs_raw": False,
    "python": [
        md("## Lesson content\n\n"
           "- Auto-generating a data dictionary — column name, data type, % missing, number of unique values, "
           "and a placeholder for a human-written description — as a fast starting point that a human then "
           "reviews and completes, rather than writing one from scratch.\n"
           "- Structuring a simple hub-wide catalog: one row per dataset covering title, source, update "
           "frequency, standard applied (HXL/P-code), owner, and sensitivity level, so staff can find and assess "
           "a dataset before reusing it.\n"
           "- HDX's dataset metadata fields (title, tags, organization, location, license, update frequency, "
           "methodology) as a worked reference participants can adapt for an internal, non-public catalog."),
        code(
"""import pandas as pd

def build_data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "column": df.columns,
        "dtype": [str(t) for t in df.dtypes],
        "pct_missing": [round(df[c].isna().mean() * 100, 1) for c in df.columns],
        "n_unique": [df[c].nunique() for c in df.columns],
        "description": ["" for _ in df.columns],   # filled in by hand after review
    })

harmonized = pd.read_csv("../../../data/processed/harmonized_regional_data.csv", skiprows=[1])  # skip HXL row
dictionary = build_data_dictionary(harmonized)
dictionary.to_csv("../../../data/processed/harmonized_regional_data_DICTIONARY.csv", index=False)
dictionary"""
        ),
        code(
"""catalog_entry = pd.DataFrame([{
    "title": "Harmonized Regional Wellbeing Indicator", "source": "Partner A/B/C + HDX-style gazetteer",
    "update_frequency": "Monthly", "standard_applied": "HXL, P-codes",
    "owner": "Regional Hub M&E Unit", "sensitivity": "Internal use only",
}])
catalog_entry"""
        ),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages."),
        code(
"""library(tidyverse)

build_data_dictionary <- function(df) {
  tibble(
    column = names(df),
    dtype = map_chr(df, ~ class(.x)[1]),
    pct_missing = map_dbl(df, ~ round(mean(is.na(.x)) * 100, 1)),
    n_unique = map_int(df, ~ n_distinct(.x)),
    description = ""            # filled in by hand after review
  )
}

harmonized <- read_csv("../../../data/processed/harmonized_regional_data.csv", skip = 1, show_col_types = FALSE)
dictionary <- build_data_dictionary(harmonized)
write_csv(dictionary, "../../../data/processed/harmonized_regional_data_DICTIONARY.csv")
dictionary"""
        ),
        code(
"""catalog_entry <- tibble(
  title = "Harmonized Regional Wellbeing Indicator", source = "Partner A/B/C + HDX-style gazetteer",
  update_frequency = "Monthly", standard_applied = "HXL, P-codes",
  owner = "Regional Hub M&E Unit", sensitivity = "Internal use only"
)
catalog_entry"""
        ),
    ],
    "exercise": "Auto-generate a data dictionary for the Module 4 harmonized dataset, complete the description column by hand, and add a catalog entry for it to a running hub catalog.",
    "assessment": "Submitted data dictionary plus catalog entry, graded on completeness of fields and accuracy of the hand-written descriptions.",
},
{
    "num": 7, "slug": "07-data-quality-frameworks", "unit_letter": "D", "week": 7,
    "title": "Data Quality Frameworks & Dimensions",
    "overview": "A conceptual module built around the UN National Quality Assurance Framework (NQAF): naming and applying its core dimensions to assess a real regional dataset.",
    "objectives": [
        "Name and define the core data-quality dimensions used in the UN NQAF.",
        "Apply the framework to assess a real regional dataset.",
    ],
    "needs_raw": False,
    "python": [
        md("## Lesson content\n\n"
           "The **UN National Quality Assurance Framework (NQAF) Manual**, adopted by the UN Statistical "
           "Commission in 2019, sets out a coherent, holistic quality-management system for official statistics "
           "— and the same dimensions translate well to non-statistical regional operational data with light "
           "adaptation. Core dimensions and the question each one answers for a regional dataset:\n\n"
           "- **Accuracy & reliability** — does the data correctly represent what it claims to measure, and "
           "would a repeat collection produce a consistent result?\n"
           "- **Timeliness & punctuality** — is this the most recent available round, and was it released when "
           "it was supposed to be?\n"
           "- **Accessibility & clarity** — can the intended users actually find, obtain, and understand this "
           "dataset without help from its creator?\n"
           "- **Coherence & comparability** — does it agree with related datasets, and can it be compared across "
           "regions or time periods?\n"
           "- **Relevance** — does it actually answer the questions decision-makers in the region are asking?\n"
           "- **Completeness** — are all expected regions/periods/categories present, and are gaps documented "
           "rather than silently missing?\n\n"
           "Data quality and data responsibility are linked, not separate concerns: an inaccurate or incomplete "
           "dataset used confidently can cause as much harm in a humanitarian response as a mishandled sensitive "
           "one — a theme picked up again in Module 10 and in Track 2's Responsible AI unit."),
        code(
"""import pandas as pd

# Score the Module 4 harmonized dataset against each NQAF dimension,
# 1-5, with a one-line justification — the hands-on exercise below.
scorecard = pd.DataFrame([
    {"dimension": "Accuracy & reliability", "score": 4, "justification": "Values fall in a plausible range; not independently re-verified against source systems."},
    {"dimension": "Timeliness & punctuality", "score": 5, "justification": "Monthly series is current through the latest published month."},
    {"dimension": "Accessibility & clarity", "score": 3, "justification": "HXL row helps machines; a human-readable data dictionary (Module 6) is still needed alongside it."},
    {"dimension": "Coherence & comparability", "score": 4, "justification": "All three sources agree once joined on P-code; no cross-source conflicts found after harmonization."},
    {"dimension": "Relevance", "score": 4, "justification": "Tracks the wellbeing indicator the regional M&E unit actually reports on."},
    {"dimension": "Completeness", "score": 4, "justification": "2 of 240 rows required an alias correction before joining; 0 rows missing after correction."},
])
scorecard"""
        ),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages."),
        code(
"""library(tibble)

scorecard <- tribble(
  ~dimension, ~score, ~justification,
  "Accuracy & reliability", 4, "Values fall in a plausible range; not independently re-verified against source systems.",
  "Timeliness & punctuality", 5, "Monthly series is current through the latest published month.",
  "Accessibility & clarity", 3, "HXL row helps machines; a human-readable data dictionary (Module 6) is still needed alongside it.",
  "Coherence & comparability", 4, "All three sources agree once joined on P-code; no cross-source conflicts found after harmonization.",
  "Relevance", 4, "Tracks the wellbeing indicator the regional M&E unit actually reports on.",
  "Completeness", 4, "2 of 240 rows required an alias correction before joining; 0 rows missing after correction."
)
scorecard"""
        ),
    ],
    "exercise": "Score a provided messy regional dataset against each NQAF dimension on a 1-5 scale, with a one-line justification per dimension.",
    "assessment": "Submitted quality scorecard, graded on realistic, defensible scoring (not uniformly high or low) and specific justifications.",
},
{
    "num": 8, "slug": "08-automated-validation-profiling", "unit_letter": "D", "week": 8,
    "title": "Automated Data Validation & Profiling in Python and R",
    "overview": "Codifies Module 7's quality dimensions as re-runnable rules with pandera, so every pipeline refresh is checked the same way automatically, and failing rows are flagged for review rather than silently dropped.",
    "objectives": [
        "Write automated, re-runnable validation rules: schema, ranges, and referential integrity against a P-code gazetteer.",
        "Generate an automated data-profiling first pass, and handle failures by flagging rows for review, never silently dropping them.",
    ],
    "needs_raw": False,
    "python": [
        md("## Lesson content\n\n"
           "- **Why codify validation.** Manual eyeballing doesn't scale once a pipeline refreshes monthly or "
           "more often — encoding the Module 7 quality checks as rules means every refresh is checked the same "
           "way, automatically.\n"
           "- **pandera** for schema, range, and uniqueness checks defined declaratively against a dataframe "
           "(the R equivalent is `pointblank`, with a human-readable pass/fail report; shown in the R notebook "
           "for reference, not executed inline here since this repo doesn't install the full R stack — see the "
           "root README).\n"
           "- **Handling failures responsibly.** Failing rows should be flagged and routed for review, never "
           "silently dropped — dropping bad rows quietly turns a data-quality problem into a data-completeness "
           "problem nobody knows about."),
        code(
"""import pandera.pandas as pa
from pandera.pandas import Column, Check
import pandas as pd

gazetteer_codes = set(pd.read_csv("../../../data/raw/cod_ab_gazetteer.csv")["district_pcode"])

schema = pa.DataFrameSchema({
    "district_pcode": Column(str, Check.isin(gazetteer_codes), nullable=False),
    "value": Column(float, Check.ge(0)),
    "date": Column(str, Check.str_matches(r"^\\d{4}-\\d{2}-\\d{2}$")),
})

df = pd.read_csv("../../../data/processed/harmonized_regional_data.csv", skiprows=[1])  # skip the HXL row
try:
    schema.validate(df, lazy=True)
    print("All validation checks passed.")
except pa.errors.SchemaErrors as err:
    print(err.failure_cases)   # flagged for review — not silently dropped
    err.failure_cases.to_csv("../../../data/processed/validation_failures.csv", index=False)"""
        ),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages. "
           "This R cell mirrors the pandera checks with `pointblank`; it is syntax-checked but not executed in "
           "this repo (see the root README for why)."),
        code(
"""library(pointblank)
library(readr)

gazetteer_codes <- read_csv("../../../data/raw/cod_ab_gazetteer.csv", show_col_types = FALSE)$district_pcode
df <- read_csv("../../../data/processed/harmonized_regional_data.csv", skip = 1, show_col_types = FALSE)

agent <- create_agent(df) %>%
  col_vals_in_set(district_pcode, set = gazetteer_codes) %>%
  col_vals_gte(value, 0) %>%
  col_vals_regex(date, regex = "^\\\\d{4}-\\\\d{2}-\\\\d{2}$") %>%
  interrogate()

get_agent_report(agent)                 # human-readable pass/fail report
write_csv(get_data_extracts(agent, 1), "../../../data/processed/validation_failures.csv")  # flagged, not dropped"""
        ),
    ],
    "exercise": "Write a validation schema for the Module 4 harmonized dataset covering at least: no missing/unmatched P-codes, value >= 0, and ISO-format dates. Run it, review the flagged rows (there should be none, since Module 4 already corrected them), and confirm the pass.",
    "assessment": "Submitted validation script plus before/after row counts, graded on rule coverage and correct handling of failures (flagged and resolved, not silently dropped).",
},
{
    "num": 9, "slug": "09-reproducible-pipeline", "unit_letter": "E", "week": "9 (part 1)",
    "title": "Designing a Reproducible Data Integration Pipeline",
    "overview": "Assembles ingest, standardize, validate, document, and publish into one reproducible, re-runnable pipeline — and this is the one that matters most for this course: its published output is data/processed/track2_dataset.csv, the exact file Track 2 reads.",
    "objectives": [
        "Assemble ingest, standardize, validate, document, and publish steps into one reproducible, re-runnable pipeline instead of manual point-and-click steps.",
        "Apply basic version control to pipeline outputs via dated, versioned filenames and a run log.",
    ],
    "needs_raw": True,
    "python": [
        md("## Lesson content\n\n"
           "- Why \"click-ops\" data preparation breaks down at scale or on handover: a chain of manual "
           "spreadsheet edits is not auditable and does not survive staff turnover; encoding every step in a "
           "script makes it re-runnable and reviewable.\n"
           "- Mapping pipeline stages to the modules already completed: **ingest** (Module 2) -> **standardize** "
           "(Module 4) -> **validate** (Module 8) -> **document** (Module 6) -> **publish** a versioned output.\n"
           "- Lightweight orchestration appropriate to a regional hub's scale: a single scheduled script with a "
           "run log is usually enough.\n"
           "- Basic data versioning: dated output filenames so a bad refresh can be identified and rolled back "
           "rather than silently overwriting the last good version."),
        code(
"""import datetime as dt
import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, Check

run_log = []

def step(name, fn):
    try:
        result = fn()
        run_log.append({"step": name, "status": "OK"})
        return result
    except Exception as e:
        run_log.append({"step": name, "status": f"FAILED: {e}"})
        raise

ALIASES = {"Nyarugenge Dist.": "Nyarugenge", "Rwamagana ": "Rwamagana"}

def ingest():
    return (
        pd.read_csv("../../../data/raw/partner_a_finance_export.csv"),
        pd.read_csv("../../../data/raw/partner_b_survey_export.csv"),
        pd.read_csv("../../../data/raw/partner_c_hdx_pull.csv"),
        pd.read_csv("../../../data/raw/cod_ab_gazetteer.csv"),
    )

def standardize(sources):
    a, b, c, gaz = sources
    a["reg"] = a["reg"].str.strip().replace(ALIASES)
    b["region_name"] = b["region_name"].str.strip().replace(ALIASES)
    a["date"] = pd.to_datetime(a["date"], format="%d/%m/%Y")
    b["date"] = pd.to_datetime(b["collection_date"], format="%d-%b-%y")
    c["date"] = pd.to_datetime(c["date"])

    a = a.merge(gaz, left_on="reg", right_on="district_name", how="left")
    b = b.merge(gaz, left_on="region_name", right_on="district_name", how="left")

    merged = (
        c.merge(a[["district_pcode", "date", "rev"]], on=["district_pcode", "date"], how="left")
         .merge(b[["district_pcode", "date", "feature_1", "feature_2"]], on=["district_pcode", "date"], how="left")
         .merge(gaz[["district_pcode", "district_name", "province"]], on="district_pcode", how="left")
    )
    published = merged.rename(columns={"rev": "value", "district_name": "district"})[
        ["date", "province", "district", "district_pcode", "indicator", "value", "feature_1", "feature_2", "outcome"]
    ]
    published["date"] = published["date"].dt.strftime("%Y-%m-%d")
    for col in ("value", "feature_1", "feature_2"):
        published[col] = published[col].round(2)
    return published.sort_values(["district", "date"]).reset_index(drop=True)

def validate(df):
    gazetteer_codes = set(pd.read_csv("../../../data/raw/cod_ab_gazetteer.csv")["district_pcode"])
    schema = pa.DataFrameSchema({
        "district_pcode": Column(str, Check.isin(gazetteer_codes), nullable=False),
        "value": Column(float, Check.ge(0)),
        "date": Column(str, Check.str_matches(r"^\\d{4}-\\d{2}-\\d{2}$")),
    })
    schema.validate(df, lazy=True)

def document(df):
    dictionary = pd.DataFrame({
        "column": df.columns, "dtype": [str(t) for t in df.dtypes],
        "pct_missing": [round(df[c].isna().mean() * 100, 1) for c in df.columns],
    })
    dictionary.to_csv("../../../data/processed/track2_dataset_DICTIONARY.csv", index=False)

sources = step("ingest", ingest)
published = step("standardize", lambda: standardize(sources))
step("validate", lambda: validate(published))
step("document", lambda: document(published))

def publish(df):
    # Two outputs: the exact file Track 2 reads, and a dated, versioned
    # copy for audit history — the "publish" and "version" halves of
    # this module's lesson content.
    df.to_csv("../../../data/processed/track2_dataset.csv", index=False)
    timestamp = dt.date.today().isoformat()
    df.to_csv(f"../../../data/processed/published_regional_data_{timestamp}.csv", index=False)

step("publish", lambda: publish(published))
pd.DataFrame(run_log).to_csv("../../../data/processed/run_log.csv", index=False)
print(pd.DataFrame(run_log))
print(f"\\nPublished {len(published):,} rows to data/processed/track2_dataset.csv")
print("This is the exact file Track 2 Module 1 reads — the handoff, made real.")"""
        ),
        md("### Verifying the handoff\n\n"
           "If Track 2's `data/make_sample_data.py` has already been run in this repo, "
           "`data/processed/track2_dataset.csv` should now contain the same values either way — this pipeline "
           "and that shortcut script are seeded identically. Run the cell below to confirm."),
        code(
"""import pandas as pd

check = pd.read_csv("../../../data/processed/track2_dataset.csv")
print(f"{len(check):,} rows · {check['district'].nunique()} districts · "
      f"{check['date'].min()} to {check['date'].max()}")
check.head()"""
        ),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages."),
        code(
"""library(tidyverse)

run_log <- list()

run_step <- function(name, fn) {
  result <- tryCatch({
    r <- fn()
    run_log[[name]] <<- "OK"
    r
  }, error = function(e) {
    run_log[[name]] <<- paste("FAILED:", conditionMessage(e))
    stop(e)
  })
  result
}

ALIASES <- c("Nyarugenge Dist." = "Nyarugenge", "Rwamagana " = "Rwamagana")

ingest <- function() {
  list(
    a = read_csv("../../../data/raw/partner_a_finance_export.csv", show_col_types = FALSE),
    b = read_csv("../../../data/raw/partner_b_survey_export.csv", show_col_types = FALSE),
    c = read_csv("../../../data/raw/partner_c_hdx_pull.csv", show_col_types = FALSE),
    gaz = read_csv("../../../data/raw/cod_ab_gazetteer.csv", show_col_types = FALSE)
  )
}

standardize <- function(sources) {
  a <- sources$a %>% mutate(reg = recode(str_trim(reg), !!!ALIASES),
                             date = as.Date(date, format = "%d/%m/%Y")) %>%
    left_join(sources$gaz, by = c("reg" = "district_name"))
  b <- sources$b %>% mutate(region_name = recode(str_trim(region_name), !!!ALIASES),
                             date = as.Date(collection_date, format = "%d-%b-%y")) %>%
    left_join(sources$gaz, by = c("region_name" = "district_name"))
  c <- sources$c %>% mutate(date = as.Date(date))

  merged <- c %>%
    left_join(a %>% select(district_pcode, date, rev), by = c("district_pcode", "date")) %>%
    left_join(b %>% select(district_pcode, date, feature_1, feature_2), by = c("district_pcode", "date")) %>%
    left_join(sources$gaz %>% select(district_pcode, district_name, province), by = "district_pcode")

  merged %>%
    transmute(date = format(date, "%Y-%m-%d"), province, district = district_name, district_pcode,
              indicator, value = round(rev, 2), feature_1 = round(feature_1, 2),
              feature_2 = round(feature_2, 2), outcome) %>%
    arrange(district, date)
}

sources <- run_step("ingest", ingest)
published <- run_step("standardize", ~ standardize(sources))
run_step("validate", ~ stopifnot(all(published$value >= 0)))
run_step("document", ~ write_csv(published, "../../../data/processed/track2_dataset_DICTIONARY_r.csv"))

write_csv(published, "../../../data/processed/track2_dataset.csv")
timestamp <- Sys.Date()
write_csv(published, paste0("../../../data/processed/published_regional_data_", timestamp, ".csv"))
print(enframe(unlist(run_log), "step", "status"))
cat("\\nPublished", nrow(published), "rows to data/processed/track2_dataset.csv\\n")"""
        ),
    ],
    "exercise": "Run this pipeline end-to-end on a fresh clone (after `python3 data/make_track1_sources.py`), confirm the run log shows every stage OK, and diff the published `track2_dataset.csv` against the copy produced by `data/make_sample_data.py` — they should match exactly.",
    "assessment": "Pipeline runs successfully end-to-end on a held-out test dataset (graded live); run log correctly captures pass/fail of each stage.",
},
{
    "num": 10, "slug": "10-governance-responsibility-sustainability", "unit_letter": "E", "week": "9 (part 2)",
    "title": "Data Governance, Responsibility & Sustainability of Integration Pipelines",
    "overview": "Closes the track with the governance note that becomes a direct input to Track 2 Module 9's Ethical Impact Assessment: licensing, sensitive fields, ownership, and a plan for the pipeline to survive staff turnover.",
    "objectives": [
        "Draft a data-sharing and licensing note for an integrated dataset.",
        "Identify sustainability risks in a pipeline.",
        "Connect integration-stage governance to the Responsible AI and data-protection practices covered in Track 2.",
    ],
    "needs_raw": False,
    "python": [
        md("## Lesson content\n\n"
           "- **Data-sharing agreements and licensing.** Check the license of every source before merging or "
           "redistributing — combining an openly licensed dataset with a restricted-use one usually makes the "
           "combined output restricted too.\n"
           "- **Applying the UN Principles on Personal Data Protection and Privacy and the OCHA/IASC Data "
           "Responsibility Guidelines at the integration stage.** This is the earliest point in the whole chain "
           "to catch a personal-data or sensitive-aggregation risk, before it ever reaches a dashboard or an "
           "AI-assisted narration in Track 2.\n"
           "- **Sustainability and maintenance.** Documenting credentials and ownership (referenced, never "
           "exposed in code or notebooks) so a pipeline survives staff turnover; monitoring for source API or "
           "schema changes that silently break a scheduled pull; and a data-retirement plan for datasets that "
           "should no longer be kept."),
        code(
"""governance_note = {
    "pipeline": "Module 9 regional data integration pipeline",
    "sources_and_licenses": [
        {"source": "Partner A finance export", "license": "Internal, hub-owned"},
        {"source": "Partner B survey export", "license": "Internal, hub-owned, informed-consent collected"},
        {"source": "Partner C HDX-style pull", "license": "CC-BY (attribution required on redistribution)"},
    ],
    "sensitive_fields": "None at district-month aggregation level; would need review if disaggregated below district.",
    "accountable_owner": "Regional Hub M&E Unit lead",
    "credential_location": "Referenced via environment variable HUB_DB_CREDENTIALS, not hardcoded — see environment/",
    "review_date": "Quarterly, aligned with the pipeline's refresh cadence",
}
governance_note"""
        ),
    ],
    "r": [
        md("## Lesson content\n\nSee the Python notebook for the full lesson content — identical in both languages."),
        code(
"""governance_note <- list(
  pipeline = "Module 9 regional data integration pipeline",
  sources_and_licenses = list(
    list(source = "Partner A finance export", license = "Internal, hub-owned"),
    list(source = "Partner B survey export", license = "Internal, hub-owned, informed-consent collected"),
    list(source = "Partner C HDX-style pull", license = "CC-BY (attribution required on redistribution)")
  ),
  sensitive_fields = "None at district-month aggregation level; would need review if disaggregated below district.",
  accountable_owner = "Regional Hub M&E Unit lead",
  credential_location = "Referenced via environment variable HUB_DB_CREDENTIALS, not hardcoded",
  review_date = "Quarterly, aligned with the pipeline's refresh cadence"
)
governance_note"""
        ),
    ],
    "exercise": "Complete a pipeline governance note for the Module 9 pipeline: data sources and their licenses, sensitive fields present, accountable owner, credential location (referenced, not exposed), and a review date.",
    "assessment": "Submitted governance note, reviewed for completeness.",
    "governance": "This note becomes a direct input to the Track 2 Module 9 Ethical Impact Assessment for any hub built downstream from this pipeline.",
},
]

# ------------------------------------------------------------------
# BUILD NOTEBOOKS
# ------------------------------------------------------------------
for m in MODULES:
    for lang, body_key in (("python", "python"), ("r", "r")):
        cells = [header(m)]
        if m["needs_raw"]:
            cells.append(RAW_NOTE)
        cells += m[body_key]
        cells.append(footer(m))
        out = os.path.join(ROOT, "notebooks", "track1", f"module-{m['slug']}", f"{lang}.ipynb")
        write_nb(out, cells, lang)
        print("wrote", out)

print(f"\n{len(MODULES)} modules x 2 languages = {len(MODULES)*2} Track 1 notebooks generated.")
