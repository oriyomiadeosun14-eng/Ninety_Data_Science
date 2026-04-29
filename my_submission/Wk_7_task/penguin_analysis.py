import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    from lets_plot import ggplot, aes, geom_point,geom_smooth,labs,LetsPlot
    from palmerpenguins import load_penguins

    LetsPlot.setup_html()
    return aes, geom_point, geom_smooth, ggplot, labs, load_penguins, pl


@app.cell
def _(load_penguins, pl):
    penguins = pl.from_pandas(load_penguins())
    penguins
    return (penguins,)


@app.cell
def _(aes, geom_point, geom_smooth, ggplot, labs, penguins):
    (
        ggplot(penguins, aes(x="flipper_length_mm", y="body_mass_g",))
        + geom_point(aes(color="species", shape="species"))
        + geom_smooth(method="lm")
        + labs(
            title="Body mass and flipper length",
            subtitle="Dimensions for Adelie, Chinstrap, and Gentoo Penguins",
            x="Flipper length (mm)",
            y="Body mass (g)",
            color="Species",
            shape="Species",
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    How many rows are in penguins? How many columns?
    """)
    return


@app.cell
def _(penguins):

    penguins
    #344 rows, 8 column
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    What does the bill_depth_mm variable in the penguins data frame describe?
    This describes how long each Penguins are
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Make a scatterplot of bill_depth_mm vs. bill_length_mm. That is, make a scatterplot with bill_depth_mm on the y-axis and bill_length_mm on the x-axis. Describe the relationship between these two variables.
    """)
    return


@app.cell
def _(aes, geom_point, geom_smooth, ggplot, penguins):
    ggplot(penguins,aes(x = "bill_length_mm", y = "bill_depth_mm") )
    + geom_point(aes(color="species", shape="species"))
    + geom_smooth()
    return


if __name__ == "__main__":
    app.run()
