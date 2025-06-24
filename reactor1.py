# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 18:23:08 2025

@author: trefr
"""

import numpy as np
import matplotlib.pyplot as plt
import cantera as ct

gas = ct.Solution('gri30.yaml', transport_model=None)

equiv_ratio = 0.5  # lean combustion
gas.TP = 300.0, ct.one_atm
gas.set_equivalence_ratio(equiv_ratio, 'CH4:1.0', 'O2:1.0, N2:3.76')
inlet = ct.Reservoir(gas)

gas.equilibrate('HP')
combustor = ct.IdealGasReactor(gas)
combustor.volume = 1.0

exhaust = ct.Reservoir(gas)

def mdot(t):
    return combustor.mass / residence_time

inlet_mfc = ct.MassFlowController(inlet, combustor, mdot=mdot)

outlet_mfc = ct.PressureController(combustor, exhaust, primary=inlet_mfc, K=0.01)

# the simulation only contains one reactor
sim = ct.ReactorNet([combustor])

states = ct.SolutionArray(gas, extra=['tres'])

residence_time = 0.1  # starting residence time
while combustor.T > 500:
    sim.initial_time = 0.0  # reset the integrator
    sim.advance_to_steady_state()
    print('tres = {:.2e}; T = {:.1f}'.format(residence_time, combustor.T))
    states.append(combustor.thermo.state, tres=residence_time)
    residence_time *= 0.9  # decrease the residence time for the next iteration