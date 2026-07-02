"""
CS-11: Interacting with Space
The Church's Center of Gravity Has Moved to Africa

A folium recreation of the LDS growth story we built in the CS-10-style
series. Strict Polars + folium stack inside Marimo. Task 19 layering
pattern translated: continuous choropleth base, discrete point overlays
on top, interactive throughout. Operating-temple popups embed temple
photos when available in the local image cache.

Inputs (drop into ../data/raw/):
  - lds_by_country_2015_vs_2025.json     159-country paired snapshot
  - lds_temples.json                     340 temples with GPS + status
  - lds_temple_images.json   (optional)  {slug: og_image_url}, built by
                                         build_temple_images.py

Export:
  marimo export html cs11_lds_folium.py -o cs11_lds_folium.html
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # The Church's Center of Gravity Has Moved to Africa
        *CS-11 — Interacting with Space (folium recreation of the LDS growth brief)*

        Between 2015 and 2025, the geography of Latter-day Saint membership growth
        decoupled from its 20th-century base. Worldwide membership grew 14% over
        the decade — but that average hides the real story. North American
        membership grew at a low single-digit rate and Russia, Ukraine and
        Kazakhstan posted outright declines. Meanwhile sub-Saharan Africa
        delivered the highest growth rates in the global Church for the decade:
        Rwanda **+954%**, Angola **+360%**, Mozambique **+358%**, the
        Democratic Republic of the Congo **+233%**, Nigeria **+93%**.

        The temple programme has followed. Of 122 temples announced or under
        construction at the close of 2025, a disproportionate share sits in
        Africa, Latin America and the Pacific. Hover any country for its
        decade-over-decade numbers, click any operating temple for its photo
        and city, and use the layer control to toggle between operating,
        under-construction and announced temples to see where the Church has
        put physical infrastructure behind the growth.
        """
    )
    return


@app.cell
def _():
    import polars as pl
    import folium
    from branca.colormap import StepColormap
    import json
    import unicodedata
    import re
    import urllib.request
    from pathlib import Path
    return Path, StepColormap, folium, json, pl, re, unicodedata, urllib


@app.cell
def _(pl):
    # LDS country panel — paired 2015/2025 snapshot
    members = pl.read_json("../../data/raw/lds_by_country_2015_vs_2025.json")
    members
    return (members,)


@app.cell
def _(pl):
    # Temple locations + status from churchofjesuschristtemples.org
    temples = pl.read_json("../../data/raw/lds_temples.json")
    temples
    return (temples,)


@app.cell
def _(Path, json):
    # Optional image cache — built by build_temple_images.py running locally.
    # Notebook degrades gracefully to text-only popups if the file is absent
    # or sparse.
    _img_path = Path("../../data/raw/lds_temple_images.json")
    if _img_path.exists():
        temple_images = json.loads(_img_path.read_text())
    else:
        temple_images = {}
    f"Temple image cache: {len(temple_images)} entries"
    return (temple_images,)


@app.cell
def _(json, urllib):
    # Natural Earth 1:50m country boundaries — substantially more complete
    # than folium's reference GeoJSON. 242 features vs 177, capturing
    # Cabo Verde, eSwatini, Cook Islands, Tonga, Antigua, Aruba, Bahamas,
    # Iceland, Kiribati, Malta, Mauritius, Samoa, Singapore and other
    # island and micro-states that the simplified file omits.
    _ne_url = (
        "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
        "master/geojson/ne_50m_admin_0_countries.geojson"
    )
    with urllib.request.urlopen(_ne_url) as _resp:
        world = json.loads(_resp.read())
    f"Loaded {len(world['features'])} country features from Natural Earth 1:50m"
    return (world,)


