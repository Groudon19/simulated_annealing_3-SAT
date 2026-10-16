import random
import math

def parse_input_file(file_path):
    num_vars = 0
    clauses = []
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            if not line or line.startswith('c') or line.startswith('%') or line == '0':
                continue
            
            if line.startswith('p cnf'):
                parts = line.split()
                num_vars = int(parts[2])
                continue
            
            clause = [int(var) for var in line.split() if var != '']
            if clause:
                if clause[-1] == 0:
                    clause.pop()
                clauses.append(clause)
                
    return num_vars, clauses
            

class SimulatedAnnealing:
    
    def __init__(
        self,
        num_vars,
        clauses,
        SAmax, 
        initial_temperature_T0,
        final_temperature_TN,
        eval_max,
        flip_probability
        ):
        
        self.SAmax = SAmax
        self.initial_temperature_T0 = initial_temperature_T0
        self.final_temperature_TN = final_temperature_TN
        self.num_vars = num_vars
        self.clauses = clauses
        self.flip_probability = flip_probability
        self.eval_max = eval_max
        
        self.N_iterations = max(1, self.eval_max // self.SAmax) 
        
        self.var_to_clauses = [[] for _ in range(num_vars)]
        for clause_idx, clause in enumerate(clauses):
            for var in clause:
                is_positive = var > 0
                self.var_to_clauses[abs(var) - 1].append((clause_idx, is_positive))
        
        # Fixamos o número de flips em num_vars*flip_probability, para melhorar eficiência, 
        # ao invés de percorrer toda a solução e decidir aleatoriamente se vai flipar ou não
        self.base_flips = max(1, int(self.flip_probability * self.num_vars))
        
        self.history = []
        self.history_best = []
        
    def generate_initial_solution(self, num_vars):
        return [random.choice([0, 1]) for _ in range(num_vars)]
    
    # # Por algum motivo esse método faz o algoritmo dar soluções piores também, além de ser mais lento
    # def generate_neighbor(self, solution):
    #     neighbor = solution.copy()
        
    #     for i in range(self.num_vars):
    #         if random.random() < self.flip_probability:
    #             neighbor[i] = 1 - neighbor[i]
                
    #     return neighbor
    
    # def generate_neighbor(self, solution):
    #     neighbor = solution.copy()
        
    #     # Fixamos o número de flips em num_vars*flip_probability, para melhorar eficiência, 
    #     # ao invés de percorrer toda a solução e decidir aleatoriamente se vai flipar ou não
    #     num_flips = max(1, int(self.flip_probability * self.num_vars))
    #     # Trás uma variação para o número de flips, com o objetivo de explorar distâncias de Hamming ímpares
    #     num_flips = num_flips + random.choice([-1, 0])
    #     num_flips = min(max(num_flips, 1), self.num_vars)
        
    #     idxs_to_flip = random.sample(range(self.num_vars), num_flips)
        
    #     for idx in idxs_to_flip:
    #         neighbor[idx] = 1 - neighbor[idx]
            
    #     return neighbor
    
    def generate_flip_indices(self):
        # Trás uma variação para o número de flips, com o objetivo de explorar distâncias de Hamming ímpares
        num_flips = self.base_flips + random.choice([0, 1])
        num_flips = min(max(num_flips, 1), self.num_vars)
        
        return random.sample(range(self.num_vars), num_flips)
       
    def evaluate_objective_function(self, solution):
        unsatisfied_count = 0
        
        for clause in self.clauses:
            satisfied = False
            
            for var in clause:
                var_index = abs(var) - 1 # Isso pq as cláusulas começam em 1, e podem ser negativas pra representar negação
                var_value = solution[var_index]
                
                # Se a variável for positiva e verdadeira, ou se for negativa e falsa, a varável é verdadeira
                if (var > 0 and var_value == 1) or (var < 0 and var_value == 0):
                    # Como dentro de uma cláusula só tem OR, se uma variável for verdadeira, a cláusula é verdadeira
                    satisfied = True
                    break
            
            if not satisfied:
                unsatisfied_count += 1
                
        return unsatisfied_count
    
    def compute_true_counts(self, solution):
        true_counts = [0] * len(self.clauses)
        unsatisfied_count = 0
        
        for clause_idx, clause in enumerate(self.clauses):
            count = 0
            for var in clause:
                if (var > 0) == (solution[abs(var) - 1] == 1):
                    count += 1
            true_counts[clause_idx] = count
            if count == 0:
                unsatisfied_count += 1
                
        return true_counts, unsatisfied_count
    
    def flip(self, solution, true_counts, var, unsatisfied_count):
        
        was_true = solution[var] == 1
        
        for clause_idx, is_positive in self.var_to_clauses[var]:
            if is_positive == was_true:
                # Era verdadeira, agr virou falsa
                true_counts[clause_idx] -= 1
                if true_counts[clause_idx] == 0:
                    unsatisfied_count += 1
            
            else:
                # Era false, agr virou verdadeira
                if true_counts[clause_idx] == 0:
                    unsatisfied_count -= 1
                true_counts[clause_idx] += 1
                                    
        solution[var] = 1 - solution[var]
        
        return unsatisfied_count
        
    def get_temperature_0(self, i, A, B):
        return self.initial_temperature_T0 - i * ((self.initial_temperature_T0 - self.final_temperature_TN) / self.N_iterations)
    
    def get_temperature_1(self, i, A, B):
        return self.initial_temperature_T0 * (self.final_temperature_TN / self.initial_temperature_T0) ** (i / self.N_iterations)
    
    def get_temperature_2(self, i, A, B):
        return (A / (i + 1)) + B
    
    def get_temperature_3(self, i, A, B):
        return self.initial_temperature_T0 - i ** A
        
    def get_temperature_4(self, i, A, B):
        progress = i / self.N_iterations
        start = 1 / (1 + math.exp(-1.5))
        end = 1 / (1 + math.exp(1.5))
        value = 1 / (1 + math.exp(3 * (progress - 0.5)))
        scale = (value - end) / (start - end)
        return self.final_temperature_TN + (self.initial_temperature_T0 - self.final_temperature_TN) * scale
        
    def get_temperature_5(self, i, A, B):
        return (1/2) * (self.initial_temperature_T0 - self.final_temperature_TN) * (1 + math.cos(i * math.pi / self.N_iterations)) + self.final_temperature_TN
        
    def get_temperature_6(self, i, A, B):
        return (1/2) * (self.initial_temperature_T0 - self.final_temperature_TN) * (1 - math.tanh((10 * i / self.N_iterations) - 5)) + self.final_temperature_TN
        
    def get_temperature_7(self, i, A, B):
        return ((self.initial_temperature_T0 - self.final_temperature_TN) / (math.cosh((10 * i) / self.N_iterations))) + self.final_temperature_TN
        
    def get_temperature_8(self, i, A, B):
        return self.initial_temperature_T0 * math.exp(-A * i)
        
    def get_temperature_9(self, i, A, B):
        return self.initial_temperature_T0 * math.exp(-A * i ** 2)
    
    def get_cooling_parameters(self, schedule_number):
        T0, TN, N = self.initial_temperature_T0, self.final_temperature_TN, self.N_iterations
        if schedule_number == 2:
            A = (T0 - TN) * (N + 1) / N
            return A, T0 - A
        if schedule_number == 3:
            return math.log(T0 - TN) / math.log(N), 0
        if schedule_number == 8:
            return math.log(T0 / TN) / N, 0
        if schedule_number == 9:
            return math.log(T0 / TN) / N**2, 0
        return 0, 0
    
    def solve(self, cooling_schedule):
        get_temperature = getattr(self, f"get_temperature_{cooling_schedule}")
        A, B = self.get_cooling_parameters(cooling_schedule)
        
        self.history = [0] * (self.eval_max + 1)
        self.history_best = [0] * (self.eval_max + 1)
        
        current_solution = self.generate_initial_solution(self.num_vars)
        true_counts, current_objective_value = self.compute_true_counts(current_solution)
                
        self.history[0] = current_objective_value
        
        best_solution = current_solution.copy()
        best_objective_value = current_objective_value
        
        self.history_best[0] = best_objective_value
        
        history_idx = 1
        
        for i in range(self.N_iterations):
            current_temperature = get_temperature(i, A, B)
            
            for _ in range(self.SAmax):
                idxs_to_flip = self.generate_flip_indices()
                neighbor_objective_value = current_objective_value
                for var in idxs_to_flip:
                    neighbor_objective_value = self.flip(current_solution, true_counts, var, neighbor_objective_value)
                
                delta = neighbor_objective_value - current_objective_value
                
                if delta < 0 or random.random() < math.exp(-delta / current_temperature):
                    current_objective_value = neighbor_objective_value
                    
                    if current_objective_value < best_objective_value:
                        best_solution = current_solution.copy()
                        best_objective_value = current_objective_value
                        
                else:
                    for var in idxs_to_flip:
                        self.flip(current_solution, true_counts, var, neighbor_objective_value)
                
                self.history[history_idx] = current_objective_value
                self.history_best[history_idx] = best_objective_value
                history_idx += 1

        assert self.evaluate_objective_function(best_solution) == best_objective_value
            
        return best_solution, best_objective_value, self.history, self.history_best
        
        