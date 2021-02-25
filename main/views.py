from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bokeh.models import Slider, Column, ColumnDataSource, TextInput, Paragraph
from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.layouts import row, layout

from bokeh_apps.ghg_calc import (
    wrangle_data_for_bar_chart,
    wrangle_data_for_stacked_chart,
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


def index(request):
    return render(request, "main/base.html")


def pop_dev_patterns_handler(doc: Document) -> None:
    """Phase2 of proof of concept. This works.
    What makes the chart update is the bar_chart_source.data = wrangle... part

    would be nice to eliminate this and just update the user_inputs. Should be able to then
    simplify/condense the create_bar_chart function - use user_input for the input and do the
    data wrangling within it.
    """

    def callback(attr, old, new):
        user_inputs["change_pop"] = pop_slider.value
        user_inputs["urban_pop_percent"] = float(urban_pop_percent_text_input.value)
        user_inputs["suburban_pop_percent"] = float(suburban_pop_percent_text_input.value)
        user_inputs["rural_pop_percent"] = float(rural_pop_percent_text_input.value)
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)

    pop_slider = Slider(start=-100, end=100, value=0, step=10, title="% Change in Population")
    pop_slider.on_change("value", callback)

    urban_pop_percent_text_input = TextInput(
        value=str(round(URBAN_POP_PERCENT, 1)),
        title="% of Population Living in Urban Municipalities",
    )
    urban_pop_percent_text_input.on_change("value", callback)

    suburban_pop_percent_text_input = TextInput(
        value=str(round(SUBURBAN_POP_PERCENT, 1)),
        title="% of Population Living in Suburban Municipalities",
    )
    suburban_pop_percent_text_input.on_change("value", callback)

    rural_pop_percent_text_input = TextInput(
        value=str(round(RURAL_POP_PERCENT, 1)),
        title="% of Population Living in Rural Municipalities",
    )
    rural_pop_percent_text_input.on_change("value", callback)

    bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
    bar_chart_source = ColumnDataSource(data=bar_chart_data)
    bar_chart = create_bar_chart(bar_chart_data, bar_chart_source)

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    inputs = Column(
        pop_slider,
        urban_pop_percent_text_input,
        suburban_pop_percent_text_input,
        rural_pop_percent_text_input,
        sizing_mode="fixed",
        width=150,
    )
    charts = row(bar_chart, inputs, stacked_chart, sizing_mode="stretch_both")
    doc.add_root(layout([[charts]]))


def pop_dev_patterns(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def res_stationary_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["res_energy_change"] = res_energy_change_slider.value
        user_inputs["urb_energy_elec"] = urb_energy_elec_slider.value
        user_inputs["sub_energy_elec"] = sub_energy_elec_slider.value
        user_inputs["rur_energy_elec"] = rur_energy_elec_slider.value
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)

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

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    inputs = Column(
        res_energy_change_slider,
        urb_energy_elec_slider,
        sub_energy_elec_slider,
        rur_energy_elec_slider,
    )
    # @HERE
    charts = row(bar_chart, inputs, stacked_chart, sizing_mode="stretch_both")
    doc.add_root(layout([[charts]]))


def res_stationary(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def non_res_stationary_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["ci_energy_change"] = ci_energy_change_slider.value
        user_inputs["ci_energy_elec"] = ci_energy_elec_slider.value
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)

    # commercial and industrial
    ci_energy_change_slider = Slider(
        start=-100,
        end=100,
        value=0,
        step=10,
        title="% Change in Commercial and Industrial Energy Usage",
    )
    ci_energy_change_slider.on_change("value", callback)

    ci_energy_elec_slider = Slider(
        start=CI_ENERGY_ELEC,
        end=100,
        value=CI_ENERGY_ELEC,
        step=1,
        title="% Electrification of Commercial and Industrial End Uses",
    )
    ci_energy_elec_slider.on_change("value", callback)

    bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
    bar_chart_source = ColumnDataSource(data=bar_chart_data)
    bar_chart = create_bar_chart(bar_chart_data, bar_chart_source)

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    inputs = Column(
        ci_energy_change_slider,
        ci_energy_elec_slider,
    )
    # @LAYOUT: changed to row. Look into grid and whatnot
    charts = row(bar_chart, inputs, stacked_chart, sizing_mode="stretch_both")
    doc.add_root(layout([[charts]]))


def non_res_stationary(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def on_road_motor_veh_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["change_veh_miles"] = change_veh_miles_slider.value
        user_inputs["reg_fleet_mpg"] = reg_fleet_mpg_slider.value
        user_inputs["veh_miles_elec"] = veh_miles_elec_slider.value
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)

    change_veh_miles_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Vehicle Miles Traveled per Person"
    )
    change_veh_miles_slider.on_change("value", callback)

    veh_miles_elec_slider = Slider(
        start=0, end=100, value=0, step=1, title="% Vehicle Miles that are Electric"
    )
    veh_miles_elec_slider.on_change("value", callback)

    reg_fleet_mpg_slider = Slider(
        start=1,
        end=100,
        value=REG_FLEET_MPG,
        step=1,
        title="Averge Regional Fleetwide Fuel Economy (MPG)",
    )
    reg_fleet_mpg_slider.on_change("value", callback)

    bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
    bar_chart_source = ColumnDataSource(data=bar_chart_data)
    bar_chart = create_bar_chart(bar_chart_data, bar_chart_source)

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    inputs = Column(
        change_veh_miles_slider,
        veh_miles_elec_slider,
        reg_fleet_mpg_slider,
    )
    # @LAYOUT: changed to row. Look into grid and whatnot
    charts = row(bar_chart, inputs, stacked_chart, sizing_mode="stretch_both")
    doc.add_root(layout([[charts]]))


