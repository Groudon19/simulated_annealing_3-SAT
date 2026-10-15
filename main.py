import sys
import simulated_annealing
import time
import math
import matplotlib.pyplot as plt

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print('Usage: python main.py <file_path>')
        print('Example: python main.py instance.cnf')
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    start_time = time.perf_counter()
    
    num_vars, clauses = simulated_annealing.parse_input_file(file_path)
    
    sa = simulated_annealing.SimulatedAnnealing(
        num_vars=num_vars,
        clauses=clauses,
        SAmax=1,
        initial_temperature_T0=100,
        final_temperature_TN=0.0001,
        eval_max=2000000,
        flip_probability=0.05
    )
    
    # O número de input da função solve é o número do método get_temperature utilizado.
    best_solution, best_objective_value, history, history_best = sa.solve(8)
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time}")
    
    print("Best solution found:", best_solution)
    print("Number of unsatisfied clauses:", best_objective_value)
    
    false_clause_ratio = [objective_value / len(clauses) for objective_value in history]
    false_clause_ratio_best = [best_objective_value / len(clauses) for best_objective_value in history_best]
    iterations = range(len(history))

    plt.plot(iterations, false_clause_ratio)
    plt.plot(iterations, false_clause_ratio_best)
    plt.xlabel("Iteration")
    plt.ylabel("False clauses / total clauses")
    plt.ylim(0, 0.3)
    plt.grid(True)
    plt.show()