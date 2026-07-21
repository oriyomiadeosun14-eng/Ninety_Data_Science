import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import pandas as pd
    import folium
    import branca.colormap as cm
    from branca.element import IFrame
    import requests
    import pycountry
    import lets_plot as lp

    lp.LetsPlot.setup_html()
    return IFrame, cm, folium, lp, mo, pd, pl, pycountry, requests


@app.cell
def _(mo):
    mo.md("""
    # Global Safety Analysis

    **Project owner: Oriyomi King Adeosun**

    Three questions, one dataset (Global Peace Index via QoG, 161 countries,
    2008–2025):

    1. Which countries are safest?
    2. Why is a country safe or unsafe?
    3. Which countries are least safe?

    The composite score `gpi_gpi` (1 = safest, 5 = least safe) is made of
    three sub-domains: **Ongoing Conflict** (`gpi_conf`), **Safety &
    Security** (`gpi_ss`), and **Militarization** (`gpi_mil`).
    """)
    return


@app.cell
def _(pl):
    df = pl.read_csv("../../data/raw/gpi_merged_wide.csv")

    return (df,)


@app.cell
def _(df, mo):
    year_dropdown = mo.ui.dropdown(
        options=[str(y) for y in sorted(df["year"].unique().to_list())],
        value="2025",
        label="Year",
    )
    year_dropdown
    return (year_dropdown,)


@app.cell
def _(df, pl, year_dropdown):
    selected_year = int(year_dropdown.value)
    # Add rank once, reuse everywhere. Ascending sort = safest first.
    year_df = (
        df.filter(pl.col("year") == selected_year)
        .sort("gpi_gpi")
        .with_row_index("rank", offset=1)
    )
    return selected_year, year_df


@app.cell
def _(mo):
    mo.md("""
    ## Q1 — Safest countries
    """)
    return


@app.cell
def _(year_df):
    safest = year_df.select(
        ["rank", "cname", "gpi_gpi", "gpi_conf", "gpi_ss", "gpi_mil"]
    )

    return (safest,)


@app.cell
def _(lp, safest):
    top15 = safest.head(15).to_pandas()

    p1 = (
        lp.ggplot(top15, lp.aes(x="cname", y="gpi_gpi"))
        + lp.geom_bar(stat="identity", fill="#2E86AB")
        + lp.coord_flip()
        + lp.scale_x_discrete(limits=top15["cname"].tolist()[::-1])
        + lp.labs(
            title="Top 15 safest countries (lower = safer)",
            x="",
            y="GPI score",
        )
        + lp.theme_minimal()
    )
    p1
    return


@app.cell
def _(mo):
    mo.md("""
    ## Q2 — Why is a country safe or unsafe?
    """)
    return


@app.cell
def _(df, mo):
    country_dropdown = mo.ui.dropdown(
        options=sorted(df["cname"].unique().to_list()),
        value="Nigeria",
        label="Country",
    )
    country_dropdown
    return (country_dropdown,)


@app.cell
def _(country_dropdown, mo, pl, year_df):
    # Country row (already has rank from year_df).
    country_row = year_df.filter(pl.col("cname") == country_dropdown.value)
    country_name = country_row["cname"][0]
    country_rank = country_row["rank"][0]
    total_countries = year_df.height

    # Global averages for the three sub-domains.
    domains = ["gpi_conf", "gpi_ss", "gpi_mil"]
    labels = {
        "gpi_conf": "Ongoing Conflict",
        "gpi_ss": "Safety & Security",
        "gpi_mil": "Militarization",
    }
    global_avg = year_df.select([pl.col(d).mean() for d in domains]).row(0)
    country_vals = country_row.select(domains).row(0)

    # Deltas: country minus global. Positive = worse than average (drives
    # the score up), negative = better.
    deltas = [(labels[d], c - g) for d, c, g in zip(domains, country_vals, global_avg)]
    biggest_driver = max(deltas, key=lambda x: x[1])
    biggest_strength = min(deltas, key=lambda x: x[1])

    direction = (
        "less safe" if country_row["gpi_gpi"][0] > year_df["gpi_gpi"].mean() else "safer"
    )

    mo.md(f"""
    **{country_name}** ranks **#{country_rank} of {total_countries}** —
    {direction} than the global average.

    - Biggest thing pulling the score **up** (worse):
      **{biggest_driver[0]}**, {biggest_driver[1]:+.2f} vs global average.
    - Biggest thing pulling the score **down** (better):
      **{biggest_strength[0]}**, {biggest_strength[1]:+.2f} vs global average.
    """)
    return country_name, country_row


