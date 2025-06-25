# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 10:20:57 2025

@author: trefr
"""
import numpy as np
import matplotlib.pyplot as plt
import cantera as ct

# Define gas mixture and initial conditions
gas = ct.Solution('gri30.yaml')
gas.TPX = 1000.0, ct.one_atm, 'CH4:0.05, O2:0.21, N2:0.74'

# Inlet and outlet reservoirs
inlet = ct.Reservoir(gas)
outlet = ct.Reservoir(gas)

# Reactor - constant pressure
combustor = ct.ConstantPressureReactor(gas)
combustor.volume = 0.01  # m^3

# Mass flow controller between inlet and combustor
mfc = ct.MassFlowController(inlet, combustor, mdot=0.5)  # kg/s

# Outlet valve
valve = ct.Valve(combustor, outlet)
valve.K = 1.0  # Proportionality constant

# Reactor network
sim = ct.ReactorNet([combustor])

# Time integration
time = 0.0
for n in range(100):
    time += 1e-4
    sim.advance(time)
    print(f"Time: {time:.4f} s, T: {combustor.T:.2f} K, P: {combustor.thermo.P:.2f} Pa")