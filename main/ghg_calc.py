from math import pi
from statistics import mean

import numpy as np
import pandas as pd

from bokeh.layouts import row, column
from bokeh.models import Slider, Column, ColumnDataSource, TextInput, Paragraph
from bokeh.palettes import Viridis7, Spectral10
from bokeh.plotting import figure, curdoc
from bokeh.transform import dodge, cumsum


sectors = [
    "Residential",
    "Commercial/Industrial",
    "Mobile-Highway",
    "Mobile-Transit",
    "Mobile-Aviation",
    "Mobile-Other",
    "Non-Energy",
]

# Implied National Emissions rate from NG Transmission, Storage, Distribution (fugitive emissions in MMTCO2e/million CF)
MMTCO2ePerMillionCFNG_CH4 = 0.00000169
MMTCO2ePerMillionCFNG_CO2 = 0.000000004

# 2015 GHG Inventory Total Emissions (MMTCO2E)
GHG_RES = 15.37
GHG_CI = 27.96  # non-residential/commercial & industrial
GHG_HIGHWAY = 17.94
GHG_TRANSIT = 0.18
GHG_AVIATION = 3.90
GHG_OTHER_MOBILE = 1.12  # includes freight & intercity rail, marine & port-related, off-road vehicles and equipment
GHG_AG = 0.41  # agriculture
GHG_SOLID_WASTE = 2.01  # landfills
GHG_WASTEWATER = 0.49
GHG_IP = 5.52  # Includes Hydrogen production, iron & steel production, industrial wastewater treatment, ODS substitutes, and petroleum refining
GHG_URBAN_TREES = -1.025
GHG_FORESTS = -1.109
GHG_FOREST_CHANGE = 0.380
RES_NG = 115884601.50 / 1000  # NG Consumpton 2015 (million CF)
CI_NG = 139139475 / 1000  # NG Consumpton 2015 (million CF)
GHG_NON_ENERGY = (
    GHG_AG
    + GHG_SOLID_WASTE
    + GHG_WASTEWATER
    + GHG_IP
    + GHG_URBAN_TREES
    + GHG_FORESTS
    + GHG_FOREST_CHANGE
    + (RES_NG + CI_NG) * (MMTCO2ePerMillionCFNG_CH4 + MMTCO2ePerMillionCFNG_CO2)
)

# Demographics
URBAN_POP = 1691830
SUBURBAN_POP = 3693658
RURAL_POP = 332445
POP = URBAN_POP + SUBURBAN_POP + RURAL_POP

pop_factor = 0
urban_pop_percent = URBAN_POP / POP * 100
suburban_pop_percent = SUBURBAN_POP / POP * 100
rural_pop_percent = RURAL_POP / POP * 100

# Average Emissions pr MWh of fossil fuels from eGRID 2014/2016 for RFCE
# NOTE: Future reference - should we pull plant-level data for this?)
CO2_LB_MWH_COAL = (2169.484351 + 2225.525) / 2
CO2_LB_MWH_OIL = (1600.098812 + 1341.468) / 2
CO2_LB_MWH_NG = (929.651872 + 897.037) / 2
CO2_LB_MWH_OTHER_FF = (1488.036692 + 1334.201) / 2

# Percent of carbon emissions from combustion of fossil fuels for electricity that are captured and stored
ff_carbon_capture = 0

# Electricity Mix from 2015 inventory
grid_coal = 20.47
grid_oil = 0.47
grid_ng = 34.38
grid_other_ff = 0.46
grid_bio = 1.59
grid_hydro = 1.06
grid_nuclear = 40.10
grid_wind = 1.16
grid_solar = 0.30
grid_geo = 0.00
GRID_LOSS = 0.047287092

CO2_MMT_KB_FOK = 0.000428929
CO2_MMT_KB_LPG = 0.000219762
CO2_LB_KCF_NG = 123.0744706

MMT_LB = 0.00000000045359
KB_G = 1 / 42000
MT_TO_MMT = 0.000001

# BTU Conversions
BTU_KWH = 3412
BTU_MWH = BTU_KWH * 1000
BTU_CF_NG_PA = 1048
BTU_CF_NG_NJ = 1050
BTU_CCF_AVG = mean([BTU_CF_NG_PA, BTU_CF_NG_NJ]) * 100
BTU_B_FKO = 5770000
BTU_GAL_FOK = BTU_B_FKO * (1 / 42)
BTU_B_LPG = 3540000
BTU_GAL_LPG = BTU_B_LPG * (1 / 42)

# MTCO2e per BBtu - From ComInd 2015
CO2_MMT_BBTU_NG = 53.20
CO2_MMT_BBTU_COAL = 95.13
CO2_MMT_BBTU_DFO = 74.39
CO2_MMT_BBTU_KER = 73.63
CO2_MMT_BBTU_LPG = 65.15
CO2_MMT_BBTU_MOTOR_GAS = 71.60
CO2_MMT_BBTU_RFO = 75.35
CO2_MMT_BBTU_PETCOKE = 102.36
CO2_MMT_BBTU_STILL_GAS = 66.96
CO2_MMT_BBTU_NAPHTHAS = 72.62

# Residential Stationary ENERGY
res_energy_change = 0

URBAN_ELEC_MWH_CAP = 2.41  # MWh/person
SUBURBAN_ELEC_MWH_CAP = 3.17  # MWh/person
RURAL_ELEC_MWH_CAP = 3.81  # MWh/person

URBAN_NG_CCF_CAP = 246.04  # CCF/person
SUBURBAN_NG_CCF_CAP = 193.00  # CCF/person
RURAL_NG_CCF_CAP = 89.35  # CCF/person

URBAN_FOK_GAL_CAP = 14.50  # gallons/person
SUBURBAN_FOK_GAL_CAP = 43.32  # gallons/person
RURAL_FOK_GAL_CAP = 80.84  # gallons/person

URBAN_LPG_GAL_CAP = 3.46  # gallons/person
SUBURBAN_LPG_GAL_CAP = 8.44  # gallons/person
RURAL_LPG_GAL_CAP = 44.38  # gallons/person

# End uses for residential fuels from EIA 2015 by decimal fraction of Trillion BTUs
RES_ELEC_SPACE = 0.1284
RES_ELEC_WATER = 0.1194
RES_ELEC_OTHER = 0.7523

RES_NG_SPACE = 0.7066
RES_NG_WATER = 0.2224
RES_NG_OTHER = 0.0697

RES_FOK_SPACE = 0.8333
RES_FOK_WATER = 0.1613
RES_FOK_OTHER = 0.0054

RES_LPG_SPACE = 0.6522
RES_LPG_WATER = 0.1957
RES_LPG_OTHER = 0.1522

# Energy to use efficiencies for residential end uses and fuels
RES_ELEC_SPACE_USEFUL = 1
RES_ELEC_WATER_USEFUL = 1
RES_ELEC_OTHER_USEFUL = 1
RES_ELEC_WATER_USEFUL_REPLACE_FF = 25.0
RES_ELEC_OTHER_USEFUL_REPLACE_FF = 15.0

RES_NG_SPACE_USEFUL = 0.80  # 80% 2014 federal minimum, 95% ENERGY STAR spec
RES_NG_WATER_USEFUL = 0.82  # 80-82% 2012 federal minimum, 90% ENERGY STAR spec
RES_NG_OTHER_USEFUL = 0.80

RES_FOK_SPACE_USEFUL = 0.80
RES_FOK_WATER_USEFUL = 0.80
RES_FOK_OTHER_USEFUL = 0.80

RES_LPG_SPACE_USEFUL = 0.80
RES_LPG_WATER_USEFUL = 0.80
RES_LPG_OTHER_USEFUL = 0.80

# Btus per person per community type, fuel type, and end use
UrbanBTUPerCapElecSpaceHeatingUsed = (
    URBAN_ELEC_MWH_CAP * (RES_ELEC_SPACE) * (RES_ELEC_SPACE_USEFUL) * BTU_MWH
)
UrbanBTUPerCapElecWaterHeatingUsed = (
    URBAN_ELEC_MWH_CAP * (RES_ELEC_WATER) * (RES_ELEC_WATER_USEFUL) * BTU_MWH
)
UrbanBTUPerCapElecOtherUsed = (
    URBAN_ELEC_MWH_CAP * (RES_ELEC_OTHER) * (RES_ELEC_OTHER_USEFUL) * BTU_MWH
)
SuburbanBTUPerCapElecSpaceHeatingUsed = (
    SUBURBAN_ELEC_MWH_CAP * (RES_ELEC_SPACE) * (RES_ELEC_SPACE_USEFUL) * BTU_MWH
)
SuburbanBTUPerCapElecWaterHeatingUsed = (
    SUBURBAN_ELEC_MWH_CAP * (RES_ELEC_WATER) * (RES_ELEC_WATER_USEFUL) * BTU_MWH
)
SuburbanBTUPerCapElecOtherUsed = (
    SUBURBAN_ELEC_MWH_CAP * (RES_ELEC_OTHER) * (RES_ELEC_OTHER_USEFUL) * BTU_MWH
)
RuralBTUPerCapElecSpaceHeatingUsed = (
    RURAL_ELEC_MWH_CAP * (RES_ELEC_SPACE) * (RES_ELEC_SPACE_USEFUL) * BTU_MWH
)
RuralBTUPerCapElecWaterHeatingUsed = (
    RURAL_ELEC_MWH_CAP * (RES_ELEC_WATER) * (RES_ELEC_WATER_USEFUL) * BTU_MWH
)
RuralBTUPerCapElecOtherUsed = (
    RURAL_ELEC_MWH_CAP * (RES_ELEC_OTHER) * (RES_ELEC_OTHER_USEFUL) * BTU_MWH
)

UrbanBTUPerCapNGSpaceHeatingUsed = (
    URBAN_NG_CCF_CAP * (RES_NG_SPACE) * (RES_NG_SPACE_USEFUL) * BTU_CCF_AVG
)
UrbanBTUPerCapNGWaterHeatingUsed = (
    URBAN_NG_CCF_CAP * (RES_NG_WATER) * (RES_NG_WATER_USEFUL) * BTU_CCF_AVG
)
UrbanBTUPerCapNGOtherUsed = URBAN_NG_CCF_CAP * (RES_NG_OTHER) * (RES_NG_OTHER_USEFUL) * BTU_CCF_AVG
SuburbanBTUPerCapNGSpaceHeatingUsed = (
    SUBURBAN_NG_CCF_CAP * (RES_NG_SPACE) * (RES_NG_SPACE_USEFUL) * BTU_CCF_AVG
)
SuburbanBTUPerCapNGWaterHeatingUsed = (
    SUBURBAN_NG_CCF_CAP * (RES_NG_WATER) * (RES_NG_WATER_USEFUL) * BTU_CCF_AVG
)
SuburbanBTUPerCapNGOtherUsed = (
    SUBURBAN_NG_CCF_CAP * (RES_NG_OTHER) * (RES_NG_OTHER_USEFUL) * BTU_CCF_AVG
)
RuralBTUPerCapNGSpaceHeatingUsed = (
    RURAL_NG_CCF_CAP * (RES_NG_SPACE) * (RES_NG_SPACE_USEFUL) * BTU_CCF_AVG
)
RuralBTUPerCapNGWaterHeatingUsed = (
    RURAL_NG_CCF_CAP * (RES_NG_WATER) * (RES_NG_WATER_USEFUL) * BTU_CCF_AVG
)
RuralBTUPerCapNGOtherUsed = RURAL_NG_CCF_CAP * (RES_NG_OTHER) * (RES_NG_OTHER_USEFUL) * BTU_CCF_AVG

UrbanBTUPerCapFOKerSpaceHeatingUsed = (
    URBAN_FOK_GAL_CAP * (RES_FOK_SPACE) * (RES_FOK_SPACE_USEFUL) * BTU_GAL_FOK
)
UrbanBTUPerCapFOKerWaterHeatingUsed = (
    URBAN_FOK_GAL_CAP * (RES_FOK_WATER) * (RES_FOK_WATER_USEFUL) * BTU_GAL_FOK
)
UrbanBTUPerCapFOKerOtherUsed = (
    URBAN_FOK_GAL_CAP * (RES_FOK_OTHER) * (RES_FOK_OTHER_USEFUL) * BTU_GAL_FOK
)
SuburbanBTUPerCapFOKerSpaceHeatingUsed = (
    SUBURBAN_FOK_GAL_CAP * (RES_FOK_SPACE) * (RES_FOK_SPACE_USEFUL) * BTU_GAL_FOK
)
SuburbanBTUPerCapFOKerWaterHeatingUsed = (
    SUBURBAN_FOK_GAL_CAP * (RES_FOK_WATER) * (RES_FOK_WATER_USEFUL) * BTU_GAL_FOK
)
SuburbanBTUPerCapFOKerOtherUsed = (
    SUBURBAN_FOK_GAL_CAP * (RES_FOK_OTHER) * (RES_FOK_OTHER_USEFUL) * BTU_GAL_FOK
)
RuralBTUPerCapFOKerSpaceHeatingUsed = (
    RURAL_FOK_GAL_CAP * (RES_FOK_SPACE) * (RES_FOK_SPACE_USEFUL) * BTU_GAL_FOK
)
RuralBTUPerCapFOKerWaterHeatingUsed = (
    RURAL_FOK_GAL_CAP * (RES_FOK_WATER) * (RES_FOK_WATER_USEFUL) * BTU_GAL_FOK
)
RuralBTUPerCapFOKerOtherUsed = (
    RURAL_FOK_GAL_CAP * (RES_FOK_OTHER) * (RES_FOK_OTHER_USEFUL) * BTU_GAL_FOK
)

UrbanBTUPerCapLPGSpaceHeatingUsed = (
    URBAN_LPG_GAL_CAP * (RES_LPG_SPACE) * (RES_LPG_SPACE_USEFUL) * BTU_GAL_LPG
)
UrbanBTUPerCapLPGWaterHeatingUsed = (
    URBAN_LPG_GAL_CAP * (RES_LPG_WATER) * (RES_LPG_WATER_USEFUL) * BTU_GAL_LPG
)
UrbanBTUPerCapLPGOtherUsed = (
    URBAN_LPG_GAL_CAP * (RES_LPG_OTHER) * (RES_LPG_OTHER_USEFUL) * BTU_GAL_LPG
)
SuburbanBTUPerCapLPGSpaceHeatingUsed = (
    SUBURBAN_LPG_GAL_CAP * (RES_LPG_SPACE) * (RES_LPG_SPACE_USEFUL) * BTU_GAL_LPG
)
SuburbanBTUPerCapLPGWaterHeatingUsed = (
    SUBURBAN_LPG_GAL_CAP * (RES_LPG_WATER) * (RES_LPG_WATER_USEFUL) * BTU_GAL_LPG
)
SuburbanBTUPerCapLPGOtherUsed = (
    SUBURBAN_LPG_GAL_CAP * (RES_LPG_OTHER) * (RES_LPG_OTHER_USEFUL) * BTU_GAL_LPG
)
RuralBTUPerCapLPGSpaceHeatingUsed = (
    RURAL_LPG_GAL_CAP * (RES_LPG_SPACE) * (RES_LPG_SPACE_USEFUL) * BTU_GAL_LPG
)
RuralBTUPerCapLPGWaterHeatingUsed = (
    RURAL_LPG_GAL_CAP * (RES_LPG_WATER) * (RES_LPG_WATER_USEFUL) * BTU_GAL_LPG
)
RuralBTUPerCapLPGOtherUsed = (
    RURAL_LPG_GAL_CAP * (RES_LPG_OTHER) * (RES_LPG_OTHER_USEFUL) * BTU_GAL_LPG
)

UrbanBTUPerCapElecUsed = (
    UrbanBTUPerCapElecSpaceHeatingUsed
    + UrbanBTUPerCapElecWaterHeatingUsed
    + UrbanBTUPerCapElecOtherUsed
)
SuburbanBTUPerCapElecUsed = (
    SuburbanBTUPerCapElecSpaceHeatingUsed
    + SuburbanBTUPerCapElecWaterHeatingUsed
    + SuburbanBTUPerCapElecOtherUsed
)
RuralBTUPerCapElecUsed = (
    RuralBTUPerCapElecSpaceHeatingUsed
    + RuralBTUPerCapElecWaterHeatingUsed
    + RuralBTUPerCapElecOtherUsed
)

