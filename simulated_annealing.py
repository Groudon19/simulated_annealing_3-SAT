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
        N_iterations,
        flip_probability=0.05
        ):
        
        self.SAmax = SAmax
        self.initial_temperature_T0 = initial_temperature_T0
        self.final_temperature_TN = final_temperature_TN
        self.num_vars = num_vars
        self.clauses = clauses
        self.flip_probability = flip_probability
        self.N_iterations = N_iterations
        
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
    
    def generate_neighbor(self, solution):
        neighbor = solution.copy()
        
        # Fixamos o número de flips em num_vars*flip_probability, para melhorar eficiência, 
        # ao invés de percorrer toda a solução e decidir aleatoriamente se vai flipar ou não
        num_flips = max(1, int(self.flip_probability * self.num_vars))
        idxs_to_flip = random.sample(range(self.num_vars), num_flips)
        
        for idx in idxs_to_flip:
            neighbor[idx] = 1 - neighbor[idx]
            
        return neighbor
       
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
    
    def solve(self, get_temperature, A, B):
        self.history = []
        self.history_best = []
        
        current_solution = self.generate_initial_solution(self.num_vars)
        current_objective_value = self.evaluate_objective_function(current_solution)
        
        self.history.append(current_objective_value)
        
        best_solution = current_solution.copy()
        best_objective_value = current_objective_value
        
        self.history_best.append(best_objective_value)
        
        current_temperature = self.initial_temperature_T0
        
        for i in range(self.N_iterations):
            current_temperature = get_temperature(i, A, B)
            
            self.history.append(current_objective_value)
            self.history_best.append(best_objective_value)
            
            for _ in range(self.SAmax):
                neighbor_solution = self.generate_neighbor(current_solution)
                neighbor_objective_value = self.evaluate_objective_function(neighbor_solution)
                
                delta = neighbor_objective_value - current_objective_value
                
                if delta < 0:
                    current_solution = neighbor_solution
                    current_objective_value = neighbor_objective_value
                    
                    if neighbor_objective_value < best_objective_value:
                        best_solution = neighbor_solution
                        best_objective_value = neighbor_objective_value
                else:
                    if random.random() < math.exp(-delta / current_temperature):
                        current_solution = neighbor_solution
                        current_objective_value = neighbor_objective_value

            
        return best_solution, best_objective_value, self.history, self.history_best
        
        