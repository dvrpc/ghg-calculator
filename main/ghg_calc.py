from math import pi
from statistics import mean

import numpy as np
import pandas as pd

from bokeh.layouts import row, column, layout
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
PerCombCapture = 0

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
MCFperCCF = 0.1
MillionCFperCF = 0.000001
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
PerCapResEnergyUse = 0

UrbanPerCapElec = 2.41  # MWh/person
SuburbanPerCapElec = 3.17  # MWh/person
RuralPerCapElec = 3.81  # MWh/person

UrbanBTUPerCapElec = UrbanPerCapElec * BTU_MWH  # BTU/Person
SuburbanBTUPerCapElec = SuburbanPerCapElec * BTU_MWH  # BTU/Person
RuralBTUPerCapElec = RuralPerCapElec * BTU_MWH  # BTU/Person

UrbanPerCapNG = 246.04  # CCF/person
SuburbanPerCapNG = 193.00  # CCF/person
RuralPerCapNG = 89.35  # CCF/person

UrbanBTUPerCapNG = UrbanPerCapNG * BTU_CCF_AVG  # BTU/Person
SuburbanBTUPerCapNG = SuburbanPerCapNG * BTU_CCF_AVG  # BTU/Person
RuralBTUPerCapNG = RuralPerCapNG * BTU_CCF_AVG  # BTU/Person

UrbanPerCapFOKer = 14.50  # gallons/person
SuburbanPerCapFOKer = 43.32  # gallons/person
RuralPerCapFOKer = 80.84  # gallons/person

UrbanBTUPerCapFOKer = UrbanPerCapFOKer * BTU_GAL_FOK  # BTU/Person
SuburbanBTUPerCapFOKer = SuburbanPerCapFOKer * BTU_GAL_FOK  # BTU/Person
RuralBTUPerCapFOKer = RuralPerCapFOKer * BTU_GAL_FOK  # BTU/Person

UrbanPerCapLPG = 3.46  # gallons/person
SuburbanPerCapLPG = 8.44  # gallons/person
RuralPerCapLPG = 44.38  # gallons/person

UrbanBTUPerCapLPG = UrbanPerCapLPG * BTU_GAL_LPG  # BTU/Person
SuburbanBTUPerCapLPG = SuburbanPerCapLPG * BTU_GAL_LPG  # BTU/Person
RuralBTUPerCapLPG = RuralPerCapLPG * BTU_GAL_LPG  # BTU/Person

# End uses for residential fuels from EIA 2015 by % of Trillion BTUs
PerResElecSpaceHeating = 12.84
PerResElecWaterHeating = 11.94
PerResElecOther = 75.23

PerResNGSpaceHeating = 70.66
PerResNGWaterHeating = 22.24
PerResNGOther = 6.97

PerResFOKerSpaceHeating = 83.33
PerResFOKerWaterHeating = 16.13
PerResFOKerOther = 0.54

PerResLPGSpaceHeating = 65.22
PerResLPGWaterHeating = 19.57
PerResLPGOther = 15.22

# Energy to use efficiencies for residential end uses and fuels
PerEnergyToUseResElecSpaceHeating = 100
PerEnergyToUseResElecWaterHeating = 100
PerEnergyToUseResElecOther = 100
PerEnergyToUseResElecSpaceHeatingSwitch = 250
PerEnergyToUseResElecWaterHeatingSwitch = 150

PerEnergyToUseResNGSpaceHeating = 80  # 80% 2014 federal minimum, 95% ENERGY STAR spec
PerEnergyToUseResNGWaterHeating = 82  # 80-82% 2012 federal minimum, 90% ENERGY STAR spec
PerEnergyToUseResNGOther = 80

PerEnergyToUseResFOKerSpaceHeating = 80
PerEnergyToUseResFOKerWaterHeating = 80
PerEnergyToUseResFOKerOther = 80

PerEnergyToUseResLPGSpaceHeating = 80
PerEnergyToUseResLPGWaterHeating = 80
PerEnergyToUseResLPGOther = 80

# Btus per person per community type, fuel type, and end use
UrbanBTUPerCapElecSpaceHeatingUsed = (
    UrbanBTUPerCapElec * (PerResElecSpaceHeating / 100) * (PerEnergyToUseResElecSpaceHeating / 100)
)
UrbanBTUPerCapElecWaterHeatingUsed = (
    UrbanBTUPerCapElec * (PerResElecWaterHeating / 100) * (PerEnergyToUseResElecWaterHeating / 100)
)
UrbanBTUPerCapElecOtherUsed = (
    UrbanBTUPerCapElec * (PerResElecOther / 100) * (PerEnergyToUseResElecOther / 100)
)
SuburbanBTUPerCapElecSpaceHeatingUsed = (
    SuburbanBTUPerCapElec
    * (PerResElecSpaceHeating / 100)
    * (PerEnergyToUseResElecSpaceHeating / 100)
)
SuburbanBTUPerCapElecWaterHeatingUsed = (
    SuburbanBTUPerCapElec
    * (PerResElecWaterHeating / 100)
    * (PerEnergyToUseResElecWaterHeating / 100)
)
SuburbanBTUPerCapElecOtherUsed = (
    SuburbanBTUPerCapElec * (PerResElecOther / 100) * (PerEnergyToUseResElecOther / 100)
)
RuralBTUPerCapElecSpaceHeatingUsed = (
    RuralBTUPerCapElec * (PerResElecSpaceHeating / 100) * (PerEnergyToUseResElecSpaceHeating / 100)
)
RuralBTUPerCapElecWaterHeatingUsed = (
    RuralBTUPerCapElec * (PerResElecWaterHeating / 100) * (PerEnergyToUseResElecWaterHeating / 100)
)
RuralBTUPerCapElecOtherUsed = (
    RuralBTUPerCapElec * (PerResElecOther / 100) * (PerEnergyToUseResElecOther / 100)
)

UrbanBTUPerCapNGSpaceHeatingUsed = (
    UrbanBTUPerCapNG * (PerResNGSpaceHeating / 100) * (PerEnergyToUseResNGSpaceHeating / 100)
)
UrbanBTUPerCapNGWaterHeatingUsed = (
    UrbanBTUPerCapNG * (PerResNGWaterHeating / 100) * (PerEnergyToUseResNGWaterHeating / 100)
)
UrbanBTUPerCapNGOtherUsed = (
    UrbanBTUPerCapNG * (PerResNGOther / 100) * (PerEnergyToUseResNGOther / 100)
)
SuburbanBTUPerCapNGSpaceHeatingUsed = (
    SuburbanBTUPerCapNG * (PerResNGSpaceHeating / 100) * (PerEnergyToUseResNGSpaceHeating / 100)
)
SuburbanBTUPerCapNGWaterHeatingUsed = (
    SuburbanBTUPerCapNG * (PerResNGWaterHeating / 100) * (PerEnergyToUseResNGWaterHeating / 100)
)
SuburbanBTUPerCapNGOtherUsed = (
    SuburbanBTUPerCapNG * (PerResNGOther / 100) * (PerEnergyToUseResNGOther / 100)
)
RuralBTUPerCapNGSpaceHeatingUsed = (
    RuralBTUPerCapNG * (PerResNGSpaceHeating / 100) * (PerEnergyToUseResNGSpaceHeating / 100)
)
RuralBTUPerCapNGWaterHeatingUsed = (
    RuralBTUPerCapNG * (PerResNGWaterHeating / 100) * (PerEnergyToUseResNGWaterHeating / 100)
)
RuralBTUPerCapNGOtherUsed = (
    RuralBTUPerCapNG * (PerResNGOther / 100) * (PerEnergyToUseResNGOther / 100)
)

