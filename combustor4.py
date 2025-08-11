# -*- coding: utf-8 -*-
"""
Created on Sun Aug 10 15:31:37 2025

@author: trefr
"""

import cantera as ct
import matplotlib.pyplot as plt
import math

#intial conditions
#Combustor Geometry
#=============================
Area = .18
Length = .063


#Gas Properties
#=============================
gas = ct.Solution('gri30.yaml')

# pressure = 60 Torr, T = 770 K
p = ct.one_atm*9.67
t = 680
vdot = 10
gas.TPX = t, p, 'CH4:1'
mdot = 17.35
#gas.density * vdot *Area # kg/s

#air
gas_a = ct.Solution('air.yaml')
gas_a.TPX = 680, p, 'O2:0.21, N2:0.78, AR:0.01'
rho_a = gas_a.density

#mix
mix = ct.Solution('gri30.yaml')
pm = ct.one_atm*3
t = 300
vdot = 10
mix.TPX = t, pm*3, 'CH4:1.0, O2:2.0, N2:7.52'


def fuel_mdot(t):
    """Create an inlet for the fuel, supplied as a Gaussian pulse"""
    total = mdot # mass of fuel [kg]
    width = .5 # width of the pulse [s]
    t0 = .1  # time of fuel pulse peak [s]
      
    amplitude = total / (width * math.sqrt(2*math.pi))
    return amplitude * math.exp(-(t-t0)**2 / (2*width**2))


#igniter
igniter_gas = ct.Solution('h2o2.yaml')
igniter_gas.TPX = 2000, ct.one_atm, 'H2:1'




#creation of inlet reservoir
#============================
upstream = ct.Reservoir(gas)

#creation of igniter
#============================
igniter_reactor = ct.Reservoir(igniter_gas)

#creation of PZ reactor
#============================
Pz = ct.IdealGasReactor(mix)
Pz.volume = Area*Length

#creation of SZ reactor
#============================
Sz = ct.IdealGasReactor(mix)
Sz.volume = Area*Length

#creation of DZ rreactor
#============================
Dz = ct.IdealGasReactor(mix)
Dz.volume = Area*Length

#creation of outlet reservoir
#============================
gas_downstream = ct.Solution('gri30.yaml')
pex= p*.95
gas_downstream.TPX = Dz.thermo.T, pex, Dz.thermo.X
downstream = ct.Reservoir(gas_downstream)

#Air Reservoir
#===========================
Air = ct.Reservoir(gas_a)

#Mass flow calculations
#===========================
mdota = mdot*65
def mdot1(t):
    return fuel_mdot(t) + mdot + mdota*0.2
def mdot2(t):
    return mdot1(t) + mdota*0.3 #for reservoir 2-3
#finalm = mdot + 3*mdota + mdoti

#creating the mass flow controllers for the sim connecting the combustion regions
#=====================================================================
#ignition mass flow
ign= ct.MassFlowController(igniter_reactor, Pz,mdot = fuel_mdot)

#reactor connections up=Pz=Sz=Dz=Out
mfc = ct.MassFlowController(upstream, Pz, mdot=mdot)
mfc1 = ct.MassFlowController(Pz, Sz, mdot=mdot1)
mfc2 = ct.MassFlowController(Sz, Dz, mdot=mdot2)
outlet = ct.Valve(Dz, downstream,K=10)

#air connections
a1 = ct.MassFlowController(Air, Pz, mdot = 0.2*mdota)
a2 = ct.MassFlowController(Air, Sz, mdot = 0.3*mdota)
a3 = ct.MassFlowController(Air, Dz, mdot = 0.5*mdota)


#simulation setup and run
#====================================================================

sim = ct.ReactorNet([Pz, Sz, Dz]) 

t_end = 10  # seconds
dt = 0.0001    # time step
time = 0.0

   
# Time loop
times = []
T_Pz = []
T_Sz = []
T_Dz = []

m_Pz = []
m_Sz = []
m_Dz = []

p_Pz = []
p_Sz = []
p_Dz = []
# Lists to store results
while time < t_end:
    
            
       
    time += dt
    sim.advance(time)
    
    #time storage
    times.append(time)
    T_Pz.append(Pz.T)
    T_Sz.append(Sz.T)
    T_Dz.append(Dz.T)
    
    p_Pz.append(Pz.thermo.P)
    p_Sz.append(Sz.thermo.P)
    p_Dz.append(Dz.thermo.P)

    
    m_Pz.append(mfc.mass_flow_rate)
    m_Sz.append(mfc1.mass_flow_rate)
    m_Dz.append(mfc2.mass_flow_rate)
    #species storage
    species_aliases = {
        'o2': 'O$_2$',
        'h2o': 'H$_2$O',

        'co2': 'CO$_2$',
        'h2': 'H$_2$',
        'ch4': 'CH$_4$'
    }
    species_data = {s: [] for s in species_aliases.keys()}
    
    
#plotting and output display
#===============================
#normal graph for temp and time
plt.plot(times, T_Pz, label='Pz')
plt.plot(times, T_Sz, label='Sz')
plt.plot(times, T_Dz, label='Dz')

plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.title('Temperature Evolution in Reactors')
plt.legend()
plt.grid(True)
plt.show()    

#log for temp
plt.figure()

plt.plot(times, T_Pz, label='Pz')
plt.plot(times, T_Sz, label='Sz')
plt.plot(times, T_Dz, label='Dz')

plt.xscale('log')  # Set x-axis to log scale
plt.xlim(1e-4, 1.5)  # Set x-axis limits from ~0 to 1 sec, avoiding 0 for log scale

plt.xlabel('Time (s)')
plt.ylabel('Amplitude T')
plt.legend()
plt.title('Log-Scale Plot from 0 to 1 sec')
plt.grid(True)
plt.show()

#normal graph for temp and time
plt.plot(times, m_Pz, label='Pz')
plt.plot(times, m_Sz, label='Sz')
plt.plot(times, m_Dz, label='Dz')

plt.xlabel('Time (s)')
plt.ylabel('Mass Flow (kg/s)')
plt.title('Mass Flow Evolution in Reactors')
plt.legend()
plt.grid(True)
plt.show()    

#log for temp
print('Mass flow each section')
print("igniter hydrogen:",fuel_mdot(2))
print("for mass flow to the section",mdot1)

target_time = 10.0
index = int(target_time / dt)

print('Mass flow at exit',m_Dz[index])
print('Temp at exit',T_Dz[index])
print('Pressure at exit',p_Dz[index])

#Species Calculations
#========================
# nice names for species, including PAH species that can be considered
# as precursors to soot formation