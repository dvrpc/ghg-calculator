from math import pi
from statistics import mean

import numpy as np
import pandas as pd

from bokeh.layouts import row, column
from bokeh.models import Slider, Column, ColumnDataSource, TextInput, Paragraph, LabelSet
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

###############################
# Residential Stationary Energy

res_energy_change = 0

URBAN_ELEC_MWH_CAP = 2.41  # MWh/person
SUBURBAN_ELEC_MWH_CAP = 3.17
RURAL_ELEC_MWH_CAP = 3.81

URBAN_NG_CCF_CAP = 246.04  # CCF/person
SUBURBAN_NG_CCF_CAP = 193.00
RURAL_NG_CCF_CAP = 89.35

URBAN_FOK_GAL_CAP = 14.50  # gallons/person
SUBURBAN_FOK_GAL_CAP = 43.32
RURAL_FOK_GAL_CAP = 80.84

URBAN_LPG_GAL_CAP = 3.46  # gallons/person
SUBURBAN_LPG_GAL_CAP = 8.44
RURAL_LPG_GAL_CAP = 44.38

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

# BTU/per person for subsector, fuel type, and end use
URB_ELEC_SPACE_BTU = URBAN_ELEC_MWH_CAP * RES_ELEC_SPACE * RES_ELEC_SPACE_USEFUL * BTU_MWH
URB_ELEC_WATER_BTU = URBAN_ELEC_MWH_CAP * RES_ELEC_WATER * RES_ELEC_WATER_USEFUL * BTU_MWH
URB_ELEC_OTHER_BTU = URBAN_ELEC_MWH_CAP * RES_ELEC_OTHER * RES_ELEC_OTHER_USEFUL * BTU_MWH
SUB_ELEC_SPACE_BTU = SUBURBAN_ELEC_MWH_CAP * RES_ELEC_SPACE * RES_ELEC_SPACE_USEFUL * BTU_MWH
SUB_ELEC_WATER_BTU = SUBURBAN_ELEC_MWH_CAP * RES_ELEC_WATER * RES_ELEC_WATER_USEFUL * BTU_MWH
SUB_ELEC_OTHER_BTU = SUBURBAN_ELEC_MWH_CAP * RES_ELEC_OTHER * RES_ELEC_OTHER_USEFUL * BTU_MWH
RUR_ELEC_SPACE_BTU = RURAL_ELEC_MWH_CAP * RES_ELEC_SPACE * RES_ELEC_SPACE_USEFUL * BTU_MWH
RUR_ELEC_WATER_BTU = RURAL_ELEC_MWH_CAP * RES_ELEC_WATER * RES_ELEC_WATER_USEFUL * BTU_MWH
RUR_ELEC_OTHER_BTU = RURAL_ELEC_MWH_CAP * RES_ELEC_OTHER * RES_ELEC_OTHER_USEFUL * BTU_MWH

URB_NG_SPACE_BTU = URBAN_NG_CCF_CAP * RES_NG_SPACE * RES_NG_SPACE_USEFUL * BTU_CCF_AVG
URB_NG_WATER_BTU = URBAN_NG_CCF_CAP * RES_NG_WATER * RES_NG_WATER_USEFUL * BTU_CCF_AVG
URB_NG_OTHER_BTU = URBAN_NG_CCF_CAP * RES_NG_OTHER * RES_NG_OTHER_USEFUL * BTU_CCF_AVG
SUB_NG_SPACE_BTU = SUBURBAN_NG_CCF_CAP * RES_NG_SPACE * RES_NG_SPACE_USEFUL * BTU_CCF_AVG
SUB_NG_WATER_BTU = SUBURBAN_NG_CCF_CAP * RES_NG_WATER * RES_NG_WATER_USEFUL * BTU_CCF_AVG
SUB_NG_OTHER_BTU = SUBURBAN_NG_CCF_CAP * RES_NG_OTHER * RES_NG_OTHER_USEFUL * BTU_CCF_AVG
RUR_NG_SPACE_BTU = RURAL_NG_CCF_CAP * RES_NG_SPACE * RES_NG_SPACE_USEFUL * BTU_CCF_AVG
RUR_NG_WATER_BTU = RURAL_NG_CCF_CAP * RES_NG_WATER * RES_NG_WATER_USEFUL * BTU_CCF_AVG
RUR_NG_OTHER_BTU = RURAL_NG_CCF_CAP * RES_NG_OTHER * RES_NG_OTHER_USEFUL * BTU_CCF_AVG

URB_FOK_SPACE_BTU = URBAN_FOK_GAL_CAP * RES_FOK_SPACE * RES_FOK_SPACE_USEFUL * BTU_GAL_FOK
URB_FOK_WATER_BTU = URBAN_FOK_GAL_CAP * RES_FOK_WATER * RES_FOK_WATER_USEFUL * BTU_GAL_FOK
URB_FOK_OTHER_BTU = URBAN_FOK_GAL_CAP * RES_FOK_OTHER * RES_FOK_OTHER_USEFUL * BTU_GAL_FOK
SUB_FOK_SPACE_BTU = SUBURBAN_FOK_GAL_CAP * RES_FOK_SPACE * RES_FOK_SPACE_USEFUL * BTU_GAL_FOK
SUB_FOK_WATER_BTU = SUBURBAN_FOK_GAL_CAP * RES_FOK_WATER * RES_FOK_WATER_USEFUL * BTU_GAL_FOK
SUB_FOK_OTHER_BTU = SUBURBAN_FOK_GAL_CAP * RES_FOK_OTHER * RES_FOK_OTHER_USEFUL * BTU_GAL_FOK
RUR_FOK_SPACE_BTU = RURAL_FOK_GAL_CAP * RES_FOK_SPACE * RES_FOK_SPACE_USEFUL * BTU_GAL_FOK
RUR_FOK_WATER_BTU = RURAL_FOK_GAL_CAP * RES_FOK_WATER * RES_FOK_WATER_USEFUL * BTU_GAL_FOK
RUR_FOK_OTHER_BTU = RURAL_FOK_GAL_CAP * RES_FOK_OTHER * RES_FOK_OTHER_USEFUL * BTU_GAL_FOK

URB_LPG_SPACE_BTU = URBAN_LPG_GAL_CAP * RES_LPG_SPACE * RES_LPG_SPACE_USEFUL * BTU_GAL_LPG
URB_LPG_WATER_BTU = URBAN_LPG_GAL_CAP * RES_LPG_WATER * RES_LPG_WATER_USEFUL * BTU_GAL_LPG
URB_LPG_OTHER_BTU = URBAN_LPG_GAL_CAP * RES_LPG_OTHER * RES_LPG_OTHER_USEFUL * BTU_GAL_LPG
SUB_LPG_SPACE_BTU = SUBURBAN_LPG_GAL_CAP * RES_LPG_SPACE * RES_LPG_SPACE_USEFUL * BTU_GAL_LPG
SUB_LPG_WATER_BTU = SUBURBAN_LPG_GAL_CAP * RES_LPG_WATER * RES_LPG_WATER_USEFUL * BTU_GAL_LPG
SUB_LPG_OTHER_BTU = SUBURBAN_LPG_GAL_CAP * RES_LPG_OTHER * RES_LPG_OTHER_USEFUL * BTU_GAL_LPG
RUR_LPG_SPACE_BTU = RURAL_LPG_GAL_CAP * RES_LPG_SPACE * RES_LPG_SPACE_USEFUL * BTU_GAL_LPG
RUR_LPG_WATER_BTU = RURAL_LPG_GAL_CAP * RES_LPG_WATER * RES_LPG_WATER_USEFUL * BTU_GAL_LPG
RUR_LPG_OTHER_BTU = RURAL_LPG_GAL_CAP * RES_LPG_OTHER * RES_LPG_OTHER_USEFUL * BTU_GAL_LPG

