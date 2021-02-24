"""Test that the funcs that calculate GHG continue to return correct values during refactor."""
import pytest

from bokeh_apps import ghg_calc as g

"""
NOTE: the tests below that check the 2015/no-change have two asserts - one to check how close the result is to the constant, known value in ghg_calc.py; the other checks the actual result from the function under test with the most recent result from it, so that we can identify any unintended/incorrect changes to the functions.

The tests that test the direction of a change only test against the most recent result of the function being tested, since we need the exact values under both circumstances to accurately test the slightest change.
"""

# 2015/no-change scenario ghg results, directly from functions
GHG_RES = 15.201897046514373
GHG_CI = 27.47829273576916
GHG_HIGHWAY = 17.937509502305318
GHG_AVIATION = 3.9
GHG_OTHER_MOBILE = 0.8219187053797102
GHG_NON_ENERGY = 8.861839878944668
GHG_RAIL = 0.4728063141496982
GHG_SEQ = -2.136751012577422


def test_calc_res_ghg():
    res_ghg, res_ng_btu, res_elec_btu = g.calc_res_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["res_energy_change"],
        g.user_inputs["change_pop"],
        g.RUR_ENERGY_ELEC * 100,
        g.SUB_ENERGY_ELEC * 100,
        g.URB_ENERGY_ELEC * 100,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
    )
    assert res_ghg == GHG_RES
    assert round(res_ghg, 1) == round(g.GHG_RES, 1)


def test_calc_ci_ghg():
    ci_ghg, ci_elec_btu = g.calc_ci_ghg(
        g.CI_ENERGY_ELEC,
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["ci_energy_change"],
    )
    assert ci_ghg == GHG_CI
    assert round(ci_ghg, 1) == round(g.GHG_CI, 1)


def test_calc_highway_GHG():
    highway_ghg, highway_elec_btu = g.calc_highway_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["veh_miles_elec"],
        g.user_inputs["change_pop"],
        g.REG_FLEET_MPG,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.user_inputs["change_veh_miles"],
    )
    assert highway_ghg == GHG_HIGHWAY
    assert round(highway_ghg, 1) == round(g.GHG_HIGHWAY, 1)


def test_calc_aviation_ghg():
    ghg = g.calc_aviation_ghg(0, 0)
    assert ghg == GHG_AVIATION
    assert round(ghg, 1) == round(g.GHG_AVIATION, 1)


def test_calc_rail_ghg():
    ghg, btu = g.calc_rail_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["change_freight_rail"],
        g.user_inputs["change_pop"],
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.RT_ENERGY_ELEC_MOTION,
        g.F_ENERGY_ELEC_MOTION,
        g.ICR_ENERGY_ELEC_MOTION,
        g.user_inputs["change_freight_rail"],
        g.user_inputs["change_inter_city_rail"],
    )
    assert ghg == GHG_RAIL
    assert round(ghg, 1) == round(g.GHG_RAIL, 1)


def test_calc_other_mobile_ghg():
    mp_or_ghg, mp_or_elec_btu = g.calc_other_mobile_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.MP_ENERGY_ELEC_MOTION,
        g.user_inputs["change_marine_port"],
        g.user_inputs["change_off_road"],
        g.OR_ENERGY_ELEC_MOTION,
    )
    assert mp_or_ghg == GHG_OTHER_MOBILE
    assert round(mp_or_ghg, 1) == round(g.GHG_OTHER_MOBILE, 1)


def test_calc_non_energy_ghg():
    ghg = g.calc_non_energy_ghg(
        g.CI_ENERGY_ELEC,
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["change_ag"],
        g.user_inputs["res_energy_change"],
        g.user_inputs["ci_energy_change"],
        g.user_inputs["change_forest"],
        g.user_inputs["change_industrial_processes"],
        g.user_inputs["change_urban_trees"],
        g.user_inputs["change_solid_waste"],
        g.user_inputs["change_wastewater"],
        g.user_inputs["change_pop"],
        g.RUR_ENERGY_ELEC * 100,
        g.SUB_ENERGY_ELEC * 100,
        g.URB_ENERGY_ELEC * 100,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
    )
    assert ghg == GHG_NON_ENERGY
    assert round(ghg, 1) == round(g.GHG_NON_ENERGY, 1)


