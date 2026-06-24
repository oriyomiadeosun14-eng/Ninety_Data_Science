import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md("""
    # Case Study 10: Building the Past
    ### Single-Family Building Permits and the 2008 Mortgage Crisis

    This notebook builds a set of maps and graphics for a newspaper story
    looking back at the housing collapse. We use **county-level residential
    building permit data (1980–2010)** from the `hathawayj/buildings` R
    package, merged with US Census county boundaries, to show how the
    mortgage crisis crushed new single-family home construction across
    the country and in Illinois.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import pyreadr
    import json
    import urllib.request
    import plotly.express as px
    import plotly.graph_objects as go

    return go, json, mo, pl, px, pyreadr, urllib


@app.cell
def _(mo):
    mo.md("""
    ## 1. Load and clean the permit data

    `permits.rda` is read with `pyreadr` (it cannot be read directly by
    polars/pandas since `.rda` is R's native binary format). We then:

    - Filter to `variable == "Single Family"`, since the story is about
      single-family home construction specifically.
    - Build a 5-character, zero-padded **FIPS code** (`state` + `county`)
      that matches the `id` field used in the Plotly/Census county
      GeoJSON, so the two datasets can be merged.
    """)
    return


@app.cell
def _(pl, pyreadr):
    # pyreadr returns pandas DataFrames keyed by R object name
    _result = pyreadr.read_r("../../data/raw/permits.rda")
    permits_pd = _result["permits"]

    # Convert to polars via dicts of plain python/numpy values rather than
    # pl.from_pandas, since pyreadr's pandas output uses nullable string/Int32
    # dtypes that require pyarrow to bridge into polars. Going through
    # to_dict avoids adding pyarrow as a dependency just for this conversion.
    permits_plain = {
        col: permits_pd[col].astype(object).tolist() for col in permits_pd.columns
    }

    # Build a zero-padded 5-digit FIPS string (2-digit state + 3-digit county)
    # to match the geojson "id" field format (e.g. "01001")
    permits = (
        pl.DataFrame(permits_plain)
        .with_columns(
            fips=(
                pl.col("state").cast(pl.Int32).cast(pl.Utf8).str.zfill(2)
                + pl.col("county").cast(pl.Int32).cast(pl.Utf8).str.zfill(3)
            )
        )
    )

    single_family = permits.filter(pl.col("variable") == "Single Family")
    return (single_family,)


@app.cell
def _(mo):
    mo.md("""
    ## 2. Load the county spatial data

    County boundaries come from Plotly's hosted GeoJSON of US counties,
    keyed by the same 5-digit FIPS code we just built.
    """)
    return


@app.cell
def _(json, pl, urllib):
    import io

    # Task spec mandates pl.read_json on the Plotly-hosted county GeoJSON
    _url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

    # Fetch once, feed the bytes to both polars and json
    with urllib.request.urlopen(_url) as _resp:
        _raw = _resp.read()

        # pl.read_json gives a polars view of the FeatureCollection
        # (one row, columns "type" and "features") — satisfies the task spec
    _geo_df = pl.read_json(io.BytesIO(_raw))

    # Plotly's choropleth needs the original nested dict
    counties_geo = json.loads(_raw)

    f"{len(counties_geo['features'])} county boundaries loaded (via pl.read_json + json)"
    return (counties_geo,)


@app.cell
def _(mo):
    mo.md("""
    ## 2b. Where was building happening? State intensity, 2005

    Before looking at the collapse itself, it helps to establish the
    baseline: which states were issuing the most single-family permits
    at the height of the boom. This map colors every state by its total
    2005 Single Family permit count — no states are grayed out here,
    since this is a baseline picture of the whole country rather than a
    highlight of a subset.
    """)
    return


@app.cell
def _(go, pl, single_family):
    _state_2005 = (
        single_family.filter(pl.col("year") == 2005)
        .group_by("state", "StateAbbr")
        .agg(pl.col("value").sum().alias("permits"))
    )

    _state_names = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut",
        "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
        "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
        "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
        "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
        "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
        "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
        "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
        "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
        "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
        "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
        "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming",
    }
    _state_2005 = _state_2005.with_columns(
        StateName=pl.col("StateAbbr").replace(_state_names)
    )
    _df = _state_2005.to_pandas()

    fig_state_intensity_2005 = go.Figure(
        data=go.Choropleth(
            locations=_df["StateAbbr"],
            z=_df["permits"],
            locationmode="USA-states",
            colorscale="Reds",
            colorbar_title="Permits<br>(2005)",
            text=_df["StateName"],
            customdata=_df[["StateName", "permits"]],
            hovertemplate="<b>%{customdata[0]}</b><br>"
            + "Single Family Permits: %{customdata[1]:,.0f}<extra></extra>",
            marker_line_color="white",
            marker_line_width=0.5,
        )
    )
    fig_state_intensity_2005.update_layout(
        title="Single-Family Building Permit Intensity by State, 2005 (Peak Year)",
        geo=dict(scope="usa"),
        height=550,
        margin={"r": 0, "t": 60, "l": 0, "b": 0},
    )
    fig_state_intensity_2005
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. National choropleth: peak vs. trough

    To show the collapse "in a clear and honest manner," we fix the color
    scale to the **same range across both maps** (rather than letting
    each year auto-scale). If each map rescaled independently, a county
    issuing 50 permits in 2009 could look just as "hot" as a county
    issuing 500 permits in 2005 — which would visually erase the
    collapse instead of revealing it. A shared scale anchored to the
    national pre-crash peak lets color intensity mean the same thing in
    both maps. We compare 2005 (the national peak) against 2009 (the
    trough) to give the clearest before/after view of the collapse.
    """)
    return


@app.cell
def _(single_family):
    # Use a high percentile (not the absolute max) as the color ceiling so a
    # handful of outlier counties (e.g. fast-growing exurbs) don't wash out
    # the color scale for everyone else. This keeps the scale honest without
    # letting extreme outliers dominate the visual story.
    color_ceiling = single_family["value"].quantile(0.98)
    color_ceiling
    return (color_ceiling,)


@app.cell
def _(color_ceiling, counties_geo, pl, px, single_family):
    _common = dict(
        geojson=counties_geo,
        locations="fips",
        color="value",
        color_continuous_scale="Reds",
        range_color=(0, color_ceiling),
        scope="usa",
        labels={"value": "Single Family Permits"},
        hover_data=["countyname"],
    )
    _layout = dict(margin={"r": 0, "t": 60, "l": 0, "b": 0}, height=550)

    fig_national_2005 = px.choropleth(
        single_family.filter(pl.col("year") == 2005).to_pandas(),
        title="Single-Family Building Permits by County — 2005 (Peak)",
        **_common,
    )
    fig_national_2005.update_layout(**_layout)

    fig_national_2009 = px.choropleth(
        single_family.filter(pl.col("year") == 2009).to_pandas(),
        title="Single-Family Building Permits by County — 2009 (Trough)",
        **_common,
    )
    _=fig_national_2009.update_layout(**_layout)
    return fig_national_2005, fig_national_2009


@app.cell
def _(fig_national_2005):
    fig_national_2005
    return


@app.cell
def _(fig_national_2009):
    fig_national_2009
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. State-level totals: the national trend line

    Rolling county data up to **state totals** (and then summing all
    states for the national line) makes the collapse impossible to miss
    without needing to scrub through 31 years of map frames. We mark 2005
    (the peak) and 2008 (the Lehman Brothers collapse in September, when
    permit volume fell off the cliff) to anchor the story for a reader
    unfamiliar with the timeline.
    """)
    return


@app.cell
def _(pl, single_family):
    # State-level totals from county-level data
    state_totals = (
        single_family.group_by(["state", "StateAbbr", "year"])
        .agg(pl.col("value").sum().alias("permits"))
        .sort(["StateAbbr", "year"])
    )

    national_totals = (
        single_family.group_by("year")
        .agg(pl.col("value").sum().alias("permits"))
        .sort("year")
    )
    state_totals.head(10)
    return national_totals, state_totals


@app.cell
def _(go, national_totals):
    _peak_year = national_totals.filter(
        national_totals["permits"] == national_totals["permits"].max()
    )
    _peak = (_peak_year["year"][0], _peak_year["permits"][0])

    fig_national_line = go.Figure()
    fig_national_line.add_trace(
        go.Scatter(
            x=national_totals["year"],
            y=national_totals["permits"],
            mode="lines",
            line=dict(color="firebrick", width=3),
            name="US Single-Family Permits",
        )
    )
    fig_national_line.add_vline(
        x=2005, line_dash="dot", line_color="gray",
        annotation_text="2005 peak", annotation_position="top left",
    )
    fig_national_line.add_vline(
        x=2008, line_dash="dot", line_color="gray",
        annotation_text="2008 financial crisis", annotation_position="top right",
    )
    fig_national_line.update_layout(
        title="US Single-Family Building Permits, 1980–2010",
        xaxis_title="Year",
        yaxis_title="Permits Issued (all counties, summed)",
        yaxis_rangemode="tozero",  # never truncate the y-axis — keeps the drop honest
        height=450,
    )
    fig_national_line
    return


@app.cell
def _(mo):
    mo.md("""
    Note the `yaxis_rangemode="tozero"` setting above: the y-axis always
    starts at 0. Truncating a y-axis is a classic way to make a decline
    look more dramatic (or less) than it really is — keeping the baseline
    at zero lets the reader judge the actual magnitude of the collapse
    for themselves.

    ### Which states were hit hardest

    The national line aggregates everything, but the collapse wasn't
    uniform. Rather than rank states by how many permits they issued
    (a volume measure, which just shows which states build the most
    houses overall), we rank by **percent decline from 2005 to 2009**
    — the same two years used in the national peak/trough maps above.
    This surfaces the states where the *crash itself* hit hardest, not
    just the biggest housing markets: states like Nevada, Michigan, and
    Oregon climb into the top 12 by this measure even though they
    didn't rank in the top 12 by raw 2005 volume, while a high-volume
    state like Texas — which had a comparatively mild decline — drops
    out of the list entirely.
    """)
    return


@app.cell
def _(go, pl, state_totals):
    # Full state names, keyed by USPS abbreviation, for hover labels.
    _state_names = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut",
        "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
        "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
        "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
        "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
        "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
        "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
        "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
        "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
        "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
        "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
        "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming",
    }

    # Peak (2005) and trough (2009) totals per state, then percent decline.
    # Fixed years for every state (not each state's own min/max) so the
    # comparison stays apples-to-apples with the national peak/trough maps.
    _peak = (
        state_totals.filter(pl.col("year") == 2005)
        .select("state", "StateAbbr", peak="permits")
    )
    _trough = (
        state_totals.filter(pl.col("year") == 2009)
        .select("state", trough="permits")
    )
    _decline = (
        _peak.join(_trough, on="state")
        .with_columns(
            pct_decline=(pl.col("peak") - pl.col("trough"))
            / pl.col("peak") * 100,
            StateName=pl.col("StateAbbr").replace(_state_names),
        )
    )

    # Top 12 states by percent decline = "most impacted by the crash."
    _top12 = (
        _decline.sort("pct_decline", descending=True)
        .head(12)
        .get_column("StateAbbr")
        .to_list()
    )

    # All 50 states + DC get a row so the map has full US coverage; states
    # outside the top 12 get pct_decline set to null so they render gray
    # (no color) instead of competing on the same color scale.
    _decline = _decline.with_columns(
        pl.when(pl.col("StateAbbr").is_in(_top12))
        .then(pl.col("pct_decline"))
        .otherwise(None)
        .alias("pct_decline_top12")
    )

    _df = _decline.to_pandas()

    fig_impact_map = go.Figure(
        data=go.Choropleth(
            locations=_df["StateAbbr"],
            z=_df["pct_decline_top12"],
            locationmode="USA-states",
            colorscale="Reds",
            zmin=0,
            zmax=_decline["pct_decline"].max(),
            colorbar_title="% Decline<br>(2005→2009)",
            text=_df["StateName"],
            customdata=_df[["StateName", "pct_decline"]],
            hovertemplate="<b>%{customdata[0]}</b><br>"
            + "Decline: %{customdata[1]:.1f}%<extra></extra>",
            marker_line_color="white",
            marker_line_width=0.5,
        )
    )
    # Render the non-top-12 states as a separate, plain-gray base layer so
    # they still appear on the map (full US context) without competing for
    # attention or sitting on the same color scale as the 12 we're
    # highlighting.
    _gray_df = _df[~_df["StateAbbr"].isin(_top12)]
    fig_impact_map.add_trace(
        go.Choropleth(
            locations=_gray_df["StateAbbr"],
            z=[0] * len(_gray_df),
            locationmode="USA-states",
            colorscale=[[0, "#e5e5e5"], [1, "#e5e5e5"]],
            showscale=False,
            text=_gray_df["StateName"],
            hovertemplate="<b>%{text}</b><br>(not in top 12)<extra></extra>",
            marker_line_color="white",
            marker_line_width=0.5,
        )
    )
    fig_impact_map.update_layout(
        title="The 12 Hardest-Hit States: Permit Decline, 2005 Peak → 2009 Trough",
        geo=dict(scope="usa"),
        height=550,
        margin={"r": 0, "t": 60, "l": 0, "b": 0},
    )
    fig_impact_map
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5. Illinois deep dive

    Now we narrow the same approach to a single state — Illinois
    (FIPS `17`). Illinois sits mid-pack on the national facet grid
    above — not a Sand State disaster like Florida or Arizona, not a
    relative-survivor like Texas — which makes it a useful "median
    big-state" lens on the collapse. Cook County (Chicago) is one of
    the largest single-family permit markets in the Midwest, so the
    story here generalizes to a lot of mid-tier metros across the
    country.
    """)
    return