PerUrbanElecBTUPerCapUsedSpaceHeating = (
    UrbanBTUPerCapElecSpaceHeatingUsed / UrbanBTUPerCapElecUsed * 100
)
PerUrbanElecBTUPerCapUsedWaterHeating = (
    UrbanBTUPerCapElecWaterHeatingUsed / UrbanBTUPerCapElecUsed * 100
)
PerUrbanElecBTUPerCapUsedOther = UrbanBTUPerCapElecOtherUsed / UrbanBTUPerCapElecUsed * 100

PerSuburbanElecBTUPerCapUsedSpaceHeating = (
    SuburbanBTUPerCapElecSpaceHeatingUsed / SuburbanBTUPerCapElecUsed * 100
)
PerSuburbanElecBTUPerCapUsedWaterHeating = (
    SuburbanBTUPerCapElecWaterHeatingUsed / SuburbanBTUPerCapElecUsed * 100
)
PerSuburbanElecBTUPerCapUsedOther = SuburbanBTUPerCapElecOtherUsed / SuburbanBTUPerCapElecUsed * 100
PerRuralElecBTUPerCapUsedSpaceHeating = (
    RuralBTUPerCapElecSpaceHeatingUsed / RuralBTUPerCapElecUsed * 100
)
PerRuralElecBTUPerCapUsedWaterHeating = (
    RuralBTUPerCapElecWaterHeatingUsed / RuralBTUPerCapElecUsed * 100
)
PerRuralElecBTUPerCapUsedOther = RuralBTUPerCapElecOtherUsed / RuralBTUPerCapElecUsed * 100

UrbanBTUPerCapNGUsed = (
    UrbanBTUPerCapNGSpaceHeatingUsed + UrbanBTUPerCapNGWaterHeatingUsed + UrbanBTUPerCapNGOtherUsed
)
SuburbanBTUPerCapNGUsed = (
    SuburbanBTUPerCapNGSpaceHeatingUsed
    + SuburbanBTUPerCapNGWaterHeatingUsed
    + SuburbanBTUPerCapNGOtherUsed
)
RuralBTUPerCapNGUsed = (
    RuralBTUPerCapNGSpaceHeatingUsed + RuralBTUPerCapNGWaterHeatingUsed + RuralBTUPerCapNGOtherUsed
)

PerUrbanNGBTUPerCapUsedSpaceHeating = UrbanBTUPerCapNGSpaceHeatingUsed / UrbanBTUPerCapNGUsed * 100
PerUrbanNGBTUPerCapUsedWaterHeating = UrbanBTUPerCapNGWaterHeatingUsed / UrbanBTUPerCapNGUsed * 100
PerUrbanNGBTUPerCapUsedOther = UrbanBTUPerCapNGOtherUsed / UrbanBTUPerCapNGUsed * 100
PerSuburbanNGBTUPerCapUsedSpaceHeating = (
    SuburbanBTUPerCapNGSpaceHeatingUsed / SuburbanBTUPerCapNGUsed * 100
)
PerSuburbanNGBTUPerCapUsedWaterHeating = (
    SuburbanBTUPerCapNGWaterHeatingUsed / SuburbanBTUPerCapNGUsed * 100
)
PerSuburbanNGBTUPerCapUsedOther = SuburbanBTUPerCapNGOtherUsed / SuburbanBTUPerCapNGUsed * 100
PerRuralNGBTUPerCapUsedSpaceHeating = RuralBTUPerCapNGSpaceHeatingUsed / RuralBTUPerCapNGUsed * 100
PerRuralNGBTUPerCapUsedWaterHeating = RuralBTUPerCapNGWaterHeatingUsed / RuralBTUPerCapNGUsed * 100
PerRuralNGBTUPerCapUsedOther = RuralBTUPerCapNGOtherUsed / RuralBTUPerCapNGUsed * 100

UrbanBTUPerCapFOKerUsed = (
    UrbanBTUPerCapFOKerSpaceHeatingUsed
    + UrbanBTUPerCapFOKerWaterHeatingUsed
    + UrbanBTUPerCapFOKerOtherUsed
)
SuburbanBTUPerCapFOKerUsed = (
    SuburbanBTUPerCapFOKerSpaceHeatingUsed
    + SuburbanBTUPerCapFOKerWaterHeatingUsed
    + SuburbanBTUPerCapFOKerOtherUsed
)
RuralBTUPerCapFOKerUsed = (
    RuralBTUPerCapFOKerSpaceHeatingUsed
    + RuralBTUPerCapFOKerWaterHeatingUsed
    + RuralBTUPerCapFOKerOtherUsed
)

PerUrbanFOKerBTUPerCapUsedSpaceHeating = (
    UrbanBTUPerCapFOKerSpaceHeatingUsed / UrbanBTUPerCapFOKerUsed * 100
)
PerUrbanFOKerBTUPerCapUsedWaterHeating = (
    UrbanBTUPerCapFOKerWaterHeatingUsed / UrbanBTUPerCapFOKerUsed * 100
)
PerUrbanFOKerBTUPerCapUsedOther = UrbanBTUPerCapFOKerOtherUsed / UrbanBTUPerCapFOKerUsed * 100
PerSuburbanFOKerBTUPerCapUsedSpaceHeating = (
    SuburbanBTUPerCapFOKerSpaceHeatingUsed / SuburbanBTUPerCapFOKerUsed * 100
)
PerSuburbanFOKerBTUPerCapUsedWaterHeating = (
    SuburbanBTUPerCapFOKerWaterHeatingUsed / SuburbanBTUPerCapFOKerUsed * 100
)
PerSuburbanFOKerBTUPerCapUsedOther = (
    SuburbanBTUPerCapFOKerOtherUsed / SuburbanBTUPerCapFOKerUsed * 100
)
PerRuralFOKerBTUPerCapUsedSpaceHeating = (
    RuralBTUPerCapFOKerSpaceHeatingUsed / RuralBTUPerCapFOKerUsed * 100
)
PerRuralFOKerBTUPerCapUsedWaterHeating = (
    RuralBTUPerCapFOKerWaterHeatingUsed / RuralBTUPerCapFOKerUsed * 100
)
PerRuralFOKerBTUPerCapUsedOther = RuralBTUPerCapFOKerOtherUsed / RuralBTUPerCapFOKerUsed * 100

UrbanBTUPerCapLPGUsed = (
    UrbanBTUPerCapLPGSpaceHeatingUsed
    + UrbanBTUPerCapLPGWaterHeatingUsed
    + UrbanBTUPerCapLPGOtherUsed
)
SuburbanBTUPerCapLPGUsed = (
    SuburbanBTUPerCapLPGSpaceHeatingUsed
    + SuburbanBTUPerCapLPGWaterHeatingUsed
    + SuburbanBTUPerCapLPGOtherUsed
)
RuralBTUPerCapLPGUsed = (
    RuralBTUPerCapLPGSpaceHeatingUsed
    + RuralBTUPerCapLPGWaterHeatingUsed
    + RuralBTUPerCapLPGOtherUsed
)

PerUrbanLPGBTUPerCapUsedSpaceHeating = (
    UrbanBTUPerCapLPGSpaceHeatingUsed / UrbanBTUPerCapLPGUsed * 100
)
PerUrbanLPGBTUPerCapUsedWaterHeating = (
    UrbanBTUPerCapLPGWaterHeatingUsed / UrbanBTUPerCapLPGUsed * 100
)
PerUrbanLPGBTUPerCapUsedOther = UrbanBTUPerCapLPGOtherUsed / UrbanBTUPerCapLPGUsed * 100
PerSuburbanLPGBTUPerCapUsedSpaceHeating = (
    SuburbanBTUPerCapLPGSpaceHeatingUsed / SuburbanBTUPerCapLPGUsed * 100
)
PerSuburbanLPGBTUPerCapUsedWaterHeating = (
    SuburbanBTUPerCapLPGWaterHeatingUsed / SuburbanBTUPerCapLPGUsed * 100
)
PerSuburbanLPGBTUPerCapUsedOther = SuburbanBTUPerCapLPGOtherUsed / SuburbanBTUPerCapLPGUsed * 100
PerRuralLPGBTUPerCapUsedSpaceHeating = (
    RuralBTUPerCapLPGSpaceHeatingUsed / RuralBTUPerCapLPGUsed * 100
)
PerRuralLPGBTUPerCapUsedWaterHeating = (
    RuralBTUPerCapLPGWaterHeatingUsed / RuralBTUPerCapLPGUsed * 100
)
PerRuralLPGBTUPerCapUsedOther = RuralBTUPerCapLPGOtherUsed / RuralBTUPerCapLPGUsed * 100

UrbanBTUPerCapUsed = (
    UrbanBTUPerCapElecUsed + UrbanBTUPerCapNGUsed + UrbanBTUPerCapFOKerUsed + UrbanBTUPerCapLPGUsed
)  # BTU/Person
SuburbanBTUPerCapUsed = (
    SuburbanBTUPerCapElecUsed
    + SuburbanBTUPerCapNGUsed
    + SuburbanBTUPerCapFOKerUsed
    + SuburbanBTUPerCapLPGUsed
)  # BTU/Person
RuralBTUPerCapUsed = (
    RuralBTUPerCapElecUsed + RuralBTUPerCapNGUsed + RuralBTUPerCapFOKerUsed + RuralBTUPerCapLPGUsed
)  # BTU/Person

urban_per_res_elec_used = UrbanBTUPerCapElecUsed / UrbanBTUPerCapUsed * 100
suburban_per_res_elec_used = SuburbanBTUPerCapElecUsed / SuburbanBTUPerCapUsed * 100
rural_per_res_elec_used = RuralBTUPerCapElecUsed / RuralBTUPerCapUsed * 100

UrbanPerResNGUsed = UrbanBTUPerCapNGUsed / UrbanBTUPerCapUsed * 100
SuburbanPerResNGUsed = SuburbanBTUPerCapNGUsed / SuburbanBTUPerCapUsed * 100
RuralPerResNGUsed = RuralBTUPerCapNGUsed / RuralBTUPerCapUsed * 100

UrbanPerResFOKerUsed = UrbanBTUPerCapFOKerUsed / UrbanBTUPerCapUsed * 100
SuburbanPerResFOKerUsed = SuburbanBTUPerCapFOKerUsed / SuburbanBTUPerCapUsed * 100
RuralPerResFOKerUsed = RuralBTUPerCapFOKerUsed / RuralBTUPerCapUsed * 100

UrbanPerResLPGUsed = UrbanBTUPerCapLPGUsed / UrbanBTUPerCapUsed * 100
SuburbanPerResLPGUsed = SuburbanBTUPerCapLPGUsed / SuburbanBTUPerCapUsed * 100
RuralPerResLPGUsed = RuralBTUPerCapLPGUsed / RuralBTUPerCapUsed * 100

UrbanMinPerResElectrification = UrbanBTUPerCapElecOtherUsed / UrbanBTUPerCapUsed * 100
UrbanPerResFossilFuelUsed2015 = UrbanPerResNGUsed + UrbanPerResFOKerUsed + UrbanPerResLPGUsed
UrbanPerResFFNGUsed = UrbanPerResNGUsed / UrbanPerResFossilFuelUsed2015 * 100
UrbanPerResFFFOKerUsed = UrbanPerResFOKerUsed / UrbanPerResFossilFuelUsed2015 * 100
UrbanPerResFFLPGUsed = UrbanPerResLPGUsed / UrbanPerResFossilFuelUsed2015 * 100

UrbanBTUPerCapElecHeatingUsed = (
    UrbanBTUPerCapElecSpaceHeatingUsed + UrbanBTUPerCapElecWaterHeatingUsed
)
UrbanPerElecHeatingUsedforSpaceHeating = (
    UrbanBTUPerCapElecSpaceHeatingUsed / UrbanBTUPerCapElecHeatingUsed * 100
)
UrbanPerElecHeatingUsedforWaterHeating = (
    UrbanBTUPerCapElecWaterHeatingUsed / UrbanBTUPerCapElecHeatingUsed * 100
)

UrbanBTUPerCapFFSpaceHeatingUsed = (
    UrbanBTUPerCapNGSpaceHeatingUsed
    + UrbanBTUPerCapFOKerSpaceHeatingUsed
    + UrbanBTUPerCapLPGSpaceHeatingUsed
)
UrbanPerResFFSpaceHeatingNGUsed = (
    UrbanBTUPerCapNGSpaceHeatingUsed / UrbanBTUPerCapFFSpaceHeatingUsed * 100
)
UrbanPerResFFSpaceHeatingFOKerUsed = (
    UrbanBTUPerCapFOKerSpaceHeatingUsed / UrbanBTUPerCapFFSpaceHeatingUsed * 100
)
UrbanPerResFFSpaceHeatingLPGUsed = (
    UrbanBTUPerCapLPGSpaceHeatingUsed / UrbanBTUPerCapFFSpaceHeatingUsed * 100
)

UrbanBTUPerCapFFWaterHeatingUsed = (
    UrbanBTUPerCapNGWaterHeatingUsed
    + UrbanBTUPerCapFOKerWaterHeatingUsed
    + UrbanBTUPerCapLPGWaterHeatingUsed
)
UrbanPerResFFWaterHeatingNGUsed = (
    UrbanBTUPerCapNGWaterHeatingUsed / UrbanBTUPerCapFFWaterHeatingUsed * 100
)
UrbanPerResFFWaterHeatingFOKerUsed = (
    UrbanBTUPerCapFOKerWaterHeatingUsed / UrbanBTUPerCapFFWaterHeatingUsed * 100
)
UrbanPerResFFWaterHeatingLPGUsed = (
    UrbanBTUPerCapLPGWaterHeatingUsed / UrbanBTUPerCapFFWaterHeatingUsed * 100
)

SuburbanMinPerResElectrification = SuburbanBTUPerCapElecOtherUsed / SuburbanBTUPerCapUsed * 100
SuburbanPerResFossilFuelUsed2015 = (
    SuburbanPerResNGUsed + SuburbanPerResFOKerUsed + SuburbanPerResLPGUsed
)
SuburbanPerResFFNGUsed = SuburbanPerResNGUsed / SuburbanPerResFossilFuelUsed2015 * 100
SuburbanPerResFFFOKerUsed = SuburbanPerResFOKerUsed / SuburbanPerResFossilFuelUsed2015 * 100
SuburbanPerResFFLPGUsed = SuburbanPerResLPGUsed / SuburbanPerResFossilFuelUsed2015 * 100

SuburbanBTUPerCapElecHeatingUsed = (
    SuburbanBTUPerCapElecSpaceHeatingUsed + SuburbanBTUPerCapElecWaterHeatingUsed
)
SuburbanPerElecHeatingUsedforSpaceHeating = (
    SuburbanBTUPerCapElecSpaceHeatingUsed / SuburbanBTUPerCapElecHeatingUsed * 100
)
SuburbanPerElecHeatingUsedforWaterHeating = (
    SuburbanBTUPerCapElecWaterHeatingUsed / SuburbanBTUPerCapElecHeatingUsed * 100
)

SuburbanBTUPerCapFFSpaceHeatingUsed = (
    SuburbanBTUPerCapNGSpaceHeatingUsed
    + SuburbanBTUPerCapFOKerSpaceHeatingUsed
    + SuburbanBTUPerCapLPGSpaceHeatingUsed
)
SuburbanPerResFFSpaceHeatingNGUsed = (
    SuburbanBTUPerCapNGSpaceHeatingUsed / SuburbanBTUPerCapFFSpaceHeatingUsed * 100
)
SuburbanPerResFFSpaceHeatingFOKerUsed = (
    SuburbanBTUPerCapFOKerSpaceHeatingUsed / SuburbanBTUPerCapFFSpaceHeatingUsed * 100
)
SuburbanPerResFFSpaceHeatingLPGUsed = (
    SuburbanBTUPerCapLPGSpaceHeatingUsed / SuburbanBTUPerCapFFSpaceHeatingUsed * 100
)

SuburbanBTUPerCapFFWaterHeatingUsed = (
    SuburbanBTUPerCapNGWaterHeatingUsed
    + SuburbanBTUPerCapFOKerWaterHeatingUsed
    + SuburbanBTUPerCapLPGWaterHeatingUsed
)
SuburbanPerResFFWaterHeatingNGUsed = (
    SuburbanBTUPerCapNGWaterHeatingUsed / SuburbanBTUPerCapFFWaterHeatingUsed * 100
)
SuburbanPerResFFWaterHeatingFOKerUsed = (
    SuburbanBTUPerCapFOKerWaterHeatingUsed / SuburbanBTUPerCapFFWaterHeatingUsed * 100
)
SuburbanPerResFFWaterHeatingLPGUsed = (
    SuburbanBTUPerCapLPGWaterHeatingUsed / SuburbanBTUPerCapFFWaterHeatingUsed * 100
)

