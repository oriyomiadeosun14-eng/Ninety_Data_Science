import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import lets_plot as lp
    import yfinance as yf
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from itables import to_html_datatable
    lp.LetsPlot.setup_html()
    return go, lp, make_subplots, mo, pl, to_html_datatable, yf


@app.cell
def _(mo):
    mo.md("""
    # CS-09: Interacting with Time
    ## Stock Performance Analysis for Investment Meeting

    > **Scenario:** You have $25,000 to invest and a 30-minute meeting with a
    > savvy investment friend who has given you 11 tickers to evaluate.
    > This notebook builds a rapid-fire suite of visualisations so you can
    > answer questions about each stock within seconds.
    >
    > **Tickers:** CXW · F · GM · JCP · KR · WDC · NKE · T · WDAY · WFC · WMT
    >
    > **Tools:** `yfinance` · `polars` · `lets-plot` · `plotly` · `itables`
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Reading Notes

    ### 1. yfinance Tickers API
    `yf.Tickers("AAPL MSFT ...")` fetches data for multiple tickers at once.
    Key method: `.history(period, interval, start, end, auto_adjust, threads)`
    Returns a pandas DataFrame with multi-level columns: (field, ticker).
    We extract `["Close", "Open", "High", "Low", "Volume"]` then convert to Polars.

    ### 2. ITables in Marimo
    `init_notebook_mode()` and `show()` do NOT work in Marimo.
    Two valid approaches:
    - `from itables.widget import ITable` — renders as a widget
    - `from itables import to_html_datatable` + `mo.iframe(html, connected=True)`
      — renders as a full interactive DataTable inside an iframe.
    We use the `to_html_datatable` + `mo.iframe` approach since it gives the
    most complete DataTables experience (search, sort, paginate, filter).

    ### 3. Plotly for Volume Analysis
    `plotly.graph_objects` allows layering a candlestick chart on top of a
    volume bar chart using `make_subplots(rows=2, shared_xaxes=True)`.
    This is the standard view traders use to correlate price moves with volume.
    Adding 20-day & 50-day SMAs and a range selector turns it into a real
    decision tool, not just a chart.

    ### 4. Visualisation Notes (this revision)
    - Date columns are passed to Lets-Plot as proper `pl.Date`, rendered via
      `scale_x_datetime()` — no string-cast hack, proper year ticks.
    - All chart labels are pre-formatted in Polars with `pl.format()` rather
      than format strings inside `geom_text`.
    - Step 5 uses the "spaghetti highlight" technique — only the top 3 and
      bottom 3 performers are coloured; everything else fades to grey.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 1: Pull 5-Year Historical Data
    """)
    return


@app.cell
def _(pl, yf):
    TICKER_NAMES = {
        "CXW":  "CoreCivic",
        "F":    "Ford Motor",
        "GM":   "General Motors",
        "JCP":  "JCPenney",
        "KR":   "Kroger",
        "WDC":  "Western Digital",
        "NKE":  "Nike",
        "T":    "AT&T",
        "WDAY": "Workday",
        "WFC":  "Wells Fargo",
        "WMT":  "Walmart",
    }
    TICKERS = list(TICKER_NAMES.keys())

    raw = yf.Tickers(" ".join(TICKERS)).history(
        period="5y", interval="1d", auto_adjust=True
    )

    fields = ["Open", "High", "Low", "Close", "Volume"]

    frames = []
    for ticker in TICKERS:
        try:
            pdf = (
                raw.loc[:, (slice(None), ticker)]
                   .droplevel(1, axis=1)
                   .reset_index()[["Date"] + fields]
            )
            frames.append(
                pl.from_pandas(pdf)
                .rename({
                    "Date":   "date",
                    "Open":   "open",
                    "High":   "high",
                    "Low":    "low",
                    "Close":  "close",
                    "Volume": "volume",
                })
                .with_columns([
                    pl.col("date").cast(pl.Date),
                    pl.col("volume").cast(pl.Int64),
                    pl.lit(ticker).alias("ticker"),
                    pl.lit(TICKER_NAMES[ticker]).alias("company"),
                ])
                .select(["date", "ticker", "company",
                         "open", "high", "low", "close", "volume"])
            )
        except Exception as e:
            print(f"Skipping {ticker}: {e}")

    stock = pl.concat(frames).sort(["ticker", "date"])

    print(f"Shape: {stock.shape}")
    print(f"Tickers: {stock['ticker'].unique().sort().to_list()}")
    print(f"Date range: {stock['date'].min()} → {stock['date'].max()}")
    stock.head(10)
    return TICKERS, TICKER_NAMES, stock


