# -*- coding: utf-8 -*-
"""
example_ideal_test_time.py

The influence of test gas composition and driven length on the available test
time is investiagted over a range of temperatures. The available test time is
calculated for an air test gas at two different driven section lengths (6 and
4 m) and for an argon test gas (6m driven length). The calculation are 
performed by assuming ideal wave propagation in the shock tube and by assumiung
that the test time is ended from a pressure wave that is reflected from the 
interaction of contact surface and reflected shock wave.

Both methods "shock_compression" and "initial_pressures_for_test_state" also
calculate the test time. Either function can be used to determine the test
time, depending on what is more practical for the user. This will be demonstrated
in this example.

Written and maintained by:
    Lisa Zander
    lisa.zander@tu-berlin.de

"""


import cantera as ct
from shocktube import shocktube
import numpy as np
import matplotlib.pyplot as plt

#%% influence of driven length on test time - air test gas

# set the gas state to the initial test gas state - here air
gas = ct.Solution('gri30.yaml')
gas.TPX = 293.15, ct.one_atm, 'O2:21,N2:79'

# initialize the shock tube object with the test gas at initial conditions
s = shocktube(testgas = gas)

# choose a set of Mach numbers for the calculation
Ms_air = np.linspace(1.5,2.5,21)

# save calculated test times and test temperature in the following lists
tt_air_6m = []
tt_air_4m = []
T5 = []

for Ms in Ms_air:
    # shock_compression method calculates the state of the testgas behind reflected
    # and incident shock, at the same time the test time is calculated
    s.shock_compression(Ms = Ms)
    T5.append(s.T5)
    
    # calculation of test time is performed automatically for a driven length
    # with the value of s.drivenLength 
    # when re-setting the length of the driven section, the test time is re-calculated
    s.drivenLength= 6
    tt_air_6m.append(s.testtime*1e3)
    s.drivenLength = 4
    tt_air_4m.append(s.testtime*1e3)
    

#%% influence of test gas composition - calculation of test time for argon tets gas

# one can create new shock tube object, however, here the existing object is used
# and the test gas is adjusted to be argon - there are two version to do this:

# version 1
s.testgas.TPX = 293.15, ct.one_atm, 'Ar:1'

# version 2
#gas.TPX = 293.15, ct.one_atm, 'Ar:1'
#s.insert_testgas(gas)


# reset the length of the driver to 6m
s.drivenLength = 6

# calculations will be performed at the same test temperature as with air in
# order to compare the test times.
# However, available test time is independent of test pressure, set it 
# arbitrarily to 35bar
# Also, an arbitrary performance curve is used

tt_argon_6m = []
# note that the mach number will be different from the one in air when temperature is kept constant
Ms_argon = []

for t5 in T5:
    s.initial_pressures_for_test_state(t5, P5 = 35e5, pc=lambda Ms: 0.9*Ms**4)
    tt_argon_6m.append(s.testtime*1e3)
    Ms_argon.append(s.Ms)

    
#%% visualize the results

plt.figure()
plt.plot(T5, tt_air_6m)
plt.plot(T5, tt_air_4m)
plt.plot(T5, tt_argon_6m)
plt.xlabel('T5/K')
plt.ylabel('available test time/ms')
plt.legend(['air, 6m driven section', 'air, 4m driven section', 'argon, 6m driven section',])


plt.figure()
plt.plot(Ms_air, tt_air_6m)
plt.plot(Ms_air, tt_air_4m)
plt.plot(Ms_argon, tt_argon_6m)
plt.xlabel('Ms')
plt.ylabel('available test time/ms')
plt.legend(['air, 6m driven section', 'air, 4m driven section', 'argon, 6m driven section',])
