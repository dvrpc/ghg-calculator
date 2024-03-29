from math import pi
from statistics import mean

import numpy as np
import pandas as pd

from bokeh.models import LabelSet
from bokeh.palettes import Viridis7, Viridis8, Spectral10
from bokeh.plotting import figure
from bokeh.transform import dodge, cumsum


# Implied National Emissions rate from NG Transmission, Storage, Distribution (fugitive emissions in MMTCO2e/million CF)
NE_CO2_MMT_NG_METHANE = 0.00000169
NE_CO2_MMT_NG_CO = 0.000000004

# 2015 GHG Inventory Total Emissions (MMTCO2E)
GHG_RES = 15.37
GHG_CI = 27.96  # non-residential/commercial & industrial
GHG_HIGHWAY = 17.94
GHG_TRANSIT = 0.18
GHG_F = 0.26  # freight rail
GHG_ICR = 0.04  # inter-city rail
GHG_RAIL = GHG_TRANSIT + GHG_F + GHG_ICR
GHG_AVIATION = 3.90
GHG_MP = 0.31  # marine and port-related
GHG_OR = 0.52  # off-road vehicles and equipment
GHG_OTHER_MOBILE = GHG_MP + GHG_OR
GHG_AG = 0.41  # agriculture
GHG_SOLID_WASTE = 2.01  # landfills
GHG_WASTEWATER = 0.49
GHG_IP = 5.52  # industrial processes; includes Hydrogen production, iron & steel production, industrial wastewater treatment, ODS substitutes, and petroleum refining
SEQ_URBAN_TREES = -1.025
SEQ_FORESTS = -1.110  # corrected rounding
GHG_FOREST_CHANGE = 0.380  # emissions from loss of forest for 2015 (MMTCO2e)
FOREST_ACRE_2010 = 792534.1253
FOREST_ACRE_2015 = 785312.64
FOREST_CHANGE_ACRE_ANNUAL = (FOREST_ACRE_2015 - FOREST_ACRE_2010) / 5
FOREST_SEQ_ACRE = -0.00000141308092029381  # weighted average MMTCO2 per acre sequestered per year.
FOREST_ACRE_2014 = FOREST_ACRE_2015 - FOREST_CHANGE_ACRE_ANNUAL
PER_ANNUAL_FOREST_CHANGE_2015 = FOREST_CHANGE_ACRE_ANNUAL / FOREST_ACRE_2014 * 100
FOREST_GHG_ACRELOSS = 0.000260941776124502  # weighted average MMTCO2 released per acre lost
GHG_SEQ = SEQ_URBAN_TREES + SEQ_FORESTS
RES_NG = 115884601.50 / 1000  # NG Consumpton 2015 (million CF)
CI_NG = 139139475 / 1000  # NG Consumpton 2015 (million CF)
GHG_NON_ENERGY = (
    GHG_AG
    + GHG_SOLID_WASTE
    + GHG_WASTEWATER
    + GHG_IP
    + GHG_FOREST_CHANGE
    + (RES_NG + CI_NG) * (NE_CO2_MMT_NG_METHANE + NE_CO2_MMT_NG_CO)
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
CO2_MT_BBTU_NG = 53.20
CO2_MT_BBTU_COAL = 95.13
CO2_MT_BBTU_DFO = 74.39
CO2_MT_BBTU_KER = 73.63
CO2_MT_BBTU_LPG = 65.15
CO2_MT_BBTU_MG = 71.60
CO2_MT_BBTU_RFO = 75.35
CO2_MT_BBTU_PETCOKE = 102.36
CO2_MT_BBTU_STILL_GAS = 66.96
CO2_MT_BBTU_NAPHTHAS = 72.62

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
CI_MG_USEFUL = 0.80
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
CI_MG_BTU = 12584.78 * CI_MG_USEFUL
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
    + CI_MG_BTU
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
CI_ENERGY_MG = CI_MG_BTU / CI_ENERGY_BTU * 100
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
CI_ENERGY_FF_MG = CI_ENERGY_MG / CI_ENERGY_FF
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
# Mobile-Rail GHG Factors

# rail transit

RT_BBTU_KB_D = 5.768
RT_CO2_MT_BBTU_D = 74.66024683
RT_D_ENERGY_MOTION = 35  # https://www.eesi.org/articles/view/electrification-of-u.s.-railways-pie-in-the-sky-or-realistic-goal
RT_ELEC_ENERGY_MOTION = 95  # https://www.eesi.org/articles/view/electrification-of-u.s.-railways-pie-in-the-sky-or-realistic-goal

RT_ELEC_URB_CAP = 115.85  # kWh/person
RT_ELEC_SUB_CAP = 66.10  # kWh/person
RT_ELEC_RUR_CAP = 21.37  # kWh/person

RT_D_GAL_URB = 0.1995  # gallons/person for rail transit diesel in urban areas
RT_D_GAL_SUB = 0.1138  # gallons/person
RT_D_GAL_RUR = 0.0368  # gallons/person

RT_D_BTU_URB = RT_D_GAL_URB * KB_G * RT_BBTU_KB_D * 1000000000  # BTU/Person
RT_D_BTU_SUB = RT_D_GAL_SUB * KB_G * RT_BBTU_KB_D * 1000000000  # BTU/Person
RT_D_BTU_RUR = RT_D_GAL_RUR * KB_G * RT_BBTU_KB_D * 1000000000  # BTU/Person

RT_ELEC_MOTION_URB = (RT_ELEC_URB_CAP * BTU_KWH) * RT_ELEC_ENERGY_MOTION / 100
RT_ELEC_MOTION_SUB = (RT_ELEC_SUB_CAP * BTU_KWH) * RT_ELEC_ENERGY_MOTION / 100
RT_ELEC_MOTION_RUR = (RT_ELEC_RUR_CAP * BTU_KWH) * RT_ELEC_ENERGY_MOTION / 100

RT_D_MOTION_URB = RT_D_BTU_URB * RT_D_ENERGY_MOTION / 100
RT_D_MOTION_SUB = RT_D_BTU_SUB * RT_D_ENERGY_MOTION / 100
RT_D_MOTION_RUR = RT_D_BTU_RUR * RT_D_ENERGY_MOTION / 100

RT_ENERGY_MOTION_URB = RT_ELEC_MOTION_URB + RT_D_MOTION_URB
RT_ENERGY_MOTION_SUB = RT_ELEC_MOTION_SUB + RT_D_MOTION_SUB
RT_ENERGY_MOTION_RUR = RT_ELEC_MOTION_RUR + RT_D_MOTION_RUR

RT_ENERGY_ELEC_MOTION = (
    (RT_ELEC_MOTION_URB + RT_ELEC_MOTION_SUB + RT_ELEC_MOTION_RUR)
    / (RT_ENERGY_MOTION_URB + RT_ENERGY_MOTION_SUB + RT_ENERGY_MOTION_RUR)
) * 100

# Freight Rail
F_ELEC = 0
F_D = 3525.18
F_ELEC_MOTION = F_ELEC * RT_ELEC_ENERGY_MOTION / 100
F_D_MOTION = F_D * RT_D_ENERGY_MOTION / 100
F_ENERGY_MOTION = F_ELEC_MOTION + F_D_MOTION
F_ENERGY_ELEC_MOTION = F_ELEC_MOTION / F_ENERGY_MOTION * 100
F_D_CO2_MT_BBTU = 74.5937203

# InterCity Rail
ICR_ELEC = 319.07
ICR_D = 24.93
ICR_ELEC_MOTION = ICR_ELEC * RT_ELEC_ENERGY_MOTION / 100
ICR_D_MOTION = ICR_D * RT_D_ENERGY_MOTION / 100
ICR_ENERGY_MOTION = ICR_ELEC_MOTION + ICR_D_MOTION
ICR_ENERGY_ELEC_MOTION = ICR_ELEC_MOTION / ICR_ENERGY_MOTION * 100
ICR_D_CO2_MT_BBTU = 73.978

##########################
# Mobile-Other GHG Factors

# Marine and Port
MP_ELEC_MOTION = 100
MP_RFO_MOTION = 50  # Calculation of Efficiencies of a Ship Power Plant Operating with Waste Heat Recovery through Combined Heat and Power Production by Mirko Grljušić 1,2,*, Vladimir Medica 3,† and Gojmir Radica 1,†
MP_DFO_MOTION = 50  # Calculation of Efficiencies of a Ship Power Plant Operating with Waste Heat Recovery through Combined Heat and Power Production by Mirko Grljušić 1,2,*, Vladimir Medica 3,† and Gojmir Radica 1,†
MP_ELEC = 0
MP_RFO = 2221.436
MP_DFO = 1855.010
MP_ELEC_MOTION_BBTU = MP_ELEC * MP_ELEC_MOTION / 100
MP_RFO_MOTION_BBTU = MP_RFO * MP_RFO_MOTION / 100
MP_DFO_MOTION_BBTU = MP_DFO * MP_DFO_MOTION / 100
MP_ENERGY_MOTION_BBTU = MP_ELEC_MOTION_BBTU + MP_RFO_MOTION_BBTU + MP_DFO_MOTION_BBTU
MP_ENERGY_ELEC_MOTION = MP_ELEC_MOTION_BBTU / MP_ENERGY_MOTION_BBTU * 100
MP_RFO_ENERGY_MOTION = MP_RFO_MOTION_BBTU / MP_ENERGY_MOTION_BBTU * 100
MP_DFO_ENERGY_MOTION = MP_DFO_MOTION_BBTU / MP_ENERGY_MOTION_BBTU * 100
MP_RFO_CO2_MMT_BBTU = 75.732
MP_DFO_CO2_MMT_BBTU = 74.581
MP_FF_ENERGY_MOTION = 100 - MP_ENERGY_ELEC_MOTION
MP_FF_RFO_ENERGY_MOTION = MP_RFO_ENERGY_MOTION / MP_FF_ENERGY_MOTION * 100
MP_FF_DFO_ENERGY_MOTION = MP_DFO_ENERGY_MOTION / MP_FF_ENERGY_MOTION * 100

# Off-Road Vehicles and Equipment
OR_ELEC_MOTION = 90
OR_MG_MOTION = 20
OR_DFO_MOTION = 20
OR_LPG_MOTION = 20

OR_ELEC = 0
OR_MG = 6041.46
OR_DFO = 889.30
OR_LPG = 31.67
OR_ELEC_MOTION_BBTU = OR_ELEC * OR_ELEC_MOTION / 100
OR_MG_MOTION_BBTU = OR_MG * OR_MG_MOTION / 100
OR_DFO_MOTION_BBTU = OR_DFO * OR_DFO_MOTION / 100
OR_LPG_MOTION_BBTU = OR_LPG * OR_LPG_MOTION / 100
OR_ENERGY_MOTION_BBTU = (
    OR_ELEC_MOTION_BBTU + OR_MG_MOTION_BBTU + OR_DFO_MOTION_BBTU + OR_LPG_MOTION_BBTU
)
OR_ENERGY_ELEC_MOTION = OR_ELEC_MOTION_BBTU / OR_ENERGY_MOTION_BBTU * 100
OR_MG_ENERGY_MOTION = OR_MG_MOTION_BBTU / OR_ENERGY_MOTION_BBTU * 100
OR_DFO_ENERGY_MOTION = OR_DFO_MOTION_BBTU / OR_ENERGY_MOTION_BBTU * 100
OR_LPG_ENERGY_MOTION = OR_LPG_MOTION_BBTU / OR_ENERGY_MOTION_BBTU * 100
OR_MG_CO2_MT_BBTU = 74.05165922
OR_DFO_CO2_MT_BBTU = 74.20539973
OR_LPG_CO2_MT_BBTU = 62.05918303
OR_FF_ENERGY_MOTION = 100 - OR_ENERGY_ELEC_MOTION
OR_FF_MG_ENERGY_MOTION = OR_MG_ENERGY_MOTION / OR_FF_ENERGY_MOTION * 100
OR_FF_DFO_ENERGY_MOTION = OR_DFO_ENERGY_MOTION / OR_FF_ENERGY_MOTION * 100
OR_FF_LPG_ENERGY_MOTION = OR_LPG_ENERGY_MOTION / OR_FF_ENERGY_MOTION * 100

# create dictionary (and set initial values) of all variables that user can change
# will be passed to functions that create charts
user_inputs = {
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
    "change_pop": 0,
    "urban_pop_percent": URBAN_POP_PERCENT,
    "rural_pop_percent": RURAL_POP_PERCENT,
    "suburban_pop_percent": SUBURBAN_POP_PERCENT,
    "rur_energy_elec": RUR_ENERGY_ELEC * 100,  # convert to % b/c func will take user % later
    "sub_energy_elec": SUB_ENERGY_ELEC * 100,  # convert to % b/c func will take user % later
    "urb_energy_elec": URB_ENERGY_ELEC * 100,  # convert to % b/c func will take user % later
    "res_energy_change": 0,
    "ci_energy_elec": CI_ENERGY_ELEC,
    "ci_energy_change": 0,
    "change_industrial_processes": 0,
    "reg_fleet_mpg": REG_FLEET_MPG,
    "change_veh_miles": 0,
    "veh_miles_elec": 0,
    "rt_energy_elec_motion": RT_ENERGY_ELEC_MOTION,
    "change_rail_transit": 0,
    "f_energy_elec_motion": F_ENERGY_ELEC_MOTION,
    "change_freight_rail": 0,
    "icr_energy_elec_motion": ICR_ENERGY_ELEC_MOTION,
    "change_inter_city_rail": 0,
    "mp_energy_elec_motion": MP_ENERGY_ELEC_MOTION,
    "change_marine_port": 0,
    "or_energy_elec_motion": OR_ENERGY_ELEC_MOTION,
    "change_off_road": 0,
    "change_air_travel": 0,
    "ff_carbon_capture": 0,
    "air_capture": 0,
    "change_forest": PER_ANNUAL_FOREST_CHANGE_2015,
    "change_urban_trees": 0,
    "change_ag": 0,
    "change_solid_waste": 0,
    "change_wastewater": 0,
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
    res_elec_btu = urban_elec_btu + suburban_elec_btu + rural_elec_btu
    res_elec_ghg = (
        res_elec_btu
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

    return res_ghg, res_ng_btu, res_elec_btu


def calc_ci_ghg(
    ci_energy_elec,
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    ci_energy_change,
):
    ci_ff = 100 - ci_energy_elec
    change_ff = (ci_ff - CI_ENERGY_FF) / CI_ENERGY_FF

    ci_elec_btu = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_energy_elec / 100)
        / CI_ELEC_USEFUL
        * 1000000000
    )
    ci_elec_ghg = (
        ci_elec_btu
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
    )

    ci_ng_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_NG
        / CI_NG_USEFUL
        * CO2_MT_BBTU_NG
        * MT_TO_MMT
    )

    ci_coal_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_COAL
        / CI_COAL_USEFUL
        * CO2_MT_BBTU_COAL
        * MT_TO_MMT
    )

    ci_dfo_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_DFO
        / CI_DFO_USEFUL
        * CO2_MT_BBTU_DFO
        * MT_TO_MMT
    )

    ci_k_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_K
        / CI_K_USEFUL
        * CO2_MT_BBTU_KER
        * MT_TO_MMT
    )

    ci_lpg_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_LPG
        / CI_LPG_USEFUL
        * CO2_MT_BBTU_LPG
        * MT_TO_MMT
    )

    ci_motor_gas_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_MG
        / CI_MG_USEFUL
        * CO2_MT_BBTU_MG
        * MT_TO_MMT
    )

    ci_rfo_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_RFO
        / CI_RFO_USEFUL
        * CO2_MT_BBTU_RFO
        * MT_TO_MMT
    )

    ci_pet_coke_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_PET_COKE
        / CI_PET_COKE_USEFUL
        * CO2_MT_BBTU_PETCOKE
        * MT_TO_MMT
    )

    ci_still_gas_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_STILL_GAS
        / CI_STILL_GAS_USEFUL
        * CO2_MT_BBTU_STILL_GAS
        * MT_TO_MMT
    )

    ci_naphthas_ghg = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_NAPHTHAS
        / CI_NAPHTHAS_USEFUL
        * CO2_MT_BBTU_NAPHTHAS
        * MT_TO_MMT
    )

    return (
        (
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
        ),
        ci_elec_btu,
    )


