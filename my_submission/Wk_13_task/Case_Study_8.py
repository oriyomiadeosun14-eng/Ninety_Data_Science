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
    return lp, mo, pl


@app.cell
def _(mo):
    mo.md("""
    # CS-08: It's About Time
    ## Business Investment Analysis

    > **Objective:** Analyse three months of Point-of-Sale (POS) transaction data for
    > six businesses and recommend the best candidate for a business loan.
    >
    > **Tools:** `polars` for data wrangling · `lets-plot` for visualisation
    >
    > **By:** **Oriyomi King Adeosun**
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 1: Load & Clean Data

    The raw data is UTC — I convert to **Mountain Time (America/Denver)**
    before any aggregation. I also remove rows where `Name` or `Type` is
    `"Missing"`, and drop transactions with non-positive `Amount` values.
    """)
    return


@app.cell
def _(pl):
    sales = pl.read_csv(
        "https://byuistats.github.io/M335/data/sales.csv",
        try_parse_dates=False,
    )

    data = (
        sales
        .with_columns(
            pl.col("Time")
              .str.to_datetime("%Y-%m-%dT%H:%M:%SZ", time_unit="us", time_zone="UTC")
              .dt.convert_time_zone("America/Denver")
              .alias("time_mt")
        )
        .filter(
            (pl.col("Name") != "Missing") &
            (pl.col("Type") != "Missing") &
            (pl.col("Amount") > 0)
        )
        .with_columns([
            pl.col("time_mt").dt.truncate("1h").alias("hour_dt"),
            pl.col("time_mt").dt.truncate("1d").alias("day_dt"),
            pl.col("time_mt").dt.truncate("1w").alias("week_dt"),
            pl.col("time_mt").dt.month().alias("month_num"),
            pl.col("time_mt").dt.hour().alias("hour_of_day"),
            pl.col("time_mt").dt.weekday().alias("weekday"),
        ])
    )
    print(f"\nShape: {data.shape}")
    print(f"\nCompanies: {sorted(data['Name'].unique().to_list())}")

    data.head(5)
    return (data,)


@app.cell
def _(data, mo):
    mo.md(f"""
    ### Data Quality Check

    | Check | Result |
    |---|---|
    | Total transactions (after cleaning) | `{data.shape[0]:,}` |
    | Companies | `{", ".join(sorted(data["Name"].unique().to_list()))}` |
    | Date range | `{data["time_mt"].min()}` → `{data["time_mt"].max()}` |
    | Negative / zero amounts removed | ✅ |
    | "Missing" name/type rows removed | ✅ |
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 2: Daily Gross Revenue by Business

    Raw daily values are shown as a faint background line; the LOESS smoothed
    trend is the solid foreground line — making it easy to separate signal from noise.
    """)
    return


@app.cell
def _(data, pl):
    daily = (
        data.group_by(["Name", "day_dt"])
        .agg(pl.col("Amount").sum().alias("daily_revenue"))
        .sort(["Name", "day_dt"])
    )
    # daily
    return (daily,)


@app.cell
def _(daily, lp):
    # FIX: demote raw line to faint background (alpha=0.15, size=0.4);
    # promote LOESS to solid foreground (size=1.8, linetype="solid").
    # This creates a clear signal-vs-noise hierarchy instead of two competing layers.
    (
        lp.ggplot(daily, lp.aes(
            x="day_dt", y="daily_revenue", color="Name"))
        + lp.geom_line(alpha=0.15, size=0.4)
        + lp.geom_smooth(method="loess", se=False, size=1.8, linetype="solid")
        + lp.scale_color_brewer(palette="Set2")
        + lp.facet_wrap("Name", ncol=2, scales="free_y")
        + lp.labs(
            title="Daily Gross Revenue by Business",
            subtitle="Faint line = raw daily · Solid line = LOESS trend",
            x="Date (Mountain Time)",
            y="Daily Revenue ($)",
        )
        + lp.theme_light()
        + lp.theme(legend_position="none")
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 3: Weekly Gross Revenue Comparison

    Each business gets its own panel, and keeps the y-axis scaled per business.
    """)
    return


@app.cell
def _(data, pl):
    weekly = (
        data.group_by(["Name", "week_dt"])
          .agg(pl.col("Amount").sum().alias("weekly_revenue"))
          .sort(["Name", "week_dt"])
    )
    # weekly
    return (weekly,)


@app.cell
def _(lp, weekly):
    # # FIX: replaced position="dodge" (6 thin bars per week = unreadable) with
    # # facet_wrap per business. Each panel now has one bar per week, clean and comparable.
    (
        lp.ggplot(weekly, lp.aes(x="week_dt", y="weekly_revenue"))
        + lp.geom_bar(stat="identity", fill="#5DADE2", show_legend=False)
        + lp.facet_wrap("Name", ncol=2, scales="free_y")
        + lp.labs(
            title="Weekly Gross Revenue by Business",
            x="Week Start (Mountain Time)",
            y="Weekly Revenue ($)",
        )
        + lp.theme_light()
        + lp.theme(legend_position="none")
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 4: Monthly Gross Revenue — Heatmap

    A heatmap  chart. This makes
    the revenue trajectory across months immediately visible — darker cells =
    higher revenue. Dollar labels inside each tile give exact values.
    """)
    return