UrbanBTUPerCapFOKerSpaceHeatingUsed = (
    UrbanBTUPerCapFOKer
    * (PerResFOKerSpaceHeating / 100)
    * (PerEnergyToUseResFOKerSpaceHeating / 100)
)
UrbanBTUPerCapFOKerWaterHeatingUsed = (
    UrbanBTUPerCapFOKer
    * (PerResFOKerWaterHeating / 100)
    * (PerEnergyToUseResFOKerWaterHeating / 100)
)
UrbanBTUPerCapFOKerOtherUsed = (
    UrbanBTUPerCapFOKer * (PerResFOKerOther / 100) * (PerEnergyToUseResFOKerOther / 100)
)
SuburbanBTUPerCapFOKerSpaceHeatingUsed = (
    SuburbanBTUPerCapFOKer
    * (PerResFOKerSpaceHeating / 100)
    * (PerEnergyToUseResFOKerSpaceHeating / 100)
)
SuburbanBTUPerCapFOKerWaterHeatingUsed = (
    SuburbanBTUPerCapFOKer
    * (PerResFOKerWaterHeating / 100)
    * (PerEnergyToUseResFOKerWaterHeating / 100)
)
SuburbanBTUPerCapFOKerOtherUsed = (
    SuburbanBTUPerCapFOKer * (PerResFOKerOther / 100) * (PerEnergyToUseResFOKerOther / 100)
)
RuralBTUPerCapFOKerSpaceHeatingUsed = (
    RuralBTUPerCapFOKer
    * (PerResFOKerSpaceHeating / 100)
    * (PerEnergyToUseResFOKerSpaceHeating / 100)
)
RuralBTUPerCapFOKerWaterHeatingUsed = (
    RuralBTUPerCapFOKer
    * (PerResFOKerWaterHeating / 100)
    * (PerEnergyToUseResFOKerWaterHeating / 100)
)
RuralBTUPerCapFOKerOtherUsed = (
    RuralBTUPerCapFOKer * (PerResFOKerOther / 100) * (PerEnergyToUseResFOKerOther / 100)
)

UrbanBTUPerCapLPGSpaceHeatingUsed = (
    UrbanBTUPerCapLPG * (PerResLPGSpaceHeating / 100) * (PerEnergyToUseResLPGSpaceHeating / 100)
)
UrbanBTUPerCapLPGWaterHeatingUsed = (
    UrbanBTUPerCapLPG * (PerResLPGWaterHeating / 100) * (PerEnergyToUseResLPGWaterHeating / 100)
)
UrbanBTUPerCapLPGOtherUsed = (
    UrbanBTUPerCapLPG * (PerResLPGOther / 100) * (PerEnergyToUseResLPGOther / 100)
)
SuburbanBTUPerCapLPGSpaceHeatingUsed = (
    SuburbanBTUPerCapLPG * (PerResLPGSpaceHeating / 100) * (PerEnergyToUseResLPGSpaceHeating / 100)
)
SuburbanBTUPerCapLPGWaterHeatingUsed = (
    SuburbanBTUPerCapLPG * (PerResLPGWaterHeating / 100) * (PerEnergyToUseResLPGWaterHeating / 100)
)
SuburbanBTUPerCapLPGOtherUsed = (
    SuburbanBTUPerCapLPG * (PerResLPGOther / 100) * (PerEnergyToUseResLPGOther / 100)
)
RuralBTUPerCapLPGSpaceHeatingUsed = (
    RuralBTUPerCapLPG * (PerResLPGSpaceHeating / 100) * (PerEnergyToUseResLPGSpaceHeating / 100)
)
RuralBTUPerCapLPGWaterHeatingUsed = (
    RuralBTUPerCapLPG * (PerResLPGWaterHeating / 100) * (PerEnergyToUseResLPGWaterHeating / 100)
)
RuralBTUPerCapLPGOtherUsed = (
    RuralBTUPerCapLPG * (PerResLPGOther / 100) * (PerEnergyToUseResLPGOther / 100)
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

UrbanPerResElecUsed = UrbanBTUPerCapElecUsed / UrbanBTUPerCapUsed * 100
SuburbanPerResElecUsed = SuburbanBTUPerCapElecUsed / SuburbanBTUPerCapUsed * 100
RuralPerResElecUsed = RuralBTUPerCapElecUsed / RuralBTUPerCapUsed * 100

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

UrbanPerResElectrification = UrbanMinPerResElectrification
SuburbanPerResElectrification = SuburbanMinPerResElectrification
RuralPerResElectrification = RuralMinPerResElectrification

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
    "PerCapResEnergyUse": PerCapResEnergyUse,
    "PerCombCapture": PerCombCapture,
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
    "RuralPerResElectrification": RuralPerResElectrification,
    "rural_pop_percent": rural_pop_percent,
    "SuburbanPerResElectrification": SuburbanPerResElectrification,
    "suburban_pop_percent": suburban_pop_percent,
    "TransRailRuralPerElecMotion": TransRailRuralPerElecMotion,
    "TransRailSuburbanPerElecMotion": TransRailSuburbanPerElecMotion,
    "TransRailUrbanPerElecMotion": TransRailUrbanPerElecMotion,
    "UrbanPerResElectrification": UrbanPerResElectrification,
    "urban_pop_percent": urban_pop_percent,
    "VMTperCap": VMTperCap,
}