def calc_highway_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
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

    highway_elec_btu = elec_miles_percent * ELEC_VEH_EFFICIENCY * BTU_KWH

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
    )

    return highway_ghg, highway_elec_btu


def calc_aviation_ghg(change_pop, change_air_travel):
    return GHG_AVIATION * (1 + change_pop / 100) * (1 + change_air_travel / 100)


def calc_rail_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    change_rail_transit,
    change_pop,
    rural_pop_percent,
    suburban_pop_percent,
    urban_pop_percent,
    rt_energy_elec_motion,
    f_energy_elec_motion,
    icr_energy_elec_motion,
    change_freight_rail,
    change_inter_city_rail,
):
    transit_elec_ghg = (
        POP
        * (1 + change_pop / 100)
        * (1 / BTU_MWH)
        / (1 - GRID_LOSS)
        * (
            (urban_pop_percent / 100 * RT_ENERGY_MOTION_URB * rt_energy_elec_motion / 100)
            + (suburban_pop_percent / 100 * RT_ENERGY_MOTION_SUB * rt_energy_elec_motion / 100)
            + (rural_pop_percent / 100 * RT_ENERGY_MOTION_RUR * rt_energy_elec_motion / 100)
        )
        / (RT_ELEC_ENERGY_MOTION / 100)
        * (
            (
                (grid_coal / 100 * CO2_LB_MWH_COAL)
                + (grid_oil / 100 * CO2_LB_MWH_OIL)
                + (grid_ng / 100 * CO2_LB_MWH_NG)
                + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
            )
            * MMT_LB
        )
    )

    transit_d_ghg = (
        POP
        * (1 + change_pop / 100)
        * RT_CO2_MT_BBTU_D
        * (1 / 1000000000)
        * MT_TO_MMT
        * (
            (urban_pop_percent / 100 * RT_ENERGY_MOTION_URB * (100 - rt_energy_elec_motion) / 100)
            + (
                suburban_pop_percent
                / 100
                * RT_ENERGY_MOTION_SUB
                * (100 - rt_energy_elec_motion)
                / 100
            )
            + (rural_pop_percent / 100 * RT_ENERGY_MOTION_RUR * (100 - rt_energy_elec_motion) / 100)
        )
        / (RT_D_ENERGY_MOTION / 100)
    )

    transit_ghg = (transit_elec_ghg + transit_d_ghg) * (1 + change_rail_transit / 100)

    transit_elec_btu = (
        POP
        * (1 + change_pop / 100)
        / (1 - GRID_LOSS)
        * (
            (urban_pop_percent / 100 * RT_ENERGY_MOTION_URB * rt_energy_elec_motion / 100)
            + (suburban_pop_percent / 100 * RT_ENERGY_MOTION_SUB * rt_energy_elec_motion / 100)
            + (rural_pop_percent / 100 * RT_ENERGY_MOTION_RUR * rt_energy_elec_motion / 100)
        )
        / (RT_ELEC_ENERGY_MOTION / 100)
    ) * (1 + change_rail_transit / 100)

    f_elec_ghg = (
        F_ENERGY_MOTION
        * (f_energy_elec_motion / 100)
        / (RT_ELEC_ENERGY_MOTION / 100)
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
    )

    f_elec_btu = (
        F_ENERGY_MOTION
        * (f_energy_elec_motion / 100)
        / (RT_ELEC_ENERGY_MOTION / 100)
        * 1000000000
        * (1 + change_freight_rail / 100)
    )

    f_d_ghg = (
        F_ENERGY_MOTION
        * ((100 - f_energy_elec_motion) / 100)
        * F_D_CO2_MT_BBTU
        * MT_TO_MMT
        / (RT_D_ENERGY_MOTION / 100)
    )

    f_ghg = (f_elec_ghg + f_d_ghg) * (1 + change_freight_rail / 100)

    icr_elec_ghg = (
        ICR_ENERGY_MOTION
        * (icr_energy_elec_motion / 100)
        / (RT_ELEC_ENERGY_MOTION / 100)
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
    )

    icr_d_ghg = (
        ICR_ENERGY_MOTION
        * ((100 - icr_energy_elec_motion) / 100)
        * ICR_D_CO2_MT_BBTU
        * MT_TO_MMT
        / (RT_D_ENERGY_MOTION / 100)
    )

    icr_elec_btu = (
        ICR_ENERGY_MOTION
        * (icr_energy_elec_motion / 100)
        / (RT_ELEC_ENERGY_MOTION / 100)
        * 1000000000
        * (1 + change_inter_city_rail / 100)
    )

    icr_ghg = (icr_elec_ghg + icr_d_ghg) * (1 + change_inter_city_rail / 100)

    return transit_ghg + f_ghg + icr_ghg, transit_elec_btu + f_elec_btu + icr_elec_btu