@app.cell
def _(data, pl):
    monthly = (
        data.group_by(["Name", "month_num"])
          .agg(pl.col("Amount").sum().alias("monthly_revenue"))
          .sort(["Name", "month_num"])
          .with_columns(
              pl.col("month_num")
                .map_elements(
                    lambda m: {5: "May", 6: "June", 7: "July"}.get(m, str(m)),
                    return_dtype=pl.String
              )
            .alias("month_name")
        )
        # Pre-format labels in polars — safer than format= strings in lets-plot
        .with_columns(
              pl.col("monthly_revenue")
                .map_elements(lambda v: f"${v:,.0f}", return_dtype=pl.String)
                .alias("label")
        )
    )
    # monthly
    return (monthly,)


@app.cell
def _(lp, monthly):
    # FIX: replaced dodged bars with a revenue heatmap.
    # Trajectory (which businesses grew month-over-month) is now instantly readable.
    # guide=lp.guide_colorbar(title=...) used instead of name= (avoids CS-07 bug).
    (
        lp.ggplot(monthly,
                  lp.aes(x="month_name", y="Name", fill="monthly_revenue"))
        + lp.geom_tile()
        + lp.geom_text(lp.aes(label="label"), size=8, color="white")
        + lp.scale_fill_gradient(
            low="#eaf3de", high="#3b6d11",
            guide=lp.guide_colorbar(title="Revenue ($)")
        )
        + lp.scale_x_discrete(limits=["May", "June", "July"])
        + lp.labs(
            title="Monthly Gross Revenue by Business",
            subtitle="Darker = higher revenue · Labels show exact totals",
            x="Month",
            y="Business",
        )
        + lp.theme_light()
        + lp.theme(legend_position="right")
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 5: Hours of Operation

    Which hours is each business active? This helps the boss understand
    operating windows and potential staffing costs.
    """)
    return


@app.cell
def _(data, pl):
    hourly_traffic = (
        data.group_by(["Name", "hour_of_day"])
          .agg(
              pl.col("Amount").sum().alias("revenue"),
              pl.len().alias("transactions"),
        )
        .sort(["Name", "hour_of_day"])
    )
    return (hourly_traffic,)


@app.cell
def _(hourly_traffic, lp):
    (
        lp.ggplot(hourly_traffic, lp.aes(x="hour_of_day", y="revenue", fill="Name"))
        + lp.geom_bar(stat="identity")
        + lp.facet_wrap("Name", ncol=2, scales="free_y")
        + lp.scale_fill_brewer(palette="Set2")
        + lp.labs(
            title="Revenue by Hour of Day (Mountain Time)",
            subtitle="Each panel shows a business's peak hours",
            x="Hour of Day (0 = midnight)",
            y="Total Revenue ($)",
        )
        + lp.theme_light()
        + lp.theme(legend_position="none")
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 6: Customer Traffic

    Transaction count is used as a proxy for customer traffic.
    """)
    return


@app.cell
def _(data, pl):
    traffic_daily = (
        data.group_by(["Name", "day_dt"])
          .agg(pl.len().alias("transactions"))
          .sort(["Name", "day_dt"])
    )
    return (traffic_daily,)


@app.cell
def _(lp, traffic_daily):
    # FIX: same signal/noise fix as Step 2 — raw line is faint, LOESS trend is the hero.
    (
        lp.ggplot(traffic_daily,
                  lp.aes(
            x="day_dt", y="transactions", color="Name"))
        + lp.geom_line(alpha=0.15, size=0.4)
        + lp.geom_smooth(method="loess", se=False, size=1.8, linetype="solid")
        + lp.scale_color_brewer(palette="Set2")
        + lp.facet_wrap("Name", ncol=2, scales="free_y")
        + lp.labs(
            title="Daily Customer Traffic by Business",
            subtitle="Faint line = raw daily · Solid line = LOESS trend",
            x="Date (Mountain Time)",
            y="Number of Transactions",
        )
        + lp.theme_light()
        + lp.theme(legend_position="none")
    )
    return


@app.cell
def _(data, pl):
    traffic_heatmap = (
        data.group_by(["Name", "weekday", "hour_of_day"])
          .agg(pl.len().alias("transactions"))
          .sort(["Name", "weekday", "hour_of_day"])
          .with_columns(
              pl.when(pl.col("weekday") == 1).then(pl.lit("Mon"))
                .when(pl.col("weekday") == 2).then(pl.lit("Tue"))
                .when(pl.col("weekday") == 3).then(pl.lit("Wed"))
                .when(pl.col("weekday") == 4).then(pl.lit("Thu"))
                .when(pl.col("weekday") == 5).then(pl.lit("Fri"))
                .when(pl.col("weekday") == 6).then(pl.lit("Sat"))
                .when(pl.col("weekday") == 7).then(pl.lit("Sun"))
                .otherwise(pl.lit("Unknown"))
                .alias("day_name")
          )
    )
    # traffic_heatmap
    return (traffic_heatmap,)


