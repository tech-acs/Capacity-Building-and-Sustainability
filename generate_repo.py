#!/usr/bin/env python3
"""
Generates the full track2-notebooks repo: sample data, module notebooks
(Python + R, one pair per module), the two dashboard apps, environment
files, and the README. Run once from the repo root:  python3 generate_repo.py
"""
import itertools
import json
import os
import uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
_id_counter = itertools.count(1)

def _cell_id():
    # short, deterministic-looking, unique-enough id (nbformat >=4.5 requires one)
    return uuid.uuid5(uuid.NAMESPACE_OID, f"track2-cell-{next(_id_counter)}").hex[:8]

# ------------------------------------------------------------------
# notebook builder helpers (hand-rolled nbformat v4.5 — no nbformat dep needed to WRITE)
# ------------------------------------------------------------------
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

**Unit {m['unit_letter']} · Week {m['week']}** · Track 2 — Visualization, Analytic Hubs & Responsible AI

{m['overview']}

## Learning objectives

{chr(10).join(f"- **{o['level']}** _{o['bloom']}_ — {o['text']}" for o in m['objectives'])}

## Setup

This notebook reads `../../data/processed/track2_dataset.csv`, built by
`data/make_sample_data.py`. It is **synthetic** data shaped like the real
NISR/HDX handoff described in the course site's Chapter 3 — swap in a real
extract by re-pointing the path below once you have one. See
`data/README.md` for where to get real data and exactly what to rename.
"""
    )

def data_load_python():
    return code(
"""import pandas as pd

DATA_PATH = "../../data/processed/track2_dataset.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["date"])
print(f"{len(df):,} rows · {df['district'].nunique()} districts · "
      f"{df['date'].min().date()} to {df['date'].max().date()}")
df.head()"""
    )

def data_load_r():
    return code(
"""library(tidyverse)

data_path <- "../../data/processed/track2_dataset.csv"
df <- read_csv(data_path, show_col_types = FALSE)
cat(nrow(df), "rows ·", n_distinct(df$district), "districts ·",
    format(min(df$date)), "to", format(max(df$date)), "\\n")
head(df)"""
    )

def footer(m):
    parts = [f"## Your turn\n\n{m['exercise']}\n\n**Formative assessment.** {m['assessment']}"]
    if m.get("peer"):
        parts.append(f"**Peer review.** {m['peer']}")
    if m.get("rai"):
        parts.append(f"## Responsible AI callback\n\n{m['rai']}")
    return md("\n\n".join(parts))

# ------------------------------------------------------------------
# MODULE CONTENT
# ------------------------------------------------------------------
MODULES = [
{
    "num": 1, "slug": "01-visual-grammar-chart-selection", "unit_letter": "A", "week": 1,
    "title": "Visual Grammar & Chart Selection",
    "overview": "Before touching a plotting library, this notebook reasons about a chart the way you'd "
                "reason about a sentence: what claim is it making, and does the chosen form support or "
                "undermine that claim. The code below builds the same two bars twice — once with a "
                "truncated axis, once corrected — so the distortion is something you see, not just read about.",
    "objectives": [
        {"level": "Foundational", "bloom": "Understand", "text": "Select an appropriate chart type for a stated data question."},
        {"level": "Foundational", "bloom": "Understand", "text": "Identify a specific flaw in a misleading chart."},
    ],
    "exercise": "Chart-critique worksheet: given six charts (three from real regional reporting, three constructed to "
                "mislead), identify the flaw in each and sketch the corrected chart type. Then extend the code "
                "below with one more distortion type (a dual-axis chart is a good second example) and its fix.",
    "assessment": "Knowledge check / quiz: chart-type matching plus flaw identification.",
    "rai": "A misleading chart is a data-integrity failure, not just a design failure. This connects forward to "
           "Module 9's Ethical Impact Assessment, where how findings are visualized is itself a responsibility question.",
    "needs_data": False,
    "python": [
        md("## The same two bars, twice\n\nA truncated y-axis and a zero-based y-axis, side by side, on identical data."),
        code(
"""import matplotlib.pyplot as plt
import pandas as pd

