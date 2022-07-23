import multiprocessing

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

def simulation_worker1(sim_tuple):
    '''Takes job index and initial temperature, runs the simulation, and returns ignition delay.
    '''
    temp, idx = sim_tuple
    pressure = 5 * ct.one_atm
    phi = 1.0
    
    # set initial conditions
    gas = ct.Solution('gri30.yaml')
    gas.TP = temp, pressure
    gas.set_equivalence_ratio(phi, fuel='H2', oxidizer={"O2": 1.0, "N2": 3.76})
    
    # create reactor, and the simulation object
    reac = ct.IdealGasConstPressureReactor(gas)
    sim = ct.ReactorNet([reac])
    
    ignition_delay = 0.0
    while sim.time < 1.0:
        sim.step()
        
        if reac.T >= temp + 400.0:
            ignition_delay = sim.time
            break
    
    return {idx: ignition_delay}

if __name__ == '__main__':
    # use all the available threads but 1
    num_threads = multiprocessing.cpu_count() - 1

    temperatures = np.linspace(1000, 2000, 15)
    ignition_delays = np.zeros_like(temperatures)

    # create list of jobs, each with a tuple of inputs
    simulations = []
    for idx, temp in enumerate(temperatures):
        simulations.append([temp, idx])
    jobs = tuple(simulations)

    # create pool of workers and apply worker function to this
    pool = multiprocessing.Pool(processes=num_threads)
    results = pool.map(simulation_worker1, jobs)
    pool.close()
    pool.join()

    results = {key:val for k in results for key, val in k.items()}
    ignition_delays = np.zeros(len(results))
    for idx, ignition_delay in results.items():
        ignition_delays[idx] = ignition_delay

    plt.semilogy(1000/temperatures, ignition_delays, 'o')
    plt.xlabel('1000/T (1/K)')
    plt.ylabel('Ignition delay (s)')
    plt.show()
