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
    import polars as pl 
    import lets_plot as lp
    life_expectancy = pl.read_csv("gapminder.csv")
    lp.LetsPlot.setup_html()
    return life_expectancy, lp, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Creating a Facet Chart
    """)
    return


@app.cell
def _(life_expectancy, lp):
    this_plot =(
        lp.ggplot(life_expectancy, lp.aes(x="lifeExp", y="gdpPercap", color="continent", size="pop"))
        + lp.geom_point(alpha=0.7)
        + lp.facet_wrap(facets="year", nrow=3, format = ".0f")
        + lp.scale_x_continuous(
            limits=[40, 80],
            breaks=[40, 60, 80]
        )
        + lp.scale_y_log10(
            # These are the labels seen in your image
            breaks=[1000, 10000, 20000, 30000, 40000, 50000, 60000],
            labels=["1000", "10000", "20000", "30000", "40000", "50000", "60000"]
        )
        + lp.labs(
            x="Life Expectancy",
            y="GDP per capita",
            color="continent",
            size="pop"
        )
        + lp.theme_bw()

    )
    lp.ggsave(
        plot=this_plot,
        filename="life_expectancy_plot.svg",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Second Plot, Scaled column Chart
    """)
    return


@app.cell
def _(life_expectancy, pl):
    y_axis = life_expectancy.with_columns(pl.col("gdpPercap").sqrt().alias("gdpPercap_scaled"))

    continent_avg = (
        y_axis.group_by(["continent", "year"])
        .agg(
            weighted_gdp = (pl.col("gdpPercap") * pl.col("pop")).sum() / pl.col("pop").sum()
        )
    )
    continent_avg
    return continent_avg, y_axis


@app.cell
def _(continent_avg, lp, y_axis):
    final_plot = (
        lp.ggplot()

        # Layer 1: Raw Points
        + lp.geom_point(
            data=y_axis,
            mapping=lp.aes(x="year", y="gdpPercap_scaled", color="continent", size="pop"),
            alpha=0.3
        )

        # Layer 2: Raw Lines
        + lp.geom_line(
            data=y_axis,
            mapping=lp.aes(x="year", y="gdpPercap_scaled", color="continent", group="country"),
            size=0.5,
            alpha=0.2
        )

        # Layer 3: Average Points
        + lp.geom_point(
            data=continent_avg,
            mapping=lp.aes(x="year", y="weighted_gdp", color="continent"),  
            size=4,
            shape="x"
        )

        # Layer 4: Average Lines
        + lp.geom_line(
            data=continent_avg,
            mapping=lp.aes(x="year", y="weighted_gdp", color="continent"),  # ✅ FIXED
            size=1.5
        )

        + lp.labs(
            x="Year",
            y="GDP per Capita (scaled)",
            color="Continent"
        )

        + lp.facet_wrap("continent", nrow = 1)  # ✅ better syntax

        + lp.theme_minimal()
    )
    lp.ggsave(
        plot=final_plot,
        filename="final_life_expectancy_plot.svg",
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
