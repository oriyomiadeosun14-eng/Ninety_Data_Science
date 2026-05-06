import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Critiquing Visualizations 📊

    ### Oriyomi Adeosun ###
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Case Study 1: The Happy Map
    **Question:** *How does where you live affect your happiness?*

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ![Happy Map](Happy_map.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visual Critique: The Happy Map
    Why the map works:
    - To give a general "vibe" or feeling of the city
    - To show the distribution of happiness across different cities

    Why the map doesn't work:
    - It encodes the data using Color Hue/Saturation, which is at the bottom of Rauser's accuracy hierarchy.
    - The map does not include a legend, so it's unclear what the colors represent in terms of happiness levels.

    Summary:

    The Happy Map communicates the Gestalt *the big picture* very well through grouping and color, but it fails to move up the Accuracy Hierarchy because it lacks a common scale for precise comparison.

       ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Case Study 2: Price of lithium-ion battery cells overtime
    **Question:** *How does time impact the price of lithium-ion battery cells?*

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ![Battery Price Chart Overtime](the-price-of-lithium-ion-batteries-has-fallen-by-99-since-1991.svg)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visual Critique: Price of lithium-ion battery cells overtime
    Why the chart works:

    - The primary chart type is a Line Chart. According to Rauser's hierarchy, this is the most accurate way to show data because it uses Position on a Common Scale. Our eyes are excellent at detecting the upward or downward slope of a line.     - It uses a line chart, which is appropriate for showing trends over time.
    - The use of a Logarithmic Scale is a strategic design choice that moves the data up the Accuracy Hierarchy. It allows for the precise estimation of percentage decreases across 30 years, ensuring that recent price improvements remain as visible as early historical drops

    Something that was compromised:

    - The use of a logarithmic scale can be less intuitive for some viewers, especially those who are not familiar with it. This may make it harder for some people to interpret the exact values or the rate of change without additional context or explanation. Although this helps the chart move up the Accuracy Hierarchy, it may reduce accessibility for a general audience.
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Case Study 3: GPU's Inflation Report
    **Question:** *How Much Did Cryptocurrency Mining Inflate GPU Prices?*

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ![GPU Price Chart Overtime](GPU_price_chart.png)
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visual Critique: GPU's Inflation Report
    Why the chart works:
    - The chart uses a Line Chart, which is the most accurate way to show data according to Rauser's hierarchy. It allows for precise comparison of GPU prices over time.
    - By having that solid line at $1,499, your eye can instantly perform Position on a Common Scale comparison. You can clearly see that almost every single dot is "higher" than the MSRP. It makes the "inflation" salient and undeniable.

    Why the chart desn't work:
    - The chart double axis is a common design choice that can be misleading.
    - Rauser explains that our primary job isn't to make a "pretty" picture or a complex graphic; it is to make the actual data points detectable and transparent.
    - The chart is cluttered. It has too many data points and the double y-axis can be confusing for viewers. This can make it difficult to identify trends or patterns in the data, and may lead to misinterpretation.
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The human cost of unsafe abortion
    **Question:** *What was the mortality rate associated to abortion ?*

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ![Unsafe Abortion Chart](Unsafe_abortion_chart.svg)
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visual Critique: The human cost of unsafe abortion
    Why the chart works:
    - This is a very simple and minimalistic bar chart that uses Position on a Common Scale, which is the most accurate way to show data according to Rauser's hierarchy. It allows for precise comparison of mortality rates across different regions.
    - By making Romania red while all other countries are blue, the designer creates immediate "Salience."
    - The simple design makes it less complicated, thus making the human brain to struggle less to process the information. The chart is easy to read and understand, which can help to effectively communicate the message about the mortality rate associated with unsafe abortion.
    ---
    """)
    return


if __name__ == "__main__":
    app.run()
