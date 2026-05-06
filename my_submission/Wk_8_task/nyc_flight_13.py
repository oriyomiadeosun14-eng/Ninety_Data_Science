import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import lets_plot as lp
    lp.LetsPlot.setup_html()
    return lp, mo, pl


@app.cell
def _(lp, pl):


    # 1. Load the data using Polars
    nyc3 = pl.read_csv("../../data/raw/flights.csv", null_values=["NA"])

    # --- GRAPHIC 1: Distribution of Departure Delays ---
    # Wrangle data to filter for a specific range for clarity
    dist_data = (
        nyc3.select("dep_delay")
        .drop_nulls()
        .filter((pl.col("dep_delay") >= -20) & (pl.col("dep_delay") <= 150))
    )

    # Using parentheses to allow the '+' to start each line
    Dep_delay = (
        lp.ggplot(dist_data, lp.aes(x="dep_delay"))
        + lp.geom_histogram(binwidth=5, fill="#5e81ac", color="white")
        + lp.labs(
            title="Distribution of Departure Delays",
            subtitle="Visualizing the frequency of delays between -20 and 150 minutes",
            x="Departure Delay (minutes)",
            y="Count"
        )
        + lp.theme_minimal2()
    )
    Dep_delay
    return (nyc3,)


@app.cell
def _(lp, nyc3, pl):

    # --- GRAPHIC 2: Bivariate Analysis (Hour vs. Delay) ---
    # Aggregate average delay by hour
    bivariate_data = (
        nyc3.group_by("hour")
        .agg(pl.col("dep_delay").mean().alias("avg_dep_delay"))
        .drop_nulls()
        .sort("hour")
    )

    bivariate = (
        lp.ggplot(bivariate_data, lp.aes(x="hour", y="avg_dep_delay"))
        + lp.geom_line(color="#bf616a", size=1)
        + lp.geom_point(color="#bf616a", size=3, fill="white", shape=21)
        + lp.scale_x_continuous(breaks=list(range(0, 25, 2)))
        + lp.labs(
            title="Average Departure Delay by Hour of Day",
            subtitle="Performance trend showing delay accumulation throughout the day",
            x="Hour of Departure (24h format)",
            y="Average Delay (minutes)"
        )
        + lp.theme_minimal2()
    )
    bivariate

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Data Visualization Insights**

    The first visualization explores the distribution of departure delays within the nycflights13 dataset. By focusing on flights within a -20 to 150-minute window, we observe that while the median flight departs slightly ahead of schedule, the distribution is heavily right-skewed. I chose a histogram with 5-minute bins to highlight the high frequency of "on-time" departures while still capturing the gradual decay of frequency as delays increase.

    The second visualization examines the bivariate relationship between the hour of departure and the average delay. The line graph reveals a clear, ascending trend: early morning flights (5:00 AM) are highly reliable, often departing early, whereas average delays peak in the late evening. This suggests a "cascading effect" where delays early in the day compound as aircraft and crews move through the system. I utilized a line plot with distinct point markers to emphasize the sequential nature of time and the specific hours where delay growth accelerates most sharply.
    """)
    return


if __name__ == "__main__":
    app.run()
