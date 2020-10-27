import numpy as np

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bokeh.models import Slider, Column, ColumnDataSource, TextInput, Paragraph, LabelSet
from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.layouts import row, layout
from bokeh.plotting import figure, curdoc
from bokeh.transform import dodge, cumsum

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
    TransRailUrbanPerElecMotion,
    TransRailRuralPerElecMotion,
    TransRailRuralPerElecMotion,
    FreightRailPerElecMotion,
    InterCityRailPerElecMotion,
    MarinePortPerElecMotion,
    OffroadPerElecMotion,
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


def population_handler(doc: Document) -> None:
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
        user_inputs["rural_pop_pecent"] = float(rural_pop_percent_text_input.value)
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
    charts = row(bar_chart, stacked_chart, sizing_mode="scale_width")
    doc.add_root(layout([[inputs, charts]]))


def population(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def stationary_energy_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["res_energy_change"] = res_energy_change_slider.value
        user_inputs["urb_energy_elec"] = urb_energy_elec_slider.value
        user_inputs["sub_energy_elec"] = sub_energy_elec_slider.value
        user_inputs["rur_energy_elec"] = rur_energy_elec_slider.value
        user_inputs["ci_energy_change"] = ci_energy_change_slider.value
        user_inputs["ci_energy_elec"] = ci_energy_elec_slider.value
        bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)

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

    inputs = Column(
        res_energy_change_slider,
        urb_energy_elec_slider,
        sub_energy_elec_slider,
        rur_energy_elec_slider,
        ci_energy_change_slider,
        ci_energy_elec_slider,
    )

    doc.add_root(layout([[inputs, bar_chart]]))


def stationary_energy(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def mobile_energy_handler(doc: Document) -> None:
    def callback(attr, old, new):
        user_inputs["change_veh_miles"] = change_veh_miles_slider.value
        user_inputs["reg_fleet_mpg"] = reg_fleet_mpg_slider.value
        user_inputs["veh_miles_elec"] = veh_miles_elec_slider.value
        user_inputs["PerTransRailRidership"] = PerTransRailRidershipSlider.value
        user_inputs["TransRailUrbanPerElecMotion"] = TransRailUrbanPerElecMotionSlider.value
        user_inputs["TransRailSuburbanPerElecMotion"] = TransRailSuburbanPerElecMotionSlider.value
        user_inputs["TransRailRuralPerElecMotion"] = TransRailRuralPerElecMotionSlider.value
        user_inputs["PerFreightRail"] = PerFreightRailSlider.value
        user_inputs["FreightRailPerElecMotion"] = FreightRailPerElecMotionSlider.value
        user_inputs["PerInterCityRail"] = PerInterCityRailSlider.value
        user_inputs["InterCityRailPerElecMotion"] = InterCityRailPerElecMotionSlider.value
        user_inputs["PerMarinePort"] = PerMarinePortSlider.value
        user_inputs["MarinePortPerElectrification"] = MarinePortPerElectrificationSlider.value
        user_inputs["PerOffroad"] = PerOffroadSlider.value
        user_inputs["OffroadPerElectrification"] = OffroadPerElectrificationSlider.value
        user_inputs["change_air_travel"] = change_air_travel_slider.value
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

    # rail transit
    PerTransRailRidershipSlider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Transit Ridership"
    )
    PerTransRailRidershipSlider.on_change("value", callback)

    TransRailUrbanPerElecMotionSlider = Slider(
        start=0,
        end=100,
        value=TransRailUrbanPerElecMotion,
        step=1,
        title="% Electrification of Rail Transit Urban Areas",
    )
    TransRailUrbanPerElecMotionSlider.on_change("value", callback)

    TransRailSuburbanPerElecMotionSlider = Slider(
        start=0,
        end=100,
        value=TransRailRuralPerElecMotion,
        step=1,
        title="% Electrification of Rail Transit in Suburban Areas",
    )
    TransRailSuburbanPerElecMotionSlider.on_change("value", callback)

    TransRailRuralPerElecMotionSlider = Slider(
        start=0,
        end=100,
        value=TransRailRuralPerElecMotion,
        step=1,
        title="% Electrification of Rail Transit in Rural Areas",
    )
    TransRailRuralPerElecMotionSlider.on_change("value", callback)

    # aviation
    change_air_travel_slider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Air Travel"
    )
    change_air_travel_slider.on_change("value", callback)

    # freight rail
    PerFreightRailSlider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Freight Rail"
    )
    PerFreightRailSlider.on_change("value", callback)

    FreightRailPerElecMotionSlider = Slider(
        start=0,
        end=100,
        value=FreightRailPerElecMotion,
        step=1,
        title="% Electrification of Rail Freight",
    )
    FreightRailPerElecMotionSlider.on_change("value", callback)

    # inter-city rail
    PerInterCityRailSlider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Inter-city Rail Travel"
    )
    PerInterCityRailSlider.on_change("value", callback)

    InterCityRailPerElecMotionSlider = Slider(
        start=0,
        end=100,
        value=InterCityRailPerElecMotion,
        step=1,
        title="% Electrification of Inter-city Rail",
    )
    InterCityRailPerElecMotionSlider.on_change("value", callback)

    # marine and port
    PerMarinePortSlider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Marine and Port-related Activity"
    )
    PerMarinePortSlider.on_change("value", callback)

    MarinePortPerElectrificationSlider = Slider(
        start=0,
        end=100,
        value=MarinePortPerElecMotion,
        step=1,
        title="% Electrification of Marine and Port-related Activity",
    )
    MarinePortPerElectrificationSlider.on_change("value", callback)

    # off-road
    PerOffroadSlider = Slider(
        start=-100, end=100, value=0, step=1, title="% Change in Offroad Vehicle Use"
    )
    PerOffroadSlider.on_change("value", callback)

    OffroadPerElectrificationSlider = Slider(
        start=0,
        end=100,
        value=OffroadPerElecMotion,
        step=1,
        title="% Electrification of Offroad vehicles",
    )
    OffroadPerElectrificationSlider.on_change("value", callback)

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
        PerTransRailRidershipSlider,
        TransRailUrbanPerElecMotionSlider,
        TransRailSuburbanPerElecMotionSlider,
        TransRailRuralPerElecMotionSlider,
        change_air_travel_slider,
        PerFreightRailSlider,
        FreightRailPerElecMotionSlider,
        PerInterCityRailSlider,
        InterCityRailPerElecMotionSlider,
        PerMarinePortSlider,
        MarinePortPerElectrificationSlider,
        PerOffroadSlider,
        OffroadPerElectrificationSlider,
    )
    charts = Column(bar_chart, stacked_chart)
    doc.add_root(layout([[inputs, charts]]))


def mobile_energy(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))


def grid_mix_handler(doc: Document) -> None:
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
        # user_inputs["net_zero_carbon_input"] = (float(net_zero_carbon_input.value),)  # TK, possibly
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

    net_zero_carbon_input = TextInput(
        value=str(round(GRID_NUCLEAR + GRID_SOLAR + GRID_WIND + GRID_BIO + GRID_HYDRO + GRID_GEO)),
        title="% Net Zero Carbon Sources in Grid Mix",
    )
    net_zero_carbon_input.on_change("value", callback)

    grid_inputs = Column(
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
    pie_chart_data = wrangle_data_for_pie_chart(user_inputs)
    pie_chart_source = ColumnDataSource(data=pie_chart_data)
    pie_chart = create_pie_chart(pie_chart_source)

    doc.add_root(layout([[grid_inputs, pie_chart]]))


def grid_mix(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "main/base.html", dict(script=script))
