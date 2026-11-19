# -*- coding: utf-8 -*-
"""
example_measurement_postprocessing.py 

A shock tube experiment is performed with air (21% O2, 79% N2) as test gas. The
test gas is at standard conditions initially (1 atm, 293.15 K). The velocity of 
the incident shock is measured to 1000 m/s.

The example shows how to use the shock tube class to determine the state of the
test gas behind the incident and reflected shock. When solving for these states,
the solution algorithm calculates the speed of the gas behind the incident 
shock, the reflected shock's speed and the available test time. 

Written and maintained by:
    Lisa Zander
    lisa.zander@tu-berlin.de

"""

import cantera as ct
from shocktube import shocktube

#%% Version 1
print('\nVersion 1\n---------') 

# set the gas state to the initial test gas state
gas = ct.Solution('gri30.yaml')
gas.TPX = 293.15, ct.one_atm, 'O2:21,N2:79'

# initialize the shock tube object with the test gas at initial conditions
s = shocktube(testgas = gas)

# shock_compression method calculates the state of the testgas behind reflected
# and incident shock
s.shock_compression(Ws = 1000)

# Look at the results
print('\nResults\n-------')
print('test gas state behind incident shock ')
print('temperature/K: ', s.T2)
print('pressure/bar: ', s.P2/1e5)
print('\ntest gas state behind reflected shock ')
print('temperature/K: ', s.T5)
print('pressure/bar: ', s.P5/1e5)
print('\ngas velocities and Mach numbers')
print('incident shock Mach number: ', s.Ms)
print('velocity of gas behind incident shock/ms^-1:', s.up)
print('reflected shock speed/ms^-1: ', s.Wr)
print('reflected shock Mach number: ', s.Mr)
print('\nAvailable test time/ms' ,s.testtime*1e3 ,'(assuming ideal wave propagation and that wave reflected from interaction of reflected shock and contact surface terminates test time)')

    
#%% Version 2
print('\nVersion 2\n---------') 

# set the gas state to the initial test gas state
gas = ct.Solution('gri30.yaml')
gas.TPX = 293.15, ct.one_atm, 'O2:21,N2:79'

# initialize the shock tube object 
s = shocktube()

# set the test gas at initial conditions
s.insert_testgas(gas)

# determine the Mach number of the incident shock
# there is a handy method for calculation of speed of sound included
c = s._speedofsound(gas)

# shock_compression method calculates the state of the testgas behind reflected
# and incident shock
s.shock_compression(Ms = 1000/c)

# Look at the results
print('\nResults\n-------')
print('test gas state behind incident shock ')
print('temperature/K: ', s.T2)
print('pressure/bar: ', s.P2/1e5)
print('\ntest gas state behind reflected shock ')
print('temperature/K: ', s.T5)
print('pressure/bar: ', s.P5/1e5)
print('\ngas velocities and Mach numbers')
print('incident shock speed/ms^-1: ', s.Ws)
print('velocity of gas behind incident shock/ms^-1:', s.up)
print('reflected shock speed/ms^-1: ', s.Wr)
print('reflected shock Mach number: ', s.Mr)
print('\nAvailable test time/ms' ,s.testtime*1e3 ,'(assuming ideal wave propagation and that wave reflected from interaction of reflected shock and contact surface terminates test time)')
