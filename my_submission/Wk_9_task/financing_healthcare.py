import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import polars.selectors as cs
    import lets_plot as lp
    lp.LetsPlot.setup_html()
    return cs, lp, mo, pl


@app.cell
def _(mo):
    mo.md(r"""
    Checked Data for any inconsistency.
    Data Insights (EDA Results)
    Before jumping into the visualization, here is what the initial EDA reveals about the dataset:

    Completeness: The dataset is exceptionally clean with 0 missing values across all 2,332 records.

    Time Span: The data covers a massive range from 1880 to 2024, allowing us to see long-term shifts from early industrial spending to modern healthcare systems.

    Spending Intensity: On average, countries spend about 4.65% of their GDP on public health, with some nations peaking at over 15%.
    """)
    return


@app.cell
def _(cs, lp, pl):

    # 1. LOAD DATA
    # Renaming the dataframe variable to financing_healthcare as requested
    financing_healthcare = pl.read_csv("../../data/raw/public-health-expenditure-share-gdp.csv")

    # 2. EXPLORATORY DATA ANALYSIS (EDA)
    print("--- DATASET SUMMARY ---")
    # Using selectors to round only numeric columns for cleaner output
    eda_summary = (
        financing_healthcare.describe()
        .with_columns(cs.numeric().round(2))
    )
    print(eda_summary)

    # Check for null values
    print("\n--- NULL COUNTS ---")
    print(financing_healthcare.null_count())

    # 3. DATA WRANGLING
    # Rename the target column for easier referencing in the plot
    target_col = "Public health expenditure as a share of GDP"
    financing_healthcare = financing_healthcare.rename({target_col: "health_exp"})

    # Filter for a representative set of countries
    target_countries = ["United Kingdom", "United States", "Nigeria", "Japan", "Germany", "Brazil"]
    plot_data = financing_healthcare.filter(pl.col("Entity").is_in(target_countries))


    # Creating the "Humanist" style chart
    plot = (
        lp.ggplot(plot_data, lp.aes(x="Year", y="health_exp", color="Entity")) +
        lp.geom_line(size=1.1, alpha=0.8) +
        lp.geom_point(size=2, stroke=1.5, fill="white", shape=21) + 
        lp.scale_color_brewer(type="qual", palette="Set1") +
        lp.scale_x_continuous(format="d") +
        lp.labs(
            title="Public Health Expenditure as a Share of GDP",
            subtitle="Analyzing trends from 1880 to 2024 across selected nations",
            x="Year",
            y="Spending (% of GDP)",
            color="Country"
        ) +
        lp.theme_minimal() +
        lp.theme(
            plot_title=lp.element_text(size=20, face="bold"),
            legend_position="bottom",
            panel_grid_minor=lp.element_blank()
        )
    )
    plot
    return


if __name__ == "__main__":
    app.run()
