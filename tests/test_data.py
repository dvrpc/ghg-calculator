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
        g.grid_coal,
        g.grid_ng,
        g.grid_oil,
        g.grid_other_ff,
        g.res_energy_change,
        g.pop_factor,
        g.rural_per_res_electrification,
        g.suburban_per_res_electrification,
        g.urban_per_res_electrification,
        g.rural_pop_percent,
        g.suburban_pop_percent,
        g.urban_pop_percent,
    )
    assert res_ghg == 15.030605191538609


def test_calc_ci_ghg():
    ci_ghg = g.calc_ci_ghg(
        g.ComIndPerElectrification,
        g.grid_coal,
        g.grid_ng,
        g.grid_oil,
        g.grid_other_ff,
        g.ff_carbon_capture,
        g.PerComIndEnergyUse,
    )

    assert ci_ghg == 27.47829273576916


def test_calc_mob_highway_GHG():
    ghg = g.calc_highway_ghg(
        g.grid_coal,
        g.grid_ng,
        g.grid_oil,
        g.grid_other_ff,
        g.ff_carbon_capture,
        g.PerEVMT,
        g.pop_factor,
        g.RegionalFleetMPG,
        g.rural_pop_percent,
        g.suburban_pop_percent,
        g.urban_pop_percent,
        g.VMTperCap,
    )

    assert ghg == 17.937509502305318


def test_calc_mob_aviation_ghg():
    ghg = g.calc_aviation_ghg(g.pop_factor, g.PerAviation)

    assert ghg == 3.9


def test_calc_mob_transit_ghg():
    ghg = g.calc_transit_ghg(
        g.grid_coal,
        g.grid_ng,
        g.grid_oil,
        g.grid_other_ff,
        g.ff_carbon_capture,
        g.PerTransRailRidership,
        g.pop_factor,
        g.rural_pop_percent,
        g.suburban_pop_percent,
        g.TransRailUrbanPerElecMotion,
        g.TransRailSuburbanPerElecMotion,
        g.TransRailRuralPerElecMotion,
        g.urban_pop_percent,
    )

    assert ghg == 0.17340094875122483


def test_calc_other_mobile_ghg():
    ghg = g.calc_other_mobile_ghg(
        g.FreightRailPerElecMotion,
        g.grid_coal,
        g.grid_ng,
        g.grid_oil,
        g.grid_other_ff,
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
        g.ComIndPerElectrification,
        g.grid_coal,
        g.grid_ng,
        g.grid_oil,
        g.grid_other_ff,
        g.PerAg,
        g.res_energy_change,
        g.PerComIndEnergyUse,
        g.PerForestCoverage,
        g.PerIP,
        g.PerUrbanTreeCoverage,
        g.PerWaste,
        g.PerWasteWater,
        g.pop_factor,
        g.rural_per_res_electrification,
        g.suburban_per_res_electrification,
        g.urban_per_res_electrification,
        g.urban_pop_percent,
    )

    assert ghg == 7.114884838160576