def on_road_motor_veh(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def rail_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["change_rail_transit"] = change_rail_transit_slider.value
        user_inputs["rt_energy_elec_motion"] = rt_energy_elec_motion_slider.value
        user_inputs["change_freight_rail"] = change_freight_rail_slider.value
        user_inputs["f_energy_elec_motion"] = f_energy_elec_motion_slider.value
        user_inputs["change_inter_city_rail"] = change_inter_city_rail_slider.value
        user_inputs["icr_energy_elec_motion"] = icr_energy_elec_motion_slider.value
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)

    # transit rail
    change_rail_transit_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Transit Ridership"
    )
    change_rail_transit_slider.on_change("value", callback)

    rt_energy_elec_motion_slider = Slider(
        start=0,
        end=100,
        value=RT_ENERGY_ELEC_MOTION,
        step=1,
        title="% Electrification of Rail Transit",
    )
    rt_energy_elec_motion_slider.on_change("value", callback)

    # freight rail
    change_freight_rail_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Freight Rail"
    )
    change_freight_rail_slider.on_change("value", callback)

    f_energy_elec_motion_slider = Slider(
        start=0,
        end=100,
        value=F_ENERGY_ELEC_MOTION,
        step=1,
        title="% Electrification of Rail Freight",
    )
    f_energy_elec_motion_slider.on_change("value", callback)

    # inter-city rail
    change_inter_city_rail_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Inter-city Rail Travel"
    )
    change_inter_city_rail_slider.on_change("value", callback)

    icr_energy_elec_motion_slider = Slider(
        start=0,
        end=100,
        value=ICR_ENERGY_ELEC_MOTION,
        step=1,
        title="% Electrification of Inter-city Rail",
    )
    icr_energy_elec_motion_slider.on_change("value", callback)

    bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
    bar_chart_source = ColumnDataSource(data=bar_chart_data)
    bar_chart = create_bar_chart(bar_chart_data, bar_chart_source)

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    inputs = Column(
        change_rail_transit_slider,
        rt_energy_elec_motion_slider,
        change_freight_rail_slider,
        f_energy_elec_motion_slider,
        change_inter_city_rail_slider,
        icr_energy_elec_motion_slider,
    )
    # @LAYOUT: changed to row. Look into grid and whatnot
    charts = row(bar_chart, inputs, stacked_chart, sizing_mode="stretch_both")
    doc.add_root(layout([[charts]]))


def rail(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def aviation_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["change_air_travel"] = change_air_travel_slider.value
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)

    change_air_travel_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Air Travel"
    )
    change_air_travel_slider.on_change("value", callback)

    bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
    bar_chart_source = ColumnDataSource(data=bar_chart_data)
    bar_chart = create_bar_chart(bar_chart_data, bar_chart_source)

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    inputs = Column(
        change_air_travel_slider,
    )
    # @LAYOUT: changed to row. Look into grid and whatnot
    charts = row(bar_chart, inputs, stacked_chart, sizing_mode="stretch_both")
    doc.add_root(layout([[charts]]))


def aviation(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def mobile_other_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["change_marine_port"] = change_marine_port_slider.value
        user_inputs["mp_energy_elec_motion"] = mp_energy_elec_motion_slider.value
        user_inputs["change_off_road"] = change_off_road_slider.value
        user_inputs["or_energy_elec_motion"] = or_energy_elec_motion_slider.value
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)

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

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    inputs = Column(
        change_marine_port_slider,
        mp_energy_elec_motion_slider,
        change_off_road_slider,
        or_energy_elec_motion_slider,
    )
    # @LAYOUT: changed to row. Look into grid and whatnot
    charts = row(bar_chart, inputs, stacked_chart, sizing_mode="stretch_both")
    doc.add_root(layout([[charts]]))


def mobile_other(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def non_energy_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["change_ag"] = change_ag_slider.value
        user_inputs["change_solid_waste"] = change_solid_waste_slider.value
        user_inputs["change_wastewater"] = change_wasterwater_slider.value
        user_inputs["change_industrial_processes"] = change_industrial_processes_slider.value
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)

    change_ag_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Emissions from Agriculture"
    )
    change_ag_slider.on_change("value", callback)

    change_solid_waste_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Per Capita Landfill Waste"
    )
    change_solid_waste_slider.on_change("value", callback)

    change_wasterwater_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Per Capita Wastewater"
    )
    change_wasterwater_slider.on_change("value", callback)

    change_industrial_processes_slider = Slider(
        start=-100,
        end=100,
        value=0,
        step=1,
        title="% Change in Emissions from Industrial Processes",
    )
    change_industrial_processes_slider.on_change("value", callback)

    bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
    bar_chart_source = ColumnDataSource(data=bar_chart_data)
    bar_chart = create_bar_chart(bar_chart_data, bar_chart_source)

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    inputs = Column(
        change_ag_slider,
        change_solid_waste_slider,
        change_wasterwater_slider,
        change_industrial_processes_slider,
    )
    # @LAYOUT: changed to row. Look into grid and whatnot
    charts = row(bar_chart, inputs, stacked_chart)
    doc.add_root(layout([[charts]]))