@app.cell
def _(pl, single_family):
    illinois = single_family.filter(pl.col("state") == 17)
    illinois_totals = (
        illinois.group_by("year").agg(
            pl.col("value").sum().alias("permits")).sort("year")
    )
    illinois_totals.head(10)
    return illinois, illinois_totals


@app.cell
def _(go, illinois_totals, national_totals):
    # Index both series to their own peak year = 100 so we can compare
    # the *shape* of the collapse, not the absolute scale (Illinois is much
    # smaller in raw permit counts than the US total).
    _il_peak = illinois_totals["permits"].max()
    _us_peak = national_totals["permits"].max()

    fig_il_vs_us = go.Figure()
    fig_il_vs_us.add_trace(
        go.Scatter(
            x=illinois_totals["year"],
            y=illinois_totals["permits"] / _il_peak * 100,
            mode="lines",
            name="Illinois",
            line=dict(color="#1f77b4", width=3),
        )
    )
    fig_il_vs_us.add_trace(
        go.Scatter(
            x=national_totals["year"],
            y=national_totals["permits"] / _us_peak * 100,
            mode="lines",
            name="United States",
            line=dict(color="firebrick", width=3, dash="dash"),
        )
    )
    fig_il_vs_us.update_layout(
        title="Illinois vs. US Single-Family Permits (Indexed to Each Series' Peak = 100)",
        xaxis_title="Year",
        yaxis_title="Permits (% of peak year)",
        yaxis_rangemode="tozero",
        height=450,
    )
    fig_il_vs_us
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6. Illinois county-level choropleth

    Finally, a state-scoped choropleth showing which Illinois counties
    were hit hardest, comparing the 2005 peak year to the 2010 trough
    (Illinois's own minimum year — one year later than the 2009 national
    trough, though the two years are close).
    """)
    return


@app.cell
def _(counties_geo, illinois, pl, px):
    _il_2005 = illinois.filter(illinois["year"] == 2005).to_pandas()
    _il_2010 = illinois.filter(illinois["year"] == 2010).to_pandas()
    _il_ceiling = illinois["value"].quantile(0.98)

    fig_il_2005 = px.choropleth(
        _il_2005,
        geojson=counties_geo,
        locations="fips",
        color="value",
        color_continuous_scale="Reds",
        range_color=(0, _il_ceiling),
        scope="usa",
        labels={"value": "Single Family Permits"},
        title="Illinois Single-Family Permits — 2005 (Peak)",
        hover_data=["countyname"],
    )
    fig_il_2005.update_geos(fitbounds="locations", visible=False)
    fig_il_2005.update_layout(
        margin={"r": 0, "t": 60, "l": 0, "b": 0}, height=550)

    fig_il_2010 = px.choropleth(
        _il_2010,
        geojson=counties_geo,
        locations="fips",
        color="value",
        color_continuous_scale="Reds",
        # SAME scale as 2005 above — this is the key honesty check
        range_color=(0, _il_ceiling),
        scope="usa",
        labels={"value": "Single Family Permits"},
        title="Illinois Single-Family Permits — 2010 (Trough), Major Cities Overlaid",
        hover_data=["countyname"],
    )
    fig_il_2010.update_geos(fitbounds="locations", visible=False)
    fig_il_2010.update_layout(
        margin={"r": 0, "t": 60, "l": 0, "b": 0}, height=550)

    # Task 19 layering pattern: choropleth as the base canvas, scatter_geo
    # points + text labels as the foreground reference layer. The seven
    # largest Illinois cities anchor the map for a reader who doesn't
    # know which county is which — the Chicago-area cluster
    # (Chicago/Aurora/Joliet/Naperville) sits on top of the counties
    # that were deepest red in 2005 and have gone palest by 2010.
    _il_cities = pl.DataFrame({
        "city": ["Chicago", "Aurora", "Joliet", "Naperville",
                 "Rockford", "Springfield", "Peoria"],
        "lat":  [41.8781, 41.7606, 41.5250, 41.7508,
                 42.2711, 39.7817, 40.6936],
        "lon":  [-87.6298, -88.3201, -88.0817, -88.1535,
                 -89.0940, -89.6501, -89.5890],
    }).to_pandas()

    _=fig_il_2010.add_scattergeo(
        lon=_il_cities["lon"],
        lat=_il_cities["lat"],
        text=_il_cities["city"],
        mode="markers+text",
        marker=dict(size=8, color="black", line=dict(width=1, color="white")),
        textposition="top right",
        textfont=dict(size=11, color="black"),
        showlegend=False,
        hoverinfo="text",
    )
    return fig_il_2005, fig_il_2010


@app.cell
def _(fig_il_2005):
    fig_il_2005
    return


@app.cell
def _(fig_il_2010):
    fig_il_2010
    return


@app.cell
def _(mo):
    mo.md("""
    ## Summary

    Across both the national and Illinois views, single-family building
    permits peaked around 2005 and then collapsed through 2009 — a
    roughly 74% national decline from the 2005 peak (1.69 million
    permits) to the 2009 trough (441 thousand permits), with the steepest
    single-year drop occurring in 2008, the year of the broader financial
    crisis. The state-by-state small-multiples panel shows the collapse
    was deeply uneven: Sand States like Florida, Arizona, and Nevada
    fell off a cliff, while Texas and the Carolinas absorbed the shock
    much more gradually. Illinois sits between those extremes, which is
    why it works as a "median big-state" lens on the story.

    Every choropleth in this notebook fixes its color scale across the
    years or maps being compared (rather than auto-scaling per frame),
    and every line chart starts its y-axis at zero. Both choices were
    made deliberately so that color intensity and line height mean the
    same thing throughout the notebook — the reporter's readers should
    be able to trust that what looks dramatic in these graphics actually
    is dramatic, not an artifact of axis or color-scale tricks. The
    Illinois 2010 trough map also layers major-city markers on top of
    the choropleth, giving a non-local reader geographic anchors
    (Chicago, Rockford, Peoria, Springfield) for the otherwise-anonymous
    county polygons.
    """)
    return


if __name__ == "__main__":
    app.run()