RuralMinPerResElectrification = RuralBTUPerCapElecOtherUsed / RuralBTUPerCapUsed * 100
RuralPerResFossilFuelUsed2015 = RuralPerResNGUsed + RuralPerResFOKerUsed + RuralPerResLPGUsed
RuralPerResFFNGUsed = RuralPerResNGUsed / RuralPerResFossilFuelUsed2015 * 100
RuralPerResFFFOKerUsed = RuralPerResFOKerUsed / RuralPerResFossilFuelUsed2015 * 100
RuralPerResFFLPGUsed = RuralPerResLPGUsed / RuralPerResFossilFuelUsed2015 * 100

RuralBTUPerCapElecHeatingUsed = (
    RuralBTUPerCapElecSpaceHeatingUsed + RuralBTUPerCapElecWaterHeatingUsed
)
RuralPerElecHeatingUsedforSpaceHeating = (
    RuralBTUPerCapElecSpaceHeatingUsed / RuralBTUPerCapElecHeatingUsed * 100
)
RuralPerElecHeatingUsedforWaterHeating = (
    RuralBTUPerCapElecWaterHeatingUsed / RuralBTUPerCapElecHeatingUsed * 100
)

RuralBTUPerCapFFSpaceHeatingUsed = (
    RuralBTUPerCapNGSpaceHeatingUsed
    + RuralBTUPerCapFOKerSpaceHeatingUsed
    + RuralBTUPerCapLPGSpaceHeatingUsed
)
RuralPerResFFSpaceHeatingNGUsed = (
    RuralBTUPerCapNGSpaceHeatingUsed / RuralBTUPerCapFFSpaceHeatingUsed * 100
)
RuralPerResFFSpaceHeatingFOKerUsed = (
    RuralBTUPerCapFOKerSpaceHeatingUsed / RuralBTUPerCapFFSpaceHeatingUsed * 100
)
RuralPerResFFSpaceHeatingLPGUsed = (
    RuralBTUPerCapLPGSpaceHeatingUsed / RuralBTUPerCapFFSpaceHeatingUsed * 100
)

RuralBTUPerCapFFWaterHeatingUsed = (
    RuralBTUPerCapNGWaterHeatingUsed
    + RuralBTUPerCapFOKerWaterHeatingUsed
    + RuralBTUPerCapLPGWaterHeatingUsed
)
RuralPerResFFWaterHeatingNGUsed = (
    RuralBTUPerCapNGWaterHeatingUsed / RuralBTUPerCapFFWaterHeatingUsed * 100
)
RuralPerResFFWaterHeatingFOKerUsed = (
    RuralBTUPerCapFOKerWaterHeatingUsed / RuralBTUPerCapFFWaterHeatingUsed * 100
)
RuralPerResFFWaterHeatingLPGUsed = (
    RuralBTUPerCapLPGWaterHeatingUsed / RuralBTUPerCapFFWaterHeatingUsed * 100
)

urban_per_res_electrification = UrbanMinPerResElectrification
suburban_per_res_electrification = SuburbanMinPerResElectrification
rural_per_res_electrification = RuralMinPerResElectrification

# Commercial/Industrial Stationary Energy from 2015 Inventory
PerEnergyToUseComIndElec = 100
PerEnergyToUseComIndNG = 75  # https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
PerEnergyToUseComIndCoal = (
    85  # https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
)
PerEnergyToUseComIndDFO = 80  # https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
PerEnergyToUseComIndKer = (
    80  # oil derivative #https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
)
PerEnergyToUseComIndLPG = (
    80  # oil derivative #https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
)
PerEnergyToUseComIndMotGas = (
    80  # oil derivative  #https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
)
PerEnergyToUseComIndRFO = 80  # https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
PerEnergyToUseComIndPetCoke = (
    80  # oil derivative #https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
)
PerEnergyToUseComIndStillGas = (
    80  # oil derivative #https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
)
PerEnergyToUseComIndSpecialNaphthas = (
    80  # oil derivative #https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf
)
PerComIndEnergyUse = 0

ComIndElecBBtu = 119120.51
ComIndNGBBtu = 145987.03
ComIndCoalBBtu = 6581.08
ComIndDFOBBtu = 24342.05
ComIndKerBBtu = 41.91
ComIndLPGBBtu = 2581.22
ComIndMotGasBBtu = 12584.78
ComIndRFOBBtu = 261.42
ComIndPetCokeBBtu = 15067.33
ComIndStillGasBBtu = 25628.52
ComIndSpecialNaphthasBBtu = 73.71

ComIndElecBBtuUsed = ComIndElecBBtu * PerEnergyToUseComIndElec / 100
ComIndNGBBtuUsed = ComIndNGBBtu * PerEnergyToUseComIndNG / 100
ComIndCoalBBtuUsed = ComIndCoalBBtu * PerEnergyToUseComIndCoal / 100
ComIndDFOBBtuUsed = ComIndDFOBBtu * PerEnergyToUseComIndDFO / 100
ComIndKerBBtuUsed = ComIndKerBBtu * PerEnergyToUseComIndKer / 100
ComIndLPGBBtuUsed = ComIndLPGBBtu * PerEnergyToUseComIndLPG / 100
ComIndMotGasBBtuUsed = ComIndMotGasBBtu * PerEnergyToUseComIndMotGas / 100
ComIndRFOBBtuUsed = ComIndRFOBBtu * PerEnergyToUseComIndRFO / 100
ComIndPetCokeBBtuUsed = ComIndPetCokeBBtu * PerEnergyToUseComIndPetCoke / 100
ComIndStillGasBBtuUsed = ComIndStillGasBBtu * PerEnergyToUseComIndStillGas / 100
ComIndSpecialNaphthasBBtuUsed = (
    ComIndSpecialNaphthasBBtu * PerEnergyToUseComIndSpecialNaphthas / 100
)

ComIndBBtuUsed = (
    ComIndElecBBtuUsed
    + ComIndNGBBtuUsed
    + ComIndCoalBBtuUsed
    + ComIndDFOBBtuUsed
    + ComIndKerBBtuUsed
    + ComIndLPGBBtuUsed
    + ComIndMotGasBBtuUsed
    + ComIndRFOBBtuUsed
    + ComIndPetCokeBBtuUsed
    + ComIndStillGasBBtuUsed
    + ComIndSpecialNaphthasBBtuUsed
)

ComIndPerElecUsed = ComIndElecBBtuUsed / ComIndBBtuUsed * 100
ComIndPerNGUsed = ComIndNGBBtuUsed / ComIndBBtuUsed * 100
ComIndPerCoalUsed = ComIndCoalBBtuUsed / ComIndBBtuUsed * 100
ComIndPerDFOUsed = ComIndDFOBBtuUsed / ComIndBBtuUsed * 100
ComIndPerKerUsed = ComIndKerBBtuUsed / ComIndBBtuUsed * 100
ComIndPerLPGUsed = ComIndLPGBBtuUsed / ComIndBBtuUsed * 100
ComIndPerMotGasUsed = ComIndMotGasBBtuUsed / ComIndBBtuUsed * 100
ComIndPerRFOUsed = ComIndRFOBBtuUsed / ComIndBBtuUsed * 100
ComIndPerPetCokeUsed = ComIndPetCokeBBtuUsed / ComIndBBtuUsed * 100
ComIndPerStillGasUsed = ComIndStillGasBBtuUsed / ComIndBBtuUsed * 100
ComIndPerSpecialNaphthasUsed = ComIndSpecialNaphthasBBtuUsed / ComIndBBtuUsed * 100

ComIndPerFossilFuelUsed2015 = 100 - ComIndPerElecUsed
ComIndPerFFNGUsed = ComIndPerNGUsed / ComIndPerFossilFuelUsed2015 * 100
ComIndPerFFCoalUsed = ComIndPerCoalUsed / ComIndPerFossilFuelUsed2015 * 100
ComIndPerFFDFOUsed = ComIndPerDFOUsed / ComIndPerFossilFuelUsed2015 * 100
ComIndPerFFKerUsed = ComIndPerKerUsed / ComIndPerFossilFuelUsed2015 * 100
ComIndPerFFLPGUsed = ComIndPerLPGUsed / ComIndPerFossilFuelUsed2015 * 100
ComIndPerFFMotGasUsed = ComIndPerMotGasUsed / ComIndPerFossilFuelUsed2015 * 100
ComIndPerFFRFOUsed = ComIndPerRFOUsed / ComIndPerFossilFuelUsed2015 * 100
ComIndPerFFPetCokeUsed = ComIndPerPetCokeUsed / ComIndPerFossilFuelUsed2015 * 100
ComIndPerFFStillGasUsed = ComIndPerStillGasUsed / ComIndPerFossilFuelUsed2015 * 100
ComIndPerFFSpecialNaphthasUsed = ComIndPerSpecialNaphthasUsed / ComIndPerFossilFuelUsed2015 * 100

ComIndMinPerElectrification = ComIndPerElecUsed
ComIndPerElectrification = ComIndMinPerElectrification

# Mobile-Highway GHG Factors
UrbanVMTperPop = 5041.95
SuburbanVMTperPop = 7405.38
RuralVMTperPop = 6591.47
VMTperCap = 0

PerEVMT = 0  # % VMT from PEVs
EVEff = 0.3  # kWh/mile

RegionalFleetMPG = 19.744607425  # mpg imputed from 2015 inventory
CO2eperGallonGasoline = (
    20.50758459351  # lbs co2e per gallon of gasoline (imputed from 2015 inventory)
)

# Mobile-Aviation GHG Factors
PerAviation = 0

# Mobile-Rail Transit GHG Factors
PerTransRailRidership = 0
TransRailBBtuPerThBarrelDiesel = 5.768
TransRailMTCO2ePerBBtuDiesel = 74.66024683
PerEnergyToMotionRailDiesel = 35  # https://www.eesi.org/articles/view/electrification-of-u.s.-railways-pie-in-the-sky-or-realistic-goal
PerEnergyToMotionRailElec = 95  # https://www.eesi.org/articles/view/electrification-of-u.s.-railways-pie-in-the-sky-or-realistic-goal

TransRailUrbanPerCapElec = 115.85  # kWh/person
TransRailSuburbanPerCapElec = 66.10  # kWh/person
TransRailRuralPerCapElec = 21.37  # kWh/person

TransRailUrbanBTUPerCapElec = TransRailUrbanPerCapElec * BTU_KWH  # BTU/Person
TransRailSuburbanBTUPerCapElec = TransRailSuburbanPerCapElec * BTU_KWH  # BTU/Person
TransRailRuralBTUPerCapElec = TransRailRuralPerCapElec * BTU_KWH  # BTU/Person

TransRailUrbanPerCapDiesel = 0.1995  # gallons/person
TransRailSuburbanPerCapDiesel = 0.1138  # gallons/person
TransRailRuralPerCapDiesel = 0.0368  # gallons/person

TransRailUrbanBTUPerCapDiesel = (
    TransRailUrbanPerCapDiesel * KB_G * TransRailBBtuPerThBarrelDiesel * 1000000000
)  # BTU/Person
TransRailSuburbanBTUPerCapDiesel = (
    TransRailSuburbanPerCapDiesel * KB_G * TransRailBBtuPerThBarrelDiesel * 1000000000
)  # BTU/Person
TransRailRuralBTUPerCapDiesel = (
    TransRailRuralPerCapDiesel * KB_G * TransRailBBtuPerThBarrelDiesel * 1000000000
)  # BTU/Person

TransRailUrbanBTUPerCapElecMotion = TransRailUrbanBTUPerCapElec * PerEnergyToMotionRailElec / 100
TransRailSuburbanBTUPerCapElecMotion = (
    TransRailSuburbanBTUPerCapElec * PerEnergyToMotionRailElec / 100
)
TransRailRuralBTUPerCapElecMotion = TransRailRuralBTUPerCapElec * PerEnergyToMotionRailElec / 100

TransRailUrbanBTUPerCapDieselMotion = (
    TransRailUrbanBTUPerCapDiesel * PerEnergyToMotionRailDiesel / 100
)
TransRailSuburbanBTUPerCapDieselMotion = (
    TransRailSuburbanBTUPerCapDiesel * PerEnergyToMotionRailDiesel / 100
)
TransRailRuralBTUPerCapDieselMotion = (
    TransRailRuralBTUPerCapDiesel * PerEnergyToMotionRailDiesel / 100
)

TransRailUrbanBTUPerCapMotion = (
    TransRailUrbanBTUPerCapElecMotion + TransRailUrbanBTUPerCapDieselMotion
)
TransRailSuburbanBTUPerCapMotion = (
    TransRailSuburbanBTUPerCapElecMotion + TransRailSuburbanBTUPerCapDieselMotion
)
TransRailRuralBTUPerCapMotion = (
    TransRailRuralBTUPerCapElecMotion + TransRailRuralBTUPerCapDieselMotion
)

TransRailUrbanPerElecMotion = (
    TransRailUrbanBTUPerCapElecMotion / TransRailUrbanBTUPerCapMotion * 100
)
TransRailSuburbanPerElecMotion = (
    TransRailSuburbanBTUPerCapElecMotion / TransRailSuburbanBTUPerCapMotion * 100
)
TransRailRuralPerElecMotion = (
    TransRailRuralBTUPerCapElecMotion / TransRailRuralBTUPerCapMotion * 100
)

TransRailRuralPerElecMotion = TransRailRuralPerElecMotion

# Mobile-Other GHG Factors

# Freight Rail
PerFreightRail = 0
FreightRailElecBBtu = 0
FreightRailDieselBBtu = 3525.18
FreightRailElecBBtuMotion = FreightRailElecBBtu * PerEnergyToMotionRailElec / 100
FreightRailDieselBBtuMotion = FreightRailDieselBBtu * PerEnergyToMotionRailDiesel / 100
FreightRailBBtuMotion = FreightRailElecBBtuMotion + FreightRailDieselBBtuMotion
FreightRailPerElecMotion = FreightRailElecBBtuMotion / FreightRailBBtuMotion * 100
FreightRailMTCO2ePerBBtuDiesel = 74.5937203

# InterCity Rail
PerInterCityRail = 0
InterCityRailElecBBtu = 319.07
InterCityRailDieselBBtu = 24.93
InterCityRailElecBBtuMotion = InterCityRailElecBBtu * PerEnergyToMotionRailElec / 100
InterCityRailDieselBBtuMotion = InterCityRailDieselBBtu * PerEnergyToMotionRailDiesel / 100
InterCityRailBBtuMotion = InterCityRailElecBBtuMotion + InterCityRailDieselBBtuMotion
InterCityRailPerElecMotion = InterCityRailElecBBtuMotion / InterCityRailBBtuMotion * 100
InterCityRailPerElectrification = InterCityRailPerElecMotion
InterCityRailMTCO2ePerBBtuDiesel = 73.978

# Marine and Port
PerEnergyToMotionMarineElec = 100
PerEnergyToMotionMarineRFO = 50  # Calculation of Efficiencies of a Ship Power Plant Operating with Waste Heat Recovery through Combined Heat and Power Production by Mirko Grljušić 1,2,*, Vladimir Medica 3,† and Gojmir Radica 1,†
PerEnergyToMotionMarineDFO = 50  # Calculation of Efficiencies of a Ship Power Plant Operating with Waste Heat Recovery through Combined Heat and Power Production by Mirko Grljušić 1,2,*, Vladimir Medica 3,† and Gojmir Radica 1,†
PerMarinePort = 0
MarinePortElecBBtu = 0
MarinePortRFOBBtu = 2221.436
MarinePortDFOBBtu = 1855.010
MarinePortElecBBtuMotion = MarinePortElecBBtu * PerEnergyToMotionMarineElec / 100
MarinePortRFOBBtuMotion = MarinePortRFOBBtu * PerEnergyToMotionMarineRFO / 100
MarinePortDFOBBtuMotion = MarinePortDFOBBtu * PerEnergyToMotionMarineDFO / 100
MarinePortBBtuMotion = MarinePortElecBBtuMotion + MarinePortRFOBBtuMotion + MarinePortDFOBBtuMotion
MarinePortPerElecMotion = MarinePortElecBBtuMotion / MarinePortBBtuMotion * 100
MarinePortPerRFOMotion = MarinePortRFOBBtuMotion / MarinePortBBtuMotion * 100
MarinePortPerDFOMotion = MarinePortDFOBBtuMotion / MarinePortBBtuMotion * 100
MarinePortMTCO2ePerBBtuRFO = 75.732
MarinePortMTCO2ePerBBtuDFO = 74.581
MarinePortPerFossilFuelMotion2015 = 100 - MarinePortPerElecMotion
MarinePortPerFFRFOMotion = MarinePortPerRFOMotion / MarinePortPerFossilFuelMotion2015 * 100
MarinePortPerFFDFOMotion = MarinePortPerDFOMotion / MarinePortPerFossilFuelMotion2015 * 100
MarinePortMinPerElectrification = MarinePortPerElecMotion
MarinePortPerElectrification = MarinePortMinPerElectrification

