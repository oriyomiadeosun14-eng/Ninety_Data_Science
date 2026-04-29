import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Flight Data
    """)
    return


@app.cell
def _():
    from narwhals.testing.asserts.series import _check_null_values
    import polars as pl
    flights = pl.read_csv("../data/raw/flights.csv", null_values = "NA")

    flights.head()
    return flights, pl


@app.cell
def _(flights):
    flights.glimpse(max_items_per_column=5)
    return


@app.cell
def _(flights, pl):
    flights.get_column("time_hour")
    flights.with_columns(pl.col("time_hour").str.to_datetime(format = "%Y-%m-%d T%H:%M:%SZ"))
    return


@app.cell
def _(pl):
    df = pl.DataFrame(
        data={
            "col0": [0, 0, 0, 0],
            "col1": [0, 0, 0, 0],
            "col2": [0, 0, 0, 0],
            "col3": ["a", "b", "b", "a"],
            "col4": ["alpha", "gamma", "gamma", "gamma"],
        },
    )
    df.head()
    return


@app.cell
def _(flights, pl):
    flights.filter(pl.col("dest") == "IAH").group_by(["year", "month", "day"]).agg(
        pl.col("arr_delay").mean()
    )

    return


@app.cell
def _(flights, pl):
    flights.sort("dep_time")

    (
        flights.filter((pl.col("dep_delay") <= 10) & (pl.col("dep_delay") >= -10))
        .sort("arr_delay", descending=True)
        .head(3)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Exercise
    """)
    return


@app.cell
def _(flights, pl):
    delay_arrival = flights.filter(pl.col("arr_delay") > 120).sort("arr_delay", descending=True)

    delay_arrival.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Flew to Houston ("IAH" or "HOU")
    """)
    return


@app.cell
def _(flights, pl):
    Des = flights.filter((pl.col("dest") == "IAH") | (pl.col("dest") == "HOU"))
    Des.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Were operated by United, American, or Delta
    """)
    return


@app.cell
def _(flights, pl):
    operated_by = flights.filter(pl.col("carrier").is_in(["AA", "DL", "UA"]))
    operated_by.head(20)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Departed in summer (July, August, and September)
    """)
    return


@app.cell
def _(flights, pl):
    summer_flights = flights.filter(pl.col("month").is_in([7, 8, 9]))
    summer_flights.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Arrived more than two hours late, but didn’t leave late
    """)
    return


@app.cell
def _(flights, pl):
    late_arrival_Early_departure = flights.filter(
        (pl.col("arr_delay") > 120) & (pl.col("dep_delay") <= 0)
    )
    late_arrival_Early_departure.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Were delayed by at least an hour, but made up over 30 minutes in flight
    """)
    return


@app.cell
def _(flights, pl):
    dep_delay_early_arrival = flights.filter(
        (pl.col("dep_delay") >= 60) & 
        (pl.col("dep_delay") - pl.col("arr_delay") > 30)
    )
    dep_delay_early_arrival.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sort flights to find the flights with longest departure delays.
    """)
    return


app._unparsable_cell(
    r"""
    long_dep_delay = flights.sort("dep_delay", descending=True, nulls_last=True)s
    long_dep_delay.head()
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sort flights to find the fastest flights
    """)
    return


@app.cell
def _(flights, pl):
    fastest_flight = flights.with_columns(
        (pl.col("distance") / pl.col("air_time") * 60).alias("speed")
    ).sort("speed", descending=True, nulls_last=True)
    fastest_flight.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Which flights traveled the farthest?
    """)
    return


@app.cell
def _(flights):
    long_flights = flights.sort("distance", descending=True, nulls_last=True)
    long_flights.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Testing
    """)
    return


@app.cell
def _(flights, pl):
    tst = flights.with_columns(new_column0=pl.Series(range(0, 336776)))
    tst
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Compare air_time with arr_time - dep_time. What do you expect to see? What do you see? What do you need to do to fix it?
    """)
    return


@app.cell
def _(flights, pl):
    New_Column = flights.with_columns(air_time_Comp =pl.Series(range(0, 336776)))
    New_Column.head()

    return


@app.cell
def _(flights, pl):
    # The corrected version of your snippet
    result = flights.group_by("month").agg(
        mean_delay=pl.mean("dep_delay"),
        count_flights=pl.count("dep_delay"),
    ).sort("month")

    result
    return


@app.cell
def _(flights, pl):
    month_year_delay = flights.group_by("month", "year").agg(
        mean_delay=pl.mean("dep_delay"),
        count_flights=pl.count("dep_delay"),
    )
    month_year_delay
    return


@app.cell
def _(flights, pl):
    # Finding the average arrival delay per carrier
    worst_carriers = (
        flights.group_by("carrier")
        .agg(avg_arr_delay = pl.mean("arr_delay"))
        .sort("avg_arr_delay", descending=True)
    )
    worst_carriers
    return


@app.cell
def _(flights, pl):
    # Grouping by both carrier AND destination
    carrier_airport_analysis = (
        flights.group_by(["carrier", "dest"])
        .agg(avg_delay = pl.mean("arr_delay"))
        .sort(["dest", "avg_delay"], descending=[False, True])
    )
    carrier_airport_analysis
    return


@app.cell
def _(flights, pl):
    flights.group_by("carrier_airport_analysis").agg(
        pl.col(["avg_delay", "dest", "carrier"])
    )
    return


if __name__ == "__main__":
    app.run()