demo = pd.DataFrame({
    "quarter": ["Q1", "Q2", "Q3", "Q4"] * 2,
    "region": ["A"] * 4 + ["B"] * 4,
    "value": [42, 45, 44, 47, 40, 41, 39, 43],
})
pivot = demo.pivot(index="quarter", columns="region", values="value")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
pivot.plot(kind="bar", ax=axes[0], ylim=(38, 48), rot=0)
axes[0].set_title("Flawed: truncated axis exaggerates the gap")
pivot.plot(kind="bar", ax=axes[1], ylim=(0, 50), rot=0)
axes[1].set_title("Corrected: zero-based axis, honest comparison")
plt.tight_layout()
plt.show()"""
        ),
        md("The right-hand chart is the same data. Region A leads Region B by 2-4 points every quarter, a modest, "
           "steady gap. The left-hand chart, by starting its axis at 38 instead of 0, makes that gap look like "
           "region B is collapsing. Nothing was altered except where the axis starts."),
    ],
    "r": [
        md("## The same two bars, twice\n\nA truncated y-axis and a zero-based y-axis, side by side, on identical data."),
        code(
"""library(tidyverse)
library(patchwork)

demo <- tibble(
  quarter = rep(c("Q1", "Q2", "Q3", "Q4"), 2),
  region  = rep(c("A", "B"), each = 4),
  value   = c(42, 45, 44, 47, 40, 41, 39, 43)
)

flawed <- ggplot(demo, aes(quarter, value, fill = region)) +
  geom_col(position = "dodge") +
  coord_cartesian(ylim = c(38, 48)) +
  labs(title = "Flawed: truncated axis exaggerates the gap")

corrected <- ggplot(demo, aes(quarter, value, fill = region)) +
  geom_col(position = "dodge") +
  coord_cartesian(ylim = c(0, 50)) +
  labs(title = "Corrected: zero-based axis, honest comparison")

flawed + corrected"""
        ),
        md("The right-hand chart is the same data. Region A leads Region B by 2-4 points every quarter, a modest, "
           "steady gap. The left-hand chart, by starting its axis at 38 instead of 0, makes that gap look like "
           "region B is collapsing. Nothing was altered except where the axis starts."),
    ],
},
{
    "num": 2, "slug": "02-static-charts", "unit_letter": "A", "week": 2,
    "title": "Static Charts in Python & R",
    "overview": "Translating a Module 1 chart-type decision into working code, applied to the Chapter 3 dataset, "
                "with a reusable house-style function and one small-multiples figure.",
    "objectives": [
        {"level": "Intermediate", "bloom": "Apply", "text": "Build publication-quality static charts with a consistent, reusable house style."},
        {"level": "Intermediate", "bloom": "Apply", "text": "Apply Module 1 principles to a real regional dataset: correct chart type, honest scale, accessible color."},
    ],
    "exercise": "Recreate the same set of five charts from the dataset in both matplotlib/seaborn and ggplot2, each "
                "wrapped in a reusable house-style theme function. Two are built below; add three more (a line chart "
                "of the national trend, a boxplot of value by province, and a small-multiples grid by district).",
    "assessment": "Hands-on scripted exercise, graded submission: house-style function plus five charts in both "
                  "languages, checklist-graded.",
    "peer": "Design-checklist review of a classmate's chart set, using the same checklist a facilitator would grade against.",
    "needs_data": True,
    "python": [
        code(
"""import matplotlib.pyplot as plt
import seaborn as sns

def house_style(ax, title):
    ax.set_title(title, fontsize=13, fontweight="bold")
    sns.despine(ax=ax)
    ax.grid(axis="y", alpha=0.3)
    return ax

by_district = df.groupby("district", as_index=False)["value"].mean().sort_values("value")

fig, ax = plt.subplots(figsize=(7, 4))
sns.barplot(data=by_district, x="value", y="district", ax=ax, color="#1D6E73")
house_style(ax, "Mean Value by District")
plt.tight_layout()
plt.show()"""
        ),
        md("### Small multiples\n\nOne distribution panel per province — the same house style, faceted."),
        code(
"""g = sns.displot(
    df, x="value", col="province", col_wrap=3, height=2.6, color="#1D6E73"
)
g.set_titles("{col_name}")
g.figure.suptitle("Value Distribution by Province", y=1.03, fontweight="bold")
plt.show()"""
        ),
    ],
    "r": [
        code(
"""library(tidyverse)

house_theme <- theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold"), panel.grid.minor = element_blank())

by_district <- df |>
  group_by(district) |>
  summarise(value = mean(value)) |>
  arrange(value)