# Off-Road Vehicles and Equipment
PerOffroad = 0
PerEnergyToMotionOffroadElec = 90
PerEnergyToMotionOffroadMotGas = 20
PerEnergyToMotionOffroadDFO = 20
PerEnergyToMotionOffroadLPG = 20

OffroadElecBBtu = 0
OffroadMotGasBBtu = 6041.46
OffroadDFOBBtu = 889.30
OffroadLPGBBtu = 31.67
OffroadElecBBtuMotion = OffroadElecBBtu * PerEnergyToMotionOffroadElec / 100
OffroadMotGasBBtuMotion = OffroadMotGasBBtu * PerEnergyToMotionOffroadMotGas / 100
OffroadDFOBBtuMotion = OffroadDFOBBtu * PerEnergyToMotionOffroadDFO / 100
OffroadLPGBBtuMotion = OffroadLPGBBtu * PerEnergyToMotionOffroadLPG / 100
OffroadBBtuMotion = (
    OffroadElecBBtuMotion + OffroadMotGasBBtuMotion + OffroadDFOBBtuMotion + OffroadLPGBBtuMotion
)
OffroadPerElecMotion = OffroadElecBBtuMotion / OffroadBBtuMotion * 100
OffroadPerMotGasMotion = OffroadMotGasBBtuMotion / OffroadBBtuMotion * 100
OffroadPerDFOMotion = OffroadDFOBBtuMotion / OffroadBBtuMotion * 100
OffroadPerLPGMotion = OffroadLPGBBtuMotion / OffroadBBtuMotion * 100
OffroadMTCO2ePerBBtuMotGas = 74.05165922
OffroadMTCO2ePerBBtuDFO = 74.20539973
OffroadMTCO2ePerBBtuLPG = 62.05918303
OffroadPerFossilFuelMotion2015 = 100 - OffroadPerElecMotion
OffroadPerFFMotGasMotion = OffroadPerMotGasMotion / OffroadPerFossilFuelMotion2015 * 100
OffroadPerFFDFOMotion = OffroadPerDFOMotion / OffroadPerFossilFuelMotion2015 * 100
OffroadPerFFLPGMotion = OffroadPerLPGMotion / OffroadPerFossilFuelMotion2015 * 100
OffroadMinPerElectrification = OffroadPerElecMotion
OffroadPerElectrification = OffroadMinPerElectrification

# Initial Non-Energy GHG Factors
PerAg = 0
PerWaste = 0
PerWasteWater = 0
PerIP = 0
PerUrbanTreeCoverage = 0
PerForestCoverage = 0

# create dictionary of all variables that user can change, to pass to functions that create charts
user_inputs = {
    "ComIndPerElectrification": ComIndPerElectrification,
    "FreightRailPerElecMotion": FreightRailPerElecMotion,
    "grid_coal": grid_coal,
    "grid_oil": grid_oil,
    "grid_ng": grid_ng,
    "grid_nuclear": grid_nuclear,
    "grid_solar": grid_solar,
    "grid_wind": grid_wind,
    "grid_bio": grid_bio,
    "grid_hydro": grid_hydro,
    "grid_geo": grid_geo,
    "grid_other_ff": grid_other_ff,
    "InterCityRailPerElecMotion": InterCityRailPerElecMotion,
    "MarinePortPerElectrification": MarinePortPerElectrification,
    "OffroadPerElectrification": OffroadPerElectrification,
    "PerAg": PerAg,
    "PerAviation": PerAviation,
    "res_energy_change": res_energy_change,
    "ff_carbon_capture": ff_carbon_capture,
    "PerComIndEnergyUse": PerComIndEnergyUse,
    "PerEVMT": PerEVMT,
    "PerForestCoverage": PerForestCoverage,
    "PerFreightRail": PerFreightRail,
    "PerInterCityRail": PerInterCityRail,
    "PerIP": PerIP,
    "PerMarinePort": PerMarinePort,
    "PerOffroad": PerOffroad,
    "PerTransRailRidership": PerTransRailRidership,
    "PerUrbanTreeCoverage": PerUrbanTreeCoverage,
    "PerWaste": PerWaste,
    "PerWasteWater": PerWasteWater,
    "pop_factor": pop_factor,
    "RegionalFleetMPG": RegionalFleetMPG,
    "rural_per_res_electrification": rural_per_res_electrification,
    "rural_pop_percent": rural_pop_percent,
    "suburban_per_res_electrification": suburban_per_res_electrification,
    "suburban_pop_percent": suburban_pop_percent,
    "TransRailRuralPerElecMotion": TransRailRuralPerElecMotion,
    "TransRailSuburbanPerElecMotion": TransRailSuburbanPerElecMotion,
    "TransRailUrbanPerElecMotion": TransRailUrbanPerElecMotion,
    "urban_per_res_electrification": urban_per_res_electrification,
    "urban_pop_percent": urban_pop_percent,
    "VMTperCap": VMTperCap,
}