def calc_other_mobile_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    mp_energy_elec_motion,
    change_marine_port,
    change_off_road,
    or_energy_elec_motion,
):
    """
    Calculate GHG emissions for freight & intercity rail, marine & port-related, and off-road
    vehicles and equipment.
    """

    mp_ff_motion = 100 - mp_energy_elec_motion
    mp_percent_changed_ff_motion = (mp_ff_motion - MP_FF_ENERGY_MOTION) / MP_FF_ENERGY_MOTION

    mp_elec_ghg = (
        MP_ENERGY_MOTION_BBTU
        * (mp_energy_elec_motion / 100)
        / (MP_ELEC_MOTION / 100)
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
    )

    mp_elec_btu = (
        MP_ENERGY_MOTION_BBTU
        * (mp_energy_elec_motion / 100)
        / (MP_ELEC_MOTION / 100)
        * 1000000000
        * (1 + change_marine_port / 100)
    )

    mp_rfo_ghg = (
        MP_ENERGY_MOTION_BBTU
        * (MP_FF_RFO_ENERGY_MOTION / 100)
        * (mp_ff_motion / 100)
        * (1 + mp_percent_changed_ff_motion)
        * MP_RFO_CO2_MMT_BBTU
        * MT_TO_MMT
        / (MP_RFO_MOTION / 100)
    )

    mp_dfo_ghg = (
        MP_ENERGY_MOTION_BBTU
        * (MP_FF_DFO_ENERGY_MOTION / 100)
        * (mp_ff_motion / 100)
        * (1 + mp_percent_changed_ff_motion)
        * MP_DFO_CO2_MMT_BBTU
        * MT_TO_MMT
        / (MP_DFO_MOTION / 100)
    )

    mp_ghg = (mp_elec_ghg + mp_rfo_ghg + mp_dfo_ghg) * (1 + change_marine_port / 100)

    or_ff_motion = 100 - or_energy_elec_motion
    or_percent_changed_ff_motion = (or_ff_motion - OR_FF_ENERGY_MOTION) / OR_FF_ENERGY_MOTION

    or_elec_ghg = (
        OR_ENERGY_MOTION_BBTU
        * (or_energy_elec_motion / 100)
        / (OR_ELEC_MOTION / 100)
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
    )

    or_elec_btu = (
        OR_ENERGY_MOTION_BBTU
        * (or_energy_elec_motion / 100)
        / (OR_ELEC_MOTION / 100)
        * 1000000000
        * (1 + change_off_road / 100)
    )

    or_mg_ghg = (
        OR_ENERGY_MOTION_BBTU
        * (OR_FF_MG_ENERGY_MOTION / 100)
        * (or_ff_motion / 100)
        * (1 + or_percent_changed_ff_motion)
        * OR_MG_CO2_MT_BBTU
        * MT_TO_MMT
        / (OR_MG_MOTION / 100)
    )

    or_dfo_ghg = (
        OR_ENERGY_MOTION_BBTU
        * (OR_FF_DFO_ENERGY_MOTION / 100)
        * (or_ff_motion / 100)
        * (1 + or_percent_changed_ff_motion)
        * OR_DFO_CO2_MT_BBTU
        * MT_TO_MMT
        / (OR_DFO_MOTION / 100)
    )

    or_lpg_ghg = (
        OR_ENERGY_MOTION_BBTU
        * (OR_FF_LPG_ENERGY_MOTION / 100)
        * (or_ff_motion / 100)
        * (1 + or_percent_changed_ff_motion)
        * OR_LPG_CO2_MT_BBTU
        * MT_TO_MMT
        / (OR_LPG_MOTION / 100)
    )

    or_ghg = (or_elec_ghg + or_mg_ghg + or_dfo_ghg + or_lpg_ghg) * (1 + change_off_road / 100)

    return mp_ghg + or_ghg, mp_elec_btu + or_elec_btu


