import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Data Cleaning for Height Spreadsheet**

    *Presented by Oriyomi King Adeosun*
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import pandas as pd
    import polars.selectors as cs
    import lets_plot as lp
    lp.LetsPlot.setup_html()
    return mo, pd, pl


@app.cell
def _(pd, pl):
    # 1. Read data with pandas, explicitly telling it to skip the 2 empty rows at the top
    # This allows it to see the numbers immediately and infer the correct float/int types
    pandas_df = pd.read_excel("../../data/raw/Height.xlsx", skiprows=2)

    # 2. Converting it instantly to a Polars DataFrame
    height = pl.from_pandas(pandas_df)

    # Now 'height' is perfectly typed and ready for  cleaning!
    height
    return (height,)


@app.cell
def _(height, pl):
    # 2. Cleaning pipeline
    height_cleaned = (
        height
        # A. Reshapeing from a Wide format to Long a format
        .unpivot(
            index=["Code", "Continent, Region, Country"],
            variable_name="year",
            value_name="height_cm"
        )
        # B. Filter out rows where height data is missing (null)
        .filter(pl.col("height_cm").is_not_null())

        # C. Converting columns to correct numerical types so we can do math
        .with_columns([
            pl.col("year").cast(pl.Int32),
            # CRITICAL: Converts text heights to numbers
            pl.col("height_cm").cast(pl.Float64)
        ])

        # D. Create  temporal and measurement columns
        .with_columns([
            ((pl.col("year") // 10) * 10).alias("decade"),     # e.g., 1854 -> 1850
            # e.g., 1854 -> 18 (First two numbers)
            (pl.col("year") // 100).alias("century"),
            # Converts cm to inches
            (pl.col("height_cm") / 2.54).round(4).alias("height_in")
        ])

        # E. Clean up column names for readability
        .rename({"Continent, Region, Country": "country"})
    )

    # 3. Preview your final tidy dataset
    height_cleaned
    return (height_cleaned,)


@app.cell
def _(height_cleaned):
    # Save the cleaned data to my data directory
    height_cleaned.write_csv("../../data/raw/height.csv")
    return


if __name__ == "__main__":
    app.run()