def calc_res_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    res_energy_change,
    pop_factor,
    rural_per_res_electrification,
    suburban_per_res_electrification,
    urban_per_res_electrification,
    rural_pop_percent,
    suburban_pop_percent,
    urban_pop_percent,
):
    """
    Determine BTU of energy by sub-sector (urban, suburban, rural) and from that calculate
    ghg emissions.
    """

    def btu_used(
        POP, pop_factor, subsector_pop_percent, subsector_btu_per_cap_used, per_cap_res_energy_use
    ):
        return (
            POP
            * (1 + pop_factor / 100)
            * (subsector_pop_percent / 100)
            * subsector_btu_per_cap_used
            * (1 + per_cap_res_energy_use / 100)
        )

    def calc_elec_BTU(
        PerChangedFossilFuelUsed,
        ElecSpaceHeatingBTUUsed,
        RES_ELEC_SPACE_USEFUL,
        ElecWaterHeatingBTUUsed,
        RES_ELEC_WATER_USEFUL,
        ElecOtherBTUUsed,
        RES_ELEC_OTHER_USEFUL,
        NGSpaceHeatingToElecBTUUsed,
        FOKerSpaceHeatingToElecBTUUsed,
        LPGSpaceHeatingToElecBTUUsed,
        RES_ELEC_WATER_USEFUL_REPLACE_FF,
        NGWaterHeatingToElecBTUUsed,
        FOKerWaterHeatingToElecBTUUsed,
        LPGWaterHeatingToElecBTUUsed,
        RES_ELEC_OTHER_USEFUL_REPLACE_FF,
        NGOtherToElecBTUUsed,
        FOKerOtherToElecBTUUsed,
        LPGOtherToElecBTUUsed,
        ElecToNGSpaceHeatingBTUUsed,
        ElecToFOKerSpaceHeatingBTUUsed,
        ElecToLPGSpaceHeatingBTUUsed,
        ElecToNGWaterHeatingBTUUsed,
        ElecToFOKerWaterHeatingBTUUsed,
        ElecToLPGWaterHeatingBTUUsed,
    ):
        if PerChangedFossilFuelUsed >= 0:
            return (
                (ElecSpaceHeatingBTUUsed / RES_ELEC_SPACE_USEFUL)
                + (ElecWaterHeatingBTUUsed / RES_ELEC_WATER_USEFUL)
                + (ElecOtherBTUUsed / RES_ELEC_OTHER_USEFUL)
                + (
                    (
                        NGSpaceHeatingToElecBTUUsed
                        + FOKerSpaceHeatingToElecBTUUsed
                        + LPGSpaceHeatingToElecBTUUsed
                    )
                    / RES_ELEC_WATER_USEFUL_REPLACE_FF
                )
                + (
                    (
                        NGWaterHeatingToElecBTUUsed
                        + FOKerWaterHeatingToElecBTUUsed
                        + LPGWaterHeatingToElecBTUUsed
                    )
                    / RES_ELEC_OTHER_USEFUL_REPLACE_FF
                )
                + (
                    (NGOtherToElecBTUUsed + FOKerOtherToElecBTUUsed + LPGOtherToElecBTUUsed)
                    / RES_ELEC_OTHER_USEFUL
                )
            )
        return (
            (ElecOtherBTUUsed / RES_ELEC_OTHER_USEFUL)
            + (
                (
                    ElecSpaceHeatingBTUUsed
                    - (
                        ElecToNGSpaceHeatingBTUUsed
                        + ElecToFOKerSpaceHeatingBTUUsed
                        + ElecToLPGSpaceHeatingBTUUsed
                    )
                )
                / RES_ELEC_SPACE_USEFUL
            )
            + (
                (
                    ElecWaterHeatingBTUUsed
                    - (
                        ElecToNGWaterHeatingBTUUsed
                        + ElecToFOKerWaterHeatingBTUUsed
                        + ElecToLPGWaterHeatingBTUUsed
                    )
                )
                / RES_ELEC_WATER_USEFUL
            )
        )

    def calc_ng_btu(
        PerChangedFossilFuelUsed,
        NGSpaceHeatingBTUUsed,
        NGSpaceHeatingToElecBTUUsed,
        RES_NG_SPACE_USEFUL,
        NGWaterHeatingBTUUsed,
        NGWaterHeatingToElecBTUUsed,
        RES_NG_WATER_USEFUL,
        NGOtherBTUUsed,
        NGOtherToElecBTUUsed,
        RES_NG_OTHER_USEFUL,
        ElecToNGSpaceHeatingBTUUsed,
        ElecToNGWaterHeatingBTUUsed,
    ):
        if PerChangedFossilFuelUsed >= 0:
            return (
                ((NGSpaceHeatingBTUUsed - NGSpaceHeatingToElecBTUUsed) / RES_NG_SPACE_USEFUL)
                + ((NGWaterHeatingBTUUsed - NGWaterHeatingToElecBTUUsed) / RES_NG_WATER_USEFUL)
                + ((NGOtherBTUUsed - NGOtherToElecBTUUsed) / RES_NG_OTHER_USEFUL)
            )
        return (
            (NGOtherBTUUsed / RES_NG_OTHER_USEFUL)
            + ((NGSpaceHeatingBTUUsed + ElecToNGSpaceHeatingBTUUsed) / RES_NG_SPACE_USEFUL)
            + ((NGWaterHeatingBTUUsed + ElecToNGWaterHeatingBTUUsed) / RES_NG_WATER_USEFUL)
        )

    def calc_fok_btu(
        PerChangedFossilFuelUsed,
        FOKerSpaceHeatingBTUUsed,
        FOKerSpaceHeatingToElecBTUUsed,
        RES_FOK_SPACE_USEFUL,
        FOKerWaterHeatingBTUUsed,
        FOKerWaterHeatingToElecBTUUsed,
        RES_FOK_WATER_USEFUL,
        FOKerOtherBTUUsed,
        FOKerOtherToElecBTUUsed,
        RES_FOK_OTHER_USEFUL,
        ElecToFOKerSpaceHeatingBTUUsed,
        ElecToFOKerWaterHeatingBTUUsed,
    ):
        if PerChangedFossilFuelUsed >= 0:
            return (
                ((FOKerSpaceHeatingBTUUsed - FOKerSpaceHeatingToElecBTUUsed) / RES_FOK_SPACE_USEFUL)
                + (
                    (FOKerWaterHeatingBTUUsed - FOKerWaterHeatingToElecBTUUsed)
                    / RES_FOK_WATER_USEFUL
                )
                + ((FOKerOtherBTUUsed - FOKerOtherToElecBTUUsed) / RES_FOK_OTHER_USEFUL)
            )
        return (
            (FOKerOtherBTUUsed / RES_FOK_OTHER_USEFUL)
            + ((FOKerSpaceHeatingBTUUsed + ElecToFOKerSpaceHeatingBTUUsed) / RES_FOK_SPACE_USEFUL)
            + ((FOKerWaterHeatingBTUUsed + ElecToFOKerWaterHeatingBTUUsed) / RES_FOK_WATER_USEFUL)
        )

    def calc_lpg_btu(
        PerChangedFossilFuelUsed,
        LPGSpaceHeatingBTUUsed,
        LPGSpaceHeatingToElecBTUUsed,
        RES_LPG_SPACE_USEFUL,
        LPGWaterHeatingBTUUsed,
        LPGWaterHeatingToElecBTUUsed,
        RES_LPG_WATER_USEFUL,
        LPGOtherBTUUsed,
        LPGOtherToElecBTUUsed,
        RES_LPG_OTHER_USEFUL,
        ElecToLPGSpaceHeatingBTUUsed,
        ElecToLPGWaterHeatingBTUUsed,
    ):
        if PerChangedFossilFuelUsed >= 0:
            return (
                ((LPGSpaceHeatingBTUUsed - LPGSpaceHeatingToElecBTUUsed) / RES_LPG_SPACE_USEFUL)
                + ((LPGWaterHeatingBTUUsed - LPGWaterHeatingToElecBTUUsed) / RES_LPG_WATER_USEFUL)
                + ((LPGOtherBTUUsed - LPGOtherToElecBTUUsed) / RES_LPG_OTHER_USEFUL)
            )
        return (
            (LPGOtherBTUUsed / RES_LPG_OTHER_USEFUL)
            + ((LPGSpaceHeatingBTUUsed + ElecToLPGSpaceHeatingBTUUsed) / RES_LPG_SPACE_USEFUL)
            + ((LPGWaterHeatingBTUUsed + ElecToLPGWaterHeatingBTUUsed) / RES_LPG_WATER_USEFUL)
        )

    urban_res_btu_used = btu_used(
        POP, pop_factor, urban_pop_percent, UrbanBTUPerCapUsed, res_energy_change
    )

    UrbanPerChangedFossilFuelUsed = urban_per_res_electrification - urban_per_res_elec_used
    urban_res_elec_used_to_FF_heating = urban_per_res_elec_used - urban_per_res_electrification

    UrbanResElecBTUUsed = urban_res_btu_used * (urban_per_res_elec_used / 100)
    UrbanResElecSpaceHeatingBTUUsed = UrbanResElecBTUUsed * (
        PerUrbanElecBTUPerCapUsedSpaceHeating / 100
    )
    UrbanResElecWaterHeatingBTUUsed = UrbanResElecBTUUsed * (
        PerUrbanElecBTUPerCapUsedWaterHeating / 100
    )
    UrbanResElecOtherBTUUsed = UrbanResElecBTUUsed * (PerUrbanElecBTUPerCapUsedOther / 100)

    UrbanResNGBTUUsed = urban_res_btu_used * (UrbanPerResNGUsed / 100)
    UrbanResNGSpaceHeatingBTUUsed = UrbanResNGBTUUsed * (PerUrbanNGBTUPerCapUsedSpaceHeating / 100)
    UrbanResNGWaterHeatingBTUUsed = UrbanResNGBTUUsed * (PerUrbanNGBTUPerCapUsedWaterHeating / 100)
    UrbanResNGOtherBTUUsed = UrbanResNGBTUUsed * (PerUrbanNGBTUPerCapUsedOther / 100)

    UrbanResFOKerBTUUsed = urban_res_btu_used * (UrbanPerResFOKerUsed / 100)
    UrbanResFOKerSpaceHeatingBTUUsed = UrbanResFOKerBTUUsed * (
        PerUrbanFOKerBTUPerCapUsedSpaceHeating / 100
    )
    UrbanResFOKerWaterHeatingBTUUsed = UrbanResFOKerBTUUsed * (
        PerUrbanFOKerBTUPerCapUsedWaterHeating / 100
    )
    UrbanResFOKerOtherBTUUsed = UrbanResFOKerBTUUsed * (PerUrbanFOKerBTUPerCapUsedOther / 100)

    UrbanResLPGBTUUsed = urban_res_btu_used * (UrbanPerResLPGUsed / 100)
    UrbanResLPGSpaceHeatingBTUUsed = UrbanResLPGBTUUsed * (
        PerUrbanLPGBTUPerCapUsedSpaceHeating / 100
    )
    UrbanResLPGWaterHeatingBTUUsed = UrbanResLPGBTUUsed * (
        PerUrbanLPGBTUPerCapUsedWaterHeating / 100
    )
    UrbanResLPGOtherBTUUsed = UrbanResLPGBTUUsed * (PerUrbanLPGBTUPerCapUsedOther / 100)

    # Fuel Switch to Electric
    UrbanResNGSpaceHeatingToElecBTUUsed = (
        urban_res_btu_used
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFNGUsed / 100)
        * (PerUrbanNGBTUPerCapUsedSpaceHeating / 100)
    )
    UrbanResNGWaterHeatingToElecBTUUsed = (
        urban_res_btu_used
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFNGUsed / 100)
        * (PerUrbanNGBTUPerCapUsedWaterHeating / 100)
    )
    UrbanResNGOtherToElecBTUUsed = (
        urban_res_btu_used
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFNGUsed / 100)
        * (PerUrbanNGBTUPerCapUsedOther / 100)
    )
    UrbanResFOKerSpaceHeatingToElecBTUUsed = (
        urban_res_btu_used
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFFOKerUsed / 100)
        * (PerUrbanFOKerBTUPerCapUsedSpaceHeating / 100)
    )
    UrbanResFOKerWaterHeatingToElecBTUUsed = (
        urban_res_btu_used
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFFOKerUsed / 100)
        * (PerUrbanFOKerBTUPerCapUsedWaterHeating / 100)
    )
    UrbanResFOKerOtherToElecBTUUsed = (
        urban_res_btu_used
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFFOKerUsed / 100)
        * (PerUrbanFOKerBTUPerCapUsedOther / 100)
    )
    UrbanResLPGSpaceHeatingToElecBTUUsed = (
        urban_res_btu_used
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFLPGUsed / 100)
        * (PerUrbanLPGBTUPerCapUsedSpaceHeating / 100)
    )
    UrbanResLPGWaterHeatingToElecBTUUsed = (
        urban_res_btu_used
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFLPGUsed / 100)
        * (PerUrbanLPGBTUPerCapUsedWaterHeating / 100)
    )
    UrbanResLPGOtherToElecBTUUsed = (
        urban_res_btu_used
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFLPGUsed / 100)
        * (PerUrbanLPGBTUPerCapUsedOther / 100)
    )

    # Fuel Switch to Fossil Fuels heating uses
    UrbanResElecToNGSpaceHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (urban_res_elec_used_to_FF_heating / 100)
        * (UrbanPerElecHeatingUsedforSpaceHeating / 100)
        * (UrbanPerResFFSpaceHeatingNGUsed / 100)
    )

    UrbanResElecToNGWaterHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (urban_res_elec_used_to_FF_heating / 100)
        * (UrbanPerElecHeatingUsedforWaterHeating / 100)
        * (UrbanPerResFFWaterHeatingNGUsed / 100)
    )

    UrbanResElecToFOKerSpaceHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (urban_res_elec_used_to_FF_heating / 100)
        * (UrbanPerElecHeatingUsedforSpaceHeating / 100)
        * (UrbanPerResFFSpaceHeatingFOKerUsed / 100)
    )

    UrbanResElecToFOKerWaterHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (urban_res_elec_used_to_FF_heating / 100)
        * (UrbanPerElecHeatingUsedforWaterHeating / 100)
        * (UrbanPerResFFWaterHeatingFOKerUsed / 100)
    )

    UrbanResElecToLPGSpaceHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (urban_res_elec_used_to_FF_heating / 100)
        * (UrbanPerElecHeatingUsedforSpaceHeating / 100)
        * (UrbanPerResFFSpaceHeatingLPGUsed / 100)
    )

    UrbanResElecToLPGWaterHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (urban_res_elec_used_to_FF_heating / 100)
        * (UrbanPerElecHeatingUsedforWaterHeating / 100)
        * (UrbanPerResFFWaterHeatingLPGUsed / 100)
    )

    # Determine whether fossil fuels (and all uses) are switched to electricity or if electricity
    # heating uses are switched to fossil fuel heating uses

    urban_elec_btu = calc_elec_BTU(
        UrbanPerChangedFossilFuelUsed,
        UrbanResElecSpaceHeatingBTUUsed,
        RES_ELEC_SPACE_USEFUL,
        UrbanResElecWaterHeatingBTUUsed,
        RES_ELEC_WATER_USEFUL,
        UrbanResElecOtherBTUUsed,
        RES_ELEC_OTHER_USEFUL,
        UrbanResNGSpaceHeatingToElecBTUUsed,
        UrbanResFOKerSpaceHeatingToElecBTUUsed,
        UrbanResLPGSpaceHeatingToElecBTUUsed,
        RES_ELEC_WATER_USEFUL_REPLACE_FF,
        UrbanResNGWaterHeatingToElecBTUUsed,
        UrbanResFOKerWaterHeatingToElecBTUUsed,
        UrbanResLPGWaterHeatingToElecBTUUsed,
        RES_ELEC_OTHER_USEFUL_REPLACE_FF,
        UrbanResNGOtherToElecBTUUsed,
        UrbanResFOKerOtherToElecBTUUsed,
        UrbanResLPGOtherToElecBTUUsed,
        UrbanResElecToNGSpaceHeatingBTUUsed,
        UrbanResElecToFOKerSpaceHeatingBTUUsed,
        UrbanResElecToLPGSpaceHeatingBTUUsed,
        UrbanResElecToNGWaterHeatingBTUUsed,
        UrbanResElecToFOKerWaterHeatingBTUUsed,
        UrbanResElecToLPGWaterHeatingBTUUsed,
    )
    urban_ng_btu = calc_ng_btu(
        UrbanPerChangedFossilFuelUsed,
        UrbanResNGSpaceHeatingBTUUsed,
        UrbanResNGSpaceHeatingToElecBTUUsed,
        RES_NG_SPACE_USEFUL,
        UrbanResNGWaterHeatingBTUUsed,
        UrbanResNGWaterHeatingToElecBTUUsed,
        RES_NG_WATER_USEFUL,
        UrbanResNGOtherBTUUsed,
        UrbanResNGOtherToElecBTUUsed,
        RES_NG_OTHER_USEFUL,
        UrbanResElecToNGSpaceHeatingBTUUsed,
        UrbanResElecToNGWaterHeatingBTUUsed,
    )
    urban_fok_btu = calc_fok_btu(
        UrbanPerChangedFossilFuelUsed,
        UrbanResFOKerSpaceHeatingBTUUsed,
        UrbanResFOKerSpaceHeatingToElecBTUUsed,
        RES_FOK_SPACE_USEFUL,
        UrbanResFOKerWaterHeatingBTUUsed,
        UrbanResFOKerWaterHeatingToElecBTUUsed,
        RES_FOK_WATER_USEFUL,
        UrbanResFOKerOtherBTUUsed,
        UrbanResFOKerOtherToElecBTUUsed,
        RES_FOK_OTHER_USEFUL,
        UrbanResElecToFOKerSpaceHeatingBTUUsed,
        UrbanResElecToFOKerWaterHeatingBTUUsed,
    )

    urban_lpg_btu = calc_lpg_btu(
        UrbanPerChangedFossilFuelUsed,
        UrbanResLPGSpaceHeatingBTUUsed,
        UrbanResLPGSpaceHeatingToElecBTUUsed,
        RES_LPG_SPACE_USEFUL,
        UrbanResLPGWaterHeatingBTUUsed,
        UrbanResLPGWaterHeatingToElecBTUUsed,
        RES_LPG_WATER_USEFUL,
        UrbanResLPGOtherBTUUsed,
        UrbanResLPGOtherToElecBTUUsed,
        RES_LPG_OTHER_USEFUL,
        UrbanResElecToLPGSpaceHeatingBTUUsed,
        UrbanResElecToLPGWaterHeatingBTUUsed,
    )

    suburban_res_btu_used = btu_used(
        POP, pop_factor, suburban_pop_percent, SuburbanBTUPerCapUsed, res_energy_change
    )

    SuburbanPerChangedFossilFuelUsed = suburban_per_res_electrification - suburban_per_res_elec_used
    suburban_per_res_elec_used_to_FF_heating = (
        suburban_per_res_elec_used - suburban_per_res_electrification
    )

    SuburbanResElecBTUUsed = suburban_res_btu_used * (suburban_per_res_elec_used / 100)
    SuburbanResElecSpaceHeatingBTUUsed = SuburbanResElecBTUUsed * (
        PerSuburbanElecBTUPerCapUsedSpaceHeating / 100
    )
    SuburbanResElecWaterHeatingBTUUsed = SuburbanResElecBTUUsed * (
        PerSuburbanElecBTUPerCapUsedWaterHeating / 100
    )
    SuburbanResElecOtherBTUUsed = SuburbanResElecBTUUsed * (PerSuburbanElecBTUPerCapUsedOther / 100)

    SuburbanResNGBTUUsed = suburban_res_btu_used * (SuburbanPerResNGUsed / 100)
    SuburbanResNGSpaceHeatingBTUUsed = SuburbanResNGBTUUsed * (
        PerSuburbanNGBTUPerCapUsedSpaceHeating / 100
    )
    SuburbanResNGWaterHeatingBTUUsed = SuburbanResNGBTUUsed * (
        PerSuburbanNGBTUPerCapUsedWaterHeating / 100
    )
    SuburbanResNGOtherBTUUsed = SuburbanResNGBTUUsed * (PerSuburbanNGBTUPerCapUsedOther / 100)

    SuburbanResFOKerBTUUsed = suburban_res_btu_used * (SuburbanPerResFOKerUsed / 100)
    SuburbanResFOKerSpaceHeatingBTUUsed = SuburbanResFOKerBTUUsed * (
        PerSuburbanFOKerBTUPerCapUsedSpaceHeating / 100
    )
    SuburbanResFOKerWaterHeatingBTUUsed = SuburbanResFOKerBTUUsed * (
        PerSuburbanFOKerBTUPerCapUsedWaterHeating / 100
    )
    SuburbanResFOKerOtherBTUUsed = SuburbanResFOKerBTUUsed * (
        PerSuburbanFOKerBTUPerCapUsedOther / 100
    )

    SuburbanResLPGBTUUsed = suburban_res_btu_used * (SuburbanPerResLPGUsed / 100)
    SuburbanResLPGSpaceHeatingBTUUsed = SuburbanResLPGBTUUsed * (
        PerSuburbanLPGBTUPerCapUsedSpaceHeating / 100
    )
    SuburbanResLPGWaterHeatingBTUUsed = SuburbanResLPGBTUUsed * (
        PerSuburbanLPGBTUPerCapUsedWaterHeating / 100
    )
    SuburbanResLPGOtherBTUUsed = SuburbanResLPGBTUUsed * (PerSuburbanLPGBTUPerCapUsedOther / 100)

    # Fuel Switch to Electric
    SuburbanResNGSpaceHeatingToElecBTUUsed = (
        suburban_res_btu_used
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFNGUsed / 100)
        * (PerSuburbanNGBTUPerCapUsedSpaceHeating / 100)
    )
    SuburbanResNGWaterHeatingToElecBTUUsed = (
        suburban_res_btu_used
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFNGUsed / 100)
        * (PerSuburbanNGBTUPerCapUsedWaterHeating / 100)
    )
    SuburbanResNGOtherToElecBTUUsed = (
        suburban_res_btu_used
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFNGUsed / 100)
        * (PerSuburbanNGBTUPerCapUsedOther / 100)
    )
    SuburbanResFOKerSpaceHeatingToElecBTUUsed = (
        suburban_res_btu_used
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFFOKerUsed / 100)
        * (PerSuburbanFOKerBTUPerCapUsedSpaceHeating / 100)
    )
    SuburbanResFOKerWaterHeatingToElecBTUUsed = (
        suburban_res_btu_used
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFFOKerUsed / 100)
        * (PerSuburbanFOKerBTUPerCapUsedWaterHeating / 100)
    )
    SuburbanResFOKerOtherToElecBTUUsed = (
        suburban_res_btu_used
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFFOKerUsed / 100)
        * (PerSuburbanFOKerBTUPerCapUsedOther / 100)
    )
    SuburbanResLPGSpaceHeatingToElecBTUUsed = (
        suburban_res_btu_used
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFLPGUsed / 100)
        * (PerSuburbanLPGBTUPerCapUsedSpaceHeating / 100)
    )
    SuburbanResLPGWaterHeatingToElecBTUUsed = (
        suburban_res_btu_used
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFLPGUsed / 100)
        * (PerSuburbanLPGBTUPerCapUsedWaterHeating / 100)
    )
    SuburbanResLPGOtherToElecBTUUsed = (
        suburban_res_btu_used
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFLPGUsed / 100)
        * (PerSuburbanLPGBTUPerCapUsedOther / 100)
    )

    # Fuel Switch to Fossil Fuels heating uses
    SuburbanResElecToNGSpaceHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * (SuburbanPerElecHeatingUsedforSpaceHeating / 100)
        * (SuburbanPerResFFSpaceHeatingNGUsed / 100)
    )

    SuburbanResElecToNGWaterHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * (SuburbanPerElecHeatingUsedforWaterHeating / 100)
        * (SuburbanPerResFFWaterHeatingNGUsed / 100)
    )

    SuburbanResElecToFOKerSpaceHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * (SuburbanPerElecHeatingUsedforSpaceHeating / 100)
        * (SuburbanPerResFFSpaceHeatingFOKerUsed / 100)
    )

    SuburbanResElecToFOKerWaterHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * (SuburbanPerElecHeatingUsedforWaterHeating / 100)
        * (SuburbanPerResFFWaterHeatingFOKerUsed / 100)
    )

    SuburbanResElecToLPGSpaceHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * (SuburbanPerElecHeatingUsedforSpaceHeating / 100)
        * (SuburbanPerResFFSpaceHeatingLPGUsed / 100)
    )

    SuburbanResElecToLPGWaterHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * (SuburbanPerElecHeatingUsedforWaterHeating / 100)
        * (SuburbanPerResFFWaterHeatingLPGUsed / 100)
    )

    # Determine whether fossil fuels (and all uses) are switched to electricity or if electricity
    # heating uses are switched to fossil fuel heating uses
    suburban_elec_btu = calc_elec_BTU(
        SuburbanPerChangedFossilFuelUsed,
        SuburbanResElecSpaceHeatingBTUUsed,
        RES_ELEC_SPACE_USEFUL,
        SuburbanResElecWaterHeatingBTUUsed,
        RES_ELEC_WATER_USEFUL,
        SuburbanResElecOtherBTUUsed,
        RES_ELEC_OTHER_USEFUL,
        SuburbanResNGSpaceHeatingToElecBTUUsed,
        SuburbanResFOKerSpaceHeatingToElecBTUUsed,
        SuburbanResLPGSpaceHeatingToElecBTUUsed,
        RES_ELEC_WATER_USEFUL_REPLACE_FF,
        SuburbanResNGWaterHeatingToElecBTUUsed,
        SuburbanResFOKerWaterHeatingToElecBTUUsed,
        SuburbanResLPGWaterHeatingToElecBTUUsed,
        RES_ELEC_OTHER_USEFUL_REPLACE_FF,
        SuburbanResNGOtherToElecBTUUsed,
        SuburbanResFOKerOtherToElecBTUUsed,
        SuburbanResLPGOtherToElecBTUUsed,
        SuburbanResElecToNGSpaceHeatingBTUUsed,
        SuburbanResElecToFOKerSpaceHeatingBTUUsed,
        SuburbanResElecToLPGSpaceHeatingBTUUsed,
        SuburbanResElecToNGWaterHeatingBTUUsed,
        SuburbanResElecToFOKerWaterHeatingBTUUsed,
        SuburbanResElecToLPGWaterHeatingBTUUsed,
    )
    suburban_ng_btu = calc_ng_btu(
        SuburbanPerChangedFossilFuelUsed,
        SuburbanResNGSpaceHeatingBTUUsed,
        SuburbanResNGSpaceHeatingToElecBTUUsed,
        RES_NG_SPACE_USEFUL,
        SuburbanResNGWaterHeatingBTUUsed,
        SuburbanResNGWaterHeatingToElecBTUUsed,
        RES_NG_WATER_USEFUL,
        SuburbanResNGOtherBTUUsed,
        SuburbanResNGOtherToElecBTUUsed,
        RES_NG_OTHER_USEFUL,
        SuburbanResElecToNGSpaceHeatingBTUUsed,
        SuburbanResElecToNGWaterHeatingBTUUsed,
    )
    suburban_fok_btu = calc_fok_btu(
        SuburbanPerChangedFossilFuelUsed,
        SuburbanResFOKerSpaceHeatingBTUUsed,
        SuburbanResFOKerSpaceHeatingToElecBTUUsed,
        RES_FOK_SPACE_USEFUL,
        SuburbanResFOKerWaterHeatingBTUUsed,
        SuburbanResFOKerWaterHeatingToElecBTUUsed,
        RES_FOK_WATER_USEFUL,
        SuburbanResFOKerOtherBTUUsed,
        SuburbanResFOKerOtherToElecBTUUsed,
        RES_FOK_OTHER_USEFUL,
        SuburbanResElecToFOKerSpaceHeatingBTUUsed,
        SuburbanResElecToFOKerWaterHeatingBTUUsed,
    )

    suburban_lpg_btu = calc_lpg_btu(
        SuburbanPerChangedFossilFuelUsed,
        SuburbanResLPGSpaceHeatingBTUUsed,
        SuburbanResLPGSpaceHeatingToElecBTUUsed,
        RES_LPG_SPACE_USEFUL,
        SuburbanResLPGWaterHeatingBTUUsed,
        SuburbanResLPGWaterHeatingToElecBTUUsed,
        RES_LPG_WATER_USEFUL,
        SuburbanResLPGOtherBTUUsed,
        SuburbanResLPGOtherToElecBTUUsed,
        RES_LPG_OTHER_USEFUL,
        SuburbanResElecToLPGSpaceHeatingBTUUsed,
        SuburbanResElecToLPGWaterHeatingBTUUsed,
    )

    rural_res_btu_used = btu_used(
        POP, pop_factor, rural_pop_percent, RuralBTUPerCapUsed, res_energy_change
    )
    RuralPerChangedFossilFuelUsed = rural_per_res_electrification - rural_per_res_elec_used
    rural_per_res_elec_used_to_FF_heating = rural_per_res_elec_used - rural_per_res_electrification

    RuralResElecBTUUsed = rural_res_btu_used * (rural_per_res_elec_used / 100)
    RuralResElecSpaceHeatingBTUUsed = RuralResElecBTUUsed * (
        PerRuralElecBTUPerCapUsedSpaceHeating / 100
    )
    RuralResElecWaterHeatingBTUUsed = RuralResElecBTUUsed * (
        PerRuralElecBTUPerCapUsedWaterHeating / 100
    )
    RuralResElecOtherBTUUsed = RuralResElecBTUUsed * (PerRuralElecBTUPerCapUsedOther / 100)

    RuralResNGBTUUsed = rural_res_btu_used * (RuralPerResNGUsed / 100)
    RuralResNGSpaceHeatingBTUUsed = RuralResNGBTUUsed * (PerRuralNGBTUPerCapUsedSpaceHeating / 100)
    RuralResNGWaterHeatingBTUUsed = RuralResNGBTUUsed * (PerRuralNGBTUPerCapUsedWaterHeating / 100)
    RuralResNGOtherBTUUsed = RuralResNGBTUUsed * (PerRuralNGBTUPerCapUsedOther / 100)

    RuralResFOKerBTUUsed = rural_res_btu_used * (RuralPerResFOKerUsed / 100)
    RuralResFOKerSpaceHeatingBTUUsed = RuralResFOKerBTUUsed * (
        PerRuralFOKerBTUPerCapUsedSpaceHeating / 100
    )
    RuralResFOKerWaterHeatingBTUUsed = RuralResFOKerBTUUsed * (
        PerRuralFOKerBTUPerCapUsedWaterHeating / 100
    )
    RuralResFOKerOtherBTUUsed = RuralResFOKerBTUUsed * (PerRuralFOKerBTUPerCapUsedOther / 100)

    RuralResLPGBTUUsed = rural_res_btu_used * (RuralPerResLPGUsed / 100)
    RuralResLPGSpaceHeatingBTUUsed = RuralResLPGBTUUsed * (
        PerRuralLPGBTUPerCapUsedSpaceHeating / 100
    )
    RuralResLPGWaterHeatingBTUUsed = RuralResLPGBTUUsed * (
        PerRuralLPGBTUPerCapUsedWaterHeating / 100
    )
    RuralResLPGOtherBTUUsed = RuralResLPGBTUUsed * (PerRuralLPGBTUPerCapUsedOther / 100)

    # Fuel Switch to Electric
    RuralResNGSpaceHeatingToElecBTUUsed = (
        rural_res_btu_used
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFNGUsed / 100)
        * (PerRuralNGBTUPerCapUsedSpaceHeating / 100)
    )
    RuralResNGWaterHeatingToElecBTUUsed = (
        rural_res_btu_used
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFNGUsed / 100)
        * (PerRuralNGBTUPerCapUsedWaterHeating / 100)
    )
    RuralResNGOtherToElecBTUUsed = (
        rural_res_btu_used
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFNGUsed / 100)
        * (PerRuralNGBTUPerCapUsedOther / 100)
    )
    RuralResFOKerSpaceHeatingToElecBTUUsed = (
        rural_res_btu_used
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFFOKerUsed / 100)
        * (PerRuralFOKerBTUPerCapUsedSpaceHeating / 100)
    )
    RuralResFOKerWaterHeatingToElecBTUUsed = (
        rural_res_btu_used
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFFOKerUsed / 100)
        * (PerRuralFOKerBTUPerCapUsedWaterHeating / 100)
    )
    RuralResFOKerOtherToElecBTUUsed = (
        rural_res_btu_used
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFFOKerUsed / 100)
        * (PerRuralFOKerBTUPerCapUsedOther / 100)
    )
    RuralResLPGSpaceHeatingToElecBTUUsed = (
        rural_res_btu_used
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFLPGUsed / 100)
        * (PerRuralLPGBTUPerCapUsedSpaceHeating / 100)
    )
    RuralResLPGWaterHeatingToElecBTUUsed = (
        rural_res_btu_used
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFLPGUsed / 100)
        * (PerRuralLPGBTUPerCapUsedWaterHeating / 100)
    )
    RuralResLPGOtherToElecBTUUsed = (
        rural_res_btu_used
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFLPGUsed / 100)
        * (PerRuralLPGBTUPerCapUsedOther / 100)
    )

    # Fuel Switch to Fossil Fuels heating uses
    RuralResElecToNGSpaceHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * (RuralPerElecHeatingUsedforSpaceHeating / 100)
        * (RuralPerResFFSpaceHeatingNGUsed / 100)
    )

    RuralResElecToNGWaterHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * (RuralPerElecHeatingUsedforWaterHeating / 100)
        * (RuralPerResFFWaterHeatingNGUsed / 100)
    )

    RuralResElecToFOKerSpaceHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * (RuralPerElecHeatingUsedforSpaceHeating / 100)
        * (RuralPerResFFSpaceHeatingFOKerUsed / 100)
    )

    RuralResElecToFOKerWaterHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * (RuralPerElecHeatingUsedforWaterHeating / 100)
        * (RuralPerResFFWaterHeatingFOKerUsed / 100)
    )

    RuralResElecToLPGSpaceHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * (RuralPerElecHeatingUsedforSpaceHeating / 100)
        * (RuralPerResFFSpaceHeatingLPGUsed / 100)
    )

    RuralResElecToLPGWaterHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * (RuralPerElecHeatingUsedforWaterHeating / 100)
        * (RuralPerResFFWaterHeatingLPGUsed / 100)
    )

    # Determine whether fossil fuels (and all uses) are switched to electricity or if electricity
    # heating uses are switched to fossil fuel heating uses

    rural_elec_btu = calc_elec_BTU(
        RuralPerChangedFossilFuelUsed,
        RuralResElecSpaceHeatingBTUUsed,
        RES_ELEC_SPACE_USEFUL,
        RuralResElecWaterHeatingBTUUsed,
        RES_ELEC_WATER_USEFUL,
        RuralResElecOtherBTUUsed,
        RES_ELEC_OTHER_USEFUL,
        RuralResNGSpaceHeatingToElecBTUUsed,
        RuralResFOKerSpaceHeatingToElecBTUUsed,
        RuralResLPGSpaceHeatingToElecBTUUsed,
        RES_ELEC_WATER_USEFUL_REPLACE_FF,
        RuralResNGWaterHeatingToElecBTUUsed,
        RuralResFOKerWaterHeatingToElecBTUUsed,
        RuralResLPGWaterHeatingToElecBTUUsed,
        RES_ELEC_OTHER_USEFUL_REPLACE_FF,
        RuralResNGOtherToElecBTUUsed,
        RuralResFOKerOtherToElecBTUUsed,
        RuralResLPGOtherToElecBTUUsed,
        RuralResElecToNGSpaceHeatingBTUUsed,
        RuralResElecToFOKerSpaceHeatingBTUUsed,
        RuralResElecToLPGSpaceHeatingBTUUsed,
        RuralResElecToNGWaterHeatingBTUUsed,
        RuralResElecToFOKerWaterHeatingBTUUsed,
        RuralResElecToLPGWaterHeatingBTUUsed,
    )
    rural_ng_btu = calc_ng_btu(
        RuralPerChangedFossilFuelUsed,
        RuralResNGSpaceHeatingBTUUsed,
        RuralResNGSpaceHeatingToElecBTUUsed,
        RES_NG_SPACE_USEFUL,
        RuralResNGWaterHeatingBTUUsed,
        RuralResNGWaterHeatingToElecBTUUsed,
        RES_NG_WATER_USEFUL,
        RuralResNGOtherBTUUsed,
        RuralResNGOtherToElecBTUUsed,
        RES_NG_OTHER_USEFUL,
        RuralResElecToNGSpaceHeatingBTUUsed,
        RuralResElecToNGWaterHeatingBTUUsed,
    )
    rural_fok_btu = calc_fok_btu(
        RuralPerChangedFossilFuelUsed,
        RuralResFOKerSpaceHeatingBTUUsed,
        RuralResFOKerSpaceHeatingToElecBTUUsed,
        RES_FOK_SPACE_USEFUL,
        RuralResFOKerWaterHeatingBTUUsed,
        RuralResFOKerWaterHeatingToElecBTUUsed,
        RES_FOK_WATER_USEFUL,
        RuralResFOKerOtherBTUUsed,
        RuralResFOKerOtherToElecBTUUsed,
        RES_FOK_OTHER_USEFUL,
        RuralResElecToFOKerSpaceHeatingBTUUsed,
        RuralResElecToFOKerWaterHeatingBTUUsed,
    )

    rural_lpg_btu = calc_lpg_btu(
        RuralPerChangedFossilFuelUsed,
        RuralResLPGSpaceHeatingBTUUsed,
        RuralResLPGSpaceHeatingToElecBTUUsed,
        RES_LPG_SPACE_USEFUL,
        RuralResLPGWaterHeatingBTUUsed,
        RuralResLPGWaterHeatingToElecBTUUsed,
        RES_LPG_WATER_USEFUL,
        RuralResLPGOtherBTUUsed,
        RuralResLPGOtherToElecBTUUsed,
        RES_LPG_OTHER_USEFUL,
        RuralResElecToLPGSpaceHeatingBTUUsed,
        RuralResElecToLPGWaterHeatingBTUUsed,
    )

    # Calculate GHG emissions
    res_elec_ghg = (
        (urban_elec_btu + suburban_elec_btu + rural_elec_btu)
        * (1 / BTU_MWH)
        / (1 - GRID_LOSS)
        * (
            (
                (grid_coal / 100 * CO2_LB_MWH_COAL)
                + (grid_oil / 100 * CO2_LB_MWH_OIL)
                + (grid_ng / 100 * CO2_LB_MWH_NG)
                + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
            )
            * MMT_LB
        )
        * (1 - ff_carbon_capture / 100)
    )

    res_ng_btu = urban_ng_btu + suburban_ng_btu + rural_ng_btu
    res_ng_ghg = (
        res_ng_btu
        * (1 / BTU_CCF_AVG)
        * (1 + res_energy_change / 100)
        * 0.1
        * CO2_LB_KCF_NG
        * MMT_LB
    )
    res_fok_ghg = (
        (urban_fok_btu + suburban_fok_btu + rural_fok_btu)
        * (1 / BTU_GAL_FOK)
        * (1 + res_energy_change / 100)
        * (CO2_MMT_KB_FOK * KB_G)
    )

    res_lpg_ghg = (
        (urban_lpg_btu + suburban_lpg_btu + rural_lpg_btu)
        * (1 / BTU_GAL_LPG)
        * (1 + res_energy_change / 100)
        * (CO2_MMT_KB_LPG * KB_G)
    )

    res_ghg = res_elec_ghg + res_ng_ghg + res_fok_ghg + res_lpg_ghg

    return res_ghg, res_ng_btu