@app.cell
def _(members, world):
    # Merge LDS panel into each Natural Earth feature's ADMIN property so
    # folium's tooltip and style_function can read them. Aliases verified
    # against Natural Earth's actual ADMIN values.
    name_aliases = {
        "United States": "United States of America",
        "Tanzania": "United Republic of Tanzania",
        "Bahamas": "The Bahamas",
        "Czech Republic": "Czechia",
        "Cape Verde": "Cabo Verde",
        "Eswatini": "eSwatini",
        "Curacao": "Curaçao",
        "Timor-Leste": "East Timor",
        "Serbia": "Republic of Serbia",
    }

    growth_map = {
        name_aliases.get(r["country"], r["country"]): r
        for r in members.to_dicts()
    }

    _matched = 0
    for feature in world["features"]:
        # Natural Earth puts the country name in ADMIN, with NAME as the
        # short-form fallback. Try ADMIN first, then NAME.
        _gname = feature["properties"].get(
            "ADMIN") or feature["properties"].get("NAME", "")
        _row = growth_map.get(_gname)
        if _row is not None:
            feature["properties"]["members_2015"] = _row["members_2015"]
            feature["properties"]["members_2025"] = _row["members_2025"]
            feature["properties"]["growth_pct"] = _row["growth_pct_10yr"]
            _matched += 1
        else:
            feature["properties"]["members_2015"] = None
            feature["properties"]["members_2025"] = None
            feature["properties"]["growth_pct"] = None

    f"Joined LDS data into {_matched} of {len(world['features'])} country features"
    return


@app.cell
def _(StepColormap):
    # Diverging step palette anchored at zero. Manual thresholds keep the
    # Russian/Ukrainian decline visible in red, mature LDS markets at the
    # cream centre, and the African surge in the deep greens — a linear
    # scale would let Rwanda's +954% flatten everything else.
    colormap = StepColormap(
        colors=[
            "#a50026", "#d73027", "#fdae61", "#f7f7f7",
            "#a6d96a", "#1a9850", "#006837",
        ],
        index=[-50, -10, 0, 25, 100, 300, 1000, 2000],
        vmin=-50, vmax=2000,
        caption="10-Year LDS Membership Growth (%)  ·  2015 → 2025",
    )
    colormap
    return (colormap,)


@app.cell
def _(re, unicodedata):
    # Slug derivation must match the one in build_temple_images.py so the
    # image-cache lookup keys line up.
    def slugify(temple_name: str) -> str:
        nfkd = unicodedata.normalize("NFKD", temple_name)
        ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
        return re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return (slugify,)


