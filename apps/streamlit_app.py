"""
Track 2 reference dashboard (Modules 5-6), Python/Streamlit version.

Run from the repo root, after `python3 data/make_sample_data.py`:

    streamlit run apps/streamlit_app.py

Two filters (province, district), one trend chart, one district-average bar
chart, and one AI-assisted summary built strictly to the schema-only /
local-execution / summary-only pattern from Module 6 (see the notebook for
the fuller walkthrough — `call_llm` here is the same kind of stand-in).
"""
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rwanda Regional Hub", layout="wide")

DATA_PATH = "data/processed/track2_dataset.csv"


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])


def call_llm(prompt: str) -> str:
    """Stand-in for a real LLM call — see Module 6. Only the schema in
    `prompt` would ever reach a real provider; this fixed reply keeps the
    demo runnable with no API key."""
    return "result = frame.groupby('district')['value'].mean().sort_values(ascending=False).head(3)"


df = load_data()

st.sidebar.title("Filters")
province = st.sidebar.selectbox("Province", sorted(df["province"].unique()))
districts_in_province = sorted(df.loc[df["province"] == province, "district"].unique())
district = st.sidebar.multiselect("District", districts_in_province, default=districts_in_province)

filtered = df[(df["province"] == province) & (df["district"].isin(district))]

st.title("Regional Analytic Hub — Prototype")
st.caption("Synthetic data. See data/README.md before treating any number here as real.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Trend")
    trend = filtered.groupby("date", as_index=False)["value"].mean()
    st.line_chart(trend, x="date", y="value")

with col2:
    st.subheader("By district")
    by_district = filtered.groupby("district", as_index=False)["value"].mean().sort_values("value")
    st.bar_chart(by_district, x="district", y="value")

st.subheader("AI-assisted summary (schema-only pattern)")
if st.button("Generate summary"):
    schema = {c: str(t) for c, t in filtered.dtypes.items()}
    prompt = f"Schema only: {schema}. Return code for the top 3 districts by mean value."
    generated_code = call_llm(prompt)
    local_vars = {"frame": filtered}
    exec(generated_code, {}, local_vars)
    result = local_vars["result"]
    st.write("Aggregate result only, no row-level data left this process:")
    st.dataframe(result)
else:
    st.caption("Click to run the Module 6 pattern: schema to the model, code executed locally, only the "
               "aggregate result shown.")