def calc_ci_ghg(
    ComIndPerElectrification,
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    ff_carbon_capture,
    PerComIndEnergyUse,
):
    ComIndPerFossilFuelUsed = 100 - ComIndPerElectrification
    PerChangedFossilFuelUsed = (
        ComIndPerFossilFuelUsed - ComIndPerFossilFuelUsed2015
    ) / ComIndPerFossilFuelUsed2015

    ComIndElecGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerElectrification / 100)
        / (PerEnergyToUseComIndElec / 100)
        * 1000000000
        * (1 / BTU_MWH)
        / (1 - GRID_LOSS)
        * (
            (
                (grid_coal / 100 * CO2_LB_MWH_COAL)
                + (grid_oil / 100 * CO2_LB_MWH_OIL)
                + (grid_ng / 100 * CO2_LB_MWH_NG)
                + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
            )
            * MMT_LB
        )
        * (1 - ff_carbon_capture / 100)
    )

    ComIndNGGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFNGUsed / 100)
        / (PerEnergyToUseComIndNG / 100)
        * CO2_MMT_BBTU_NG
        * MT_TO_MMT
    )

    ComIndCoalGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFCoalUsed / 100)
        / (PerEnergyToUseComIndCoal / 100)
        * CO2_MMT_BBTU_COAL
        * MT_TO_MMT
    )

    ComIndDFOGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFDFOUsed / 100)
        / (PerEnergyToUseComIndDFO / 100)
        * CO2_MMT_BBTU_DFO
        * MT_TO_MMT
    )

    ComIndKerGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFKerUsed / 100)
        / (PerEnergyToUseComIndKer / 100)
        * CO2_MMT_BBTU_KER
        * MT_TO_MMT
    )

    ComIndLPGGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFLPGUsed / 100)
        / (PerEnergyToUseComIndLPG / 100)
        * CO2_MMT_BBTU_LPG
        * MT_TO_MMT
    )

    ComIndMotGasGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFMotGasUsed / 100)
        / (PerEnergyToUseComIndMotGas / 100)
        * CO2_MMT_BBTU_MOTOR_GAS
        * MT_TO_MMT
    )

    ComIndRFOGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFRFOUsed / 100)
        / (PerEnergyToUseComIndRFO / 100)
        * CO2_MMT_BBTU_RFO
        * MT_TO_MMT
    )

    ComIndPetCokeGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFPetCokeUsed / 100)
        / (PerEnergyToUseComIndPetCoke / 100)
        * CO2_MMT_BBTU_PETCOKE
        * MT_TO_MMT
    )

    ComIndStillGasGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFStillGasUsed / 100)
        / (PerEnergyToUseComIndStillGas / 100)
        * CO2_MMT_BBTU_STILL_GAS
        * MT_TO_MMT
    )

    ComIndSpecialNaphthasGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFSpecialNaphthasUsed / 100)
        / (PerEnergyToUseComIndSpecialNaphthas / 100)
        * CO2_MMT_BBTU_NAPHTHAS
        * MT_TO_MMT
    )

    return (
        ComIndElecGHG
        + ComIndNGGHG
        + ComIndCoalGHG
        + ComIndDFOGHG
        + ComIndKerGHG
        + ComIndLPGGHG
        + ComIndMotGasGHG
        + ComIndRFOGHG
        + ComIndPetCokeGHG
        + ComIndStillGasGHG
        + ComIndSpecialNaphthasGHG
    )


def calc_highway_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    ff_carbon_capture,
    PerEVMT,
    pop_factor,
    RegionalFleetMPG,
    rural_pop_percent,
    suburban_pop_percent,
    urban_pop_percent,
    VMTperCap,
):
    VMT = (
        (POP * urban_pop_percent / 100 * (1 + pop_factor / 100) * UrbanVMTperPop)
        + (POP * suburban_pop_percent / 100 * (1 + pop_factor / 100) * SuburbanVMTperPop)
        + (POP * rural_pop_percent / 100 * (1 + pop_factor / 100) * RuralVMTperPop)
    ) * (1 + VMTperCap / 100)

    EVMT = VMT * PerEVMT / 100

    highway_ghg = (VMT - EVMT) / RegionalFleetMPG * CO2eperGallonGasoline * MMT_LB + (
        EVMT
        * EVEff
        * 0.001
        / (1 - GRID_LOSS)
        * (
            (grid_coal / 100 * CO2_LB_MWH_COAL)
            + (grid_oil / 100 * CO2_LB_MWH_OIL)
            + (grid_ng / 100 * CO2_LB_MWH_NG)
            + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
        )
        * MMT_LB
    ) * (1 - ff_carbon_capture / 100)

    return highway_ghg