@app.cell
def _(pl, stock):
    # Compute total returns ONCE, reuse downstream (Step 5 highlight, Step 9 bars, Step 10 scatter)
    overall = (
        stock.sort(["ticker", "date"])
        .group_by(["ticker", "company"])
        .agg([
            pl.col("close").first().alias("start_price"),
            pl.col("close").last().alias("end_price"),
        ])
        .with_columns(
            (((pl.col("end_price") - pl.col("start_price"))
              / pl.col("start_price")) * 100)
            .round(1)
            .alias("total_return")
        )
        .with_columns(
            # Pre-formatted label, e.g. "+23.4%" or "-12.1%"
            pl.format(
                "{}{}%",
                pl.when(pl.col("total_return") >= 0).then(
                    pl.lit("+")).otherwise(pl.lit("")),
                pl.col("total_return"),
            ).alias("return_label")
        )
        .sort("total_return", descending=True)
    )
    return (overall,)


@app.cell
def _(mo, pl, stock):
    quality = (
        stock.group_by("ticker")
        .agg([
            pl.len().alias("rows"),
            pl.col("close").null_count().alias("null_close"),
            pl.col("close").min().round(2).alias("min_close"),
            pl.col("close").max().round(2).alias("max_close"),
            pl.col("date").min().alias("first_date"),
            pl.col("date").max().alias("last_date"),
        ])
        .sort("ticker")
    )

    mo.md(
        "## Step 2: Data Quality Check\n\n"
        + quality.to_pandas().to_markdown(index=False)
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 3: Interactive Data Table

    Searchable, sortable, paginated table of all OHLCV data.
    Use the search box to filter by ticker or company name, or click column headers to sort.
    """)
    return


@app.cell
def _(mo, stock, to_html_datatable):
    table_html = to_html_datatable(
        stock.to_pandas(),
        connected=True,
        caption="5-Year Daily OHLCV Data — All Tickers",
        style="width:100%;",
        classes="display compact",
        lengthMenu=[10, 25, 50, 100],
        pageLength=25,
    )
    mo.iframe(table_html, height=450)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 4: 5-Year Closing Price Performance

    Each panel shows one ticker's price history. Free y-axis scales so
    low-price stocks (JCP, F) aren't squished next to high-price ones (WMT, WDAY).
    Panel colour reflects 5-year total return — green = gain, red = loss.
    """)
    return


