# -*- coding: utf-8 -*-
"""
example_measurement_planning.py

The relation between pressure ratio across the membrane P4/P1 and the incident 
shock Mach number Ms is experimentally determined to be
    	(1) P4/P1 = 0.9 * Ms^4
for an air (21% O2, 79% N2) test gas and helium driver gas at room temperature
(293.15K).

The relation in (1) is used for planing of shock tube experiments. For a 
desired test state, the necessary pressures in driver and driven section  
before bursting of the membrane are obtained for a range of test conditions 
(35 bar, temperature ranging from 600 to 1000K).

Written and maintained by:
    Lisa Zander
    lisa.zander@tu-berlin.de

"""

import cantera as ct
from shocktube import shocktube
import numpy as np

#%% Parameters

# Test conditions of interest
P5 = 35e5 # 35bar
T5 = np.linspace(600,1000,9)

# performance curve determined experimentally for Helium driver and air test 
# gas at 293.15K
pc = lambda Ms: 0.9*Ms**4

#%% Determine P1 and P4 necessary for the given test conditions

# define the test gas
gas = ct.Solution('gri30.yaml')
gas.TPX = 293.15, ct.one_atm, 'O2:21,N2:79' 
# the pressure does not matter, the exact P1 will be determined through 
# 'initial_pressures_for_test_state'

# initialize the shock tube object with the test gas at initial conditions
s = shocktube(testgas = gas)

P1 = []
P4 = []
for t5 in T5:
    # call the function that solves the initial pressures for the desired test
    # state 't5, P5' for given relation 'pc'
    p1, p4 = s.initial_pressures_for_test_state(t5, P5, pc=pc)    
    P1.append(p1)
    P4.append(p4)
    
#%% Display the results
print('\nT5/K   P1/bar         P4/bar')
for i in range(len(T5)):
    print(T5[i], P1[i]/1e5, P4[i]/1e5)
