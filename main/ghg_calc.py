from math import pi
from statistics import mean

import numpy as np
import pandas as pd

from bokeh.layouts import column
from bokeh.models import Slider, Column, ColumnDataSource, TextInput, Paragraph, LabelSet
from bokeh.palettes import Viridis7, Spectral10
from bokeh.plotting import figure, curdoc
from bokeh.transform import dodge, cumsum


SECTORS = [
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
GHG_IP = 5.52  # industrial processes; includes Hydrogen production, iron & steel production, industrial wastewater treatment, ODS substitutes, and petroleum refining
GHG_URBAN_TREES = -1.025
GHG_FORESTS = -1.109
GHG_FOREST_CHANGE = 0.380  # TODO: why is this not 0?
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

URBAN_POP_PERCENT = URBAN_POP / POP * 100
SUBURBAN_POP_PERCENT = SUBURBAN_POP / POP * 100
RURAL_POP_PERCENT = RURAL_POP / POP * 100

# Average Emissions pr MWh of fossil fuels from eGRID 2014/2016 for RFCE
# NOTE: Future reference - should we pull plant-level data for this?)
CO2_LB_MWH_COAL = (2169.484351 + 2225.525) / 2
CO2_LB_MWH_OIL = (1600.098812 + 1341.468) / 2
CO2_LB_MWH_NG = (929.651872 + 897.037) / 2
CO2_LB_MWH_OTHER_FF = (1488.036692 + 1334.201) / 2

# Percent of carbon emissions from combustion of fossil fuels for electricity that are captured and stored
ff_carbon_capture = 0

# Electricity Mix from 2015 inventory
GRID_COAL = 20.47
GRID_OIL = 0.47
GRID_NG = 34.38
GRID_OTHER_FF = 0.46
GRID_BIO = 1.59
GRID_HYDRO = 1.06
GRID_NUCLEAR = 40.10
GRID_WIND = 1.16
GRID_SOLAR = 0.30
GRID_GEO = 0.00
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

# share of total energy/sector by energy type
URB_ENERGY_ELEC = URB_ELEC_BTU / URB_ENERGY_BTU
URB_ENERGY_NG = URB_NG_BTU / URB_ENERGY_BTU
URB_ENERGY_FOK = URB_FOK_BTU / URB_ENERGY_BTU
URB_ENERGY_LPG = URB_LPG_BTU / URB_ENERGY_BTU
SUB_ENERGY_ELEC = SUB_ELEC_BTU / SUB_ENERGY_BTU
SUB_ENERGY_NG = SUB_NG_BTU / SUB_ENERGY_BTU
SUB_ENERGY_FOK = SUB_FOK_BTU / SUB_ENERGY_BTU
SUB_ENERGY_LPG = SUB_LPG_BTU / SUB_ENERGY_BTU
RUR_ENERGY_ELEC = RUR_ELEC_BTU / RUR_ENERGY_BTU
RUR_ENERGY_NG = RUR_NB_BTU / RUR_ENERGY_BTU
RUR_ENERGY_FOK = RUR_FOK_BTU / RUR_ENERGY_BTU
RUR_ENERGY_LPG = RUR_LPG_BTU / RUR_ENERGY_BTU

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

# share of fuel that is converted to useful energy
CI_ELEC_USEFUL = 1
CI_NG_USEFUL = 0.75
CI_COAL_USEFUL = 0.85
CI_DFO_USEFUL = 0.80
CI_K_USEFUL = 0.80
CI_LPG_USEFUL = 0.80
CI_MOTOR_GAS_USEFUL = 0.80
CI_RFO_USEFUL = 0.80
CI_PET_COKE_USEFUL = 0.80
CI_STILL_GAS_USEFUL = 0.80
CI_NAPHTHAS_USEFUL = 0.80

# useful BTUs consumed
CI_ELEC_BTU = 119120.51 * CI_ELEC_USEFUL
CI_NG_BTU = 145987.03 * CI_NG_USEFUL
CI_COAL_BTU = 6581.08 * CI_COAL_USEFUL
CI_DFO_BTU = 24342.05 * CI_DFO_USEFUL
CI_K_BTU = 41.91 * CI_K_USEFUL
CI_LPG_BTU = 2581.22 * CI_LPG_USEFUL
CI_MOTOR_GAS_BTU = 12584.78 * CI_MOTOR_GAS_USEFUL
CI_RFO_BTU = 261.42 * CI_RFO_USEFUL
CI_PET_COKE_BTU = 15067.33 * CI_PET_COKE_USEFUL
CI_STILL_GAS_BTU = 25628.52 * CI_STILL_GAS_USEFUL
CI_NAPHTHAS_BTU = 73.71 * CI_NAPHTHAS_USEFUL

CI_ENERGY_BTU = (
    CI_ELEC_BTU
    + CI_NG_BTU
    + CI_COAL_BTU
    + CI_DFO_BTU
    + CI_K_BTU
    + CI_LPG_BTU
    + CI_MOTOR_GAS_BTU
    + CI_RFO_BTU
    + CI_PET_COKE_BTU
    + CI_STILL_GAS_BTU
    + CI_NAPHTHAS_BTU
)

# percent of energy by fuel type
CI_ENERGY_ELEC = CI_ELEC_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_NG = CI_NG_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_COAL = CI_COAL_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_DFO = CI_DFO_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_K = CI_K_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_LPG = CI_LPG_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_MOTOR_GAS = CI_MOTOR_GAS_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_RFO = CI_RFO_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_PET_COKE = CI_PET_COKE_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_STILL_GAS = CI_STILL_GAS_BTU / CI_ENERGY_BTU * 100
CI_ENERGY_NAPHTHAS = CI_NAPHTHAS_BTU / CI_ENERGY_BTU * 100

# share of FF energy by individual FF
CI_ENERGY_FF = 100 - CI_ENERGY_ELEC
CI_ENERGY_FF_NG = CI_ENERGY_NG / CI_ENERGY_FF
CI_ENERGY_FF_COAL = CI_ENERGY_COAL / CI_ENERGY_FF
CI_ENERGY_FF_DFO = CI_ENERGY_DFO / CI_ENERGY_FF
CI_ENERGY_FF_K = CI_ENERGY_K / CI_ENERGY_FF
CI_ENERGY_FF_LPG = CI_ENERGY_LPG / CI_ENERGY_FF
CI_ENERGY_FF_MOTOR_GAS = CI_ENERGY_MOTOR_GAS / CI_ENERGY_FF
CI_ENERGY_FF_RFO = CI_ENERGY_RFO / CI_ENERGY_FF
CI_ENERGY_FF_PET_COKE = CI_ENERGY_PET_COKE / CI_ENERGY_FF
CI_ENERGY_FF_STILL_GAS = CI_ENERGY_STILL_GAS / CI_ENERGY_FF
CI_ENERGY_FF_NAPHTHAS = CI_ENERGY_NAPHTHAS / CI_ENERGY_FF

############################
# Mobile-Highway GHG Factors

URB_VEH_MILES = 5041.95
SUB_VEH_MILES = 7405.38
RUR_VEH_MILES = 6591.47
ELEC_VEH_EFFICIENCY = 0.3  # kWh/mile
REG_FLEET_MPG = 19.744607425  # mpg imputed from 2015 inventory
CO2_LB_GAL_GAS = 20.50758459351  # lbs co2e per gallon of gasoline (imputed from 2015 inventory)

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

# create dictionary (and set initial values) of all variables that user can change
# will be passed to functions that create charts
user_inputs = {
    "ci_energy_elec": CI_ENERGY_ELEC,
    "FreightRailPerElecMotion": FreightRailPerElecMotion,
    "grid_coal": GRID_COAL,
    "grid_oil": GRID_OIL,
    "grid_ng": GRID_NG,
    "grid_nuclear": GRID_NUCLEAR,
    "grid_solar": GRID_SOLAR,
    "grid_wind": GRID_WIND,
    "grid_bio": GRID_BIO,
    "grid_hydro": GRID_HYDRO,
    "grid_geo": GRID_GEO,
    "grid_other_ff": GRID_OTHER_FF,
    "InterCityRailPerElecMotion": InterCityRailPerElecMotion,
    "MarinePortPerElectrification": MarinePortPerElectrification,
    "OffroadPerElectrification": OffroadPerElectrification,
    "change_ag": 0,
    "change_air_travel": 0,
    "res_energy_change": 0,
    "ff_carbon_capture": ff_carbon_capture,
    "ci_energy_change": 0,
    "veh_miles_elec": 0,
    "change_forest": 0,
    "PerFreightRail": PerFreightRail,
    "PerInterCityRail": PerInterCityRail,
    "change_industrial_processes": 0,
    "PerMarinePort": PerMarinePort,
    "PerOffroad": PerOffroad,
    "PerTransRailRidership": PerTransRailRidership,
    "change_urban_trees": 0,
    "change_solid_waste": 0,
    "change_wastewater": 0,
    "change_pop": 0,
    "reg_fleet_mpg": REG_FLEET_MPG,
    "rur_energy_elec": RUR_ENERGY_ELEC * 100,  # convert to % b/c func will take user % later
    "rural_pop_percent": RURAL_POP_PERCENT,
    "sub_energy_elec": SUB_ENERGY_ELEC * 100,  # convert to % b/c func will take user % later
    "suburban_pop_percent": SUBURBAN_POP_PERCENT,
    "TransRailRuralPerElecMotion": TransRailRuralPerElecMotion,
    "TransRailSuburbanPerElecMotion": TransRailSuburbanPerElecMotion,
    "TransRailUrbanPerElecMotion": TransRailUrbanPerElecMotion,
    "urb_energy_elec": URB_ENERGY_ELEC * 100,  # convert to % b/c func will take user % later
    "urban_pop_percent": URBAN_POP_PERCENT,
    "change_veh_miles": 0,
}


def calc_res_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    res_energy_change,
    change_pop,
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

    def calc_btu_by_res_sector(
        pop_percent,
        energy_btu,
        energy_elec,
        new_energy_elec,
        energy_ng,
        energy_fok,
        energy_lpg,
        elec_space,
        elec_water,
        elec_other,
        ng_space,
        ng_water,
        ng_other,
        fok_space,
        fok_water,
        fok_other,
        lpg_space,
        lpg_water,
        lpg_other,
        ff_ng,
        ff_fok,
        ff_lpg,
        elec_heat_space,
        elec_heat_water,
        ff_space_ng,
        ff_water_ng,
        ff_space_fok,
        ff_water_fok,
        ff_space_lpg,
        ff_water_lpg,
    ):
        """Calculate BTUs by residential sub-sector."""

        # change in BTU/per from change in sub-sector pop & change in amt of energy consumption
        btu = (
            POP
            * (1 + change_pop / 100)
            * (pop_percent / 100)
            * energy_btu
            * (1 + res_energy_change / 100)
        )

        # calculate the base amounts, which will be adjusted below depending on change in %
        # of energy use that is electric
        base_elec_btu = btu * energy_elec
        base_elec_space_btu = base_elec_btu * elec_space
        base_elec_water_btu = base_elec_btu * elec_water
        base_elec_other_btu = base_elec_btu * elec_other

        base_ng_btu = btu * energy_ng
        base_ng_space_btu = base_ng_btu * ng_space
        base_ng_water_btu = base_ng_btu * ng_water
        base_ng_other_btu = base_ng_btu * ng_other

        base_fok_btu = btu * energy_fok
        base_fok_space_btu = base_fok_btu * fok_space
        base_fok_water_btu = base_fok_btu * fok_water
        base_fok_other_btu = base_fok_btu * fok_other

        base_lpg_btu = btu * energy_lpg
        base_lpg_space_btu = base_lpg_btu * lpg_space
        base_lpg_water_btu = base_lpg_btu * lpg_water
        base_lpg_other_btu = base_lpg_btu * lpg_other

        #######
        # BTU/per change resulting from change in % subsector energy use that is electric
        # switch fossil fuels (and all uses) to electricity or electricity heating uses to ff

        change_elec_use = (new_energy_elec / 100) - energy_elec

        if change_elec_use >= 0:  # more energy is electric, therefore less FF used
            ng_space_btu_to_elec = btu * change_elec_use * ff_ng * ng_space
            ng_water_btu_to_elec = btu * change_elec_use * ff_ng * ng_water
            ng_other_btu_to_elec = btu * change_elec_use * ff_ng * ng_other
            fok_space_btu_to_elec = btu * change_elec_use * ff_fok * fok_space
            fok_water_btu_to_elec = btu * change_elec_use * ff_fok * fok_water
            fok_other_btu_to_elec = btu * change_elec_use * ff_fok * fok_other
            lpg_space_btu_to_elec = btu * change_elec_use * ff_lpg * lpg_space
            lpg_water_btu_to_elec = btu * change_elec_use * ff_lpg * lpg_water
            lpg_other_btu_to_elec = btu * change_elec_use * ff_lpg * lpg_other

            elec_btu = (
                (base_elec_space_btu / RES_ELEC_SPACE_USEFUL)
                + (base_elec_water_btu / RES_ELEC_WATER_USEFUL)
                + (base_elec_other_btu / RES_ELEC_OTHER_USEFUL)
                + (
                    (ng_space_btu_to_elec + fok_space_btu_to_elec + lpg_space_btu_to_elec)
                    / RES_ELEC_WATER_USEFUL_REPLACE_FF
                )
                + (
                    (ng_water_btu_to_elec + fok_water_btu_to_elec + lpg_water_btu_to_elec)
                    / RES_ELEC_OTHER_USEFUL_REPLACE_FF
                )
                + (
                    (ng_other_btu_to_elec + fok_other_btu_to_elec + lpg_other_btu_to_elec)
                    / RES_ELEC_OTHER_USEFUL
                )
            )
            ng_btu = (
                ((base_ng_space_btu - ng_space_btu_to_elec) / RES_NG_SPACE_USEFUL)
                + ((base_ng_water_btu - ng_water_btu_to_elec) / RES_NG_WATER_USEFUL)
                + ((base_ng_other_btu - ng_other_btu_to_elec) / RES_NG_OTHER_USEFUL)
            )
            fok_btu = (
                ((base_fok_space_btu - fok_space_btu_to_elec) / RES_FOK_SPACE_USEFUL)
                + ((base_fok_water_btu - fok_water_btu_to_elec) / RES_FOK_WATER_USEFUL)
                + ((base_fok_other_btu - fok_other_btu_to_elec) / RES_FOK_OTHER_USEFUL)
            )
            lpg_btu = (
                ((base_lpg_space_btu - lpg_space_btu_to_elec) / RES_LPG_SPACE_USEFUL)
                + ((base_lpg_water_btu - lpg_water_btu_to_elec) / RES_LPG_WATER_USEFUL)
                + ((base_lpg_other_btu - lpg_other_btu_to_elec) / RES_LPG_OTHER_USEFUL)
            )
        else:  # less energy is electric, therefore more FF used
            elec_space_btu_to_ng = base_elec_btu * -change_elec_use * elec_heat_space * ff_space_ng

            elec_water_btu_to_ng = base_elec_btu * -change_elec_use * elec_heat_water * ff_water_ng

            elec_space_btu_to_fok = (
                base_elec_btu * -change_elec_use * elec_heat_space * ff_space_fok
            )

            elec_water_btu_to_fok = (
                base_elec_btu * -change_elec_use * elec_heat_water * ff_water_fok
            )

            elec_space_btu_to_lpg = (
                base_elec_btu * -change_elec_use * elec_heat_space * ff_space_lpg
            )

            elec_water_btu_to_lpg = (
                base_elec_btu * -change_elec_use * elec_heat_water * ff_water_lpg
            )

            elec_btu = (
                (base_elec_other_btu / RES_ELEC_OTHER_USEFUL)
                + (
                    (
                        base_elec_space_btu
                        - (elec_space_btu_to_ng + elec_space_btu_to_fok + elec_space_btu_to_lpg)
                    )
                    / RES_ELEC_SPACE_USEFUL
                )
                + (
                    (
                        base_elec_water_btu
                        - (elec_water_btu_to_ng + elec_water_btu_to_fok + elec_water_btu_to_lpg)
                    )
                    / RES_ELEC_WATER_USEFUL
                )
            )
            ng_btu = (
                (base_ng_other_btu / RES_NG_OTHER_USEFUL)
                + ((base_ng_space_btu + elec_space_btu_to_ng) / RES_NG_SPACE_USEFUL)
                + ((base_ng_water_btu + elec_water_btu_to_ng) / RES_NG_WATER_USEFUL)
            )
            fok_btu = (
                (base_fok_other_btu / RES_FOK_OTHER_USEFUL)
                + ((base_fok_space_btu + elec_space_btu_to_fok) / RES_FOK_SPACE_USEFUL)
                + ((base_fok_water_btu + elec_water_btu_to_fok) / RES_FOK_WATER_USEFUL)
            )
            lpg_btu = (
                (base_lpg_other_btu / RES_LPG_OTHER_USEFUL)
                + ((base_lpg_space_btu + elec_space_btu_to_lpg) / RES_LPG_SPACE_USEFUL)
                + ((base_lpg_water_btu + elec_water_btu_to_lpg) / RES_LPG_WATER_USEFUL)
            )
        return elec_btu, ng_btu, fok_btu, lpg_btu

    urban_elec_btu, urban_ng_btu, urban_fok_btu, urban_lpg_btu = calc_btu_by_res_sector(
        urban_pop_percent,
        URB_ENERGY_BTU,
        URB_ENERGY_ELEC,
        urb_energy_elec,
        URB_ENERGY_NG,
        URB_ENERGY_FOK,
        URB_ENERGY_LPG,
        URB_ELEC_SPACE,
        URB_ELEC_WATER,
        URB_ELEC_OTHER,
        URB_NG_SPACE,
        URB_NG_WATER,
        URB_NG_OTHER,
        URB_FOK_SPACE,
        URB_FOK_WATER,
        URB_FOK_OTHER,
        URB_LPG_SPACE,
        URB_LPG_WATER,
        URB_LPG_OTHER,
        URB_FF_NG,
        URB_FF_FOK,
        URB_FF_LPG,
        URB_ELEC_HEAT_SPACE,
        URB_ELEC_HEAT_WATER,
        URB_FF_SPACE_NG,
        URB_FF_WATER_NG,
        URB_FF_SPACE_FOK,
        URB_FF_WATER_FOK,
        URB_FF_SPACE_LPG,
        URB_FF_WATER_LPG,
    )

    suburban_elec_btu, suburban_ng_btu, suburban_fok_btu, suburban_lpg_btu = calc_btu_by_res_sector(
        suburban_pop_percent,
        SUB_ENERGY_BTU,
        SUB_ENERGY_ELEC,
        sub_energy_elec,
        SUB_ENERGY_NG,
        SUB_ENERGY_FOK,
        SUB_ENERGY_LPG,
        SUB_ELEC_SPACE,
        SUB_ELEC_WATER,
        SUB_ELEC_OTHER,
        SUB_NG_SPACE,
        SUB_NG_WATER,
        SUB_NG_OTHER,
        SUB_FOK_SPACE,
        SUB_FOK_WATER,
        SUB_FOK_OTHER,
        SUB_LPG_SPACE,
        SUB_LPG_WATER,
        SUB_LPG_OTHER,
        SUB_FF_NG,
        SUB_FF_FOK,
        SUB_FF_LPG,
        SUB_ELEC_HEAT_SPACE,
        SUB_ELEC_HEAT_WATER,
        SUB_FF_SPACE_NG,
        SUB_FF_WATER_NG,
        SUB_FF_SPACE_FOK,
        SUB_FF_WATER_FOK,
        SUB_FF_SPACE_LPG,
        SUB_FF_WATER_LPG,
    )
    rural_elec_btu, rural_ng_btu, rural_fok_btu, rural_lpg_btu = calc_btu_by_res_sector(
        rural_pop_percent,
        RUR_ENERGY_BTU,
        RUR_ENERGY_ELEC,
        rur_energy_elec,
        RUR_ENERGY_NG,
        RUR_ENERGY_FOK,
        RUR_ENERGY_LPG,
        RUR_ELEC_SPACE,
        RUR_ELEC_WATER,
        RUR_ELEC_OTHER,
        RUR_NG_SPACE,
        RUR_NG_WATER,
        RUR_NG_OTHER,
        RUR_FOK_SPACE,
        RUR_FOK_WATER,
        RUR_FOK_OTHER,
        RUR_LPG_SPACE,
        RUR_LPG_WATER,
        RUR_LPG_OTHER,
        RUR_FF_NG,
        RUR_FF_FOK,
        RUR_FF_LPG,
        RUR_ELEC_HEAT_SPACE,
        RUR_ELEC_HEAT_WATER,
        RUR_FF_SPACE_NG,
        RUR_FF_WATER_NG,
        RUR_FF_SPACE_FOK,
        RUR_FF_WATER_FOK,
        RUR_FF_SPACE_LPG,
        RUR_FF_WATER_LPG,
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
    ci_energy_elec,
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    ff_carbon_capture,
    ci_energy_change,
):
    ci_ff = 100 - ci_energy_elec
    change_ff = (ci_ff - CI_ENERGY_FF) / CI_ENERGY_FF

    ci_elec_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_energy_elec / 100)
        / CI_ELEC_USEFUL
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

    ci_ng_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_NG
        / CI_NG_USEFUL
        * CO2_MMT_BBTU_NG
        * MT_TO_MMT
    )

    ci_coal_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_COAL
        / CI_COAL_USEFUL
        * CO2_MMT_BBTU_COAL
        * MT_TO_MMT
    )

    ci_dfo_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_DFO
        / CI_DFO_USEFUL
        * CO2_MMT_BBTU_DFO
        * MT_TO_MMT
    )

    ci_k_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_K
        / CI_K_USEFUL
        * CO2_MMT_BBTU_KER
        * MT_TO_MMT
    )

    ci_lpg_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_LPG
        / CI_LPG_USEFUL
        * CO2_MMT_BBTU_LPG
        * MT_TO_MMT
    )

    ci_motor_gas_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_MOTOR_GAS
        / CI_MOTOR_GAS_USEFUL
        * CO2_MMT_BBTU_MOTOR_GAS
        * MT_TO_MMT
    )

    ci_rfo_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_RFO
        / CI_RFO_USEFUL
        * CO2_MMT_BBTU_RFO
        * MT_TO_MMT
    )

    ci_pet_coke_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_PET_COKE
        / CI_PET_COKE_USEFUL
        * CO2_MMT_BBTU_PETCOKE
        * MT_TO_MMT
    )

    ci_still_gas_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_STILL_GAS
        / CI_STILL_GAS_USEFUL
        * CO2_MMT_BBTU_STILL_GAS
        * MT_TO_MMT
    )

    ci_naphthas_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_NAPHTHAS
        / CI_NAPHTHAS_USEFUL
        * CO2_MMT_BBTU_NAPHTHAS
        * MT_TO_MMT
    )

    return (
        ci_elec_ghg
        + ci_ng_ghg
        + ci_coal_ghg
        + ci_dfo_ghg
        + ci_k_ghg
        + ci_lpg_ghg
        + ci_motor_gas_ghg
        + ci_rfo_ghg
        + ci_pet_coke_ghg
        + ci_still_gas_ghg
        + ci_naphthas_ghg
    )


