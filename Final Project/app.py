"""
NYC Property Sales Dashboard (2023-2025)
Data viz final project -- interactive Streamlit companion to the analysis notebook.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------- Page setup ----------------
st.set_page_config(page_title="NYC Property Sales Explorer", layout="wide", page_icon="🏙️")

# ---------------- CVD-safe palette (Okabe-Ito), consistent with the notebook ----------------
GREY = "#B0B0B0"
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILLION = "#D55E00"
PURPLE = "#CC79A7"
YELLOW = "#F0E442"
BOROUGH_COLORS = {
    "Manhattan": BLUE, "Brooklyn": ORANGE, "Queens": GREEN,
    "Bronx": VERMILLION, "Staten Island": PURPLE,
}
BASE_LAYOUT = dict(
    template="plotly_white",
    font=dict(family="Helvetica, Arial, sans-serif", size=13, color="#333333"),
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=60, r=30, t=70, b=50),
)


@st.cache_data
def load_data():
    df = pd.read_csv("nyc_sales_cleaned.csv", parse_dates=["sale_date"])
    df["price_per_sqft"] = df["sale_price"] / df["gross_square_feet"]
    df.loc[~np.isfinite(df["price_per_sqft"]), "price_per_sqft"] = np.nan
    df = df[(df["price_per_sqft"].isna()) | (df["price_per_sqft"].between(20, 5000))]
    return df


df = load_data()

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")

boroughs = sorted(df["borough"].dropna().unique())
sel_boroughs = st.sidebar.multiselect("Borough", boroughs, default=boroughs)

years = sorted(df["sale_year"].dropna().unique().astype(int))
sel_years = st.sidebar.select_slider(
    "Sale year range", options=years, value=(min(years), max(years))
)

top_types = df["property_type"].value_counts().head(10).index.tolist()
sel_types = st.sidebar.multiselect("Property type", top_types, default=top_types)

price_min, price_max = int(df["sale_price"].min()), int(df["sale_price"].quantile(0.99))
sel_price = st.sidebar.slider(
    "Sale price range ($)", min_value=price_min, max_value=price_max,
    value=(price_min, price_max), step=10000, format="$%d"
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Source: NYC Dept. of Finance, Citywide Annualized Calendar Sales Update "
    "(NYC Open Data). Sample of arm's-length sales, 2023-2025."
)

mask = (
    df["borough"].isin(sel_boroughs)
    & df["sale_year"].between(sel_years[0], sel_years[1])
    & df["property_type"].isin(sel_types)
    & df["sale_price"].between(sel_price[0], sel_price[1])
)
fdf = df[mask]

# ---------------- Header + KPIs ----------------
st.title("NYC Property Sales Explorer")
st.caption("2023-2025 · Real recorded sale transactions across all five boroughs")

if fdf.empty:
    st.warning("No transactions match the current filters. Try widening your selection.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Transactions", f"{len(fdf):,}")
k2.metric("Median sale price", f"${fdf['sale_price'].median():,.0f}")
k3.metric("Median $ / sq ft", f"${fdf['price_per_sqft'].median():,.0f}" if fdf["price_per_sqft"].notna().any() else "n/a")
k4.metric("Boroughs shown", f"{fdf['borough'].nunique()} of {len(boroughs)}")

st.markdown("---")

# ---------------- Tabs ----------------
tab1, tab2, tab3 = st.tabs(["Price Trends", "Property Types", "Geography"])

with tab1:
    st.subheader("Price per square foot by borough over time")
    g = fdf.dropna(subset=["price_per_sqft"]).groupby(["borough", "sale_year"])["price_per_sqft"].median().reset_index()
    fig = go.Figure()
    for b in sel_boroughs:
        sub = g[g.borough == b]
        fig.add_trace(go.Scatter(x=sub.sale_year, y=sub.price_per_sqft, mode="lines+markers",
                                  name=b, line=dict(color=BOROUGH_COLORS.get(b, GREY), width=3)))
    fig.update_layout(**BASE_LAYOUT, xaxis_title="", yaxis_title="Median $ / sq ft", legend_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top neighborhoods by median price growth")
    nbhd_year = fdf.groupby(["neighborhood", "sale_year"])["sale_price"].median().reset_index()
    piv = nbhd_year.pivot(index="neighborhood", columns="sale_year", values="sale_price").dropna()
    if piv.shape[1] >= 2:
        first_col, last_col = piv.columns.min(), piv.columns.max()
        piv["pct_growth"] = (piv[last_col] - piv[first_col]) / piv[first_col] * 100
        top_growth = piv.sort_values("pct_growth", ascending=False).head(12)
        fig2 = go.Figure(go.Bar(x=top_growth["pct_growth"], y=top_growth.index, orientation="h", marker_color=BLUE))
        fig2.update_layout(**BASE_LAYOUT, xaxis_title=f"% change in median price, {first_col}→{last_col}", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Select a wider year range to see growth comparisons.")

with tab2:
    st.subheader("Sale price by property type")
    fig3 = px.box(fdf, x="property_type", y="sale_price", color="borough",
                  color_discrete_map=BOROUGH_COLORS, points=False)
    fig3.update_layout(**BASE_LAYOUT, xaxis_title="", yaxis_title="Sale price ($)", legend_title="")
    fig3.update_xaxes(tickangle=30)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Price per unit vs. building density")
    d7 = fdf.dropna(subset=["total_units", "sale_price"])
    d7 = d7[d7.total_units > 0]
    d7 = d7.assign(price_per_unit=d7["sale_price"] / d7["total_units"])
    d7 = d7[d7.price_per_unit.between(10000, 5000000)]
    if len(d7) > 5:
        fig4 = px.scatter(d7, x="total_units", y="price_per_unit", color="borough",
                           color_discrete_map=BOROUGH_COLORS, opacity=0.6, log_x=True)
        fig4.update_layout(**BASE_LAYOUT, xaxis_title="Total units in building (log scale)",
                            yaxis_title="Price per unit ($)", legend_title="")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Not enough data in this selection to show density vs. price.")

with tab3:
    st.subheader("Where the highest-value sales are happening")
    thresh = fdf["sale_price"].quantile(0.9)
    d12 = fdf.dropna(subset=["latitude", "longitude"]).copy()
    d12["tier"] = np.where(d12.sale_price >= thresh, "Top 10% by price", "Rest of market")
    fig5 = px.scatter_map(
        d12, lat="latitude", lon="longitude", color="tier",
        color_discrete_map={"Top 10% by price": VERMILLION, "Rest of market": GREY},
        opacity=0.55, zoom=9, height=600,
        hover_data=["neighborhood", "property_type", "sale_price"],
    )
    fig5.update_layout(map_style="carto-positron", font=BASE_LAYOUT["font"], margin=BASE_LAYOUT["margin"])
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Sales volume by borough")
    vol = fdf["borough"].value_counts().reset_index()
    vol.columns = ["borough", "count"]
    fig6 = go.Figure(go.Bar(x=vol["borough"], y=vol["count"],
                             marker_color=[BOROUGH_COLORS.get(b, GREY) for b in vol["borough"]]))
    fig6.update_layout(**BASE_LAYOUT, xaxis_title="", yaxis_title="Number of sales")
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption("Full 12-question analysis available in the companion Jupyter notebook.")
