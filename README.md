# Introduction and Scope


This code is a python-implementation of the classic one-dimensional shock tube theory, namely the conservation equations over incident and reflected shock, developed within the PhD [^1]. Thermodynamic relations are integrated by using the package Cantera [^2]. This code is mainly designed for two tasks:

1. **Planning a shock‑tube experiment:** Determine the pressures at the beginning of the experiment (`P1` and `P4`), that are required for a desired test condition behind the reflected shock (temperature `T5` and pressure `P5`).

2. **Post‑processing a shock‑tube measurement:** Determine the test condition behind the reflected shock (temperature `T5` and pressure `P5`) from the incident shock speed `Ws` (or the Mach number `Ms`) and the initial conditions (temperature `T1` and pressure `P1`).

In both cases, the states behind incident and reflected shocks, as well as characteristic velocities (incident and reflected shock speed, particle velocity behind incident shock) and the available test time are solved for.

# License

The source code of this project is licensed under the MIT License.


# Third-Party Libraries

This software uses the following open-source libraries:

- Cantera
- NumPy
- SciPy
- Matplotlib

The full license texts for these libraries are included in the `third_party_licenses/` directory.


# Nomenclature and Background


The terminology is chosen similar to [^3] and summarised in the following table:


| Attribute | Meaning | Units |
|-----------|---------|-------|
| `T2` | Temperature behind the incident shock (state 2) | K | 
| `P2` | Pressure behind the incident shock (state 2) | Pa | 
| `T5` | Temperature behind the reflected shock (state 5) | K |
| `P5` | Pressure behind the reflected shock (state 5) | Pa | 
| `Ws` | Incident‑shock speed (lab frame) | m s⁻¹ | 
| `Wr` | Reflected‑shock speed (lab frame) | m s⁻¹ | 
| `Ms` | Mach number of the incident shock | – | 
| `Mr` | Mach number of the reflected shock | – | 
| `up` | Particle velocity of the gas behind the incident shock | m s⁻¹ | 
| `c1` | Speed of sound in the test gas prior to shock compression (state 1) | m s⁻¹ | 
| `c2` | Speed of sound behind the incident shock (state 2) | m s⁻¹ | 
| `c5` | Speed of sound behind the reflected shock (state 5) | m s⁻¹ | 
| `testtime` | Available test time (time between shock arrival at the end wall and the reflected‑shock-contact-surface disturbance arrival) | s | 
| `T1` | Initial temperature of the test gas (state 1) | K | 
| `P1` | Initial pressure of the test gas (state 1) | Pa | 
| `Xtest` | Mole fraction vector of the test gas | – | 
| `drivenLength` | Length of the driven section of the shock tube (user‑settable) | m | 


The conservation equations of mass, momentum and energy over incident and reflected shocks are solved. The solution approach and background is explained in the dissertation [^1]. 

The test time is calculated from the interaction of waves in the shock tube, taking the length of the driven section into account. The calculation of the test time is explained in [^4]. Please note that only the case in which the test time is terminated by the wave reflected from the interaction of the reflected shock and the contact surface is considered.

All of the attributes in the table above, except the `drivenLength`, are read-only. They are automatically updated when a calculation is performed. When `drivenLength` is updated, the `testtime` is recalculated.


# Usage Overview

Here, an overview over the usage of the code is provided. Additional examples are summarised in the next section.


## Import required modules and define the test gas

First, import Cantera and the shocktube code:

```python
import cantera as ct
from shocktube import shocktube
```

Cantera is then used to define the test gas at the state prior to shock compression, e.g. air at 300 K, 1 atm:

```python
gas = ct.Solution('gri30.yaml')
gas.TPX = 300, ct.one_atm, 'N2:0.79, O2:0.21'
```

Then, a shocktube object is initialised by passing the test gas and setting the driven section length (default is 6m):

```python
st = shocktube(gas, drivenLength=6.0)
```

Two main methods are implemented to support planning and post-processing a shock tube experiment, namely `initial_pressures_for_test_state` and `shock_compression`.

## Planning a shock tube experiment with `initial_pressures_for_test_state`

Planning a shock tube experiment requires the calculation of the initial pressures in the shock tube (pressures `P1` and `P4`) that result in the desired test state behind the reflected shock (temperature `T5` and pressure `P5`).

