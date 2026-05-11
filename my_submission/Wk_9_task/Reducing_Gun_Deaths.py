import marimo

__generated_with = "0.23.3"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import polars.selectors as cs
    import lets_plot as lp
    lp.LetsPlot.setup_html()
    return lp, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The following analysis uses Polars for high-performance data manipulation and Lets-Plot for presentation-quality visualizations to fulfill the requirements for Case Study 4.

    1. **Summary of the FiveThirtyEight Articl**e
    The FiveThirtyEight article, "Gun Deaths in America," moves beyond the surface-level statistics of gun violence to reveal that the issue is composed of several distinct demographic trends. By analyzing approximately 33,000 annual deaths, they highlight that suicides are the leading cause of gun mortality, primarily affecting older white men, followed by homicides, which disproportionately impact young Black men. Their interactive visualization allows readers to see that while mass shootings often dominate public discourse, they represent a small fraction of the total lives lost.

    2. **Core Insight Visualization** (Polars & Lets-Plot)
    This plot mirrors the primary takeaway of the original article: the distribution of gun deaths by intent.
    """)
    return


@app.cell
def _(lp, pl):
    #Loading Data
    gun_death = pl.read_csv("../../data/raw/full_data.csv")
    intent_df = (
        gun_death
        .filter(pl.col("intent").is_not_null())
        .group_by("intent")
        .len()
    )

    fig = (
        lp.ggplot(intent_df, lp.aes(x="intent", y="len", fill="intent")) +
        lp.geom_bar(stat='identity', show_legend=False) +
        lp.scale_fill_brewer(type='qual', palette='Set1') +
        lp.labs(
            title="U.S. Gun Deaths by Intent (2012-2014)",
            x="Intent",
            y="Total Deaths"
        ) +
        lp.theme_minimal()
    )

    fig
    return (gun_death,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    3. **Analysis Summary**
    The FiveThirtyEight article is a landmark piece of data journalism because it reframes the national conversation on gun violence. It moves the focus away from rare, high-profile mass shootings toward the systemic issues of suicide and urban homicide. The authors use data to show that gun violence is a cluster of different problems: suicide is largely a crisis among older white men, while homicide is a crisis among young Black men. This distinction is vital for any organization looking to create effective reduction strategies.

    4. **Client Targeting Strategy** (Seasonal Trends)
    To effectively target commercials for reducing gun deaths, we analyzed seasonal fluctuations:

    The "Summer Surge": Total gun deaths peak in July. This is driven by both high suicide rates and a significant spike in homicides.

    The "Winter Homicide Spike": While totals are lower in winter, December shows a distinct rise in homicides compared to the months surrounding it.

    Consistent Suicide Risk: Suicides remain the dominant cause of death every month, but show slight increases during the spring and mid-summer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    5. **Potential Group Targetings** (Seasonal Visualizations)
    Plot 1: Total Seasonal Deaths by Month
    This plot identifies the months where the client should spend the most on commercial airtime.
    """)
    return


@app.cell
def _(gun_death, lp):
    monthly_total = (
        gun_death
        .group_by("month")
        .len()
        .sort("month")
    )

    fig1 = (
        lp.ggplot(monthly_total, lp.aes(x="month", y="len")) +
        lp.geom_line(size=1.5, color="black") +
        lp.geom_point(size=3) +
        lp.scale_x_continuous(breaks=list(range(1, 13))) +
        lp.labs(
            title="Seasonal Trend: Total Gun Deaths per Month",
            x="Month",
            y="Number of Deaths"
        ) +
        lp.theme_minimal()
    )

    fig1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Description**: The above visualization shows that gun deaths steadily rise through the spring and peak in July. For the client, this suggests a "Summer Safety" campaign should launch in June and run through August to address the period of highest risk.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Plot 2: Intent Shifts by Season**
    This allows the client to change the message of the commercial depending on the month.
    """)
    return


@app.cell
def _(gun_death, lp):
    intent_seasonal = gun_death.group_by(["month", "intent"]).len().sort("month")

    fig2 = (
        lp.ggplot(intent_seasonal, lp.aes(x="month", y="len", color="intent")) +
        lp.geom_line(size=1.2) +
        lp.scale_x_continuous(breaks=list(range(1, 13))) +
        lp.labs(title="Targeted Messaging: Intent Trends by Month",
             x="Month", y="Number of Deaths", color="Intent") +
        lp.theme_minimal()
    )
    fig2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Description**: The plot above highlights that Suicide remains high year-round but peaks in July, while Homicide sees a major spike in both July and December. The client should pivot from suicide prevention in the spring to homicide/community-violence messages in the summer and winter holidays.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Plot 3: Summer Homicide Demographics**
    This plot identifies which demographic groups are most impacted during the high-risk summer months.
    """)
    return


@app.cell
def _(gun_death, lp, pl):
    homicide_race = (
        gun_death
        .filter(pl.col("intent") == "Homicide")
        .group_by(["month", "race"])
        .len()
        .sort("month")
    )

    fig3 = (
        lp.ggplot(
            homicide_race,
            lp.aes(x="month", y="len", color="race")
        ) +
        lp.geom_line(size=1) +
        lp.geom_point(size=3) +
        lp.scale_x_continuous(breaks=list(range(1, 13))) +
        lp.labs(
            title="Demographic Focus: Homicides by Race and Month",
            x="Month",
            y="Total Homicides",
            color="Race"
        ) +
        lp.theme_minimal()
    )

    fig3
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Description**: The data shows that the summer homicide surge disproportionately affects Black Americans. To have the most impact, the client should place targeted commercials in urban markets and media outlets catering to these communities specifically during the months of June, July, and August.
    """)
    return


if __name__ == "__main__":
    app.run()