def calc_res_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    PerCapResEnergyUse,
    pop_factor,
    RuralPerResElectrification,
    SuburbanPerResElectrification,
    UrbanPerResElectrification,
    rural_pop_percent,
    suburban_pop_percent,
    urban_pop_percent,
):
    """
    Determine BTU of energy by sub-sector (urban, suburban, rural) and from that calculate
    ghg emissions.
    """
    UrbanResBTUUsed = (
        POP
        * (1 + pop_factor / 100)
        * (urban_pop_percent / 100)
        * UrbanBTUPerCapUsed
        * (1 + PerCapResEnergyUse / 100)
    )
    UrbanPerChangedFossilFuelUsed = UrbanPerResElectrification - UrbanPerResElecUsed
    UrbanPerResElecUsedToFFHeating = UrbanPerResElecUsed - UrbanPerResElectrification

    UrbanResElecBTUUsed = UrbanResBTUUsed * (UrbanPerResElecUsed / 100)
    UrbanResElecSpaceHeatingBTUUsed = UrbanResElecBTUUsed * (
        PerUrbanElecBTUPerCapUsedSpaceHeating / 100
    )
    UrbanResElecWaterHeatingBTUUsed = UrbanResElecBTUUsed * (
        PerUrbanElecBTUPerCapUsedWaterHeating / 100
    )
    UrbanResElecOtherBTUUsed = UrbanResElecBTUUsed * (PerUrbanElecBTUPerCapUsedOther / 100)

    UrbanResNGBTUUsed = UrbanResBTUUsed * (UrbanPerResNGUsed / 100)
    UrbanResNGSpaceHeatingBTUUsed = UrbanResNGBTUUsed * (PerUrbanNGBTUPerCapUsedSpaceHeating / 100)
    UrbanResNGWaterHeatingBTUUsed = UrbanResNGBTUUsed * (PerUrbanNGBTUPerCapUsedWaterHeating / 100)
    UrbanResNGOtherBTUUsed = UrbanResNGBTUUsed * (PerUrbanNGBTUPerCapUsedOther / 100)

    UrbanResFOKerBTUUsed = UrbanResBTUUsed * (UrbanPerResFOKerUsed / 100)
    UrbanResFOKerSpaceHeatingBTUUsed = UrbanResFOKerBTUUsed * (
        PerUrbanFOKerBTUPerCapUsedSpaceHeating / 100
    )
    UrbanResFOKerWaterHeatingBTUUsed = UrbanResFOKerBTUUsed * (
        PerUrbanFOKerBTUPerCapUsedWaterHeating / 100
    )
    UrbanResFOKerOtherBTUUsed = UrbanResFOKerBTUUsed * (PerUrbanFOKerBTUPerCapUsedOther / 100)

    UrbanResLPGBTUUsed = UrbanResBTUUsed * (UrbanPerResLPGUsed / 100)
    UrbanResLPGSpaceHeatingBTUUsed = UrbanResLPGBTUUsed * (
        PerUrbanLPGBTUPerCapUsedSpaceHeating / 100
    )
    UrbanResLPGWaterHeatingBTUUsed = UrbanResLPGBTUUsed * (
        PerUrbanLPGBTUPerCapUsedWaterHeating / 100
    )
    UrbanResLPGOtherBTUUsed = UrbanResLPGBTUUsed * (PerUrbanLPGBTUPerCapUsedOther / 100)

    # Fuel Switch to Electric
    UrbanResNGSpaceHeatingToElecBTUUsed = (
        UrbanResBTUUsed
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFNGUsed / 100)
        * (PerUrbanNGBTUPerCapUsedSpaceHeating / 100)
    )
    UrbanResNGWaterHeatingToElecBTUUsed = (
        UrbanResBTUUsed
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFNGUsed / 100)
        * (PerUrbanNGBTUPerCapUsedWaterHeating / 100)
    )
    UrbanResNGOtherToElecBTUUsed = (
        UrbanResBTUUsed
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFNGUsed / 100)
        * (PerUrbanNGBTUPerCapUsedOther / 100)
    )
    UrbanResFOKerSpaceHeatingToElecBTUUsed = (
        UrbanResBTUUsed
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFFOKerUsed / 100)
        * (PerUrbanFOKerBTUPerCapUsedSpaceHeating / 100)
    )
    UrbanResFOKerWaterHeatingToElecBTUUsed = (
        UrbanResBTUUsed
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFFOKerUsed / 100)
        * (PerUrbanFOKerBTUPerCapUsedWaterHeating / 100)
    )
    UrbanResFOKerOtherToElecBTUUsed = (
        UrbanResBTUUsed
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFFOKerUsed / 100)
        * (PerUrbanFOKerBTUPerCapUsedOther / 100)
    )
    UrbanResLPGSpaceHeatingToElecBTUUsed = (
        UrbanResBTUUsed
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFLPGUsed / 100)
        * (PerUrbanLPGBTUPerCapUsedSpaceHeating / 100)
    )
    UrbanResLPGWaterHeatingToElecBTUUsed = (
        UrbanResBTUUsed
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFLPGUsed / 100)
        * (PerUrbanLPGBTUPerCapUsedWaterHeating / 100)
    )
    UrbanResLPGOtherToElecBTUUsed = (
        UrbanResBTUUsed
        * (UrbanPerChangedFossilFuelUsed / 100)
        * (UrbanPerResFFLPGUsed / 100)
        * (PerUrbanLPGBTUPerCapUsedOther / 100)
    )

    # Fuel Switch to Fossil Fuels heating uses
    UrbanResElecToNGSpaceHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (UrbanPerResElecUsedToFFHeating / 100)
        * (UrbanPerElecHeatingUsedforSpaceHeating / 100)
        * (UrbanPerResFFSpaceHeatingNGUsed / 100)
    )

    UrbanResElecToNGWaterHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (UrbanPerResElecUsedToFFHeating / 100)
        * (UrbanPerElecHeatingUsedforWaterHeating / 100)
        * (UrbanPerResFFWaterHeatingNGUsed / 100)
    )

    UrbanResElecToFOKerSpaceHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (UrbanPerResElecUsedToFFHeating / 100)
        * (UrbanPerElecHeatingUsedforSpaceHeating / 100)
        * (UrbanPerResFFSpaceHeatingFOKerUsed / 100)
    )

    UrbanResElecToFOKerWaterHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (UrbanPerResElecUsedToFFHeating / 100)
        * (UrbanPerElecHeatingUsedforWaterHeating / 100)
        * (UrbanPerResFFWaterHeatingFOKerUsed / 100)
    )

    UrbanResElecToLPGSpaceHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (UrbanPerResElecUsedToFFHeating / 100)
        * (UrbanPerElecHeatingUsedforSpaceHeating / 100)
        * (UrbanPerResFFSpaceHeatingLPGUsed / 100)
    )

    UrbanResElecToLPGWaterHeatingBTUUsed = (
        UrbanResElecBTUUsed
        * (UrbanPerResElecUsedToFFHeating / 100)
        * (UrbanPerElecHeatingUsedforWaterHeating / 100)
        * (UrbanPerResFFWaterHeatingLPGUsed / 100)
    )

    # Determine whether fossil fuels (and all uses) are switched to electricity or if electricity
    # heating uses are switched to fossil fuel heating uses
    if UrbanPerChangedFossilFuelUsed >= 0:
        UrbanResElecBTU = (
            (UrbanResElecSpaceHeatingBTUUsed / (PerEnergyToUseResElecSpaceHeating / 100))
            + (UrbanResElecWaterHeatingBTUUsed / (PerEnergyToUseResElecWaterHeating / 100))
            + (UrbanResElecOtherBTUUsed / (PerEnergyToUseResElecOther / 100))
            + (
                (
                    UrbanResNGSpaceHeatingToElecBTUUsed
                    + UrbanResFOKerSpaceHeatingToElecBTUUsed
                    + UrbanResLPGSpaceHeatingToElecBTUUsed
                )
                / (PerEnergyToUseResElecSpaceHeatingSwitch / 100)
            )
            + (
                (
                    UrbanResNGWaterHeatingToElecBTUUsed
                    + UrbanResFOKerWaterHeatingToElecBTUUsed
                    + UrbanResLPGWaterHeatingToElecBTUUsed
                )
                / (PerEnergyToUseResElecWaterHeatingSwitch / 100)
            )
            + (
                (
                    UrbanResNGOtherToElecBTUUsed
                    + UrbanResFOKerOtherToElecBTUUsed
                    + UrbanResLPGOtherToElecBTUUsed
                )
                / (PerEnergyToUseResElecOther / 100)
            )
        )

        UrbanResNGBTU = (
            (
                (UrbanResNGSpaceHeatingBTUUsed - UrbanResNGSpaceHeatingToElecBTUUsed)
                / (PerEnergyToUseResNGSpaceHeating / 100)
            )
            + (
                (UrbanResNGWaterHeatingBTUUsed - UrbanResNGWaterHeatingToElecBTUUsed)
                / (PerEnergyToUseResNGWaterHeating / 100)
            )
            + (
                (UrbanResNGOtherBTUUsed - UrbanResNGOtherToElecBTUUsed)
                / (PerEnergyToUseResNGOther / 100)
            )
        )

        UrbanResFOKerBTU = (
            (
                (UrbanResFOKerSpaceHeatingBTUUsed - UrbanResFOKerSpaceHeatingToElecBTUUsed)
                / (PerEnergyToUseResFOKerSpaceHeating / 100)
            )
            + (
                (UrbanResFOKerWaterHeatingBTUUsed - UrbanResFOKerWaterHeatingToElecBTUUsed)
                / (PerEnergyToUseResFOKerWaterHeating / 100)
            )
            + (
                (UrbanResFOKerOtherBTUUsed - UrbanResFOKerOtherToElecBTUUsed)
                / (PerEnergyToUseResFOKerOther / 100)
            )
        )

        UrbanResLPGBTU = (
            (
                (UrbanResLPGSpaceHeatingBTUUsed - UrbanResLPGSpaceHeatingToElecBTUUsed)
                / (PerEnergyToUseResLPGSpaceHeating / 100)
            )
            + (
                (UrbanResLPGWaterHeatingBTUUsed - UrbanResLPGWaterHeatingToElecBTUUsed)
                / (PerEnergyToUseResLPGWaterHeating / 100)
            )
            + (
                (UrbanResLPGOtherBTUUsed - UrbanResLPGOtherToElecBTUUsed)
                / (PerEnergyToUseResLPGOther / 100)
            )
        )
    else:
        UrbanResElecBTU = (
            (UrbanResElecOtherBTUUsed / (PerEnergyToUseResElecOther / 100))
            + (
                (
                    UrbanResElecSpaceHeatingBTUUsed
                    - (
                        UrbanResElecToNGSpaceHeatingBTUUsed
                        + UrbanResElecToFOKerSpaceHeatingBTUUsed
                        + UrbanResElecToLPGSpaceHeatingBTUUsed
                    )
                )
                / (PerEnergyToUseResElecSpaceHeating / 100)
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
                / (PerEnergyToUseResElecWaterHeating / 100)
            )
        )

        UrbanResNGBTU = (
            (UrbanResNGOtherBTUUsed / (PerEnergyToUseResNGOther / 100))
            + (
                (UrbanResNGSpaceHeatingBTUUsed + UrbanResElecToNGSpaceHeatingBTUUsed)
                / (PerEnergyToUseResNGSpaceHeating / 100)
            )
            + (
                (UrbanResNGWaterHeatingBTUUsed + UrbanResElecToNGWaterHeatingBTUUsed)
                / (PerEnergyToUseResNGWaterHeating / 100)
            )
        )

        UrbanResFOKerBTU = (
            (UrbanResFOKerOtherBTUUsed / (PerEnergyToUseResFOKerOther / 100))
            + (
                (UrbanResFOKerSpaceHeatingBTUUsed + UrbanResElecToFOKerSpaceHeatingBTUUsed)
                / (PerEnergyToUseResFOKerSpaceHeating / 100)
            )
            + (
                (UrbanResFOKerWaterHeatingBTUUsed + UrbanResElecToFOKerWaterHeatingBTUUsed)
                / (PerEnergyToUseResFOKerWaterHeating / 100)
            )
        )

        UrbanResLPGBTU = (
            (UrbanResLPGOtherBTUUsed / (PerEnergyToUseResLPGOther / 100))
            + (
                (UrbanResLPGSpaceHeatingBTUUsed + UrbanResElecToLPGSpaceHeatingBTUUsed)
                / (PerEnergyToUseResLPGSpaceHeating / 100)
            )
            + (
                (UrbanResLPGWaterHeatingBTUUsed + UrbanResElecToLPGWaterHeatingBTUUsed)
                / (PerEnergyToUseResLPGWaterHeating / 100)
            )
        )

    SuburbanResBTUUsed = (
        POP
        * (1 + pop_factor / 100)
        * (suburban_pop_percent / 100)
        * SuburbanBTUPerCapUsed
        * (1 + PerCapResEnergyUse / 100)
    )
    SuburbanPerChangedFossilFuelUsed = SuburbanPerResElectrification - SuburbanPerResElecUsed
    SuburbanPerResElecUsedToFFHeating = SuburbanPerResElecUsed - SuburbanPerResElectrification

    SuburbanResElecBTUUsed = SuburbanResBTUUsed * (SuburbanPerResElecUsed / 100)
    SuburbanResElecSpaceHeatingBTUUsed = SuburbanResElecBTUUsed * (
        PerSuburbanElecBTUPerCapUsedSpaceHeating / 100
    )
    SuburbanResElecWaterHeatingBTUUsed = SuburbanResElecBTUUsed * (
        PerSuburbanElecBTUPerCapUsedWaterHeating / 100
    )
    SuburbanResElecOtherBTUUsed = SuburbanResElecBTUUsed * (PerSuburbanElecBTUPerCapUsedOther / 100)

    SuburbanResNGBTUUsed = SuburbanResBTUUsed * (SuburbanPerResNGUsed / 100)
    SuburbanResNGSpaceHeatingBTUUsed = SuburbanResNGBTUUsed * (
        PerSuburbanNGBTUPerCapUsedSpaceHeating / 100
    )
    SuburbanResNGWaterHeatingBTUUsed = SuburbanResNGBTUUsed * (
        PerSuburbanNGBTUPerCapUsedWaterHeating / 100
    )
    SuburbanResNGOtherBTUUsed = SuburbanResNGBTUUsed * (PerSuburbanNGBTUPerCapUsedOther / 100)

    SuburbanResFOKerBTUUsed = SuburbanResBTUUsed * (SuburbanPerResFOKerUsed / 100)
    SuburbanResFOKerSpaceHeatingBTUUsed = SuburbanResFOKerBTUUsed * (
        PerSuburbanFOKerBTUPerCapUsedSpaceHeating / 100
    )
    SuburbanResFOKerWaterHeatingBTUUsed = SuburbanResFOKerBTUUsed * (
        PerSuburbanFOKerBTUPerCapUsedWaterHeating / 100
    )
    SuburbanResFOKerOtherBTUUsed = SuburbanResFOKerBTUUsed * (
        PerSuburbanFOKerBTUPerCapUsedOther / 100
    )

    SuburbanResLPGBTUUsed = SuburbanResBTUUsed * (SuburbanPerResLPGUsed / 100)
    SuburbanResLPGSpaceHeatingBTUUsed = SuburbanResLPGBTUUsed * (
        PerSuburbanLPGBTUPerCapUsedSpaceHeating / 100
    )
    SuburbanResLPGWaterHeatingBTUUsed = SuburbanResLPGBTUUsed * (
        PerSuburbanLPGBTUPerCapUsedWaterHeating / 100
    )
    SuburbanResLPGOtherBTUUsed = SuburbanResLPGBTUUsed * (PerSuburbanLPGBTUPerCapUsedOther / 100)

    # Fuel Switch to Electric
    SuburbanResNGSpaceHeatingToElecBTUUsed = (
        SuburbanResBTUUsed
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFNGUsed / 100)
        * (PerSuburbanNGBTUPerCapUsedSpaceHeating / 100)
    )
    SuburbanResNGWaterHeatingToElecBTUUsed = (
        SuburbanResBTUUsed
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFNGUsed / 100)
        * (PerSuburbanNGBTUPerCapUsedWaterHeating / 100)
    )
    SuburbanResNGOtherToElecBTUUsed = (
        SuburbanResBTUUsed
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFNGUsed / 100)
        * (PerSuburbanNGBTUPerCapUsedOther / 100)
    )
    SuburbanResFOKerSpaceHeatingToElecBTUUsed = (
        SuburbanResBTUUsed
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFFOKerUsed / 100)
        * (PerSuburbanFOKerBTUPerCapUsedSpaceHeating / 100)
    )
    SuburbanResFOKerWaterHeatingToElecBTUUsed = (
        SuburbanResBTUUsed
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFFOKerUsed / 100)
        * (PerSuburbanFOKerBTUPerCapUsedWaterHeating / 100)
    )
    SuburbanResFOKerOtherToElecBTUUsed = (
        SuburbanResBTUUsed
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFFOKerUsed / 100)
        * (PerSuburbanFOKerBTUPerCapUsedOther / 100)
    )
    SuburbanResLPGSpaceHeatingToElecBTUUsed = (
        SuburbanResBTUUsed
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFLPGUsed / 100)
        * (PerSuburbanLPGBTUPerCapUsedSpaceHeating / 100)
    )
    SuburbanResLPGWaterHeatingToElecBTUUsed = (
        SuburbanResBTUUsed
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFLPGUsed / 100)
        * (PerSuburbanLPGBTUPerCapUsedWaterHeating / 100)
    )
    SuburbanResLPGOtherToElecBTUUsed = (
        SuburbanResBTUUsed
        * (SuburbanPerChangedFossilFuelUsed / 100)
        * (SuburbanPerResFFLPGUsed / 100)
        * (PerSuburbanLPGBTUPerCapUsedOther / 100)
    )

    # Fuel Switch to Fossil Fuels heating uses
    SuburbanResElecToNGSpaceHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (SuburbanPerResElecUsedToFFHeating / 100)
        * (SuburbanPerElecHeatingUsedforSpaceHeating / 100)
        * (SuburbanPerResFFSpaceHeatingNGUsed / 100)
    )

    SuburbanResElecToNGWaterHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (SuburbanPerResElecUsedToFFHeating / 100)
        * (SuburbanPerElecHeatingUsedforWaterHeating / 100)
        * (SuburbanPerResFFWaterHeatingNGUsed / 100)
    )

    SuburbanResElecToFOKerSpaceHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (SuburbanPerResElecUsedToFFHeating / 100)
        * (SuburbanPerElecHeatingUsedforSpaceHeating / 100)
        * (SuburbanPerResFFSpaceHeatingFOKerUsed / 100)
    )

    SuburbanResElecToFOKerWaterHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (SuburbanPerResElecUsedToFFHeating / 100)
        * (SuburbanPerElecHeatingUsedforWaterHeating / 100)
        * (SuburbanPerResFFWaterHeatingFOKerUsed / 100)
    )

    SuburbanResElecToLPGSpaceHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (SuburbanPerResElecUsedToFFHeating / 100)
        * (SuburbanPerElecHeatingUsedforSpaceHeating / 100)
        * (SuburbanPerResFFSpaceHeatingLPGUsed / 100)
    )

    SuburbanResElecToLPGWaterHeatingBTUUsed = (
        SuburbanResElecBTUUsed
        * (SuburbanPerResElecUsedToFFHeating / 100)
        * (SuburbanPerElecHeatingUsedforWaterHeating / 100)
        * (SuburbanPerResFFWaterHeatingLPGUsed / 100)
    )

    # Determine whether fossil fuels (and all uses) are switched to electricity or if electricity
    # heating uses are switched to fossil fuel heating uses
    if SuburbanPerChangedFossilFuelUsed >= 0:
        SuburbanResElecBTU = (
            (SuburbanResElecSpaceHeatingBTUUsed / (PerEnergyToUseResElecSpaceHeating / 100))
            + (SuburbanResElecWaterHeatingBTUUsed / (PerEnergyToUseResElecWaterHeating / 100))
            + (SuburbanResElecOtherBTUUsed / (PerEnergyToUseResElecOther / 100))
            + (
                (
                    SuburbanResNGSpaceHeatingToElecBTUUsed
                    + SuburbanResFOKerSpaceHeatingToElecBTUUsed
                    + SuburbanResLPGSpaceHeatingToElecBTUUsed
                )
                / (PerEnergyToUseResElecSpaceHeatingSwitch / 100)
            )
            + (
                (
                    SuburbanResNGWaterHeatingToElecBTUUsed
                    + SuburbanResFOKerWaterHeatingToElecBTUUsed
                    + SuburbanResLPGWaterHeatingToElecBTUUsed
                )
                / (PerEnergyToUseResElecWaterHeatingSwitch / 100)
            )
            + (
                (
                    SuburbanResNGOtherToElecBTUUsed
                    + SuburbanResFOKerOtherToElecBTUUsed
                    + SuburbanResLPGOtherToElecBTUUsed
                )
                / (PerEnergyToUseResElecOther / 100)
            )
        )

        SuburbanResNGBTU = (
            (
                (SuburbanResNGSpaceHeatingBTUUsed - SuburbanResNGSpaceHeatingToElecBTUUsed)
                / (PerEnergyToUseResNGSpaceHeating / 100)
            )
            + (
                (SuburbanResNGWaterHeatingBTUUsed - SuburbanResNGWaterHeatingToElecBTUUsed)
                / (PerEnergyToUseResNGWaterHeating / 100)
            )
            + (
                (SuburbanResNGOtherBTUUsed - SuburbanResNGOtherToElecBTUUsed)
                / (PerEnergyToUseResNGOther / 100)
            )
        )

        SuburbanResFOKerBTU = (
            (
                (SuburbanResFOKerSpaceHeatingBTUUsed - SuburbanResFOKerSpaceHeatingToElecBTUUsed)
                / (PerEnergyToUseResFOKerSpaceHeating / 100)
            )
            + (
                (SuburbanResFOKerWaterHeatingBTUUsed - SuburbanResFOKerWaterHeatingToElecBTUUsed)
                / (PerEnergyToUseResFOKerWaterHeating / 100)
            )
            + (
                (SuburbanResFOKerOtherBTUUsed - SuburbanResFOKerOtherToElecBTUUsed)
                / (PerEnergyToUseResFOKerOther / 100)
            )
        )

        SuburbanResLPGBTU = (
            (
                (SuburbanResLPGSpaceHeatingBTUUsed - SuburbanResLPGSpaceHeatingToElecBTUUsed)
                / (PerEnergyToUseResLPGSpaceHeating / 100)
            )
            + (
                (SuburbanResLPGWaterHeatingBTUUsed - SuburbanResLPGWaterHeatingToElecBTUUsed)
                / (PerEnergyToUseResLPGWaterHeating / 100)
            )
            + (
                (SuburbanResLPGOtherBTUUsed - SuburbanResLPGOtherToElecBTUUsed)
                / (PerEnergyToUseResLPGOther / 100)
            )
        )
    else:
        SuburbanResElecBTU = (
            (SuburbanResElecOtherBTUUsed / (PerEnergyToUseResElecOther / 100))
            + (
                (
                    SuburbanResElecSpaceHeatingBTUUsed
                    - (
                        SuburbanResElecToNGSpaceHeatingBTUUsed
                        + SuburbanResElecToFOKerSpaceHeatingBTUUsed
                        + SuburbanResElecToLPGSpaceHeatingBTUUsed
                    )
                )
                / (PerEnergyToUseResElecSpaceHeating / 100)
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
                / (PerEnergyToUseResElecWaterHeating / 100)
            )
        )

        SuburbanResNGBTU = (
            (SuburbanResNGOtherBTUUsed / (PerEnergyToUseResNGOther / 100))
            + (
                (SuburbanResNGSpaceHeatingBTUUsed + SuburbanResElecToNGSpaceHeatingBTUUsed)
                / (PerEnergyToUseResNGSpaceHeating / 100)
            )
            + (
                (SuburbanResNGWaterHeatingBTUUsed + SuburbanResElecToNGWaterHeatingBTUUsed)
                / (PerEnergyToUseResNGWaterHeating / 100)
            )
        )

        SuburbanResFOKerBTU = (
            (SuburbanResFOKerOtherBTUUsed / (PerEnergyToUseResFOKerOther / 100))
            + (
                (SuburbanResFOKerSpaceHeatingBTUUsed + SuburbanResElecToFOKerSpaceHeatingBTUUsed)
                / (PerEnergyToUseResFOKerSpaceHeating / 100)
            )
            + (
                (SuburbanResFOKerWaterHeatingBTUUsed + SuburbanResElecToFOKerWaterHeatingBTUUsed)
                / (PerEnergyToUseResFOKerWaterHeating / 100)
            )
        )

        SuburbanResLPGBTU = (
            (SuburbanResLPGOtherBTUUsed / (PerEnergyToUseResLPGOther / 100))
            + (
                (SuburbanResLPGSpaceHeatingBTUUsed + SuburbanResElecToLPGSpaceHeatingBTUUsed)
                / (PerEnergyToUseResLPGSpaceHeating / 100)
            )
            + (
                (SuburbanResLPGWaterHeatingBTUUsed + SuburbanResElecToLPGWaterHeatingBTUUsed)
                / (PerEnergyToUseResLPGWaterHeating / 100)
            )
        )

    RuralResBTUUsed = (
        POP
        * (1 + pop_factor / 100)
        * (rural_pop_percent / 100)
        * RuralBTUPerCapUsed
        * (1 + PerCapResEnergyUse / 100)
    )
    RuralPerChangedFossilFuelUsed = RuralPerResElectrification - RuralPerResElecUsed
    RuralPerResElecUsedToFFHeating = RuralPerResElecUsed - RuralPerResElectrification

    RuralResElecBTUUsed = RuralResBTUUsed * (RuralPerResElecUsed / 100)
    RuralResElecSpaceHeatingBTUUsed = RuralResElecBTUUsed * (
        PerRuralElecBTUPerCapUsedSpaceHeating / 100
    )
    RuralResElecWaterHeatingBTUUsed = RuralResElecBTUUsed * (
        PerRuralElecBTUPerCapUsedWaterHeating / 100
    )
    RuralResElecOtherBTUUsed = RuralResElecBTUUsed * (PerRuralElecBTUPerCapUsedOther / 100)

    RuralResNGBTUUsed = RuralResBTUUsed * (RuralPerResNGUsed / 100)
    RuralResNGSpaceHeatingBTUUsed = RuralResNGBTUUsed * (PerRuralNGBTUPerCapUsedSpaceHeating / 100)
    RuralResNGWaterHeatingBTUUsed = RuralResNGBTUUsed * (PerRuralNGBTUPerCapUsedWaterHeating / 100)
    RuralResNGOtherBTUUsed = RuralResNGBTUUsed * (PerRuralNGBTUPerCapUsedOther / 100)

    RuralResFOKerBTUUsed = RuralResBTUUsed * (RuralPerResFOKerUsed / 100)
    RuralResFOKerSpaceHeatingBTUUsed = RuralResFOKerBTUUsed * (
        PerRuralFOKerBTUPerCapUsedSpaceHeating / 100
    )
    RuralResFOKerWaterHeatingBTUUsed = RuralResFOKerBTUUsed * (
        PerRuralFOKerBTUPerCapUsedWaterHeating / 100
    )
    RuralResFOKerOtherBTUUsed = RuralResFOKerBTUUsed * (PerRuralFOKerBTUPerCapUsedOther / 100)

    RuralResLPGBTUUsed = RuralResBTUUsed * (RuralPerResLPGUsed / 100)
    RuralResLPGSpaceHeatingBTUUsed = RuralResLPGBTUUsed * (
        PerRuralLPGBTUPerCapUsedSpaceHeating / 100
    )
    RuralResLPGWaterHeatingBTUUsed = RuralResLPGBTUUsed * (
        PerRuralLPGBTUPerCapUsedWaterHeating / 100
    )
    RuralResLPGOtherBTUUsed = RuralResLPGBTUUsed * (PerRuralLPGBTUPerCapUsedOther / 100)

    # Fuel Switch to Electric
    RuralResNGSpaceHeatingToElecBTUUsed = (
        RuralResBTUUsed
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFNGUsed / 100)
        * (PerRuralNGBTUPerCapUsedSpaceHeating / 100)
    )
    RuralResNGWaterHeatingToElecBTUUsed = (
        RuralResBTUUsed
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFNGUsed / 100)
        * (PerRuralNGBTUPerCapUsedWaterHeating / 100)
    )
    RuralResNGOtherToElecBTUUsed = (
        RuralResBTUUsed
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFNGUsed / 100)
        * (PerRuralNGBTUPerCapUsedOther / 100)
    )
    RuralResFOKerSpaceHeatingToElecBTUUsed = (
        RuralResBTUUsed
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFFOKerUsed / 100)
        * (PerRuralFOKerBTUPerCapUsedSpaceHeating / 100)
    )
    RuralResFOKerWaterHeatingToElecBTUUsed = (
        RuralResBTUUsed
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFFOKerUsed / 100)
        * (PerRuralFOKerBTUPerCapUsedWaterHeating / 100)
    )
    RuralResFOKerOtherToElecBTUUsed = (
        RuralResBTUUsed
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFFOKerUsed / 100)
        * (PerRuralFOKerBTUPerCapUsedOther / 100)
    )
    RuralResLPGSpaceHeatingToElecBTUUsed = (
        RuralResBTUUsed
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFLPGUsed / 100)
        * (PerRuralLPGBTUPerCapUsedSpaceHeating / 100)
    )
    RuralResLPGWaterHeatingToElecBTUUsed = (
        RuralResBTUUsed
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFLPGUsed / 100)
        * (PerRuralLPGBTUPerCapUsedWaterHeating / 100)
    )
    RuralResLPGOtherToElecBTUUsed = (
        RuralResBTUUsed
        * (RuralPerChangedFossilFuelUsed / 100)
        * (RuralPerResFFLPGUsed / 100)
        * (PerRuralLPGBTUPerCapUsedOther / 100)
    )

    # Fuel Switch to Fossil Fuels heating uses
    RuralResElecToNGSpaceHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (RuralPerResElecUsedToFFHeating / 100)
        * (RuralPerElecHeatingUsedforSpaceHeating / 100)
        * (RuralPerResFFSpaceHeatingNGUsed / 100)
    )

    RuralResElecToNGWaterHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (RuralPerResElecUsedToFFHeating / 100)
        * (RuralPerElecHeatingUsedforWaterHeating / 100)
        * (RuralPerResFFWaterHeatingNGUsed / 100)
    )

    RuralResElecToFOKerSpaceHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (RuralPerResElecUsedToFFHeating / 100)
        * (RuralPerElecHeatingUsedforSpaceHeating / 100)
        * (RuralPerResFFSpaceHeatingFOKerUsed / 100)
    )

    RuralResElecToFOKerWaterHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (RuralPerResElecUsedToFFHeating / 100)
        * (RuralPerElecHeatingUsedforWaterHeating / 100)
        * (RuralPerResFFWaterHeatingFOKerUsed / 100)
    )

    RuralResElecToLPGSpaceHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (RuralPerResElecUsedToFFHeating / 100)
        * (RuralPerElecHeatingUsedforSpaceHeating / 100)
        * (RuralPerResFFSpaceHeatingLPGUsed / 100)
    )

    RuralResElecToLPGWaterHeatingBTUUsed = (
        RuralResElecBTUUsed
        * (RuralPerResElecUsedToFFHeating / 100)
        * (RuralPerElecHeatingUsedforWaterHeating / 100)
        * (RuralPerResFFWaterHeatingLPGUsed / 100)
    )

    # Determine whether fossil fuels (and all uses) are switched to electricity or if electricity
    # heating uses are switched to fossil fuel heating uses
    if RuralPerChangedFossilFuelUsed >= 0:
        RuralResElecBTU = (
            (RuralResElecSpaceHeatingBTUUsed / (PerEnergyToUseResElecSpaceHeating / 100))
            + (RuralResElecWaterHeatingBTUUsed / (PerEnergyToUseResElecWaterHeating / 100))
            + (RuralResElecOtherBTUUsed / (PerEnergyToUseResElecOther / 100))
            + (
                (
                    RuralResNGSpaceHeatingToElecBTUUsed
                    + RuralResFOKerSpaceHeatingToElecBTUUsed
                    + RuralResLPGSpaceHeatingToElecBTUUsed
                )
                / (PerEnergyToUseResElecSpaceHeatingSwitch / 100)
            )
            + (
                (
                    RuralResNGWaterHeatingToElecBTUUsed
                    + RuralResFOKerWaterHeatingToElecBTUUsed
                    + RuralResLPGWaterHeatingToElecBTUUsed
                )
                / (PerEnergyToUseResElecWaterHeatingSwitch / 100)
            )
            + (
                (
                    RuralResNGOtherToElecBTUUsed
                    + RuralResFOKerOtherToElecBTUUsed
                    + RuralResLPGOtherToElecBTUUsed
                )
                / (PerEnergyToUseResElecOther / 100)
            )
        )

        RuralResNGBTU = (
            (
                (RuralResNGSpaceHeatingBTUUsed - RuralResNGSpaceHeatingToElecBTUUsed)
                / (PerEnergyToUseResNGSpaceHeating / 100)
            )
            + (
                (RuralResNGWaterHeatingBTUUsed - RuralResNGWaterHeatingToElecBTUUsed)
                / (PerEnergyToUseResNGWaterHeating / 100)
            )
            + (
                (RuralResNGOtherBTUUsed - RuralResNGOtherToElecBTUUsed)
                / (PerEnergyToUseResNGOther / 100)
            )
        )

        RuralResFOKerBTU = (
            (
                (RuralResFOKerSpaceHeatingBTUUsed - RuralResFOKerSpaceHeatingToElecBTUUsed)
                / (PerEnergyToUseResFOKerSpaceHeating / 100)
            )
            + (
                (RuralResFOKerWaterHeatingBTUUsed - RuralResFOKerWaterHeatingToElecBTUUsed)
                / (PerEnergyToUseResFOKerWaterHeating / 100)
            )
            + (
                (RuralResFOKerOtherBTUUsed - RuralResFOKerOtherToElecBTUUsed)
                / (PerEnergyToUseResFOKerOther / 100)
            )
        )

        RuralResLPGBTU = (
            (
                (RuralResLPGSpaceHeatingBTUUsed - RuralResLPGSpaceHeatingToElecBTUUsed)
                / (PerEnergyToUseResLPGSpaceHeating / 100)
            )
            + (
                (RuralResLPGWaterHeatingBTUUsed - RuralResLPGWaterHeatingToElecBTUUsed)
                / (PerEnergyToUseResLPGWaterHeating / 100)
            )
            + (
                (RuralResLPGOtherBTUUsed - RuralResLPGOtherToElecBTUUsed)
                / (PerEnergyToUseResLPGOther / 100)
            )
        )
    else:
        RuralResElecBTU = (
            (RuralResElecOtherBTUUsed / (PerEnergyToUseResElecOther / 100))
            + (
                (
                    RuralResElecSpaceHeatingBTUUsed
                    - (
                        RuralResElecToNGSpaceHeatingBTUUsed
                        + RuralResElecToFOKerSpaceHeatingBTUUsed
                        + RuralResElecToLPGSpaceHeatingBTUUsed
                    )
                )
                / (PerEnergyToUseResElecSpaceHeating / 100)
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
                / (PerEnergyToUseResElecWaterHeating / 100)
            )
        )

        RuralResNGBTU = (
            (RuralResNGOtherBTUUsed / (PerEnergyToUseResNGOther / 100))
            + (
                (RuralResNGSpaceHeatingBTUUsed + RuralResElecToNGSpaceHeatingBTUUsed)
                / (PerEnergyToUseResNGSpaceHeating / 100)
            )
            + (
                (RuralResNGWaterHeatingBTUUsed + RuralResElecToNGWaterHeatingBTUUsed)
                / (PerEnergyToUseResNGWaterHeating / 100)
            )
        )

        RuralResFOKerBTU = (
            (RuralResFOKerOtherBTUUsed / (PerEnergyToUseResFOKerOther / 100))
            + (
                (RuralResFOKerSpaceHeatingBTUUsed + RuralResElecToFOKerSpaceHeatingBTUUsed)
                / (PerEnergyToUseResFOKerSpaceHeating / 100)
            )
            + (
                (RuralResFOKerWaterHeatingBTUUsed + RuralResElecToFOKerWaterHeatingBTUUsed)
                / (PerEnergyToUseResFOKerWaterHeating / 100)
            )
        )

        RuralResLPGBTU = (
            (RuralResLPGOtherBTUUsed / (PerEnergyToUseResLPGOther / 100))
            + (
                (RuralResLPGSpaceHeatingBTUUsed + RuralResElecToLPGSpaceHeatingBTUUsed)
                / (PerEnergyToUseResLPGSpaceHeating / 100)
            )
            + (
                (RuralResLPGWaterHeatingBTUUsed + RuralResElecToLPGWaterHeatingBTUUsed)
                / (PerEnergyToUseResLPGWaterHeating / 100)
            )
        )

    # Calculate GHG emissions
    ResElecGHG = (
        (UrbanResElecBTU + SuburbanResElecBTU + RuralResElecBTU)
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
        * (1 - PerCombCapture / 100)
    )

    ResNGBTU = UrbanResNGBTU + SuburbanResNGBTU + RuralResNGBTU
    ResNGGHG = (
        ResNGBTU
        * (1 / BTU_CCF_AVG)
        * (1 + PerCapResEnergyUse / 100)
        * MCFperCCF
        * CO2_LB_KCF_NG
        * MMT_LB
    )
    ResFOKerGHG = (
        (UrbanResFOKerBTU + SuburbanResFOKerBTU + RuralResFOKerBTU)
        * (1 / BTU_GAL_FOK)
        * (1 + PerCapResEnergyUse / 100)
        * (CO2_MMT_KB_FOK * KB_G)
    )

    ResLPGGHG = (
        (UrbanResLPGBTU + SuburbanResLPGBTU + RuralResLPGBTU)
        * (1 / BTU_GAL_LPG)
        * (1 + PerCapResEnergyUse / 100)
        * (CO2_MMT_KB_LPG * KB_G)
    )

    ResGHG = ResElecGHG + ResNGGHG + ResFOKerGHG + ResLPGGHG

    return ResGHG, ResNGBTU