def calc_lulucf(
    change_forest,
    change_urban_trees,
):

    seq_urban_trees = SEQ_URBAN_TREES * (1 + change_urban_trees / 100)
    seq_forest = FOREST_ACRE_2014 * (1 + change_forest / 100) * FOREST_SEQ_ACRE
    if change_forest < 0:
        ghg_forest = FOREST_ACRE_2014 * -(change_forest / 100) * FOREST_GHG_ACRELOSS
    else:
        ghg_forest = 0

    seq_lulucf = seq_urban_trees + seq_forest

    ghg_lulucf = ghg_forest

    return seq_lulucf, ghg_lulucf


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
    rural_pop_percent,
    suburban_pop_percent,
    urban_pop_percent,
):
    ag_ghg = GHG_AG * (1 + change_ag / 100)
    solid_waste_ghg = GHG_SOLID_WASTE * (1 + change_solid_waste / 100) * (1 + change_pop / 100)
    wastewater_ghg = GHG_WASTEWATER * (1 + change_wastewater / 100) * (1 + change_pop / 100)
    ip_ghg = GHG_IP * (1 + change_industrial_processes / 100)

    res_ng_consumption = calc_res_ghg(
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
    )[1]

    ci_ff = 100 - ci_energy_elec
    change_ff = (ci_ff - CI_ENERGY_FF) / CI_ENERGY_FF

    ci_ng_consumption = (
        CI_ENERGY_BTU
        * (1 + ci_energy_change / 100)
        * (ci_ff / 100)
        * (1 + change_ff)
        * CI_ENERGY_FF_NG
        / CI_NG_USEFUL
        * 1000000000
    )

    ng_systems_ghg = (
        (res_ng_consumption + ci_ng_consumption)
        * (1 / BTU_CCF_AVG)
        * 100
        * 0.000001
        * (NE_CO2_MMT_NG_METHANE + NE_CO2_MMT_NG_CO)
    )

    lulucf_ghg = calc_lulucf(change_forest, change_urban_trees)[1]

    return ag_ghg + solid_waste_ghg + wastewater_ghg + ip_ghg + ng_systems_ghg + lulucf_ghg