# BTU/person by subsector/fuel type
URB_ELEC_BTU = URB_ELEC_SPACE_BTU + URB_ELEC_WATER_BTU + URB_ELEC_OTHER_BTU
SUB_ELEC_BTU = SUB_ELEC_SPACE_BTU + SUB_ELEC_WATER_BTU + SUB_ELEC_OTHER_BTU
RUR_ELEC_BTU = RUR_ELEC_SPACE_BTU + RUR_ELEC_WATER_BTU + RUR_ELEC_OTHER_BTU

URB_NG_BTU = URB_NG_SPACE_BTU + URB_NG_WATER_BTU + URB_NG_OTHER_BTU
SUB_NG_BTU = SUB_NG_SPACE_BTU + SUB_NG_WATER_BTU + SUB_NG_OTHER_BTU
RUR_NB_BTU = RUR_NG_SPACE_BTU + RUR_NG_WATER_BTU + RUR_NG_OTHER_BTU

URB_FOK_BTU = URB_FOK_SPACE_BTU + URB_FOK_WATER_BTU + URB_FOK_OTHER_BTU
SUB_FOK_BTU = SUB_FOK_SPACE_BTU + SUB_FOK_WATER_BTU + SUB_FOK_OTHER_BTU
RUR_FOK_BTU = RUR_FOK_SPACE_BTU + RUR_FOK_WATER_BTU + RUR_FOK_OTHER_BTU

URB_LPG_BTU = URB_LPG_SPACE_BTU + URB_LPG_WATER_BTU + URB_LPG_OTHER_BTU
SUB_LPG_BTU = SUB_LPG_SPACE_BTU + SUB_LPG_WATER_BTU + SUB_LPG_OTHER_BTU
RUR_LPG_BTU = RUR_LPG_SPACE_BTU + RUR_LPG_WATER_BTU + RUR_LPG_OTHER_BTU

# BTU/person by subsector
URB_ENERGY_BTU = URB_ELEC_BTU + URB_NG_BTU + URB_FOK_BTU + URB_LPG_BTU
SUB_ENERGY_BTU = SUB_ELEC_BTU + SUB_NG_BTU + SUB_FOK_BTU + SUB_LPG_BTU
RUR_ENERGY_BTU = RUR_ELEC_BTU + RUR_NB_BTU + RUR_FOK_BTU + RUR_LPG_BTU

# some additional BTU groupings
URB_ELEC_HEAT_BTU = URB_ELEC_SPACE_BTU + URB_ELEC_WATER_BTU
SUB_ELEC_HEAT_BTU = SUB_ELEC_SPACE_BTU + SUB_ELEC_WATER_BTU
RUR_ELEC_HEAT_BTU = RUR_ELEC_SPACE_BTU + RUR_ELEC_WATER_BTU

URB_FF_SPACE_BTU = URB_NG_SPACE_BTU + URB_FOK_SPACE_BTU + URB_LPG_SPACE_BTU
URB_FF_WATER_BTU = URB_NG_WATER_BTU + URB_FOK_WATER_BTU + URB_LPG_WATER_BTU
SUB_FF_SPACE_BTU = SUB_NG_SPACE_BTU + SUB_FOK_SPACE_BTU + SUB_LPG_SPACE_BTU
SUB_FF_WATER_BTU = SUB_NG_WATER_BTU + SUB_FOK_WATER_BTU + SUB_LPG_WATER_BTU
RUR_FF_SPACE_BTU = RUR_NG_SPACE_BTU + RUR_FOK_SPACE_BTU + RUR_LPG_SPACE_BTU
RUR_FF_WATER_BTU = RUR_NG_WATER_BTU + RUR_FOK_WATER_BTU + RUR_LPG_WATER_BTU

# shares of subsectors, fuel type, end use
URB_ELEC_SPACE = URB_ELEC_SPACE_BTU / URB_ELEC_BTU
URB_ELEC_WATER = URB_ELEC_WATER_BTU / URB_ELEC_BTU
URB_ELEC_OTHER = URB_ELEC_OTHER_BTU / URB_ELEC_BTU
SUB_ELEC_SPACE = SUB_ELEC_SPACE_BTU / SUB_ELEC_BTU
SUB_ELEC_WATER = SUB_ELEC_WATER_BTU / SUB_ELEC_BTU
SUB_ELEC_OTHER = SUB_ELEC_OTHER_BTU / SUB_ELEC_BTU
RUR_ELEC_SPACE = RUR_ELEC_SPACE_BTU / RUR_ELEC_BTU
RUR_ELEC_WATER = RUR_ELEC_WATER_BTU / RUR_ELEC_BTU
RUR_ELEC_OTHER = RUR_ELEC_OTHER_BTU / RUR_ELEC_BTU

URB_NG_SPACE = URB_NG_SPACE_BTU / URB_NG_BTU
URB_NG_WATER = URB_NG_WATER_BTU / URB_NG_BTU
URB_NG_OTHER = URB_NG_OTHER_BTU / URB_NG_BTU
SUB_NG_SPACE = SUB_NG_SPACE_BTU / SUB_NG_BTU
SUB_NG_WATER = SUB_NG_WATER_BTU / SUB_NG_BTU
SUB_NG_OTHER = SUB_NG_OTHER_BTU / SUB_NG_BTU
RUR_NG_SPACE = RUR_NG_SPACE_BTU / RUR_NB_BTU
RUR_NG_WATER = RUR_NG_WATER_BTU / RUR_NB_BTU
RUR_NG_OTHER = RUR_NG_OTHER_BTU / RUR_NB_BTU

URB_FOK_SPACE = URB_FOK_SPACE_BTU / URB_FOK_BTU
URB_FOK_WATER = URB_FOK_WATER_BTU / URB_FOK_BTU
URB_FOK_OTHER = URB_FOK_OTHER_BTU / URB_FOK_BTU
SUB_FOK_SPACE = SUB_FOK_SPACE_BTU / SUB_FOK_BTU
SUB_FOK_WATER = SUB_FOK_WATER_BTU / SUB_FOK_BTU
SUB_FOK_OTHER = SUB_FOK_OTHER_BTU / SUB_FOK_BTU
RUR_FOK_SPACE = RUR_FOK_SPACE_BTU / RUR_FOK_BTU
RUR_FOK_WATER = RUR_FOK_WATER_BTU / RUR_FOK_BTU
RUR_FOK_OTHER = RUR_FOK_OTHER_BTU / RUR_FOK_BTU

