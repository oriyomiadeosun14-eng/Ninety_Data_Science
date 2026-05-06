import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import polars as pl
    import numpy as np
    import lets_plot as lp

    lp.LetsPlot.setup_html()
    return lp, mo, pl


@app.cell(hide_code=True)
def _(pl):
    flights = pl.read_csv("../../data/raw/flights.csv", null_values=["NA", ""])
    flights.head()
    return (flights,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # NYC Flights Analysis (2013)

    This report explores flight delay patterns in NYC airports using the flights dataset.

    The goal is to understand:
    - which airlines perform best in the morning
    - which airports are best for Delta Airlines
    - which destinations have the worst delays

    The analysis uses grouping, percentiles, and averages to compare flight performance.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Question 1: Best airlines before noon
    """)
    return


@app.cell(hide_code=True)
def _(flights, pl):
    morning = flights.filter(pl.col("dep_time") < 1200)

    question1 = (
        morning
        .group_by(["origin", "carrier"])
        .agg(
            pl.col("arr_delay").quantile(0.75).alias("p75_delay")
        )
    )

    best_airlines = (
        question1.sort("p75_delay")
        .group_by("origin")
        .head(2)
    )

    best_airlines
    return (best_airlines,)


@app.cell(hide_code=True)
def _(best_airlines, lp):
    first_plot = (
        lp.ggplot(best_airlines,
                  lp.aes(x="carrier", y="p75_delay", fill="origin"))
        + lp.geom_bar()
        + lp.facet_wrap("origin", ncol=3)
        + lp.labs(
            title="Best airlines for morning flights",
            x="Airline",
            y="75th percentile delay"
        )
    )
    first_plot
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Question 2: Best airport for Delta Airlines
    """)
    return


@app.cell(hide_code=True)
def _(flights, pl):
    delta = flights.filter(pl.col("carrier") == "DL")

    question2 = (
        delta
        .group_by("origin")
        .agg(
            pl.mean("arr_delay").alias("avg_delay")
        )
        .sort("avg_delay")
    )

    question2
    return (question2,)


@app.cell(hide_code=True)
def _(lp, question2):
    second_plot = (
        lp.ggplot(
            question2,
            lp.aes(x="origin", y="avg_delay")
        )

        + lp.geom_bar(stat="identity")

        + lp.labs(
            title="Best airport for Delta Airlines", x="Airport", y="Average arrival delay"
        )
    )
    second_plot
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Question 3: Worst destination airports
    """)
    return


@app.cell(hide_code=True)
def _(flights, pl):
    worst_dest = (
        flights
        .group_by("dest")
        .agg(
            pl.mean("arr_delay").alias("avg_delay")
        )
        .sort("avg_delay", descending=True)
        .head(10)
    )

    worst_dest
    return (worst_dest,)


@app.cell(hide_code=True)
def _(lp, worst_dest):
    third_plot = (
        lp.ggplot(worst_dest,
                  lp.aes(x="dest", y="avg_delay"))
        + lp.geom_bar(stat="identity")
        + lp.labs(
            title="Worst destination airports", x="Destination", y="Average delay"
        )
    )

    third_plot
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    **Complexity Plot**

          The last plot
    """)
    return


@app.cell(hide_code=True)
def _(flights, lp):
    plot_complex = (
        lp.ggplot(flights,
                  lp.aes(x="distance", y="arr_delay", color="carrier"))
        + lp.geom_point(alpha=0.3)
        + lp.scale_x_log10()
        + lp.labs(
            title="Flight distance vs delay", x="Distance (log scale)", y="Arrival delay"
        )
    )

    plot_complex
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Conclusion

    Carrier Consistency: Early morning data suggests that an airline’s reliability is often tied to the specific airport from which it operates. For instance, Delta Airlines exhibits fluctuating performance levels based on the point of origin.

    Predictable Bottlenecks: Certain destination airports demonstrate a persistent trend of longer wait times and more frequent delays.

    Conclusion
    In summary, the duration of a flight delay is rarely a product of distance alone. Instead, it is a complex outcome driven by the strategic combination of the airline selected and the geographical locations involved in the route.
    """)
    return


if __name__ == "__main__":
    app.run()
