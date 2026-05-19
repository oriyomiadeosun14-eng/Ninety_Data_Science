import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Here I am combining the other data's together into a single Dataframe**

    The data's here includes:


          1: germanprison.dta

         2: germanconscr.dta

         3: heights.csv

         4: cleaned_heights.csv

         5: B6090.DBF
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
    from dbfread import DBF


    return DBF, lp, mo, pd, pl


@app.cell
def _(DBF, pd, pl):
    # ----------------------------------------------------
    # 1. BAVARIAN SOLDIERS (b6090)
    # ----------------------------------------------------
    dbf_records = DBF(
        "../../data/raw/B6090.DBF", 
        ignore_missing_memofile=True, 
        encoding="latin1", 
        char_decode_errors="replace"
    )
    df_b6090_raw = pl.DataFrame(list(dbf_records))

    b6090_tidy = (
        df_b6090_raw
        .select([
            pl.col("GEBJ").alias("birth_year"),
            pl.col("CMETER").alias("height.cm")
        ])
        .with_columns([
            pl.col("birth_year").cast(pl.Int32),
            pl.col("height.cm").cast(pl.Float64)
        ])
        .filter((pl.col("birth_year") > 0) & (pl.col("height.cm") > 0))
        .with_columns([
            (pl.col("height.cm") / 2.54).round(4).alias("height.in"),
            pl.lit("b6090").alias("study_id")
        ])
        .select(["study_id", "birth_year", "height.cm", "height.in"])
    )

    # ----------------------------------------------------
    # 2. BLS WAGE DATA (bls_wage)
    # ----------------------------------------------------
    bls_tidy = (
        pl.read_csv("../../data/raw/heights.csv", schema_overrides={"earn": pl.Float64})
        .select([
            pl.lit("bls_wage").alias("study_id"),
            pl.lit(1950).cast(pl.Int32).alias("birth_year"),
            (pl.col("height") * 2.54).round(4).alias("height.cm"),
            pl.col("height").cast(pl.Float64).round(4).alias("height.in")
        ])
    )

    # ----------------------------------------------------
    # 3. GERMAN CONSCRIPTS (german_conscripts)
    # ----------------------------------------------------
    # Read Stata file using pandas bridge
    df_conscr_pd = pd.read_stata("../../data/raw/germanconscr.dta")
    df_conscr_raw = pl.from_pandas(df_conscr_pd)

    conscr_tidy = (
        df_conscr_raw
        .select([
            pl.col("bdec").cast(pl.Int32).alias("birth_year"), 
            pl.col("height").cast(pl.Float64).alias("height.cm")
        ])
        .filter((pl.col("birth_year") > 0) & (pl.col("height.cm") > 0))
        .with_columns([
            (pl.col("height.cm") / 2.54).round(4).alias("height.in"),
            pl.lit("german_conscripts").alias("study_id")
        ])
        .select(["study_id", "birth_year", "height.cm", "height.in"])
    )

    # ----------------------------------------------------
    # 4. GERMAN PRISONERS (german_prisoners)
    # ----------------------------------------------------
    df_prison_pd = pd.read_stata("../../data/raw/germanprison.dta")
    df_prison_raw = pl.from_pandas(df_prison_pd)

    prison_tidy = (
        df_prison_raw
        .select([
            pl.col("bdec").cast(pl.Int32).alias("birth_year"),
            pl.col("height").cast(pl.Float64).alias("height.cm")
        ])
        .filter((pl.col("birth_year") > 0) & (pl.col("height.cm") > 0))
        .with_columns([
            (pl.col("height.cm") / 2.54).round(4).alias("height.in"),
            pl.lit("german_prisoners").alias("study_id")
        ])
        .select(["study_id", "birth_year", "height.cm", "height.in"])
    )

    # ----------------------------------------------------
    # 5. COMBINE ALL INDIVIDUAL MEASUREMENTS
    # ----------------------------------------------------
    # Stack them row-by-row
    individual_combined = pl.concat([b6090_tidy, bls_tidy, conscr_tidy, prison_tidy])

    # Preview the master sheet
    individual_combined
    return (individual_combined,)


@app.cell
def _(individual_combined):
    individual_combined.write_csv("../../data/raw/combined_data.csv")
    return


@app.cell
def _(pl):
    # Load the aggregate world dataset
    world_estimates = pl.read_csv("../../data/raw/Cleaned_Height.csv")

    # Load your stacked master individual dataset
    combined_data = pl.read_csv("../../data/raw/combined_data.csv")
    return combined_data, world_estimates


@app.cell
def _(lp, pl, world_estimates):
    # 1. Separate Germany from the rest of the world data
    df_background = world_estimates.filter(~pl.col("country").is_in(["Germany", "Federal Republic of Germany (until 1990)"]))
    df_germany = world_estimates.filter(pl.col("country").is_in(["Germany", "Federal Republic of Germany (until 1990)"]))

    # 2. Build the highlight visualization layer by layer
    germany_plot = (
        lp.ggplot()
        # Layer 1: Global background lines (thin and grey)
        + lp.geom_line(
            data=df_background.to_pandas(), 
            mapping=lp.aes(x="decade", y="height_in", group="country"), 
            color="lightgrey", 
            size=0.5
        )
        # Layer 2: Highlight Germany line (thick and dark red)
        + lp.geom_line(
            data=df_germany.to_pandas(), 
            mapping=lp.aes(x="decade", y="height_in", group="country"), 
            color="#c0392b", 
            size=1.5
        )
        + lp.geom_point(
            data=df_germany.to_pandas(), 
            mapping=lp.aes(x="decade", y="height_in"), 
            color="#c0392b", 
            size=3
        )
        # FIX: Explicitly format axis numbers to integers without commas
        + lp.scale_x_continuous(format="d")
    
        # Labels and thematic styling
        + lp.ggtitle("Global Height Trends: Germany Highlighted")
        + lp.labs(x="Decade", y="Height (Inches)")
        + lp.theme_minimal()
    )

    # Render the graph
    germany_plot
    return


@app.cell
def _(combined_data, lp, pl):
    # 1. Group records by century categories dynamically
    df_distribution = (
        combined_data
        .with_columns([
            ((pl.col("birth_year") // 100) * 100).cast(pl.Int32).alias("century")
        ])
        .filter(pl.col("century").is_in([1700, 1800, 1900])) # focus on relevant data centuries
        .with_columns([
            pl.col("century").map_elements(lambda c: f"{c}s", return_dtype=pl.String).alias("century_label")
        ])
    ).to_pandas()

    # 2. Build a column-faceted plot array
    distribution_plot = (
        lp.ggplot(df_distribution, lp.aes(x="height.in", fill="century_label"))
        # Generate density curves to look at height shapes smoothly
        + lp.geom_density(alpha=0.5, color="white")
        # Facet purely into columns side-by-side by study_id
        + lp.facet_wrap(facets="study_id", ncol=5)
        # Color schemes and presentation updates
        + lp.scale_fill_brewer(type="qual", palette="Set2")
        + lp.ggtitle("Height Distribution Variations Across Centuries")
        + lp.labs(x="Height (Inches)", y="Density", fill="Century Group")
        + lp.theme_minimal()
        + lp.theme(legend_position="bottom")
    )

    # Render the graph
    distribution_plot
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Summary Sheet:
    The Peak: Where the average/most common height sits.

    The Width: How much height inequality there was in that group.

    Moving Right: Society is getting healthier/better fed.

    A Sharp Drop on the Left: A minimum height rule was active.
    """)
    return


if __name__ == "__main__":
    app.run()