def calc_highway_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    ff_carbon_capture,
    veh_miles_elec,
    change_pop,
    reg_fleet_mpg,
    rural_pop_percent,
    suburban_pop_percent,
    urban_pop_percent,
    change_veh_miles,
):
    veh_miles_traveled = (
        (POP * urban_pop_percent / 100 * (1 + change_pop / 100) * URB_VEH_MILES)
        + (POP * suburban_pop_percent / 100 * (1 + change_pop / 100) * SUB_VEH_MILES)
        + (POP * rural_pop_percent / 100 * (1 + change_pop / 100) * RUR_VEH_MILES)
    ) * (1 + change_veh_miles / 100)

    elec_miles_percent = veh_miles_traveled * veh_miles_elec / 100

    highway_ghg = (
        veh_miles_traveled - elec_miles_percent
    ) / reg_fleet_mpg * CO2_LB_GAL_GAS * MMT_LB + (
        elec_miles_percent
        * ELEC_VEH_EFFICIENCY
        * 0.001
        / (1 - GRID_LOSS)
        * (
            (grid_coal / 100 * CO2_LB_MWH_COAL)
            + (grid_oil / 100 * CO2_LB_MWH_OIL)
            + (grid_ng / 100 * CO2_LB_MWH_NG)
            + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
        )
        * MMT_LB
    ) * (
        1 - ff_carbon_capture / 100
    )

    return highway_ghg