URB_LPG_SPACE = URB_LPG_SPACE_BTU / URB_LPG_BTU
URB_LPG_WATER = URB_LPG_WATER_BTU / URB_LPG_BTU
URB_LPG_OTHER = URB_LPG_OTHER_BTU / URB_LPG_BTU
SUB_LPG_SPACE = SUB_LPG_SPACE_BTU / SUB_LPG_BTU
SUB_LPG_WATER = SUB_LPG_WATER_BTU / SUB_LPG_BTU
SUB_LPG_OTHER = SUB_LPG_OTHER_BTU / SUB_LPG_BTU
RUR_LPG_SPACE = RUR_LPG_SPACE_BTU / RUR_LPG_BTU
RUR_LPG_WATER = RUR_LPG_WATER_BTU / RUR_LPG_BTU
RUR_LPG_OTHER = RUR_LPG_OTHER_BTU / RUR_LPG_BTU

# TODO: change these from percent to shares
# percent of total energy/sector by energy type
URB_ENERGY_ELEC = URB_ELEC_BTU / URB_ENERGY_BTU * 100
URB_ENERGY_NG = URB_NG_BTU / URB_ENERGY_BTU * 100
URB_ENERGY_FOK = URB_FOK_BTU / URB_ENERGY_BTU * 100
URB_ENERGY_LPG = URB_LPG_BTU / URB_ENERGY_BTU * 100
SUB_ENERGY_ELEC = SUB_ELEC_BTU / SUB_ENERGY_BTU * 100
SUB_ENERGY_NG = SUB_NG_BTU / SUB_ENERGY_BTU * 100
SUB_ENERGY_FOK = SUB_FOK_BTU / SUB_ENERGY_BTU * 100
SUB_ENERGY_LPG = SUB_LPG_BTU / SUB_ENERGY_BTU * 100
RUR_ENERGY_ELEC = RUR_ELEC_BTU / RUR_ENERGY_BTU * 100
RUR_ENERGY_NG = RUR_NB_BTU / RUR_ENERGY_BTU * 100
RUR_ENERGY_FOK = RUR_FOK_BTU / RUR_ENERGY_BTU * 100
RUR_ENERGY_LPG = RUR_LPG_BTU / RUR_ENERGY_BTU * 100

# share of total electric heating/sector by heating type
URB_ELEC_HEAT_SPACE = URB_ELEC_SPACE_BTU / URB_ELEC_HEAT_BTU
URB_ELEC_HEAT_WATER = URB_ELEC_WATER_BTU / URB_ELEC_HEAT_BTU
SUB_ELEC_HEAT_SPACE = SUB_ELEC_SPACE_BTU / SUB_ELEC_HEAT_BTU
SUB_ELEC_HEAT_WATER = SUB_ELEC_WATER_BTU / SUB_ELEC_HEAT_BTU
RUR_ELEC_HEAT_SPACE = RUR_ELEC_SPACE_BTU / RUR_ELEC_HEAT_BTU
RUR_ELEC_HEAT_WATER = RUR_ELEC_WATER_BTU / RUR_ELEC_HEAT_BTU

# share of all fossil fuels by subsector
URB_ENERGY_FF = URB_ENERGY_NG + URB_ENERGY_FOK + URB_ENERGY_LPG
SUB_ENERGY_FF = SUB_ENERGY_NG + SUB_ENERGY_FOK + SUB_ENERGY_LPG
RUR_ENERGY_FF = RUR_ENERGY_NG + RUR_ENERGY_FOK + RUR_ENERGY_LPG

# individual fossil fuel share of subsector ff
URB_FF_NG = URB_ENERGY_NG / URB_ENERGY_FF
URB_FF_FOK = URB_ENERGY_FOK / URB_ENERGY_FF
URB_FF_LPG = URB_ENERGY_LPG / URB_ENERGY_FF
SUB_FF_NG = SUB_ENERGY_NG / SUB_ENERGY_FF
SUB_FF_FOK = SUB_ENERGY_FOK / SUB_ENERGY_FF
SUB_FF_LPG = SUB_ENERGY_LPG / SUB_ENERGY_FF
RUR_FF_NG = RUR_ENERGY_NG / RUR_ENERGY_FF
RUR_FF_FOK = RUR_ENERGY_FOK / RUR_ENERGY_FF
RUR_FF_LPG = RUR_ENERGY_LPG / RUR_ENERGY_FF

# individual fossil fuel share of space heating by subsector
URB_FF_SPACE_NG = URB_NG_SPACE_BTU / URB_FF_SPACE_BTU
URB_FF_SPACE_FOK = URB_FOK_SPACE_BTU / URB_FF_SPACE_BTU
URB_FF_SPACE_LPG = URB_LPG_SPACE_BTU / URB_FF_SPACE_BTU
SUB_FF_SPACE_NG = SUB_NG_SPACE_BTU / SUB_FF_SPACE_BTU
SUB_FF_SPACE_FOK = SUB_FOK_SPACE_BTU / SUB_FF_SPACE_BTU
SUB_FF_SPACE_LPG = SUB_LPG_SPACE_BTU / SUB_FF_SPACE_BTU
RUR_FF_SPACE_NG = RUR_NG_SPACE_BTU / RUR_FF_SPACE_BTU
RUR_FF_SPACE_FOK = RUR_FOK_SPACE_BTU / RUR_FF_SPACE_BTU
RUR_FF_SPACE_LPG = RUR_LPG_SPACE_BTU / RUR_FF_SPACE_BTU

# individual fossil fuel share of water heating by subsector
URB_FF_WATER_NG = URB_NG_WATER_BTU / URB_FF_WATER_BTU
URB_FF_WATER_FOK = URB_FOK_WATER_BTU / URB_FF_WATER_BTU
URB_FF_WATER_LPG = URB_LPG_WATER_BTU / URB_FF_WATER_BTU
SUB_FF_WATER_NG = SUB_NG_WATER_BTU / SUB_FF_WATER_BTU
SUB_FF_WATER_FOK = SUB_FOK_WATER_BTU / SUB_FF_WATER_BTU
SUB_FF_WATER_LPG = SUB_LPG_WATER_BTU / SUB_FF_WATER_BTU
RUR_FF_WATER_NG = RUR_NG_WATER_BTU / RUR_FF_WATER_BTU
RUR_FF_WATER_FOK = RUR_FOK_WATER_BTU / RUR_FF_WATER_BTU
RUR_FF_WATER_LPG = RUR_LPG_WATER_BTU / RUR_FF_WATER_BTU

#############################################################
# Commercial/Industrial Stationary Energy from 2015 Inventory
# Also: https://www.iea-etsap.org/E-TechDS/PDF/I01-ind_boilers-GS-AD-gct.pdf

PerEnergyToUseComIndElec = 100
PerEnergyToUseComIndNG = 75
PerEnergyToUseComIndCoal = 85
PerEnergyToUseComIndDFO = 80
PerEnergyToUseComIndKer = 80
PerEnergyToUseComIndLPG = 80
PerEnergyToUseComIndMotGas = 80
PerEnergyToUseComIndRFO = 80
PerEnergyToUseComIndPetCoke = 80
PerEnergyToUseComIndStillGas = 80
PerEnergyToUseComIndSpecialNaphthas = 80
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

############################
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

#################################
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

