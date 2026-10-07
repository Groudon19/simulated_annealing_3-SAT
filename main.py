import sys
import simulated_annealing
import math

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print('Usage: python main.py <file_path>')
        print('Example: python main.py instance.cnf')
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    num_vars, clauses = simulated_annealing.parse_input_file(file_path)
    
    sa = simulated_annealing.SimulatedAnnealing(
        num_vars=num_vars,
        clauses=clauses,
        alpha=0.95,
        SAmax=1,
        initial_temperature_T0=100,
        final_temperature_TN=0.0001,
        N_iterations=200000,
        flip_probability=0.05
    )
    
    A2 = ((sa.initial_temperature_T0 - sa.final_temperature_TN) * (sa.N_iterations + 1)) / sa.N_iterations
    B2 = sa.initial_temperature_T0 - A2
    A3 = (math.log(sa.initial_temperature_T0 - sa.final_temperature_TN)) / (math.log(sa.N_iterations))
    A8 = (1 / sa.N_iterations) * math.log(sa.initial_temperature_T0 / sa.final_temperature_TN)
    A9 = (1 / (sa.N_iterations ** 2)) * math.log(sa.initial_temperature_T0 / sa.final_temperature_TN)
    
    best_solution, best_objective_value = sa.solve(sa.get_temperature_8, A8, B2)
    
    print("Best solution found:", best_solution)
    print("Number of unsatisfied clauses:", best_objective_value) 