def calc_aviation_ghg(pop_factor, PerAviation):
    return GHG_AVIATION * (1 + pop_factor / 100) * (1 + PerAviation / 100)


def calc_transit_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    ff_carbon_capture,
    PerTransRailRidership,
    pop_factor,
    rural_pop_percent,
    suburban_pop_percent,
    TransRailUrbanPerElecMotion,
    TransRailSuburbanPerElecMotion,
    TransRailRuralPerElecMotion,
    urban_pop_percent,
):
    TransRailUrbanPerDieselMotion = 100 - TransRailUrbanPerElecMotion
    TransRailSuburbanPerDieselMotion = 100 - TransRailSuburbanPerElecMotion
    TransRailRuralPerDieselMotion = 100 - TransRailRuralPerElecMotion

    MobTransitElecGHG = (
        POP
        * (1 + pop_factor / 100)
        * (1 / BTU_MWH)
        / (1 - GRID_LOSS)
        * (
            (
                urban_pop_percent
                / 100
                * TransRailUrbanBTUPerCapMotion
                * TransRailUrbanPerElecMotion
                / 100
            )
            + (
                suburban_pop_percent
                / 100
                * TransRailSuburbanBTUPerCapMotion
                * TransRailSuburbanPerElecMotion
                / 100
            )
            + (
                rural_pop_percent
                / 100
                * TransRailRuralBTUPerCapMotion
                * TransRailRuralPerElecMotion
                / 100
            )
        )
        / (PerEnergyToMotionRailElec / 100)
        * (
            (
                (grid_coal / 100 * CO2_LB_MWH_COAL)
                + (grid_oil / 100 * CO2_LB_MWH_OIL)
                + (grid_ng / 100 * CO2_LB_MWH_NG)
                + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
            )
            * MMT_LB
        )
        * (1 - ff_carbon_capture / 100)
    )

    MobTransitDieselGHG = (
        POP
        * (1 + pop_factor / 100)
        * TransRailMTCO2ePerBBtuDiesel
        * (1 / 1000000000)
        * MT_TO_MMT
        * (
            (
                urban_pop_percent
                / 100
                * TransRailUrbanBTUPerCapMotion
                * TransRailUrbanPerDieselMotion
                / 100
            )
            + (
                suburban_pop_percent
                / 100
                * TransRailSuburbanBTUPerCapMotion
                * TransRailSuburbanPerDieselMotion
                / 100
            )
            + (
                rural_pop_percent
                / 100
                * TransRailRuralBTUPerCapMotion
                * TransRailRuralPerDieselMotion
                / 100
            )
        )
        / (PerEnergyToMotionRailDiesel / 100)
    )

    return (MobTransitElecGHG + MobTransitDieselGHG) * (1 + PerTransRailRidership / 100)


def calc_other_mobile_ghg(
    FreightRailPerElecMotion,
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    InterCityRailPerElecMotion,
    MarinePortPerElectrification,
    ff_carbon_capture,
    PerFreightRail,
    PerInterCityRail,
    PerMarinePort,
    PerOffroad,
    OffroadPerElectrification,
):
    """
    Calculate GHG emissions for freight & intercity rail, marine & port-related, and off-road
    vehicles and equipment.
    """
    FreightRailPerDieselMotion = 100 - FreightRailPerElecMotion

    FreightRailElecGHG = (
        FreightRailBBtuMotion
        * (FreightRailPerElecMotion / 100)
        / (PerEnergyToMotionRailElec / 100)
        * 1000000000
        * (1 / BTU_MWH)
        / (1 - GRID_LOSS)
        * (
            (
                (grid_coal / 100 * CO2_LB_MWH_COAL)
                + (grid_oil / 100 * CO2_LB_MWH_OIL)
                + (grid_ng / 100 * CO2_LB_MWH_NG)
                + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
            )
            * MMT_LB
        )
        * (1 - ff_carbon_capture / 100)
    )

    FreightRailDieselGHG = (
        FreightRailBBtuMotion
        * (FreightRailPerDieselMotion / 100)
        * FreightRailMTCO2ePerBBtuDiesel
        * MT_TO_MMT
        / (PerEnergyToMotionRailDiesel / 100)
    )

    FreightRailGHG = (FreightRailElecGHG + FreightRailDieselGHG) * (1 + PerFreightRail / 100)

    InterCityRailPerDieselMotion = 100 - InterCityRailPerElecMotion
    InterCityRailElecGHG = (
        InterCityRailBBtuMotion
        * (InterCityRailPerElecMotion / 100)
        / (PerEnergyToMotionRailElec / 100)
        * 1000000000
        * (1 / BTU_MWH)
        / (1 - GRID_LOSS)
        * (
            (
                (grid_coal / 100 * CO2_LB_MWH_COAL)
                + (grid_oil / 100 * CO2_LB_MWH_OIL)
                + (grid_ng / 100 * CO2_LB_MWH_NG)
                + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
            )
            * MMT_LB
        )
        * (1 - ff_carbon_capture / 100)
    )

    InterCityRailDieselGHG = (
        InterCityRailBBtuMotion
        * (InterCityRailPerDieselMotion / 100)
        * InterCityRailMTCO2ePerBBtuDiesel
        * MT_TO_MMT
        / (PerEnergyToMotionRailDiesel / 100)
    )

    InterCityRailGHG = (InterCityRailElecGHG + InterCityRailDieselGHG) * (
        1 + PerInterCityRail / 100
    )

    MarinePortPerFossilFuelMotion = 100 - MarinePortPerElectrification
    MarinePortPerChangedFossilFuelMotion = (
        MarinePortPerFossilFuelMotion - MarinePortPerFossilFuelMotion2015
    ) / MarinePortPerFossilFuelMotion2015

    MarinePortElecGHG = (
        MarinePortBBtuMotion
        * (MarinePortPerElectrification / 100)
        / (PerEnergyToMotionMarineElec / 100)
        * 1000000000
        * (1 / BTU_MWH)
        / (1 - GRID_LOSS)
        * (
            (
                (grid_coal / 100 * CO2_LB_MWH_COAL)
                + (grid_oil / 100 * CO2_LB_MWH_OIL)
                + (grid_ng / 100 * CO2_LB_MWH_NG)
                + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
            )
            * MMT_LB
        )
        * (1 - ff_carbon_capture / 100)
    )

    MarinePortRFOGHG = (
        MarinePortBBtuMotion
        * (MarinePortPerFFRFOMotion / 100)
        * (MarinePortPerFossilFuelMotion / 100)
        * (1 + MarinePortPerChangedFossilFuelMotion)
        * MarinePortMTCO2ePerBBtuRFO
        * MT_TO_MMT
        / (PerEnergyToMotionMarineRFO / 100)
    )

    MarinePortDFOGHG = (
        MarinePortBBtuMotion
        * (MarinePortPerFFDFOMotion / 100)
        * (MarinePortPerFossilFuelMotion / 100)
        * (1 + MarinePortPerChangedFossilFuelMotion)
        * MarinePortMTCO2ePerBBtuDFO
        * MT_TO_MMT
        / (PerEnergyToMotionMarineDFO / 100)
    )

    MarinePortGHG = (MarinePortElecGHG + MarinePortRFOGHG + MarinePortDFOGHG) * (
        1 + PerMarinePort / 100
    )

    OffroadPerFossilFuelMotion = 100 - OffroadPerElectrification
    OffroadPerChangedFossilFuelMotion = (
        OffroadPerFossilFuelMotion - OffroadPerFossilFuelMotion2015
    ) / OffroadPerFossilFuelMotion2015

    OffroadElecGHG = (
        OffroadBBtuMotion
        * (OffroadPerElectrification / 100)
        / (PerEnergyToMotionOffroadElec / 100)
        * 1000000000
        * (1 / BTU_MWH)
        / (1 - GRID_LOSS)
        * (
            (
                (grid_coal / 100 * CO2_LB_MWH_COAL)
                + (grid_oil / 100 * CO2_LB_MWH_OIL)
                + (grid_ng / 100 * CO2_LB_MWH_NG)
                + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
            )
            * MMT_LB
        )
        * (1 - ff_carbon_capture / 100)
    )

    OffroadMotGasGHG = (
        OffroadBBtuMotion
        * (OffroadPerFFMotGasMotion / 100)
        * (OffroadPerFossilFuelMotion / 100)
        * (1 + OffroadPerChangedFossilFuelMotion)
        * OffroadMTCO2ePerBBtuMotGas
        * MT_TO_MMT
        / (PerEnergyToMotionOffroadMotGas / 100)
    )

    OffroadDFOGHG = (
        OffroadBBtuMotion
        * (OffroadPerFFDFOMotion / 100)
        * (OffroadPerFossilFuelMotion / 100)
        * (1 + OffroadPerChangedFossilFuelMotion)
        * OffroadMTCO2ePerBBtuDFO
        * MT_TO_MMT
        / (PerEnergyToMotionOffroadDFO / 100)
    )

    OffroadLPGGHG = (
        OffroadBBtuMotion
        * (OffroadPerFFLPGMotion / 100)
        * (OffroadPerFossilFuelMotion / 100)
        * (1 + OffroadPerChangedFossilFuelMotion)
        * OffroadMTCO2ePerBBtuLPG
        * MT_TO_MMT
        / (PerEnergyToMotionOffroadLPG / 100)
    )

    OffroadGHG = (OffroadElecGHG + OffroadMotGasGHG + OffroadDFOGHG + OffroadLPGGHG) * (
        1 + PerOffroad / 100
    )

    return FreightRailGHG + InterCityRailGHG + MarinePortGHG + OffroadGHG


def calc_non_energy_ghg(
    ComIndPerElectrification,
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    PerAg,
    res_energy_change,
    PerComIndEnergyUse,
    PerForestCoverage,
    PerIP,
    PerUrbanTreeCoverage,
    PerWaste,
    PerWasteWater,
    pop_factor,
    rural_per_res_electrification,
    suburban_per_res_electrification,
    urban_per_res_electrification,
    urban_pop_percent,
):
    AgricultureGHG = GHG_AG * (1 + PerAg / 100)
    SolidWasteGHG = GHG_SOLID_WASTE * (1 + PerWaste / 100) * (1 + pop_factor / 100)
    WasteWaterGHG = GHG_WASTEWATER * (1 + PerWasteWater / 100) * (1 + pop_factor / 100)
    IndProcGHG = GHG_IP * (1 + PerIP / 100)

    ResNGConsumption = calc_res_ghg(
        grid_coal,
        grid_ng,
        grid_oil,
        grid_other_ff,
        res_energy_change,
        pop_factor,
        rural_per_res_electrification,
        suburban_per_res_electrification,
        urban_per_res_electrification,
        rural_pop_percent,
        suburban_pop_percent,
        urban_pop_percent,
    )[1]

    ComIndPerFossilFuelUsed = 100 - ComIndPerElectrification
    PerChangedFossilFuelUsed = (
        ComIndPerFossilFuelUsed - ComIndPerFossilFuelUsed2015
    ) / ComIndPerFossilFuelUsed2015

    ComIndNGConsumption = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFNGUsed / 100)
        / (PerEnergyToUseComIndNG / 100)
        * 1000000000
    )

    NGSystemsGHG = (
        (ResNGConsumption + ComIndNGConsumption)
        * (1 / BTU_CCF_AVG)
        * 100
        * 0.000001
        * (MMTCO2ePerMillionCFNG_CH4 + MMTCO2ePerMillionCFNG_CO2)
    )

    LULUCFGHG = GHG_URBAN_TREES * (1 + PerUrbanTreeCoverage / 100) + (
        GHG_FORESTS + GHG_FOREST_CHANGE
    ) * (1 + PerForestCoverage / 100)

    return AgricultureGHG + SolidWasteGHG + WasteWaterGHG + IndProcGHG + NGSystemsGHG + LULUCFGHG


