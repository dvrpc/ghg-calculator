"""Test that the funcs that calculate GHG continue to return correct values during refactor."""
import pytest

from bokeh_apps import ghg_calc as g

# 2015/no-change scenario ghg results
GHG_RES = 15.201897046514373  # originally 15.030605191538607, and then 15.201897046514375
GHG_CI = 27.47829273576916
GHG_HIGHWAY = 17.937509502305318
GHG_AVIATION = 3.9
GHG_OTHER_MOBILE = 0.8219187053797102
GHG_NON_ENERGY = 7.10780219120066  # this had been 7.114884838160576
GHG_RAIL = 0.4728063141496982
GHG_SEQ = -2.1367512166682836

# test the 2015/no-change scenario values are correct


def test_calc_res_ghg():
    res_ghg, res_ng_btu, res_elec_btu = g.calc_res_ghg(
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
    ci_ghg, ci_elec_btu = g.calc_ci_ghg(
        g.CI_ENERGY_ELEC,
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # change in CI energy usage
    )
    assert ci_ghg == GHG_CI


def test_calc_highway_GHG():
    highway_ghg, highway_elec_btu = g.calc_highway_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # percent vehicles miles that are electric
        0,  # change in population
        g.REG_FLEET_MPG,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        0,  # change in vehicle miles per person
    )
    assert highway_ghg == GHG_HIGHWAY


def test_calc_aviation_ghg():
    ghg = g.calc_aviation_ghg(0, 0)
    assert ghg == GHG_AVIATION


def test_calc_rail_ghg():
    ghg, btu = g.calc_rail_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # change in transit rail ridership
        0,  # change in population
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.RT_ENERGY_ELEC_MOTION,
        g.F_ENERGY_ELEC_MOTION,
        g.ICR_ENERGY_ELEC_MOTION,
        0,  # change in freight rail
        0,  # change in inter city rail
    )
    assert ghg == GHG_RAIL


def test_calc_other_mobile_ghg():
    mp_or_ghg, mp_or_elec_btu = g.calc_other_mobile_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.MP_ENERGY_ELEC_MOTION,
        0,  # change in marine and port-related activity
        0,  # change in off-road vehicle and equipment use
        g.OR_ENERGY_ELEC_MOTION,
    )
    assert mp_or_ghg == GHG_OTHER_MOBILE


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
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
    )
    assert ghg == g.GHG_NON_ENERGY


def test_calc_sequestration():
    ghg = g.calc_sequestration(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # change in residential energy usage
        0,  # change in pop
        g.RUR_ENERGY_ELEC,
        g.SUB_ENERGY_ELEC,
        g.URB_ENERGY_ELEC,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.CI_ENERGY_ELEC,
        0,  # change in CI energy usage
        0,  # vehicle miles electric
        g.REG_FLEET_MPG,
        0,  # change in veh miles
        0,  # change in rail transit
        g.RT_ENERGY_ELEC_MOTION,
        g.F_ENERGY_ELEC_MOTION,
        g.ICR_ENERGY_ELEC_MOTION,
        0,  # change in freight rail
        0,  # change in inter city rail
        g.MP_ENERGY_ELEC_MOTION,
        0,  # change in marine port
        0,  # change in off orad
        g.OR_ENERGY_ELEC_MOTION,
        0,  # change_ag
        0,  # change_ip
        0,  # change_solid_waste
        0,  # change_wasterwater
        0,  # change_forest
        0,  # change_urban_trees
        0,  # carbon capture
        0,  # air capture
    )
    assert ghg == GHG_SEQ


# test that changed inputs result in appropriate change in ghg (> or < than original)

# population change


def test_increase_pop_increase_res_ghg():
    res_ghg, res_ngbtu, res_elec_btu = g.calc_res_ghg(
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
    res_ghg, res_ngbtu, res_elec_btu = g.calc_res_ghg(
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
    highway_ghg, highway_elec_btu = g.calc_highway_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
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
    highway_ghg, highway_elect_btu = g.calc_highway_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # percent vehicles miles that are electric
        -1,  # change in population
        g.REG_FLEET_MPG,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        0,  # change in vehicle miles per person
    )
    assert highway_ghg < GHG_HIGHWAY


def test_increase_pop_increase_rail_ghg():
    ghg, btu = g.calc_rail_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # change in rail transit ridership
        1,  # change in population
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.RT_ENERGY_ELEC_MOTION,
        g.F_ENERGY_ELEC_MOTION,
        g.ICR_ENERGY_ELEC_MOTION,
        0,  # change in freight rail
        0,  # change in inter city rail
    )
    assert ghg > GHG_RAIL


def test_decrease_pop_decrease_rail_ghg():
    ghg, btu = g.calc_rail_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        0,  # change in rail transit ridership
        -1,  # change in population
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.RT_ENERGY_ELEC_MOTION,
        g.F_ENERGY_ELEC_MOTION,
        g.ICR_ENERGY_ELEC_MOTION,
        0,  # change in freight rail
        0,  # change in inter city rail
    )
    assert ghg < GHG_RAIL


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
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
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
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
    )
    assert ghg < GHG_NON_ENERGY
