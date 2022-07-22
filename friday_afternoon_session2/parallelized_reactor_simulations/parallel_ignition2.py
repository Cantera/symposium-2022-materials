from typing import NamedTuple, Dict
import multiprocessing

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

class Input(NamedTuple):
    """Holds input parameters for a single autoignition case.
    """
    model_file: str
    temperature: float
    pressure: float
    equivalence_ratio: float = 1.0
    fuel: Dict = {}
    oxidizer: Dict = {}
    end_time: float = 1.0

class Simulation(object):
    def __init__(self, properties):
        '''Initialize constant-pressure autoignition simulation.
        '''
        self.gas = ct.Solution(properties.model_file)
        self.gas.TP = properties.temperature, properties.pressure
        self.gas.set_equivalence_ratio(
            properties.equivalence_ratio, properties.fuel, properties.oxidizer
            )
        
        self.reac = ct.IdealGasConstPressureReactor(self.gas)
        self.sim = ct.ReactorNet([self.reac])
        
        self.initial_temperature = properties.temperature
        self.ignition_delay = 0.0
        self.end_time = properties.end_time
    
    def run_case(self):
        '''Runs autoignition simulation.
        '''
        while self.sim.time < 1.0:
            self.sim.step()

            if self.reac.T >= self.initial_temperature + 400.0:
                self.ignition_delay = self.sim.time
                break

def simulation_worker2(inp_tuple):
    '''Takes job index and inputs, runs the simulation, and returns ignition delay.
    '''
    idx, inputs = inp_tuple
    sim = Simulation(inputs)
    sim.run_case()
    
    return {idx: sim.ignition_delay}

if __name__ == '__main__':
    # use all the available threads but 1
    num_threads = multiprocessing.cpu_count() - 1

    temperatures = np.linspace(1000, 2000, 15)

    pressure = 5 * ct.one_atm

    # create list of jobs, each with a tuple of inputs
    inputs = []
    for idx, temp in enumerate(temperatures):
        inputs.append([idx, Input(
            'gri30.yaml', temp, pressure, 1.0, {'H2': 1.0}, 
            {'O2': 1.0, 'N2': 3.76}, 1.0
            )])
    jobs = tuple(inputs)

    # create pool of workers and apply worker function to this
    pool = multiprocessing.Pool(processes=num_threads)
    results = pool.map(simulation_worker2, jobs)
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
