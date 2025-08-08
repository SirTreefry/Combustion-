# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 17:28:10 2025

@author: Andrew Trefry
 Jet engine combustor
 second test no chnages in mass flow
"""



import cantera as ct
import matplotlib.pyplot as plt
import math

#intial conditions
#Combustor Geometry
#=============================
Area = .1
Length = .2


#Gas Properties
#=============================
gas = ct.Solution('gri30.yaml')

# pressure = 60 Torr, T = 770 K
p = ct.one_atm*6
t = 600
vdot = 10
gas.TPX = t, p, 'CH4:1'
mdot = gas.density * vdot *Area # kg/s

#air
p = ct.one_atm*3
gas_a = ct.Solution('air.yaml')
gas_a.TPX = 600, ct.one_atm, 'O2:0.21, N2:0.78, AR:0.01'
rho_a = gas_a.density

def fuel_mdot(t):
    """Create an inlet for the fuel, supplied as a Gaussian pulse"""
    total = mdot  # mass of fuel [kg]
    width = .3 # width of the pulse [s]
    t0 = 2  # time of fuel pulse peak [s]
      
    amplitude = total / (width * math.sqrt(2*math.pi))
    return amplitude * math.exp(-(t-t0)**2 / (2*width**2))


#igniter
igniter_gas = ct.Solution('gri30.yaml')
igniter_gas.TPX = 3000, ct.one_atm, 'CH4:1'
mdoti = fuel_mdot(2)

#creation of outlet reservoir
#============================
downstream = ct.Reservoir(gas)

#creation of inlet reservoir
#============================
upstream = ct.Reservoir(gas)

#creation of igniter
#============================
igniter_reactor = ct.IdealGasReactor(igniter_gas)

#creation of PZ reactor
#============================
Pz = ct.IdealGasConstPressureReactor(gas)
Pz.volume = Area*Length

#creation of SZ reactor
#============================
Sz = ct.IdealGasConstPressureReactor(gas)
Sz.volume = Area*Length

#creation of DZ rreactor
#============================
Dz = ct.IdealGasConstPressureReactor(gas)
Dz.volume = Area*Length


#Air Reservoir
#===========================
Air = ct.Reservoir(gas)

#Mass flow calculations
#===========================
mdota = gas_a.density * vdot *Area
mdot1 = mdot + mdota + mdoti
mdot2 = mdot + 2*mdota + mdoti #for reservoir 2-3
finalm = mdot + 3*mdota + mdoti
#creating the mass flow controllers for the sim connecting the combustion regions
#=====================================================================
#ignition mass flow
ign= ct.MassFlowController(igniter_reactor, Pz,mdot = mdoti)

#reactor connections
mfc = ct.MassFlowController(upstream, Pz, mdot=mdot)
mfc1 = ct.MassFlowController(Pz, Sz, mdot=mdot1)
mfc2 = ct.MassFlowController(Sz, Dz, mdot=mdot2)
outlet = ct.Valve(Dz, downstream, K=10.0, name="Valve")

#air connections
a1 = ct.MassFlowController(Air, Pz, mdot = mdota)
a2 = ct.MassFlowController(Air, Sz, mdot = mdota)
a3 = ct.MassFlowController(Air, Dz, mdot = mdota)


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
print("igniter hydrogen:",mdoti)
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