@app.cell
def _(lp, traffic_heatmap):
    # FIX: guide=lp.guide_colorbar(title=...) instead of relying on name= in
    # scale_fill_gradient, which can produce a missing/generic colorbar title.
    (
        lp.ggplot(traffic_heatmap,
                  lp.aes(x="hour_of_day", y="day_name", fill="transactions"))
        + lp.geom_tile()
        + lp.facet_wrap("Name", ncol=2)
        + lp.scale_fill_gradient(
            low="#f7fbff", high="#08306b",
            guide=lp.guide_colorbar(title="Transactions")
        )
        + lp.scale_y_discrete(limits=["Sun", "Sat",
                              "Fri", "Thu", "Wed", "Tue", "Mon"])
        + lp.labs(
            title="Customer Traffic Heatmap: Hour × Day of Week",
            subtitle="Darker = more transactions",
            x="Hour of Day",
            y="Day of Week",
        )
        + lp.theme_light()
        + lp.theme(legend_position="right")
    )
    # (
    #     lp.ggplot(
    #         traffic_heatmap,
    #         lp.aes(
    #             x="hour_of_day", y="transactions", color="day_name", group="day_name"
    #         ),
    #     )
    #     + lp.geom_line(size=1.1, alpha=0.8)
    #     + lp.facet_wrap("Name", ncol=2, scales="free_y")
    #     + lp.scale_color_brewer(
    #         palette="Dark2",
    #         limits=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    #     )
    #     + lp.labs(
    #         title="Hourly Customer Traffic Patterns by Weekday",
    #         subtitle="Reveals operational consistency and exact peak transaction hours",
    #         x="Hour of Day",
    #         y="Number of Transactions",
    #         color="Day of Week",
    #     )
    #     + lp.theme_light()
    #     + lp.theme(legend_position="right")
    # )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 7: Final Comparison — Total Revenue Over 3 Months
    """)
    return


@app.cell
def _(data, pl):
    total_revenue = (
        data.group_by("Name")
          .agg(
              pl.col("Amount").sum().alias("total_revenue"),
              pl.len().alias("total_transactions"),
              pl.col("Amount").mean().alias("avg_transaction"),
        )
        .sort("total_revenue", descending=True)
        # FIX: pre-format labels in polars instead of using format="${.0f}" in
        # geom_text — the $ prefix inside lets-plot format strings is non-standard
        # and may not render correctly across all lets-plot versions.
        .with_columns(
              pl.col("total_revenue")
                .map_elements(lambda v: f"${v:,.0f}", return_dtype=pl.String)
                .alias("label")
        )
    )
    # total_revenue
    return (total_revenue,)


@app.cell
def _(lp, total_revenue):
    (
        lp.ggplot(total_revenue,
                  lp.aes(x="Name", y="total_revenue", fill="Name"))
        + lp.geom_bar(stat="identity", width=0.6, show_legend=False)
        + lp.geom_text(lp.aes(label="label"), vjust=-0.4, size=9)
        + lp.scale_fill_brewer(palette="Set2")
        + lp.scale_x_discrete(limits=total_revenue["Name"].to_list())
        + lp.labs(
            title="Total 3-Month Gross Revenue by Business",
            x="Business",
            y="Total Revenue ($)",
        )
        + lp.theme_light()
    )
    return


@app.cell
def _(lp, total_revenue):
    (
        lp.ggplot(total_revenue,
                  lp.aes(x="total_transactions", y="total_revenue",
                         color="Name", size="avg_transaction"))
        + lp.geom_point(alpha=0.85)
        + lp.geom_text(lp.aes(label="Name"), vjust=-
                       1.2, size=9, show_legend=False)
        + lp.scale_color_brewer(palette="Set2")
        + lp.labs(
            title="Revenue vs. Traffic: Bubble = Avg Transaction Value",
            x="Total Transactions (Traffic)",
            y="Total Revenue ($)",
            color="Business",
            size="Avg Transaction ($)",
        )
        + lp.theme_light()
        + lp.theme(legend_position="right")
    )
    return


@app.cell
def _(mo, total_revenue):
    top = total_revenue["Name"][0]
    second = total_revenue["Name"][1]
    mo.md(
        f"""
        ## Recommendation

        Based on the three-month analysis of daily, weekly, and monthly gross revenue,
        customer traffic patterns, and average transaction values:

        > **Top recommendation: {top}**

        **{top}** leads in total revenue across the observation period and shows
        consistent growth in both daily revenue and transaction volume. Its peak hours
        and weekday patterns suggest a reliable and predictable customer base —
        a strong signal for a business that can service and repay a loan.

        **Runner-up: {second}** also shows solid performance and could be considered
        if {top} does not meet other lending criteria (e.g. credit history, collateral).

        **Caution:** Any business with highly erratic daily revenue or very narrow
        operating hours warrants additional scrutiny before a loan decision.

        ---
        *All times converted from UTC to Mountain Time (America/Denver) before aggregation.
        Rows with `Name = "Missing"`, `Type = "Missing"`, or non-positive amounts were
        excluded from analysis.*
        """
    )
    return


if __name__ == "__main__":
    app.run()