@app.cell
def _(lp, overall, pl, stock):
    # Join total_return so we can colour each facet by performance sign
    price_panels = (
        stock.join(overall.select(["ticker", "total_return"]), on="ticker")
        .with_columns(
            pl.when(pl.col("total_return") >= 0)
              .then(pl.lit("Gain"))
              .otherwise(pl.lit("Loss"))
              .alias("perf_group")
        )
    )

    (
        lp.ggplot(price_panels.to_pandas(),
                  lp.aes(x="date", y="close", color="perf_group"))
        + lp.geom_line(size=0.7, alpha=0.9, show_legend=False)
        + lp.facet_wrap("company", ncol=3, scales="free_y")
        + lp.scale_x_datetime(format="%Y")
        + lp.scale_color_manual(values={"Gain": "#1a9850", "Loss": "#d73027"})
        + lp.labs(
            title="5-Year Daily Closing Price by Company",
            subtitle="Free y-scales per panel. Green panels = 5-yr net gain, red = net loss.",
            x="Year",
            y="Closing Price ($)",
        )
        + lp.theme_light()
        + lp.theme(
            plot_title=lp.element_text(size=14),
            strip_text=lp.element_text(size=10),
            legend_position="none",
            axis_text_x=lp.element_text(size=8),
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 5: Normalised Performance — Top & Bottom Highlighted

    All tickers rebased to $100 at the start of the 5-year window. To cut through
    spaghetti, only the **top 3** and **bottom 3** performers are coloured;
    everything in the middle fades to grey. A value of 150 = +50% since start.
    """)
    return


@app.cell
def _(lp, overall, pl, stock):
    top3 = overall["company"].head(3).to_list()
    bottom3 = overall["company"].tail(3).to_list()
    highlighted = top3 + bottom3

    first_close = (
        stock.sort(["ticker", "date"])
        .group_by("ticker")
        .agg(pl.col("close").first().alias("first_close"))
    )

    rebased = (
        stock.join(first_close, on="ticker")
        .with_columns(
            ((pl.col("close") / pl.col("first_close")) * 100)
            .round(2)
            .alias("rebased")
        )
        .sort(["ticker", "date"])
    )

    rebased_other = rebased.filter(~pl.col("company").is_in(highlighted))
    rebased_hi = rebased.filter(pl.col("company").is_in(highlighted))

    (
        lp.ggplot()
        + lp.geom_line(
            data=rebased_other.to_pandas(),
            mapping=lp.aes(x="date", y="rebased", group="company"),
            color="#cccccc", size=0.5, alpha=0.7, show_legend=False,
        )
        + lp.geom_line(
            data=rebased_hi.to_pandas(),
            mapping=lp.aes(x="date", y="rebased",
                           color="company", group="company"),
            size=1.1, alpha=0.95,
        )
        + lp.geom_hline(yintercept=100, linetype="dashed",
                        color="#666666", size=0.6)
        + lp.scale_x_datetime(format="%Y")
        + lp.scale_color_brewer(palette="Paired")
        + lp.labs(
            title="5-Year Normalised Performance — Top 3 & Bottom 3 Highlighted",
            subtitle="Grey = middle performers. Dashed line = $100 starting value.",
            x="Year",
            y="Rebased Price ($100 start)",
            color="Highlighted Company",
        )
        + lp.theme_light()
        + lp.theme(legend_position="right")
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 6: Annual Returns Heatmap

    Companies are sorted top-to-bottom by 5-year total return, so consistent
    winners cluster at the top. Cells show annual % return — green = positive,
    red = negative.
    """)
    return


@app.cell
def _(lp, overall, pl, stock):
    # Order y-axis by overall return (best on top)
    company_order_heatmap = overall["company"].reverse().to_list()

    annual = (
        stock.with_columns(pl.col("date").dt.year().alias("year"))
        .sort(["ticker", "date"])
        .group_by(["ticker", "year", "company"])
        .agg([
            pl.col("close").first().alias("start_price"),
            pl.col("close").last().alias("end_price"),
        ])
        .with_columns(
            (((pl.col("end_price") - pl.col("start_price"))
              / pl.col("start_price")) * 100)
            .round(1)
            .alias("annual_return")
        )
        .with_columns(
            # Pre-format label as Polars string — no format= in geom_text
            pl.format("{}%", pl.col("annual_return")).alias("annual_label")
        )
        .sort(["company", "year"])
    )

    (
        lp.ggplot(annual.to_pandas(),
                  lp.aes(x="year", y="company", fill="annual_return"))
        + lp.geom_tile(color="white", size=0.6)
        + lp.geom_text(lp.aes(label="annual_label"), size=8, color="#222222")
        + lp.scale_fill_gradient2(
            low="#d73027", mid="#ffffff", high="#1a9850", midpoint=0,
            guide=lp.guide_colorbar(title="Annual Return (%)"),
        )
        + lp.scale_x_continuous(breaks=annual["year"].unique().sort().to_list())
        + lp.scale_y_discrete(limits=company_order_heatmap)
        + lp.labs(
            title="Annual Return Heatmap — Sorted by 5-Year Total Return",
            subtitle="Top of chart = best 5-year performer. Green = positive year, red = negative.",
            x="Year",
            y="Company",
        )
        + lp.theme_light()
        + lp.theme(
            legend_position="right",
            axis_text_x=lp.element_text(angle=0),
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 7: Rolling 90-Day Volatility

    Volatility = standard deviation of daily returns over a 90-day rolling
    window. Higher = riskier. The dashed reference line is the cross-company
    median, so it's instantly visible which stocks sit above or below average.
    """)
    return


@app.cell
def _(lp, pl, stock):
    volatility = (
        stock.sort(["ticker", "date"])
        .with_columns(
            pl.col("close").pct_change().over("ticker").alias("daily_return")
        )
        .with_columns(
            (pl.col("daily_return").rolling_std(
                window_size=90).over("ticker") * 100)
            .round(2)
            .alias("volatility_90d")
        )
        .drop_nulls("volatility_90d")
    )

    median_vol = volatility["volatility_90d"].median()

    (
        lp.ggplot(volatility.to_pandas(),
                  lp.aes(x="date", y="volatility_90d", color="company"))
        + lp.geom_line(size=0.7, alpha=0.9, show_legend=False)
        + lp.geom_hline(yintercept=median_vol, linetype="dashed",
                        color="#666666", size=0.5)
        + lp.facet_wrap("company", ncol=3, scales="free_y")
        + lp.scale_x_datetime(format="%Y")
        + lp.scale_color_brewer(palette="Paired")
        + lp.labs(
            title="Rolling 90-Day Volatility by Company",
            subtitle=f"Std-dev of daily returns over 90 days. Dashed line = cross-stock median ({median_vol:.2f}%).",
            x="Year",
            y="Volatility (%)",
        )
        + lp.theme_light()
        + lp.theme(
            legend_position="none",
            strip_text=lp.element_text(size=10),
            axis_text_x=lp.element_text(size=8),
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 8: Volume & Price — Plotly Interactive Chart

    Candlestick + volume + 20-day and 50-day moving averages. Use the range
    buttons (1M · 3M · 6M · 1Y · All) to zoom in. The SMAs surface trend:
    price above both = uptrend, price below both = downtrend, 20 crossing 50 =
    momentum shift.
    """)
    return


@app.cell
def _(TICKER_NAMES, go, make_subplots, pl, stock):
    def make_candlestick_volume(ticker_sym: str, n_days: int = 365):
        # Compute SMAs on the FULL series first, then tail — so SMAs are populated
        # from day 1 of the visible window
        ticker_df = (
            stock.filter(pl.col("ticker") == ticker_sym)
            .sort("date")
            .with_columns([
                pl.col("close").rolling_mean(window_size=20).alias("sma20"),
                pl.col("close").rolling_mean(window_size=50).alias("sma50"),
            ])
            .tail(n_days)
        )

        dates = ticker_df["date"].to_list()
        opens = ticker_df["open"].to_list()
        highs = ticker_df["high"].to_list()
        lows = ticker_df["low"].to_list()
        closes = ticker_df["close"].to_list()
        volumes = ticker_df["volume"].to_list()
        sma20 = ticker_df["sma20"].to_list()
        sma50 = ticker_df["sma50"].to_list()

        colors = [
            "#26a69a" if c >= o else "#ef5350"
            for c, o in zip(closes, opens)
        ]

        company_name = TICKER_NAMES.get(ticker_sym, ticker_sym)

        # Window return for subtitle
        window_return = (closes[-1] - closes[0]) / closes[0] * 100
        arrow = "▲" if window_return >= 0 else "▼"
        ret_color = "#1a9850" if window_return >= 0 else "#d73027"

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.72, 0.28],
            subplot_titles=("", ""),
        )

        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=dates, open=opens, high=highs, low=lows, close=closes,
                name="OHLC",
                increasing_line_color="#26a69a",
                decreasing_line_color="#ef5350",
                increasing_fillcolor="#26a69a",
                decreasing_fillcolor="#ef5350",
                showlegend=False,
            ),
            row=1, col=1,
        )

        # Moving averages
        fig.add_trace(
            go.Scatter(
                x=dates, y=sma20, name="SMA 20",
                line=dict(color="#ff9800", width=1.5),
                hovertemplate="SMA 20: $%{y:.2f}<extra></extra>",
            ),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=dates, y=sma50, name="SMA 50",
                line=dict(color="#3f51b5", width=1.5),
                hovertemplate="SMA 50: $%{y:.2f}<extra></extra>",
            ),
            row=1, col=1,
        )

        # Volume bars
        fig.add_trace(
            go.Bar(
                x=dates, y=volumes,
                marker_color=colors,
                name="Volume",
                showlegend=False,
                hovertemplate="Volume: %{y:,.0f}<extra></extra>",
            ),
            row=2, col=1,
        )

        fig.update_layout(
            height=640,
            xaxis_rangeslider_visible=False,
            template="plotly_white",
            title=dict(
                text=(
                    f"<b>{company_name} ({ticker_sym})</b> — Candlestick & Volume"
                    f"<br><span style='font-size:12px;color:{ret_color}'>"
                    f"{arrow} {window_return:+.1f}% over last {n_days} trading days</span>"
                ),
                font=dict(size=15),
                x=0.02, xanchor="left",
            ),
            font=dict(family="Inter, Arial, sans-serif"),
            margin=dict(l=50, r=30, t=80, b=40),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1,
            ),
            hovermode="x unified",
        )

        # Range selector buttons on the bottom (volume) x-axis so they're shared
        fig.update_xaxes(
            rangeselector=dict(
                buttons=[
                    dict(count=1,  label="1M",
                         step="month", stepmode="backward"),
                    dict(count=3,  label="3M",
                         step="month", stepmode="backward"),
                    dict(count=6,  label="6M",
                         step="month", stepmode="backward"),
                    dict(count=1,  label="1Y",
                         step="year",  stepmode="backward"),
                    dict(step="all", label="All"),
                ],
                bgcolor="#f5f5f5",
                activecolor="#3f51b5",
                font=dict(size=11),
            ),
            row=1, col=1,
        )
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume",    row=2, col=1)

        return fig

    return (make_candlestick_volume,)