@app.cell
def _(country_name, country_row, lp, pd, pl, year_df):
    # Recomputing locally with distinct names so Marimo's one-definition-
    # per-variable rule is satisfied.
    plot_labels = ["Ongoing Conflict", "Safety & Security", "Militarization"]
    plot_cols = ["gpi_conf", "gpi_ss", "gpi_mil"]

    plot_country_vals = country_row.select(plot_cols).row(0)
    plot_global_avg = year_df.select([pl.col(d).mean() for d in plot_cols]).row(0)

    breakdown = pd.DataFrame(
        {
            "Domain": plot_labels * 2,
            "Score": list(plot_country_vals) + list(plot_global_avg),
            "Group": [country_name] * 3 + ["Global average"] * 3,
        }
    )

    p2 = (
        lp.ggplot(breakdown, lp.aes(x="Domain", y="Score", fill="Group"))
        + lp.geom_bar(stat="identity", position="dodge")
        + lp.labs(
            title=f"{country_name} vs global average, by sub-domain",
            y="Score (1 = best, 5 = worst)",
            x="",
        )
        + lp.theme_minimal()
    )
    p2
    return


@app.cell
def _(mo):
    mo.md("""
    ## Q3 — Least safe countries
    """)
    return


@app.cell
def _(safest):
    least_safe = safest.sort("gpi_gpi", descending=True).head(15)

    return (least_safe,)


@app.cell
def _(least_safe, lp):
    bottom15 = least_safe.to_pandas()

    p3 = (
        lp.ggplot(bottom15, lp.aes(x="cname", y="gpi_gpi"))
        + lp.geom_bar(stat="identity", fill="#C1272D")
        + lp.coord_flip()
        + lp.scale_x_discrete(limits=bottom15["cname"].tolist()[::-1])
        + lp.labs(
            title="15 least safe countries (higher = less safe)",
            x="",
            y="GPI score",
        )
        + lp.theme_minimal()
    )
    p3
    return


@app.cell
def _(mo):
    mo.md("""
    ## World map — interactive

    Hover any country for a quick label (name, rank, GPI score). Click for a
    richer card: flag, biggest driver of insecurity, and the country's GPI
    trend from 2008 to the selected year.
    """)
    return


@app.cell
def _(df, pl, pycountry, year_df):
    # Precompute everything the map needs, keyed by ISO alpha-3.
    # All top-level names prefixed `mi_` so Marimo doesn't clash with Q2.
    mi_domains = ["gpi_conf", "gpi_ss", "gpi_mil"]
    mi_domain_names = {
        "gpi_conf": "Ongoing Conflict",
        "gpi_ss": "Safety & Security",
        "gpi_mil": "Militarization",
    }
    mi_global_avg = dict(
        zip(mi_domains, year_df.select([pl.col(d).mean() for d in mi_domains]).row(0))
    )

    def alpha3_to_alpha2(a3):
        try:
            c = pycountry.countries.get(alpha_3=a3)
            return c.alpha_2.lower() if c else None
        except Exception:
            return None

    def sparkline_svg(pairs, width=210, height=52, y_min=1.0, y_max=5.0):
        pairs = [(y, v) for y, v in pairs if v is not None]
        if len(pairs) < 2:
            return ""
        vals = [v for _, v in pairs]
        n = len(vals)
        pad_l, pad_r, pad_t, pad_b = 22, 8, 8, 14
        iw, ih = width - pad_l - pad_r, height - pad_t - pad_b
        xs = [pad_l + i * iw / (n - 1) for i in range(n)]
        ys = [pad_t + (v - y_min) / (y_max - y_min) * ih for v in vals]
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
        last = vals[-1]
        color = "#2E86AB" if last < 2 else "#F4A261" if last < 3 else "#C1272D"
        y0, y1 = pairs[0][0], pairs[-1][0]
        return (
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
            f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{height-pad_b}" '
            f'stroke="#ccc" stroke-width="0.5"/>'
            f'<line x1="{pad_l}" y1="{height-pad_b}" x2="{width-pad_r}" '
            f'y2="{height-pad_b}" stroke="#ccc" stroke-width="0.5"/>'
            f'<text x="4" y="{pad_t+4}" font-size="8" fill="#888">5</text>'
            f'<text x="4" y="{height-pad_b}" font-size="8" fill="#888">1</text>'
            f'<text x="{pad_l}" y="{height-3}" font-size="8" fill="#888">{y0}</text>'
            f'<text x="{width-pad_r-24}" y="{height-3}" font-size="8" fill="#888">{y1}</text>'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5"/>'
            f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="2.5" fill="{color}"/>'
            f"</svg>"
        )

    # Group history once so we don't re-filter per country.
    # Polars group_by yields the key as a tuple, hence the (name,) unpack.
    mi_history = {
        name: list(zip(g["year"].to_list(), g["gpi_gpi"].to_list()))
        for (name,), g in df.sort("year").group_by("cname", maintain_order=True)
    }

    country_info = {}
    for mi_row in year_df.iter_rows(named=True):
        mi_a3 = mi_row["ccodealp"]
        mi_deltas = [
            (mi_domain_names[d], mi_row[d] - mi_global_avg[d]) for d in mi_domains
        ]
        mi_cause = max(mi_deltas, key=lambda x: x[1])
        mi_strength = min(mi_deltas, key=lambda x: x[1])

        country_info[mi_a3] = {
            "cname": mi_row["cname"],
            "rank": mi_row["rank"],
            "score": mi_row["gpi_gpi"],
            "alpha2": alpha3_to_alpha2(mi_a3),
            "cause_name": mi_cause[0],
            "cause_delta": mi_cause[1],
            "strength_name": mi_strength[0],
            "strength_delta": mi_strength[1],
            "sparkline": sparkline_svg(mi_history.get(mi_row["cname"], [])),
        }
    return (country_info,)


