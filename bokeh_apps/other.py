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


def callback(attr, old, new):
    user_inputs["change_marine_port"] = change_marine_port_slider.value
    user_inputs["mp_energy_elec_motion"] = mp_energy_elec_motion_slider.value
    user_inputs["change_off_road"] = change_off_road_slider.value
    user_inputs["or_energy_elec_motion"] = or_energy_elec_motion_slider.value
    bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
    stacked_chart_positive_source.data = wrangle_pos_data_for_stacked_chart(user_inputs)
    stacked_chart_negative_source.data = wrangle_neg_data_for_stacked_chart(user_inputs)


# marine and port
change_marine_port_slider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Marine and Port-related Activity"
)
change_marine_port_slider.on_change("value", callback)

mp_energy_elec_motion_slider = Slider(
    start=0,
    end=100,
    value=MP_ENERGY_ELEC_MOTION,
    step=1,
    title="% Electrification of Marine and Port-related Activity",
)
mp_energy_elec_motion_slider.on_change("value", callback)

# off-road
change_off_road_slider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Offroad Vehicle Use"
)
change_off_road_slider.on_change("value", callback)

or_energy_elec_motion_slider = Slider(
    start=0,
    end=100,
    value=OR_ENERGY_ELEC_MOTION,
    step=1,
    title="% Electrification of Offroad vehicles",
)
or_energy_elec_motion_slider.on_change("value", callback)

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
    change_marine_port_slider,
    mp_energy_elec_motion_slider,
    change_off_road_slider,
    or_energy_elec_motion_slider,
)

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