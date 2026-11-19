# -*- coding: utf-8 -*-
"""
example_ideal_performance_curve.py

The relation between pressure ratio across the membrane P4/P1 and the incident 
shock Mach number Ms is usually referred to as "performance curve". It is often
experimentally determined in order to plan shock tube measurements. In this
example file a fictitious experimental performance curve is compared to ideal 
shock tube calculations.

Air (21% O2, 79% N2) is used as test gas and helium as driver gas, both at room 
temperature (293.15K). The ideal relation between the pressure in test and 
driver section and shock Mach number is determined here for a range of chosen
test temperatures T5 and at a constant test pressure P5 of 35 bar.
It is compared to the following fictitious experimental curve,
    	P4/P1 = 0.9 * Ms^4.



Written and maintained by:
    Lisa Zander
    lisa.zander@tu-berlin.de

"""

import numpy as np
import matplotlib.pyplot as plt
import cantera as ct
from shocktube import shocktube


#%% Parameters

# considered test pressure
P5 = 35e5 # 35bar

# performance curve determined experimentally for helium driver  and air test 
# gas at 293.15K
pc = lambda Ms: 0.9*Ms**4

#%% calculation of the ideal performance curve

# define the test gas
# set the gas state to the initial test gas state
gas = ct.Solution('gri30.yaml')
gas.TPX = 293.15, ct.one_atm, 'O2:21,N2:79'

# define the driver gas from cti/yaml-file
driver = ct.Solution('helium.yaml')
driver.TPX = 293.15, 1*ct.one_atm, 'He:1' # pressure does not matter here
# ALTERNATIVELY:
# driver = {'T':293.15, 'heat capacity ratio':1.6666666666666665, 'molar mass':  4.0026}

# initialize the shock tube object with the test gas at initial conditions
s = shocktube(testgas = gas)

# save Ms and P4/P1
Ms = []
P41_ideal = []

for T5 in np.linspace(500,1000,11):
    P1, P4 = s.initial_pressures_for_test_state(T5, P5, drivergas = driver)
    Ms.append(s.Ms)
    P41_ideal.append(P4/P1)
      
#%% Visualize the results

plt.figure()
plt.plot(Ms, P41_ideal)
plt.plot(Ms, pc(np.array(Ms)))
plt.xlabel('Ms')
plt.ylabel('P4/P1')
plt.legend(['ideal', 'measurement'])  
