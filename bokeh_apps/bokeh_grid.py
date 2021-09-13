from bokeh.models import Slider, Column, ColumnDataSource, TextInput, Paragraph
from bokeh.layouts import row, layout, column
from bokeh.plotting import curdoc
from bokeh.themes import Theme

from ghg_calc import (
    wrangle_data_for_bar_chart,
    wrangle_data_for_stacked_chart,
    wrangle_pos_data_for_stacked_chart,
    wrangle_neg_data_for_stacked_chart,
    wrangle_data_for_pie_chart,
    create_bar_chart,
    create_stacked_chart,
    create_pie_chart,
    user_inputs,
    URBAN_POP_PERCENT,
    SUBURBAN_POP_PERCENT,
    RURAL_POP_PERCENT,
    GRID_COAL,
    GRID_OIL,
    GRID_NG,
    GRID_NUCLEAR,
    GRID_SOLAR,
    GRID_WIND,
    GRID_BIO,
    GRID_HYDRO,
    GRID_GEO,
    GRID_OTHER_FF,
    URB_ELEC_OTHER_BTU,
    URB_ENERGY_BTU,
    URB_ENERGY_ELEC,
    SUB_ELEC_OTHER_BTU,
    SUB_ENERGY_BTU,
    SUB_ENERGY_ELEC,
    RUR_ELEC_OTHER_BTU,
    RUR_ENERGY_BTU,
    RUR_ENERGY_ELEC,
    CI_ENERGY_ELEC,
    REG_FLEET_MPG,
    RT_ENERGY_ELEC_MOTION,
    F_ENERGY_ELEC_MOTION,
    ICR_ENERGY_ELEC_MOTION,
    MP_ENERGY_ELEC_MOTION,
    OR_ENERGY_ELEC_MOTION,
)


def generate_text_and_style(user_inputs):
    """Generate text and style for creating/updating grid mix Paragraph widget."""
    total = round(
        sum(
            [
                user_inputs["grid_coal"],
                user_inputs["grid_oil"],
                user_inputs["grid_ng"],
                user_inputs["grid_nuclear"],
                user_inputs["grid_solar"],
                user_inputs["grid_wind"],
                user_inputs["grid_bio"],
                user_inputs["grid_hydro"],
                user_inputs["grid_geo"],
                user_inputs["grid_other_ff"],
            ]
        ),
        1,
    )

    text = f"Input percentages. Make sure the grid mix sums to 100%. The current sum is {total}%."
    if total > 100:
        style = {"color": "red"}
    elif total < 100:
        style = {"color": "orange"}
    else:
        style = {"color": "black"}
    return text, style


def callback(attr, old, new):
    user_inputs["grid_coal"] = float(grid_coal_input.value)
    user_inputs["grid_oil"] = float(grid_oil_input.value)
    user_inputs["grid_ng"] = float(grid_ng_input.value)
    user_inputs["grid_nuclear"] = float(grid_nuclear_input.value)
    user_inputs["grid_solar"] = float(grid_solar_input.value)
    user_inputs["grid_wind"] = float(grid_wind_input.value)
    user_inputs["grid_bio"] = float(grid_bio_input.value)
    user_inputs["grid_hydro"] = float(grid_hydro_input.value)
    user_inputs["grid_geo"] = float(grid_geo_input.value)
    user_inputs["grid_other_ff"] = float(grid_other_ff_input.value)
    bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
    stacked_chart_positive_source.data = wrangle_pos_data_for_stacked_chart(user_inputs)
    stacked_chart_negative_source.data = wrangle_neg_data_for_stacked_chart(user_inputs)
    pie_chart_source.data = wrangle_data_for_pie_chart(user_inputs)
    grid_text.text, grid_text.style = generate_text_and_style(user_inputs)


# electric grid mix
text, style = generate_text_and_style(user_inputs)
grid_text = Paragraph(text=text, style=style)

grid_coal_input = TextInput(value=str(round(GRID_COAL, 1)), title="% Coal")
grid_coal_input.on_change("value", callback)

grid_oil_input = TextInput(value=str(round(GRID_OIL, 1)), title="% Oil")
grid_oil_input.on_change("value", callback)

grid_ng_input = TextInput(value=str(round(GRID_NG, 1)), title="% Natural")
grid_ng_input.on_change("value", callback)

grid_nuclear_input = TextInput(value=str(round(GRID_NUCLEAR, 1)), title="% Nuclear")
grid_nuclear_input.on_change("value", callback)

grid_solar_input = TextInput(value=str(round(GRID_SOLAR, 1)), title="% Solar")
grid_solar_input.on_change("value", callback)

grid_wind_input = TextInput(value=str(round(GRID_WIND, 1)), title="% Wind")
grid_wind_input.on_change("value", callback)

grid_bio_input = TextInput(value=str(round(GRID_BIO, 1)), title="% Biomass")
grid_bio_input.on_change("value", callback)

grid_hydro_input = TextInput(value=str(round(GRID_HYDRO, 1)), title="% Hydropower")
grid_hydro_input.on_change("value", callback)

grid_geo_input = TextInput(value=str(round(GRID_GEO, 1)), title="% Geothermal")
grid_geo_input.on_change("value", callback)

grid_other_ff_input = TextInput(value=str(round(GRID_OTHER_FF, 1)), title="% Other Fossil Fuel")
grid_other_ff_input.on_change("value", callback)

inputs = Column(
    grid_text,
    grid_coal_input,
    grid_oil_input,
    grid_ng_input,
    grid_nuclear_input,
    grid_solar_input,
    grid_wind_input,
    grid_bio_input,
    grid_hydro_input,
    grid_geo_input,
    grid_other_ff_input,
    width=200,
)
bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
bar_chart_source = ColumnDataSource(data=bar_chart_data)
bar_chart = create_bar_chart(bar_chart_data, bar_chart_source)

stacked_chart_positive_data = wrangle_pos_data_for_stacked_chart(user_inputs)
stacked_chart_negative_data = wrangle_neg_data_for_stacked_chart(user_inputs)
stacked_chart_positive_source = ColumnDataSource(data=stacked_chart_positive_data)
stacked_chart_negative_source = ColumnDataSource(data=stacked_chart_negative_data)
stacked_chart = create_stacked_chart(
    stacked_chart_positive_data,
    stacked_chart_negative_data,
    stacked_chart_positive_source,
    stacked_chart_negative_source,
)

pie_chart_data = wrangle_data_for_pie_chart(user_inputs)
pie_chart_source = ColumnDataSource(data=pie_chart_data)
pie_chart = create_pie_chart(pie_chart_source)

# layout of charts
bar_chart.margin = (0, 0, 15, 0)
stacked_chart.margin = (0, 0, 15, 0)

charts = column(
    bar_chart,
    stacked_chart,
    pie_chart,
    sizing_mode="stretch_width",
    margin=(0, 15, 0, 15),
)
# doc.theme = Theme(filename="main/static/main/ghg_bokeh_theme.yaml")
curdoc().add_root(layout([[inputs, charts]], css_classes=["center"]))