@app.cell
def _(TICKERS, TICKER_NAMES, mo):
    ticker_select = mo.ui.dropdown(
        # options is {company_name: ticker_symbol} — so `value` must be a
        # company name (a key), not the ticker symbol (a value).
        options={TICKER_NAMES[t]: t for t in TICKERS},
        value="Kroger",   # maps internally to "KR"
        label="Select Company",
    )
    ticker_select
    return (ticker_select,)


@app.cell
def _(make_candlestick_volume, mo, ticker_select):
    mo.ui.plotly(make_candlestick_volume(ticker_select.value, n_days=365))
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 9: Overall 5-Year Return Ranking

    Horizontal bars so the full company names sit comfortably on the y-axis.
    Sorted highest-to-lowest with green/red colour-coding by sign — the single
    most important chart for the investment conversation.
    """)
    return


@app.cell
def _(lp, overall):
    # Reverse so the biggest gainer appears at the TOP of a horizontal bar chart
    company_order_bars = overall["company"].reverse().to_list()

    (
        lp.ggplot(overall.to_pandas(),
                  lp.aes(x="company", y="total_return", fill="total_return"))
        + lp.geom_bar(stat="identity", show_legend=False, width=0.7)
        + lp.geom_text(
            lp.aes(label="return_label"),
            hjust=-0.15, size=9,
        )
        + lp.geom_hline(yintercept=0, color="#333333", size=0.5)
        + lp.scale_x_discrete(limits=company_order_bars)
        + lp.scale_fill_gradient2(
            low="#d73027", mid="#ffffbf", high="#1a9850", midpoint=0,
            guide=lp.guide_colorbar(title="Return (%)"),
        )
        + lp.coord_flip()
        + lp.labs(
            title="5-Year Total Return by Company",
            subtitle="Sorted highest to lowest. Green = gain, red = loss.",
            x="",
            y="Total Return (%)",
        )
        + lp.theme_light()
        + lp.theme(
            plot_title=lp.element_text(size=14),
            axis_text_y=lp.element_text(size=10),
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 10: Risk vs Return Scatter — with Quadrants

    Each bubble is a company. X = annualised volatility (risk),
    Y = total 5-year return (reward). Dashed lines split the chart into
    four quadrants at the **median** risk and return — so the labels
    *Ideal · Aggressive · Defensive · Avoid* describe real, data-driven regions.
    """)
    return


