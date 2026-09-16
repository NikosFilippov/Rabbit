import time
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
st.set_page_config(page_title="Market Analytics View", layout="wide")
st.title("Market Analytics View")
st.caption("An interactive dashboard for stocks, crypto, indices, and commodities.")
#I begin to name the stocks and seperate them into different categories so its easier for the people to understand what each
#ticker means ex(^gspc = S&P 500) and so they can select that they are looking for Comodities and it would show them a list of comodities

assets = {
    "Stocks": {
        "AAPL": "Apple",
        "MSFT": "Microsoft",
        "AMZN": "Amazon",
        "GOOG": "Google",
        "META": "Meta",
        "NFLX": "Netflix",
        "NVDA": "NVIDIA",
        "TSLA" : "Tesla",
    },
    "Crypto": {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "ADA-USD": "Cardano",
        "BNB-USD": "Binance Coin",
        "XRP-USD": "Ripple",
        "SOL-USD" : "Solana",
    },
    "Indices": {
        "^GSPC": "S&P 500",
        "^IXIC": "Nasdaq Composite",
        "^DJI": "Dow Jones",
        "^RUT" : "Russell 2000",
    },
    "Commodities": {
        "GC=F": "Gold",
        "SI=F": "Silver",
        "CL=F": "Crude Oil",
        "NG=F": "Natural Gas"
    },
}
ticker_names = {
    ticker: name
    for category in assets.values()
    for ticker, name in category.items()
}
ticker_categories = {
    ticker: category_name
    for category_name, category in assets.items()
    for ticker in category
}
all_tickers = list(ticker_names.keys())
#i am loading the data from yahoo finance
@st.cache_data(ttl=300)
def load_data(tickers):
    # the function takes the tickers that we categorized before and returns data for the last 2 years
    raw_data = yf.download(
        tickers=list(tickers),
        period="2y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        group_by="column",
    )
    if raw_data.empty:
        return pd.DataFrame()
    if isinstance(raw_data.columns, pd.MultiIndex):
        if "Close" in raw_data.columns.get_level_values(0):
            close_data = raw_data["Close"].copy()
        else:
            close_data = raw_data.xs("Close", axis=1, level=-1).copy()
    else:
        close_data = raw_data[["Close"]].copy()
        if len(tickers) == 1:
            close_data.columns = [tickers[0]]

    close_data = close_data.reset_index()

    date_column = "Date" if "Date" in close_data.columns else close_data.columns[0]

    long_data = close_data.melt(
        id_vars=[date_column],
        var_name="ticker",
        value_name="price",
    )
    long_data = long_data.rename(columns={date_column: "date"})
    long_data["date"] = pd.to_datetime(long_data["date"]).dt.tz_localize(None)
    long_data["price"] = pd.to_numeric(long_data["price"], errors="coerce")
    long_data = long_data.dropna(subset=["price"])

    long_data["name"] = long_data["ticker"].map(ticker_names)
    long_data["category"] = long_data["ticker"].map(ticker_categories)

    return long_data.sort_values(["ticker", "date"])

df = load_data(tuple(all_tickers))
if df.empty:
    #check if the data downloas was succesfull
    st.error("No market data could be downloaded. Please try again later.")
    st.stop()
#Sidebar controls that help you select the data you want displayed on the main page and the date range
# that you will show
with st.sidebar:
    st.header("Dashboard Controls")

    selected_category = st.selectbox(
        "Asset category",
        ["All"] + list(assets.keys()),
    )

    if selected_category == "All":
        available_assets = ticker_names
    else:
        available_assets = assets[selected_category]

    selected_names = st.multiselect(
        "Select assets",
        options=list(available_assets.values()),
        default=list(available_assets.values())[:3],
    )

    selected_tickers = [
        ticker
        for ticker, name in available_assets.items()
        if name in selected_names
    ]

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    start_date, end_date = st.slider(
        "Date range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
    )

    rebase_prices = st.checkbox(
        "Rebase prices to 100",
        value=False,
        help="Useful for comparing relative performance.",
    )

    st.divider()

    show_correlation = st.checkbox(
        "Show correlation matrix",
        value=False,
        help="Enable this when you want to examine relationships between assets.",
    )

    refresh_data = st.button("Refresh data")

    if refresh_data:
        st.cache_data.clear()
        st.rerun()
#validate that there have been selected tickers
if not selected_tickers:
    st.warning("Please select at least one asset from the sidebar.")
    st.stop()

