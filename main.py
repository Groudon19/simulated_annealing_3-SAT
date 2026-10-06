import sys
import simulated_annealing

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
        flip_probability=0.05
    )
    
    best_solution, best_objective_value = sa.solve()
    
    print("Best solution found:", best_solution)
    print("Number of unsatisfied clauses:", best_objective_value) 