@app.cell
def _(lp, overall, pl, stock):
    avg_vol = (
        stock.sort(["ticker", "date"])
        .with_columns(
            pl.col("close").pct_change().over("ticker").alias("daily_return")
        )
        .group_by("ticker")
        .agg(
            (pl.col("daily_return").std() * 100 * (252 ** 0.5))
            .round(2)
            .alias("annual_volatility")
        )
    )

    risk_return = overall.join(avg_vol, on="ticker")

    median_risk = risk_return["annual_volatility"].median()
    median_return = risk_return["total_return"].median()

    # Quadrant annotation positions (corners of the data range)
    xmin = risk_return["annual_volatility"].min()
    xmax = risk_return["annual_volatility"].max()
    ymin = risk_return["total_return"].min()
    ymax = risk_return["total_return"].max()

    (
        lp.ggplot(risk_return.to_pandas(),
                  lp.aes(x="annual_volatility", y="total_return"))
        # Quadrant divider lines at the medians
        + lp.geom_vline(xintercept=median_risk,
                        linetype="dashed", color="#aaaaaa")
        + lp.geom_hline(yintercept=median_return,
                        linetype="dashed", color="#aaaaaa")
        # Zero-return reference line
        + lp.geom_hline(yintercept=0, color="#666666", size=0.4)
        + lp.geom_point(lp.aes(color="total_return"), size=7, alpha=0.9)
        + lp.geom_text(lp.aes(label="company"),
                       vjust=-1.2, size=9, show_legend=False)
        # Quadrant labels
        + lp.geom_text(x=xmin, y=ymax,
                       label="Ideal\n(high return,\nlow risk)",
                       color="#1a9850", size=8, hjust=0, vjust=1,
                       fontface="bold")
        + lp.geom_text(x=xmax, y=ymax,
                       label="Aggressive",
                       color="#888888", size=8, hjust=1, vjust=1)
        + lp.geom_text(x=xmin, y=ymin,
                       label="Defensive",
                       color="#888888", size=8, hjust=0, vjust=0)
        + lp.geom_text(x=xmax, y=ymin,
                       label="Avoid\n(low return,\nhigh risk)",
                       color="#d73027", size=8, hjust=1, vjust=0,
                       fontface="bold")
        + lp.scale_color_gradient2(
            low="#d73027", mid="#ffffbf", high="#1a9850", midpoint=0,
            guide=lp.guide_colorbar(title="Return (%)"),
        )
        + lp.labs(
            title="Risk vs Return — All 11 Companies",
            subtitle=f"Dashed lines = median risk ({median_risk:.1f}%) and median return ({median_return:.1f}%).",
            x="Annualised Volatility (%)",
            y="5-Year Total Return (%)",
        )
        + lp.theme_light()
        + lp.theme(legend_position="right")
    )
    return (risk_return,)