def calc_aviation_ghg(change_pop, change_air_travel):
    return GHG_AVIATION * (1 + change_pop / 100) * (1 + change_air_travel / 100)


def calc_transit_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    ff_carbon_capture,
    PerTransRailRidership,
    change_pop,
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
        * (1 + change_pop / 100)
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
        * (1 + change_pop / 100)
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
    ci_energy_elec,
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    change_ag,
    res_energy_change,
    ci_energy_change,
    change_forest,
    change_industrial_processes,
    change_urban_trees,
    change_solid_waste,
    change_wastewater,
    change_pop,
    rur_energy_elec,
    sub_energy_elec,
    urb_energy_elec,
    urban_pop_percent,  # TODO: why only urban_pop_percent and not sub and rural?
):
    AgricultureGHG = GHG_AG * (1 + change_ag / 100)
    SolidWasteGHG = GHG_SOLID_WASTE * (1 + change_solid_waste / 100) * (1 + change_pop / 100)
    WasteWaterGHG = GHG_WASTEWATER * (1 + change_wastewater / 100) * (1 + change_pop / 100)
    IndProcGHG = GHG_IP * (1 + change_industrial_processes / 100)

    ResNGConsumption = calc_res_ghg(
        grid_coal,
        grid_ng,
        grid_oil,
        grid_other_ff,
        res_energy_change,
        change_pop,
        rur_energy_elec,
        sub_energy_elec,
        urb_energy_elec,
        RURAL_POP_PERCENT,
        SUBURBAN_POP_PERCENT,
        urban_pop_percent,
    )[1]

    ci_ff = 100 - ci_energy_elec
    change_ff = (ci_ff - CI_ENERGY_FF) / CI_ENERGY_FF

    ComIndNGConsumption = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_NG
        / CI_NG_USEFUL
        * 1000000000
    )

    NGSystemsGHG = (
        (ResNGConsumption + ComIndNGConsumption)
        * (1 / BTU_CCF_AVG)
        * 100
        * 0.000001
        * (MMTCO2ePerMillionCFNG_CH4 + MMTCO2ePerMillionCFNG_CO2)
    )

    LULUCFGHG = GHG_URBAN_TREES * (1 + change_urban_trees / 100) + (
        GHG_FORESTS + GHG_FOREST_CHANGE
    ) * (1 + change_forest / 100)

    return AgricultureGHG + SolidWasteGHG + WasteWaterGHG + IndProcGHG + NGSystemsGHG + LULUCFGHG


