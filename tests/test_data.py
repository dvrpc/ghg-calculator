"""Test that the funcs that calculate GHG continue to return correct values during refactor."""

from bokeh_apps import ghg_calc as g

"""
print("Stationary - Residential = ", ResGHG)
print("Stationary - Commercial and Industrial = ", ComIndGHG)
print("Mobile - Highway = ", MobHighwayGHG)
print("Mobile - Aviation = ", MobAviationGHG)
print("Mobile - Other = ", MobOtherGHG)
print("Mobile - Rail Transit = ", MobTransitGHG)
print("Non-Energy = ", NonEnergyGHG)
"""

# 2015/no-change scenario ghg results
GHG_RES = 15.201897046514373  # originally 15.030605191538607, and then 15.201897046514375
GHG_CI = 27.47829273576916
GHG_HIGHWAY = 17.937509502305318
GHG_AVIATION = 3.9
GHG_TRANSIT = 0.17340094875122483
GHG_OTHER_MOB = 1.1213238804345218
GHG_NON_ENERGY = 7.10780219120066  # this had been 7.114884838160576


# test the 2015/no-change scenario values are correct


def test_calc_res_ghg():
    res_ghg, res_ngbtu = g.calc_res_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # residential energy change
        0,  # change in population
        g.RUR_ENERGY_ELEC * 100,
        g.SUB_ENERGY_ELEC * 100,
        g.URB_ENERGY_ELEC * 100,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
    )
    assert res_ghg == GHG_RES


def test_calc_ci_ghg():
    ci_ghg = g.calc_ci_ghg(
        g.CI_ENERGY_ELEC,
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.ff_carbon_capture,
        0,  # change in CI energy usage
    )
    assert ci_ghg == GHG_CI


def test_calc_mob_highway_GHG():
    ghg = g.calc_highway_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.ff_carbon_capture,
        0,  # percent vehicles miles that are electric
        0,  # change in population
        g.REG_FLEET_MPG,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        0,  # change in vehicle miles per person
    )
    assert ghg == GHG_HIGHWAY


def test_calc_mob_aviation_ghg():
    ghg = g.calc_aviation_ghg(0, 0)
    assert ghg == GHG_AVIATION


def test_calc_mob_transit_ghg():
    ghg = g.calc_transit_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.ff_carbon_capture,
        0,  # change in transit rail ridership
        0,  # change in population
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.RT_ENERGY_ELEC_MOTION_URB,
        g.RT_ENERGY_ELEC_MOTION_SUB,
        g.RT_ENERGY_ELEC_MOTION_RUR,
        g.URBAN_POP_PERCENT,
    )
    assert ghg == GHG_TRANSIT


def test_calc_other_mobile_ghg():
    ghg = g.calc_other_mobile_ghg(
        g.F_ENERGY_ELEC_MOTION,
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.ICR_ENERGY_ELEC_MOTION,
        g.MP_ENERGY_ELEC_MOTION,
        g.ff_carbon_capture,
        0,  # change in freight rail ridership
        0,  # change in inter-city rail ridership
        0,  # change in marine and port-related activity
        0,  # change in off-road vehicle and equipment use
        g.OF_ENERGY_ELEC_MOTION,
    )
    assert ghg == GHG_OTHER_MOB


def test_calc_non_energy_ghg():
    ghg = g.calc_non_energy_ghg(
        g.CI_ENERGY_ELEC,
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # change in ag
        0,  # change in residential energy usage
        0,  # change in CI energy usage
        0,  # change in forest coverage
        0,  # change in energy use for industrial processes
        0,  # change in urban tree coverage
        0,  # change in solid waste
        0,  # change in wastewater
        0,  # change in population
        g.RUR_ENERGY_ELEC * 100,
        g.SUB_ENERGY_ELEC * 100,
        g.URB_ENERGY_ELEC * 100,
        g.URBAN_POP_PERCENT,
    )
    assert ghg == GHG_NON_ENERGY


# test that changed inputs result in appropriate change in ghg (> or < than original)

# population change