def calc_sequestration(  # May need all inputs for electricity calculations below
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
    ci_energy_elec,
    ci_energy_change,
    veh_miles_elec,
    reg_fleet_mpg,
    change_veh_miles,
    change_rail_transit,
    rt_energy_elec_motion,
    f_energy_elec_motion,
    icr_energy_elec_motion,
    change_freight_rail,
    change_inter_city_rail,
    mp_energy_elec_motion,
    change_marine_port,
    change_off_road,
    or_energy_elec_motion,
    change_ag,
    change_industrial_processes,
    change_solid_waste,
    change_wastewater,
    change_forest,
    change_urban_trees,
    ff_carbon_capture,
    air_capture,
):

    lulucf_seq = calc_lulucf(change_forest, change_urban_trees)[0]

    res_elec_btu = calc_res_ghg(
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
    )[2]

    ci_elec_btu = calc_ci_ghg(
        ci_energy_elec,
        grid_coal,
        grid_ng,
        grid_oil,
        grid_other_ff,
        ci_energy_change,
    )[1]

    highway_elec_btu = calc_highway_ghg(
        grid_coal,
        grid_ng,
        grid_oil,
        grid_other_ff,
        veh_miles_elec,
        change_pop,
        reg_fleet_mpg,
        rural_pop_percent,
        suburban_pop_percent,
        urban_pop_percent,
        change_veh_miles,
    )[1]

    rail_elec_btu = calc_rail_ghg(
        grid_coal,
        grid_ng,
        grid_oil,
        grid_other_ff,
        change_rail_transit,
        change_pop,
        rural_pop_percent,
        suburban_pop_percent,
        urban_pop_percent,
        rt_energy_elec_motion,
        f_energy_elec_motion,
        icr_energy_elec_motion,
        change_freight_rail,
        change_inter_city_rail,
    )[1]

    om_elec_btu = calc_other_mobile_ghg(
        grid_coal,
        grid_ng,
        grid_oil,
        grid_other_ff,
        mp_energy_elec_motion,
        change_marine_port,
        change_off_road,
        or_energy_elec_motion,
    )[1]

    total_elec_btu = res_elec_btu + ci_elec_btu + highway_elec_btu + rail_elec_btu + om_elec_btu

    seq_source_capture = -(
        total_elec_btu
        * (1 / BTU_MWH)
        / (1 - GRID_LOSS)
        * (
            (
                (grid_coal / 100 * CO2_LB_MWH_COAL)
                + (grid_oil / 100 * CO2_LB_MWH_OIL)
                + (grid_ng / 100 * CO2_LB_MWH_NG)
                + (grid_other_ff / 100 * CO2_LB_MWH_OTHER_FF)
            )
        )
        * MMT_LB
        * ff_carbon_capture
        / 100
    )

    gross_ghg = (
        calc_res_ghg(
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
        )[0]
        + calc_ci_ghg(
            ci_energy_elec,
            grid_coal,
            grid_ng,
            grid_oil,
            grid_other_ff,
            ci_energy_change,
        )[0]
        + calc_highway_ghg(
            grid_coal,
            grid_ng,
            grid_oil,
            grid_other_ff,
            veh_miles_elec,
            change_pop,
            reg_fleet_mpg,
            rural_pop_percent,
            suburban_pop_percent,
            urban_pop_percent,
            change_veh_miles,
        )[0]
        + calc_rail_ghg(
            grid_coal,
            grid_ng,
            grid_oil,
            grid_other_ff,
            change_rail_transit,
            change_pop,
            rural_pop_percent,
            suburban_pop_percent,
            urban_pop_percent,
            rt_energy_elec_motion,
            f_energy_elec_motion,
            icr_energy_elec_motion,
            change_freight_rail,
            change_inter_city_rail,
        )[0]
        + calc_other_mobile_ghg(
            grid_coal,
            grid_ng,
            grid_oil,
            grid_other_ff,
            mp_energy_elec_motion,
            change_marine_port,
            change_off_road,
            or_energy_elec_motion,
        )[0]
        + calc_non_energy_ghg(
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
            rural_pop_percent,
            suburban_pop_percent,
            urban_pop_percent,
        )
    )
    seq_air_capture = -(gross_ghg + seq_source_capture + lulucf_seq) * air_capture / 100

    return seq_air_capture + seq_source_capture + lulucf_seq