def calc_ci_ghg(
    ComIndPerElectrification,
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    PerCombCapture,
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
        * (1 - PerCombCapture / 100)
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
    PerCombCapture,
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
    ) * (1 - PerCombCapture / 100)

    return highway_ghg


def calc_aviation_ghg(pop_factor, PerAviation):
    return GHG_AVIATION * (1 + pop_factor / 100) * (1 + PerAviation / 100)


def calc_transit_ghg(
    grid_coal,
    grid_ng,
    grid_oil,
    grid_other_ff,
    PerCombCapture,
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
        * (1 - PerCombCapture / 100)
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
    PerCombCapture,
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
        * (1 - PerCombCapture / 100)
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
        * (1 - PerCombCapture / 100)
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
        * (1 - PerCombCapture / 100)
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
        * (1 - PerCombCapture / 100)
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
    PerCapResEnergyUse,
    PerComIndEnergyUse,
    PerForestCoverage,
    PerIP,
    PerUrbanTreeCoverage,
    PerWaste,
    PerWasteWater,
    pop_factor,
    RuralPerResElectrification,
    SuburbanPerResElectrification,
    UrbanPerResElectrification,
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
        PerCapResEnergyUse,
        pop_factor,
        RuralPerResElectrification,
        SuburbanPerResElectrification,
        UrbanPerResElectrification,
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
        * MillionCFperCF
        * (MMTCO2ePerMillionCFNG_CH4 + MMTCO2ePerMillionCFNG_CO2)
    )

    LULUCFGHG = GHG_URBAN_TREES * (1 + PerUrbanTreeCoverage / 100) + (
        GHG_FORESTS + GHG_FOREST_CHANGE
    ) * (1 + PerForestCoverage / 100)

    return AgricultureGHG + SolidWasteGHG + WasteWaterGHG + IndProcGHG + NGSystemsGHG + LULUCFGHG


