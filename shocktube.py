# -*- coding: utf-8 -*-
"""
shocktube.py

An implementation of the shock tube equations in python. The solution algorithm 
consideres that the thermodynamic properties of the test gas vary with 
temperature.

The following modules are required (version number used for implementing this 
code are given in parentheses):
    cantera (2.4.0 & 3.1.0)
    numpy (1.15.4 & 2.2.4)
    scipy (optimize module, 1.4.1 & 1.15.2)

Written and maintained by:
    Lisa Zander
    lisa.zander@tu-berlin.de

"""

import cantera as ct
import numpy as np
import scipy.optimize as optm

class shocktube():
    '''
    A class to represent a shock tube. The solution algorithm 
    consideres that the thermodynamic properties of the test gas vary with 
    temperature.
    '''

    
    def __init__(self, testgas = None, drivenLength = 6):
        '''
        Initializes the shocktube.

        Parameters
        ----------
        testgas : cantera.Solution, optional
            Represents the test gas in state 1 (before shock compression). The 
            default is None.
        drivenLength : float, optional
            The length of the driven section in meters. The default is 6.

        Returns
        -------
        None.

        '''
        # length of driven section in m
           
        # for test time calculation length is needed
        self.__drivenLength = drivenLength
        
        if testgas!= None:
            self.insert_testgas(testgas)
        else:
            self.testgas = None       
            # calculation results are read-only properties 
            # set them to None for now, to indicate calculation was not performed
            self._reset_all_calculation_values()
        
    def insert_testgas(self, gas ):
        '''
        Sets the test gas in state 1 (before shock compression) to 'gas'.

        Parameters
        ----------
        gas : Cantera.Solution
            Represents the test gas in state 1.

        Returns
        -------
        None.

        '''
    # insert the testgas at state 1 into the shock tube
       
        # check if gas is a cantera solution object
        if isinstance(gas, ct.Solution) == False:
                raise Exception("'testgas' needs to be cantera solution object!")
        
        self.testgas = gas        
        # reset all the values, that are calculated
        # reason: when new gas is inserted, the old calculation results do not match
        self._reset_all_calculation_values()

    
    def _reset_all_calculation_values(self):
        """Reset every attribute that stores a result of a previous calculation.
        
        All attributes that are read‑only for the user are set to 'None'.
        """
        
        self._T2 = None
        self._P2 = None
        self._c2 = None
        self._T5 = None
        self._P5 = None
        self._c5 = None
        self._Ws = None
        self._Wr = None
        self._Ms = None
        self._Mr = None
        self._up = None
        self._testtime = None
        # the state 1 will be saved when a calculation is started 
        # this helps to remeber at which conditions the calculations were performed
        # in case the testgas is changed outside of this class
        self._P1 = None
        self._T1 = None
        self._Xtest = None
        self._c1 = None

        
    # read-only attributes
    @property
    def T2(self):
        '''Temperature behind the incident shock (state 2) in K.
        
        Read-only! 
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._T2
    
    @property
    def P2(self):
        '''Pressure behind the incident shock (state 2) in Pa.
        
        Read-only! 
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._P2
    
    @property
    def T5(self):
        '''Temperature behind the reflected shock (state 5) in K.
        
        Read-only! 
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._T5
    
    @property
    def P5(self):
        '''Pressure behind the reflected shock (state 5) in Pa.
        
        Read-only! 
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._P5
    
    @property
    def Wr(self):
        '''Speed of the reflected shock relative to the laboratory frame (ms^-1).
        
        Read-only! 
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._Wr
    
    @property
    def Ws(self):
        '''Speed of the incident shock relative to the laboratory frame (ms^-1).
        
        Read-only! 
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._Ws

    @property
    def Mr(self):
        '''
        Mach number of reflected shock.
        
        Read-only.
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._Mr
    
    @property
    def Ms(self):
        '''
        Mach number of incident shock.
        
        Read-only.
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._Ms
    
    @property
    def up(self):
        '''
        Particle velocity of the gas behind the incident shock (ms^-1).
        
        Read-only.
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._up

    @property
    def c2(self):
        '''
        Speed of sound in the gas behind the incident shock (state 2) (ms^-1).        
        
        Read-only.
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._c2

    @property
    def c5(self):
        '''
        Speed of sound in the gas behind the reflected shock (state 2) (ms^-1).        
        
        Read-only.
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._c5
        
    @property
    def testtime(self):
        """Available test time (seconds) for the chosen tube length.

        Computed from the ideal wave‑propagation model after a successful
        call to 'shock_compression' or 'initial_pressures_for_test_state'.
        """
        return self._testtime

    @property
    def c1(self):
        '''
        Speed of sound in the test gas before shock compression (state 1) (ms^-1).        
        
        Read-only.
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._c1

    @property
    def T1(self):
        '''Temperature of the test gas before shock compression (state 1) in K.
        
        Read-only! 
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._T1
    
    @property
    def P1(self):
        '''Pressure of the test gas before shock compression (state 1) in Pa.
        
        Read-only! 
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._P1
    
    @property
    def Xtest(self):
        '''Composition of the test gas (mole fraction vector).
        
        Read-only! 
        
        It's value is set when calculations are performed, i.e. methods 
        'shock_compression' or 'initial_pressures_for_test_state' are called.
        If no calculation was perfomed yet, it's values is 'None'.
        '''
        return self._Xtest
    
    @property
    def drivenLength(self):
        '''Length of the shock tube's driven section in m.
        
        Defaults to 6. This value is used to calculate the available test test 
        time. When this value is updated, the test time is re-calculated.
        '''
        return self.__drivenLength

    @drivenLength.setter
    def drivenLength(self, L):
        if L != self.__drivenLength:
            # set new values
            self.__drivenLength = L
            # check if calculation was performed already:
            if self.Ms:
                # calculation was performed --> recalculate available test time:
                print('Driven section length is updated -> test time is recalculated for updated driven section length.')
                self._availableTestTime()
            
    
    # Methods that call the global calculation functions
    
    def shock_compression(self, Ws = None, Ms = None, drivergas = None, verbose = False):
        '''
        Calculates the states 2 and 5 after compression of test gas by incident
        and reflected shock wave.
        
        Calculation results are stored in the attributes T2, P2, c2, T5, P5, 
        c5, Ms, Mr, Ws, Wr, up. Note, all previous calculation results stored in 
        these attributes are overwritten. The test time is also calculated and 
        stored in the attribute 'testtime', assuming ideal wave propagation 
        and that the wave originating from the interaction of contact surface 
        and reflected shock terminates the test time and using the shock tube 
        length that is store in drivenLength. The state of the test gas
        prior to shock compression (state 1) is stored in the attributes T1, P1
        and c1 upon calling this method. The composition of the test gas is 
        stored in Xtest.
        
        As input, either provide incident shock wave speed, Mach number or 
        driver gas state and composition. When driver gas is specified, the
        incident shock strength is determined assuming ideal shock tube 
        relations. The driver gas is always assumed to have non-temperature 
        dependent heat capacities.
        
        Parameters
        ----------
        Ws : float, optional
            Incident shock speed in m/s. The default is None.
        Ms : float, optional
            Incident shock Mach number. The default is None.
        drivergas : cantera.Solution or dict, optional
            The driver gas at condition before the experiment (state 4). 
            Provide it either as cantera.Solution object or dict with the entries 
            'P' (pressure in Pa), 'T' (temperature in K), 'heat capacity ratio'
            (heat capacity ratio), 'molar mass' (molar mass in g/mol). E.g.
            for Helium at 300K and 40bar
            {'P':40e5, 'T':300, 'heat capacity ratio':1.667, 'molar mass': 4.0}
            The default is None.

        Raises
        ------
        Exception
            DESCRIPTION.

        Returns
        -------
        None. Solution written to attributes T2, P2, c2, T5, P5, c5, Ms, Mr, 
        Ws, Wr, up and testtime.

        '''

        
        # check input options - Ws OR Ms OR driver gas - only one option should be provided
        if Ws == None and Ms == None and drivergas == None:
            raise Exception("Please provide either 'Ws' or 'Ms' or 'drivergas'!")
        if (Ws and Ms) or (Ws and drivergas) or (Ms and drivergas) or (Ws and Ms and drivergas):
            raise Exception("Please provide only one of 'Ws' or 'Ms' or 'drivergas'!")
        
        # check type of driver- either cantera.solution or driverprops
        if drivergas != None:
            if isinstance(drivergas, ct.Solution) == False:
                if isinstance(drivergas,dict) == False:
                    raise Exception("Please provide driver gas either as 'ct.Solution' or dictionary!")
                else:
                    # check that the keys P, T, heat cap ratio, molar mass are in the keys 
                    for k in ['P', 'T', 'heat capacity ratio', 'molar mass']:
                        if k not in drivergas.keys():
                            raise Exception("Driver gas dictionary needs all of the following keys - P, T, heat capacity ratio, molar mass ")
            
        
        if self.testgas == None:
            raise Exception("Please set the testgas with shocktube.insert_testgas()!")

        # first reset all previous result (is this actually necessary?)
        self._reset_all_calculation_values()

        # then save state 1
        # (I checked: copy(self.testgas.T/P/X) is not necessary here)
        self._T1 = self.testgas.T        
        self._P1 = self.testgas.P
        self._Xtest = self.testgas.X
        
        # calculate and store speed of sound in region 1 (for Ms calculation)
        c1 = self._speedofsound(self.testgas)
        self._c1 = c1
        
        # print info to screen (that may make usage easier)
        if verbose == True:
            print('Calculation of states 2 and 5 is performed.')
            print('Test gas is initially at (state 1):')
            print('Temperature:', self.testgas.T ,'K' )
            print('Pressure:', self.testgas.P/1e5 ,'Pa' )
            print('Mole fractions:')
            # rather iterate through X than mole_fraction_dict - I had issues with the latter
            for x, s in zip(self.testgas.X, self.testgas.species_names ):
                if x !=0:
                    print('\t',s, x)
            
        
        # perform calculations depending on input
        if Ws:
            self._Ws = Ws
            self._Ms = Ws/c1
            self._calculateState25fromSWS(Ws)
        elif Ms:
            Ws = Ms*self._c1
            self._Ws = Ws
            self._Ms = Ms
            self._calculateState25fromSWS(Ws)
        elif drivergas:
            if isinstance(drivergas, ct.Solution) == True:
                g4 = drivergas.cp / drivergas.cv
                R4 = ct.gas_constant/ drivergas.mean_molecular_weight
                self._calculateState25fromIC( drivergas.P, g4, drivergas.T, R4 )
            else:
                R4 = ct.gas_constant/ drivergas['molar mass']
                self._calculateState25fromIC( drivergas['P'], drivergas['heat capacity ratio'], drivergas['T'], R4 )                

        # calculation of the available test time in the ideal case
        self._availableTestTime()

        
    def initial_pressures_for_test_state(self, T5, P5, drivergas = None, pc = None, verbose = False):
        '''
        Calculates the pressure of the driver and test gas necessary to obtain
        a certain test gas condition.
        
        As an input either a fuctional relation between incident shock Mach 
        number and pressure ratio across the membrane P4/P1 (= performance
        curve) or the driver gas at the temperature before the experiment can be
        given. The use of a measured performance curve enables to account for 
        non-idealities, while the use of the driver gas as input performs the
        calculations assuming ideal shock tube behavior. Note, the driver gas is 
        assumed to have non-temperature dependent heat capacities.
        
        During the solution process, also states 2 and 5 are calculated. These
        calculation results are stored in the attributes T2, P2, c2, T5, P5, 
        c5, Ms, Mr, Ws, Wr, up. Note, all prvious calculation results stored in 
        these attributes are overwritten. The test time is also calculated and 
        stored in the attribute 'testtime', assuming ideal wave propagation 
        and that the wave originating from the interaction of contact surface 
        and reflected shock terminates the test time and using the shock tube 
        length that is store in drivenLength. The state of the test gas prior
        to shock compression, as well as the test gas composition are stored in
        the attributes T1, P1, C1, Xtest.       
        
        Parameters
        ----------
        T5 : float
            Desired test temperature in K.
        P5 : float
            Desired test pressure in Pa.
        drivergas : cantera.Solution or dict, optional
            The driver gas at condition before the experiment (state 4). 
            Provide it either as cantera.Solution object or dict with the entries 
            'T' (temperature in K), 'heat capacity ratio' (heat capacity ratio), 
            'molar mass' (molar mass in g/mol). E.g. for Helium at 300K
            {'T':300, 'heat capacity ratio':1.667, 'molar mass': 4.0}
            The default is None.
        pc : function, optional
            Performance curve. Function that takes the inciden shock Mach 
            number Ms as an input and returns the pressure ratio across the
            membrane prior to the experiment P4/P1. 
            The default is None.

        Raises
        ------
        Exception
            DESCRIPTION.

        Returns
        -------
        P1 : float
            Test gas pressure before experiment in Pa.
        P4 : float
            Driver gas presure before experiment in Pa.

        '''
        
        # check the inputs - driver or pc must be provided
        if (drivergas == None and pc == None) or (pc and drivergas):
            raise Exception("Please provide either 'pc' or 'drivergas'!")
        
        # check type of driver- either cantera.solution or driverprops
        if drivergas != None:
            if isinstance(drivergas, ct.Solution) == False:
                if isinstance(drivergas,dict) == False:
                    raise Exception("Please provide driver gas either as 'ct.Solution' or dictionary!")
                else:
                    # check that the keys T, heat cap ratio, molar mass are in the keys 
                    for k in ['T', 'heat capacity ratio', 'molar mass']:
                        if k not in drivergas.keys():
                            raise Exception("Driver gas dictionary needs all of the following keys - T, heat capacity ratio, molar mass ")
        else:
            if callable(pc) == False:
                raise Exception("The performance curve 'pc' needs to be provided as a function.")
        
        
        # first reset all previous result (is this actually necessary?)
        self._reset_all_calculation_values()

        if self.testgas == None:
            raise Exception("Please set the testgas with shocktube.insert_testgas()!")


        # then save state 1
        # (I checked: copy(self.testgas.T/P/X) is not necessary here)
        self._T1 = self.testgas.T        
        self._Xtest = self.testgas.X
        # calculate and store speed of sound in region 1 (for Ms calculation)
        c1 = self._speedofsound(self.testgas)
        self._c1 = c1
        
        # save state 5 TODO does this even make sense?
        self._T5 = T5
        self._P5 = P5
        
        # print info to screen (that may make usage easier)
        if verbose == True:
            print('Calculation of initial pressures for desired test state is performed.')
            print('Test gas is initially at:')
            print('Temperature:', self.testgas.T ,'K' )
            print('Mole fractions:')
            # rather iterate through X than mole_fraction_dict - I had issues with the latter
            for x, s in zip(self.testgas.X, self.testgas.species_names ):
                if x !=0:
                    print('\t',s, x)
        
        
        if pc:
            P1, P4 = self._determineICforState5_performanceCurve(T5, P5, pc)
            # set all the remaining values:
            self._P1 = P1    
            #self._calculateState25fromSWS(self.Ws)

            
        elif drivergas:
            if isinstance(drivergas, ct.Solution) == True:
                g4 = drivergas.cp / drivergas.cv
                R4 = ct.gas_constant/ drivergas.mean_molecular_weight
                P1, P4 = self._determineIdealICforState5(T5, P5, g4, drivergas.T, R4)
            else:
                R4 = ct.gas_constant/ drivergas['molar mass']
                P1,P4 = self._determineIdealICforState5( T5, P5, drivergas['heat capacity ratio'], drivergas['T'], R4)
            # set all the remaining values:
            self._P1 = P1            
            #self._calculateState25fromSWS(self.Ws)              

        # calculation of the available test time in the ideal case
        self._availableTestTime()      

        return P1,P4
    
    def printresults(self):

        print('\ntest gas state before shock compression ')
        print('temperature/K: ', self.T1)
        print('pressure/Pa: ', self.P1)        
        
        print('\ntest gas state behind incident shock ')
        print('temperature/K: ', self.T2)
        print('pressure/Pa: ', self.P2)
        
        print('\ntest gas state behind reflected shock ')
        print('temperature/K: ', self.T5)
        print('pressure/Pa: ', self.P5)
        
        print('\ngas velocities and Mach numbers')
        print('incident shock speed/ms^-1: ', self.Ws)
        print('incident shock Mach number: ', self.Ms)
        print('velocity of gas behind incident shock/ms^-1:', self.up)
        print('reflected shock speed/ms^-1: ', self.Wr)
        print('reflected shock Mach number: ', self.Mr)
        
        print('\nAvailable test time/s:' ,self.testtime ,'(assuming ideal wave propagation and that wave reflected from interaction of reflected shock and contact surface terminates test time)')
  
    @staticmethod
    def _speedofsound(gas):
        R = ct.gas_constant/gas.mean_molecular_weight
        g = gas.cp/gas.cv
        return (g*R*gas.T)**(0.5)
    
    @staticmethod
    def _normalshock(gas, u1):

        # check the input - scipy solve functions sometimes makes ndarray out of float:
        if type(u1) == np.ndarray:
            u1 = u1[0]
        
        # save initial state:
        T1, P1, X1 = gas.TPX
        rho1 = gas.density
        h1 = gas.enthalpy_mass

        # initial guess for solution algorithm - CPG assumption:
        R1 = ct.gas_constant/gas.mean_molecular_weight
        g1 = gas.cp/gas.cv
        a1 = (g1*R1*T1)**0.5
        M1 = u1/a1
        P2est = P1*( 1 + 2*g1/(g1+1)*(M1**2 - 1) )
        T2est = T1*( 1 + 2*g1/(g1+1)*(M1**2 - 1) )*( (2 + (g1-1)*M1**2)/((g1+1)*M1**2) )

        # set up the equaiton system
        def nsEquations( T2P2 ):
            T2, P2 = T2P2[0], T2P2[1]
            gas.TPX = T2, P2, X1
            rho2 = gas.density
            h2 = gas.enthalpy_mass
            # continuity equation:
            u2 = u1*rho1/rho2
            # momentum equation:
            mom = P1 - P2 + rho1*u1**2 - rho2*u2**2
            # energy equation:
            en = h1 + u1**2/2 - h2 - u2**2/2
            return [mom, en]

        # solve it
        initGuess = np.array([T2est, P2est])
        sol = optm.root( nsEquations, initGuess)
        T2, P2 = sol.x
        gas.TPX = T2, P2, X1
        rho2 = gas.density
        u2 = u1*rho1/rho2

        # reset to state 1:
        gas.TPX = T1, P1, X1

        return T2, P2, u2


    def _reflectedshock(self, gas2, up, Wr_ig = None):

        T2, P2, X2 = gas2.TPX
        rho2 = gas2.density
        h2 = gas2.enthalpy_mass
        
        # simple initial guess
        if Wr_ig == None:
            Wr_ig = 2*up
            # print('initial guess for Wr is set to 2*up in _reflectedshock')
            
        # initial guess: cpg assumption
        R2 = ct.gas_constant/gas2.mean_molecular_weight
        g2 = gas2.cp/gas2.cv
        a2 = (g2*R2*T2)**0.5
        
        Mr = (Wr_ig + up)/a2
        
        P5_ig = P2*( 1 + 2*g2/(g2+1)*(Mr**2 - 1) )
        T5_ig = T2*( 1 + 2*g2/(g2+1)*(Mr**2 - 1) )*( (2 + (g2-1)*Mr**2)/((g2+1)*Mr**2) )       

        
        # set up the equaiton system
        def nsEquations( WrT5P5 ):
            
            Wr, T5, P5 = WrT5P5[0], WrT5P5[1], WrT5P5[2]
            gas2.TPX = T5, P5, X2
            rho5 = gas2.density
            h5 = gas2.enthalpy_mass
            
            # continuity equation:
            conti = rho2*(Wr + up) - rho5*Wr            
            # momentum equation:
            mom = P2 - P5 + rho2*(Wr + up)**2 - rho5*Wr**2
            # energy equation:
            en = h2 + (Wr + up)**2/2 - h5 - Wr**2/2
            
            return [conti, mom, en]
        

        # solve it
        initGuess = np.array([Wr_ig, T5_ig, P5_ig])
        sol = optm.root( nsEquations, initGuess)
        Wr, T5, P5 = sol.x

        # reset to state 2:
        gas2.TPX = T2, P2, X2


        return T5, P5, Wr


    def _calculateState25fromSWS(self, W):

        # conditions after the incident shock
        self.testgas.TPX =  self.T1, self.P1, self.Xtest
        T2, P2, u2 = self._normalshock(self.testgas, W)
        up = W - u2
        
        
        # initial guess for reflected shock speed
        Ms = W/self.c1    
        self.testgas.TPX = self.T1, self.P1, self.Xtest
        g = self.testgas.cp/self.testgas.cv
        C = Ms/(Ms**2 - 1)*( 1 + 2*(g - 1)/(g + 1)**2*(Ms**2 - 1)*(g + 1/Ms**2 ) )**0.5
        sol = 1/(2*C) +( (1/(2*C))**2 + 1 )**0.5
        self.testgas.TPX = T2, P2, self.Xtest
        c2 = self._speedofsound(self.testgas)
        Wr_ig = sol*c2 - up
        
        
        # conditions after the reflected shock
        self.testgas.TPX = T2, P2, self.Xtest
        T5, P5, Wr = self._reflectedshock(self.testgas, up, Wr_ig = Wr_ig)

        # Mr
        self.testgas.TPX = T2, P2, self.Xtest
        c2 = self._speedofsound(self.testgas)
        Mr = (Wr+up)/c2

        # sound speed in state 5
        self.testgas.TPX = T5, P5, self.Xtest
        c5 = self._speedofsound(self.testgas)

        # reset to state 1:
        self.testgas.TPX = self.T1, self.P1, self.Xtest

        # set all the calculated values:
        self._T2 = T2
        self._P2 = P2
        self._T5 = T5
        self._P5 = P5
        self._Wr = Wr
        self._Mr = Mr
        self._up = up
        self._c2 = c2
        self._c5 = c5
        
        return T5, P5 # return this for determineIC...


    def _shockspeed(self, gas1, R4, T4, g4, P4):

        a4 = ( g4*R4*T4)**0.5

        def upMatch(W):
            # up from shock conditions:
            T2, P2, u2 = self._normalshock(gas1, W)
            up = W - u2
            # up from expansion:
            u3 = 2*a4/(g4 -1)*( 1 - (P2/P4)**((g4-1)/(2*g4))  )
            return u3 - up

        W = optm.fsolve( upMatch, 1000 )[0]

        return W

    def _calculateState25fromIC(self, p4, g4, T4, R4):
        
        # incident shock strength
        W = self._shockspeed(self.testgas, R4, T4, g4, p4)
        self._Ws = W
        self._Ms = W/self.c1
        
        # reset to state 1:
        self.testgas.TPX = self.T1, self.P1, self.Xtest

        # perform the calculations
        self._calculateState25fromSWS(W)

    def _availableTestTime(self):
 
        ud = self.c5
        L = self.__drivenLength

        # time when incident shock hits endwall
        t0 = L/self.Ws
        # time when reflected disturbance hits the endwall
        t2 = L*(1./ud + (1./self.Ws + 1./self.Wr)/(1./self.up + 1./self.Wr)*(1./self.up - 1./ud))

        self._testtime = t2-t0
    
    
    def _solve_WsP1_for_T5P5(self, T5, P5):        
        
        self.testgas.TPX = self.T1, ct.one_atm, self.Xtest
        g1 = self.testgas.cp/self.testgas.cv
        
        
        def fun0( Ms ):
            
          f1 = 2*(g1 - 1)*Ms**2 + 3 - g1  
          f2 = (3*g1 - 1)*Ms**2  - 2*(g1 - 1) 
          f3 = (g1 + 1)**2*Ms**2
          
          t5 = self.T1 * f1*f2/f3
          
          return t5 - T5
      
        
        def fun1( WP1 ):

            W, P1 = WP1[0], WP1[1]  
            
            self._P1 = P1
        
            t5, p5 = self._calculateState25fromSWS(W)
            
            resT5 = t5 - T5 
            resP5 = p5 - P5
            
            return [resT5, resP5] # T5, P5
        
                
        # find initial guess with cpg assumption
        
        #sol = optm.root_scalar(fun0, x0 = 3)     
        #Ms_ig = sol.root

        # Use Newton’s method with a fallback to Brent
        try:
            sol = optm.root_scalar(
                fun0, x0=3.0, fprime=None, method="newton", xtol=1e-6, maxiter=50
            )
            if not sol.converged:
                raise RuntimeError
            Ms_ig = sol.root
        except Exception:
            sol = optm.root_scalar(
                fun0, bracket=[1.01, 30.0], method="brentq", xtol=1e-6, maxiter=100
            )
            Ms_ig = sol.root        
               
        
        
        f1 = (2*g1*Ms_ig**2 - (g1 - 1))/(g1 + 1) 
        f2 = (-2*(g1 - 1) + Ms_ig**2*(3*g1 -1))/(2 + Ms_ig**2*(g1 - 1))
        P1_ig = P5/f1/f2
        # print('CPG', Ms_ig, P1_ig)
        
        
        # solve it
        initGuess = np.array( [Ms_ig*self.c1 , P1_ig] ) 
        #sol = optm.root( fun1,  initGuess)
        sol = optm.root(fun1, initGuess, method="hybr")
        if not sol.success:
            raise RuntimeError(
                "Failed to find Ws and P1 for the requested (T5,P5) pair."
            )
        Ws, p1 = sol.x
        self.testgas.TPX = self.T1, p1, self.Xtest
        
        return Ws, p1
    
    def _determineICforState5_performanceCurve(self, T5, P5, pc):

        Ws, P1 = self._solve_WsP1_for_T5P5(T5, P5)
        
        Ms = Ws/self.c1
        self._Ws = Ws
        self._Ms = Ms

        # determine p4/p1 through performance curve
        P41 = pc(Ms)
        
        return P1, P41*P1

    def _determineIdealICforState5(self, T5, P5, g4, T4, R4):

        Ws, P1 = self._solve_WsP1_for_T5P5(T5, P5)
        
        Ms = Ws/self.c1
        self._Ws = Ws
        self._Ms = Ms

        # find p4       
        a4 = ( g4*R4*T4)**0.5        
        P4 = 2**((2*g4)/(-1 + g4)) * self.P2 * (((1 - g4)*((2*a4)/(1 - g4) + self.up))/a4)**(-(2*g4)/(-1 + g4))

        return P1, P4
        