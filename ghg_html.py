from math import pi
from statistics import mean

import numpy as np
import pandas as pd

from bokeh.layouts import row, column
from bokeh.models import Slider, Column, ColumnDataSource, TextInput, Paragraph
from bokeh.palettes import Viridis7, Spectral10
from bokeh.plotting import figure, curdoc
from bokeh.transform import dodge, cumsum


# Implied National Emissions rate from NG Transmission, Storage, Distribution (fugitive emissions in MMTCO2e/million CF)
MMTCO2ePerMillionCFNG_CH4 = 0.00000169
MMTCO2ePerMillionCFNG_CO2 = 0.000000004

# 2015 GHG Inventory Total Emissions (MMTCO2E)
Residential2015 = 15.37
ComInd2015 = 27.96  # non-residential/commercial & industrial
MobHighway2015 = 17.94
MobTransit2015 = 0.18
MobAviation2015 = 3.90
MobOther2015 = 1.12  # includes freight & intercity rail, marine & port-related, off-road vehicles and equipment
Ag2015 = 0.41  # agriculture
Waste2015 = 2.01  # landfills
WasteWater2015 = 0.49
IP2015 = 5.52  # Includes Hydrogen production, iron & steel production, industrial wastewater treatment, ODS substitutes, and petroleum refining
UrbanTrees2015 = -1.025
ForestSequestration2015 = -1.109
ForestLossGain2015 = 0.380
ResNGCon2015 = 115884601.50 / 1000  # NG Consumpton 2015 (million CF)
ComIndNGCon2015 = 139139475 / 1000  # NG Consumpton 2015 (million CF)
NonEnergy2015 = (
    Ag2015
    + Waste2015
    + WasteWater2015
    + IP2015
    + UrbanTrees2015
    + ForestSequestration2015
    + ForestLossGain2015
    + (ResNGCon2015 + ComIndNGCon2015) * (MMTCO2ePerMillionCFNG_CH4 + MMTCO2ePerMillionCFNG_CO2)
)

# Demographics
UrbanPop2015 = 1691830

SuburbanPop2015 = 3693658

RuralPop2015 = 332445

Population = UrbanPop2015 + SuburbanPop2015 + RuralPop2015

PopFactor = 0
PerUrbanPop = UrbanPop2015 / Population * 100
PerSuburbanPop = SuburbanPop2015 / Population * 100
PerRuralPop = RuralPop2015 / Population * 100

# Average Emissions pr MWh of fossil fuels from eGRID 2014/2016 for RFCE (Future reference - should we pull plant-level data for this?)
LB_CO2e_MWh_Coal = (2169.484351 + 2225.525) / 2
LB_CO2e_MWh_Oil = (1600.098812 + 1341.468) / 2
LB_CO2e_MWh_NG = (929.651872 + 897.037) / 2
LB_CO2e_MWh_OtherFos = (1488.036692 + 1334.201) / 2

# Percent of carbon emissions from combustion of fossil fuels for electricity that are captured and stored
PerCombCapture = 0

# Electricity Mix from 2015 inventory
PerCoal = 20.47
PerOil = 0.47
PerNG = 34.38
PerOtherFos = 0.46
PerBio = 1.59
PerHydro = 1.06
PerNuclear = 40.10
PerWind = 1.16
PerSolar = 0.30
PerGeo = 0.00
GridLoss = 0.047287092

MMTCO2e_ThBarrel_FOKer = 0.000428929
MMTCO2e_ThBarrel_LPG = 0.000219762
LB_CO2e_MCF_NG = 123.0744706

MMTperLB = 0.00000000045359
ThBarrelperGallon = 1 / 42000
MCFperCCF = 0.1
CFperCCF = 100
MillionCFperCF = 0.000001
GalperBarrel = 42
kWhperMWh = 1000
BTUPerBBtu = 1000000000
MMTperMT = 0.000001

# Btu Conversions
BTUperkWh = 3412
BTUperMWh = BTUperkWh * kWhperMWh
BTUperCFPA = 1048
BTUperCFNJ = 1050
BTUperCFavg = mean([BTUperCFPA, BTUperCFNJ])
BTUperCCF = BTUperCFavg * CFperCCF
BTUperBarrelFOKer = 5770000
BTUperGallonFOKer = BTUperBarrelFOKer * (1 / GalperBarrel)
BTUperBarrelLPG = 3540000
BTUperGallonLPG = BTUperBarrelLPG * (1 / GalperBarrel)

# MTCO2e per BBtu - From ComInd 2015
MTCO2ePerBBtuNG = 53.20
MTCO2ePerBBtuCoal = 95.13
MTCO2ePerBBtuDFO = 74.39
MTCO2ePerBBtuKer = 73.63
MTCO2ePerBBtuLPG = 65.15
MTCO2ePerBBtuMotGas = 71.60
MTCO2ePerBBtuRFO = 75.35
MTCO2ePerBBtuPetCoke = 102.36
MTCO2ePerBBtuStillGas = 66.96
MTCO2ePerBBtuSpecialNaphthas = 72.62

# Residential Stationary ENERGY
PerCapResEnergyUse = 0

UrbanPerCapElec = 2.41  # MWh/person
SuburbanPerCapElec = 3.17  # MWh/person
RuralPerCapElec = 3.81  # MWh/person

UrbanBTUPerCapElec = UrbanPerCapElec * BTUperMWh  # BTU/Person
SuburbanBTUPerCapElec = SuburbanPerCapElec * BTUperMWh  # BTU/Person
RuralBTUPerCapElec = RuralPerCapElec * BTUperMWh  # BTU/Person

UrbanPerCapNG = 246.04  # CCF/person
SuburbanPerCapNG = 193.00  # CCF/person
RuralPerCapNG = 89.35  # CCF/person

UrbanBTUPerCapNG = UrbanPerCapNG * BTUperCCF  # BTU/Person
SuburbanBTUPerCapNG = SuburbanPerCapNG * BTUperCCF  # BTU/Person
RuralBTUPerCapNG = RuralPerCapNG * BTUperCCF  # BTU/Person

UrbanPerCapFOKer = 14.50  # gallons/person
SuburbanPerCapFOKer = 43.32  # gallons/person
RuralPerCapFOKer = 80.84  # gallons/person

UrbanBTUPerCapFOKer = UrbanPerCapFOKer * BTUperGallonFOKer  # BTU/Person
SuburbanBTUPerCapFOKer = SuburbanPerCapFOKer * BTUperGallonFOKer  # BTU/Person
RuralBTUPerCapFOKer = RuralPerCapFOKer * BTUperGallonFOKer  # BTU/Person

UrbanPerCapLPG = 3.46  # gallons/person
SuburbanPerCapLPG = 8.44  # gallons/person
RuralPerCapLPG = 44.38  # gallons/person

UrbanBTUPerCapLPG = UrbanPerCapLPG * BTUperGallonLPG  # BTU/Person
SuburbanBTUPerCapLPG = SuburbanPerCapLPG * BTUperGallonLPG  # BTU/Person
RuralBTUPerCapLPG = RuralPerCapLPG * BTUperGallonLPG  # BTU/Person

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

TransRailUrbanBTUPerCapElec = TransRailUrbanPerCapElec * BTUperkWh  # BTU/Person
TransRailSuburbanBTUPerCapElec = TransRailSuburbanPerCapElec * BTUperkWh  # BTU/Person
TransRailRuralBTUPerCapElec = TransRailRuralPerCapElec * BTUperkWh  # BTU/Person

TransRailUrbanPerCapDiesel = 0.1995  # gallons/person
TransRailSuburbanPerCapDiesel = 0.1138  # gallons/person
TransRailRuralPerCapDiesel = 0.0368  # gallons/person

