# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "polars",
#     "pandas",
#     "rdata",
#     "lets-plot",
# ]
# ///

import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _():
    import re
    import rdata
    import polars as pl
    import pandas as pd
    from lets_plot import (
        ggplot, aes, geom_bar, geom_text, coord_flip, facet_wrap,
        scale_fill_manual, scale_fill_gradient, labs,
        theme_light, theme, element_text, element_rect,
        position_dodge, ggsize, LetsPlot
    )
    LetsPlot.setup_html()
    return (
        aes,
        coord_flip,
        element_rect,
        element_text,
        facet_wrap,
        geom_bar,
        ggplot,
        ggsize,
        labs,
        pd,
        pl,
        position_dodge,
        rdata,
        re,
        scale_fill_gradient,
        scale_fill_manual,
        theme,
        theme_light,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🏗️ CS-06: The Collapse of Construction in Idaho
    ### Idaho Restaurant Commission — 2008 & 2009 Building Permit Analysis

    ---

    It is 2010. Idaho's construction sector has just lived through one of its
    worst downturns in decades. The Restaurant Commission has asked us to make
    sense of two years of commercial building permits — 1,248 projects across
    every Idaho county — and answer four specific questions about what happened
    to restaurant construction during that period.

    **The four questions we answer:**

    1. How did full-service restaurant construction compare to quick-service across county and year?
    2. How did restaurant construction fare compared to all other commercial construction?
    3. Which county spent the most on fast-food construction each year?
    4. In that county, how did other commercial construction compare?

    > **Data sources:** `buildings0809`, `restaurants`, `climate_zone_fips`, `permits`
    > from the [hathawayj/buildings](https://github.com/hathawayj/buildings) R package.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 📦 Step 1 — Load & Inspect the Data
    """)
    return


@app.cell
def _(pd, pl, rdata):
    b_raw = rdata.read_rda("../../data/raw/buildings_all_tagged.rda")
    r_raw = rdata.read_rda("../../data/raw/restaurants_lookup.rda")

    buildings   = pl.from_pandas(pd.DataFrame(list(b_raw.values())[0]))
    restaurants = pl.from_pandas(pd.DataFrame(list(r_raw.values())[0]))
    return buildings, restaurants


@app.cell(hide_code=True)
def _(buildings, mo, restaurants):
    mo.md(f"""
    **Buildings dataset:** {buildings.shape[0]:,} rows × {buildings.shape[1]} columns
    covering Idaho commercial construction permits in 2008 and 2009.

    **Restaurants dataset:** {restaurants.shape[0]:,} rows — a lookup table mapping
    restaurant chain names to dining categories
    (Fast Food, Casual Dining, Pizza, coffee, Ice Cream, Fast Casual).

    Key columns in `buildings`:
    - `ProjectTitle` — free-text name of the project (where regex is needed!)
    - `Type` — building category; we focus on `Food_Beverage_Service`
    - `SqFt` — square footage (used for fallback size-based classification)
    - `Value1000` — construction value in thousands of dollars
    - `County`, `Year`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🧹 Step 2 — Clean & Standardise
    """)
    return


@app.cell
def _(buildings, pl):
    # Regex: strip ", ID" suffix from county names for clean labels
    buildings_clean = buildings.with_columns(
        pl.col("County")
          .str.replace(r",\s*ID$", "", literal=False)
          .str.strip_chars()
          .str.to_titlecase()
          .alias("county_clean")
    )
    return (buildings_clean,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    County names arrived as `"ADA, ID"`, `"BANNOCK, ID"` etc.
    A simple regex — `r",\s*ID$"` — strips the state suffix and
    `str.to_titlecase()` converts to `"Ada"`, `"Bannock"`.
    Clean labels, zero manual editing.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🔍 Step 3 — Classify Restaurant Types

    The `Food_Beverage_Service` building type is a mixed bag — it includes
    school cafeterias, bakeries, and retail food outlets alongside actual
    restaurants. We need to:

    1. **Exclude** non-restaurants (cafeterias, schools, warehouses, etc.)
    2. **Match** known chain names from the `restaurants` lookup table
    3. **Match** keyword patterns in `ProjectTitle` using **regex**
    4. **Apply fallback rules** based on square footage for anything remaining

    Classification priority order:
    ```
    Not-restaurant keywords  →  excluded
    Standalone retail        →  excluded
    Known QS chain names     →  Quick Service
    Known FS chain names     →  Full Service
    QS keyword patterns      →  Quick Service
    FS keyword patterns      →  Full Service
    SqFt ≥ 4,000             →  Full Service  (fallback)
    SqFt > 0 & < 4,000       →  Quick Service (fallback)
    Otherwise                →  Unknown
    ```
    """)
    return


@app.cell
def _(pl, re, restaurants):
    # ── Keyword lists (standardised, lower-case) ──────────────────────────────
    not_restaurants   = [
        "development", "food preperation center", "food services center",
        "bakery", "grocery", "conceession", "cafeteria", "lunchroom",
        "school", "facility", " hall ", "dining hall", "concession",
        "jazz club", "facade", "office", "warehouse", "retail", "repair"
    ]
    standalone_retail = [
        "wine", "spirits", "liquor", "convenience", "drugstore",
        "flying j", "rite aid", "walgreens", "love's travel"
    ]
    full_service_type = [
        "ristorante", "mexican", "pizza", "steakhouse", "grill",
        "buffet", "tavern", " bar", "waffle", "italian", "steak house",
        "sushi", "bbq", "roadhouse", "barbeque"
    ]
    quick_service_type = [
        "coffee", "java", "donut", "doughnut", "burger", "ice cream",
        "custard", "sandwich", "fast food", "bagel", "drive.thru",
        "drive thru", "espresso", "smoothie", "sub shop", "taco", "smashburger"
    ]

    # ── Name lookups from restaurants dataset ────────────────────────────────
    qs_names = [
        n.strip().lower() for n in
        restaurants.filter(
            pl.col("Type").is_in(["coffee", "Ice Cream", " Ice Cream", "Fast Food"])
        )["Restaurant"].to_list()
    ]
    fs_names = [
        n.strip().lower() for n in
        restaurants.filter(
            pl.col("Type").is_in(["Pizza", "Casual Dining", "Fast Casual"])
        )["Restaurant"].to_list()
    ]

    # ── Classification function ───────────────────────────────────────────────
    def classify(title: str, sqft: float) -> str:
        t = title.strip().lower()
        # Exclusions
        if any(kw in t for kw in not_restaurants):   return "Not Restaurant"
        if any(kw in t for kw in standalone_retail): return "Not Restaurant"
        # Known names (regex word-boundary–style match)
        for name in qs_names:
            if re.search(re.escape(name), t):        return "Quick Service"
        for name in fs_names:
            if re.search(re.escape(name), t):        return "Full Service"
        # Keyword patterns
        if any(re.search(re.escape(kw), t) for kw in quick_service_type): return "Quick Service"
        if any(re.search(re.escape(kw), t) for kw in full_service_type):  return "Full Service"
        # Size fallback
        if sqft >= 4000: return "Full Service"
        if sqft > 0:     return "Quick Service"
        return "Unknown"

    return (classify,)


@app.cell
def _(buildings_clean, classify, pl):
    food_df = (
        buildings_clean
        .filter(pl.col("Type") == "Food_Beverage_Service")
        .with_columns(
            pl.struct(["ProjectTitle", "SqFt"])
              .map_elements(
                  lambda r: classify(r["ProjectTitle"], r["SqFt"]),
                  return_dtype=pl.Utf8
              )
              .alias("RestaurantType")
        )
    )

    rest_df = food_df.filter(
        pl.col("RestaurantType").is_in(["Full Service", "Quick Service", "Unknown"])
    )
    return food_df, rest_df


@app.cell(hide_code=True)
def _(food_df, mo):
    _summary = food_df.group_by("RestaurantType").len().sort("len", descending=True)
    _rows = _summary.to_dicts()

    mo.md(f"""
    **Classification results across {food_df.shape[0]} Food & Beverage buildings:**

    | Category | Count |
    |---|---|
    {"".join(f"| {r['RestaurantType']} | {r['len']} |" + chr(10) for r in _rows)}

    > **21 "Unknown"** entries are generic titles like *"Restaurant (Alteration)"*
    > with zero square footage — no keyword or name matched, and no size data
    > to fall back on. These are included in restaurant totals where relevant
    > but excluded from the Full/Quick comparison to avoid noise.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## 📊 Question 1
    ### How did full-service restaurant construction compare to quick-service across county and year?
    """)
    return


@app.cell
def _(
    aes,
    element_rect,
    element_text,
    facet_wrap,
    geom_bar,
    ggplot,
    ggsize,
    labs,
    pl,
    position_dodge,
    rest_df,
    scale_fill_manual,
    theme,
    theme_light,
):
    q1_df = (
        rest_df
        .filter(pl.col("RestaurantType").is_in(["Full Service", "Quick Service"]))
        .group_by(["county_clean", "Year", "RestaurantType"])
        .agg(pl.col("Value1000").sum().alias("TotalValue"))
        .sort(["county_clean", "Year"])
    ).to_pandas()

    p1 = (
        ggplot(q1_df, aes(x="county_clean", y="TotalValue", fill="RestaurantType"))
        + geom_bar(stat="identity", position=position_dodge(width=0.75), width=0.65)
        + facet_wrap("Year", nrow=2)
        + scale_fill_manual(values={"Full Service": "#1B5299", "Quick Service": "#E07B00"})
        + labs(
            title="Full-Service vs Quick-Service Restaurant Construction in Idaho",
            subtitle="Total construction value ($1,000s) by county — 2008 vs 2009",
            x="County",
            y="Construction Value ($1,000s)",
            fill="Restaurant Type"
        )
        + theme_light()
        + theme(
            axis_text_x=element_text(angle=40, hjust=1, size=9),
            plot_title=element_text(size=13, face="bold"),
            strip_background=element_rect(fill="#1B5299"),
            strip_text=element_text(color="white", face="bold"),
            legend_position="bottom"
        )
        + ggsize(880, 620)
    )
    p1
    return (q1_df,)


@app.cell(hide_code=True)
def _(mo, q1_df):
    # Compute key stats for the summary
    _ada_2008_fs = q1_df[(q1_df["county_clean"]=="Ada") & (q1_df["Year"]=="2008") & (q1_df["RestaurantType"]=="Full Service")]["TotalValue"].sum()
    _ada_2008_qs = q1_df[(q1_df["county_clean"]=="Ada") & (q1_df["Year"]=="2008") & (q1_df["RestaurantType"]=="Quick Service")]["TotalValue"].sum()
    _ada_2009_fs = q1_df[(q1_df["county_clean"]=="Ada") & (q1_df["Year"]=="2009") & (q1_df["RestaurantType"]=="Full Service")]["TotalValue"].sum()
    _ada_2009_qs = q1_df[(q1_df["county_clean"]=="Ada") & (q1_df["Year"]=="2009") & (q1_df["RestaurantType"]=="Quick Service")]["TotalValue"].sum()
    _total_fs_08 = q1_df[(q1_df["RestaurantType"]=="Full Service") & (q1_df["Year"]=="2008")]["TotalValue"].sum()
    _total_qs_08 = q1_df[(q1_df["RestaurantType"]=="Quick Service") & (q1_df["Year"]=="2008")]["TotalValue"].sum()

    mo.callout(
        mo.md(f"""
        **Key findings:**

        - **Ada County** (Greater Boise) is the dominant market by far —
          it accounts for the vast majority of restaurant construction investment
          in both years and both categories.

        - In Ada County, **Full Service** construction totalled **${_ada_2008_fs:,.0f}K** in 2008
          and **${_ada_2009_fs:,.0f}K** in 2009, while **Quick Service** came in at
          **${_ada_2008_qs:,.0f}K** (2008) and **${_ada_2009_qs:,.0f}K** (2009).

        - **Full Service restaurants held up better.** Quick-service construction
          in Ada County dropped sharply from 2008 to 2009, while full-service
          remained more resilient — suggesting sit-down dining projects
          were already in the pipeline and harder to cancel.

        - Outside Ada, **Canyon, Kootenai, and Bonneville** counties show
          small but meaningful restaurant activity. Every other county
          recorded minimal or no restaurant construction.
        """),
        kind="info"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## 📊 Question 2
    ### How did restaurant construction fare compared to all other commercial construction in Idaho?
    """)
    return


@app.cell
def _(
    aes,
    buildings_clean,
    element_text,
    geom_bar,
    ggplot,
    ggsize,
    labs,
    pl,
    position_dodge,
    scale_fill_manual,
    theme,
    theme_light,
):
    q2_df = (
        buildings_clean
        .with_columns(
            pl.when(pl.col("Type") == "Food_Beverage_Service")
              .then(pl.lit("Restaurant"))
              .otherwise(pl.lit("Other Commercial"))
              .alias("Sector")
        )
        .group_by(["Year", "Sector"])
        .agg(pl.col("Value1000").sum().alias("TotalValue"))
        .sort(["Year", "Sector"])
    ).to_pandas()

    p2 = (
        ggplot(q2_df, aes(x="Year", y="TotalValue", fill="Sector"))
        + geom_bar(stat="identity", position=position_dodge(width=0.6), width=0.5)
        + scale_fill_manual(values={"Restaurant": "#C0392B", "Other Commercial": "#95A5A6"})
        + labs(
            title="Restaurant vs All Other Commercial Construction in Idaho",
            subtitle="Construction value ($1,000s) — 2008 vs 2009",
            x="Year",
            y="Construction Value ($1,000s)",
            fill="Sector"
        )
        + theme_light()
        + theme(
            plot_title=element_text(size=13, face="bold"),
            legend_position="bottom"
        )
        + ggsize(680, 480)
    )
    p2
    return (q2_df,)


@app.cell(hide_code=True)
def _(mo, q2_df):
    _rest_08   = q2_df[(q2_df["Sector"]=="Restaurant")       & (q2_df["Year"]=="2008")]["TotalValue"].sum()
    _other_08  = q2_df[(q2_df["Sector"]=="Other Commercial") & (q2_df["Year"]=="2008")]["TotalValue"].sum()
    _rest_09   = q2_df[(q2_df["Sector"]=="Restaurant")       & (q2_df["Year"]=="2009")]["TotalValue"].sum()
    _other_09  = q2_df[(q2_df["Sector"]=="Other Commercial") & (q2_df["Year"]=="2009")]["TotalValue"].sum()
    _rest_pct  = _rest_08  / (_rest_08 + _other_08) * 100
    _drop_rest = (_rest_09  - _rest_08)  / _rest_08  * 100
    _drop_other= (_other_09 - _other_08) / _other_08 * 100

    mo.callout(
        mo.md(f"""
        **Key findings:**

        - Restaurants represent only **{_rest_pct:.1f}%** of total commercial
          construction value in 2008 — a small but visible slice.

        - From 2008 to 2009, **restaurant construction fell {_drop_rest:.0f}%**
          (from **${_rest_08:,.0f}K** to **${_rest_09:,.0f}K**),
          while all other commercial construction fell **{_drop_other:.0f}%**
          (from **${_other_08:,.0f}K** to **${_other_09:,.0f}K**).

        - The restaurant sector did not collapse in isolation — it was caught
          inside a **broad, economy-wide construction bust**. The Financial
          Crisis of 2008 froze credit markets, and new commercial builds
          across every sector dried up simultaneously.

        - If anything, restaurants weathered the downturn *slightly* better
          than the overall market in proportional terms, likely because
          food-service projects tend to be smaller, faster to complete, and
          harder to cancel once a franchise lease is signed.
        """),
        kind="warn"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## 📊 Question 3
    ### Which county in Idaho spent the most on fast-food (quick-service) construction each year?
    """)
    return


@app.cell
def _(
    aes,
    coord_flip,
    element_rect,
    element_text,
    facet_wrap,
    geom_bar,
    ggplot,
    ggsize,
    labs,
    pl,
    rest_df,
    scale_fill_gradient,
    theme,
    theme_light,
):
    q3_df = (
        rest_df
        .filter(pl.col("RestaurantType") == "Quick Service")
        .group_by(["county_clean", "Year"])
        .agg(pl.col("Value1000").sum().alias("TotalValue"))
        .sort(["Year", "TotalValue"], descending=[False, True])
    ).to_pandas()

    # Determine top county programmatically
    top_county = (
        q3_df.groupby("county_clean")["TotalValue"]
             .sum()
             .idxmax()
    )

    p3 = (
        ggplot(q3_df, aes(x="county_clean", y="TotalValue", fill="TotalValue"))
        + geom_bar(stat="identity")
        + coord_flip()
        + facet_wrap("Year", nrow=1)
        + scale_fill_gradient(low="#FDE8C8", high="#C0392B")
        + labs(
            title="Quick-Service Restaurant Construction Spend by County",
            subtitle="Which Idaho county invested most in fast food — 2008 vs 2009?",
            x="County",
            y="Construction Value ($1,000s)",
            fill="Value ($K)"
        )
        + theme_light()
        + theme(
            plot_title=element_text(size=13, face="bold"),
            strip_background=element_rect(fill="#C0392B"),
            strip_text=element_text(color="white", face="bold"),
            legend_position="right"
        )
        + ggsize(860, 460)
    )
    p3
    return q3_df, top_county


@app.cell(hide_code=True)
def _(mo, q3_df, top_county):
    _top_08 = q3_df[q3_df["Year"]=="2008"].sort_values("TotalValue", ascending=False).iloc[0]
    _top_09 = q3_df[q3_df["Year"]=="2009"].sort_values("TotalValue", ascending=False).iloc[0]
    _second_08 = q3_df[q3_df["Year"]=="2008"].sort_values("TotalValue", ascending=False).iloc[1]

    mo.callout(
        mo.md(f"""
        **Key findings:**

        - **{top_county} County** is the undisputed fast-food construction
          capital of Idaho in both years.

        - In 2008, {_top_08['county_clean']} County spent **${_top_08['TotalValue']:,.0f}K**
          on quick-service construction — more than **{_top_08['TotalValue'] / _second_08['TotalValue']:.1f}×**
          the second-place county ({_second_08['county_clean']}, ${_second_08['TotalValue']:,.0f}K).

        - In 2009, {_top_09['county_clean']} County still led with **${_top_09['TotalValue']:,.0f}K**,
          though total spend fell significantly as the economic downturn hit.

        - The concentration in Ada reflects its population density and the
          presence of major commercial corridors in Boise, Meridian, and Nampa
          — prime locations for national fast-food franchise expansion.
        """),
        kind="success"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## 📊 Question 4
    ### In that county, how did other commercial construction compare?
    """)
    return


@app.cell
def _(
    aes,
    buildings_clean,
    coord_flip,
    element_text,
    geom_bar,
    ggplot,
    ggsize,
    labs,
    pl,
    position_dodge,
    scale_fill_manual,
    theme,
    theme_light,
    top_county,
):
    q4_df = (
        buildings_clean
        .filter(pl.col("county_clean") == top_county)
        .group_by(["Year", "Type"])
        .agg(pl.col("Value1000").sum().alias("TotalValue"))
        .with_columns(
            pl.col("Type")
              .str.replace_all("_", " ")
              .str.to_titlecase()
              .str.slice(0, 32)
              .alias("TypeLabel")
        )
        .sort("TotalValue", descending=True)
    ).to_pandas()

    # Top 10 building types by combined value across both years
    _top10 = (
        q4_df.groupby("TypeLabel")["TotalValue"]
             .sum()
             .nlargest(10)
             .index.tolist()
    )
    q4_plot = q4_df[q4_df["TypeLabel"].isin(_top10)].copy()

    p4 = (
        ggplot(q4_plot, aes(x="TypeLabel", y="TotalValue", fill="Year"))
        + geom_bar(stat="identity", position=position_dodge(width=0.7), width=0.62)
        + coord_flip()
        + scale_fill_manual(values={"2008": "#1B5299", "2009": "#C0392B"})
        + labs(
            title=f"{top_county} County — Commercial Construction by Sector",
            subtitle="How restaurant construction compares to other building types — 2008 vs 2009",
            x="Building Type",
            y="Construction Value ($1,000s)",
            fill="Year"
        )
        + theme_light()
        + theme(
            plot_title=element_text(size=13, face="bold"),
            legend_position="bottom"
        )
        + ggsize(900, 560)
    )
    p4
    return (q4_df,)


@app.cell(hide_code=True)
def _(mo, q4_df, top_county):
    _food_total = q4_df[q4_df["TypeLabel"].str.contains("Food|Beverage", na=False)]["TotalValue"].sum()
    _grand_total = q4_df["TotalValue"].sum()
    _food_share = _food_total / _grand_total * 100 if _grand_total > 0 else 0

    _top_sector = (
        q4_df.groupby("TypeLabel")["TotalValue"]
             .sum()
             .idxmax()
    )
    _top_sector_val = q4_df.groupby("TypeLabel")["TotalValue"].sum().max()

    mo.callout(
        mo.md(f"""
        **Key findings:**

        - In {top_county} County, **Food & Beverage** accounts for roughly
          **{_food_share:.1f}%** of total commercial construction value
          across both years — a meaningful but not dominant sector.

        - The **{_top_sector}** sector dwarfs restaurants in absolute terms
          (${_top_sector_val:,.0f}K combined), reflecting the broader mix
          of commercial development happening in the Boise metro area.

        - The **2009 collapse** is visible across *every* sector — the blue
          (2008) bars are consistently taller than the red (2009) bars.
          This is not a restaurant story; it is an **economy-wide story**.

        - The sectors that fell hardest were large-footprint commercial
          projects — offices, stores, and shopping centres — which require
          long-term financing commitments that dried up after the financial
          crisis. Restaurants, being smaller and often franchise-driven,
          were somewhat insulated.

        - **Implication for the Commission:** the drop in restaurant
          construction mirrors the broader market. Monitoring restaurant
          construction as a share of total commercial building — rather
          than in absolute terms — would give a cleaner signal of industry
          health going forward.
        """),
        kind="neutral"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## 📝 Executive Summary

    The Idaho Restaurant Commission asked us to examine two years of commercial
    building permits during a turbulent economic period. Here is what the data shows:

    **1. Full Service vs Quick Service**
    Ada County dominated both categories. Quick-service construction was
    hit harder in 2009, while full-service projects proved more resilient —
    likely because larger sit-down restaurant builds had longer lead times
    and were already committed before the downturn.

    **2. Restaurants vs the broader market**
    Restaurants were a small fraction (~3–5%) of all commercial construction.
    Both sectors declined sharply from 2008 to 2009, but restaurants did not
    collapse disproportionately — the whole market contracted together.

    **3. Fast-food investment concentration**
    Ada County led fast-food construction spend in both years, by a wide
    margin. The Boise–Meridian corridor was the primary growth engine for
    franchise quick-service expansion in Idaho.

    **4. Ada County's construction landscape**
    Within Ada, Food & Beverage sits in the middle of the sector pack.
    Offices and retail led construction volume. The 2009 decline was
    universal — every sector fell, not just restaurants.

    ---
    > *Analysis produced for the Idaho Restaurant Commission, 2010.*
    > *Data: hathawayj/buildings R package. Tools: Polars · Regex · lets-plot · Marimo.*
    """)
    return


if __name__ == "__main__":
    app.run()
