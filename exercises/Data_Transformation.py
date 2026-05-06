import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


app._cell(
    """
    mo.md(r\"\"\"
    # Exercise 3: Plotting Visualizations 📊

    **Week 7**

    **What you'll do:**

    - Create visualizations

    **Data Transformation**
    \"\"\")
    return

    import polars as pl
    flight = pl.read_csv(\"../data/raw/flights.csv\", null_values=\"NA\")
    flight.head()
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Flight that has arrival delay of two or more hours
    """)
    return


@app.cell
def _(flight, pl):
    arrival_delay = flight.filter(
        pl.col("arr_delay") > 120
    )
    arrival_delay
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Flew to Houston (IAH or HOU)
    """)
    return


@app.cell
def _(flight, pl):
    Flew_to_Houston = flight.filter(
        (pl.col("dest") == "IAH") | (pl.col("dest") == "HOU")
    )
    Flew_to_Houston
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Were operated by United, American
    """)
    return


@app.cell
def _(flight, pl):
    United_American_or_Delta = flight.filter(
        (pl.col("carrier") == "UA") | (
            pl.col("carrier") == "AA") | (pl.col("carrier") == "DL")
    )
    United_American_or_Delta
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Departed in summer (July, August, and September)
    """)
    return


@app.cell
def _(flight, pl):
    Departed_In_Summer = flight.filter(
        (pl.col("month") == 7) | (pl.col("month") == 8) | (pl.col("month") == 9)
    )
    Departed_In_Summer
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


@app.cell
def _(flight, pl):
    late_Arrivals_early_Departure = flight.filter(
        (pl.col("arr_delay") > 120) & (pl.col("dep_delay") <= 0)
    )
    late_Arrivals_early_Departure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Were delayed by at least an hour, but made up over 30 minutes in flight
    """)
    return


@app.cell
def _(flight, pl):
    delayed_but_fast = flight.filter(
        (pl.col("dep_delay") >= 60) &
        ((pl.col("dep_delay") - pl.col("arr_delay")) > 30)
    )

    delayed_but_fast
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Departed between midnight and 6am (inclusive)
    """)
    return


@app.cell
def _(flight, pl):
    early_flights = flight.filter(
        (pl.col("dep_time") <= 600) | (pl.col("dep_time") == 2400)
    )
    early_flights
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    How many flights have a missing departure times
    """)
    return


@app.cell
def _(flight, pl):
    Missing_Departure_Times = flight.filter(
        pl.col("dep_time").is_null()
    )
    Missing_Departure_Times
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Other variables  missing
    """)
    return


@app.cell
def _(flight):
    # Shows a count of nulls for every column
    print(flight.null_count())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sort all missing values to the start
    """)
    return


@app.cell
def _(flight):
    print(flight.sort("", nulls_last=False))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Most Delayed Flight
    """)
    return


@app.cell
def _(flight):
    Most_delayed_flights = flight.sort("arr_delay", descending=True)
    return


if __name__ == "__main__":
    app.run()