def grid_text(
    grid_coal,
    grid_oil,
    grid_ng,
    grid_nuclear,
    grid_solar,
    grid_wind,
    grid_bio,
    grid_hydro,
    grid_geo,
    grid_other_ff,
):
    """Create text to give user current sum of grid mix choices."""
    t = sum(
        [
            grid_coal,
            grid_oil,
            grid_ng,
            grid_nuclear,
            grid_solar,
            grid_wind,
            grid_bio,
            grid_hydro,
            grid_geo,
            grid_other_ff,
        ]
    )

    return f"Input percentages. Make sure the grid mix sums to 100%. The current sum is {t:.1f}%."


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
        "PerCapResEnergyUse": PerCapResEnergyUseSlider.value,
        "UrbanPerResElectrification": UrbanPerResElectrificationSlider.value,
        "SuburbanPerResElectrification": SuburbanPerResElectrificationSlider.value,
        "RuralPerResElectrification": RuralPerResElectrificationSlider.value,
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
        "PerCombCapture": PerCombCaptureSlider.value,
        "AirCapture": AirCaptureSlider.value,  # TK, possibly
    }

    source.data = wrangle_data_for_bar_chart(user_inputs)
    source2.data = wrangle_data_for_stacked_chart(user_inputs)

    # Update source data for pie chart
    source3.data = {
        "FuelType": [
            "Coal",
            "Oil",
            "Natural Gas",
            "Nuclear",
            "Solar",
            "Wind",
            "Biomass",
            "Hydropower",
            "Geothermal",
            "Other Fossil Fuel",
        ],
        "Percentage": [
            grid_coal,
            grid_oil,
            grid_ng,
            grid_nuclear,
            grid_solar,
            grid_wind,
            grid_bio,
            grid_hydro,
            grid_geo,
            grid_other_ff,
        ],
        "angle": [
            (
                grid_coal
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
            (
                grid_oil
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
            (
                grid_ng
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
            (
                grid_nuclear
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
            (
                grid_solar
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
            (
                grid_wind
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
            (
                grid_bio
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
            (
                grid_hydro
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
            (
                grid_geo
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
            (
                grid_other_ff
                / (
                    grid_bio
                    + grid_coal
                    + grid_hydro
                    + grid_ng
                    + grid_nuclear
                    + grid_oil
                    + grid_other_ff
                    + grid_solar
                    + grid_wind
                    + grid_geo
                )
                * (2 * pi)
            ),
        ],
        "color": Spectral10,
    }
    # Update the paragraph widget text based on the new text inputs
    if (
        round(
            (
                grid_coal
                + grid_oil
                + grid_ng
                + grid_nuclear
                + grid_solar
                + grid_wind
                + grid_bio
                + grid_hydro
                + grid_geo
                + grid_other_ff
            ),
            2,
        )
        > 100
    ):
        GridTextParagraph.text = grid_text(
            grid_coal,
            grid_oil,
            grid_ng,
            grid_nuclear,
            grid_solar,
            grid_wind,
            grid_bio,
            grid_hydro,
            grid_geo,
            grid_other_ff,
        )
        GridTextParagraph.style = {"color": "red"}
    elif (
        round(
            (
                grid_coal
                + grid_oil
                + grid_ng
                + grid_nuclear
                + grid_solar
                + grid_wind
                + grid_bio
                + grid_hydro
                + grid_other_ff
            ),
            2,
        )
        < 100
    ):
        GridTextParagraph.text = grid_text(
            grid_coal,
            grid_oil,
            grid_ng,
            grid_nuclear,
            grid_solar,
            grid_wind,
            grid_bio,
            grid_hydro,
            grid_geo,
            grid_other_ff,
        )
        GridTextParagraph.style = {"color": "orange"}
    else:
        GridTextParagraph.text = grid_text(
            grid_coal,
            grid_oil,
            grid_ng,
            grid_nuclear,
            grid_solar,
            grid_wind,
            grid_bio,
            grid_hydro,
            grid_geo,
            grid_other_ff,
        )
        GridTextParagraph.style = {"color": "black"}


# Create initial plots


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
                user_inputs["PerCapResEnergyUse"],
                user_inputs["pop_factor"],
                user_inputs["RuralPerResElectrification"],
                user_inputs["SuburbanPerResElectrification"],
                user_inputs["UrbanPerResElectrification"],
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
                user_inputs["PerCombCapture"],
                user_inputs["PerComIndEnergyUse"],
            ),
            calc_highway_ghg(
                user_inputs["grid_coal"],
                user_inputs["grid_ng"],
                user_inputs["grid_oil"],
                user_inputs["grid_other_ff"],
                user_inputs["PerCombCapture"],
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
                user_inputs["PerCombCapture"],
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
                user_inputs["PerCombCapture"],
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
                user_inputs["PerCapResEnergyUse"],
                user_inputs["PerComIndEnergyUse"],
                user_inputs["PerForestCoverage"],
                user_inputs["PerIP"],
                user_inputs["PerUrbanTreeCoverage"],
                user_inputs["PerWaste"],
                user_inputs["PerWasteWater"],
                user_inputs["pop_factor"],
                user_inputs["RuralPerResElectrification"],
                user_inputs["SuburbanPerResElectrification"],
                user_inputs["UrbanPerResElectrification"],
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
                user_inputs["PerCapResEnergyUse"],
                user_inputs["pop_factor"],
                user_inputs["RuralPerResElectrification"],
                user_inputs["SuburbanPerResElectrification"],
                user_inputs["UrbanPerResElectrification"],
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
                user_inputs["PerCombCapture"],
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
                user_inputs["PerCombCapture"],
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
                user_inputs["PerCombCapture"],
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
                user_inputs["PerCombCapture"],
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
                user_inputs["PerCapResEnergyUse"],
                user_inputs["PerComIndEnergyUse"],
                user_inputs["PerForestCoverage"],
                user_inputs["PerIP"],
                user_inputs["PerUrbanTreeCoverage"],
                user_inputs["PerWaste"],
                user_inputs["PerWasteWater"],
                user_inputs["pop_factor"],
                user_inputs["RuralPerResElectrification"],
                user_inputs["SuburbanPerResElectrification"],
                user_inputs["UrbanPerResElectrification"],
                user_inputs["urban_pop_percent"],
            ),
        ],
    }
    return data


bar_chart_data = wrangle_data_for_bar_chart(user_inputs)
source = ColumnDataSource(data=bar_chart_data)

# Configure vertical bar plot
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

stacked_chart_data = wrangle_data_for_stacked_chart(user_inputs)
source2 = ColumnDataSource(data=stacked_chart_data)

# Configure stacked bar plot
stacked_bar_chart = figure(
    x_range=stacked_chart_data["Year"],
    y_range=(0, 100),
    plot_height=500,
    plot_width=500,
    y_axis_label="Million Metric Tons of CO2e",
    title="Greenhouse Gas Emissions in Greater Philadelphia",
)

stacked_bar_chart.vbar_stack(
    sectors, x="Year", width=0.4, color=Viridis7, source=source2, legend_label=sectors
)

stacked_bar_chart.legend[
    0
].items.reverse()  # Reverses legend items to match order of occurence in stack
stacked_bar_chart_legend = stacked_bar_chart.legend[0]
stacked_bar_chart.add_layout(stacked_bar_chart_legend, "right")


def wrangle_data_for_pie_chart(user_inputs):
    # Configure data and plot for pie chart
    x = {
        "Coal": grid_coal,
        "Oil": grid_oil,
        "Natural Gas": grid_ng,
        "Nuclear": grid_nuclear,
        "Solar": grid_solar,
        "Wind": grid_wind,
        "Biomass": grid_bio,
        "Hydropower": grid_hydro,
        "Geothermal": grid_geo,
        "Other Fossil Fuel": grid_other_ff,
    }

    data = pd.Series(x).reset_index(name="Percentage").rename(columns={"index": "FuelType"})
    data["angle"] = data["Percentage"] / data["Percentage"].sum() * 2 * pi
    data["color"] = Spectral10

    return data


data3 = wrangle_data_for_pie_chart(user_inputs)
source3 = ColumnDataSource(data=data3)

electric_grid_pie_chart = figure(
    title="Electricity Grid Resource Mix",
    toolbar_location=None,
    plot_height=400,
    plot_width=750,
    tools="hover",
    tooltips="@FuelType: @Percentage",
    x_range=(-0.5, 1.0),
)

electric_grid_pie_chart.wedge(
    x=0,
    y=1,
    radius=0.3,
    start_angle=cumsum("angle", include_zero=True),
    end_angle=cumsum("angle"),
    line_color="white",
    fill_color="color",
    legend_field="FuelType",
    source=source3,
)

electric_grid_pie_chart.axis.axis_label = None
electric_grid_pie_chart.axis.visible = False
electric_grid_pie_chart.grid.grid_line_color = None

# Initializes paragraph widget based on calculating grid mix and assigning it to text within the paragraph to be updated
GridTextParagraph = Paragraph(
    text=grid_text(
        grid_coal,
        grid_oil,
        grid_ng,
        grid_nuclear,
        grid_solar,
        grid_wind,
        grid_bio,
        grid_hydro,
        grid_geo,
        grid_other_ff,
    ),
    style={"color": "black"},
)

# Creates Widgets

# Grid Inputs
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

# Population Inputs
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

# Stationary Energy Inputs - Residential
PerCapResEnergyUseSlider = Slider(
    start=-100, end=100, value=0, step=10, title="% Change in Per Capita Residential Energy Usage",
)
PerCapResEnergyUseSlider.on_change("value", callback)

UrbanPerResElectrificationSlider = Slider(
    start=UrbanMinPerResElectrification,
    end=100,
    value=UrbanPerResElecUsed,
    step=1,
    title="% Electrification of Residential End Uses in Urban Areas",
)
UrbanPerResElectrificationSlider.on_change("value", callback)

SuburbanPerResElectrificationSlider = Slider(
    start=SuburbanMinPerResElectrification,
    end=100,
    value=SuburbanPerResElecUsed,
    step=1,
    title="% Electrification of Residential End Uses in Suburban Areas",
)
SuburbanPerResElectrificationSlider.on_change("value", callback)

RuralPerResElectrificationSlider = Slider(
    start=RuralMinPerResElectrification,
    end=100,
    value=RuralPerResElecUsed,
    step=1,
    title="% Electrification of Residential End Uses in Rural Areas",
)
RuralPerResElectrificationSlider.on_change("value", callback)

# Stationary Energy Inputs - Commercial and Industrial
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

# Mobile Energy Inputs - Highway
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

# Mobile Energy Inputs - Rail Transit
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

# Mobile Energy Inputs - Aviation
PerAviationSlider = Slider(start=-100, end=100, value=0, step=1, title="% Change in Air Travel")
PerAviationSlider.on_change("value", callback)

# Mobile Energy Inputs - Freight Rail
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

# Mobile Energy Inputs - Inter-city Rail
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

# Mobile Energy Inputs - Marine and Port
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

# Mobile Energy Inputs - Off-road
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

# Non-Energy Inputs
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

# Carbon Capture Inputs
PerCombCaptureSlider = Slider(
    start=0,
    end=100,
    value=0,
    step=1,
    title="% Carbon Captured at Combustion Site for Electricity Generation",
)
PerCombCaptureSlider.on_change("value", callback)

AirCaptureSlider = Slider(start=0, end=100, value=0, step=1, title="MMTCO2e Captured from the Air")
AirCaptureSlider.on_change("value", callback)


# widgets
widgetPop = Column(
    pop_factorSlider,
    urban_pop_percentTextInput,
    suburban_pop_percentTextInput,
    rural_pop_percentTextInput,
)
widgetGrid = Column(
    GridTextParagraph,
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
widgetResidential = Column(
    PerCapResEnergyUseSlider,
    UrbanPerResElectrificationSlider,
    SuburbanPerResElectrificationSlider,
    RuralPerResElectrificationSlider,
)
widgetCommInd = Column(PerComIndEnergyUseSlider, ComIndPerElectrificationSlider)
widgetMobileHighway = Column(VMTperCapSlider, PerEVMTSlider, RegionalFleetMPGSlider)
widgetMobileRailTrans = Column(
    PerTransRailRidershipSlider,
    TransRailUrbanPerElecMotionSlider,
    TransRailSuburbanPerElecMotionSlider,
    TransRailRuralPerElecMotionSlider,
)
widgetMobileOther = Column(
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
widgetNonEnergy = Column(
    PerAgSlider,
    PerWasteSlider,
    PerWasteWaterSlider,
    PerIPSlider,
    PerUrbanTreeCoverageSlider,
    PerForestCoverageSlider,
)
widgetCarbonCapture = Column(PerCombCaptureSlider, AirCaptureSlider)

all_widgets = [
    widgetPop,
    widgetGrid,
    widgetResidential,
    widgetCommInd,
    widgetMobileHighway,
    widgetMobileRailTrans,
    widgetMobileOther,
    widgetNonEnergy,
    widgetCarbonCapture,
]
doc = curdoc()
doc.add_root(column(all_widgets))
doc.add_root(column(bar_chart, stacked_bar_chart, electric_grid_pie_chart))