def wrangle_data_for_bar_chart(user_inputs):
    data = {
        "Category": SECTORS,
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
                user_inputs["change_pop"],
                user_inputs["rur_energy_elec"],
                user_inputs["sub_energy_elec"],
                user_inputs["urb_energy_elec"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
            )[0],
            calc_ci_ghg(
                user_inputs["ci_energy_elec"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["ci_energy_change"],
            ),
            calc_highway_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["veh_miles_elec"],
                user_inputs["change_pop"],
                user_inputs["reg_fleet_mpg"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
                user_inputs["change_veh_miles"],
            ),
            calc_transit_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["PerTransRailRidership"],
                user_inputs["change_pop"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["TransRailUrbanPerElecMotion"],
                user_inputs["TransRailSuburbanPerElecMotion"],
                user_inputs["TransRailRuralPerElecMotion"],
                user_inputs["urban_pop_percent"],
            ),
            calc_aviation_ghg(user_inputs["change_pop"], user_inputs["change_air_travel"]),
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
                user_inputs["ci_energy_elec"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["change_ag"],
                user_inputs["res_energy_change"],
                user_inputs["ci_energy_change"],
                user_inputs["change_forest"],
                user_inputs["change_industrial_processes"],
                user_inputs["change_urban_trees"],
                user_inputs["change_solid_waste"],
                user_inputs["change_wastewater"],
                user_inputs["change_pop"],
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
                user_inputs["change_pop"],
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
                user_inputs["ci_energy_elec"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ff_carbon_capture"],
                user_inputs["ci_energy_change"],
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
                user_inputs["veh_miles_elec"],
                user_inputs["change_pop"],
                user_inputs["reg_fleet_mpg"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
                user_inputs["change_veh_miles"],
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
                user_inputs["change_pop"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["TransRailUrbanPerElecMotion"],
                user_inputs["TransRailSuburbanPerElecMotion"],
                user_inputs["TransRailRuralPerElecMotion"],
                user_inputs["urban_pop_percent"],
            ),
        ],
        "Mobile-Aviation": [
            GHG_AVIATION,
            calc_aviation_ghg(user_inputs["change_pop"], user_inputs["change_air_travel"]),
        ],
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
                user_inputs["ci_energy_elec"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["change_ag"],
                user_inputs["res_energy_change"],
                user_inputs["ci_energy_change"],
                user_inputs["change_forest"],
                user_inputs["change_industrial_processes"],
                user_inputs["change_urban_trees"],
                user_inputs["change_solid_waste"],
                user_inputs["change_wastewater"],
                user_inputs["change_pop"],
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
        "grid_coal": float(grid_coal_input.value),
        "grid_ng": float(grid_ng_input.value),
        "grid_oil": float(grid_oil_input.value),
        "grid_nuclear": float(grid_nuclear_input.value),
        "grid_solar": float(grid_solar_input.value),
        "grid_wind": float(grid_wind_input.value),
        "grid_bio": float(grid_bio_input.value),
        "grid_hydro": float(grid_hydro_input.value),
        "grid_geo": float(grid_geo_input.value),
        "grid_other_ff": float(grid_other_ff_input.value),
        "PerNetZeroCarbon": float(PerNetZeroCarbonTextInput.value),  # TK, possibly
        "change_pop": change_pop_slider.value,
        "urban_pop_percent": float(urban_pop_percentTextInput.value),
        "suburban_pop_percent": float(suburban_pop_percentTextInput.value),
        "rural_pop_percent": float(rural_pop_percentTextInput.value),
        "res_energy_change": res_energy_change_slider.value,
        "urb_energy_elec": urb_energy_elec_slider.value,
        "sub_energy_elec": sub_energy_elec_slider.value,
        "rur_energy_elec": rur_energy_elec_slider.value,
        "ci_energy_change": ci_energy_change_slider.value,
        "ci_energy_elec": ci_energy_elec_slider.value,
        "change_veh_miles": change_veh_miles_slider.value,
        "reg_fleet_mpg": reg_fleet_mpg_slider.value,
        "veh_miles_elec": veh_miles_elec_slider.value,
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
        "change_air_travel": change_air_travel_slider.value,
        "change_ag": change_ag_slider.value,
        "change_solid_waste": change_solid_waste_slider.value,
        "change_wastewater": change_wasterwater_slider.value,
        "change_industrial_processes": change_industrial_processes_slider.value,
        "change_urban_trees": change_urban_trees_slider.value,
        "change_forest": change_forest_slider.value,
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
    SECTORS, x="Year", width=0.4, color=Viridis7, source=stacked_chart_source, legend_label=SECTORS
)
stacked_bar_chart.legend[0].items.reverse()  # Reverse legend items to match order  in stack
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

PerNetZeroCarbonTextInput = TextInput(
    value=str(round(GRID_NUCLEAR + GRID_SOLAR + GRID_WIND + GRID_BIO + GRID_HYDRO + GRID_GEO)),
    title="% Net Zero Carbon Sources in Grid Mix",
)
PerNetZeroCarbonTextInput.on_change("value", callback)

# population
change_pop_slider = Slider(start=-100, end=100, value=0, step=10, title="% Change in Population")
change_pop_slider.on_change("value", callback)

urban_pop_percentTextInput = TextInput(
    value=str(round(URBAN_POP_PERCENT, 1)), title="% of Population Living in Urban Municipalities"
)
urban_pop_percentTextInput.on_change("value", callback)

suburban_pop_percentTextInput = TextInput(
    value=str(round(SUBURBAN_POP_PERCENT, 1)),
    title="% of Population Living in Suburban Municipalities",
)
suburban_pop_percentTextInput.on_change("value", callback)

rural_pop_percentTextInput = TextInput(
    value=str(round(RURAL_POP_PERCENT, 1)), title="% of Population Living in Rural Municipalities"
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

# highway
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

# non-energy
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
    start=-100, end=100, value=0, step=1, title="% Change in Emissions from Industrial Processes",
)
change_industrial_processes_slider.on_change("value", callback)

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

AirCaptureSlider = Slider(start=0, end=100, value=0, step=1, title="MMTCO2e Captured from the Air")
AirCaptureSlider.on_change("value", callback)

#########################
# group the input widgets

population_inputs = Column(
    change_pop_slider,
    urban_pop_percentTextInput,
    suburban_pop_percentTextInput,
    rural_pop_percentTextInput,
)

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
res_inputs = Column(
    res_energy_change_slider,
    urb_energy_elec_slider,
    sub_energy_elec_slider,
    rur_energy_elec_slider,
)
ci_inputs = Column(ci_energy_change_slider, ci_energy_elec_slider)
highway_inputs = Column(change_veh_miles_slider, veh_miles_elec_slider, reg_fleet_mpg_slider)
transit_inputs = Column(
    PerTransRailRidershipSlider,
    TransRailUrbanPerElecMotionSlider,
    TransRailSuburbanPerElecMotionSlider,
    TransRailRuralPerElecMotionSlider,
)
other_mobile_inputs = Column(
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
non_energy_inputs = Column(
    change_ag_slider,
    change_solid_waste_slider,
    change_wasterwater_slider,
    change_industrial_processes_slider,
    change_urban_trees_slider,
    change_forest_slider,
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