@app.cell
def _(colormap, folium, slugify, temple_images, temples, world):
    # ====================================================================
    # The Main Map
    # --------------------------------------------------------------------
    # Task 19 layering pattern in folium:
    #   base    = choropleth via GeoJson + style_function
    #   points  = three FeatureGroups, one per temple status,
    #             independently toggleable from the LayerControl
    # ====================================================================

    def _country_style(feature):
        g = feature["properties"].get("growth_pct")
        if g is None:
            return {"fillColor": "#e8e8e8", "color": "#fff", "weight": 0.4, "fillOpacity": 0.55}
        return {"fillColor": colormap(g), "color": "#fff", "weight": 0.5, "fillOpacity": 0.88}

    def _country_highlight(_f):
        return {"weight": 2.5, "color": "#222", "fillOpacity": 0.95}

    m = folium.Map(
        location=[10, 15], zoom_start=2,
        tiles="cartodbpositron", world_copy_jump=True,
    )

    # Use ADMIN as the tooltip label since that's what Natural Earth uses
    # for the canonical country name.
    folium.GeoJson(
        world,
        name="Membership growth, 2015–2025",
        style_function=_country_style,
        highlight_function=_country_highlight,
        tooltip=folium.GeoJsonTooltip(
            fields=["ADMIN", "members_2015", "members_2025", "growth_pct"],
            aliases=["Country:", "2015 members:",
                     "2025 members:", "10-yr growth (%):"],
            localize=True, sticky=False, labels=True,
            style=(
                "background-color: white; color: #2c2c2c;"
                " font-family: -apple-system, sans-serif; font-size: 12px;"
                " padding: 8px 10px; border-radius: 4px;"
                " box-shadow: 0 2px 8px rgba(0,0,0,0.15);"
            ),
        ),
    ).add_to(m)

    # Temple overlays — three layers, styled to encode status structurally
    TEMPLE_BROWN = "#8B5A3C"
    style_by_status = {
        "Dedicated":          dict(radius=4.5, fill=True,  fill_opacity=0.92, opacity=1.0, weight=1.2),
        "Under Construction": dict(radius=4.0, fill=True,  fill_opacity=0.45, opacity=1.0, weight=1.2),
        "Announced":          dict(radius=3.5, fill=False, fill_opacity=0.0,  opacity=0.85, weight=1.6),
    }
    layer_labels = {
        "Dedicated":          "Operating temples (end-2025)",
        "Under Construction": "Under construction",
        "Announced":          "Announced (planned)",
    }

    def _build_popup_html(t, status, img_url):
        """HTML popup body — embed photo when cache has it, else text-only."""
        if img_url:
            img_block = (
                f'<img src="{img_url}" width="240" '
                f'style="display:block;margin:0 auto 8px;border-radius:3px;'
                f'box-shadow:0 1px 4px rgba(0,0,0,0.2);" '
                f'alt="{t["name"]}" />'
            )
        else:
            img_block = ""
        location = f"{t['city']}, {t['country']}" if t.get(
            "city") else t["country"]
        return (
            f'<div style="font-family:-apple-system,sans-serif;width:240px;">'
            f'{img_block}'
            f'<div style="font-weight:600;font-size:13px;color:#2c2c2c;'
            f'margin-bottom:2px;">{t["name"]}</div>'
            f'<div style="color:#666;font-size:11px;">{location}</div>'
            f'<div style="color:#888;font-size:10px;font-style:italic;'
            f'margin-top:4px;">{status}</div>'
            f'</div>'
        )

    for status, label in layer_labels.items():
        group = folium.FeatureGroup(name=label, show=(status == "Dedicated"))
        st = style_by_status[status]
        subset = temples.filter(temples["status"] == status).to_dicts()
        for t in subset:
            # Only Dedicated temples get image popups (the cache only covers
            # operating temples by design).
            img_url = temple_images.get(
                slugify(t["name"])) if status == "Dedicated" else None
            popup_html = _build_popup_html(t, status, img_url)
            folium.CircleMarker(
                location=[t["lat"], t["lon"]],
                radius=st["radius"],
                popup=folium.Popup(popup_html, max_width=280),
                color=TEMPLE_BROWN,
                weight=st["weight"],
                opacity=st["opacity"],
                fill=st["fill"],
                fill_color=TEMPLE_BROWN,
                fill_opacity=st["fill_opacity"],
            ).add_to(group)
        group.add_to(m)

    colormap.add_to(m)
    folium.LayerControl(collapsed=False, position="topright").add_to(m)
    m
    return (m,)


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Design choices

        **Folium replaces Plotly to make the African story legible at every
        zoom level.** Plotly's `scatter_geo` renders the temple overlay as a
        static image; at a global zoom the sub-Saharan growth cluster reads
        as a single green band and the half-dozen DRC and Nigerian temples
        pile on top of each other. Folium produces a true Leaflet slippy
        map, so the reader can drill from global view down to neighbourhood
        scale and click any operating temple for its photo, name and city.
        The choropleth uses `folium.GeoJson` with a custom `style_function`
        rather than the simpler `folium.Choropleth` — that gave full control
        over the colormap (a diverging seven-step `StepColormap` anchored at
        zero) and let me attach a rich `GeoJsonTooltip` showing both the 2015
        and 2025 membership figures, so magnitude *and* rate of change are
        visible on hover.

        **The temple layer encodes status structurally, not by colour
        alone.** Operating temples are full-opacity filled circles with
        embedded photos in their popups; under-construction temples are
        half-filled at the same hue; announced temples are hollow rings. All
        three share the same temple-stone brown and live in independent
        `FeatureGroup`s, toggleable from the `LayerControl`. The default
        view shows only operating temples — the *now* state — and turning
        on the under-construction and announced layers reveals where the
        Church is committing infrastructure next. Read together, the
        choropleth answers "where did growth happen" and the layered temple
        overlay answers "where does the Church believe growth will continue."

        **A note on the grey countries.** Grey is honest about three
        different gaps: countries with no recognised Church presence
        (Saudi Arabia, Iran, Afghanistan), countries where the Church
        operates but does not publish membership figures (China, Belarus,
        Lebanon), and a small residual of countries whose names couldn't be
        matched to the Natural Earth 1:50m boundaries file (a handful of
        territories like Bonaire and the Northern Mariana Islands). The
        first two are substantive absences; the third is a data-join
        artefact. Switching from folium's reference GeoJSON to Natural
        Earth 1:50m raised the matched-country count from 118 to 153 of 159,
        eliminating earlier visible gaps for Cabo Verde, eSwatini, Cook
        Islands, Tonga and Iceland.
        """
    )
    return


if __name__ == "__main__":
    app.run()