##########################
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
    "rur_energy_elec": RUR_ENERGY_ELEC,
    "rural_pop_percent": rural_pop_percent,
    "sub_energy_elec": SUB_ENERGY_ELEC,
    "suburban_pop_percent": suburban_pop_percent,
    "TransRailRuralPerElecMotion": TransRailRuralPerElecMotion,
    "TransRailSuburbanPerElecMotion": TransRailSuburbanPerElecMotion,
    "TransRailUrbanPerElecMotion": TransRailUrbanPerElecMotion,
    "urb_energy_elec": URB_ENERGY_ELEC,
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
    rur_energy_elec,
    sub_energy_elec,
    urb_energy_elec,
    rural_pop_percent,
    suburban_pop_percent,
    urban_pop_percent,
):
    """
    Determine BTU of energy by sub-sector (urban, suburban, rural) and from that calculate
    ghg emissions.
    """

    def btu_used(subsector_pop_percent, subsector_energy_btu):
        return (
            POP
            * (1 + pop_factor / 100)
            * (subsector_pop_percent / 100)
            * subsector_energy_btu
            * (1 + res_energy_change / 100)
        )

    # TODO: rename variables below - I think it can be some form of "base" and "additional"

    # calculate BTUs of residential energy use from urban areas
    # change URB_ENERGY_BTU based on urban_pop_percent

    # change in BTU/person from change in urban population and change in amount of energy consumption
    urban_btu = btu_used(urban_pop_percent, URB_ENERGY_BTU)

    # these are the base amounts, will be added to/subtracted below, depending on change in %
    # of energy use that is electric
    UrbanResElecBTUUsed = urban_btu * (URB_ENERGY_ELEC / 100)
    UrbanResElecSpaceHeatingBTUUsed = UrbanResElecBTUUsed * URB_ELEC_SPACE
    UrbanResElecWaterHeatingBTUUsed = UrbanResElecBTUUsed * URB_ELEC_WATER
    UrbanResElecOtherBTUUsed = UrbanResElecBTUUsed * URB_ELEC_OTHER

    UrbanResNGBTUUsed = urban_btu * (URB_ENERGY_NG / 100)
    UrbanResNGSpaceHeatingBTUUsed = UrbanResNGBTUUsed * URB_NG_SPACE
    UrbanResNGWaterHeatingBTUUsed = UrbanResNGBTUUsed * URB_NG_WATER
    UrbanResNGOtherBTUUsed = UrbanResNGBTUUsed * URB_NG_OTHER

    UrbanResFOKerBTUUsed = urban_btu * (URB_ENERGY_FOK / 100)
    UrbanResFOKerSpaceHeatingBTUUsed = UrbanResFOKerBTUUsed * URB_FOK_SPACE
    UrbanResFOKerWaterHeatingBTUUsed = UrbanResFOKerBTUUsed * URB_FOK_WATER
    UrbanResFOKerOtherBTUUsed = UrbanResFOKerBTUUsed * URB_FOK_OTHER

    UrbanResLPGBTUUsed = urban_btu * (URB_ENERGY_LPG / 100)
    UrbanResLPGSpaceHeatingBTUUsed = UrbanResLPGBTUUsed * URB_LPG_SPACE
    UrbanResLPGWaterHeatingBTUUsed = UrbanResLPGBTUUsed * URB_LPG_WATER
    UrbanResLPGOtherBTUUsed = UrbanResLPGBTUUsed * URB_LPG_OTHER

    #########
    # BTU change resulting from change in % subsector energy use that is electric

    change_in_electric_use = urb_energy_elec - URB_ENERGY_ELEC

    # Determine whether fossil fuels (and all uses) are switched to electricity or if electricity
    # heating uses are switched to fossil fuel heating uses
    if change_in_electric_use >= 0:  # less FF used

        # Fuel Switch to Electric
        UrbanResNGSpaceHeatingToElecBTUUsed = (
            urban_btu * (change_in_electric_use / 100) * URB_FF_NG * URB_NG_SPACE
        )
        UrbanResNGWaterHeatingToElecBTUUsed = (
            urban_btu * (change_in_electric_use / 100) * URB_FF_NG * URB_NG_WATER
        )
        UrbanResNGOtherToElecBTUUsed = (
            urban_btu * (change_in_electric_use / 100) * URB_FF_NG * URB_NG_OTHER
        )
        UrbanResFOKerSpaceHeatingToElecBTUUsed = (
            urban_btu * (change_in_electric_use / 100) * URB_FF_FOK * URB_FOK_SPACE
        )
        UrbanResFOKerWaterHeatingToElecBTUUsed = (
            urban_btu * (change_in_electric_use / 100) * URB_FF_FOK * URB_FOK_WATER
        )
        UrbanResFOKerOtherToElecBTUUsed = (
            urban_btu * (change_in_electric_use / 100) * URB_FF_FOK * URB_FOK_OTHER
        )
        UrbanResLPGSpaceHeatingToElecBTUUsed = (
            urban_btu * (change_in_electric_use / 100) * URB_FF_LPG * URB_LPG_SPACE
        )
        UrbanResLPGWaterHeatingToElecBTUUsed = (
            urban_btu * (change_in_electric_use / 100) * URB_FF_LPG * URB_LPG_WATER
        )
        UrbanResLPGOtherToElecBTUUsed = (
            urban_btu * (change_in_electric_use / 100) * URB_FF_LPG * URB_LPG_OTHER
        )

        urban_elec_btu = (
            (UrbanResElecSpaceHeatingBTUUsed / RES_ELEC_SPACE_USEFUL)
            + (UrbanResElecWaterHeatingBTUUsed / RES_ELEC_WATER_USEFUL)
            + (UrbanResElecOtherBTUUsed / RES_ELEC_OTHER_USEFUL)
            + (
                (
                    UrbanResNGSpaceHeatingToElecBTUUsed
                    + UrbanResFOKerSpaceHeatingToElecBTUUsed
                    + UrbanResLPGSpaceHeatingToElecBTUUsed
                )
                / RES_ELEC_WATER_USEFUL_REPLACE_FF
            )
            + (
                (
                    UrbanResNGWaterHeatingToElecBTUUsed
                    + UrbanResFOKerWaterHeatingToElecBTUUsed
                    + UrbanResLPGWaterHeatingToElecBTUUsed
                )
                / RES_ELEC_OTHER_USEFUL_REPLACE_FF
            )
            + (
                (
                    UrbanResNGOtherToElecBTUUsed
                    + UrbanResFOKerOtherToElecBTUUsed
                    + UrbanResLPGOtherToElecBTUUsed
                )
                / RES_ELEC_OTHER_USEFUL
            )
        )
        urban_ng_btu = (
            (
                (UrbanResNGSpaceHeatingBTUUsed - UrbanResNGSpaceHeatingToElecBTUUsed)
                / RES_NG_SPACE_USEFUL
            )
            + (
                (UrbanResNGWaterHeatingBTUUsed - UrbanResNGWaterHeatingToElecBTUUsed)
                / RES_NG_WATER_USEFUL
            )
            + ((UrbanResNGOtherBTUUsed - UrbanResNGOtherToElecBTUUsed) / RES_NG_OTHER_USEFUL)
        )
        urban_fok_btu = (
            (
                (UrbanResFOKerSpaceHeatingBTUUsed - UrbanResFOKerSpaceHeatingToElecBTUUsed)
                / RES_FOK_SPACE_USEFUL
            )
            + (
                (UrbanResFOKerWaterHeatingBTUUsed - UrbanResFOKerWaterHeatingToElecBTUUsed)
                / RES_FOK_WATER_USEFUL
            )
            + ((UrbanResFOKerOtherBTUUsed - UrbanResFOKerOtherToElecBTUUsed) / RES_FOK_OTHER_USEFUL)
        )
        urban_lpg_btu = (
            (
                (UrbanResLPGSpaceHeatingBTUUsed - UrbanResLPGSpaceHeatingToElecBTUUsed)
                / RES_LPG_SPACE_USEFUL
            )
            + (
                (UrbanResLPGWaterHeatingBTUUsed - UrbanResLPGWaterHeatingToElecBTUUsed)
                / RES_LPG_WATER_USEFUL
            )
            + ((UrbanResLPGOtherBTUUsed - UrbanResLPGOtherToElecBTUUsed) / RES_LPG_OTHER_USEFUL)
        )
    else:  # more FF used
        # Fuel Switch to Fossil Fuels heating uses
        UrbanResElecToNGSpaceHeatingBTUUsed = (
            UrbanResElecBTUUsed
            * (-(change_in_electric_use) / 100)
            * URB_ELEC_HEAT_SPACE
            * URB_FF_SPACE_NG
        )
        print(UrbanResElecToNGSpaceHeatingBTUUsed)

        UrbanResElecToNGWaterHeatingBTUUsed = (
            UrbanResElecBTUUsed
            * (-(change_in_electric_use) / 100)
            * URB_ELEC_HEAT_WATER
            * URB_FF_WATER_NG
        )

        UrbanResElecToFOKerSpaceHeatingBTUUsed = (
            UrbanResElecBTUUsed
            * (-(change_in_electric_use) / 100)
            * URB_ELEC_HEAT_SPACE
            * URB_FF_SPACE_FOK
        )

        UrbanResElecToFOKerWaterHeatingBTUUsed = (
            UrbanResElecBTUUsed
            * (-(change_in_electric_use) / 100)
            * URB_ELEC_HEAT_WATER
            * URB_FF_WATER_FOK
        )

        UrbanResElecToLPGSpaceHeatingBTUUsed = (
            UrbanResElecBTUUsed
            * (-(change_in_electric_use) / 100)
            * URB_ELEC_HEAT_SPACE
            * URB_FF_SPACE_LPG
        )

        UrbanResElecToLPGWaterHeatingBTUUsed = (
            UrbanResElecBTUUsed
            * (-(change_in_electric_use) / 100)
            * URB_ELEC_HEAT_WATER
            * URB_FF_WATER_LPG
        )

        urban_elec_btu = (
            (UrbanResElecOtherBTUUsed / RES_ELEC_OTHER_USEFUL)
            + (
                (
                    UrbanResElecSpaceHeatingBTUUsed
                    - (
                        UrbanResElecToNGSpaceHeatingBTUUsed
                        + UrbanResElecToFOKerSpaceHeatingBTUUsed
                        + UrbanResElecToLPGSpaceHeatingBTUUsed
                    )
                )
                / RES_ELEC_SPACE_USEFUL
            )
            + (
                (
                    UrbanResElecWaterHeatingBTUUsed
                    - (
                        UrbanResElecToNGWaterHeatingBTUUsed
                        + UrbanResElecToFOKerWaterHeatingBTUUsed
                        + UrbanResElecToLPGWaterHeatingBTUUsed
                    )
                )
                / RES_ELEC_WATER_USEFUL
            )
        )
        urban_ng_btu = (
            (UrbanResNGOtherBTUUsed / RES_NG_OTHER_USEFUL)
            + (
                (UrbanResNGSpaceHeatingBTUUsed + UrbanResElecToNGSpaceHeatingBTUUsed)
                / RES_NG_SPACE_USEFUL
            )
            + (
                (UrbanResNGWaterHeatingBTUUsed + UrbanResElecToNGWaterHeatingBTUUsed)
                / RES_NG_WATER_USEFUL
            )
        )
        urban_fok_btu = (
            (UrbanResFOKerOtherBTUUsed / RES_FOK_OTHER_USEFUL)
            + (
                (UrbanResFOKerSpaceHeatingBTUUsed + UrbanResElecToFOKerSpaceHeatingBTUUsed)
                / RES_FOK_SPACE_USEFUL
            )
            + (
                (UrbanResFOKerWaterHeatingBTUUsed + UrbanResElecToFOKerWaterHeatingBTUUsed)
                / RES_FOK_WATER_USEFUL
            )
        )
        urban_lpg_btu = (
            (UrbanResLPGOtherBTUUsed / RES_LPG_OTHER_USEFUL)
            + (
                (UrbanResLPGSpaceHeatingBTUUsed + UrbanResElecToLPGSpaceHeatingBTUUsed)
                / RES_LPG_SPACE_USEFUL
            )
            + (
                (UrbanResLPGWaterHeatingBTUUsed + UrbanResElecToLPGWaterHeatingBTUUsed)
                / RES_LPG_WATER_USEFUL
            )
        )

    sub_btu = btu_used(suburban_pop_percent, SUB_ENERGY_BTU)

    SuburbanPerChangedFossilFuelUsed = sub_energy_elec - SUB_ENERGY_ELEC
    suburban_per_res_elec_used_to_FF_heating = SUB_ENERGY_ELEC - sub_energy_elec

    SuburbanResElecBTUUsed = sub_btu * (SUB_ENERGY_ELEC / 100)
    SuburbanResElecSpaceHeatingBTUUsed = SuburbanResElecBTUUsed * SUB_ELEC_SPACE
    SuburbanResElecWaterHeatingBTUUsed = SuburbanResElecBTUUsed * SUB_ELEC_WATER
    SuburbanResElecOtherBTUUsed = SuburbanResElecBTUUsed * SUB_ELEC_OTHER

    SuburbanResNGBTUUsed = sub_btu * (SUB_ENERGY_NG / 100)
    SuburbanResNGSpaceHeatingBTUUsed = SuburbanResNGBTUUsed * SUB_NG_SPACE
    SuburbanResNGWaterHeatingBTUUsed = SuburbanResNGBTUUsed * SUB_NG_WATER
    SuburbanResNGOtherBTUUsed = SuburbanResNGBTUUsed * SUB_NG_OTHER

    SuburbanResFOKerBTUUsed = sub_btu * (SUB_ENERGY_FOK / 100)
    SuburbanResFOKerSpaceHeatingBTUUsed = SuburbanResFOKerBTUUsed * SUB_FOK_SPACE
    SuburbanResFOKerWaterHeatingBTUUsed = SuburbanResFOKerBTUUsed * SUB_FOK_WATER
    SuburbanResFOKerOtherBTUUsed = SuburbanResFOKerBTUUsed * SUB_FOK_OTHER

    SuburbanResLPGBTUUsed = sub_btu * (SUB_ENERGY_LPG / 100)
    SuburbanResLPGSpaceHeatingBTUUsed = SuburbanResLPGBTUUsed * SUB_LPG_SPACE
    SuburbanResLPGWaterHeatingBTUUsed = SuburbanResLPGBTUUsed * SUB_LPG_WATER
    SuburbanResLPGOtherBTUUsed = SuburbanResLPGBTUUsed * SUB_LPG_OTHER

    # Fuel Switch to Electric
    SuburbanResNGSpaceHeatingToElecBTUUsed = (
        sub_btu * (SuburbanPerChangedFossilFuelUsed / 100) * SUB_FF_NG * SUB_NG_SPACE
    )
    SuburbanResNGWaterHeatingToElecBTUUsed = (
        sub_btu * (SuburbanPerChangedFossilFuelUsed / 100) * SUB_FF_NG * SUB_NG_WATER
    )
    SuburbanResNGOtherToElecBTUUsed = (
        sub_btu * (SuburbanPerChangedFossilFuelUsed / 100) * SUB_FF_NG * SUB_NG_OTHER
    )
    SuburbanResFOKerSpaceHeatingToElecBTUUsed = (
        sub_btu * (SuburbanPerChangedFossilFuelUsed / 100) * SUB_FF_FOK * SUB_FOK_SPACE
    )
    SuburbanResFOKerWaterHeatingToElecBTUUsed = (
        sub_btu * (SuburbanPerChangedFossilFuelUsed / 100) * SUB_FF_FOK * SUB_FOK_WATER
    )
    SuburbanResFOKerOtherToElecBTUUsed = (
        sub_btu * (SuburbanPerChangedFossilFuelUsed / 100) * SUB_FF_FOK * SUB_FOK_OTHER
    )
    SuburbanResLPGSpaceHeatingToElecBTUUsed = (
        sub_btu * (SuburbanPerChangedFossilFuelUsed / 100) * SUB_FF_LPG * SUB_LPG_SPACE
    )
    SuburbanResLPGWaterHeatingToElecBTUUsed = (
        sub_btu * (SuburbanPerChangedFossilFuelUsed / 100) * SUB_FF_LPG * SUB_LPG_WATER
    )
    SuburbanResLPGOtherToElecBTUUsed = (
        sub_btu * (SuburbanPerChangedFossilFuelUsed / 100) * SUB_FF_LPG * SUB_LPG_OTHER
    )

    # Fuel Switch to Fossil Fuels heating uses
    SuburbanResElecToNGSpaceHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * SUB_ELEC_HEAT_SPACE
        * SUB_FF_SPACE_NG
    )

    SuburbanResElecToNGWaterHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * SUB_ELEC_HEAT_WATER
        * SUB_FF_WATER_NG
    )

    SuburbanResElecToFOKerSpaceHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * SUB_ELEC_HEAT_SPACE
        * SUB_FF_SPACE_FOK
    )

    SuburbanResElecToFOKerWaterHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * SUB_ELEC_HEAT_WATER
        * SUB_FF_WATER_FOK
    )

    SuburbanResElecToLPGSpaceHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * SUB_ELEC_HEAT_SPACE
        * SUB_FF_SPACE_LPG
    )

    SuburbanResElecToLPGWaterHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (suburban_per_res_elec_used_to_FF_heating / 100)
        * SUB_ELEC_HEAT_WATER
        * SUB_FF_WATER_LPG
    )

    # Determine whether fossil fuels (and all uses) are switched to electricity or if electricity
    # heating uses are switched to fossil fuel heating uses
    if SuburbanPerChangedFossilFuelUsed >= 0:
        suburban_elec_btu = (
            (SuburbanResElecSpaceHeatingBTUUsed / RES_ELEC_SPACE_USEFUL)
            + (SuburbanResElecWaterHeatingBTUUsed / RES_ELEC_WATER_USEFUL)
            + (SuburbanResElecOtherBTUUsed / RES_ELEC_OTHER_USEFUL)
            + (
                (
                    SuburbanResNGSpaceHeatingToElecBTUUsed
                    + SuburbanResFOKerSpaceHeatingToElecBTUUsed
                    + SuburbanResLPGSpaceHeatingToElecBTUUsed
                )
                / RES_ELEC_WATER_USEFUL_REPLACE_FF
            )
            + (
                (
                    SuburbanResNGWaterHeatingToElecBTUUsed
                    + SuburbanResFOKerWaterHeatingToElecBTUUsed
                    + SuburbanResLPGWaterHeatingToElecBTUUsed
                )
                / RES_ELEC_OTHER_USEFUL_REPLACE_FF
            )
            + (
                (
                    SuburbanResNGOtherToElecBTUUsed
                    + SuburbanResFOKerOtherToElecBTUUsed
                    + SuburbanResLPGOtherToElecBTUUsed
                )
                / RES_ELEC_OTHER_USEFUL
            )
        )
        suburban_ng_btu = (
            (
                (SuburbanResNGSpaceHeatingBTUUsed - SuburbanResNGSpaceHeatingToElecBTUUsed)
                / RES_NG_SPACE_USEFUL
            )
            + (
                (SuburbanResNGWaterHeatingBTUUsed - SuburbanResNGWaterHeatingToElecBTUUsed)
                / RES_NG_WATER_USEFUL
            )
            + ((SuburbanResNGOtherBTUUsed - SuburbanResNGOtherToElecBTUUsed) / RES_NG_OTHER_USEFUL)
        )
        suburban_fok_btu = (
            (
                (SuburbanResFOKerSpaceHeatingBTUUsed - SuburbanResFOKerSpaceHeatingToElecBTUUsed)
                / RES_FOK_SPACE_USEFUL
            )
            + (
                (SuburbanResFOKerWaterHeatingBTUUsed - SuburbanResFOKerWaterHeatingToElecBTUUsed)
                / RES_FOK_WATER_USEFUL
            )
            + (
                (SuburbanResFOKerOtherBTUUsed - SuburbanResFOKerOtherToElecBTUUsed)
                / RES_FOK_OTHER_USEFUL
            )
        )
        suburban_lpg_btu = (
            (
                (SuburbanResLPGSpaceHeatingBTUUsed - SuburbanResLPGSpaceHeatingToElecBTUUsed)
                / RES_LPG_SPACE_USEFUL
            )
            + (
                (SuburbanResLPGWaterHeatingBTUUsed - SuburbanResLPGWaterHeatingToElecBTUUsed)
                / RES_LPG_WATER_USEFUL
            )
            + (
                (SuburbanResLPGOtherBTUUsed - SuburbanResLPGOtherToElecBTUUsed)
                / RES_LPG_OTHER_USEFUL
            )
        )
    else:
        suburban_elec_btu = (
            (SuburbanResElecOtherBTUUsed / RES_ELEC_OTHER_USEFUL)
            + (
                (
                    SuburbanResElecSpaceHeatingBTUUsed
                    - (
                        SuburbanResElecToNGSpaceHeatingBTUUsed
                        + SuburbanResElecToFOKerSpaceHeatingBTUUsed
                        + SuburbanResElecToLPGSpaceHeatingBTUUsed
                    )
                )
                / RES_ELEC_SPACE_USEFUL
            )
            + (
                (
                    SuburbanResElecWaterHeatingBTUUsed
                    - (
                        SuburbanResElecToNGWaterHeatingBTUUsed
                        + SuburbanResElecToFOKerWaterHeatingBTUUsed
                        + SuburbanResElecToLPGWaterHeatingBTUUsed
                    )
                )
                / RES_ELEC_WATER_USEFUL
            )
        )
        suburban_ng_btu = (
            (SuburbanResNGOtherBTUUsed / RES_NG_OTHER_USEFUL)
            + (
                (SuburbanResNGSpaceHeatingBTUUsed + SuburbanResElecToNGSpaceHeatingBTUUsed)
                / RES_NG_SPACE_USEFUL
            )
            + (
                (SuburbanResNGWaterHeatingBTUUsed + SuburbanResElecToNGWaterHeatingBTUUsed)
                / RES_NG_WATER_USEFUL
            )
        )
        suburban_fok_btu = (
            (SuburbanResFOKerOtherBTUUsed / RES_FOK_OTHER_USEFUL)
            + (
                (SuburbanResFOKerSpaceHeatingBTUUsed + SuburbanResElecToFOKerSpaceHeatingBTUUsed)
                / RES_FOK_SPACE_USEFUL
            )
            + (
                (SuburbanResFOKerWaterHeatingBTUUsed + SuburbanResElecToFOKerWaterHeatingBTUUsed)
                / RES_FOK_WATER_USEFUL
            )
        )
        suburban_lpg_btu = (
            (SuburbanResLPGOtherBTUUsed / RES_LPG_OTHER_USEFUL)
            + (
                (SuburbanResLPGSpaceHeatingBTUUsed + SuburbanResElecToLPGSpaceHeatingBTUUsed)
                / RES_LPG_SPACE_USEFUL
            )
            + (
                (SuburbanResLPGWaterHeatingBTUUsed + SuburbanResElecToLPGWaterHeatingBTUUsed)
                / RES_LPG_WATER_USEFUL
            )
        )

    rur_btu = btu_used(rural_pop_percent, RUR_ENERGY_BTU)
    RuralPerChangedFossilFuelUsed = rur_energy_elec - RUR_ENERGY_ELEC
    rural_per_res_elec_used_to_FF_heating = RUR_ENERGY_ELEC - rur_energy_elec

    RuralResElecBTUUsed = rur_btu * (RUR_ENERGY_ELEC / 100)
    RuralResElecSpaceHeatingBTUUsed = RuralResElecBTUUsed * RUR_ELEC_SPACE
    RuralResElecWaterHeatingBTUUsed = RuralResElecBTUUsed * RUR_ELEC_WATER
    RuralResElecOtherBTUUsed = RuralResElecBTUUsed * RUR_ELEC_OTHER

    RuralResNGBTUUsed = rur_btu * (RUR_ENERGY_NG / 100)
    RuralResNGSpaceHeatingBTUUsed = RuralResNGBTUUsed * RUR_NG_SPACE
    RuralResNGWaterHeatingBTUUsed = RuralResNGBTUUsed * RUR_NG_WATER
    RuralResNGOtherBTUUsed = RuralResNGBTUUsed * RUR_NG_OTHER

    RuralResFOKerBTUUsed = rur_btu * (RUR_ENERGY_FOK / 100)
    RuralResFOKerSpaceHeatingBTUUsed = RuralResFOKerBTUUsed * RUR_FOK_SPACE
    RuralResFOKerWaterHeatingBTUUsed = RuralResFOKerBTUUsed * RUR_FOK_WATER
    RuralResFOKerOtherBTUUsed = RuralResFOKerBTUUsed * RUR_FOK_OTHER

    RuralResLPGBTUUsed = rur_btu * (RUR_ENERGY_LPG / 100)
    RuralResLPGSpaceHeatingBTUUsed = RuralResLPGBTUUsed * RUR_LPG_SPACE
    RuralResLPGWaterHeatingBTUUsed = RuralResLPGBTUUsed * RUR_LPG_WATER
    RuralResLPGOtherBTUUsed = RuralResLPGBTUUsed * RUR_LPG_OTHER

    # Fuel Switch to Electric
    RuralResNGSpaceHeatingToElecBTUUsed = (
        rur_btu * (RuralPerChangedFossilFuelUsed / 100) * RUR_FF_NG * RUR_NG_SPACE
    )
    RuralResNGWaterHeatingToElecBTUUsed = (
        rur_btu * (RuralPerChangedFossilFuelUsed / 100) * RUR_FF_NG * RUR_NG_WATER
    )
    RuralResNGOtherToElecBTUUsed = (
        rur_btu * (RuralPerChangedFossilFuelUsed / 100) * RUR_FF_NG * RUR_NG_OTHER
    )
    RuralResFOKerSpaceHeatingToElecBTUUsed = (
        rur_btu * (RuralPerChangedFossilFuelUsed / 100) * RUR_FF_FOK * RUR_FOK_SPACE
    )
    RuralResFOKerWaterHeatingToElecBTUUsed = (
        rur_btu * (RuralPerChangedFossilFuelUsed / 100) * RUR_FF_FOK * RUR_FOK_WATER
    )
    RuralResFOKerOtherToElecBTUUsed = (
        rur_btu * (RuralPerChangedFossilFuelUsed / 100) * RUR_FF_FOK * RUR_FOK_OTHER
    )
    RuralResLPGSpaceHeatingToElecBTUUsed = (
        rur_btu * (RuralPerChangedFossilFuelUsed / 100) * RUR_FF_LPG * RUR_LPG_SPACE
    )
    RuralResLPGWaterHeatingToElecBTUUsed = (
        rur_btu * (RuralPerChangedFossilFuelUsed / 100) * RUR_FF_LPG * RUR_LPG_WATER
    )
    RuralResLPGOtherToElecBTUUsed = (
        rur_btu * (RuralPerChangedFossilFuelUsed / 100) * RUR_FF_LPG * RUR_LPG_OTHER
    )

    # Fuel Switch to Fossil Fuels heating uses
    RuralResElecToNGSpaceHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * RUR_ELEC_HEAT_SPACE
        * RUR_FF_SPACE_NG
    )

    RuralResElecToNGWaterHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * RUR_ELEC_HEAT_WATER
        * RUR_FF_WATER_NG
    )

    RuralResElecToFOKerSpaceHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * RUR_ELEC_HEAT_SPACE
        * RUR_FF_SPACE_FOK
    )

    RuralResElecToFOKerWaterHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * RUR_ELEC_HEAT_WATER
        * RUR_FF_WATER_FOK
    )

    RuralResElecToLPGSpaceHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * RUR_ELEC_HEAT_SPACE
        * RUR_FF_SPACE_LPG
    )

    RuralResElecToLPGWaterHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (rural_per_res_elec_used_to_FF_heating / 100)
        * RUR_ELEC_HEAT_WATER
        * RUR_FF_WATER_LPG
    )

    # Determine whether fossil fuels (and all uses) are switched to electricity or if electricity
    # heating uses are switched to fossil fuel heating uses
    if RuralPerChangedFossilFuelUsed >= 0:
        rural_elec_btu = (
            (RuralResElecSpaceHeatingBTUUsed / RES_ELEC_SPACE_USEFUL)
            + (RuralResElecWaterHeatingBTUUsed / RES_ELEC_WATER_USEFUL)
            + (RuralResElecOtherBTUUsed / RES_ELEC_OTHER_USEFUL)
            + (
                (
                    RuralResNGSpaceHeatingToElecBTUUsed
                    + RuralResFOKerSpaceHeatingToElecBTUUsed
                    + RuralResLPGSpaceHeatingToElecBTUUsed
                )
                / RES_ELEC_WATER_USEFUL_REPLACE_FF
            )
            + (
                (
                    RuralResNGWaterHeatingToElecBTUUsed
                    + RuralResFOKerWaterHeatingToElecBTUUsed
                    + RuralResLPGWaterHeatingToElecBTUUsed
                )
                / RES_ELEC_OTHER_USEFUL_REPLACE_FF
            )
            + (
                (
                    RuralResNGOtherToElecBTUUsed
                    + RuralResFOKerOtherToElecBTUUsed
                    + RuralResLPGOtherToElecBTUUsed
                )
                / RES_ELEC_OTHER_USEFUL
            )
        )
        rural_ng_btu = (
            (
                (RuralResNGSpaceHeatingBTUUsed - RuralResNGSpaceHeatingToElecBTUUsed)
                / RES_NG_SPACE_USEFUL
            )
            + (
                (RuralResNGWaterHeatingBTUUsed - RuralResNGWaterHeatingToElecBTUUsed)
                / RES_NG_WATER_USEFUL
            )
            + ((RuralResNGOtherBTUUsed - RuralResNGOtherToElecBTUUsed) / RES_NG_OTHER_USEFUL)
        )
        rural_fok_btu = (
            (
                (RuralResFOKerSpaceHeatingBTUUsed - RuralResFOKerSpaceHeatingToElecBTUUsed)
                / RES_FOK_SPACE_USEFUL
            )
            + (
                (RuralResFOKerWaterHeatingBTUUsed - RuralResFOKerWaterHeatingToElecBTUUsed)
                / RES_FOK_WATER_USEFUL
            )
            + ((RuralResFOKerOtherBTUUsed - RuralResFOKerOtherToElecBTUUsed) / RES_FOK_OTHER_USEFUL)
        )
        rural_lpg_btu = (
            (
                (RuralResLPGSpaceHeatingBTUUsed - RuralResLPGSpaceHeatingToElecBTUUsed)
                / RES_LPG_SPACE_USEFUL
            )
            + (
                (RuralResLPGWaterHeatingBTUUsed - RuralResLPGWaterHeatingToElecBTUUsed)
                / RES_LPG_WATER_USEFUL
            )
            + ((RuralResLPGOtherBTUUsed - RuralResLPGOtherToElecBTUUsed) / RES_LPG_OTHER_USEFUL)
        )
    else:
        rural_elec_btu = (
            (RuralResElecOtherBTUUsed / RES_ELEC_OTHER_USEFUL)
            + (
                (
                    RuralResElecSpaceHeatingBTUUsed
                    - (
                        RuralResElecToNGSpaceHeatingBTUUsed
                        + RuralResElecToFOKerSpaceHeatingBTUUsed
                        + RuralResElecToLPGSpaceHeatingBTUUsed
                    )
                )
                / RES_ELEC_SPACE_USEFUL
            )
            + (
                (
                    RuralResElecWaterHeatingBTUUsed
                    - (
                        RuralResElecToNGWaterHeatingBTUUsed
                        + RuralResElecToFOKerWaterHeatingBTUUsed
                        + RuralResElecToLPGWaterHeatingBTUUsed
                    )
                )
                / RES_ELEC_WATER_USEFUL
            )
        )
        rural_ng_btu = (
            (RuralResNGOtherBTUUsed / RES_NG_OTHER_USEFUL)
            + (
                (RuralResNGSpaceHeatingBTUUsed + RuralResElecToNGSpaceHeatingBTUUsed)
                / RES_NG_SPACE_USEFUL
            )
            + (
                (RuralResNGWaterHeatingBTUUsed + RuralResElecToNGWaterHeatingBTUUsed)
                / RES_NG_WATER_USEFUL
            )
        )
        rural_fok_btu = (
            (RuralResFOKerOtherBTUUsed / RES_FOK_OTHER_USEFUL)
            + (
                (RuralResFOKerSpaceHeatingBTUUsed + RuralResElecToFOKerSpaceHeatingBTUUsed)
                / RES_FOK_SPACE_USEFUL
            )
            + (
                (RuralResFOKerWaterHeatingBTUUsed + RuralResElecToFOKerWaterHeatingBTUUsed)
                / RES_FOK_WATER_USEFUL
            )
        )
        rural_lpg_btu = (
            (RuralResLPGOtherBTUUsed / RES_LPG_OTHER_USEFUL)
            + (
                (RuralResLPGSpaceHeatingBTUUsed + RuralResElecToLPGSpaceHeatingBTUUsed)
                / RES_LPG_SPACE_USEFUL
            )
            + (
                (RuralResLPGWaterHeatingBTUUsed + RuralResElecToLPGWaterHeatingBTUUsed)
                / RES_LPG_WATER_USEFUL
            )
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
    rur_energy_elec,
    sub_energy_elec,
    urb_energy_elec,
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
        rur_energy_elec,
        sub_energy_elec,
        urb_energy_elec,
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
                user_inputs["rur_energy_elec"],
                user_inputs["sub_energy_elec"],
                user_inputs["urb_energy_elec"],
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
                user_inputs["rur_energy_elec"],
                user_inputs["sub_energy_elec"],
                user_inputs["urb_energy_elec"],
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
                user_inputs["rur_energy_elec"],
                user_inputs["sub_energy_elec"],
                user_inputs["urb_energy_elec"],
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
                user_inputs["rur_energy_elec"],
                user_inputs["sub_energy_elec"],
                user_inputs["urb_energy_elec"],
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
        "urb_energy_elec": urb_energy_elec_slider.value,
        "sub_energy_elec": sub_energy_elec_slider.value,
        "rur_energy_elec": rur_energy_elec_slider.value,
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

# temporary data labels
labels_scenario = LabelSet(
    x=dodge("Category", 0.15, range=bar_chart.x_range),
    y="Scenario",
    x_offset=4,
    y_offset=5,
    text="Scenario",
    text_font_size="9px",
    angle=1.57,
    level="glyph",
    source=bar_chart_source,
)
labels_2015 = LabelSet(
    x=dodge("Category", 0.15, range=bar_chart.x_range),
    y="2015",
    x_offset=-10,
    y_offset=5,
    text="2015",
    text_font_size="9px",
    angle=1.57,
    level="glyph",
    source=bar_chart_source,
)
bar_chart.add_layout(labels_scenario)
bar_chart.add_layout(labels_2015)


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
urb_energy_elec_slider = Slider(
    start=URB_ELEC_OTHER_BTU / URB_ENERGY_BTU * 100,
    end=100,
    value=URB_ENERGY_ELEC,
    step=1,
    title="% Electrification of Residential End Uses in Urban Areas",
)
urb_energy_elec_slider.on_change("value", callback)

sub_energy_elec_slider = Slider(
    start=SUB_ELEC_OTHER_BTU / SUB_ENERGY_BTU * 100,
    end=100,
    value=SUB_ENERGY_ELEC,
    step=1,
    title="% Electrification of Residential End Uses in Suburban Areas",
)
sub_energy_elec_slider.on_change("value", callback)

rur_energy_elec_slider = Slider(
    start=RUR_ELEC_OTHER_BTU / RUR_ENERGY_BTU * 100,
    end=100,
    value=RUR_ENERGY_ELEC,
    step=1,
    title="% Electrification of Residential End Uses in Rural Areas",
)
rur_energy_elec_slider.on_change("value", callback)

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
    urb_energy_elec_slider,
    sub_energy_elec_slider,
    rur_energy_elec_slider,
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