###########################
# Prepare data for charts #
###########################

SECTORS = [
    "Carbon Seq. & Storage",
    "Residential Stationary Energy",
    "Non-Residential Stationary Energy",
    "On-Road Motor Vehicles",
    "Rail",
    "Aviation",
    "Other Mobile Energy",
    "Non-Energy",
]


def wrangle_data_for_bar_chart(user_inputs):
    data = {
        "Category": SECTORS,
        "2015": [
            round(GHG_SEQ, 1),
            round(GHG_RES, 1),
            round(GHG_CI, 1),
            round(GHG_HIGHWAY, 1),
            round(GHG_RAIL, 1),
            round(GHG_AVIATION, 1),
            round(GHG_OTHER_MOBILE, 1),
            round(GHG_NON_ENERGY, 1),
        ],
        "Scenario": [
            round(
                calc_sequestration(
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
                    user_inputs["ci_energy_elec"],
                    user_inputs["ci_energy_change"],
                    user_inputs["veh_miles_elec"],
                    user_inputs["reg_fleet_mpg"],
                    user_inputs["change_veh_miles"],
                    user_inputs["change_rail_transit"],
                    user_inputs["rt_energy_elec_motion"],
                    user_inputs["f_energy_elec_motion"],
                    user_inputs["icr_energy_elec_motion"],
                    user_inputs["change_freight_rail"],
                    user_inputs["change_inter_city_rail"],
                    user_inputs["mp_energy_elec_motion"],
                    user_inputs["change_marine_port"],
                    user_inputs["change_off_road"],
                    user_inputs["or_energy_elec_motion"],
                    user_inputs["change_ag"],
                    user_inputs["change_industrial_processes"],
                    user_inputs["change_solid_waste"],
                    user_inputs["change_wastewater"],
                    user_inputs["change_forest"],
                    user_inputs["change_urban_trees"],
                    user_inputs["ff_carbon_capture"],
                    user_inputs["air_capture"],
                ),
                1,
            ),
            round(
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
                1,
            ),
            round(
                calc_ci_ghg(
                    user_inputs["ci_energy_elec"],
                    user_inputs["grid_coal"],
                    user_inputs["grid_ng"],
                    user_inputs["grid_oil"],
                    user_inputs["grid_other_ff"],
                    user_inputs["ci_energy_change"],
                )[0],
                1,
            ),
            round(
                calc_highway_ghg(
                    user_inputs["grid_coal"],
                    user_inputs["grid_ng"],
                    user_inputs["grid_oil"],
                    user_inputs["grid_other_ff"],
                    user_inputs["veh_miles_elec"],
                    user_inputs["change_pop"],
                    user_inputs["reg_fleet_mpg"],
                    user_inputs["rural_pop_percent"],
                    user_inputs["suburban_pop_percent"],
                    user_inputs["urban_pop_percent"],
                    user_inputs["change_veh_miles"],
                )[0],
                1,
            ),
            round(
                calc_rail_ghg(
                    user_inputs["grid_coal"],
                    user_inputs["grid_ng"],
                    user_inputs["grid_oil"],
                    user_inputs["grid_other_ff"],
                    user_inputs["change_rail_transit"],
                    user_inputs["change_pop"],
                    user_inputs["rural_pop_percent"],
                    user_inputs["suburban_pop_percent"],
                    user_inputs["urban_pop_percent"],
                    user_inputs["rt_energy_elec_motion"],
                    user_inputs["f_energy_elec_motion"],
                    user_inputs["icr_energy_elec_motion"],
                    user_inputs["change_freight_rail"],
                    user_inputs["change_inter_city_rail"],
                )[0],
                1,
            ),
            round(
                calc_aviation_ghg(user_inputs["change_pop"], user_inputs["change_air_travel"]), 1
            ),
            round(
                calc_other_mobile_ghg(
                    user_inputs["grid_coal"],
                    user_inputs["grid_ng"],
                    user_inputs["grid_oil"],
                    user_inputs["grid_other_ff"],
                    user_inputs["mp_energy_elec_motion"],
                    user_inputs["change_marine_port"],
                    user_inputs["change_off_road"],
                    user_inputs["or_energy_elec_motion"],
                )[0],
                1,
            ),
            round(
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
                    user_inputs["rural_pop_percent"],
                    user_inputs["suburban_pop_percent"],
                    user_inputs["urban_pop_percent"],
                ),
                1,
            ),
        ],
    }
    return data


