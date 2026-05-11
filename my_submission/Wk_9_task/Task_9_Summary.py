import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    # Task 07: Polars Data Structures & Types
    Notes based on [Polars Official Documentation](https://docs.pola.rs/user-guide/concepts/data-types-and-structures/)
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. Core Structures
    * **Series**: 1D homogeneous array. The building block of columns.
    * **DataFrame**: 2D table composed of Series. Uses the **Apache Arrow** memory format for extreme speed.

    ## 2. Schema Management
    Polars uses **Schema Inference** to guess types. We can override this using a dictionary.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Handling Floating Points (IEEE 754)
    Polars tweaks standard math for speed:
    * `NaN == NaN` evaluates to **True**.
    * `NaN` is treated as the **largest** value during sorting.
    * These choices make grouping and sorting much faster.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Lists vs. Arrays
    * **List**: For "ragged" data (different lengths in each row).
    * **Array**: For fixed-length data (every row has the same count).
    * **Requirement**: Both must be **homogeneous** (no mixing strings and numbers).
    """)
    return


if __name__ == "__main__":
    app.run()