def non_energy(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def sequestration_storage_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["change_urban_trees"] = change_urban_trees_slider.value
        user_inputs["change_forest"] = change_forest_slider.value
        user_inputs["ff_carbon_capture"] = ff_carbon_capture_slider.value
        user_inputs["air_capture"] = air_capture_slider.value
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)

    # sequestration
    change_urban_trees_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Urban Tree Coverage"
    )
    change_urban_trees_slider.on_change("value", callback)

    change_forest_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Forest Coverage"
    )
    change_forest_slider.on_change("value", callback)

    # carbon capture
    ff_carbon_capture_slider = Slider(
        start=0,
        end=100,
        value=0,
        step=1,
        title="% Carbon Captured at Combustion Site for Electricity Generation",
    )
    ff_carbon_capture_slider.on_change("value", callback)

    air_capture_slider = Slider(
        start=0, end=100, value=0, step=1, title="MMTCO2e Captured from the Air"
    )
    air_capture_slider.on_change("value", callback)

    bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
    bar_chart_source = ColumnDataSource(data=bar_chart_data)
    bar_chart = create_bar_chart(bar_chart_data, bar_chart_source)

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    inputs = Column(
        change_urban_trees_slider,
        change_forest_slider,
        ff_carbon_capture_slider,
        air_capture_slider,
    )
    # @LAYOUT: changed to row. Look into grid and whatnot
    charts = row(bar_chart, inputs, stacked_chart)
    doc.add_root(layout([[charts]]))


def sequestration_storage(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def electricity_grid_handler(doc: Document) -> None:
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
        # user_inputs["net_zero_carbon_input"] = (float(net_zero_carbon_input.value_input),)  # TK, possibly
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
        stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)
        pie_chart_source.data = wrangle_data_for_pie_chart(user_inputs)
        grid_text.text, grid_text.style = generate_text_and_style(user_inputs)

    # electric grid mix
    text, style = generate_text_and_style(user_inputs)
    grid_text = Paragraph(text=text, style=style)

    grid_coal_input = TextInput(value=str(round(GRID_COAL, 1)), title="% Coal in Grid Mix")
    grid_coal_input.on_change("value", callback)

    grid_oil_input = TextInput(value=str(round(GRID_OIL, 1)), title="% Oil in Grid Mix")
    grid_oil_input.on_change("value", callback)

    grid_ng_input = TextInput(value=str(round(GRID_NG, 1)), title="% Natural Gas in Grid Mix")
    grid_ng_input.on_change("value", callback)

    grid_nuclear_input = TextInput(value=str(round(GRID_NUCLEAR, 1)), title="% Nuclear in Grid Mix")
    grid_nuclear_input.on_change("value", callback)

    grid_solar_input = TextInput(value=str(round(GRID_SOLAR, 1)), title="% Solar in Grid Mix")
    grid_solar_input.on_change("value", callback)

    grid_wind_input = TextInput(value=str(round(GRID_WIND, 1)), title="% Wind in Grid Mix")
    grid_wind_input.on_change("value", callback)

    grid_bio_input = TextInput(value=str(round(GRID_BIO, 1)), title="% Biomass in Grid Mix")
    grid_bio_input.on_change("value", callback)

    grid_hydro_input = TextInput(value=str(round(GRID_HYDRO, 1)), title="% Hydropower in Grid Mix")
    grid_hydro_input.on_change("value", callback)

    grid_geo_input = TextInput(value=str(round(GRID_GEO, 1)), title="% Geothermal in Grid Mix")
    grid_geo_input.on_change("value", callback)

    grid_other_ff_input = TextInput(
        value=str(round(GRID_OTHER_FF, 1)), title="% Other Fossil Fuel in Grid Mix"
    )
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
    )
    bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
    bar_chart_source = ColumnDataSource(data=bar_chart_data)
    bar_chart = create_bar_chart(bar_chart_data, bar_chart_source)

    stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
    stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
    stacked_chart = create_stacked_chart(stacked_chart_data, stacked_chart_source)

    pie_chart_data = wrangle_data_for_pie_chart(user_inputs)
    pie_chart_source = ColumnDataSource(data=pie_chart_data)
    pie_chart = create_pie_chart(pie_chart_source)

    # @LAYOUT: changed to row. Look into grid and whatnot
    charts = row(bar_chart, stacked_chart, pie_chart)
    doc.add_root(layout([[inputs, charts]]))


def electricity_grid(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))