def wrangle_data_for_stacked_chart(user_inputs):
    # Transpose data
    data = {
        "Year": ["2015", "Scenario"],
        "Carbon Sequestration & Storage": [
            GHG_SEQ,
            calc_sequestration(
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
                user_inputs["ci_energy_elec"],
                user_inputs["ci_energy_change"],
                user_inputs["veh_miles_elec"],
                user_inputs["reg_fleet_mpg"],
                user_inputs["change_veh_miles"],
                user_inputs["change_rail_transit"],
                user_inputs["rt_energy_elec_motion"],
                user_inputs["f_energy_elec_motion"],
                user_inputs["icr_energy_elec_motion"],
                user_inputs["change_freight_rail"],
                user_inputs["change_inter_city_rail"],
                user_inputs["mp_energy_elec_motion"],
                user_inputs["change_marine_port"],
                user_inputs["change_off_road"],
                user_inputs["or_energy_elec_motion"],
                user_inputs["change_ag"],
                user_inputs["change_industrial_processes"],
                user_inputs["change_solid_waste"],
                user_inputs["change_wastewater"],
                user_inputs["change_forest"],
                user_inputs["change_urban_trees"],
                user_inputs["ff_carbon_capture"],
                user_inputs["air_capture"],
            ),
        ],
        "Residential Stationary Energy": [
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
        "Non-Residential Stationary Energy": [
            GHG_CI,
            calc_ci_ghg(
                user_inputs["ci_energy_elec"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ci_energy_change"],
            )[0],
        ],
        "On-Road Motor Vehicles": [
            GHG_HIGHWAY,
            calc_highway_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["veh_miles_elec"],
                user_inputs["change_pop"],
                user_inputs["reg_fleet_mpg"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
                user_inputs["change_veh_miles"],
            )[0],
        ],
        "Rail": [
            GHG_RAIL,
            calc_rail_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["change_rail_transit"],
                user_inputs["change_pop"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
                user_inputs["rt_energy_elec_motion"],
                user_inputs["f_energy_elec_motion"],
                user_inputs["icr_energy_elec_motion"],
                user_inputs["change_freight_rail"],
                user_inputs["change_inter_city_rail"],
            )[0],
        ],
        "Aviation": [
            GHG_AVIATION,
            calc_aviation_ghg(user_inputs["change_pop"], user_inputs["change_air_travel"]),
        ],
        "Other Mobile Energy": [
            GHG_OTHER_MOBILE,
            calc_other_mobile_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["mp_energy_elec_motion"],
                user_inputs["change_marine_port"],
                user_inputs["change_off_road"],
                user_inputs["or_energy_elec_motion"],
            )[0],
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
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
            ),
        ],
    }
    return data


def wrangle_pos_data_for_stacked_chart(user_inputs):
    # Transpose data
    data = {
        "Year": ["2015", "Scenario"],
        "Residential Stationary Energy": [
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
        "Non-Residential Stationary Energy": [
            GHG_CI,
            calc_ci_ghg(
                user_inputs["ci_energy_elec"],
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["ci_energy_change"],
            )[0],
        ],
        "On-Road Motor Vehicles": [
            GHG_HIGHWAY,
            calc_highway_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["veh_miles_elec"],
                user_inputs["change_pop"],
                user_inputs["reg_fleet_mpg"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
                user_inputs["change_veh_miles"],
            )[0],
        ],
        "Rail": [
            GHG_RAIL,
            calc_rail_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["change_rail_transit"],
                user_inputs["change_pop"],
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
                user_inputs["rt_energy_elec_motion"],
                user_inputs["f_energy_elec_motion"],
                user_inputs["icr_energy_elec_motion"],
                user_inputs["change_freight_rail"],
                user_inputs["change_inter_city_rail"],
            )[0],
        ],
        "Aviation": [
            GHG_AVIATION,
            calc_aviation_ghg(user_inputs["change_pop"], user_inputs["change_air_travel"]),
        ],
        "Other Mobile Energy": [
            GHG_OTHER_MOBILE,
            calc_other_mobile_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["mp_energy_elec_motion"],
                user_inputs["change_marine_port"],
                user_inputs["change_off_road"],
                user_inputs["or_energy_elec_motion"],
            )[0],
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
                user_inputs["rural_pop_percent"],
                user_inputs["suburban_pop_percent"],
                user_inputs["urban_pop_percent"],
            ),
        ],
    }
    return data