@app.cell
def _(IFrame, cm, country_info, folium, requests, selected_year):
    n_countries = len(country_info)
    world_map = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodbpositron")

    geo_url = (
        "https://raw.githubusercontent.com/python-visualization/folium/"
        "master/examples/data/world-countries.json"
    )
    geo_data = requests.get(geo_url).json()

    # Green (safe) → red (unsafe), matching RdYlGn_r on a 1–5 scale.
    colormap = cm.LinearColormap(
        colors=["#1a9850", "#66bd63", "#fee08b", "#fdae61", "#d73027"],
        vmin=1.0,
        vmax=5.0,
        caption=f"GPI score, {selected_year} (higher = less safe)",
    )

    def build_popup(info):
        flag_img = (
            f'<img src="https://flagcdn.com/w40/{info["alpha2"]}.png" '
            f'style="width:40px;height:auto;border:1px solid #ccc;">'
            if info["alpha2"]
            else ""
        )
        return f"""
        <div style="font-family:system-ui,sans-serif;width:240px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            {flag_img}
            <div>
              <div style="font-weight:600;font-size:14px;">{info['cname']}</div>
              <div style="color:#666;font-size:11px;">
                Rank #{info['rank']} of {n_countries} &middot; GPI {info['score']:.2f}
              </div>
            </div>
          </div>
          <div style="font-size:12px;margin-bottom:4px;">
            <b>Main driver of insecurity:</b> {info['cause_name']}
            <span style="color:#C1272D;">({info['cause_delta']:+.2f} vs global avg)</span>
          </div>
          <div style="font-size:12px;margin-bottom:8px;">
            <b>Relative strength:</b> {info['strength_name']}
            <span style="color:#1a9850;">({info['strength_delta']:+.2f} vs global avg)</span>
          </div>
          <div style="font-size:11px;color:#666;margin-bottom:2px;">GPI trend 2008–{selected_year}</div>
          {info['sparkline']}
        </div>
        """

    def build_tooltip(info):
        return (
            f'<div style="font-family:system-ui,sans-serif;font-size:12px;">'
            f'<b>{info["cname"]}</b><br>'
            f'Rank #{info["rank"]} &middot; GPI {info["score"]:.2f}'
            f"</div>"
        )

    for feature in geo_data["features"]:
        a3 = feature.get("id")
        info = country_info.get(a3)
        if info is None:
            # No data for this country in the selected year — show grey, no popup.
            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    "fillColor": "#dddddd",
                    "color": "white",
                    "weight": 0.3,
                    "fillOpacity": 0.6,
                },
                tooltip=folium.Tooltip(
                    f'<b>{feature["properties"].get("name", "?")}</b><br>No data'
                ),
            ).add_to(world_map)
            continue

        # Bind the score at loop time so the lambda doesn't close over the last value.
        folium.GeoJson(
            feature,
            style_function=lambda x, s=info["score"]: {
                "fillColor": colormap(s),
                "color": "white",
                "weight": 0.4,
                "fillOpacity": 0.8,
            },
            highlight_function=lambda x: {"weight": 1.5, "color": "#333"},
            tooltip=folium.Tooltip(build_tooltip(info), sticky=True),
            popup=folium.Popup(
                IFrame(html=build_popup(info), width=280, height=210),
                max_width=320,
            ),
        ).add_to(world_map)

    colormap.add_to(world_map)
    world_map
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ### Summary

    - **Q1 & Q3** are two ends of one sorted ranking.
    - **Q2** is answered by comparing a country's three sub-scores to the
      global average — the biggest positive delta is what's making it
      unsafe.

    Data: Global Peace Index via the Quality of Government Institute,
    2008–2025, 161 countries.

    **Project owner: Oriyomi King Adeosun**
    """)
    return


if __name__ == "__main__":
    app.run()
