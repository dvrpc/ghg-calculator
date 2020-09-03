"""Test that the funcs that calculate GHG continue to return correct values during refactor."""

from main import ghg_calc as g

"""
print("Stationary - Residential = ", ResGHG)
print("Stationary - Commercial and Industrial = ", ComIndGHG)
print("Mobile - Highway = ", MobHighwayGHG)
print("Mobile - Aviation = ", MobAviationGHG)
print("Mobile - Other = ", MobOtherGHG)
print("Mobile - Rail Transit = ", MobTransitGHG)
print("Non-Energy = ", NonEnergyGHG)
"""


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
    # this had been 15.030605191538607
    # and then assert res_ghg == 15.201897046514375 (difference with new number due to removing
    # conversion back and forth from %)
    assert res_ghg == 15.201897046514373


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

    assert ci_ghg == 27.47829273576916


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

    assert ghg == 17.937509502305318


def test_calc_mob_aviation_ghg():
    ghg = g.calc_aviation_ghg(0, 0)

    assert ghg == 3.9


def test_calc_mob_transit_ghg():
    ghg = g.calc_transit_ghg(
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.ff_carbon_capture,
        g.PerTransRailRidership,
        0,  # change in population
        g.RURAL_POP_PERCENT,
        g.SUBURBAN_POP_PERCENT,
        g.TransRailUrbanPerElecMotion,
        g.TransRailSuburbanPerElecMotion,
        g.TransRailRuralPerElecMotion,
        g.URBAN_POP_PERCENT,
    )

    assert ghg == 0.17340094875122483


def test_calc_other_mobile_ghg():
    ghg = g.calc_other_mobile_ghg(
        g.FreightRailPerElecMotion,
        g.GRID_COAL,
        g.GRID_NG,
        g.GRID_OIL,
        g.GRID_OTHER_FF,
        g.InterCityRailPerElecMotion,
        g.MarinePortPerElectrification,
        g.ff_carbon_capture,
        g.PerFreightRail,
        g.PerInterCityRail,
        g.PerMarinePort,
        g.PerOffroad,
        g.OffroadPerElectrification,
    )
    assert ghg == 1.1213238804345218


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
    # this had been 7.114884838160576
    assert ghg == 7.10780219120066
