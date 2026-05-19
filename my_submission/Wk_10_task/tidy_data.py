import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import polars.selectors as cs
    import lets_plot as lp
    lp.LetsPlot.setup_html()
    return lp, mo, pl


@app.cell
def _(pl):
    # 1. Load data
    df = pl.read_csv("../../data/raw/Dart_Expert_Dow_6month_anova.csv")

    # 2. Start the cleaning pipeline
    df_tidy = (
        df
        # A. Split the period to get the 'end' part (e.g., "June1990")
        .with_columns([
            pl.col("contest_period").str.split("-").list.last().alias("temp_end")
        ])
        # B. Extract Month and Year strings
        .with_columns([
            pl.col("temp_end").str.replace_all(r"\d+", "").alias("month"),
            pl.col("temp_end").str.extract(r"(\d{4})", 1).alias("year_end")
        ])
        # C. Fix typos and Rename Groups (CRITICAL: Fix typos before Step D)
        .with_columns([
            pl.col("month").replace({"Febuary": "February", "Dec.": "December"}),
            pl.col("variable").replace({
                "PROS": "Pro Selection",
                "DARTS": "Dartboard",
                "DJIA": "Dow Jones"
            })
        ])
       # --- >>> STEP D GOES HERE <<< ---
        .with_columns([
            pl.format("{}-{}", pl.col("month"), pl.col("year_end"))
            .str.to_date(format="%B-%Y")
            .alias("date")
        ])
        .with_columns([
            pl.col("date").dt.month().alias("month_number")
        ])
        # --------------------------------
        # Step E: Final cleanup
        .rename({"variable": "group", "value": "return_value"})
        .drop("temp_end")
    )
    return (df_tidy,)


@app.cell
def _(df_tidy, lp):
    time_series_plot = (
        lp.ggplot(df_tidy.to_pandas(), lp.aes(x='date', y='return_value', color='group')) +
        lp.geom_line(size=1.2) +
        lp.geom_point(size=2) +
        lp.scale_x_datetime(format='%Y') + 
        lp.theme_minimal() +
        lp.labs(
            title="Six-Month Stock Returns by Year of Collection",
            subtitle="Comparing Professional Picks, Random Darts, and the DJIA",
            x="Year Collected",
            y="Return (%)",
            color="Strategy"
        )
    )
    time_series_plot
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **1. The Goal**
    The primary objective of this project was to take a raw dataset of stock market contest returns and transform it into a clear, actionable comparison of three investment strategies: Professional Picks, Random Selection (Dartboard), and the Market Index (Dow Jones).

    **2. The Analysis (The Plot)**
    The resulting Time Series Plot illustrates the "Six-Month Returns" for each group. Unlike a static table, this visualization reveals the momentum and risk profiles of the strategies:

    Volatility: You will notice the Pro Selection line shows the most aggressive movement. While it offers high peaks, it also carries deeper valleys, highlighting the risk of active management.

    Market Synchronization: The plot clearly shows how all three strategies—even the random ones—are heavily influenced by the overall movement of the Dow Jones, suggesting that market-wide trends are often stronger than individual stock-picking expertise.

    **3. The "Spread" Summary**
    Following the visual analysis, I have provided a Pivoted Summary Table. This table "spreads" the Dow Jones returns across a grid of months and years, allowing for a quick, precise audit of performance at any specific point in the six-year timeline.
    """)
    return


@app.cell
def _(df_tidy, pl):
    # 3. Create the DJIA Spread Table
    # We use month_number to make sure the table is sorted chronologically (Jan, Feb, March...)
    # instead of alphabetically (April, August, December...)
    djia_table = (
        df_tidy
        .filter(pl.col("group") == "Dow Jones")
        .sort("month_number") # Sorts by 1, 2, 3...
        .pivot(
            index="month",
            on="year_end",
            values="return_value"
        )
        # The pivot will now maintain the month_number order in the rows
    )
    # FINAL STEP: Reorder columns so 1990 comes before 1991
    # We keep "month" first, then sort all other column names (the years)
    djia_table = djia_table.select([
        "month", 
        *sorted(djia_table.columns[1:]) 
    ])

    djia_table
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