def test_calc_sequestration():
    ghg = g.calc_sequestration(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["res_energy_change"],
        g.user_inputs["change_pop"],
        g.RUR_ENERGY_ELEC,
        g.SUB_ENERGY_ELEC,
        g.URB_ENERGY_ELEC,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.CI_ENERGY_ELEC,
        g.user_inputs["ci_energy_change"],
        g.user_inputs["veh_miles_elec"],
        g.REG_FLEET_MPG,
        g.user_inputs["change_veh_miles"],
        g.user_inputs["change_rail_transit"],
        g.RT_ENERGY_ELEC_MOTION,
        g.F_ENERGY_ELEC_MOTION,
        g.ICR_ENERGY_ELEC_MOTION,
        g.user_inputs["change_freight_rail"],
        g.user_inputs["change_inter_city_rail"],
        g.MP_ENERGY_ELEC_MOTION,
        g.user_inputs["change_marine_port"],
        g.user_inputs["change_off_road"],
        g.OR_ENERGY_ELEC_MOTION,
        g.user_inputs["change_ag"],
        g.user_inputs["change_industrial_processes"],
        g.user_inputs["change_solid_waste"],
        g.user_inputs["change_wastewater"],
        g.user_inputs["change_forest"],
        g.user_inputs["change_urban_trees"],
        g.user_inputs["ff_carbon_capture"],
        g.user_inputs["air_capture"],
    )
    assert ghg == GHG_SEQ
    assert round(ghg, 1) == round(g.GHG_SEQ, 1)


# test that changed inputs result in appropriate change in ghg (> or < than original)

# population change


def test_increase_pop_increase_res_ghg():
    res_ghg, res_ngbtu, res_elec_btu = g.calc_res_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["res_energy_change"],
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
        g.user_inputs["res_energy_change"],
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
        g.user_inputs["veh_miles_elec"],
        1,  # change in population
        g.REG_FLEET_MPG,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.user_inputs["change_veh_miles"],
    )
    assert highway_ghg > GHG_HIGHWAY


def test_decease_pop_decrease_highway_ghg():
    highway_ghg, highway_elect_btu = g.calc_highway_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["veh_miles_elec"],
        -1,  # change in population
        g.REG_FLEET_MPG,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.user_inputs["change_veh_miles"],
    )
    assert highway_ghg < GHG_HIGHWAY


def test_increase_pop_increase_rail_ghg():
    ghg, btu = g.calc_rail_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["change_rail_transit"],
        1,  # change in population
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.RT_ENERGY_ELEC_MOTION,
        g.F_ENERGY_ELEC_MOTION,
        g.ICR_ENERGY_ELEC_MOTION,
        g.user_inputs["change_freight_rail"],
        g.user_inputs["change_inter_city_rail"],
    )
    assert ghg > GHG_RAIL


def test_decrease_pop_decrease_rail_ghg():
    ghg, btu = g.calc_rail_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.user_inputs["change_rail_transit"],
        -1,  # change in population
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.URBAN_POP_PERCENT,
        g.RT_ENERGY_ELEC_MOTION,
        g.F_ENERGY_ELEC_MOTION,
        g.ICR_ENERGY_ELEC_MOTION,
        g.user_inputs["change_freight_rail"],
        g.user_inputs["change_inter_city_rail"],
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
        g.user_inputs["change_ag"],
        g.user_inputs["res_energy_change"],
        g.user_inputs["ci_energy_change"],
        g.user_inputs["change_forest"],
        g.user_inputs["change_industrial_processes"],
        g.user_inputs["change_urban_trees"],
        g.user_inputs["change_solid_waste"],
        g.user_inputs["change_wastewater"],
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
        g.user_inputs["change_ag"],
        g.user_inputs["res_energy_change"],
        g.user_inputs["ci_energy_change"],
        g.user_inputs["change_forest"],
        g.user_inputs["change_industrial_processes"],
        g.user_inputs["change_urban_trees"],
        g.user_inputs["change_solid_waste"],
        g.user_inputs["change_wastewater"],
        -1,  # change in population
        g.RUR_ENERGY_ELEC * 100,
        g.SUB_ENERGY_ELEC * 100,
        g.URB_ENERGY_ELEC * 100,
        g.URBAN_POP_PERCENT,
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
    )
    assert ghg < GHG_NON_ENERGY
