# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 14:02:16 2025

@author: trefr
first test no airvalues
"""

import cantera as ct
import matplotlib.pyplot as plt


#intial conditions
#=============================
gas = ct.Solution('gri30.yaml')

# pressure = 60 Torr, T = 770 K
p = 60.0*133.3
t = 300
vdot = 10;
gas.TPX = t, p, 'CH4:1, O2:0.21, N2:0.78, AR:0.01'
mdot = gas.density * vdot  # kg/s


#creation of outlet reservoir
#============================
downstream = ct.Reservoir(gas)

#creation of igniter
#============================
igniter_gas = ct.Solution('gri30.yaml')
igniter_gas.TPX = 2000, ct.one_atm, 'CH4:1, O2:2'
igniter_reactor = ct.IdealGasReactor(igniter_gas)
mdoti = .5

upstream = ct.Reservoir(gas)
#creation of PZ reactor
#============================
Pz = ct.IdealGasConstPressureReactor(gas)
Pz.volume = .5

#creation of SZ reactor
#============================
Sz = ct.IdealGasConstPressureReactor(gas)
Sz.volume = .5

#creation of DZ rreactor
#============================
Dz = ct.IdealGasConstPressureReactor(gas)
Dz.volume = .1

#creation of outlet reservoir
#============================
downstream = ct.Reservoir(gas)

#Air Reservoir
#===========================

#creating the mass flow controllers for the sim connecting the combustion regions
#=====================================================================
ign= ct.MassFlowController(igniter_reactor, Pz, mdot=mdoti)
mfc = ct.MassFlowController(upstream, Pz, mdot=mdot)
mfc1 = ct.MassFlowController(Pz, Sz, mdot=mdot)
mfc2 = ct.MassFlowController(Sz, Dz, mdot=mdot)
outlet = ct.Valve(Dz, downstream, K=10.0, name="Valve")



#simulation setup and run
#====================================================================
sim = ct.ReactorNet([Pz, Sz, Dz]) 

t_end = 1.5  # seconds
dt = 0.0001    # time step
time = 0.0

# Time loop
times = []
T_Pz = []
T_Sz = []
T_Dz = []

# Lists to store results
while time < t_end:
    time += dt
    sim.advance(time)
    
    times.append(time)
    T_Pz.append(Pz.T)
    T_Sz.append(Sz.T)
    T_Dz.append(Dz.T)
    
plt.plot(times, T_Pz, label='Pz')
plt.plot(times, T_Sz, label='Sz')
plt.plot(times, T_Dz, label='Dz')

plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.title('Temperature Evolution in Reactors')
plt.legend()
plt.grid(True)
plt.show()    

plt.figure()

plt.plot(times, T_Pz, label='Pz')
plt.plot(times, T_Sz, label='Sz')
plt.plot(times, T_Dz, label='Dz')

plt.xscale('log')  # Set x-axis to log scale
plt.xlim(1e-4, 1.5)  # Set x-axis limits from ~0 to 1 sec, avoiding 0 for log scale

plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.title('Log-Scale Plot from 0 to 1 sec')
plt.grid(True)
plt.show()
