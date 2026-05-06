import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""
    # Exercise 3: Plotting Visualizations 📊

    **Week 7**

    **What you'll do:**

    - Create visualizations with gapminder dataset

    **Data Transformation**
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import lets_plot as lp
    life_expectancy = pl.read_csv("gapminder.csv")
    lp.LetsPlot.setup_html()
    life_expectancy.head()
    return life_expectancy, lp, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Creating a Facet Chart
    """)
    return


@app.cell
def _(life_expectancy, lp, pl):
    gapminder_scaled = life_expectancy.with_columns(pl.col("gdpPercap").sqrt().alias(
        "gdpPercap_scaled"), pl.col("year").cast(pl.Utf8).str.strptime(pl.Date, "%Y"))

    (
        lp.ggplot(gapminder_scaled, lp.aes(
            x="lifeExp", y="gdpPercap_scaled", color="continent", size="pop"))
        + lp.geom_point(alpha=0.7)
        + lp.facet_wrap(facets="year", ncol=12,)
        + lp.scale_x_continuous(
            limits=[40, 80],
            breaks=[40, 60, 80]
        )
        + lp.scale_size_area(
            max_size=30,
            breaks=[250000000, 500000000, 750000000, 1000000000, 1250000000],
            labels=["2500", "5000", "7500", "10000", "12000"],
            name="Population(100k)"
        )
        + lp.labs(
            x="Life Expectancy",
            y="GDP per capita",
            color="continent",
            size="pop"
        )
        + lp.theme_bw()
    )
    return (gapminder_scaled,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Second Plot, Scaled column Chart
    """)
    return


@app.cell
def _(gapminder_scaled, pl):

    continent_avg = (
        gapminder_scaled.group_by(["continent", "year"])
        .agg(
            weighted_gdp=(pl.col("gdpPercap_scaled") *
                          pl.col("pop")).sum() / pl.col("pop").sum()
        )
    )
    return (continent_avg,)


@app.cell
def _(continent_avg, gapminder_scaled, lp):
    final_plot = (
        lp.ggplot()

        # Layer 1: Raw Points
        + lp.geom_point(
            data=gapminder_scaled,
            mapping=lp.aes(x="year", y="gdpPercap_scaled",
                           color="continent", size="pop"),
            alpha=0.3
        )

        # Layer 2: Raw Lines
        + lp.geom_line(
            data=gapminder_scaled,
            mapping=lp.aes(x="year", y="gdpPercap_scaled",
                           color="continent", group="country"),
            size=0.5,
            alpha=0.2
        )

        # Layer 3: Average Points
        + lp.geom_point(
            data=continent_avg,
            mapping=lp.aes(x="year", y="weighted_gdp"),  # black
            size=4,
            shape="x"
        )

        # Layer 4: Average Lines
        + lp.geom_line(
            data=continent_avg,
            mapping=lp.aes(x="year", y="weighted_gdp"),  # black
            size=1.5
        )

        + lp.labs(
            x="Year",
            y="GDP per Capita (scaled)",
            color="Continent"
        )

        + lp.facet_wrap(facets="continent", ncol=6)

        + lp.theme_minimal()
    )
    final_plot
    # lp.ggsave(
    #     plot=final_plot,
    #     filename="final_life_expectancy_plot.svg",
    # )
    return


if __name__ == "__main__":
    app.run()
