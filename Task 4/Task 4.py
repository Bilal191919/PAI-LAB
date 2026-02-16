import random

# 1. Backtracking Algorithm

def run_backtracking(n):
    print(f"\n--- Running Backtracking for N={n} ---")
    board = [-1] * n  
    solutions = []

    def is_safe(row, col):
        for prev_row in range(row):
            if board[prev_row] == col or \
               abs(board[prev_row] - col) == abs(prev_row - row):
                return False
        return True

    def solve(row):
        if row == n:
            solutions.append(list(board))
            return True  
        
        for col in range(n):
            if is_safe(row, col):
                board[row] = col
                if solve(row + 1):
                    return True
        return False

    if solve(0):
        print_board(board)
    else:
        print("No solution found using Backtracking.")


# 2. Hill Climbing (Local Search)

def run_hill_climbing(n):
    print(f"\n--- Running Hill Climbing for N={n} ---")
    
   
    board = [random.randint(0, n-1) for _ in range(n)]
    
    def count_conflicts(current_board):
        conflicts = 0
        for i in range(n):
            for j in range(i + 1, n):
                if current_board[i] == current_board[j] or \
                   abs(current_board[i] - current_board[j]) == abs(i - j):
                    conflicts += 1
        return conflicts

    current_conflicts = count_conflicts(board)
    steps = 0
    max_steps = 1000  

    while current_conflicts > 0 and steps < max_steps:
        steps += 1
        best_neighbor = list(board)
        min_conflicts = current_conflicts
        

        found_better = False
        for row in range(n):
            original_col = board[row]
            for col in range(n):
                if col != original_col:
                    board[row] = col
                    new_conflicts = count_conflicts(board)
                    if new_conflicts < min_conflicts:
                        min_conflicts = new_conflicts
                        best_neighbor = list(board)
                        found_better = True
                    board[row] = original_col 
            
            if found_better:
                break 
        
        if not found_better:
   
            print("Stuck at local optimum. Restarting...")
            board = [random.randint(0, n-1) for _ in range(n)]
            current_conflicts = count_conflicts(board)
        else:
            board = best_neighbor
            current_conflicts = min_conflicts
            
    if current_conflicts == 0:
        print(f"Solution found in {steps} steps!")
        print_board(board)
    else:
        print("Could not find a solution within step limit.")

# 3. Genetic Algorithm

def run_genetic_algorithm(n):
    print(f"\n--- Running Genetic Algorithm for N={n} ---")
    population_size = 100
    generations = 1000
    mutation_rate = 0.1

    def create_individual():
        return [random.randint(0, n-1) for _ in range(n)]

    def fitness(individual):
      
        conflicts = 0
        for i in range(n):
            for j in range(i + 1, n):
                if individual[i] == individual[j] or \
                   abs(individual[i] - individual[j]) == abs(i - j):
                    conflicts += 1
        return (n * (n - 1)) // 2 - conflicts

    population = [create_individual() for _ in range(population_size)]
    max_fitness = (n * (n - 1)) // 2

    for gen in range(generations):
        population.sort(key=fitness, reverse=True)
        
        if fitness(population[0]) == max_fitness:
            print(f"Solution found in generation {gen}!")
            print_board(population[0])
            return

        
        new_population = population[:population_size // 2]
        
     
        while len(new_population) < population_size:
            parent1 = random.choice(new_population)
            parent2 = random.choice(new_population)
            
           
            cut = random.randint(1, n - 1)
            child = parent1[:cut] + parent2[cut:]
            
          
            if random.random() < mutation_rate:
                child[random.randint(0, n - 1)] = random.randint(0, n - 1)
                
            new_population.append(child)
            
        population = new_population

    print("Genetic Algorithm finished without a perfect solution.")
    print("Best solution found:")
    print_board(population[0])


def print_board(board):
    n = len(board)
    for i in range(n):
        row = ['.'] * n
        row[board[i]] = 'Q'
        print(' '.join(row))
    print(f"Board Representation: {board}")


def main():
    while True:
        try:
            print("\n=== N-Queens Solver ===")
            n_input = input("Enter N (number of queens, or 'q' to quit): ")
            if n_input.lower() == 'q':
                break
            n = int(n_input)
            if n < 4:
                print("Size too small for interesting solutions (try >= 4).")
                continue
            
            print("\nSelect Algorithm:")
            print("1. Backtracking")
            print("2. Hill Climbing")
            print("3. Genetic Algorithm")
            choice = input("Enter choice (1-3): ")

            if choice == '1':
                run_backtracking(n)
            elif choice == '2':
                run_hill_climbing(n)
            elif choice == '3':
                run_genetic_algorithm(n)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()
