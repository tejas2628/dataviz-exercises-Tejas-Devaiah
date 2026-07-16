
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    path = '/Users/tejasdevaiah/Desktop/DataViz Tejas /dataviz-exercises-Tejas-Devaiah/data/co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")
print(df.head())
print(df.columns.tolist())

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
#   a) st.selectbox for Region (with 'All')
#   b) st.multiselect for Countries (updates based on region — chained)
#   c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
#   d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
#   e) st.checkbox labelled "Show only top emitter highlighted"
#
# Guards:
#   - empty countries → st.warning + st.stop()
#   - incomplete date_input → st.warning + st.stop()
# Convert date_input result to pd.Timestamp before filtering.
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

# a) Region
    regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
    selected_region = st.selectbox("Region", regions)

    # b) Countries (chained)
    if selected_region == "All":
        available_countries = sorted(df["Country"].unique())
    else:
        available_countries = sorted(
            df[df["Region"] == selected_region]["Country"].unique()
        )

    selected_countries = st.multiselect(
        "Countries",
        available_countries,
        default=available_countries[:5]
    )

    if len(selected_countries) == 0:
        st.warning("Please select at least one country.")
        st.stop()

    # c) Date Range
    min_date = df["Date"].min()
    max_date = df["Date"].max()

    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if len(date_range) != 2:
        st.warning("Please select a start and end date.")
        st.stop()

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    # d) Metric
    metric = st.radio(
        "Metric",
        ["Total CO2 (Mt)", "CO2 per capita"]
    )

    # e) Checkbox
    highlight = st.checkbox("Show only top emitter highlighted")

filtered = df.copy()

if selected_region != "All":
    filtered = filtered[filtered["Region"] == selected_region]

filtered = filtered[
    filtered["Country"].isin(selected_countries)
]

filtered = filtered[
    (filtered["Date"] >= start_date)
    & (filtered["Date"] <= end_date)
]

metric_column = (
    "CO2_Mt"
    if metric == "Total CO2 (Mt)"
    else "CO2_per_capita"
)
# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# Show: "X countries | Region | Date range | Metric"
# BBD rule: always show users how many records match current filters
# ─────────────────────────────────────────────────────────────────────────────
st.caption(
    f"""
**{len(selected_countries)} countries**
| **Region:** {selected_region}
| **Date:** {start_date.year}-{end_date.year}
| **Metric:** {metric}
"""
)



# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
#   Left: line chart — selected metric over time, one line per country
#         If "Show only top emitter highlighted" checkbox is on:
#           - grey all lines except the highest emitter in the date range
#           - label that country at the end of its line (SWD grey-and-highlight)
#   Right: bar chart — ranking for the last year in selected date range
#
# BBD colour requirement: name the colour type in a comment next to each chart
# SWD requirements: white background, insight title, use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    # Line chart
    # YOUR CODE HERE
    st.subheader("CO₂ emissions over time")

    # Qualitative colour palette

    if highlight:

        totals = (
            filtered.groupby("Country")[metric_column]
            .sum()
            .sort_values(ascending=False)
        )

        top = totals.index[0]

        filtered["Highlight"] = filtered["Country"].apply(
            lambda x: top if x == top else "Other"
        )

        fig = px.line(
            filtered,
            x="Year",
            y=metric_column,
            color="Highlight",
            line_group="Country",
            hover_name="Country",
            color_discrete_map={
                top: "red",
                "Other": "lightgrey",
            },
        )

        last_point = filtered[
            (filtered["Country"] == top)
            & (filtered["Year"] == filtered["Year"].max())
        ]

        fig.add_annotation(
            x=last_point["Year"].iloc[0],
            y=last_point[metric_column].iloc[0],
            text=top,
            showarrow=False,
            xshift=20,
        )

    else:

        fig = px.line(
            filtered,
            x="Year",
            y=metric_column,
            color="Country",
        )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    st.plotly_chart(fig, use_container_width=True)

    pass

with col_right:
    # Bar chart
    # YOUR CODE HERE
    st.subheader("Ranking in Final Year")

    ranking = (
        filtered[
            filtered["Year"] == filtered["Year"].max()
        ]
        .sort_values(metric_column, ascending=False)
    )

    # Sequential colour palette

    fig2 = px.bar(
        ranking,
        x=metric_column,
        y="Country",
        orientation="h",
        color=metric_column,
    )

    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(categoryorder="total ascending"),
    )

    st.plotly_chart(fig2, use_container_width=True)
    pass


# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
#   - Total CO2 in last year of selected range (sum across selected countries)
#   - % change from first to last year
#   - Country with highest emissions in last year
# ─────────────────────────────────────────────────────────────────────────────
last_year = filtered["Year"].max()
first_year = filtered["Year"].min()

last_df = filtered[filtered["Year"] == last_year]
first_df = filtered[filtered["Year"] == first_year]

total_last = last_df[metric_column].sum()
total_first = first_df[metric_column].sum()

if total_first != 0:
    pct_change = ((total_last - total_first) / total_first) * 100
else:
    pct_change = 0

top_country = (
    last_df.sort_values(metric_column, ascending=False)
    .iloc[0]["Country"]
)

k1, k2, k3 = st.columns(3)

k1.metric("Total Emissions (Last Year)", f"{total_last:,.2f}")

k2.metric(
    "% Change",
    f"{pct_change:.1f}%"
)

k3.metric(
    "Top Emitter",
    top_country
)