def wrangle_data_for_bar_chart(user_inputs):
    data = {
        "Category": sectors,
        "2015": [
            GHG_RES,
            GHG_CI,
            GHG_HIGHWAY,
            GHG_TRANSIT,
            GHG_AVIATION,
            GHG_OTHER_MOBILE,
            GHG_NON_ENERGY,
        ],
        "Scenario": [
            calc_res_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["res_energy_change"],
                user_inputs["pop_factor"],
                user_inputs["rural_per_res_electrification"],
                user_inputs["suburban_per_res_electrification"],
                user_inputs["urban_per_res_electrification"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
            )[0],
            calc_ci_ghg(
                user_inputs["ComIndPerElectrification"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["PerComIndEnergyUse"],
            ),
            calc_highway_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["PerEVMT"],
                user_inputs["pop_factor"],
                user_inputs["RegionalFleetMPG"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
                user_inputs["VMTperCap"],
            ),
            calc_transit_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["PerTransRailRidership"],
                user_inputs["pop_factor"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["TransRailUrbanPerElecMotion"],
                user_inputs["TransRailSuburbanPerElecMotion"],
                user_inputs["TransRailRuralPerElecMotion"],
                user_inputs["urban_pop_percent"],
            ),
            calc_aviation_ghg(user_inputs["pop_factor"], user_inputs["PerAviation"]),
            calc_other_mobile_ghg(
                user_inputs["FreightRailPerElecMotion"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["InterCityRailPerElecMotion"],
                user_inputs["MarinePortPerElectrification"],
                user_inputs["ff_carbon_capture"],
                user_inputs["PerFreightRail"],
                user_inputs["PerInterCityRail"],
                user_inputs["PerMarinePort"],
                user_inputs["PerOffroad"],
                user_inputs["OffroadPerElectrification"],
            ),
            calc_non_energy_ghg(
                user_inputs["ComIndPerElectrification"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["PerAg"],
                user_inputs["res_energy_change"],
                user_inputs["PerComIndEnergyUse"],
                user_inputs["PerForestCoverage"],
                user_inputs["PerIP"],
                user_inputs["PerUrbanTreeCoverage"],
                user_inputs["PerWaste"],
                user_inputs["PerWasteWater"],
                user_inputs["pop_factor"],
                user_inputs["rural_per_res_electrification"],
                user_inputs["suburban_per_res_electrification"],
                user_inputs["urban_per_res_electrification"],
                user_inputs["urban_pop_percent"],
            ),
        ],
    }
    return data


def wrangle_data_for_stacked_chart(user_inputs):
    # Transpose data
    data = {
        "Year": ["2015", "Scenario"],
        "Residential": [
            GHG_RES,
            calc_res_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["res_energy_change"],
                user_inputs["pop_factor"],
                user_inputs["rural_per_res_electrification"],
                user_inputs["suburban_per_res_electrification"],
                user_inputs["urban_per_res_electrification"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
            )[0],
        ],
        "Commercial/Industrial": [
            GHG_CI,
            calc_ci_ghg(
                user_inputs["ComIndPerElectrification"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["PerComIndEnergyUse"],
            ),
        ],
        "Mobile-Highway": [
            GHG_HIGHWAY,
            calc_highway_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["PerEVMT"],
                user_inputs["pop_factor"],
                user_inputs["RegionalFleetMPG"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
                user_inputs["VMTperCap"],
            ),
        ],
        "Mobile-Transit": [
            GHG_TRANSIT,
            calc_transit_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["PerTransRailRidership"],
                user_inputs["pop_factor"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["TransRailUrbanPerElecMotion"],
                user_inputs["TransRailSuburbanPerElecMotion"],
                user_inputs["TransRailRuralPerElecMotion"],
                user_inputs["urban_pop_percent"],
            ),
        ],
        "Mobile-Aviation": [GHG_AVIATION, calc_aviation_ghg(pop_factor, PerAviation)],
        "Mobile-Other": [
            GHG_OTHER_MOBILE,
            calc_other_mobile_ghg(
                user_inputs["FreightRailPerElecMotion"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["InterCityRailPerElecMotion"],
                user_inputs["MarinePortPerElectrification"],
                user_inputs["ff_carbon_capture"],
                user_inputs["PerFreightRail"],
                user_inputs["PerInterCityRail"],
                user_inputs["PerMarinePort"],
                user_inputs["PerOffroad"],
                user_inputs["OffroadPerElectrification"],
            ),
        ],
        "Non-Energy": [
            GHG_NON_ENERGY,
            calc_non_energy_ghg(
                user_inputs["ComIndPerElectrification"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["PerAg"],
                user_inputs["res_energy_change"],
                user_inputs["PerComIndEnergyUse"],
                user_inputs["PerForestCoverage"],
                user_inputs["PerIP"],
                user_inputs["PerUrbanTreeCoverage"],
                user_inputs["PerWaste"],
                user_inputs["PerWasteWater"],
                user_inputs["pop_factor"],
                user_inputs["rural_per_res_electrification"],
                user_inputs["suburban_per_res_electrification"],
                user_inputs["urban_per_res_electrification"],
                user_inputs["urban_pop_percent"],
            ),
        ],
    }
    return data


def wrangle_data_for_pie_chart(user_inputs):
    """Configure data and plot for pie chart."""
    x = {
        "Coal": user_inputs["grid_coal"],
        "Oil": user_inputs["grid_oil"],
        "Natural Gas": user_inputs["grid_ng"],
        "Nuclear": user_inputs["grid_nuclear"],
        "Solar": user_inputs["grid_solar"],
        "Wind": user_inputs["grid_wind"],
        "Biomass": user_inputs["grid_bio"],
        "Hydropower": user_inputs["grid_hydro"],
        "Geothermal": user_inputs["grid_geo"],
        "Other Fossil Fuel": user_inputs["grid_other_ff"],
    }

    data = pd.Series(x).reset_index(name="Percentage").rename(columns={"index": "FuelType"})
    data["angle"] = data["Percentage"] / data["Percentage"].sum() * 2 * pi
    data["color"] = Spectral10

    return data


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
    """Set variables according to user inputs."""
    user_inputs = {
        "grid_coal": float(grid_coalTextInput.value),
        "grid_ng": float(grid_ngTextInput.value),
        "grid_oil": float(grid_oilTextInput.value),
        "grid_nuclear": float(grid_nuclearTextInput.value),
        "grid_solar": float(grid_solarTextInput.value),
        "grid_wind": float(grid_windTextInput.value),
        "grid_bio": float(grid_bioTextInput.value),
        "grid_hydro": float(grid_hydroTextInput.value),
        "grid_geo": float(grid_geoTextInput.value),
        "grid_other_ff": float(grid_other_ffTextInput.value),
        "PerNetZeroCarbon": float(PerNetZeroCarbonTextInput.value),  # TK, possibly
        "pop_factor": pop_factorSlider.value,
        "urban_pop_percent": float(urban_pop_percentTextInput.value),
        "suburban_pop_percent": float(suburban_pop_percentTextInput.value),
        "rural_pop_percent": float(rural_pop_percentTextInput.value),
        "res_energy_change": res_energy_change_slider.value,
        "urban_per_res_electrification": urban_per_res_electrification_slider.value,
        "suburban_per_res_electrification": suburban_per_res_electrification_slider.value,
        "rural_per_res_electrification": rural_per_res_electrification_slider.value,
        "PerComIndEnergyUse": PerComIndEnergyUseSlider.value,
        "ComIndPerElectrification": ComIndPerElectrificationSlider.value,
        "VMTperCap": VMTperCapSlider.value,
        "RegionalFleetMPG": RegionalFleetMPGSlider.value,
        "PerEVMT": PerEVMTSlider.value,
        "PerTransRailRidership": PerTransRailRidershipSlider.value,
        "TransRailUrbanPerElecMotion": TransRailUrbanPerElecMotionSlider.value,
        "TransRailSuburbanPerElecMotion": TransRailSuburbanPerElecMotionSlider.value,
        "TransRailRuralPerElecMotion": TransRailRuralPerElecMotionSlider.value,
        "PerFreightRail": PerFreightRailSlider.value,
        "FreightRailPerElecMotion": FreightRailPerElecMotionSlider.value,
        "PerInterCityRail": PerInterCityRailSlider.value,
        "InterCityRailPerElecMotion": InterCityRailPerElecMotionSlider.value,
        "PerMarinePort": PerMarinePortSlider.value,
        "MarinePortPerElectrification": MarinePortPerElectrificationSlider.value,
        "PerOffroad": PerOffroadSlider.value,
        "OffroadPerElectrification": OffroadPerElectrificationSlider.value,
        "PerAviation": PerAviationSlider.value,
        "PerAg": PerAgSlider.value,
        "PerWaste": PerWasteSlider.value,
        "PerWasteWater": PerWasteWaterSlider.value,
        "PerIP": PerIPSlider.value,
        "PerUrbanTreeCoverage": PerUrbanTreeCoverageSlider.value,
        "PerForestCoverage": PerForestCoverageSlider.value,
        "ff_carbon_capture": ff_carbon_capture_slider.value,
        "AirCapture": AirCaptureSlider.value,  # TK, possibly
    }

    # update the data for the charts
    bar_chart_source.data = wrangle_data_for_bar_chart(user_inputs)
    stacked_chart_source.data = wrangle_data_for_stacked_chart(user_inputs)
    pie_chart_source.data = wrangle_data_for_pie_chart(user_inputs)

    # update text and style for the grid paragraph widget
    grid_text.text, grid_text.style = generate_text_and_style(user_inputs)


###############
# Create charts

bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
bar_chart_source = ColumnDataSource(data=bar_chart_data)
bar_chart = figure(
    x_range=bar_chart_data["Category"],
    y_range=(0, 50),
    plot_height=500,
    plot_width=450,
    y_axis_label="Million Metric Tons of CO2e",
    title="Greenhouse Gas Emissions in Greater Philadelphia",
    name="barchart",
)
bar_chart.vbar(
    x=dodge("Category", -0.15, range=bar_chart.x_range),
    top="2015",
    source=bar_chart_source,
    width=0.2,
    color="steelblue",
    legend_label="2015",
)
bar_chart.vbar(
    x=dodge("Category", 0.15, range=bar_chart.x_range),
    top="Scenario",
    source=bar_chart_source,
    width=0.2,
    color="darkseagreen",
    legend_label="Scenario",
)
bar_chart.xaxis.major_label_orientation = np.pi / 4
bar_chart.x_range.range_padding = 0.1

stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
stacked_chart_source = ColumnDataSource(data=stacked_chart_data)
stacked_bar_chart = figure(
    x_range=stacked_chart_data["Year"],
    y_range=(0, 100),
    plot_height=500,
    plot_width=500,
    y_axis_label="Million Metric Tons of CO2e",
    title="Greenhouse Gas Emissions in Greater Philadelphia",
)
stacked_bar_chart.vbar_stack(
    sectors, x="Year", width=0.4, color=Viridis7, source=stacked_chart_source, legend_label=sectors
)
stacked_bar_chart.legend[
    0
].items.reverse()  # Reverses legend items to match order of occurence in stack
stacked_bar_chart_legend = stacked_bar_chart.legend[0]
stacked_bar_chart.add_layout(stacked_bar_chart_legend, "right")

pie_chart_data = wrangle_data_for_pie_chart(user_inputs)
pie_chart_source = ColumnDataSource(data=pie_chart_data)

pie_chart = figure(
    title="Electricity Grid Resource Mix",
    toolbar_location=None,
    plot_height=400,
    plot_width=750,
    tools="hover",
    tooltips="@FuelType: @Percentage",
    x_range=(-0.5, 1.0),
)

pie_chart.wedge(
    x=0,
    y=1,
    radius=0.3,
    start_angle=cumsum("angle", include_zero=True),
    end_angle=cumsum("angle"),
    line_color="white",
    fill_color="color",
    legend_field="FuelType",
    source=pie_chart_source,
)

pie_chart.axis.axis_label = None
pie_chart.axis.visible = False
pie_chart.grid.grid_line_color = None

###############################################################
# create the input widgets that allow user to change the charts

# electric grid mix
text, style = generate_text_and_style(user_inputs)
grid_text = Paragraph(text=text, style=style)

grid_coalTextInput = TextInput(value=str(round(grid_coal, 1)), title="% Coal in Grid Mix")
grid_coalTextInput.on_change("value", callback)

grid_oilTextInput = TextInput(value=str(round(grid_oil, 1)), title="% Oil in Grid Mix")
grid_oilTextInput.on_change("value", callback)

grid_ngTextInput = TextInput(value=str(round(grid_ng, 1)), title="% Natural Gas in Grid Mix")
grid_ngTextInput.on_change("value", callback)

grid_nuclearTextInput = TextInput(value=str(round(grid_nuclear, 1)), title="% Nuclear in Grid Mix")
grid_nuclearTextInput.on_change("value", callback)

grid_solarTextInput = TextInput(value=str(round(grid_solar, 1)), title="% Solar in Grid Mix")
grid_solarTextInput.on_change("value", callback)

grid_windTextInput = TextInput(value=str(round(grid_wind, 1)), title="% Wind in Grid Mix")
grid_windTextInput.on_change("value", callback)

grid_bioTextInput = TextInput(value=str(round(grid_bio, 1)), title="% Biomass in Grid Mix")
grid_bioTextInput.on_change("value", callback)

grid_hydroTextInput = TextInput(value=str(round(grid_hydro, 1)), title="% Hydropower in Grid Mix")
grid_hydroTextInput.on_change("value", callback)

grid_geoTextInput = TextInput(value=str(round(grid_geo, 1)), title="% Geothermal in Grid Mix")
grid_geoTextInput.on_change("value", callback)

grid_other_ffTextInput = TextInput(
    value=str(round(grid_other_ff, 1)), title="% Other Fossil Fuel in Grid Mix"
)
grid_other_ffTextInput.on_change("value", callback)

PerNetZeroCarbonTextInput = TextInput(
    value=str(round(grid_nuclear + grid_solar + grid_wind + grid_bio + grid_hydro + grid_geo)),
    title="% Net Zero Carbon Sources in Grid Mix",
)
PerNetZeroCarbonTextInput.on_change("value", callback)

# population
pop_factorSlider = Slider(start=-100, end=100, value=0, step=10, title="% Change in Population")
pop_factorSlider.on_change("value", callback)

urban_pop_percentTextInput = TextInput(
    value=str(round(urban_pop_percent, 1)), title="% of Population Living in Urban Municipalities"
)
urban_pop_percentTextInput.on_change("value", callback)

suburban_pop_percentTextInput = TextInput(
    value=str(round(suburban_pop_percent, 1)),
    title="% of Population Living in Suburban Municipalities",
)
suburban_pop_percentTextInput.on_change("value", callback)

rural_pop_percentTextInput = TextInput(
    value=str(round(rural_pop_percent, 1)), title="% of Population Living in Rural Municipalities"
)
rural_pop_percentTextInput.on_change("value", callback)

# residential
res_energy_change_slider = Slider(
    start=-100, end=100, value=0, step=10, title="% Change in Per Capita Residential Energy Usage",
)
res_energy_change_slider.on_change("value", callback)
urban_per_res_electrification_slider = Slider(
    start=UrbanMinPerResElectrification,
    end=100,
    value=urban_per_res_elec_used,
    step=1,
    title="% Electrification of Residential End Uses in Urban Areas",
)
urban_per_res_electrification_slider.on_change("value", callback)

suburban_per_res_electrification_slider = Slider(
    start=SuburbanMinPerResElectrification,
    end=100,
    value=suburban_per_res_elec_used,
    step=1,
    title="% Electrification of Residential End Uses in Suburban Areas",
)
suburban_per_res_electrification_slider.on_change("value", callback)

rural_per_res_electrification_slider = Slider(
    start=RuralMinPerResElectrification,
    end=100,
    value=rural_per_res_elec_used,
    step=1,
    title="% Electrification of Residential End Uses in Rural Areas",
)
rural_per_res_electrification_slider.on_change("value", callback)

# commercial and industrial
PerComIndEnergyUseSlider = Slider(
    start=-100,
    end=100,
    value=0,
    step=10,
    title="% Change in Commercial and Industrial Energy Usage",
)
PerComIndEnergyUseSlider.on_change("value", callback)

ComIndPerElectrificationSlider = Slider(
    start=ComIndMinPerElectrification,
    end=100,
    value=ComIndPerElecUsed,
    step=1,
    title="% Electrification of Commercial and Industrial End Uses",
)
ComIndPerElectrificationSlider.on_change("value", callback)

# highway
VMTperCapSlider = Slider(start=-100, end=100, value=0, step=1, title="% Change in VMT per Capita")
VMTperCapSlider.on_change("value", callback)

PerEVMTSlider = Slider(start=0, end=100, value=0, step=1, title="% Vehicle Miles that are Electric")
PerEVMTSlider.on_change("value", callback)

RegionalFleetMPGSlider = Slider(
    start=1,
    end=100,
    value=RegionalFleetMPG,
    step=1,
    title="Averge Regional Fleetwide Fuel Economy (MPG)",
)
RegionalFleetMPGSlider.on_change("value", callback)

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
PerAviationSlider = Slider(start=-100, end=100, value=0, step=1, title="% Change in Air Travel")
PerAviationSlider.on_change("value", callback)

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

# non-energy
PerAgSlider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Emissions from Agriculture"
)
PerAgSlider.on_change("value", callback)

PerWasteSlider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Per Capita Landfill Waste"
)
PerWasteSlider.on_change("value", callback)

PerWasteWaterSlider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Per Capita Wastewater"
)
PerWasteWaterSlider.on_change("value", callback)

PerIPSlider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Emissions from Industrial Processes",
)
PerIPSlider.on_change("value", callback)

PerUrbanTreeCoverageSlider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Urban Tree Coverage"
)
PerUrbanTreeCoverageSlider.on_change("value", callback)

PerForestCoverageSlider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Forest Coverage"
)
PerForestCoverageSlider.on_change("value", callback)

# carbon capture
ff_carbon_capture_slider = Slider(
    start=0,
    end=100,
    value=0,
    step=1,
    title="% Carbon Captured at Combustion Site for Electricity Generation",
)
ff_carbon_capture_slider.on_change("value", callback)

AirCaptureSlider = Slider(start=0, end=100, value=0, step=1, title="MMTCO2e Captured from the Air")
AirCaptureSlider.on_change("value", callback)

#########################
# group the input widgets

population_inputs = Column(
    pop_factorSlider,
    urban_pop_percentTextInput,
    suburban_pop_percentTextInput,
    rural_pop_percentTextInput,
)

grid_inputs = Column(
    grid_text,
    grid_coalTextInput,
    grid_oilTextInput,
    grid_ngTextInput,
    grid_nuclearTextInput,
    grid_solarTextInput,
    grid_windTextInput,
    grid_bioTextInput,
    grid_hydroTextInput,
    grid_geoTextInput,
    grid_other_ffTextInput,
)
res_inputs = Column(
    res_energy_change_slider,
    urban_per_res_electrification_slider,
    suburban_per_res_electrification_slider,
    rural_per_res_electrification_slider,
)
ci_inputs = Column(PerComIndEnergyUseSlider, ComIndPerElectrificationSlider)
highway_inputs = Column(VMTperCapSlider, PerEVMTSlider, RegionalFleetMPGSlider)
transit_inputs = Column(
    PerTransRailRidershipSlider,
    TransRailUrbanPerElecMotionSlider,
    TransRailSuburbanPerElecMotionSlider,
    TransRailRuralPerElecMotionSlider,
)
other_mobile_inputs = Column(
    PerAviationSlider,
    PerFreightRailSlider,
    FreightRailPerElecMotionSlider,
    PerInterCityRailSlider,
    InterCityRailPerElecMotionSlider,
    PerMarinePortSlider,
    MarinePortPerElectrificationSlider,
    PerOffroadSlider,
    OffroadPerElectrificationSlider,
)
non_energy_inputs = Column(
    PerAgSlider,
    PerWasteSlider,
    PerWasteWaterSlider,
    PerIPSlider,
    PerUrbanTreeCoverageSlider,
    PerForestCoverageSlider,
)
carbon_capture_inputs = Column(ff_carbon_capture_slider, AirCaptureSlider)

all_inputs = [
    population_inputs,
    grid_inputs,
    res_inputs,
    ci_inputs,
    highway_inputs,
    transit_inputs,
    other_mobile_inputs,
    non_energy_inputs,
    carbon_capture_inputs,
]

doc = curdoc()
doc.add_root(column(all_inputs))
doc.add_root(column(bar_chart, stacked_bar_chart, pie_chart))