#Filter data that is going to be shown depending on the sidebar selections thhe user has put
#it loads the selected tickers and the selected timeframes or shows that no data is available
#It calculates the data on a percentage scale in order to visualize certain metrics a bit better

view = df[
    df["ticker"].isin(selected_tickers)
    & df["date"].dt.date.between(start_date, end_date)
].copy()

if view.empty:
    st.warning("No data is available for the selected assets and date range.")
    st.stop()

if rebase_prices:
    view["display_price"] = view.groupby("ticker")["price"].transform(
        lambda series: series / series.iloc[0] * 100
    )
    y_axis_title = "Indexed price"
else:
    view["display_price"] = view["price"]
    y_axis_title = "Price"
#Calculating the summaries
latest_rows = (
    view.sort_values("date")
    .groupby("ticker", as_index=False)
    .tail(1)
    .copy()
)

first_rows = (
    view.sort_values("date")
    .groupby("ticker", as_index=False)
    .head(1)
    .copy()
)

summary = latest_rows[
    ["ticker", "name", "category", "date", "price"]
].rename(
    columns={
        "date": "latest_date",
        "price": "latest_price",
    }
)

first_prices = first_rows[["ticker", "price"]].rename(
    columns={"price": "first_price"}
)

summary = summary.merge(first_prices, on="ticker", how="left")
summary["return_pct"] = (
    (summary["latest_price"] - summary["first_price"])
    / summary["first_price"]
    * 100
)

summary = summary.sort_values("return_pct", ascending=False)

latest_date = view["date"].max().strftime("%d %b %Y")
#Top metrics for the data selected
c1, c2, c3, c4 = st.columns(4)

c1.metric("Selected assets", len(selected_tickers))
c2.metric("Data through", latest_date)

average_return = summary["return_pct"].mean()
best_asset = summary.iloc[0]["name"]
best_return = summary.iloc[0]["return_pct"]

c3.metric("Average return", f"{average_return:.2f}%")
c4.metric("Top performer", f"{best_asset} ({best_return:.2f}%)")


st.divider()
#Main Chart of the project
st.subheader("Price Development")

chart = px.line(
    view,
    x="date",
    y="display_price",
    color="name",
    line_group="ticker",
    title="Historical price movement",
    labels={
        "date": "Date",
        "display_price": y_axis_title,
        "name": "Asset",
    },
)

chart.update_layout(
    hovermode="x unified",
    legend_title_text="Asset",
    margin=dict(l=10, r=10, t=50, b=10),
)

st.plotly_chart(chart, use_container_width=True)

#Performance table
st.subheader("Performance Overview")

performance_table = summary[
    ["name", "category", "latest_price", "return_pct", "latest_date"]
].copy()

performance_table = performance_table.rename(
    columns={
        "name": "Asset",
        "category": "Category",
        "latest_price": "Latest Price",
        "return_pct": "Return (%)",
        "latest_date": "Latest Date",
    }
)

performance_table["Latest Price"] = performance_table["Latest Price"].round(4)
performance_table["Return (%)"] = performance_table["Return (%)"].round(2)
performance_table["Latest Date"] = performance_table["Latest Date"].dt.strftime(
    "%Y-%m-%d"
)

st.dataframe(
    performance_table,
    use_container_width=True,
    hide_index=True,
)
#Correlation Matrix
if show_correlation:
    st.divider()
    st.subheader("Correlation Matrix")

    correlation_data = view.pivot(
        index="date",
        columns="name",
        values="price",
    )

    correlation_returns = correlation_data.pct_change().dropna()

    if correlation_returns.shape[1] < 2:
        st.info("Select at least two assets to calculate correlation.")
    else:
        correlation_matrix = correlation_returns.corr()

        fig, ax = plt.subplots(figsize=(10, 6))

        sns.heatmap(
            correlation_matrix,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            center=0,
            linewidths=0.5,
            ax=ax,
        )

        ax.set_title("Correlation of Daily Returns")
        st.pyplot(fig)
        plt.close(fig)
#Finally the download buttons and stating i got the data from yahoo finance
st.divider()
st.subheader("Export Data")

download_data = view[
    ["date", "ticker", "name", "category", "price", "display_price"]
].copy()

download_data["date"] = download_data["date"].dt.strftime("%Y-%m-%d")

csv_data = download_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered data as CSV",
    data=csv_data,
    file_name="market_dashboard_data.csv",
    mime="text/csv",
)

st.caption(
    "Data source: Yahoo Finance through yfinance. "
    "Prices represent the latest available downloaded observations and may be delayed."
)