TransRailUrbanBTUPerCapDiesel = (
    TransRailUrbanPerCapDiesel * ThBarrelperGallon * TransRailBBtuPerThBarrelDiesel * BTUPerBBtu
)  # BTU/Person
TransRailSuburbanBTUPerCapDiesel = (
    TransRailSuburbanPerCapDiesel * ThBarrelperGallon * TransRailBBtuPerThBarrelDiesel * BTUPerBBtu
)  # BTU/Person
TransRailRuralBTUPerCapDiesel = (
    TransRailRuralPerCapDiesel * ThBarrelperGallon * TransRailBBtuPerThBarrelDiesel * BTUPerBBtu
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

TransRailUrbanPerElectrification = TransRailUrbanPerElecMotion
TransRailSuburbanPerElectrification = TransRailSuburbanPerElecMotion
TransRailRuralPerElectrification = TransRailRuralPerElecMotion

# Mobile-Other GHG Factors

# Freight Rail
PerFreightRail = 0

FreightRailElecBBtu = 0
FreightRailDieselBBtu = 3525.18

FreightRailElecBBtuMotion = FreightRailElecBBtu * PerEnergyToMotionRailElec / 100
FreightRailDieselBBtuMotion = FreightRailDieselBBtu * PerEnergyToMotionRailDiesel / 100
FreightRailBBtuMotion = FreightRailElecBBtuMotion + FreightRailDieselBBtuMotion

FreightRailPerElecMotion = FreightRailElecBBtuMotion / FreightRailBBtuMotion * 100
FreightRailPerElectrification = FreightRailPerElecMotion

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


def CalcResGHG(
    Population,
    PopFactor,
    PerUrbanPop,
    UrbanBTUPerCapUsed,
    PerCapResEnergyUse,
    UrbanPerResElectrification,
    UrbanPerResElecUsed,
    PerUrbanElecBTUPerCapUsedSpaceHeating,
    PerUrbanElecBTUPerCapUsedWaterHeating,
    PerUrbanElecBTUPerCapUsedOther,
    UrbanPerResNGUsed,
    PerUrbanNGBTUPerCapUsedSpaceHeating,
    PerUrbanNGBTUPerCapUsedWaterHeating,
    PerUrbanNGBTUPerCapUsedOther,
    UrbanPerResFOKerUsed,
    PerUrbanFOKerBTUPerCapUsedSpaceHeating,
    PerUrbanFOKerBTUPerCapUsedWaterHeating,
    PerUrbanFOKerBTUPerCapUsedOther,
    UrbanPerResLPGUsed,
    PerUrbanLPGBTUPerCapUsedSpaceHeating,
    PerUrbanLPGBTUPerCapUsedWaterHeating,
    PerUrbanLPGBTUPerCapUsedOther,
    UrbanPerResFFNGUsed,
    UrbanPerResFFFOKerUsed,
    UrbanPerResFFLPGUsed,
    UrbanPerElecHeatingUsedforSpaceHeating,
    UrbanPerResFFSpaceHeatingNGUsed,
    UrbanPerElecHeatingUsedforWaterHeating,
    UrbanPerResFFWaterHeatingNGUsed,
    UrbanPerResFFSpaceHeatingFOKerUsed,
    UrbanPerResFFWaterHeatingFOKerUsed,
    UrbanPerResFFSpaceHeatingLPGUsed,
    UrbanPerResFFWaterHeatingLPGUsed,
    PerEnergyToUseResElecSpaceHeating,
    PerEnergyToUseResElecWaterHeating,
    PerEnergyToUseResElecOther,
    PerEnergyToUseResElecSpaceHeatingSwitch,
    PerEnergyToUseResElecWaterHeatingSwitch,
    PerEnergyToUseResNGSpaceHeating,
    PerEnergyToUseResNGWaterHeating,
    PerEnergyToUseResNGOther,
    PerEnergyToUseResFOKerSpaceHeating,
    PerEnergyToUseResFOKerWaterHeating,
    PerEnergyToUseResFOKerOther,
    PerEnergyToUseResLPGSpaceHeating,
    PerEnergyToUseResLPGWaterHeating,
    PerEnergyToUseResLPGOther,
    SuburbanBTUPerCapUsed,
    SuburbanPerResElectrification,
    SuburbanPerResElecUsed,
    PerSuburbanElecBTUPerCapUsedSpaceHeating,
    PerSuburbanElecBTUPerCapUsedWaterHeating,
    PerSuburbanElecBTUPerCapUsedOther,
    SuburbanPerResNGUsed,
    PerSuburbanNGBTUPerCapUsedSpaceHeating,
    PerSuburbanNGBTUPerCapUsedWaterHeating,
    PerSuburbanNGBTUPerCapUsedOther,
    SuburbanPerResFOKerUsed,
    PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
    PerSuburbanFOKerBTUPerCapUsedWaterHeating,
    PerSuburbanFOKerBTUPerCapUsedOther,
    SuburbanPerResLPGUsed,
    PerSuburbanLPGBTUPerCapUsedSpaceHeating,
    PerSuburbanLPGBTUPerCapUsedWaterHeating,
    PerSuburbanLPGBTUPerCapUsedOther,
    SuburbanPerResFFNGUsed,
    SuburbanPerResFFFOKerUsed,
    SuburbanPerResFFLPGUsed,
    SuburbanPerElecHeatingUsedforSpaceHeating,
    SuburbanPerResFFSpaceHeatingNGUsed,
    SuburbanPerElecHeatingUsedforWaterHeating,
    SuburbanPerResFFWaterHeatingNGUsed,
    SuburbanPerResFFSpaceHeatingFOKerUsed,
    SuburbanPerResFFWaterHeatingFOKerUsed,
    SuburbanPerResFFSpaceHeatingLPGUsed,
    SuburbanPerResFFWaterHeatingLPGUsed,
    RuralBTUPerCapUsed,
    RuralPerResElectrification,
    RuralPerResElecUsed,
    PerRuralElecBTUPerCapUsedSpaceHeating,
    PerRuralElecBTUPerCapUsedWaterHeating,
    PerRuralElecBTUPerCapUsedOther,
    RuralPerResNGUsed,
    PerRuralNGBTUPerCapUsedSpaceHeating,
    PerRuralNGBTUPerCapUsedWaterHeating,
    PerRuralNGBTUPerCapUsedOther,
    RuralPerResFOKerUsed,
    PerRuralFOKerBTUPerCapUsedSpaceHeating,
    PerRuralFOKerBTUPerCapUsedWaterHeating,
    PerRuralFOKerBTUPerCapUsedOther,
    RuralPerResLPGUsed,
    PerRuralLPGBTUPerCapUsedSpaceHeating,
    PerRuralLPGBTUPerCapUsedWaterHeating,
    PerRuralLPGBTUPerCapUsedOther,
    RuralPerResFFNGUsed,
    RuralPerResFFFOKerUsed,
    RuralPerResFFLPGUsed,
    RuralPerElecHeatingUsedforSpaceHeating,
    RuralPerResFFSpaceHeatingNGUsed,
    RuralPerElecHeatingUsedforWaterHeating,
    RuralPerResFFWaterHeatingNGUsed,
    RuralPerResFFSpaceHeatingFOKerUsed,
    RuralPerResFFWaterHeatingFOKerUsed,
    RuralPerResFFSpaceHeatingLPGUsed,
    RuralPerResFFWaterHeatingLPGUsed,
    BTUperMWh,
    GridLoss,
    PerCoal,
    LB_CO2e_MWh_Coal,
    PerOil,
    LB_CO2e_MWh_Oil,
    PerNG,
    LB_CO2e_MWh_NG,
    PerOtherFos,
    LB_CO2e_MWh_OtherFos,
    MMTperLB,
    PerCombCapture,
    BTUperCCF,
    MCFperCCF,
    LB_CO2e_MCF_NG,
    BTUperGallonFOKer,
    MMTCO2e_ThBarrel_FOKer,
    ThBarrelperGallon,
    BTUperGallonLPG,
    MMTCO2e_ThBarrel_LPG,
):
    """
    Residential function uses split of energy per community type by BTU of energy and population
    Begins calculating BTUs of residential energy use from urban areas.
    """
    UrbanResBTUUsed = (
        Population
        * (1 + PopFactor / 100)
        * (PerUrbanPop / 100)
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

    # If statement determines whether fossil fuels (and all uses) are switched to electricity or if electricity heating uses are switched to fossil fuel heating uses
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

    # Begins calculating energy use in suburban areas
    SuburbanResBTUUsed = (
        Population
        * (1 + PopFactor / 100)
        * (PerSuburbanPop / 100)
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

    # If statement determines whether fossil fuels (and all uses) are switched to electricity or if electricity heating uses are switched to fossil fuel heating uses
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

    # Begins calculating BTUs of residential energy use from rural areas
    RuralResBTUUsed = (
        Population
        * (1 + PopFactor / 100)
        * (PerRuralPop / 100)
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

    # If statement determines whether fossil fuels (and all uses) are switched to electricity or if electricity heating uses are switched to fossil fuel heating uses
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

    # Begins calculating GHG emissions
    ResElecGHG = (
        (UrbanResElecBTU + SuburbanResElecBTU + RuralResElecBTU)
        * (1 / BTUperMWh)
        / (1 - GridLoss)
        * (
            (
                (PerCoal / 100 * LB_CO2e_MWh_Coal)
                + (PerOil / 100 * LB_CO2e_MWh_Oil)
                + (PerNG / 100 * LB_CO2e_MWh_NG)
                + (PerOtherFos / 100 * LB_CO2e_MWh_OtherFos)
            )
            * MMTperLB
        )
        * (1 - PerCombCapture / 100)
    )

    ResNGBTU = UrbanResNGBTU + SuburbanResNGBTU + RuralResNGBTU
    ResNGGHG = (
        ResNGBTU
        * (1 / BTUperCCF)
        * (1 + PerCapResEnergyUse / 100)
        * MCFperCCF
        * LB_CO2e_MCF_NG
        * MMTperLB
    )
    ResFOKerGHG = (
        (UrbanResFOKerBTU + SuburbanResFOKerBTU + RuralResFOKerBTU)
        * (1 / BTUperGallonFOKer)
        * (1 + PerCapResEnergyUse / 100)
        * (MMTCO2e_ThBarrel_FOKer * ThBarrelperGallon)
    )

    ResLPGGHG = (
        (UrbanResLPGBTU + SuburbanResLPGBTU + RuralResLPGBTU)
        * (1 / BTUperGallonLPG)
        * (1 + PerCapResEnergyUse / 100)
        * (MMTCO2e_ThBarrel_LPG * ThBarrelperGallon)
    )

    ResGHG = ResElecGHG + ResNGGHG + ResFOKerGHG + ResLPGGHG

    return ResGHG, ResNGBTU


def CalcComIndGHG(
    ComIndPerElectrification,
    ComIndBBtuUsed,
    PerComIndEnergyUse,
    PerEnergyToUseComIndElec,
    BTUPerBBtu,
    BTUperMWh,
    GridLoss,
    PerCoal,
    LB_CO2e_MWh_Coal,
    PerOil,
    LB_CO2e_MWh_Oil,
    PerNG,
    LB_CO2e_MWh_NG,
    PerOtherFos,
    LB_CO2e_MWh_OtherFos,
    MMTperLB,
    PerCombCapture,
    ComIndPerFossilFuelUsed2015,
    ComIndPerFFNGUsed,
    PerEnergyToUseComIndNG,
    MTCO2ePerBBtuNG,
    MMTperMT,
    ComIndPerFFCoalUsed,
    PerEnergyToUseComIndCoal,
    MTCO2ePerBBtuCoal,
    ComIndPerFFDFOUsed,
    PerEnergyToUseComIndDFO,
    MTCO2ePerBBtuDFO,
    ComIndPerFFKerUsed,
    PerEnergyToUseComIndKer,
    MTCO2ePerBBtuKer,
    ComIndPerFFLPGUsed,
    PerEnergyToUseComIndLPG,
    MTCO2ePerBBtuLPG,
    ComIndPerFFMotGasUsed,
    PerEnergyToUseComIndMotGas,
    MTCO2ePerBBtuMotGas,
    ComIndPerFFRFOUsed,
    PerEnergyToUseComIndRFO,
    MTCO2ePerBBtuRFO,
    ComIndPerFFPetCokeUsed,
    PerEnergyToUseComIndPetCoke,
    MTCO2ePerBBtuPetCoke,
    ComIndPerFFStillGasUsed,
    PerEnergyToUseComIndStillGas,
    MTCO2ePerBBtuStillGas,
    ComIndPerSpecialNaphthasUsed,
    PerEnergyToUseComIndSpecialNaphthas,
    MTCO2ePerBBtuSpecialNaphthas,
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
        * BTUPerBBtu
        * (1 / BTUperMWh)
        / (1 - GridLoss)
        * (
            (
                (PerCoal / 100 * LB_CO2e_MWh_Coal)
                + (PerOil / 100 * LB_CO2e_MWh_Oil)
                + (PerNG / 100 * LB_CO2e_MWh_NG)
                + (PerOtherFos / 100 * LB_CO2e_MWh_OtherFos)
            )
            * MMTperLB
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
        * MTCO2ePerBBtuNG
        * MMTperMT
    )

    ComIndCoalGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFCoalUsed / 100)
        / (PerEnergyToUseComIndCoal / 100)
        * MTCO2ePerBBtuCoal
        * MMTperMT
    )

    ComIndDFOGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFDFOUsed / 100)
        / (PerEnergyToUseComIndDFO / 100)
        * MTCO2ePerBBtuDFO
        * MMTperMT
    )

    ComIndKerGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFKerUsed / 100)
        / (PerEnergyToUseComIndKer / 100)
        * MTCO2ePerBBtuKer
        * MMTperMT
    )

    ComIndLPGGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFLPGUsed / 100)
        / (PerEnergyToUseComIndLPG / 100)
        * MTCO2ePerBBtuLPG
        * MMTperMT
    )

    ComIndMotGasGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFMotGasUsed / 100)
        / (PerEnergyToUseComIndMotGas / 100)
        * MTCO2ePerBBtuMotGas
        * MMTperMT
    )

    ComIndRFOGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFRFOUsed / 100)
        / (PerEnergyToUseComIndRFO / 100)
        * MTCO2ePerBBtuRFO
        * MMTperMT
    )

    ComIndPetCokeGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFPetCokeUsed / 100)
        / (PerEnergyToUseComIndPetCoke / 100)
        * MTCO2ePerBBtuPetCoke
        * MMTperMT
    )

    ComIndStillGasGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFStillGasUsed / 100)
        / (PerEnergyToUseComIndStillGas / 100)
        * MTCO2ePerBBtuStillGas
        * MMTperMT
    )

    ComIndSpecialNaphthasGHG = (
        ComIndBBtuUsed
        * (1 + PerComIndEnergyUse / 100)
        * (ComIndPerFossilFuelUsed / 100)
        * (1 + PerChangedFossilFuelUsed)
        * (ComIndPerFFSpecialNaphthasUsed / 100)
        / (PerEnergyToUseComIndSpecialNaphthas / 100)
        * MTCO2ePerBBtuSpecialNaphthas
        * MMTperMT
    )

    ComIndGHG = (
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

    return ComIndGHG


def CalcMobHighwayGHG(
    Population,
    PerUrbanPop,
    PopFactor,
    UrbanVMTperPop,
    PerSuburbanPop,
    SuburbanVMTperPop,
    PerRuralPop,
    RuralVMTperPop,
    VMTperCap,
    PerEVMT,
    RegionalFleetMPG,
    CO2eperGallonGasoline,
    MMTperLB,
    EVEff,
    PerCoal,
    LB_CO2e_MWh_Coal,
    PerOil,
    LB_CO2e_MWh_Oil,
    PerNG,
    LB_CO2e_MWh_NG,
    PerOtherFos,
    LB_CO2e_MWh_OtherFos,
    PerCombCapture,
):
    VMT = (
        (Population * PerUrbanPop / 100 * (1 + PopFactor / 100) * UrbanVMTperPop)
        + (Population * PerSuburbanPop / 100 * (1 + PopFactor / 100) * SuburbanVMTperPop)
        + (Population * PerRuralPop / 100 * (1 + PopFactor / 100) * RuralVMTperPop)
    ) * (1 + VMTperCap / 100)

    EVMT = VMT * PerEVMT / 100

    MobHighwayGHG = (VMT - EVMT) / RegionalFleetMPG * CO2eperGallonGasoline * MMTperLB + (
        EVMT
        * EVEff
        * 0.001
        / (1 - GridLoss)
        * (
            (PerCoal / 100 * LB_CO2e_MWh_Coal)
            + (PerOil / 100 * LB_CO2e_MWh_Oil)
            + (PerNG / 100 * LB_CO2e_MWh_NG)
            + (PerOtherFos / 100 * LB_CO2e_MWh_OtherFos)
        )
        * MMTperLB
    ) * (1 - PerCombCapture / 100)

    return MobHighwayGHG


def CalcMobAviationGHG(MobAviation2015, PopFactor, PerAviation):
    MobAviationGHG = MobAviation2015 * (1 + PopFactor / 100) * (1 + PerAviation / 100)
    return MobAviationGHG


def CalcMobTransitGHG(
    Population,
    PopFactor,
    BTUperMWh,
    GridLoss,
    PerUrbanPop,
    TransRailUrbanPerElectrification,
    TransRailSuburbanPerElectrification,
    TransRailRuralPerElectrification,
    TransRailUrbanBTUPerCapMotion,
    PerSuburbanPop,
    TransRailSuburbanBTUPerCapMotion,
    PerRuralPop,
    TransRailRuralBTUPerCapMotion,
    PerEnergyToMotionRailElec,
    PerCoal,
    LB_CO2e_MWh_Coal,
    PerOil,
    LB_CO2e_MWh_Oil,
    PerNG,
    LB_CO2e_MWh_NG,
    PerOtherFos,
    LB_CO2e_MWh_OtherFos,
    MMTperLB,
    PerCombCapture,
    TransRailMTCO2ePerBBtuDiesel,
    BTUPerBBtu,
    MMTperMT,
    PerEnergyToMotionRailDiesel,
    PerTransRailRidership,
):
    TransRailUrbanPerDieselMotion = 100 - TransRailUrbanPerElectrification
    TransRailSuburbanPerDieselMotion = 100 - TransRailSuburbanPerElectrification
    TransRailRuralPerDieselMotion = 100 - TransRailRuralPerElectrification

    MobTransitElecGHG = (
        Population
        * (1 + PopFactor / 100)
        * (1 / BTUperMWh)
        / (1 - GridLoss)
        * (
            (
                PerUrbanPop
                / 100
                * TransRailUrbanBTUPerCapMotion
                * TransRailUrbanPerElectrification
                / 100
            )
            + (
                PerSuburbanPop
                / 100
                * TransRailSuburbanBTUPerCapMotion
                * TransRailSuburbanPerElectrification
                / 100
            )
            + (
                PerRuralPop
                / 100
                * TransRailRuralBTUPerCapMotion
                * TransRailRuralPerElectrification
                / 100
            )
        )
        / (PerEnergyToMotionRailElec / 100)
        * (
            (
                (PerCoal / 100 * LB_CO2e_MWh_Coal)
                + (PerOil / 100 * LB_CO2e_MWh_Oil)
                + (PerNG / 100 * LB_CO2e_MWh_NG)
                + (PerOtherFos / 100 * LB_CO2e_MWh_OtherFos)
            )
            * MMTperLB
        )
        * (1 - PerCombCapture / 100)
    )

    MobTransitDieselGHG = (
        Population
        * (1 + PopFactor / 100)
        * TransRailMTCO2ePerBBtuDiesel
        * (1 / BTUPerBBtu)
        * MMTperMT
        * (
            (
                PerUrbanPop
                / 100
                * TransRailUrbanBTUPerCapMotion
                * TransRailUrbanPerDieselMotion
                / 100
            )
            + (
                PerSuburbanPop
                / 100
                * TransRailSuburbanBTUPerCapMotion
                * TransRailSuburbanPerDieselMotion
                / 100
            )
            + (
                PerRuralPop
                / 100
                * TransRailRuralBTUPerCapMotion
                * TransRailRuralPerDieselMotion
                / 100
            )
        )
        / (PerEnergyToMotionRailDiesel / 100)
    )

    MobTransitGHG = (MobTransitElecGHG + MobTransitDieselGHG) * (1 + PerTransRailRidership / 100)

    return MobTransitGHG


# includes freight & intercity rail, marine & port-related, off-road vehicles and equipment
def CalcMobOtherGHG(
    FreightRailBBtuMotion,
    FreightRailPerElectrification,
    PerEnergyToMotionRailElec,
    BTUPerBBtu,
    BTUperMWh,
    GridLoss,
    PerCoal,
    LB_CO2e_MWh_Coal,
    PerOil,
    LB_CO2e_MWh_Oil,
    PerNG,
    LB_CO2e_MWh_NG,
    PerOtherFos,
    LB_CO2e_MWh_OtherFos,
    MMTperLB,
    PerCombCapture,
    FreightRailMTCO2ePerBBtuDiesel,
    MMTperMT,
    PerEnergyToMotionRailDiesel,
    PerFreightRail,
    InterCityRailBBtuMotion,
    InterCityRailPerElectrification,
    InterCityRailMTCO2ePerBBtuDiesel,
    PerInterCityRail,
    MarinePortPerElectrification,
    MarinePortPerFossilFuelMotion2015,
    MarinePortBBtuMotion,
    PerEnergyToMotionMarineElec,
    MarinePortPerFFRFOMotion,
    MarinePortMTCO2ePerBBtuRFO,
    PerEnergyToMotionMarineRFO,
    MarinePortPerFFDFOMotion,
    MarinePortMTCO2ePerBBtuDFO,
    PerEnergyToMotionMarineDFO,
    PerMarinePort,
    OffroadPerElectrification,
    OffroadPerFossilFuelMotion2015,
    OffroadBBtuMotion,
    PerEnergyToMotionOffroadElec,
    OffroadPerFFMotGasMotion,
    OffroadMTCO2ePerBBtuMotGas,
    PerEnergyToMotionOffroadMotGas,
    OffroadPerFFDFOMotion,
    OffroadMTCO2ePerBBtuDFO,
    PerEnergyToMotionOffroadDFO,
    OffroadPerFFLPGMotion,
    OffroadMTCO2ePerBBtuLPG,
    PerEnergyToMotionOffroadLPG,
    PerOffroad,
):
    FreightRailPerDieselMotion = 100 - FreightRailPerElectrification

    FreightRailElecGHG = (
        FreightRailBBtuMotion
        * (FreightRailPerElectrification / 100)
        / (PerEnergyToMotionRailElec / 100)
        * BTUPerBBtu
        * (1 / BTUperMWh)
        / (1 - GridLoss)
        * (
            (
                (PerCoal / 100 * LB_CO2e_MWh_Coal)
                + (PerOil / 100 * LB_CO2e_MWh_Oil)
                + (PerNG / 100 * LB_CO2e_MWh_NG)
                + (PerOtherFos / 100 * LB_CO2e_MWh_OtherFos)
            )
            * MMTperLB
        )
        * (1 - PerCombCapture / 100)
    )

    FreightRailDieselGHG = (
        FreightRailBBtuMotion
        * (FreightRailPerDieselMotion / 100)
        * FreightRailMTCO2ePerBBtuDiesel
        * MMTperMT
        / (PerEnergyToMotionRailDiesel / 100)
    )

    FreightRailGHG = (FreightRailElecGHG + FreightRailDieselGHG) * (1 + PerFreightRail / 100)

    InterCityRailPerDieselMotion = 100 - InterCityRailPerElectrification
    InterCityRailElecGHG = (
        InterCityRailBBtuMotion
        * (InterCityRailPerElectrification / 100)
        / (PerEnergyToMotionRailElec / 100)
        * BTUPerBBtu
        * (1 / BTUperMWh)
        / (1 - GridLoss)
        * (
            (
                (PerCoal / 100 * LB_CO2e_MWh_Coal)
                + (PerOil / 100 * LB_CO2e_MWh_Oil)
                + (PerNG / 100 * LB_CO2e_MWh_NG)
                + (PerOtherFos / 100 * LB_CO2e_MWh_OtherFos)
            )
            * MMTperLB
        )
        * (1 - PerCombCapture / 100)
    )

    InterCityRailDieselGHG = (
        InterCityRailBBtuMotion
        * (InterCityRailPerDieselMotion / 100)
        * InterCityRailMTCO2ePerBBtuDiesel
        * MMTperMT
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
        * BTUPerBBtu
        * (1 / BTUperMWh)
        / (1 - GridLoss)
        * (
            (
                (PerCoal / 100 * LB_CO2e_MWh_Coal)
                + (PerOil / 100 * LB_CO2e_MWh_Oil)
                + (PerNG / 100 * LB_CO2e_MWh_NG)
                + (PerOtherFos / 100 * LB_CO2e_MWh_OtherFos)
            )
            * MMTperLB
        )
        * (1 - PerCombCapture / 100)
    )

    MarinePortRFOGHG = (
        MarinePortBBtuMotion
        * (MarinePortPerFFRFOMotion / 100)
        * (MarinePortPerFossilFuelMotion / 100)
        * (1 + MarinePortPerChangedFossilFuelMotion)
        * MarinePortMTCO2ePerBBtuRFO
        * MMTperMT
        / (PerEnergyToMotionMarineRFO / 100)
    )

    MarinePortDFOGHG = (
        MarinePortBBtuMotion
        * (MarinePortPerFFDFOMotion / 100)
        * (MarinePortPerFossilFuelMotion / 100)
        * (1 + MarinePortPerChangedFossilFuelMotion)
        * MarinePortMTCO2ePerBBtuDFO
        * MMTperMT
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
        * BTUPerBBtu
        * (1 / BTUperMWh)
        / (1 - GridLoss)
        * (
            (
                (PerCoal / 100 * LB_CO2e_MWh_Coal)
                + (PerOil / 100 * LB_CO2e_MWh_Oil)
                + (PerNG / 100 * LB_CO2e_MWh_NG)
                + (PerOtherFos / 100 * LB_CO2e_MWh_OtherFos)
            )
            * MMTperLB
        )
        * (1 - PerCombCapture / 100)
    )

    OffroadMotGasGHG = (
        OffroadBBtuMotion
        * (OffroadPerFFMotGasMotion / 100)
        * (OffroadPerFossilFuelMotion / 100)
        * (1 + OffroadPerChangedFossilFuelMotion)
        * OffroadMTCO2ePerBBtuMotGas
        * MMTperMT
        / (PerEnergyToMotionOffroadMotGas / 100)
    )

    OffroadDFOGHG = (
        OffroadBBtuMotion
        * (OffroadPerFFDFOMotion / 100)
        * (OffroadPerFossilFuelMotion / 100)
        * (1 + OffroadPerChangedFossilFuelMotion)
        * OffroadMTCO2ePerBBtuDFO
        * MMTperMT
        / (PerEnergyToMotionOffroadDFO / 100)
    )

    OffroadLPGGHG = (
        OffroadBBtuMotion
        * (OffroadPerFFLPGMotion / 100)
        * (OffroadPerFossilFuelMotion / 100)
        * (1 + OffroadPerChangedFossilFuelMotion)
        * OffroadMTCO2ePerBBtuLPG
        * MMTperMT
        / (PerEnergyToMotionOffroadLPG / 100)
    )

    OffroadGHG = (OffroadElecGHG + OffroadMotGasGHG + OffroadDFOGHG + OffroadLPGGHG) * (
        1 + PerOffroad / 100
    )

    MobOtherGHG = FreightRailGHG + InterCityRailGHG + MarinePortGHG + OffroadGHG

    return MobOtherGHG


def CalcNonEnergyGHG(
    Ag2015,
    PerAg,
    Waste2015,
    PerWaste,
    PopFactor,
    WasteWater2015,
    PerWasteWater,
    IP2015,
    PerIP,
    Population,
    PerUrbanPop,
    UrbanBTUPerCapUsed,
    PerCapResEnergyUse,
    UrbanPerResElectrification,
    UrbanPerResElecUsed,
    PerUrbanElecBTUPerCapUsedSpaceHeating,
    PerUrbanElecBTUPerCapUsedWaterHeating,
    PerUrbanElecBTUPerCapUsedOther,
    UrbanPerResNGUsed,
    PerUrbanNGBTUPerCapUsedSpaceHeating,
    PerUrbanNGBTUPerCapUsedWaterHeating,
    PerUrbanNGBTUPerCapUsedOther,
    UrbanPerResFOKerUsed,
    PerUrbanFOKerBTUPerCapUsedSpaceHeating,
    PerUrbanFOKerBTUPerCapUsedWaterHeating,
    PerUrbanFOKerBTUPerCapUsedOther,
    UrbanPerResLPGUsed,
    PerUrbanLPGBTUPerCapUsedSpaceHeating,
    PerUrbanLPGBTUPerCapUsedWaterHeating,
    PerUrbanLPGBTUPerCapUsedOther,
    UrbanPerResFFNGUsed,
    UrbanPerResFFFOKerUsed,
    UrbanPerResFFLPGUsed,
    UrbanPerElecHeatingUsedforSpaceHeating,
    UrbanPerResFFSpaceHeatingNGUsed,
    UrbanPerElecHeatingUsedforWaterHeating,
    UrbanPerResFFWaterHeatingNGUsed,
    UrbanPerResFFSpaceHeatingFOKerUsed,
    UrbanPerResFFWaterHeatingFOKerUsed,
    UrbanPerResFFSpaceHeatingLPGUsed,
    UrbanPerResFFWaterHeatingLPGUsed,
    PerEnergyToUseResElecSpaceHeating,
    PerEnergyToUseResElecWaterHeating,
    PerEnergyToUseResElecOther,
    PerEnergyToUseResElecSpaceHeatingSwitch,
    PerEnergyToUseResElecWaterHeatingSwitch,
    PerEnergyToUseResNGSpaceHeating,
    PerEnergyToUseResNGWaterHeating,
    PerEnergyToUseResNGOther,
    PerEnergyToUseResFOKerSpaceHeating,
    PerEnergyToUseResFOKerWaterHeating,
    PerEnergyToUseResFOKerOther,
    PerEnergyToUseResLPGSpaceHeating,
    PerEnergyToUseResLPGWaterHeating,
    PerEnergyToUseResLPGOther,
    SuburbanBTUPerCapUsed,
    SuburbanPerResElectrification,
    SuburbanPerResElecUsed,
    PerSuburbanElecBTUPerCapUsedSpaceHeating,
    PerSuburbanElecBTUPerCapUsedWaterHeating,
    PerSuburbanElecBTUPerCapUsedOther,
    SuburbanPerResNGUsed,
    PerSuburbanNGBTUPerCapUsedSpaceHeating,
    PerSuburbanNGBTUPerCapUsedWaterHeating,
    PerSuburbanNGBTUPerCapUsedOther,
    SuburbanPerResFOKerUsed,
    PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
    PerSuburbanFOKerBTUPerCapUsedWaterHeating,
    PerSuburbanFOKerBTUPerCapUsedOther,
    SuburbanPerResLPGUsed,
    PerSuburbanLPGBTUPerCapUsedSpaceHeating,
    PerSuburbanLPGBTUPerCapUsedWaterHeating,
    PerSuburbanLPGBTUPerCapUsedOther,
    SuburbanPerResFFNGUsed,
    SuburbanPerResFFFOKerUsed,
    SuburbanPerResFFLPGUsed,
    SuburbanPerElecHeatingUsedforSpaceHeating,
    SuburbanPerResFFSpaceHeatingNGUsed,
    SuburbanPerElecHeatingUsedforWaterHeating,
    SuburbanPerResFFWaterHeatingNGUsed,
    SuburbanPerResFFSpaceHeatingFOKerUsed,
    SuburbanPerResFFWaterHeatingFOKerUsed,
    SuburbanPerResFFSpaceHeatingLPGUsed,
    SuburbanPerResFFWaterHeatingLPGUsed,
    RuralBTUPerCapUsed,
    RuralPerResElectrification,
    RuralPerResElecUsed,
    PerRuralElecBTUPerCapUsedSpaceHeating,
    PerRuralElecBTUPerCapUsedWaterHeating,
    PerRuralElecBTUPerCapUsedOther,
    RuralPerResNGUsed,
    PerRuralNGBTUPerCapUsedSpaceHeating,
    PerRuralNGBTUPerCapUsedWaterHeating,
    PerRuralNGBTUPerCapUsedOther,
    RuralPerResFOKerUsed,
    PerRuralFOKerBTUPerCapUsedSpaceHeating,
    PerRuralFOKerBTUPerCapUsedWaterHeating,
    PerRuralFOKerBTUPerCapUsedOther,
    RuralPerResLPGUsed,
    PerRuralLPGBTUPerCapUsedSpaceHeating,
    PerRuralLPGBTUPerCapUsedWaterHeating,
    PerRuralLPGBTUPerCapUsedOther,
    RuralPerResFFNGUsed,
    RuralPerResFFFOKerUsed,
    RuralPerResFFLPGUsed,
    RuralPerElecHeatingUsedforSpaceHeating,
    RuralPerResFFSpaceHeatingNGUsed,
    RuralPerElecHeatingUsedforWaterHeating,
    RuralPerResFFWaterHeatingNGUsed,
    RuralPerResFFSpaceHeatingFOKerUsed,
    RuralPerResFFWaterHeatingFOKerUsed,
    RuralPerResFFSpaceHeatingLPGUsed,
    RuralPerResFFWaterHeatingLPGUsed,
    BTUperMWh,
    GridLoss,
    PerCoal,
    LB_CO2e_MWh_Coal,
    PerOil,
    LB_CO2e_MWh_Oil,
    PerNG,
    LB_CO2e_MWh_NG,
    PerOtherFos,
    LB_CO2e_MWh_OtherFos,
    MMTperLB,
    PerCombCapture,
    BTUperCCF,
    MCFperCCF,
    LB_CO2e_MCF_NG,
    BTUperGallonFOKer,
    MMTCO2e_ThBarrel_FOKer,
    ThBarrelperGallon,
    BTUperGallonLPG,
    MMTCO2e_ThBarrel_LPG,
    ComIndPerElectrification,
    ComIndPerFossilFuelUsed2015,
    ComIndBBtuUsed,
    PerComIndEnergyUse,
    ComIndPerFFNGUsed,
    PerEnergyToUseComIndNG,
    BTUPerBBtu,
    CFperCCF,
    MillionCFperCF,
    MMTCO2ePerMillionCFNG_CH4,
    MMTCO2ePerMillionCFNG_CO2,
    UrbanTrees2015,
    PerUrbanTreeCoverage,
    ForestSequestration2015,
    ForestLossGain2015,
    PerForestCoverage,
):
    AgricultureGHG = Ag2015 * (1 + PerAg / 100)

    SolidWasteGHG = Waste2015 * (1 + PerWaste / 100) * (1 + PopFactor / 100)

    WasteWaterGHG = WasteWater2015 * (1 + PerWasteWater / 100) * (1 + PopFactor / 100)

    IndProcGHG = IP2015 * (1 + PerIP / 100)

    ResNGConsumption = CalcResGHG(
        Population,
        PopFactor,
        PerUrbanPop,
        UrbanBTUPerCapUsed,
        PerCapResEnergyUse,
        UrbanPerResElectrification,
        UrbanPerResElecUsed,
        PerUrbanElecBTUPerCapUsedSpaceHeating,
        PerUrbanElecBTUPerCapUsedWaterHeating,
        PerUrbanElecBTUPerCapUsedOther,
        UrbanPerResNGUsed,
        PerUrbanNGBTUPerCapUsedSpaceHeating,
        PerUrbanNGBTUPerCapUsedWaterHeating,
        PerUrbanNGBTUPerCapUsedOther,
        UrbanPerResFOKerUsed,
        PerUrbanFOKerBTUPerCapUsedSpaceHeating,
        PerUrbanFOKerBTUPerCapUsedWaterHeating,
        PerUrbanFOKerBTUPerCapUsedOther,
        UrbanPerResLPGUsed,
        PerUrbanLPGBTUPerCapUsedSpaceHeating,
        PerUrbanLPGBTUPerCapUsedWaterHeating,
        PerUrbanLPGBTUPerCapUsedOther,
        UrbanPerResFFNGUsed,
        UrbanPerResFFFOKerUsed,
        UrbanPerResFFLPGUsed,
        UrbanPerElecHeatingUsedforSpaceHeating,
        UrbanPerResFFSpaceHeatingNGUsed,
        UrbanPerElecHeatingUsedforWaterHeating,
        UrbanPerResFFWaterHeatingNGUsed,
        UrbanPerResFFSpaceHeatingFOKerUsed,
        UrbanPerResFFWaterHeatingFOKerUsed,
        UrbanPerResFFSpaceHeatingLPGUsed,
        UrbanPerResFFWaterHeatingLPGUsed,
        PerEnergyToUseResElecSpaceHeating,
        PerEnergyToUseResElecWaterHeating,
        PerEnergyToUseResElecOther,
        PerEnergyToUseResElecSpaceHeatingSwitch,
        PerEnergyToUseResElecWaterHeatingSwitch,
        PerEnergyToUseResNGSpaceHeating,
        PerEnergyToUseResNGWaterHeating,
        PerEnergyToUseResNGOther,
        PerEnergyToUseResFOKerSpaceHeating,
        PerEnergyToUseResFOKerWaterHeating,
        PerEnergyToUseResFOKerOther,
        PerEnergyToUseResLPGSpaceHeating,
        PerEnergyToUseResLPGWaterHeating,
        PerEnergyToUseResLPGOther,
        SuburbanBTUPerCapUsed,
        SuburbanPerResElectrification,
        SuburbanPerResElecUsed,
        PerSuburbanElecBTUPerCapUsedSpaceHeating,
        PerSuburbanElecBTUPerCapUsedWaterHeating,
        PerSuburbanElecBTUPerCapUsedOther,
        SuburbanPerResNGUsed,
        PerSuburbanNGBTUPerCapUsedSpaceHeating,
        PerSuburbanNGBTUPerCapUsedWaterHeating,
        PerSuburbanNGBTUPerCapUsedOther,
        SuburbanPerResFOKerUsed,
        PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
        PerSuburbanFOKerBTUPerCapUsedWaterHeating,
        PerSuburbanFOKerBTUPerCapUsedOther,
        SuburbanPerResLPGUsed,
        PerSuburbanLPGBTUPerCapUsedSpaceHeating,
        PerSuburbanLPGBTUPerCapUsedWaterHeating,
        PerSuburbanLPGBTUPerCapUsedOther,
        SuburbanPerResFFNGUsed,
        SuburbanPerResFFFOKerUsed,
        SuburbanPerResFFLPGUsed,
        SuburbanPerElecHeatingUsedforSpaceHeating,
        SuburbanPerResFFSpaceHeatingNGUsed,
        SuburbanPerElecHeatingUsedforWaterHeating,
        SuburbanPerResFFWaterHeatingNGUsed,
        SuburbanPerResFFSpaceHeatingFOKerUsed,
        SuburbanPerResFFWaterHeatingFOKerUsed,
        SuburbanPerResFFSpaceHeatingLPGUsed,
        SuburbanPerResFFWaterHeatingLPGUsed,
        RuralBTUPerCapUsed,
        RuralPerResElectrification,
        RuralPerResElecUsed,
        PerRuralElecBTUPerCapUsedSpaceHeating,
        PerRuralElecBTUPerCapUsedWaterHeating,
        PerRuralElecBTUPerCapUsedOther,
        RuralPerResNGUsed,
        PerRuralNGBTUPerCapUsedSpaceHeating,
        PerRuralNGBTUPerCapUsedWaterHeating,
        PerRuralNGBTUPerCapUsedOther,
        RuralPerResFOKerUsed,
        PerRuralFOKerBTUPerCapUsedSpaceHeating,
        PerRuralFOKerBTUPerCapUsedWaterHeating,
        PerRuralFOKerBTUPerCapUsedOther,
        RuralPerResLPGUsed,
        PerRuralLPGBTUPerCapUsedSpaceHeating,
        PerRuralLPGBTUPerCapUsedWaterHeating,
        PerRuralLPGBTUPerCapUsedOther,
        RuralPerResFFNGUsed,
        RuralPerResFFFOKerUsed,
        RuralPerResFFLPGUsed,
        RuralPerElecHeatingUsedforSpaceHeating,
        RuralPerResFFSpaceHeatingNGUsed,
        RuralPerElecHeatingUsedforWaterHeating,
        RuralPerResFFWaterHeatingNGUsed,
        RuralPerResFFSpaceHeatingFOKerUsed,
        RuralPerResFFWaterHeatingFOKerUsed,
        RuralPerResFFSpaceHeatingLPGUsed,
        RuralPerResFFWaterHeatingLPGUsed,
        BTUperMWh,
        GridLoss,
        PerCoal,
        LB_CO2e_MWh_Coal,
        PerOil,
        LB_CO2e_MWh_Oil,
        PerNG,
        LB_CO2e_MWh_NG,
        PerOtherFos,
        LB_CO2e_MWh_OtherFos,
        MMTperLB,
        PerCombCapture,
        BTUperCCF,
        MCFperCCF,
        LB_CO2e_MCF_NG,
        BTUperGallonFOKer,
        MMTCO2e_ThBarrel_FOKer,
        ThBarrelperGallon,
        BTUperGallonLPG,
        MMTCO2e_ThBarrel_LPG,
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
        * BTUPerBBtu
    )

    NGSystemsGHG = (
        (ResNGConsumption + ComIndNGConsumption)
        * (1 / BTUperCCF)
        * CFperCCF
        * MillionCFperCF
        * (MMTCO2ePerMillionCFNG_CH4 + MMTCO2ePerMillionCFNG_CO2)
    )

    LULUCFGHG = UrbanTrees2015 * (1 + PerUrbanTreeCoverage / 100) + (
        ForestSequestration2015 + ForestLossGain2015
    ) * (1 + PerForestCoverage / 100)

    NonEnergyGHG = (
        AgricultureGHG + SolidWasteGHG + WasteWaterGHG + IndProcGHG + NGSystemsGHG + LULUCFGHG
    )

    return NonEnergyGHG


def CalcGridText(
    PerCoal, PerOil, PerNG, PerNuclear, PerSolar, PerWind, PerBio, PerHydro, PerGeo, PerOtherFos
):
    """
    Creates function for creating paragraph widget text for grid mix to update based on recalculated
    grid mix with user input.
    """
    GridText = (
        """Input percentages. Make sure the grid mix sums to 100%. The current sum is: """
        + str(
            round(
                (
                    PerCoal
                    + PerOil
                    + PerNG
                    + PerNuclear
                    + PerSolar
                    + PerWind
                    + PerBio
                    + PerHydro
                    + PerGeo
                    + PerOtherFos
                ),
                2,
            )
        )
        + "%."
    )
    return GridText


# Modify plot with callbacks based on user input in sliders.
categories = [
    "Residential",
    "Commercial/Industrial",
    "Mobile-Highway",
    "Mobile-Transit",
    "Mobile-Aviation",
    "Mobile-Other",
    "Non-Energy",
]
data = {
    "Category": categories,
    "2015": [
        Residential2015,
        ComInd2015,
        MobHighway2015,
        MobTransit2015,
        MobAviation2015,
        MobOther2015,
        NonEnergy2015,
    ],
    "Scenario": [
        CalcResGHG(
            Population,
            PopFactor,
            PerUrbanPop,
            UrbanBTUPerCapUsed,
            PerCapResEnergyUse,
            UrbanPerResElectrification,
            UrbanPerResElecUsed,
            PerUrbanElecBTUPerCapUsedSpaceHeating,
            PerUrbanElecBTUPerCapUsedWaterHeating,
            PerUrbanElecBTUPerCapUsedOther,
            UrbanPerResNGUsed,
            PerUrbanNGBTUPerCapUsedSpaceHeating,
            PerUrbanNGBTUPerCapUsedWaterHeating,
            PerUrbanNGBTUPerCapUsedOther,
            UrbanPerResFOKerUsed,
            PerUrbanFOKerBTUPerCapUsedSpaceHeating,
            PerUrbanFOKerBTUPerCapUsedWaterHeating,
            PerUrbanFOKerBTUPerCapUsedOther,
            UrbanPerResLPGUsed,
            PerUrbanLPGBTUPerCapUsedSpaceHeating,
            PerUrbanLPGBTUPerCapUsedWaterHeating,
            PerUrbanLPGBTUPerCapUsedOther,
            UrbanPerResFFNGUsed,
            UrbanPerResFFFOKerUsed,
            UrbanPerResFFLPGUsed,
            UrbanPerElecHeatingUsedforSpaceHeating,
            UrbanPerResFFSpaceHeatingNGUsed,
            UrbanPerElecHeatingUsedforWaterHeating,
            UrbanPerResFFWaterHeatingNGUsed,
            UrbanPerResFFSpaceHeatingFOKerUsed,
            UrbanPerResFFWaterHeatingFOKerUsed,
            UrbanPerResFFSpaceHeatingLPGUsed,
            UrbanPerResFFWaterHeatingLPGUsed,
            PerEnergyToUseResElecSpaceHeating,
            PerEnergyToUseResElecWaterHeating,
            PerEnergyToUseResElecOther,
            PerEnergyToUseResElecSpaceHeatingSwitch,
            PerEnergyToUseResElecWaterHeatingSwitch,
            PerEnergyToUseResNGSpaceHeating,
            PerEnergyToUseResNGWaterHeating,
            PerEnergyToUseResNGOther,
            PerEnergyToUseResFOKerSpaceHeating,
            PerEnergyToUseResFOKerWaterHeating,
            PerEnergyToUseResFOKerOther,
            PerEnergyToUseResLPGSpaceHeating,
            PerEnergyToUseResLPGWaterHeating,
            PerEnergyToUseResLPGOther,
            SuburbanBTUPerCapUsed,
            SuburbanPerResElectrification,
            SuburbanPerResElecUsed,
            PerSuburbanElecBTUPerCapUsedSpaceHeating,
            PerSuburbanElecBTUPerCapUsedWaterHeating,
            PerSuburbanElecBTUPerCapUsedOther,
            SuburbanPerResNGUsed,
            PerSuburbanNGBTUPerCapUsedSpaceHeating,
            PerSuburbanNGBTUPerCapUsedWaterHeating,
            PerSuburbanNGBTUPerCapUsedOther,
            SuburbanPerResFOKerUsed,
            PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
            PerSuburbanFOKerBTUPerCapUsedWaterHeating,
            PerSuburbanFOKerBTUPerCapUsedOther,
            SuburbanPerResLPGUsed,
            PerSuburbanLPGBTUPerCapUsedSpaceHeating,
            PerSuburbanLPGBTUPerCapUsedWaterHeating,
            PerSuburbanLPGBTUPerCapUsedOther,
            SuburbanPerResFFNGUsed,
            SuburbanPerResFFFOKerUsed,
            SuburbanPerResFFLPGUsed,
            SuburbanPerElecHeatingUsedforSpaceHeating,
            SuburbanPerResFFSpaceHeatingNGUsed,
            SuburbanPerElecHeatingUsedforWaterHeating,
            SuburbanPerResFFWaterHeatingNGUsed,
            SuburbanPerResFFSpaceHeatingFOKerUsed,
            SuburbanPerResFFWaterHeatingFOKerUsed,
            SuburbanPerResFFSpaceHeatingLPGUsed,
            SuburbanPerResFFWaterHeatingLPGUsed,
            RuralBTUPerCapUsed,
            RuralPerResElectrification,
            RuralPerResElecUsed,
            PerRuralElecBTUPerCapUsedSpaceHeating,
            PerRuralElecBTUPerCapUsedWaterHeating,
            PerRuralElecBTUPerCapUsedOther,
            RuralPerResNGUsed,
            PerRuralNGBTUPerCapUsedSpaceHeating,
            PerRuralNGBTUPerCapUsedWaterHeating,
            PerRuralNGBTUPerCapUsedOther,
            RuralPerResFOKerUsed,
            PerRuralFOKerBTUPerCapUsedSpaceHeating,
            PerRuralFOKerBTUPerCapUsedWaterHeating,
            PerRuralFOKerBTUPerCapUsedOther,
            RuralPerResLPGUsed,
            PerRuralLPGBTUPerCapUsedSpaceHeating,
            PerRuralLPGBTUPerCapUsedWaterHeating,
            PerRuralLPGBTUPerCapUsedOther,
            RuralPerResFFNGUsed,
            RuralPerResFFFOKerUsed,
            RuralPerResFFLPGUsed,
            RuralPerElecHeatingUsedforSpaceHeating,
            RuralPerResFFSpaceHeatingNGUsed,
            RuralPerElecHeatingUsedforWaterHeating,
            RuralPerResFFWaterHeatingNGUsed,
            RuralPerResFFSpaceHeatingFOKerUsed,
            RuralPerResFFWaterHeatingFOKerUsed,
            RuralPerResFFSpaceHeatingLPGUsed,
            RuralPerResFFWaterHeatingLPGUsed,
            BTUperMWh,
            GridLoss,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            BTUperCCF,
            MCFperCCF,
            LB_CO2e_MCF_NG,
            BTUperGallonFOKer,
            MMTCO2e_ThBarrel_FOKer,
            ThBarrelperGallon,
            BTUperGallonLPG,
            MMTCO2e_ThBarrel_LPG,
        )[0],
        CalcComIndGHG(
            ComIndPerElectrification,
            ComIndBBtuUsed,
            PerComIndEnergyUse,
            PerEnergyToUseComIndElec,
            BTUPerBBtu,
            BTUperMWh,
            GridLoss,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            ComIndPerFossilFuelUsed2015,
            ComIndPerFFNGUsed,
            PerEnergyToUseComIndNG,
            MTCO2ePerBBtuNG,
            MMTperMT,
            ComIndPerFFCoalUsed,
            PerEnergyToUseComIndCoal,
            MTCO2ePerBBtuCoal,
            ComIndPerFFDFOUsed,
            PerEnergyToUseComIndDFO,
            MTCO2ePerBBtuDFO,
            ComIndPerFFKerUsed,
            PerEnergyToUseComIndKer,
            MTCO2ePerBBtuKer,
            ComIndPerFFLPGUsed,
            PerEnergyToUseComIndLPG,
            MTCO2ePerBBtuLPG,
            ComIndPerFFMotGasUsed,
            PerEnergyToUseComIndMotGas,
            MTCO2ePerBBtuMotGas,
            ComIndPerFFRFOUsed,
            PerEnergyToUseComIndRFO,
            MTCO2ePerBBtuRFO,
            ComIndPerFFPetCokeUsed,
            PerEnergyToUseComIndPetCoke,
            MTCO2ePerBBtuPetCoke,
            ComIndPerFFStillGasUsed,
            PerEnergyToUseComIndStillGas,
            MTCO2ePerBBtuStillGas,
            ComIndPerSpecialNaphthasUsed,
            PerEnergyToUseComIndSpecialNaphthas,
            MTCO2ePerBBtuSpecialNaphthas,
        ),
        CalcMobHighwayGHG(
            Population,
            PerUrbanPop,
            PopFactor,
            UrbanVMTperPop,
            PerSuburbanPop,
            SuburbanVMTperPop,
            PerRuralPop,
            RuralVMTperPop,
            VMTperCap,
            PerEVMT,
            RegionalFleetMPG,
            CO2eperGallonGasoline,
            MMTperLB,
            EVEff,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            PerCombCapture,
        ),
        CalcMobTransitGHG(
            Population,
            PopFactor,
            BTUperMWh,
            GridLoss,
            PerUrbanPop,
            TransRailUrbanPerElectrification,
            TransRailSuburbanPerElectrification,
            TransRailRuralPerElectrification,
            TransRailUrbanBTUPerCapMotion,
            PerSuburbanPop,
            TransRailSuburbanBTUPerCapMotion,
            PerRuralPop,
            TransRailRuralBTUPerCapMotion,
            PerEnergyToMotionRailElec,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            TransRailMTCO2ePerBBtuDiesel,
            BTUPerBBtu,
            MMTperMT,
            PerEnergyToMotionRailDiesel,
            PerTransRailRidership,
        ),
        CalcMobAviationGHG(MobAviation2015, PopFactor, PerAviation),
        CalcMobOtherGHG(
            FreightRailBBtuMotion,
            FreightRailPerElectrification,
            PerEnergyToMotionRailElec,
            BTUPerBBtu,
            BTUperMWh,
            GridLoss,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            FreightRailMTCO2ePerBBtuDiesel,
            MMTperMT,
            PerEnergyToMotionRailDiesel,
            PerFreightRail,
            InterCityRailBBtuMotion,
            InterCityRailPerElectrification,
            InterCityRailMTCO2ePerBBtuDiesel,
            PerInterCityRail,
            MarinePortPerElectrification,
            MarinePortPerFossilFuelMotion2015,
            MarinePortBBtuMotion,
            PerEnergyToMotionMarineElec,
            MarinePortPerFFRFOMotion,
            MarinePortMTCO2ePerBBtuRFO,
            PerEnergyToMotionMarineRFO,
            MarinePortPerFFDFOMotion,
            MarinePortMTCO2ePerBBtuDFO,
            PerEnergyToMotionMarineDFO,
            PerMarinePort,
            OffroadPerElectrification,
            OffroadPerFossilFuelMotion2015,
            OffroadBBtuMotion,
            PerEnergyToMotionOffroadElec,
            OffroadPerFFMotGasMotion,
            OffroadMTCO2ePerBBtuMotGas,
            PerEnergyToMotionOffroadMotGas,
            OffroadPerFFDFOMotion,
            OffroadMTCO2ePerBBtuDFO,
            PerEnergyToMotionOffroadDFO,
            OffroadPerFFLPGMotion,
            OffroadMTCO2ePerBBtuLPG,
            PerEnergyToMotionOffroadLPG,
            PerOffroad,
        ),
        CalcNonEnergyGHG(
            Ag2015,
            PerAg,
            Waste2015,
            PerWaste,
            PopFactor,
            WasteWater2015,
            PerWasteWater,
            IP2015,
            PerIP,
            Population,
            PerUrbanPop,
            UrbanBTUPerCapUsed,
            PerCapResEnergyUse,
            UrbanPerResElectrification,
            UrbanPerResElecUsed,
            PerUrbanElecBTUPerCapUsedSpaceHeating,
            PerUrbanElecBTUPerCapUsedWaterHeating,
            PerUrbanElecBTUPerCapUsedOther,
            UrbanPerResNGUsed,
            PerUrbanNGBTUPerCapUsedSpaceHeating,
            PerUrbanNGBTUPerCapUsedWaterHeating,
            PerUrbanNGBTUPerCapUsedOther,
            UrbanPerResFOKerUsed,
            PerUrbanFOKerBTUPerCapUsedSpaceHeating,
            PerUrbanFOKerBTUPerCapUsedWaterHeating,
            PerUrbanFOKerBTUPerCapUsedOther,
            UrbanPerResLPGUsed,
            PerUrbanLPGBTUPerCapUsedSpaceHeating,
            PerUrbanLPGBTUPerCapUsedWaterHeating,
            PerUrbanLPGBTUPerCapUsedOther,
            UrbanPerResFFNGUsed,
            UrbanPerResFFFOKerUsed,
            UrbanPerResFFLPGUsed,
            UrbanPerElecHeatingUsedforSpaceHeating,
            UrbanPerResFFSpaceHeatingNGUsed,
            UrbanPerElecHeatingUsedforWaterHeating,
            UrbanPerResFFWaterHeatingNGUsed,
            UrbanPerResFFSpaceHeatingFOKerUsed,
            UrbanPerResFFWaterHeatingFOKerUsed,
            UrbanPerResFFSpaceHeatingLPGUsed,
            UrbanPerResFFWaterHeatingLPGUsed,
            PerEnergyToUseResElecSpaceHeating,
            PerEnergyToUseResElecWaterHeating,
            PerEnergyToUseResElecOther,
            PerEnergyToUseResElecSpaceHeatingSwitch,
            PerEnergyToUseResElecWaterHeatingSwitch,
            PerEnergyToUseResNGSpaceHeating,
            PerEnergyToUseResNGWaterHeating,
            PerEnergyToUseResNGOther,
            PerEnergyToUseResFOKerSpaceHeating,
            PerEnergyToUseResFOKerWaterHeating,
            PerEnergyToUseResFOKerOther,
            PerEnergyToUseResLPGSpaceHeating,
            PerEnergyToUseResLPGWaterHeating,
            PerEnergyToUseResLPGOther,
            SuburbanBTUPerCapUsed,
            SuburbanPerResElectrification,
            SuburbanPerResElecUsed,
            PerSuburbanElecBTUPerCapUsedSpaceHeating,
            PerSuburbanElecBTUPerCapUsedWaterHeating,
            PerSuburbanElecBTUPerCapUsedOther,
            SuburbanPerResNGUsed,
            PerSuburbanNGBTUPerCapUsedSpaceHeating,
            PerSuburbanNGBTUPerCapUsedWaterHeating,
            PerSuburbanNGBTUPerCapUsedOther,
            SuburbanPerResFOKerUsed,
            PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
            PerSuburbanFOKerBTUPerCapUsedWaterHeating,
            PerSuburbanFOKerBTUPerCapUsedOther,
            SuburbanPerResLPGUsed,
            PerSuburbanLPGBTUPerCapUsedSpaceHeating,
            PerSuburbanLPGBTUPerCapUsedWaterHeating,
            PerSuburbanLPGBTUPerCapUsedOther,
            SuburbanPerResFFNGUsed,
            SuburbanPerResFFFOKerUsed,
            SuburbanPerResFFLPGUsed,
            SuburbanPerElecHeatingUsedforSpaceHeating,
            SuburbanPerResFFSpaceHeatingNGUsed,
            SuburbanPerElecHeatingUsedforWaterHeating,
            SuburbanPerResFFWaterHeatingNGUsed,
            SuburbanPerResFFSpaceHeatingFOKerUsed,
            SuburbanPerResFFWaterHeatingFOKerUsed,
            SuburbanPerResFFSpaceHeatingLPGUsed,
            SuburbanPerResFFWaterHeatingLPGUsed,
            RuralBTUPerCapUsed,
            RuralPerResElectrification,
            RuralPerResElecUsed,
            PerRuralElecBTUPerCapUsedSpaceHeating,
            PerRuralElecBTUPerCapUsedWaterHeating,
            PerRuralElecBTUPerCapUsedOther,
            RuralPerResNGUsed,
            PerRuralNGBTUPerCapUsedSpaceHeating,
            PerRuralNGBTUPerCapUsedWaterHeating,
            PerRuralNGBTUPerCapUsedOther,
            RuralPerResFOKerUsed,
            PerRuralFOKerBTUPerCapUsedSpaceHeating,
            PerRuralFOKerBTUPerCapUsedWaterHeating,
            PerRuralFOKerBTUPerCapUsedOther,
            RuralPerResLPGUsed,
            PerRuralLPGBTUPerCapUsedSpaceHeating,
            PerRuralLPGBTUPerCapUsedWaterHeating,
            PerRuralLPGBTUPerCapUsedOther,
            RuralPerResFFNGUsed,
            RuralPerResFFFOKerUsed,
            RuralPerResFFLPGUsed,
            RuralPerElecHeatingUsedforSpaceHeating,
            RuralPerResFFSpaceHeatingNGUsed,
            RuralPerElecHeatingUsedforWaterHeating,
            RuralPerResFFWaterHeatingNGUsed,
            RuralPerResFFSpaceHeatingFOKerUsed,
            RuralPerResFFWaterHeatingFOKerUsed,
            RuralPerResFFSpaceHeatingLPGUsed,
            RuralPerResFFWaterHeatingLPGUsed,
            BTUperMWh,
            GridLoss,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            BTUperCCF,
            MCFperCCF,
            LB_CO2e_MCF_NG,
            BTUperGallonFOKer,
            MMTCO2e_ThBarrel_FOKer,
            ThBarrelperGallon,
            BTUperGallonLPG,
            MMTCO2e_ThBarrel_LPG,
            ComIndPerElectrification,
            ComIndPerFossilFuelUsed2015,
            ComIndBBtuUsed,
            PerComIndEnergyUse,
            ComIndPerFFNGUsed,
            PerEnergyToUseComIndNG,
            BTUPerBBtu,
            CFperCCF,
            MillionCFperCF,
            MMTCO2ePerMillionCFNG_CH4,
            MMTCO2ePerMillionCFNG_CO2,
            UrbanTrees2015,
            PerUrbanTreeCoverage,
            ForestSequestration2015,
            ForestLossGain2015,
            PerForestCoverage,
        ),
    ],
}

source = ColumnDataSource(data=data)

# Configure vertical bar plot
bar_chart = figure(
    x_range=data["Category"],
    y_range=(0, 50),
    plot_height=500,
    plot_width=450,
    y_axis_label="Million Metric Tons of CO2e",
    title="Greenhouse Gas Emissions in Greater Philadelphia",
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

# Transpose data
data2 = {
    "Year": ["2015", "Scenario"],
    "Residential": [
        Residential2015,
        CalcResGHG(
            Population,
            PopFactor,
            PerUrbanPop,
            UrbanBTUPerCapUsed,
            PerCapResEnergyUse,
            UrbanPerResElectrification,
            UrbanPerResElecUsed,
            PerUrbanElecBTUPerCapUsedSpaceHeating,
            PerUrbanElecBTUPerCapUsedWaterHeating,
            PerUrbanElecBTUPerCapUsedOther,
            UrbanPerResNGUsed,
            PerUrbanNGBTUPerCapUsedSpaceHeating,
            PerUrbanNGBTUPerCapUsedWaterHeating,
            PerUrbanNGBTUPerCapUsedOther,
            UrbanPerResFOKerUsed,
            PerUrbanFOKerBTUPerCapUsedSpaceHeating,
            PerUrbanFOKerBTUPerCapUsedWaterHeating,
            PerUrbanFOKerBTUPerCapUsedOther,
            UrbanPerResLPGUsed,
            PerUrbanLPGBTUPerCapUsedSpaceHeating,
            PerUrbanLPGBTUPerCapUsedWaterHeating,
            PerUrbanLPGBTUPerCapUsedOther,
            UrbanPerResFFNGUsed,
            UrbanPerResFFFOKerUsed,
            UrbanPerResFFLPGUsed,
            UrbanPerElecHeatingUsedforSpaceHeating,
            UrbanPerResFFSpaceHeatingNGUsed,
            UrbanPerElecHeatingUsedforWaterHeating,
            UrbanPerResFFWaterHeatingNGUsed,
            UrbanPerResFFSpaceHeatingFOKerUsed,
            UrbanPerResFFWaterHeatingFOKerUsed,
            UrbanPerResFFSpaceHeatingLPGUsed,
            UrbanPerResFFWaterHeatingLPGUsed,
            PerEnergyToUseResElecSpaceHeating,
            PerEnergyToUseResElecWaterHeating,
            PerEnergyToUseResElecOther,
            PerEnergyToUseResElecSpaceHeatingSwitch,
            PerEnergyToUseResElecWaterHeatingSwitch,
            PerEnergyToUseResNGSpaceHeating,
            PerEnergyToUseResNGWaterHeating,
            PerEnergyToUseResNGOther,
            PerEnergyToUseResFOKerSpaceHeating,
            PerEnergyToUseResFOKerWaterHeating,
            PerEnergyToUseResFOKerOther,
            PerEnergyToUseResLPGSpaceHeating,
            PerEnergyToUseResLPGWaterHeating,
            PerEnergyToUseResLPGOther,
            SuburbanBTUPerCapUsed,
            SuburbanPerResElectrification,
            SuburbanPerResElecUsed,
            PerSuburbanElecBTUPerCapUsedSpaceHeating,
            PerSuburbanElecBTUPerCapUsedWaterHeating,
            PerSuburbanElecBTUPerCapUsedOther,
            SuburbanPerResNGUsed,
            PerSuburbanNGBTUPerCapUsedSpaceHeating,
            PerSuburbanNGBTUPerCapUsedWaterHeating,
            PerSuburbanNGBTUPerCapUsedOther,
            SuburbanPerResFOKerUsed,
            PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
            PerSuburbanFOKerBTUPerCapUsedWaterHeating,
            PerSuburbanFOKerBTUPerCapUsedOther,
            SuburbanPerResLPGUsed,
            PerSuburbanLPGBTUPerCapUsedSpaceHeating,
            PerSuburbanLPGBTUPerCapUsedWaterHeating,
            PerSuburbanLPGBTUPerCapUsedOther,
            SuburbanPerResFFNGUsed,
            SuburbanPerResFFFOKerUsed,
            SuburbanPerResFFLPGUsed,
            SuburbanPerElecHeatingUsedforSpaceHeating,
            SuburbanPerResFFSpaceHeatingNGUsed,
            SuburbanPerElecHeatingUsedforWaterHeating,
            SuburbanPerResFFWaterHeatingNGUsed,
            SuburbanPerResFFSpaceHeatingFOKerUsed,
            SuburbanPerResFFWaterHeatingFOKerUsed,
            SuburbanPerResFFSpaceHeatingLPGUsed,
            SuburbanPerResFFWaterHeatingLPGUsed,
            RuralBTUPerCapUsed,
            RuralPerResElectrification,
            RuralPerResElecUsed,
            PerRuralElecBTUPerCapUsedSpaceHeating,
            PerRuralElecBTUPerCapUsedWaterHeating,
            PerRuralElecBTUPerCapUsedOther,
            RuralPerResNGUsed,
            PerRuralNGBTUPerCapUsedSpaceHeating,
            PerRuralNGBTUPerCapUsedWaterHeating,
            PerRuralNGBTUPerCapUsedOther,
            RuralPerResFOKerUsed,
            PerRuralFOKerBTUPerCapUsedSpaceHeating,
            PerRuralFOKerBTUPerCapUsedWaterHeating,
            PerRuralFOKerBTUPerCapUsedOther,
            RuralPerResLPGUsed,
            PerRuralLPGBTUPerCapUsedSpaceHeating,
            PerRuralLPGBTUPerCapUsedWaterHeating,
            PerRuralLPGBTUPerCapUsedOther,
            RuralPerResFFNGUsed,
            RuralPerResFFFOKerUsed,
            RuralPerResFFLPGUsed,
            RuralPerElecHeatingUsedforSpaceHeating,
            RuralPerResFFSpaceHeatingNGUsed,
            RuralPerElecHeatingUsedforWaterHeating,
            RuralPerResFFWaterHeatingNGUsed,
            RuralPerResFFSpaceHeatingFOKerUsed,
            RuralPerResFFWaterHeatingFOKerUsed,
            RuralPerResFFSpaceHeatingLPGUsed,
            RuralPerResFFWaterHeatingLPGUsed,
            BTUperMWh,
            GridLoss,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            BTUperCCF,
            MCFperCCF,
            LB_CO2e_MCF_NG,
            BTUperGallonFOKer,
            MMTCO2e_ThBarrel_FOKer,
            ThBarrelperGallon,
            BTUperGallonLPG,
            MMTCO2e_ThBarrel_LPG,
        )[0],
    ],
    "Commercial/Industrial": [
        ComInd2015,
        CalcComIndGHG(
            ComIndPerElectrification,
            ComIndBBtuUsed,
            PerComIndEnergyUse,
            PerEnergyToUseComIndElec,
            BTUPerBBtu,
            BTUperMWh,
            GridLoss,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            ComIndPerFossilFuelUsed2015,
            ComIndPerFFNGUsed,
            PerEnergyToUseComIndNG,
            MTCO2ePerBBtuNG,
            MMTperMT,
            ComIndPerFFCoalUsed,
            PerEnergyToUseComIndCoal,
            MTCO2ePerBBtuCoal,
            ComIndPerFFDFOUsed,
            PerEnergyToUseComIndDFO,
            MTCO2ePerBBtuDFO,
            ComIndPerFFKerUsed,
            PerEnergyToUseComIndKer,
            MTCO2ePerBBtuKer,
            ComIndPerFFLPGUsed,
            PerEnergyToUseComIndLPG,
            MTCO2ePerBBtuLPG,
            ComIndPerFFMotGasUsed,
            PerEnergyToUseComIndMotGas,
            MTCO2ePerBBtuMotGas,
            ComIndPerFFRFOUsed,
            PerEnergyToUseComIndRFO,
            MTCO2ePerBBtuRFO,
            ComIndPerFFPetCokeUsed,
            PerEnergyToUseComIndPetCoke,
            MTCO2ePerBBtuPetCoke,
            ComIndPerFFStillGasUsed,
            PerEnergyToUseComIndStillGas,
            MTCO2ePerBBtuStillGas,
            ComIndPerSpecialNaphthasUsed,
            PerEnergyToUseComIndSpecialNaphthas,
            MTCO2ePerBBtuSpecialNaphthas,
        ),
    ],
    "Mobile-Highway": [
        MobHighway2015,
        CalcMobHighwayGHG(
            Population,
            PerUrbanPop,
            PopFactor,
            UrbanVMTperPop,
            PerSuburbanPop,
            SuburbanVMTperPop,
            PerRuralPop,
            RuralVMTperPop,
            VMTperCap,
            PerEVMT,
            RegionalFleetMPG,
            CO2eperGallonGasoline,
            MMTperLB,
            EVEff,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            PerCombCapture,
        ),
    ],
    "Mobile-Transit": [
        MobTransit2015,
        CalcMobTransitGHG(
            Population,
            PopFactor,
            BTUperMWh,
            GridLoss,
            PerUrbanPop,
            TransRailUrbanPerElectrification,
            TransRailSuburbanPerElectrification,
            TransRailRuralPerElectrification,
            TransRailUrbanBTUPerCapMotion,
            PerSuburbanPop,
            TransRailSuburbanBTUPerCapMotion,
            PerRuralPop,
            TransRailRuralBTUPerCapMotion,
            PerEnergyToMotionRailElec,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            TransRailMTCO2ePerBBtuDiesel,
            BTUPerBBtu,
            MMTperMT,
            PerEnergyToMotionRailDiesel,
            PerTransRailRidership,
        ),
    ],
    "Mobile-Aviation": [
        MobAviation2015,
        CalcMobAviationGHG(MobAviation2015, PopFactor, PerAviation),
    ],
    "Mobile-Other": [
        MobOther2015,
        CalcMobOtherGHG(
            FreightRailBBtuMotion,
            FreightRailPerElectrification,
            PerEnergyToMotionRailElec,
            BTUPerBBtu,
            BTUperMWh,
            GridLoss,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            FreightRailMTCO2ePerBBtuDiesel,
            MMTperMT,
            PerEnergyToMotionRailDiesel,
            PerFreightRail,
            InterCityRailBBtuMotion,
            InterCityRailPerElectrification,
            InterCityRailMTCO2ePerBBtuDiesel,
            PerInterCityRail,
            MarinePortPerElectrification,
            MarinePortPerFossilFuelMotion2015,
            MarinePortBBtuMotion,
            PerEnergyToMotionMarineElec,
            MarinePortPerFFRFOMotion,
            MarinePortMTCO2ePerBBtuRFO,
            PerEnergyToMotionMarineRFO,
            MarinePortPerFFDFOMotion,
            MarinePortMTCO2ePerBBtuDFO,
            PerEnergyToMotionMarineDFO,
            PerMarinePort,
            OffroadPerElectrification,
            OffroadPerFossilFuelMotion2015,
            OffroadBBtuMotion,
            PerEnergyToMotionOffroadElec,
            OffroadPerFFMotGasMotion,
            OffroadMTCO2ePerBBtuMotGas,
            PerEnergyToMotionOffroadMotGas,
            OffroadPerFFDFOMotion,
            OffroadMTCO2ePerBBtuDFO,
            PerEnergyToMotionOffroadDFO,
            OffroadPerFFLPGMotion,
            OffroadMTCO2ePerBBtuLPG,
            PerEnergyToMotionOffroadLPG,
            PerOffroad,
        ),
    ],
    "Non-Energy": [
        NonEnergy2015,
        CalcNonEnergyGHG(
            Ag2015,
            PerAg,
            Waste2015,
            PerWaste,
            PopFactor,
            WasteWater2015,
            PerWasteWater,
            IP2015,
            PerIP,
            Population,
            PerUrbanPop,
            UrbanBTUPerCapUsed,
            PerCapResEnergyUse,
            UrbanPerResElectrification,
            UrbanPerResElecUsed,
            PerUrbanElecBTUPerCapUsedSpaceHeating,
            PerUrbanElecBTUPerCapUsedWaterHeating,
            PerUrbanElecBTUPerCapUsedOther,
            UrbanPerResNGUsed,
            PerUrbanNGBTUPerCapUsedSpaceHeating,
            PerUrbanNGBTUPerCapUsedWaterHeating,
            PerUrbanNGBTUPerCapUsedOther,
            UrbanPerResFOKerUsed,
            PerUrbanFOKerBTUPerCapUsedSpaceHeating,
            PerUrbanFOKerBTUPerCapUsedWaterHeating,
            PerUrbanFOKerBTUPerCapUsedOther,
            UrbanPerResLPGUsed,
            PerUrbanLPGBTUPerCapUsedSpaceHeating,
            PerUrbanLPGBTUPerCapUsedWaterHeating,
            PerUrbanLPGBTUPerCapUsedOther,
            UrbanPerResFFNGUsed,
            UrbanPerResFFFOKerUsed,
            UrbanPerResFFLPGUsed,
            UrbanPerElecHeatingUsedforSpaceHeating,
            UrbanPerResFFSpaceHeatingNGUsed,
            UrbanPerElecHeatingUsedforWaterHeating,
            UrbanPerResFFWaterHeatingNGUsed,
            UrbanPerResFFSpaceHeatingFOKerUsed,
            UrbanPerResFFWaterHeatingFOKerUsed,
            UrbanPerResFFSpaceHeatingLPGUsed,
            UrbanPerResFFWaterHeatingLPGUsed,
            PerEnergyToUseResElecSpaceHeating,
            PerEnergyToUseResElecWaterHeating,
            PerEnergyToUseResElecOther,
            PerEnergyToUseResElecSpaceHeatingSwitch,
            PerEnergyToUseResElecWaterHeatingSwitch,
            PerEnergyToUseResNGSpaceHeating,
            PerEnergyToUseResNGWaterHeating,
            PerEnergyToUseResNGOther,
            PerEnergyToUseResFOKerSpaceHeating,
            PerEnergyToUseResFOKerWaterHeating,
            PerEnergyToUseResFOKerOther,
            PerEnergyToUseResLPGSpaceHeating,
            PerEnergyToUseResLPGWaterHeating,
            PerEnergyToUseResLPGOther,
            SuburbanBTUPerCapUsed,
            SuburbanPerResElectrification,
            SuburbanPerResElecUsed,
            PerSuburbanElecBTUPerCapUsedSpaceHeating,
            PerSuburbanElecBTUPerCapUsedWaterHeating,
            PerSuburbanElecBTUPerCapUsedOther,
            SuburbanPerResNGUsed,
            PerSuburbanNGBTUPerCapUsedSpaceHeating,
            PerSuburbanNGBTUPerCapUsedWaterHeating,
            PerSuburbanNGBTUPerCapUsedOther,
            SuburbanPerResFOKerUsed,
            PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
            PerSuburbanFOKerBTUPerCapUsedWaterHeating,
            PerSuburbanFOKerBTUPerCapUsedOther,
            SuburbanPerResLPGUsed,
            PerSuburbanLPGBTUPerCapUsedSpaceHeating,
            PerSuburbanLPGBTUPerCapUsedWaterHeating,
            PerSuburbanLPGBTUPerCapUsedOther,
            SuburbanPerResFFNGUsed,
            SuburbanPerResFFFOKerUsed,
            SuburbanPerResFFLPGUsed,
            SuburbanPerElecHeatingUsedforSpaceHeating,
            SuburbanPerResFFSpaceHeatingNGUsed,
            SuburbanPerElecHeatingUsedforWaterHeating,
            SuburbanPerResFFWaterHeatingNGUsed,
            SuburbanPerResFFSpaceHeatingFOKerUsed,
            SuburbanPerResFFWaterHeatingFOKerUsed,
            SuburbanPerResFFSpaceHeatingLPGUsed,
            SuburbanPerResFFWaterHeatingLPGUsed,
            RuralBTUPerCapUsed,
            RuralPerResElectrification,
            RuralPerResElecUsed,
            PerRuralElecBTUPerCapUsedSpaceHeating,
            PerRuralElecBTUPerCapUsedWaterHeating,
            PerRuralElecBTUPerCapUsedOther,
            RuralPerResNGUsed,
            PerRuralNGBTUPerCapUsedSpaceHeating,
            PerRuralNGBTUPerCapUsedWaterHeating,
            PerRuralNGBTUPerCapUsedOther,
            RuralPerResFOKerUsed,
            PerRuralFOKerBTUPerCapUsedSpaceHeating,
            PerRuralFOKerBTUPerCapUsedWaterHeating,
            PerRuralFOKerBTUPerCapUsedOther,
            RuralPerResLPGUsed,
            PerRuralLPGBTUPerCapUsedSpaceHeating,
            PerRuralLPGBTUPerCapUsedWaterHeating,
            PerRuralLPGBTUPerCapUsedOther,
            RuralPerResFFNGUsed,
            RuralPerResFFFOKerUsed,
            RuralPerResFFLPGUsed,
            RuralPerElecHeatingUsedforSpaceHeating,
            RuralPerResFFSpaceHeatingNGUsed,
            RuralPerElecHeatingUsedforWaterHeating,
            RuralPerResFFWaterHeatingNGUsed,
            RuralPerResFFSpaceHeatingFOKerUsed,
            RuralPerResFFWaterHeatingFOKerUsed,
            RuralPerResFFSpaceHeatingLPGUsed,
            RuralPerResFFWaterHeatingLPGUsed,
            BTUperMWh,
            GridLoss,
            PerCoal,
            LB_CO2e_MWh_Coal,
            PerOil,
            LB_CO2e_MWh_Oil,
            PerNG,
            LB_CO2e_MWh_NG,
            PerOtherFos,
            LB_CO2e_MWh_OtherFos,
            MMTperLB,
            PerCombCapture,
            BTUperCCF,
            MCFperCCF,
            LB_CO2e_MCF_NG,
            BTUperGallonFOKer,
            MMTCO2e_ThBarrel_FOKer,
            ThBarrelperGallon,
            BTUperGallonLPG,
            MMTCO2e_ThBarrel_LPG,
            ComIndPerElectrification,
            ComIndPerFossilFuelUsed2015,
            ComIndBBtuUsed,
            PerComIndEnergyUse,
            ComIndPerFFNGUsed,
            PerEnergyToUseComIndNG,
            BTUPerBBtu,
            CFperCCF,
            MillionCFperCF,
            MMTCO2ePerMillionCFNG_CH4,
            MMTCO2ePerMillionCFNG_CO2,
            UrbanTrees2015,
            PerUrbanTreeCoverage,
            ForestSequestration2015,
            ForestLossGain2015,
            PerForestCoverage,
        ),
    ],
}

source2 = ColumnDataSource(data=data2)
sectors = [
    "Residential",
    "Commercial/Industrial",
    "Mobile-Highway",
    "Mobile-Transit",
    "Mobile-Aviation",
    "Mobile-Other",
    "Non-Energy",
]

# Configure stacked bar plot
stacked_bar_chart = figure(
    x_range=data2["Year"],
    y_range=(0, 100),
    plot_height=500,
    plot_width=500,
    y_axis_label="Million Metric Tons of CO2e",
    title="Greenhouse Gas Emissions in Greater Philadelphia",
)

stacked_bar_chart.vbar_stack(
    categories, x="Year", width=0.4, color=Viridis7, source=source2, legend_label=sectors
)

stacked_bar_chart.legend[
    0
].items.reverse()  # Reverses legend items to match order of occurence in stack
stacked_bar_chart_legend = stacked_bar_chart.legend[0]
stacked_bar_chart.add_layout(stacked_bar_chart_legend, "right")

# Configure data and plot for pie chart

x = {
    "Coal": PerCoal,
    "Oil": PerOil,
    "Natural Gas": PerNG,
    "Nuclear": PerNuclear,
    "Solar": PerSolar,
    "Wind": PerWind,
    "Biomass": PerBio,
    "Hydropower": PerHydro,
    "Geothermal": PerGeo,
    "Other Fossil Fuel": PerOtherFos,
}

data3 = pd.Series(x).reset_index(name="Percentage").rename(columns={"index": "FuelType"})
data3["angle"] = data3["Percentage"] / data3["Percentage"].sum() * 2 * pi
data3["color"] = Spectral10

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
    text=CalcGridText(
        PerCoal,
        PerOil,
        PerNG,
        PerNuclear,
        PerSolar,
        PerWind,
        PerBio,
        PerHydro,
        PerGeo,
        PerOtherFos,
    ),
    style={"color": "black"},
)


def callback(attr, old, new):
    """Callback function nested within modify function."""
    PerCoal = float(PerCoalTextInput.value)
    PerOil = float(PerOilTextInput.value)
    PerNG = float(PerNGTextInput.value)
    PerNuclear = float(PerNuclearTextInput.value)
    PerSolar = float(PerSolarTextInput.value)
    PerWind = float(PerWindTextInput.value)
    PerBio = float(PerBioTextInput.value)
    PerHydro = float(PerHydroTextInput.value)
    PerGeo = float(PerGeoTextInput.value)
    PerOtherFos = float(PerOtherFosTextInput.value)
    PerNetZeroCarbon = float(
        PerNetZeroCarbonTextInput.value
    )  # we may add this scenario in the future

    PopFactor = PopFactorSlider.value
    PerUrbanPop = float(PerUrbanPopTextInput.value)
    PerSuburbanPop = float(PerSuburbanPopTextInput.value)
    PerRuralPop = float(PerRuralPopTextInput.value)

    PerCapResEnergyUse = PerCapResEnergyUseSlider.value
    UrbanPerResElectrification = UrbanPerResElectrificationSlider.value
    SuburbanPerResElectrification = SuburbanPerResElectrificationSlider.value
    RuralPerResElectrification = RuralPerResElectrificationSlider.value

    PerComIndEnergyUse = PerComIndEnergyUseSlider.value
    ComIndPerElectrification = ComIndPerElectrificationSlider.value

    VMTperCap = VMTperCapSlider.value
    RegionalFleetMPG = RegionalFleetMPGSlider.value
    #         EVEff = 1/(EVEffSlider.value)
    PerEVMT = PerEVMTSlider.value

    PerTransRailRidership = PerTransRailRidershipSlider.value
    TransRailUrbanPerElectrification = TransRailUrbanPerElectrificationSlider.value
    TransRailSuburbanPerElectrification = TransRailSuburbanPerElectrificationSlider.value
    TransRailRuralPerElectrification = TransRailRuralPerElectrificationSlider.value

    PerFreightRail = PerFreightRailSlider.value
    FreightRailPerElectrification = FreightRailPerElectrificationSlider.value

    PerInterCityRail = PerInterCityRailSlider.value
    InterCityRailPerElectrification = InterCityRailPerElectrificationSlider.value

    PerMarinePort = PerMarinePortSlider.value
    MarinePortPerElectrification = MarinePortPerElectrificationSlider.value

    PerOffroad = PerOffroadSlider.value
    OffroadPerElectrification = OffroadPerElectrificationSlider.value

    PerAviation = PerAviationSlider.value
    PerAg = PerAgSlider.value
    PerWaste = PerWasteSlider.value
    PerWasteWater = PerWasteWaterSlider.value
    PerIP = PerIPSlider.value
    PerUrbanTreeCoverage = PerUrbanTreeCoverageSlider.value
    PerForestCoverage = PerForestCoverageSlider.value

    PerCombCapture = PerCombCaptureSlider.value
    AirCapture = AirCaptureSlider.value  # TK

    # Updates source data for vertical bar chart
    source.data = {
        "Category": [
            "Residential",
            "Commercial/Industrial",
            "Mobile-Highway",
            "Mobile-Transit",
            "Mobile-Aviation",
            "Mobile-Other",
            "Non-Energy",
        ],
        "2015": [
            Residential2015,
            ComInd2015,
            MobHighway2015,
            MobTransit2015,
            MobAviation2015,
            MobOther2015,
            NonEnergy2015,
        ],
        "Scenario": [
            CalcResGHG(
                Population,
                PopFactor,
                PerUrbanPop,
                UrbanBTUPerCapUsed,
                PerCapResEnergyUse,
                UrbanPerResElectrification,
                UrbanPerResElecUsed,
                PerUrbanElecBTUPerCapUsedSpaceHeating,
                PerUrbanElecBTUPerCapUsedWaterHeating,
                PerUrbanElecBTUPerCapUsedOther,
                UrbanPerResNGUsed,
                PerUrbanNGBTUPerCapUsedSpaceHeating,
                PerUrbanNGBTUPerCapUsedWaterHeating,
                PerUrbanNGBTUPerCapUsedOther,
                UrbanPerResFOKerUsed,
                PerUrbanFOKerBTUPerCapUsedSpaceHeating,
                PerUrbanFOKerBTUPerCapUsedWaterHeating,
                PerUrbanFOKerBTUPerCapUsedOther,
                UrbanPerResLPGUsed,
                PerUrbanLPGBTUPerCapUsedSpaceHeating,
                PerUrbanLPGBTUPerCapUsedWaterHeating,
                PerUrbanLPGBTUPerCapUsedOther,
                UrbanPerResFFNGUsed,
                UrbanPerResFFFOKerUsed,
                UrbanPerResFFLPGUsed,
                UrbanPerElecHeatingUsedforSpaceHeating,
                UrbanPerResFFSpaceHeatingNGUsed,
                UrbanPerElecHeatingUsedforWaterHeating,
                UrbanPerResFFWaterHeatingNGUsed,
                UrbanPerResFFSpaceHeatingFOKerUsed,
                UrbanPerResFFWaterHeatingFOKerUsed,
                UrbanPerResFFSpaceHeatingLPGUsed,
                UrbanPerResFFWaterHeatingLPGUsed,
                PerEnergyToUseResElecSpaceHeating,
                PerEnergyToUseResElecWaterHeating,
                PerEnergyToUseResElecOther,
                PerEnergyToUseResElecSpaceHeatingSwitch,
                PerEnergyToUseResElecWaterHeatingSwitch,
                PerEnergyToUseResNGSpaceHeating,
                PerEnergyToUseResNGWaterHeating,
                PerEnergyToUseResNGOther,
                PerEnergyToUseResFOKerSpaceHeating,
                PerEnergyToUseResFOKerWaterHeating,
                PerEnergyToUseResFOKerOther,
                PerEnergyToUseResLPGSpaceHeating,
                PerEnergyToUseResLPGWaterHeating,
                PerEnergyToUseResLPGOther,
                SuburbanBTUPerCapUsed,
                SuburbanPerResElectrification,
                SuburbanPerResElecUsed,
                PerSuburbanElecBTUPerCapUsedSpaceHeating,
                PerSuburbanElecBTUPerCapUsedWaterHeating,
                PerSuburbanElecBTUPerCapUsedOther,
                SuburbanPerResNGUsed,
                PerSuburbanNGBTUPerCapUsedSpaceHeating,
                PerSuburbanNGBTUPerCapUsedWaterHeating,
                PerSuburbanNGBTUPerCapUsedOther,
                SuburbanPerResFOKerUsed,
                PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
                PerSuburbanFOKerBTUPerCapUsedWaterHeating,
                PerSuburbanFOKerBTUPerCapUsedOther,
                SuburbanPerResLPGUsed,
                PerSuburbanLPGBTUPerCapUsedSpaceHeating,
                PerSuburbanLPGBTUPerCapUsedWaterHeating,
                PerSuburbanLPGBTUPerCapUsedOther,
                SuburbanPerResFFNGUsed,
                SuburbanPerResFFFOKerUsed,
                SuburbanPerResFFLPGUsed,
                SuburbanPerElecHeatingUsedforSpaceHeating,
                SuburbanPerResFFSpaceHeatingNGUsed,
                SuburbanPerElecHeatingUsedforWaterHeating,
                SuburbanPerResFFWaterHeatingNGUsed,
                SuburbanPerResFFSpaceHeatingFOKerUsed,
                SuburbanPerResFFWaterHeatingFOKerUsed,
                SuburbanPerResFFSpaceHeatingLPGUsed,
                SuburbanPerResFFWaterHeatingLPGUsed,
                RuralBTUPerCapUsed,
                RuralPerResElectrification,
                RuralPerResElecUsed,
                PerRuralElecBTUPerCapUsedSpaceHeating,
                PerRuralElecBTUPerCapUsedWaterHeating,
                PerRuralElecBTUPerCapUsedOther,
                RuralPerResNGUsed,
                PerRuralNGBTUPerCapUsedSpaceHeating,
                PerRuralNGBTUPerCapUsedWaterHeating,
                PerRuralNGBTUPerCapUsedOther,
                RuralPerResFOKerUsed,
                PerRuralFOKerBTUPerCapUsedSpaceHeating,
                PerRuralFOKerBTUPerCapUsedWaterHeating,
                PerRuralFOKerBTUPerCapUsedOther,
                RuralPerResLPGUsed,
                PerRuralLPGBTUPerCapUsedSpaceHeating,
                PerRuralLPGBTUPerCapUsedWaterHeating,
                PerRuralLPGBTUPerCapUsedOther,
                RuralPerResFFNGUsed,
                RuralPerResFFFOKerUsed,
                RuralPerResFFLPGUsed,
                RuralPerElecHeatingUsedforSpaceHeating,
                RuralPerResFFSpaceHeatingNGUsed,
                RuralPerElecHeatingUsedforWaterHeating,
                RuralPerResFFWaterHeatingNGUsed,
                RuralPerResFFSpaceHeatingFOKerUsed,
                RuralPerResFFWaterHeatingFOKerUsed,
                RuralPerResFFSpaceHeatingLPGUsed,
                RuralPerResFFWaterHeatingLPGUsed,
                BTUperMWh,
                GridLoss,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                BTUperCCF,
                MCFperCCF,
                LB_CO2e_MCF_NG,
                BTUperGallonFOKer,
                MMTCO2e_ThBarrel_FOKer,
                ThBarrelperGallon,
                BTUperGallonLPG,
                MMTCO2e_ThBarrel_LPG,
            )[0],
            CalcComIndGHG(
                ComIndPerElectrification,
                ComIndBBtuUsed,
                PerComIndEnergyUse,
                PerEnergyToUseComIndElec,
                BTUPerBBtu,
                BTUperMWh,
                GridLoss,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                ComIndPerFossilFuelUsed2015,
                ComIndPerFFNGUsed,
                PerEnergyToUseComIndNG,
                MTCO2ePerBBtuNG,
                MMTperMT,
                ComIndPerFFCoalUsed,
                PerEnergyToUseComIndCoal,
                MTCO2ePerBBtuCoal,
                ComIndPerFFDFOUsed,
                PerEnergyToUseComIndDFO,
                MTCO2ePerBBtuDFO,
                ComIndPerFFKerUsed,
                PerEnergyToUseComIndKer,
                MTCO2ePerBBtuKer,
                ComIndPerFFLPGUsed,
                PerEnergyToUseComIndLPG,
                MTCO2ePerBBtuLPG,
                ComIndPerFFMotGasUsed,
                PerEnergyToUseComIndMotGas,
                MTCO2ePerBBtuMotGas,
                ComIndPerFFRFOUsed,
                PerEnergyToUseComIndRFO,
                MTCO2ePerBBtuRFO,
                ComIndPerFFPetCokeUsed,
                PerEnergyToUseComIndPetCoke,
                MTCO2ePerBBtuPetCoke,
                ComIndPerFFStillGasUsed,
                PerEnergyToUseComIndStillGas,
                MTCO2ePerBBtuStillGas,
                ComIndPerSpecialNaphthasUsed,
                PerEnergyToUseComIndSpecialNaphthas,
                MTCO2ePerBBtuSpecialNaphthas,
            ),
            CalcMobHighwayGHG(
                Population,
                PerUrbanPop,
                PopFactor,
                UrbanVMTperPop,
                PerSuburbanPop,
                SuburbanVMTperPop,
                PerRuralPop,
                RuralVMTperPop,
                VMTperCap,
                PerEVMT,
                RegionalFleetMPG,
                CO2eperGallonGasoline,
                MMTperLB,
                EVEff,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                PerCombCapture,
            ),
            CalcMobTransitGHG(
                Population,
                PopFactor,
                BTUperMWh,
                GridLoss,
                PerUrbanPop,
                TransRailUrbanPerElectrification,
                TransRailSuburbanPerElectrification,
                TransRailRuralPerElectrification,
                TransRailUrbanBTUPerCapMotion,
                PerSuburbanPop,
                TransRailSuburbanBTUPerCapMotion,
                PerRuralPop,
                TransRailRuralBTUPerCapMotion,
                PerEnergyToMotionRailElec,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                TransRailMTCO2ePerBBtuDiesel,
                BTUPerBBtu,
                MMTperMT,
                PerEnergyToMotionRailDiesel,
                PerTransRailRidership,
            ),
            CalcMobAviationGHG(MobAviation2015, PopFactor, PerAviation),
            CalcMobOtherGHG(
                FreightRailBBtuMotion,
                FreightRailPerElectrification,
                PerEnergyToMotionRailElec,
                BTUPerBBtu,
                BTUperMWh,
                GridLoss,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                FreightRailMTCO2ePerBBtuDiesel,
                MMTperMT,
                PerEnergyToMotionRailDiesel,
                PerFreightRail,
                InterCityRailBBtuMotion,
                InterCityRailPerElectrification,
                InterCityRailMTCO2ePerBBtuDiesel,
                PerInterCityRail,
                MarinePortPerElectrification,
                MarinePortPerFossilFuelMotion2015,
                MarinePortBBtuMotion,
                PerEnergyToMotionMarineElec,
                MarinePortPerFFRFOMotion,
                MarinePortMTCO2ePerBBtuRFO,
                PerEnergyToMotionMarineRFO,
                MarinePortPerFFDFOMotion,
                MarinePortMTCO2ePerBBtuDFO,
                PerEnergyToMotionMarineDFO,
                PerMarinePort,
                OffroadPerElectrification,
                OffroadPerFossilFuelMotion2015,
                OffroadBBtuMotion,
                PerEnergyToMotionOffroadElec,
                OffroadPerFFMotGasMotion,
                OffroadMTCO2ePerBBtuMotGas,
                PerEnergyToMotionOffroadMotGas,
                OffroadPerFFDFOMotion,
                OffroadMTCO2ePerBBtuDFO,
                PerEnergyToMotionOffroadDFO,
                OffroadPerFFLPGMotion,
                OffroadMTCO2ePerBBtuLPG,
                PerEnergyToMotionOffroadLPG,
                PerOffroad,
            ),
            CalcNonEnergyGHG(
                Ag2015,
                PerAg,
                Waste2015,
                PerWaste,
                PopFactor,
                WasteWater2015,
                PerWasteWater,
                IP2015,
                PerIP,
                Population,
                PerUrbanPop,
                UrbanBTUPerCapUsed,
                PerCapResEnergyUse,
                UrbanPerResElectrification,
                UrbanPerResElecUsed,
                PerUrbanElecBTUPerCapUsedSpaceHeating,
                PerUrbanElecBTUPerCapUsedWaterHeating,
                PerUrbanElecBTUPerCapUsedOther,
                UrbanPerResNGUsed,
                PerUrbanNGBTUPerCapUsedSpaceHeating,
                PerUrbanNGBTUPerCapUsedWaterHeating,
                PerUrbanNGBTUPerCapUsedOther,
                UrbanPerResFOKerUsed,
                PerUrbanFOKerBTUPerCapUsedSpaceHeating,
                PerUrbanFOKerBTUPerCapUsedWaterHeating,
                PerUrbanFOKerBTUPerCapUsedOther,
                UrbanPerResLPGUsed,
                PerUrbanLPGBTUPerCapUsedSpaceHeating,
                PerUrbanLPGBTUPerCapUsedWaterHeating,
                PerUrbanLPGBTUPerCapUsedOther,
                UrbanPerResFFNGUsed,
                UrbanPerResFFFOKerUsed,
                UrbanPerResFFLPGUsed,
                UrbanPerElecHeatingUsedforSpaceHeating,
                UrbanPerResFFSpaceHeatingNGUsed,
                UrbanPerElecHeatingUsedforWaterHeating,
                UrbanPerResFFWaterHeatingNGUsed,
                UrbanPerResFFSpaceHeatingFOKerUsed,
                UrbanPerResFFWaterHeatingFOKerUsed,
                UrbanPerResFFSpaceHeatingLPGUsed,
                UrbanPerResFFWaterHeatingLPGUsed,
                PerEnergyToUseResElecSpaceHeating,
                PerEnergyToUseResElecWaterHeating,
                PerEnergyToUseResElecOther,
                PerEnergyToUseResElecSpaceHeatingSwitch,
                PerEnergyToUseResElecWaterHeatingSwitch,
                PerEnergyToUseResNGSpaceHeating,
                PerEnergyToUseResNGWaterHeating,
                PerEnergyToUseResNGOther,
                PerEnergyToUseResFOKerSpaceHeating,
                PerEnergyToUseResFOKerWaterHeating,
                PerEnergyToUseResFOKerOther,
                PerEnergyToUseResLPGSpaceHeating,
                PerEnergyToUseResLPGWaterHeating,
                PerEnergyToUseResLPGOther,
                SuburbanBTUPerCapUsed,
                SuburbanPerResElectrification,
                SuburbanPerResElecUsed,
                PerSuburbanElecBTUPerCapUsedSpaceHeating,
                PerSuburbanElecBTUPerCapUsedWaterHeating,
                PerSuburbanElecBTUPerCapUsedOther,
                SuburbanPerResNGUsed,
                PerSuburbanNGBTUPerCapUsedSpaceHeating,
                PerSuburbanNGBTUPerCapUsedWaterHeating,
                PerSuburbanNGBTUPerCapUsedOther,
                SuburbanPerResFOKerUsed,
                PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
                PerSuburbanFOKerBTUPerCapUsedWaterHeating,
                PerSuburbanFOKerBTUPerCapUsedOther,
                SuburbanPerResLPGUsed,
                PerSuburbanLPGBTUPerCapUsedSpaceHeating,
                PerSuburbanLPGBTUPerCapUsedWaterHeating,
                PerSuburbanLPGBTUPerCapUsedOther,
                SuburbanPerResFFNGUsed,
                SuburbanPerResFFFOKerUsed,
                SuburbanPerResFFLPGUsed,
                SuburbanPerElecHeatingUsedforSpaceHeating,
                SuburbanPerResFFSpaceHeatingNGUsed,
                SuburbanPerElecHeatingUsedforWaterHeating,
                SuburbanPerResFFWaterHeatingNGUsed,
                SuburbanPerResFFSpaceHeatingFOKerUsed,
                SuburbanPerResFFWaterHeatingFOKerUsed,
                SuburbanPerResFFSpaceHeatingLPGUsed,
                SuburbanPerResFFWaterHeatingLPGUsed,
                RuralBTUPerCapUsed,
                RuralPerResElectrification,
                RuralPerResElecUsed,
                PerRuralElecBTUPerCapUsedSpaceHeating,
                PerRuralElecBTUPerCapUsedWaterHeating,
                PerRuralElecBTUPerCapUsedOther,
                RuralPerResNGUsed,
                PerRuralNGBTUPerCapUsedSpaceHeating,
                PerRuralNGBTUPerCapUsedWaterHeating,
                PerRuralNGBTUPerCapUsedOther,
                RuralPerResFOKerUsed,
                PerRuralFOKerBTUPerCapUsedSpaceHeating,
                PerRuralFOKerBTUPerCapUsedWaterHeating,
                PerRuralFOKerBTUPerCapUsedOther,
                RuralPerResLPGUsed,
                PerRuralLPGBTUPerCapUsedSpaceHeating,
                PerRuralLPGBTUPerCapUsedWaterHeating,
                PerRuralLPGBTUPerCapUsedOther,
                RuralPerResFFNGUsed,
                RuralPerResFFFOKerUsed,
                RuralPerResFFLPGUsed,
                RuralPerElecHeatingUsedforSpaceHeating,
                RuralPerResFFSpaceHeatingNGUsed,
                RuralPerElecHeatingUsedforWaterHeating,
                RuralPerResFFWaterHeatingNGUsed,
                RuralPerResFFSpaceHeatingFOKerUsed,
                RuralPerResFFWaterHeatingFOKerUsed,
                RuralPerResFFSpaceHeatingLPGUsed,
                RuralPerResFFWaterHeatingLPGUsed,
                BTUperMWh,
                GridLoss,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                BTUperCCF,
                MCFperCCF,
                LB_CO2e_MCF_NG,
                BTUperGallonFOKer,
                MMTCO2e_ThBarrel_FOKer,
                ThBarrelperGallon,
                BTUperGallonLPG,
                MMTCO2e_ThBarrel_LPG,
                ComIndPerElectrification,
                ComIndPerFossilFuelUsed2015,
                ComIndBBtuUsed,
                PerComIndEnergyUse,
                ComIndPerFFNGUsed,
                PerEnergyToUseComIndNG,
                BTUPerBBtu,
                CFperCCF,
                MillionCFperCF,
                MMTCO2ePerMillionCFNG_CH4,
                MMTCO2ePerMillionCFNG_CO2,
                UrbanTrees2015,
                PerUrbanTreeCoverage,
                ForestSequestration2015,
                ForestLossGain2015,
                PerForestCoverage,
            ),
        ],
    }

    # Updates source data for stacked bar chart
    source2.data = {
        "Year": ["2015", "Scenario"],
        "Residential": [
            Residential2015,
            CalcResGHG(
                Population,
                PopFactor,
                PerUrbanPop,
                UrbanBTUPerCapUsed,
                PerCapResEnergyUse,
                UrbanPerResElectrification,
                UrbanPerResElecUsed,
                PerUrbanElecBTUPerCapUsedSpaceHeating,
                PerUrbanElecBTUPerCapUsedWaterHeating,
                PerUrbanElecBTUPerCapUsedOther,
                UrbanPerResNGUsed,
                PerUrbanNGBTUPerCapUsedSpaceHeating,
                PerUrbanNGBTUPerCapUsedWaterHeating,
                PerUrbanNGBTUPerCapUsedOther,
                UrbanPerResFOKerUsed,
                PerUrbanFOKerBTUPerCapUsedSpaceHeating,
                PerUrbanFOKerBTUPerCapUsedWaterHeating,
                PerUrbanFOKerBTUPerCapUsedOther,
                UrbanPerResLPGUsed,
                PerUrbanLPGBTUPerCapUsedSpaceHeating,
                PerUrbanLPGBTUPerCapUsedWaterHeating,
                PerUrbanLPGBTUPerCapUsedOther,
                UrbanPerResFFNGUsed,
                UrbanPerResFFFOKerUsed,
                UrbanPerResFFLPGUsed,
                UrbanPerElecHeatingUsedforSpaceHeating,
                UrbanPerResFFSpaceHeatingNGUsed,
                UrbanPerElecHeatingUsedforWaterHeating,
                UrbanPerResFFWaterHeatingNGUsed,
                UrbanPerResFFSpaceHeatingFOKerUsed,
                UrbanPerResFFWaterHeatingFOKerUsed,
                UrbanPerResFFSpaceHeatingLPGUsed,
                UrbanPerResFFWaterHeatingLPGUsed,
                PerEnergyToUseResElecSpaceHeating,
                PerEnergyToUseResElecWaterHeating,
                PerEnergyToUseResElecOther,
                PerEnergyToUseResElecSpaceHeatingSwitch,
                PerEnergyToUseResElecWaterHeatingSwitch,
                PerEnergyToUseResNGSpaceHeating,
                PerEnergyToUseResNGWaterHeating,
                PerEnergyToUseResNGOther,
                PerEnergyToUseResFOKerSpaceHeating,
                PerEnergyToUseResFOKerWaterHeating,
                PerEnergyToUseResFOKerOther,
                PerEnergyToUseResLPGSpaceHeating,
                PerEnergyToUseResLPGWaterHeating,
                PerEnergyToUseResLPGOther,
                SuburbanBTUPerCapUsed,
                SuburbanPerResElectrification,
                SuburbanPerResElecUsed,
                PerSuburbanElecBTUPerCapUsedSpaceHeating,
                PerSuburbanElecBTUPerCapUsedWaterHeating,
                PerSuburbanElecBTUPerCapUsedOther,
                SuburbanPerResNGUsed,
                PerSuburbanNGBTUPerCapUsedSpaceHeating,
                PerSuburbanNGBTUPerCapUsedWaterHeating,
                PerSuburbanNGBTUPerCapUsedOther,
                SuburbanPerResFOKerUsed,
                PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
                PerSuburbanFOKerBTUPerCapUsedWaterHeating,
                PerSuburbanFOKerBTUPerCapUsedOther,
                SuburbanPerResLPGUsed,
                PerSuburbanLPGBTUPerCapUsedSpaceHeating,
                PerSuburbanLPGBTUPerCapUsedWaterHeating,
                PerSuburbanLPGBTUPerCapUsedOther,
                SuburbanPerResFFNGUsed,
                SuburbanPerResFFFOKerUsed,
                SuburbanPerResFFLPGUsed,
                SuburbanPerElecHeatingUsedforSpaceHeating,
                SuburbanPerResFFSpaceHeatingNGUsed,
                SuburbanPerElecHeatingUsedforWaterHeating,
                SuburbanPerResFFWaterHeatingNGUsed,
                SuburbanPerResFFSpaceHeatingFOKerUsed,
                SuburbanPerResFFWaterHeatingFOKerUsed,
                SuburbanPerResFFSpaceHeatingLPGUsed,
                SuburbanPerResFFWaterHeatingLPGUsed,
                RuralBTUPerCapUsed,
                RuralPerResElectrification,
                RuralPerResElecUsed,
                PerRuralElecBTUPerCapUsedSpaceHeating,
                PerRuralElecBTUPerCapUsedWaterHeating,
                PerRuralElecBTUPerCapUsedOther,
                RuralPerResNGUsed,
                PerRuralNGBTUPerCapUsedSpaceHeating,
                PerRuralNGBTUPerCapUsedWaterHeating,
                PerRuralNGBTUPerCapUsedOther,
                RuralPerResFOKerUsed,
                PerRuralFOKerBTUPerCapUsedSpaceHeating,
                PerRuralFOKerBTUPerCapUsedWaterHeating,
                PerRuralFOKerBTUPerCapUsedOther,
                RuralPerResLPGUsed,
                PerRuralLPGBTUPerCapUsedSpaceHeating,
                PerRuralLPGBTUPerCapUsedWaterHeating,
                PerRuralLPGBTUPerCapUsedOther,
                RuralPerResFFNGUsed,
                RuralPerResFFFOKerUsed,
                RuralPerResFFLPGUsed,
                RuralPerElecHeatingUsedforSpaceHeating,
                RuralPerResFFSpaceHeatingNGUsed,
                RuralPerElecHeatingUsedforWaterHeating,
                RuralPerResFFWaterHeatingNGUsed,
                RuralPerResFFSpaceHeatingFOKerUsed,
                RuralPerResFFWaterHeatingFOKerUsed,
                RuralPerResFFSpaceHeatingLPGUsed,
                RuralPerResFFWaterHeatingLPGUsed,
                BTUperMWh,
                GridLoss,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                BTUperCCF,
                MCFperCCF,
                LB_CO2e_MCF_NG,
                BTUperGallonFOKer,
                MMTCO2e_ThBarrel_FOKer,
                ThBarrelperGallon,
                BTUperGallonLPG,
                MMTCO2e_ThBarrel_LPG,
            )[0],
        ],
        "Commercial/Industrial": [
            ComInd2015,
            CalcComIndGHG(
                ComIndPerElectrification,
                ComIndBBtuUsed,
                PerComIndEnergyUse,
                PerEnergyToUseComIndElec,
                BTUPerBBtu,
                BTUperMWh,
                GridLoss,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                ComIndPerFossilFuelUsed2015,
                ComIndPerFFNGUsed,
                PerEnergyToUseComIndNG,
                MTCO2ePerBBtuNG,
                MMTperMT,
                ComIndPerFFCoalUsed,
                PerEnergyToUseComIndCoal,
                MTCO2ePerBBtuCoal,
                ComIndPerFFDFOUsed,
                PerEnergyToUseComIndDFO,
                MTCO2ePerBBtuDFO,
                ComIndPerFFKerUsed,
                PerEnergyToUseComIndKer,
                MTCO2ePerBBtuKer,
                ComIndPerFFLPGUsed,
                PerEnergyToUseComIndLPG,
                MTCO2ePerBBtuLPG,
                ComIndPerFFMotGasUsed,
                PerEnergyToUseComIndMotGas,
                MTCO2ePerBBtuMotGas,
                ComIndPerFFRFOUsed,
                PerEnergyToUseComIndRFO,
                MTCO2ePerBBtuRFO,
                ComIndPerFFPetCokeUsed,
                PerEnergyToUseComIndPetCoke,
                MTCO2ePerBBtuPetCoke,
                ComIndPerFFStillGasUsed,
                PerEnergyToUseComIndStillGas,
                MTCO2ePerBBtuStillGas,
                ComIndPerSpecialNaphthasUsed,
                PerEnergyToUseComIndSpecialNaphthas,
                MTCO2ePerBBtuSpecialNaphthas,
            ),
        ],
        "Mobile-Highway": [
            MobHighway2015,
            CalcMobHighwayGHG(
                Population,
                PerUrbanPop,
                PopFactor,
                UrbanVMTperPop,
                PerSuburbanPop,
                SuburbanVMTperPop,
                PerRuralPop,
                RuralVMTperPop,
                VMTperCap,
                PerEVMT,
                RegionalFleetMPG,
                CO2eperGallonGasoline,
                MMTperLB,
                EVEff,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                PerCombCapture,
            ),
        ],
        "Mobile-Transit": [
            MobTransit2015,
            CalcMobTransitGHG(
                Population,
                PopFactor,
                BTUperMWh,
                GridLoss,
                PerUrbanPop,
                TransRailUrbanPerElectrification,
                TransRailSuburbanPerElectrification,
                TransRailRuralPerElectrification,
                TransRailUrbanBTUPerCapMotion,
                PerSuburbanPop,
                TransRailSuburbanBTUPerCapMotion,
                PerRuralPop,
                TransRailRuralBTUPerCapMotion,
                PerEnergyToMotionRailElec,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                TransRailMTCO2ePerBBtuDiesel,
                BTUPerBBtu,
                MMTperMT,
                PerEnergyToMotionRailDiesel,
                PerTransRailRidership,
            ),
        ],
        "Mobile-Aviation": [
            MobAviation2015,
            CalcMobAviationGHG(MobAviation2015, PopFactor, PerAviation),
        ],
        "Mobile-Other": [
            MobOther2015,
            CalcMobOtherGHG(
                FreightRailBBtuMotion,
                FreightRailPerElectrification,
                PerEnergyToMotionRailElec,
                BTUPerBBtu,
                BTUperMWh,
                GridLoss,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                FreightRailMTCO2ePerBBtuDiesel,
                MMTperMT,
                PerEnergyToMotionRailDiesel,
                PerFreightRail,
                InterCityRailBBtuMotion,
                InterCityRailPerElectrification,
                InterCityRailMTCO2ePerBBtuDiesel,
                PerInterCityRail,
                MarinePortPerElectrification,
                MarinePortPerFossilFuelMotion2015,
                MarinePortBBtuMotion,
                PerEnergyToMotionMarineElec,
                MarinePortPerFFRFOMotion,
                MarinePortMTCO2ePerBBtuRFO,
                PerEnergyToMotionMarineRFO,
                MarinePortPerFFDFOMotion,
                MarinePortMTCO2ePerBBtuDFO,
                PerEnergyToMotionMarineDFO,
                PerMarinePort,
                OffroadPerElectrification,
                OffroadPerFossilFuelMotion2015,
                OffroadBBtuMotion,
                PerEnergyToMotionOffroadElec,
                OffroadPerFFMotGasMotion,
                OffroadMTCO2ePerBBtuMotGas,
                PerEnergyToMotionOffroadMotGas,
                OffroadPerFFDFOMotion,
                OffroadMTCO2ePerBBtuDFO,
                PerEnergyToMotionOffroadDFO,
                OffroadPerFFLPGMotion,
                OffroadMTCO2ePerBBtuLPG,
                PerEnergyToMotionOffroadLPG,
                PerOffroad,
            ),
        ],
        "Non-Energy": [
            NonEnergy2015,
            CalcNonEnergyGHG(
                Ag2015,
                PerAg,
                Waste2015,
                PerWaste,
                PopFactor,
                WasteWater2015,
                PerWasteWater,
                IP2015,
                PerIP,
                Population,
                PerUrbanPop,
                UrbanBTUPerCapUsed,
                PerCapResEnergyUse,
                UrbanPerResElectrification,
                UrbanPerResElecUsed,
                PerUrbanElecBTUPerCapUsedSpaceHeating,
                PerUrbanElecBTUPerCapUsedWaterHeating,
                PerUrbanElecBTUPerCapUsedOther,
                UrbanPerResNGUsed,
                PerUrbanNGBTUPerCapUsedSpaceHeating,
                PerUrbanNGBTUPerCapUsedWaterHeating,
                PerUrbanNGBTUPerCapUsedOther,
                UrbanPerResFOKerUsed,
                PerUrbanFOKerBTUPerCapUsedSpaceHeating,
                PerUrbanFOKerBTUPerCapUsedWaterHeating,
                PerUrbanFOKerBTUPerCapUsedOther,
                UrbanPerResLPGUsed,
                PerUrbanLPGBTUPerCapUsedSpaceHeating,
                PerUrbanLPGBTUPerCapUsedWaterHeating,
                PerUrbanLPGBTUPerCapUsedOther,
                UrbanPerResFFNGUsed,
                UrbanPerResFFFOKerUsed,
                UrbanPerResFFLPGUsed,
                UrbanPerElecHeatingUsedforSpaceHeating,
                UrbanPerResFFSpaceHeatingNGUsed,
                UrbanPerElecHeatingUsedforWaterHeating,
                UrbanPerResFFWaterHeatingNGUsed,
                UrbanPerResFFSpaceHeatingFOKerUsed,
                UrbanPerResFFWaterHeatingFOKerUsed,
                UrbanPerResFFSpaceHeatingLPGUsed,
                UrbanPerResFFWaterHeatingLPGUsed,
                PerEnergyToUseResElecSpaceHeating,
                PerEnergyToUseResElecWaterHeating,
                PerEnergyToUseResElecOther,
                PerEnergyToUseResElecSpaceHeatingSwitch,
                PerEnergyToUseResElecWaterHeatingSwitch,
                PerEnergyToUseResNGSpaceHeating,
                PerEnergyToUseResNGWaterHeating,
                PerEnergyToUseResNGOther,
                PerEnergyToUseResFOKerSpaceHeating,
                PerEnergyToUseResFOKerWaterHeating,
                PerEnergyToUseResFOKerOther,
                PerEnergyToUseResLPGSpaceHeating,
                PerEnergyToUseResLPGWaterHeating,
                PerEnergyToUseResLPGOther,
                SuburbanBTUPerCapUsed,
                SuburbanPerResElectrification,
                SuburbanPerResElecUsed,
                PerSuburbanElecBTUPerCapUsedSpaceHeating,
                PerSuburbanElecBTUPerCapUsedWaterHeating,
                PerSuburbanElecBTUPerCapUsedOther,
                SuburbanPerResNGUsed,
                PerSuburbanNGBTUPerCapUsedSpaceHeating,
                PerSuburbanNGBTUPerCapUsedWaterHeating,
                PerSuburbanNGBTUPerCapUsedOther,
                SuburbanPerResFOKerUsed,
                PerSuburbanFOKerBTUPerCapUsedSpaceHeating,
                PerSuburbanFOKerBTUPerCapUsedWaterHeating,
                PerSuburbanFOKerBTUPerCapUsedOther,
                SuburbanPerResLPGUsed,
                PerSuburbanLPGBTUPerCapUsedSpaceHeating,
                PerSuburbanLPGBTUPerCapUsedWaterHeating,
                PerSuburbanLPGBTUPerCapUsedOther,
                SuburbanPerResFFNGUsed,
                SuburbanPerResFFFOKerUsed,
                SuburbanPerResFFLPGUsed,
                SuburbanPerElecHeatingUsedforSpaceHeating,
                SuburbanPerResFFSpaceHeatingNGUsed,
                SuburbanPerElecHeatingUsedforWaterHeating,
                SuburbanPerResFFWaterHeatingNGUsed,
                SuburbanPerResFFSpaceHeatingFOKerUsed,
                SuburbanPerResFFWaterHeatingFOKerUsed,
                SuburbanPerResFFSpaceHeatingLPGUsed,
                SuburbanPerResFFWaterHeatingLPGUsed,
                RuralBTUPerCapUsed,
                RuralPerResElectrification,
                RuralPerResElecUsed,
                PerRuralElecBTUPerCapUsedSpaceHeating,
                PerRuralElecBTUPerCapUsedWaterHeating,
                PerRuralElecBTUPerCapUsedOther,
                RuralPerResNGUsed,
                PerRuralNGBTUPerCapUsedSpaceHeating,
                PerRuralNGBTUPerCapUsedWaterHeating,
                PerRuralNGBTUPerCapUsedOther,
                RuralPerResFOKerUsed,
                PerRuralFOKerBTUPerCapUsedSpaceHeating,
                PerRuralFOKerBTUPerCapUsedWaterHeating,
                PerRuralFOKerBTUPerCapUsedOther,
                RuralPerResLPGUsed,
                PerRuralLPGBTUPerCapUsedSpaceHeating,
                PerRuralLPGBTUPerCapUsedWaterHeating,
                PerRuralLPGBTUPerCapUsedOther,
                RuralPerResFFNGUsed,
                RuralPerResFFFOKerUsed,
                RuralPerResFFLPGUsed,
                RuralPerElecHeatingUsedforSpaceHeating,
                RuralPerResFFSpaceHeatingNGUsed,
                RuralPerElecHeatingUsedforWaterHeating,
                RuralPerResFFWaterHeatingNGUsed,
                RuralPerResFFSpaceHeatingFOKerUsed,
                RuralPerResFFWaterHeatingFOKerUsed,
                RuralPerResFFSpaceHeatingLPGUsed,
                RuralPerResFFWaterHeatingLPGUsed,
                BTUperMWh,
                GridLoss,
                PerCoal,
                LB_CO2e_MWh_Coal,
                PerOil,
                LB_CO2e_MWh_Oil,
                PerNG,
                LB_CO2e_MWh_NG,
                PerOtherFos,
                LB_CO2e_MWh_OtherFos,
                MMTperLB,
                PerCombCapture,
                BTUperCCF,
                MCFperCCF,
                LB_CO2e_MCF_NG,
                BTUperGallonFOKer,
                MMTCO2e_ThBarrel_FOKer,
                ThBarrelperGallon,
                BTUperGallonLPG,
                MMTCO2e_ThBarrel_LPG,
                ComIndPerElectrification,
                ComIndPerFossilFuelUsed2015,
                ComIndBBtuUsed,
                PerComIndEnergyUse,
                ComIndPerFFNGUsed,
                PerEnergyToUseComIndNG,
                BTUPerBBtu,
                CFperCCF,
                MillionCFperCF,
                MMTCO2ePerMillionCFNG_CH4,
                MMTCO2ePerMillionCFNG_CO2,
                UrbanTrees2015,
                PerUrbanTreeCoverage,
                ForestSequestration2015,
                ForestLossGain2015,
                PerForestCoverage,
            ),
        ],
    }

    # Updates source data for pie chart
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
            PerCoal,
            PerOil,
            PerNG,
            PerNuclear,
            PerSolar,
            PerWind,
            PerBio,
            PerHydro,
            PerGeo,
            PerOtherFos,
        ],
        "angle": [
            (
                PerCoal
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
            (
                PerOil
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
            (
                PerNG
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
            (
                PerNuclear
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
            (
                PerSolar
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
            (
                PerWind
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
            (
                PerBio
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
            (
                PerHydro
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
            (
                PerGeo
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
            (
                PerOtherFos
                / (
                    PerBio
                    + PerCoal
                    + PerHydro
                    + PerNG
                    + PerNuclear
                    + PerOil
                    + PerOtherFos
                    + PerSolar
                    + PerWind
                    + PerGeo
                )
                * (2 * pi)
            ),
        ],
        "color": Spectral10,
    }
    # Updates the paragraph widget text based on the new text inputs
    if (
        round(
            (
                PerCoal
                + PerOil
                + PerNG
                + PerNuclear
                + PerSolar
                + PerWind
                + PerBio
                + PerHydro
                + PerGeo
                + PerOtherFos
            ),
            2,
        )
        > 100
    ):
        GridTextParagraph.text = CalcGridText(
            PerCoal,
            PerOil,
            PerNG,
            PerNuclear,
            PerSolar,
            PerWind,
            PerBio,
            PerHydro,
            PerGeo,
            PerOtherFos,
        )
        GridTextParagraph.style = {"color": "red"}
    elif (
        round(
            (
                PerCoal
                + PerOil
                + PerNG
                + PerNuclear
                + PerSolar
                + PerWind
                + PerBio
                + PerHydro
                + PerOtherFos
            ),
            2,
        )
        < 100
    ):
        GridTextParagraph.text = CalcGridText(
            PerCoal,
            PerOil,
            PerNG,
            PerNuclear,
            PerSolar,
            PerWind,
            PerBio,
            PerHydro,
            PerGeo,
            PerOtherFos,
        )
        GridTextParagraph.style = {"color": "orange"}
    else:
        GridTextParagraph.text = CalcGridText(
            PerCoal,
            PerOil,
            PerNG,
            PerNuclear,
            PerSolar,
            PerWind,
            PerBio,
            PerHydro,
            PerGeo,
            PerOtherFos,
        )
        GridTextParagraph.style = {"color": "black"}


# Creates Widgets

# Grid Inputs
PerCoalTextInput = TextInput(value=str(round(PerCoal, 1)), title="% Coal in Grid Mix")
PerCoalTextInput.on_change("value", callback)

PerOilTextInput = TextInput(value=str(round(PerOil, 1)), title="% Oil in Grid Mix")
PerOilTextInput.on_change("value", callback)

PerNGTextInput = TextInput(value=str(round(PerNG, 1)), title="% Natural Gas in Grid Mix")
PerNGTextInput.on_change("value", callback)

PerNuclearTextInput = TextInput(value=str(round(PerNuclear, 1)), title="% Nuclear in Grid Mix")
PerNuclearTextInput.on_change("value", callback)

PerSolarTextInput = TextInput(value=str(round(PerSolar, 1)), title="% Solar in Grid Mix")
PerSolarTextInput.on_change("value", callback)

PerWindTextInput = TextInput(value=str(round(PerWind, 1)), title="% Wind in Grid Mix")
PerWindTextInput.on_change("value", callback)

PerBioTextInput = TextInput(value=str(round(PerBio, 1)), title="% Biomass in Grid Mix")
PerBioTextInput.on_change("value", callback)

PerHydroTextInput = TextInput(value=str(round(PerHydro, 1)), title="% Hydropower in Grid Mix")
PerHydroTextInput.on_change("value", callback)

PerGeoTextInput = TextInput(value=str(round(PerGeo, 1)), title="% Geothermal in Grid Mix")
PerGeoTextInput.on_change("value", callback)

PerOtherFosTextInput = TextInput(
    value=str(round(PerOtherFos, 1)), title="% Other Fossil Fuel in Grid Mix"
)
PerOtherFosTextInput.on_change("value", callback)

PerNetZeroCarbonTextInput = TextInput(
    value=str(round(PerNuclear + PerSolar + PerWind + PerBio + PerHydro + PerGeo)),
    title="% Net Zero Carbon Sources in Grid Mix",
)
PerNetZeroCarbonTextInput.on_change("value", callback)

# Population Inputs
PopFactorSlider = Slider(start=-100, end=100, value=0, step=10, title="% Change in Population")
PopFactorSlider.on_change("value", callback)

PerUrbanPopTextInput = TextInput(
    value=str(round(PerUrbanPop, 1)), title="% of Population Living in Urban Municipalities"
)
PerUrbanPopTextInput.on_change("value", callback)

PerSuburbanPopTextInput = TextInput(
    value=str(round(PerSuburbanPop, 1)), title="% of Population Living in Suburban Municipalities",
)
PerSuburbanPopTextInput.on_change("value", callback)

PerRuralPopTextInput = TextInput(
    value=str(round(PerRuralPop, 1)), title="% of Population Living in Rural Municipalities"
)
PerRuralPopTextInput.on_change("value", callback)

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

#     EVEffSlider = Slider(start=0.1, end=10, value=1/EVEff, step=.1, title = "EV Efficiency (mi/kWh)")
#     EVEffSlider.on_change('value', callback)

# Mobile Energy Inputs - Rail Transit
PerTransRailRidershipSlider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Transit Ridership"
)
PerTransRailRidershipSlider.on_change("value", callback)

TransRailUrbanPerElectrificationSlider = Slider(
    start=0,
    end=100,
    value=TransRailUrbanPerElecMotion,
    step=1,
    title="% Electrification of Rail Transit Urban Areas",
)
TransRailUrbanPerElectrificationSlider.on_change("value", callback)

TransRailSuburbanPerElectrificationSlider = Slider(
    start=0,
    end=100,
    value=TransRailRuralPerElecMotion,
    step=1,
    title="% Electrification of Rail Transit in Suburban Areas",
)
TransRailSuburbanPerElectrificationSlider.on_change("value", callback)

TransRailRuralPerElectrificationSlider = Slider(
    start=0,
    end=100,
    value=TransRailRuralPerElecMotion,
    step=1,
    title="% Electrification of Rail Transit in Rural Areas",
)
TransRailRuralPerElectrificationSlider.on_change("value", callback)

# Mobile Energy Inputs - Aviation
PerAviationSlider = Slider(start=-100, end=100, value=0, step=1, title="% Change in Air Travel")
PerAviationSlider.on_change("value", callback)

# Mobile Energy Inputs - Freight Rail
PerFreightRailSlider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Freight Rail"
)
PerFreightRailSlider.on_change("value", callback)

FreightRailPerElectrificationSlider = Slider(
    start=0,
    end=100,
    value=FreightRailPerElecMotion,
    step=1,
    title="% Electrification of Rail Freight",
)
FreightRailPerElectrificationSlider.on_change("value", callback)

# Mobile Energy Inputs - Inter-city Rail
PerInterCityRailSlider = Slider(
    start=-100, end=100, value=0, step=1, title="% Change in Inter-city Rail Travel"
)
PerInterCityRailSlider.on_change("value", callback)

InterCityRailPerElectrificationSlider = Slider(
    start=0,
    end=100,
    value=InterCityRailPerElecMotion,
    step=1,
    title="% Electrification of Inter-city Rail",
)
InterCityRailPerElectrificationSlider.on_change("value", callback)

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
    PopFactorSlider, PerUrbanPopTextInput, PerSuburbanPopTextInput, PerRuralPopTextInput
)
widgetGrid = Column(
    GridTextParagraph,
    PerCoalTextInput,
    PerOilTextInput,
    PerNGTextInput,
    PerNuclearTextInput,
    PerSolarTextInput,
    PerWindTextInput,
    PerBioTextInput,
    PerHydroTextInput,
    PerGeoTextInput,
    PerOtherFosTextInput,
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
    TransRailUrbanPerElectrificationSlider,
    TransRailSuburbanPerElectrificationSlider,
    TransRailRuralPerElectrificationSlider,
)
widgetMobileOther = Column(
    PerAviationSlider,
    PerFreightRailSlider,
    FreightRailPerElectrificationSlider,
    PerInterCityRailSlider,
    InterCityRailPerElectrificationSlider,
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

user_inputs = [
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

curdoc().add_root(column(bar_chart, stacked_bar_chart, electric_grid_pie_chart))
curdoc().add_root(column(user_inputs))