@app.cell
def _(mo, overall, pl, risk_return):
    top3_summary = overall["company"].head(3).to_list()
    bottom3_summary = overall["company"].tail(3).to_list()
    best_risk_return = (
        risk_return
        .filter(pl.col("total_return") > 0)
        .sort(pl.col("total_return") / pl.col("annual_volatility"), descending=True)
        .head(1)["company"][0]
    )

    mo.md(
        f"""
        ## Summary

        This notebook was designed as a rapid-response tool for a 30-minute investment
        meeting, pulling five years of daily OHLCV data for all 11 tickers in a single
        `yf.Tickers().history()` call and converting immediately to Polars for all
        wrangling. The interactive ITables DataTable in Step 3 provides a fully
        searchable, sortable view of the raw data so any specific date or price can be
        checked on the fly during the meeting.

        The normalised performance chart (Step 5) rebases all tickers to $100 and uses
        the spaghetti-highlight technique — only the top 3 and bottom 3 performers are
        coloured, so the eye lands on the decisions that matter. The annual return
        heatmap (Step 6) is sorted by 5-year total return so consistent winners cluster
        at the top. The rolling 90-day volatility chart (Step 7) shows how risk evolves
        over time, with a cross-stock median reference line. The Plotly candlestick
        (Step 8) adds 20-day and 50-day SMAs and range selector buttons, turning a
        static chart into a real exploration tool. The risk-vs-return scatter (Step 10)
        is the single most useful decision chart: median lines carve the space into
        Ideal · Aggressive · Defensive · Avoid quadrants.

        Based on 5-year total return, the top three performers were
        **{", ".join(top3_summary)}**, while the weakest were **{", ".join(bottom3_summary)}**.
        When adjusting for risk (return per unit of volatility), **{best_risk_return}**
        offers the most efficient tradeoff and would be the strongest candidate for the
        $25,000 investment in a risk-conscious strategy.
        """
    )
    return


if __name__ == "__main__":
    app.run()