ggplot(by_district, aes(x = value, y = fct_reorder(district, value))) +
  geom_col(fill = "#1D6E73") +
  labs(title = "Mean Value by District", x = NULL, y = NULL) +
  house_theme"""
        ),
        md("### Small multiples\n\nOne distribution panel per province — the same house style, faceted."),
        code(
"""ggplot(df, aes(x = value)) +
  geom_histogram(fill = "#1D6E73", bins = 20) +
  facet_wrap(~ province) +
  labs(title = "Value Distribution by Province", x = NULL, y = NULL) +
  house_theme"""
        ),
    ],
},
{
    "num": 3, "slug": "03-interactive-visualization", "unit_letter": "B", "week": 3,
    "title": "Interactive Visualization",
    "overview": "Extending static charting into the interactive layer the Unit C dashboards are built on: hover "
                "text, and a dropdown that filters by province without leaving the chart.",
    "objectives": [
        {"level": "Intermediate", "bloom": "Apply", "text": "Build interactive charts with hover, zoom, and filter behavior, in both languages."},
        {"level": "Intermediate", "bloom": "Apply", "text": "Judge when interactivity clarifies a chart versus when it only adds noise."},
    ],
    "exercise": "Convert two Module 2 static charts into interactive versions with meaningful, non-default hover "
                "text; export each as a standalone HTML file (see the commented `write_html` / `saveWidget` line "
                "below).",
    "assessment": "Hands-on scripted exercise, checklist-graded.",
    "needs_data": True,
    "python": [
        code(
"""import plotly.express as px

monthly = df.groupby(["date", "province"], as_index=False)["value"].mean()

