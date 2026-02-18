def water_jug_dfs(limit1, limit2, goal):
    stack = []
    visited_nodes = []
    
    start_point = (0, 0)
    stack.append((start_point, []))
    
    print(f"Starting process for {limit1}L and {limit2}L jugs to measure {goal}L")
    
    while len(stack) > 0:
        current_state, path = stack.pop()
        x, y = current_state
        
        if x == goal or y == goal:
            print(f"\nTarget {goal}L reached!")
            complete_path = path + [current_state]
            for idx, step in enumerate(complete_path):
                print(f"Step {idx}: {step}")
            return True
            
        if current_state in visited_nodes:
            continue
            
        visited_nodes.append(current_state)
        
        possible_moves = []
        
        if x < limit1:
            possible_moves.append(((limit1, y), path + [current_state]))
            
        if y < limit2:
            possible_moves.append(((x, limit2), path + [current_state]))
            
        if x > 0:
            possible_moves.append(((0, y), path + [current_state]))
            
        if y > 0:
            possible_moves.append(((x, 0), path + [current_state]))
            
        if x > 0 and y < limit2:
            amt = min(x, limit2 - y)
            possible_moves.append(((x - amt, y + amt), path + [current_state]))
            
        if y > 0 and x < limit1:
            amt = min(y, limit1 - x)
            possible_moves.append(((x + amt, y - amt), path + [current_state]))
            
        for move in possible_moves:
            state, p = move
            if state not in visited_nodes:
                stack.append((state, p))
                
    print("Solution not found")
    return False

j1 = 4
j2 = 3
target = 2
water_jug_dfs(j1, j2, target)
