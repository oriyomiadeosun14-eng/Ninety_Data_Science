import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import lets_plot as lp
    lp.LetsPlot.setup_html()

    battery = pl.read_csv(
        "../../data/raw/price-of-lithium-ion-battery-cells.csv")
    battery.head()
    return battery, lp, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Graphics for communication**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I was able to understand the basic concept of changing default setting to control the non-data parts of my plot, such as fonts, backgrounds, and colors.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Themes**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Themes allow me to change the look of a plot, Without changing data or the logic of a chart. I am also able to learn diffrent functions and the argument that goes into each of those funtions to ne able to control the non data parts of my plots
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Writing Code**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This material makes it clear when to use a script versus a notebook. I also learned what an IDE is and why VS Code is such a smart choice for coding.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Data Import**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    From this material, I get to understand how to read data from mutiple files, and also writing to a file. Writing to a file is basically taking information that is currently on my computer's temporary memory (RAM) and saving it onto a permanent storage device, like a hard drive or an SSD.
    """)
    return


@app.cell
def _(battery, lp):
    (
        lp.ggplot(battery, lp.aes(x="year", y="price"))
        + lp.geom_line(color="#923d8d", )
        + lp.geom_point(color="#923d8d")
        + lp.scale_x_continuous(format="d")
        + lp.scale_y_log10(
            breaks=[100, 200, 500, 1000, 2000, 5000, 10000],
            labels=["$100", "$200", "$500", "$1,000",
                    "$2,000", "$5,000", "$10,000"],
            limits=[70, 11000]
        )
        + lp.theme_minimal()
    )
    return


if __name__ == "__main__":
    app.run()