fig = px.line(
    monthly, x="date", y="value", color="province",
    hover_data={"value": ":.1f"},
    title="Provincial Trend Over Time",
)
fig.update_layout(template="simple_white")
fig.show()
# fig.write_html("outputs/trend_interactive.html")"""
        ),
    ],
    "r": [
        code(
"""library(tidyverse)
library(plotly)

monthly <- df |>
  group_by(date, province) |>
  summarise(value = mean(value), .groups = "drop")

p <- ggplot(monthly, aes(date, value, color = province)) +
  geom_line() +
  labs(title = "Provincial Trend Over Time")

ggplotly(p, tooltip = c("date", "value", "province"))
# htmlwidgets::saveWidget(last_plot(), "outputs/trend_interactive.html")"""
        ),
    ],
},
{
    "num": 4, "slug": "04-geospatial-analysis", "unit_letter": "B", "week": 4,
    "title": "Geospatial Analysis & Mapping on P-codes",
    "overview": "Joining the dataset to district boundaries on a P-code, then building a choropleth two ways: "
                "a static one (fast, prints to a report) and an interactive one (a hover-able map for a dashboard). "
                "The boundary file here is a **synthetic** grid standing in for the real HDX shapefile — same join "
                "logic, fabricated geometry. See `data/README.md`.",
    "objectives": [
        {"level": "Foundational", "bloom": "Understand", "text": "Distinguish point data from polygon/boundary data; explain why averaging coordinates produces a misleading centroid."},
        {"level": "Intermediate", "bloom": "Apply", "text": "Build bubble maps and choropleths correctly joined on P-codes, with an appropriate sequential or diverging color scale."},
    ],
    "exercise": "Join the dataset to the (synthetic) district boundary layer on P-codes; produce one choropleth and "
                "one bubble map in both languages, with a written justification of the chosen color scale. Then "
                "swap in the real HDX Rwanda COD-AB file (Chapter 3.2 of the course site) and re-run unchanged.",
    "assessment": "Hands-on scripted exercise plus a data-quality note documenting any join failures caused by "
                  "P-code mismatches.",
    "rai": "A granular choropleth of a small population subgroup can itself be a re-identification or protection "
           "risk. This previews Module 6's data-minimization pattern and Module 9's formal governance treatment.",
    "needs_data": True,
    "python": [
        code(
"""import warnings
import geopandas as gpd
import matplotlib.pyplot as plt

admin = gpd.read_file("../../data/processed/admin_boundaries_synthetic.geojson")
latest = df[df["date"] == df["date"].max()]
merged = admin.merge(latest, left_on="pcode_sim", right_on="district_pcode")

fig, ax = plt.subplots(figsize=(6, 5))
merged.plot(column="value", cmap="YlGnBu", legend=True, edgecolor="white", ax=ax)
ax.set_title("Choropleth: Value by District (synthetic boundaries)")
ax.set_axis_off()"""
        ),
        md("### Interactive version"),
        code(
"""import folium

# these are small illustrative rectangles, not real projected geometry —
# safe to silence the "geographic CRS" precision warning here
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=UserWarning)
    centroid = merged.geometry.centroid

m = folium.Map(location=[centroid.y.mean(), centroid.x.mean()], zoom_start=9, tiles="cartodbpositron")
map_layer = merged[["pcode_sim", "value", "geometry"]]  # drop non-JSON-serializable columns (e.g. dates)
folium.Choropleth(
    geo_data=map_layer, data=map_layer, columns=["pcode_sim", "value"],
    key_on="feature.properties.pcode_sim", fill_color="YlGnBu", legend_name="Value",
).add_to(m)
m"""
        ),
    ],
    "r": [
        code(
"""library(sf)

admin <- st_read("../../data/processed/admin_boundaries_synthetic.geojson", quiet = TRUE)
latest <- df |> filter(date == max(date))
merged <- admin |> left_join(latest, by = c("pcode_sim" = "district_pcode"))

plot(merged["value"], main = "Choropleth: Value by District (synthetic boundaries)")"""
        ),
        md("### Interactive version"),
        code(
"""library(leaflet)

pal <- colorNumeric("YlGnBu", domain = merged$value)

leaflet(merged) |>
  addProviderTiles("CartoDB.Positron") |>
  addPolygons(fillColor = ~pal(value), fillOpacity = 0.8, color = "white", weight = 1) |>
  addLegend(pal = pal, values = ~value, title = "Value")"""
        ),
    ],
},
{
    "num": 5, "slug": "05-dashboard-foundations", "unit_letter": "C", "week": 5,
    "title": "Dashboard Foundations",
    "overview": "A dashboard's chart-and-filter logic is worth proving out in a notebook before it goes into an "
                "app. This notebook builds the exact aggregation the app's callback will run; the app itself "
                "(Streamlit and Shiny versions) lives in `apps/` at the repo root and is run outside Jupyter.",
    "objectives": [
        {"level": "Foundational", "bloom": "Understand", "text": "Explain what distinguishes an analytic hub from a static report; sketch a basic architecture and audience-persona wireframe."},
        {"level": "Intermediate", "bloom": "Apply (started)", "text": "Wire a single chart and a single filter into a minimal working app."},
    ],
    "exercise": "Design brief: a one-page wireframe plus architecture sketch for a regional analytic hub, plus a "
                "minimal one-filter, one-chart working prototype. Run `streamlit run apps/streamlit_app.py` or "
                "`Rscript -e \"shiny::runApp('apps/shiny_app.R')\"` from the repo root to see the finished version.",
    "assessment": "Design brief / structured worksheet, checklist-graded.",
    "needs_data": True,
    "python": [
        md("### The filter logic the app's callback will run\n\nGiven a province, return the filtered frame the chart draws from — this is the function `apps/streamlit_app.py` calls on every dropdown change."),
        code(
"""def filter_by_province(frame, province):
    return frame[frame["province"] == province].sort_values("date")

sample = filter_by_province(df, df["province"].iloc[0])
sample.plot(x="date", y="value", figsize=(7, 3.5), color="#1D6E73",
            title=f"Preview: {df['province'].iloc[0]}")"""
        ),
        md("### The app\n\n```python\n# apps/streamlit_app.py  (excerpt — full file at the repo root)\nimport streamlit as st\nimport pandas as pd\n\nst.set_page_config(page_title=\"Rwanda Regional Hub\", layout=\"wide\")\ndf = pd.read_csv(\"data/processed/track2_dataset.csv\")\n\nprovince = st.sidebar.selectbox(\"Province\", sorted(df[\"province\"].unique()))\nfiltered = df[df[\"province\"] == province]\n\nst.title(\"Regional Analytic Hub, Prototype\")\nst.line_chart(filtered, x=\"date\", y=\"value\")\n```\n\nRun with `streamlit run apps/streamlit_app.py` from the repo root."),
    ],
    "r": [
        md("### The filter logic the app's callback will run\n\nGiven a province, return the filtered frame the chart draws from — this is the function `apps/shiny_app.R` calls on every dropdown change."),
        code(
"""filter_by_province <- function(frame, prov) {
  frame |> filter(province == prov) |> arrange(date)
}

sample <- filter_by_province(df, df$province[1])
ggplot(sample, aes(date, value)) +
  geom_line(color = "#1D6E73") +
  labs(title = paste("Preview:", df$province[1]))"""
        ),
        md("### The app\n\n```r\n# apps/shiny_app.R  (excerpt — full file at the repo root)\nlibrary(shiny)\nlibrary(ggplot2)\n\ndf <- read.csv(\"data/processed/track2_dataset.csv\")\n\nui <- fluidPage(\n  titlePanel(\"Regional Analytic Hub, Prototype\"),\n  sidebarLayout(\n    sidebarPanel(selectInput(\"province\", \"Province\", sort(unique(df$province)))),\n    mainPanel(plotOutput(\"trend\"))\n  )\n)\n\nserver <- function(input, output) {\n  output$trend <- renderPlot({\n    ggplot(subset(df, province == input$province), aes(date, value)) +\n      geom_line(color = \"#1D6E73\")\n  })\n}\n\nshinyApp(ui, server)\n```\n\nRun with `Rscript -e \"shiny::runApp('apps/shiny_app.R')\"` from the repo root."),
    ],
},
{
    "num": 6, "slug": "06-ai-assisted-analytics-pattern", "unit_letter": "C", "week": "6 + Extension",
    "title": "AI-Assisted Analytics Pattern",
    "overview": "The track's signature pattern: share only the data **schema** with an LLM, run the code it returns "
                "**locally**, and pass on only an **aggregate summary**. `call_llm()` below is a stand-in for a "
                "real API call so this runs with no API key — swap in your provider's client and the rest of the "
                "pattern is unchanged.",
    "objectives": [
        {"level": "Intermediate", "bloom": "Apply", "text": "Build a working, multi-filter dashboard with at least one chart and one map wired together."},
        {"level": "Advanced", "bloom": "Analyze / Create, via the Extension", "text": "Integrate an AI-assisted analytics pattern (schema-only code generation, local execution, summary-only narration) with data-minimization safeguards designed in from the start."},
        {"level": "Advanced", "bloom": "Analyze / Create", "text": "Port a dashboard component's logic between Python and R without loss of correctness."},
    ],
    "exercise": "Extend the Module 5 prototype into a full dashboard (at least 2 filters, 1 chart, 1 map); add one "
                "AI-assisted feature built strictly to the schema-only / local-execution / summary-only pattern "
                "below; port one component to the other language.",
    "assessment": "Live demo + code review: a 5-minute live dashboard demo graded against a reactivity/design "
                  "rubric.",
    "rai": "The schema-only / local-execution / summary-only pattern is itself a data-minimization safeguard, "
           "named explicitly here so it is a practiced habit before Module 9 formalizes it as a governance requirement.",
    "needs_data": True,
    "python": [
        code(
"""def call_llm(prompt: str) -> str:
    \"\"\"Stand-in for a real LLM call. In the exercise, call your provider's
    API here. Whatever it returns is executed locally in Step 2 — the
    model only ever sees the schema from Step 1, never a data row.\"\"\"
    return "result = df.groupby('district')['value'].mean().sort_values(ascending=False).head(5)"


# Step 1: share only the schema, never raw rows
schema = {c: str(t) for c, t in df.dtypes.items()}
prompt = f"Data frame schema (columns and types only): {schema}\\nWrite pandas code that returns the top 5 districts by mean 'value'. Return code only, no data."
generated_code = call_llm(prompt)
print("LLM returned:\\n ", generated_code)

# Step 2: run it locally, against the real data
local_vars = {"df": df}
exec(generated_code, {}, local_vars)
result = local_vars["result"]

# Step 3: only the aggregate result is passed on
narration_prompt = f"Summarize this result in one paragraph: {result.to_dict()}"
print("\\nWhat leaves the machine (aggregate only):\\n ", result.to_dict())"""
        ),
    ],
    "r": [
        code(
"""call_llm <- function(prompt) {
  # Stand-in for a real LLM call. In the exercise, call your provider's
  # API here. Whatever it returns is executed locally in Step 2 — the
  # model only ever sees the schema from Step 1, never a data row.
  "result <- df |> group_by(district) |> summarise(value = mean(value)) |> arrange(desc(value)) |> head(5)"
}

# Step 1: share only the schema, never raw rows
schema <- sapply(df, class)
prompt <- paste0(
  "Data frame schema (columns and types only): ", toString(schema),
  ". Write R code that returns the top 5 districts by mean 'value'. Return code only, no data."
)
generated_code <- call_llm(prompt)
cat("LLM returned:\\n ", generated_code, "\\n")

# Step 2: run it locally, against the real data
eval(parse(text = generated_code))

# Step 3: only the aggregate result is passed on
cat("\\nWhat leaves the machine (aggregate only):\\n")
print(result)"""
        ),
    ],
},
{
    "num": 7, "slug": "07-forecasting", "unit_letter": "D", "week": 7,
    "title": "Forecasting Regional Time Series",
    "overview": "Small-N regional data rarely supports anything fancier than exponential smoothing, and the chart "
                "must always carry a confidence interval, never a bare point forecast. Both languages below use the "
                "same method (Holt-Winters exponential smoothing) so the outputs are directly comparable; if you "
                "have Prophet installed, the commented cell shows the same forecast that way instead.",
    "objectives": [
        {"level": "Foundational", "bloom": "Understand", "text": "Distinguish trend from seasonality in a time series; explain when machine learning is, and is not, appropriate for small-N regional data."},
        {"level": "Intermediate", "bloom": "Apply", "text": "Produce a forecast with a visible confidence interval."},
    ],
    "exercise": "Forecast one time series from the dataset in both languages; the chart must show history, "
                "forecast, and confidence interval together. Then repeat for a second district and compare.",
    "assessment": "Feeds into the combined Module 7 to 8 forecast and model report (see Module 8).",
    "rai": "A forecast presented without its confidence interval is a governance issue, not a style choice. It "
           "misrepresents certainty to a decision-maker who may act on it.",
    "needs_data": True,
    "python": [
        code(
"""import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

ts = df.groupby("date")["value"].mean().asfreq("MS").interpolate()

fit = ExponentialSmoothing(ts, trend="add", seasonal=None).fit()
horizon = 6
forecast = fit.forecast(horizon)
resid_std = fit.resid.std()
ci = 1.645 * resid_std  # ~90% band from in-sample residual spread

ax = ts.plot(figsize=(8, 4), label="history", color="#1D6E73")
forecast.plot(ax=ax, label="forecast", color="#AF4A2E")
ax.fill_between(forecast.index, forecast - ci, forecast + ci, color="#AF4A2E", alpha=0.15, label="~90% band")
ax.legend()
ax.set_title("National Trend: History + 6-Month Forecast")
import matplotlib.pyplot as plt
plt.show()

# --- Prophet alternative (if installed) ---
# from prophet import Prophet
# prophet_df = ts.reset_index().rename(columns={"date": "ds", "value": "y"})
# m = Prophet(interval_width=0.90).fit(prophet_df)
# future = m.make_future_dataframe(periods=horizon, freq="MS")
# m.plot(m.predict(future))"""
        ),
    ],
    "r": [
        code(
"""library(forecast)

monthly <- df |>
  group_by(date) |>
  summarise(value = mean(value), .groups = "drop") |>
  arrange(date)
ts_data <- ts(monthly$value, frequency = 12)

fit <- ets(ts_data)
fc <- forecast(fit, h = 6, level = 90)
autoplot(fc) + labs(title = "National Trend: History + 6-Month Forecast, 90% CI")

# --- Prophet alternative (if installed) ---
# library(prophet)
# prophet_df <- monthly |> rename(ds = date, y = value)
# m <- prophet(prophet_df, interval.width = 0.90)
# future <- make_future_dataframe(m, periods = 6, freq = "month")
# plot(m, predict(m, future))"""
        ),
    ],
},
{
    "num": 8, "slug": "08-interpretable-models", "unit_letter": "D", "week": 7,
    "title": "Interpretable First Models",
    "overview": "A proper train/test split and an interpretable model family, chosen deliberately over anything "
                "black-box, plus a one-paragraph plain-language translation of what the model actually says.",
    "objectives": [
        {"level": "Intermediate", "bloom": "Apply", "text": "Train and evaluate a simple, interpretable model with a proper train/test split."},
        {"level": "Advanced", "bloom": "Evaluate, begun here and completed at capstone", "text": "Communicate a model's or forecast's uncertainty and limitations in plain language for a non-technical decision-maker."},
    ],
    "exercise": "Forecast & model report: combine the Module 7 forecast and this module's interpretable model into "
                "a short report with a plain-language uncertainty summary for a non-technical reader.",
    "assessment": "Graded report, rubric-checked against the capstone criterion it previews (Analytical rigor of "
                  "model/forecast, 20 pts).",
    "needs_data": True,
    "python": [
        code(
"""from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

X = df[["feature_1", "feature_2"]]
y = df["outcome"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

model = LogisticRegression().fit(X_train, y_train)
preds = model.predict(X_test)
print(classification_report(y_test, preds))

coefs = pd.Series(model.coef_[0], index=X.columns).sort_values()
print("\\nCoefficients (log-odds scale):\\n", coefs)"""
        ),
        md("**Plain-language summary (fill in after running):** the model correctly classifies about "
           "_[accuracy]_ of held-out cases. `feature_1` moves the odds of a positive outcome _[up/down]_ "
           "per unit increase; `feature_2` _[up/down]_. This is a first, interpretable pass, not a final "
           "verdict — see the capstone rubric's Analytical Rigor line for what a complete report needs."),
    ],
    "r": [
        code(
"""library(tidymodels)

split <- initial_split(df, prop = 0.75, strata = outcome)
train <- training(split)
test  <- testing(split)

log_fit <- logistic_reg() |>
  set_engine("glm") |>
  fit(as.factor(outcome) ~ feature_1 + feature_2, data = train)

predict(log_fit, test) |>
  bind_cols(test) |>
  metrics(truth = as.factor(outcome), estimate = .pred_class)

tidy(log_fit)"""
        ),
        md("**Plain-language summary (fill in after running):** the model correctly classifies about "
           "_[accuracy]_ of held-out cases. `feature_1` moves the odds of a positive outcome _[up/down]_ "
           "per unit increase; `feature_2` _[up/down]_. This is a first, interpretable pass, not a final "
           "verdict — see the capstone rubric's Analytical Rigor line for what a complete report needs."),
    ],
},
{
    "num": 9, "slug": "09-responsible-ai-eia", "unit_letter": "E", "week": 8,
    "title": "UN/UNESCO Responsible AI Frameworks & Ethical Impact Assessment",
    "overview": "This notebook is mostly template, not code: a data inventory grounds the Ethical Impact "
                "Assessment in the actual columns you are working with, then the EIA itself follows the structure "
                "used throughout the course.",
    "objectives": [
        {"level": "Foundational", "bloom": "Remember/Understand", "text": "Name the core principles of the UN Data Protection Principles, the UNESCO AI Ethics Recommendation, and the OCHA/IASC Data Responsibility Guidelines."},
        {"level": "Intermediate", "bloom": "Apply", "text": "Complete an Ethical Impact Assessment and a data-governance/licensing note for a real dataset or hub; apply a data-minimization design pattern."},
    ],
    "exercise": "Ethical Impact Assessment worksheet, applied to your own Unit C dashboard. Replace every "
                "_[bracketed]_ prompt below with your own answer.",
    "assessment": "Scorecard / structured worksheet, checklist-graded. Feeds the capstone's Responsible AI "
                  "documentation criterion (20 pts).",
    "needs_data": True,
    "python": [
        md("## Data inventory\n\nWhat you actually have, before assessing what you should do with it."),
        code("""df.dtypes.to_frame("dtype").assign(n_unique=df.nunique(), n_missing=df.isna().sum())"""),
        md(
"""## Ethical Impact Assessment

**Purpose.** _[Why does this hub exist — what decision does it inform?]_

**Data sources.** _[NISR EICV / census extract; HDX admin boundaries; note whether this run used real or synthetic data.]_

**Minimization measures.** _[e.g. the Module 6 schema-only pattern; aggregation before any AI narration; no row-level exports.]_

**Consent / provenance.** _[Where did each source dataset come from, and under what terms? Link the catalog page.]_

**Risk of harm.** _[Could a granular view (Module 4's re-identification risk) expose a small subgroup? Could a forecast without a CI (Module 7) mislead a decision-maker?]_

**Mitigation.** _[What did you change in response to the risks above?]_
"""),
    ],
    "r": [
        md("## Data inventory\n\nWhat you actually have, before assessing what you should do with it."),
        code(
"""library(tidyverse)
df |>
  summarise(across(everything(), list(
    n_unique = ~n_distinct(.), n_missing = ~sum(is.na(.))
  ))) |>
  pivot_longer(everything(), names_to = "column_stat", values_to = "value")"""
        ),
        md(
"""## Ethical Impact Assessment

**Purpose.** _[Why does this hub exist — what decision does it inform?]_

**Data sources.** _[NISR EICV / census extract; HDX admin boundaries; note whether this run used real or synthetic data.]_

**Minimization measures.** _[e.g. the Module 6 schema-only pattern; aggregation before any AI narration; no row-level exports.]_

**Consent / provenance.** _[Where did each source dataset come from, and under what terms? Link the catalog page.]_

**Risk of harm.** _[Could a granular view (Module 4's re-identification risk) expose a small subgroup? Could a forecast without a CI (Module 7) mislead a decision-maker?]_

**Mitigation.** _[What did you change in response to the risks above?]_
"""),
    ],
},
{
    "num": 10, "slug": "10-bias-fairness-audit", "unit_letter": "E", "week": 8,
    "title": "Bias, Fairness & Sustainability Audit",
    "overview": "Auditing the Module 8 model for group-wise fairness by province, then drafting a mitigation "
                "rather than stopping at detection.",
    "objectives": [
        {"level": "Advanced", "bloom": "Analyze/Evaluate", "text": "Run a group-wise fairness/bias audit on a model and draft mitigations."},
        {"level": "Advanced", "bloom": "Analyze/Evaluate", "text": "Evaluate a pipeline or hub end-to-end for sustainability and accountability risk."},
    ],
    "exercise": "Fairness audit report on the Module 8 model, disaggregated by province, with at least one drafted "
                "mitigation.",
    "assessment": "Graded audit report. The second, advanced-level formative touchpoint for the Responsible AI "
                  "domain, immediately ahead of the capstone.",
    "needs_data": True,
    "python": [
        code(
"""from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from fairlearn.metrics import MetricFrame, demographic_parity_difference
from sklearn.metrics import accuracy_score

X = df[["feature_1", "feature_2"]]
y = df["outcome"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
model = LogisticRegression().fit(X_train, y_train)
preds = model.predict(X_test)

sub = df.loc[X_test.index, "province"]
mf = MetricFrame(metrics=accuracy_score, y_true=y_test, y_pred=preds, sensitive_features=sub)
print("Accuracy by province:\\n", mf.by_group)

dpd = demographic_parity_difference(y_test, preds, sensitive_features=sub)
print(f"\\nDemographic parity difference: {dpd:.3f}")"""
        ),
        md("**Mitigation note (fill in after running):** if accuracy or the parity gap above is wide across "
           "provinces, name at least one mitigation, e.g. a province-aware decision threshold, collecting more "
           "training data from the underperforming province, or dropping the model in favor of the simpler "
           "Module 7 forecast for that province specifically."),
    ],
    "r": [
        code(
"""library(tidymodels)

split <- initial_split(df, prop = 0.75, strata = outcome)
train <- training(split)
test  <- testing(split)

log_fit <- logistic_reg() |>
  set_engine("glm") |>
  fit(as.factor(outcome) ~ feature_1 + feature_2, data = train)

test_with_preds <- predict(log_fit, test) |> bind_cols(test)

test_with_preds |>
  group_by(province) |>
  accuracy(truth = as.factor(outcome), estimate = .pred_class)

# install.packages("fairness") for a packaged demographic-parity metric:
# library(fairness)
# dem_parity(data = test_with_preds, outcome = "outcome", group = "province",
#            probs = ".pred_class", base = "reference_province")"""
        ),
        md("**Mitigation note (fill in after running):** if accuracy varies widely across provinces, name at "
           "least one mitigation, e.g. a province-aware decision threshold, collecting more training data from "
           "the underperforming province, or dropping the model in favor of the simpler Module 7 forecast for "
           "that province specifically."),
    ],
},
]

# ------------------------------------------------------------------
# BUILD NOTEBOOKS
# ------------------------------------------------------------------
for m in MODULES:
    for lang, body_key in (("python", "python"), ("r", "r")):
        cells = [header(m)]
        if m["needs_data"]:
            cells.append(data_load_python() if lang == "python" else data_load_r())
        cells += m[body_key]
        cells.append(footer(m))
        out = os.path.join(ROOT, "notebooks", f"module-{m['slug']}", f"{lang}.ipynb")
        write_nb(out, cells, lang)
        print("wrote", out)

print(f"\n{len(MODULES)} modules x 2 languages = {len(MODULES)*2} notebooks generated.")
