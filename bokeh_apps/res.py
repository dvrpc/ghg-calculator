from bokeh.layouts import row, layout, column
from bokeh.models import Slider, Column, ColumnDataSource
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


def callback(attr, old, new):
    user_inputs["res_energy_change"] = res_energy_change_slider.value
    user_inputs["urb_energy_elec"] = urb_energy_elec_slider.value
    user_inputs["sub_energy_elec"] = sub_energy_elec_slider.value
    user_inputs["rur_energy_elec"] = rur_energy_elec_slider.value
    bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
    stacked_chart_positive_source.data = wrangle_pos_data_for_stacked_chart(user_inputs)
    stacked_chart_negative_source.data = wrangle_neg_data_for_stacked_chart(user_inputs)


# residential
res_energy_change_slider = Slider(
    start=-100,
    end=100,
    value=0,
    step=10,
    title="% Change in Per Capita Residential Energy Usage",
)
res_energy_change_slider.on_change("value", callback)
urb_energy_elec_slider = Slider(
    start=URB_ELEC_OTHER_BTU / URB_ENERGY_BTU * 100,
    end=100,
    value=URB_ENERGY_ELEC * 100,
    step=1,
    title="% Electrification of Residential End Uses in Urban Areas",
)
urb_energy_elec_slider.on_change("value", callback)

sub_energy_elec_slider = Slider(
    start=SUB_ELEC_OTHER_BTU / SUB_ENERGY_BTU * 100,
    end=100,
    value=SUB_ENERGY_ELEC * 100,
    step=1,
    title="% Electrification of Residential End Uses in Suburban Areas",
)
sub_energy_elec_slider.on_change("value", callback)

rur_energy_elec_slider = Slider(
    start=RUR_ELEC_OTHER_BTU / RUR_ENERGY_BTU * 100,
    end=100,
    value=RUR_ENERGY_ELEC * 100,
    step=1,
    title="% Electrification of Residential End Uses in Rural Areas",
)
rur_energy_elec_slider.on_change("value", callback)

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

inputs = Column(
    res_energy_change_slider,
    urb_energy_elec_slider,
    sub_energy_elec_slider,
    rur_energy_elec_slider,
)
# @HERE
# charts = row(bar_chart, inputs, stacked_chart, sizing_mode="stretch_both")
# doc.add_root(layout([[charts]]))

# layout of charts
bar_chart.margin = (0, 0, 15, 0)
stacked_chart.margin = (0, 0, 15, 0)

charts = column(
    bar_chart,
    stacked_chart,
    sizing_mode="stretch_width",
    margin=(0, 15, 0, 15),
)
# doc.theme = Theme(filename="main/static/main/ghg_bokeh_theme.yaml")
curdoc().add_root(layout([[inputs, charts]], css_classes=["center"]))