def wrangle_neg_data_for_stacked_chart(user_inputs):
    # Transpose data
    data = {
        "Year": ["2015", "Scenario"],
        "Carbon Sequestration & Storage": [
            GHG_SEQ,
            calc_sequestration(
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
                user_inputs["ci_energy_elec"],
                user_inputs["ci_energy_change"],
                user_inputs["veh_miles_elec"],
                user_inputs["reg_fleet_mpg"],
                user_inputs["change_veh_miles"],
                user_inputs["change_rail_transit"],
                user_inputs["rt_energy_elec_motion"],
                user_inputs["f_energy_elec_motion"],
                user_inputs["icr_energy_elec_motion"],
                user_inputs["change_freight_rail"],
                user_inputs["change_inter_city_rail"],
                user_inputs["mp_energy_elec_motion"],
                user_inputs["change_marine_port"],
                user_inputs["change_off_road"],
                user_inputs["or_energy_elec_motion"],
                user_inputs["change_ag"],
                user_inputs["change_industrial_processes"],
                user_inputs["change_solid_waste"],
                user_inputs["change_wastewater"],
                user_inputs["change_forest"],
                user_inputs["change_urban_trees"],
                user_inputs["ff_carbon_capture"],
                user_inputs["air_capture"],
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

    data = pd.Series(x).reset_index(name="percentage").rename(columns={"index": "fuel_type"})
    data["angle"] = data["percentage"] / data["percentage"].sum() * 2 * pi
    data["color"] = Spectral10

    return data


##############################
# Functions to create charts #
##############################

"""
We need these functions that create the charts - rather than creating the charts directly and
importing them into the appropriate view - because bokeh requires that each Figure be in only
one document, otherwise it seems that multiple users could be changing the same chart/input
at the same time. So main/views.py imports these functions, and then individual views create
the charts as needed.

Additionally, the data/source (for the bar chart and stacked bar chart) and source (for pie chart)
are created outside these functions and then used as parameters because, in order to update the
chart, we need to directly update the source.data attribute after user inputs change. Otherwise,
they could be created at the top of each function and then used within them.
"""


def create_bar_chart(data, source):
    """
    Return a figure object.

    *data* is output of wrangle_data_for_bar_chart().

    *source* is the result of feeding *data* into bokeh's ColumnDataSource().
    """
    bar_chart = figure(
        x_range=data["Category"],
        y_range=(-25, 50),
        plot_height=500,
        plot_width=750,
        y_axis_label="Million Metric Tons of CO2e",
        title="Greenhouse Gas Emissions in Greater Philadelphia",
        name="barchart",
        toolbar_location="below",
    )
    bar_chart.vbar(
        x=dodge("Category", -0.15, range=bar_chart.x_range),
        top="2015",
        source=source,
        width=0.2,
        color="steelblue",
        legend_label="2015",
    )
    bar_chart.vbar(
        x=dodge("Category", 0.15, range=bar_chart.x_range),
        top="Scenario",
        source=source,
        width=0.2,
        color="darkseagreen",
        legend_label="Scenario",
    )
    bar_chart.xaxis.major_label_orientation = np.pi / 4
    bar_chart.x_range.range_padding = 0.1

    labels_scenario = LabelSet(
        x=dodge("Category", 0.15, range=bar_chart.x_range),
        y="Scenario",
        x_offset=4,
        y_offset=5,
        text="Scenario",
        text_font_size="10px",
        angle=1.57,
        level="glyph",
        source=source,
    )
    labels_2015 = LabelSet(
        x=dodge("Category", 0.15, range=bar_chart.x_range),
        y="2015",
        x_offset=-10,
        y_offset=5,
        text="2015",
        text_font_size="10px",
        angle=1.57,
        level="glyph",
        source=source,
    )
    bar_chart.add_layout(labels_scenario)
    bar_chart.add_layout(labels_2015)
    bar_chart.add_layout(bar_chart.legend[0], "right")

    return bar_chart


POS_SECTORS = [
    "Residential Stationary Energy",
    "Non-Residential Stationary Energy",
    "On-Road Motor Vehicles",
    "Rail",
    "Aviation",
    "Other Mobile Energy",
    "Non-Energy",
]


def create_stacked_chart(positive_data, negative_data, positive_source, negative_source):
    """
    Return a figure object.

    *positive_data* is output of wrangle_data_for_stacked_chart().

    *source* is the result of feeding *data* into bokeh's ColumnDataSource().
    """
    stacked_bar_chart = figure(
        x_range=positive_data["Year"],
        y_range=(-50, 100),
        plot_height=500,
        plot_width=500,
        y_axis_label="Million Metric Tons of CO2e",
        title="Greenhouse Gas Emissions in Greater Philadelphia",
        toolbar_location="below",
    )
    stacked_bar_chart.vbar_stack(
        ["Carbon Sequestration & Storage"],
        x="Year",
        width=0.4,
        color=Viridis8[:1],
        source=negative_source,
        legend_label=["Carbon Sequestration & Storage"],
    )
    stacked_bar_chart.vbar_stack(
        POS_SECTORS,
        x="Year",
        width=0.4,
        color=Viridis8[1:],
        source=positive_source,
        legend_label=POS_SECTORS,
    )
    stacked_bar_chart.legend[0].items.reverse()  # Reverse legend items to match order in stack
    stacked_bar_chart_legend = stacked_bar_chart.legend[0]
    stacked_bar_chart.add_layout(stacked_bar_chart_legend, "right")

    return stacked_bar_chart


def create_pie_chart(source):
    """
    Return a figure object.

    *source* is the result of feeding the output from wrangle_data_for_piechart() into
    bokeh's ColumnDataSource().
    """
    pie_chart = figure(
        title="Electricity Grid Resource Mix",
        toolbar_location="below",
        plot_height=400,
        plot_width=750,
        tooltips="@fuel_type: @percentage",
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
        legend_field="fuel_type",
        source=source,
    )
    pie_chart.axis.axis_label = None
    pie_chart.axis.visible = False
    pie_chart.grid.grid_line_color = None
    pie_chart.add_layout(pie_chart.legend[0], "right")

    return pie_chart