def test_increase_pop_increase_res_ghg():
    res_ghg, res_ngbtu = g.calc_res_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # residential energy change
        1,  # change in population
        g.RUR_ENERGY_ELEC * 100,
        g.SUB_ENERGY_ELEC * 100,
        g.URB_ENERGY_ELEC * 100,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
    )
    assert res_ghg > GHG_RES


def test_decrease_pop_decrease_res_ghg():
    res_ghg, res_ngbtu = g.calc_res_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # residential energy change
        -1,  # change in population
        g.RUR_ENERGY_ELEC * 100,
        g.SUB_ENERGY_ELEC * 100,
        g.URB_ENERGY_ELEC * 100,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
    )
    assert res_ghg < GHG_RES


def test_increase_pop_increase_highway_ghg():
    highway_ghg = g.calc_highway_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.ff_carbon_capture,
        0,  # percent vehicles miles that are electric
        1,  # change in population
        g.REG_FLEET_MPG,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        0,  # change in vehicle miles per person
    )
    assert highway_ghg > GHG_HIGHWAY


def test_decease_pop_decrease_highway_ghg():
    highway_ghg = g.calc_highway_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.ff_carbon_capture,
        0,  # percent vehicles miles that are electric
        -1,  # change in population
        g.REG_FLEET_MPG,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        0,  # change in vehicle miles per person
    )
    assert highway_ghg < GHG_HIGHWAY


def test_increase_pop_increase_transit_ghg():
    ghg = g.calc_transit_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.ff_carbon_capture,
        0,  # change in rail transit ridership
        1,  # change in population
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.RT_ENERGY_ELEC_MOTION_URB,
        g.RT_ENERGY_ELEC_MOTION_SUB,
        g.RT_ENERGY_ELEC_MOTION_RUR,
        g.URBAN_POP_PERCENT,
    )
    assert ghg > GHG_TRANSIT


def test_decrease_pop_decrease_transit_ghg():
    ghg = g.calc_transit_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.ff_carbon_capture,
        0,  # change in rail transit ridership
        -1,  # change in population
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.RT_ENERGY_ELEC_MOTION_URB,
        g.RT_ENERGY_ELEC_MOTION_SUB,
        g.RT_ENERGY_ELEC_MOTION_RUR,
        g.URBAN_POP_PERCENT,
    )
    assert ghg < GHG_TRANSIT


def test_increase_pop_increase_aviation_ghg():
    ghg = g.calc_aviation_ghg(1, 0)
    assert ghg > GHG_AVIATION


def test_decrease_pop_decrease_aviation_ghg():
    ghg = g.calc_aviation_ghg(-1, 0)
    assert ghg < GHG_AVIATION


def test_increase_pop_increase_non_energy_ghg():
    ghg = g.calc_non_energy_ghg(
        g.CI_ENERGY_ELEC,
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # change in ag
        0,  # change in residential energy usage
        0,  # change in CI energy usage
        0,  # change in forest coverage
        0,  # change in energy use for industrial processes
        0,  # change in urban tree coverage
        0,  # change in solid waste
        0,  # change in wastewater
        1,  # change in population
        g.RUR_ENERGY_ELEC * 100,
        g.SUB_ENERGY_ELEC * 100,
        g.URB_ENERGY_ELEC * 100,
        g.URBAN_POP_PERCENT,
    )
    assert ghg > GHG_NON_ENERGY


def test_decrease_pop_decrease_non_energy_ghg():
    ghg = g.calc_non_energy_ghg(
        g.CI_ENERGY_ELEC,
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # change in ag
        0,  # change in residential energy usage
        0,  # change in CI energy usage
        0,  # change in forest coverage
        0,  # change in energy use for industrial processes
        0,  # change in urban tree coverage
        0,  # change in solid waste
        0,  # change in wastewater
        -1,  # change in population
        g.RUR_ENERGY_ELEC * 100,
        g.SUB_ENERGY_ELEC * 100,
        g.URB_ENERGY_ELEC * 100,
        g.URBAN_POP_PERCENT,
    )
    assert ghg < GHG_NON_ENERGY


# change in per capita energy use