In following example, the test gas is air at initially 300K (added to shock tube object `st` in the previous section). The following code demonstrates, how to obtain `P1` and `P4` for the desired test state of `T5`=1500K and `P5`=5e5Pa, when the test gas is helium at 300K:

```python
P1, P4 = st.initial_pressures_for_test_state(T5=1500, P5=5e5, drivergas={'T':300, 'heat capacity ratio':1.667,'molar mass':4.0})
print(f'Initial test gas pressure = {P1/1e5:.2f}bar')
print(f'Driver gas pressure      = {P4/1e5:.2f}bar')
```

All read-only attributes are filled during the calculation. An overview over the calculation results can be obtained with:

```python
st.printresults()
```

In the example above, the shock tube behaves as an ideal shock tube, in particular there are no losses and no incident shock attenuation. In this case, the `drivergas` is passed to `initial_pressures_for_test_state` either as a dict or as a `cantera.Solution` object.

To account for real non-ideal shock tube behaviour, a performance curve can be passed to `initial_pressures_for_test_state`. This is illustrated in `example_measurement_planning.py`. A performance curve describes the relation between pressure ratio across the membrane `P4/P1` and the incident shock Mach number `Ms`, `P4/P1 = f(Ms)`.



## Post-processing a shock tube experiment with `shock_compression`

Usually, the incident shock wave speed (or incident shock Mach number) is measured in a shock tube experiment, as well as the incident (pre-shock) thermodynamic state and mixture of the test gas. During post processing, the state behind the reflected shock (temperature `T5` and pressure `P5`) is obtained from these measured quantities.

In the following example, the incident shock speed was measured to 1100 m s⁻¹ and the test gas is air initially at 300K and 1atm.

Note, that the testgas in the shock tube `st` is now at the pressure `P1` from the previous calculation. It is possible to set the initial gas state through `st.testgas.TPX`. However, the cleaner method is to use `insert_testgas`, as all  results from previous calculations are reset to avoid confusion with old results:

```python
gas.TPX = 300, ct.one_atm, 'N2:0.79, O2:0.21'
st.insert_testgas(gas)
st.printresults()
```

The actual calculation of the post-reflected-shock conditions is performed with:

```python
st.shock_compression(Ws=1100)
print(f'temperature behind reflected shock = {st.T5:.1f}K')
print(f'Pressure behind reflected shock = {st.P5/1e5:.2f}bar')
```

Again, an overview over the calculation results can be obtained with:

```python
st.printresults()
```



# Examples

A few use cases are presented in example python scripts:

* `example_ideal_performance_curve.py`: A performance curve, ie. the relation `P4/P1 = f(Ms)`, is determined for ideal shock tube behavior and helium driver gas
* `example_ideal_test_time.py`: The available test time is calculated assuming ideal shock tube behavior with variation of temperature `T5`, driven section length `drivenLength` and test gas composition (air vs argon)
* `example_measurement_planning.py`: Create a table with the pressures `P1` and `P4` required for a measurement campaign targeting a constant `P5` and varying `T5` utilising a performance curve
* `example_measurement_postprocessing.py`: Calculate the post-reflected shock state (temperature `T5` and pressure `P5`) for a given initial test gas state and incident shock speed (`Ws`)

# References

[^1]: Zander, L. Optimization of Combustible Mixtures for Shockless Explosion Combustion Based on Shock
Tube Investigations, 2026.

[^2]: Goodwin, D. G.; Speth, R. L.; Moffat, H. K.; Weber, B. W. Cantera: An Object-Oriented Software Toolkit for Chemical Kinetics, Thermodynamics, and Transport Processes, 2021. https://doi.org/10.5281/zenodo.4527812.

[^3]: Anderson, J. D. Modern Compressible Flow: With Historical Perspective, 3. ed., internat. ed.; McGraw-Hill: Boston u.a., 2003.

[^4]: Zander, L.; Vinkeloe, J.; Djordjevic, N. Ignition Delay and Chemical–Kinetic Modeling of Undiluted Mixtures in a High-Pressure Shock Tube: Nonideal Effects and Comparative Uncertainty Analysis. International Journal of Chemical Kinetics 2021, 53 (5), 611–637. https://doi.org/10.1002/kin.21469.



