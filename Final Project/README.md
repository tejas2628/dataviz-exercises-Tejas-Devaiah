# NYC Property Sales Explorer

Interactive Streamlit companion to the `NYC_Property_Sales_Analysis.ipynb` notebook.

## What it shows
- KPI summary (transaction count, median price, median $/sq ft) that updates live with your filters
- **Price Trends** tab: price-per-sqft trend by borough, top neighborhoods by price growth
- **Property Types** tab: price distribution by property type and borough, price-per-unit vs. building density
- **Geography** tab: map of top 10% highest-value sales, sales volume by borough

## Filters
Borough, sale year range, property type, and sale price range — all in the sidebar, all cross-filtering every chart on every tab.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud
1. Push this `dashboard/` folder (containing `app.py`, `requirements.txt`, and `nyc_sales_cleaned.csv`) to a **public** GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, and click "New app".
3. Select the repo, branch, and set the main file path to `app.py` (adjust if `app.py` isn't at the repo root).
4. Deploy — Streamlit Cloud installs `requirements.txt` automatically and gives you a public URL.
5. Add that public repo link and the live app URL to your presentation deck and final submission.

## Data source
NYC Department of Finance — Citywide Annualized Calendar Sales Update, via NYC Open Data
(`https://data.cityofnewyork.us/City-Government/NYC-Citywide-Annualized-Calendar-Sales-Update/w2pb-icbu`).
Sample of arm's-length sale transactions, 2023–2025.
