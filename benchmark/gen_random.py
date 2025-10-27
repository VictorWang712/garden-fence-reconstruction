import random
import os

def gen_case(n, m, min_connectors=2, max_connectors=30, min_edges=1, max_edges=100):
    positions = [(i, j) for i in range(n) for j in range(m)] # Generate all possible grid positions 
    random.shuffle(positions) # Shuffle the positions randomly 
    num_connectors = random.randint(min_connectors, min(max_connectors, n*m//2)) # Randomly determine number of connectors 
    connectors = positions[:num_connectors] # Select the first num_connectors as connector positions 
    connectors_set = set(connectors) # Create a set for fast lookup of connectors 
    deg = {pos: 0 for pos in connectors} # Initialize degree for each connector as 0 
    grid = [[0 for _ in range(m)] for _ in range(n)] # Create an n x m grid filled with 0 
    for (i, j) in connectors:
        grid[i][j] = 1 # Mark connector positions with 1 initially 
    dir_map = {pos: [0,0,0,0] for pos in connectors} # Track used directions for each connector: up, down, left, right 
    fence_grid = [[0 for _ in range(m)] for _ in range(n)] # Track occupation of non-connector cells: 0=none, 1=vertical, 2=horizontal 
    def can_link(a, b): # Check if two connectors can be linked directly 
        (x1, y1), (x2, y2) = a, b # Unpack positions 
        if x1 == x2: # Same row: horizontal link 
            if abs(y1-y2) < 2: # Must have at least one cell between 
                return False 
            step = 1 if y2 > y1 else -1 # Determine direction 
            for y in range(y1+step, y2, step): # Check all cells between a and b 
                if (x1, y) in connectors_set: # Cannot cross another connector 
                    return False 
                if fence_grid[x1][y] not in (0,2): # Cannot cross vertical fence 
                    return False 
            return True 
        elif y1 == y2: # Same column: vertical link 
            if abs(x1-x2) < 2: # Must have at least one cell between 
                return False 
            step = 1 if x2 > x1 else -1 # Determine direction 
            for x in range(x1+step, x2, step): # Check all cells between a and b 
                if (x, y1) in connectors_set: # Cannot cross another connector 
                    return False 
                if fence_grid[x][y1] not in (0,1): # Cannot cross horizontal fence 
                    return False 
            return True 
        else: # Not aligned horizontally or vertically 
            return False 
    edges = [] # Store all valid edges 
    tries = 0 # Count failed attempts 
    max_try = 2000 # Maximum attempts to add an edge 
    while len(edges) < max_edges and tries < max_try: # Try to add up to max_edges 
        a, b = random.sample(connectors, 2) # Randomly pick two connectors 
        if deg[a] >= 4 or deg[b] >= 4: # Each connector can have at most 4 edges 
            tries += 1 
            continue 
        if not can_link(a, b): # Check if a and b can be linked 
            tries += 1 
            continue 
        x1, y1 = a # Unpack a 
        x2, y2 = b # Unpack b 
        if x1 == x2: # Horizontal 
            d1 = 3 if y2 > y1 else 2 # Direction for a: right or left 
            d2 = 2 if y2 > y1 else 3 # Direction for b: left or right 
        else: # Vertical 
            d1 = 1 if x2 > x1 else 0 # Direction for a: down or up 
            d2 = 0 if x2 > x1 else 1 # Direction for b: up or down 
        if dir_map[a][d1] or dir_map[b][d2]: # Check if direction already used 
            tries += 1 
            continue 
        if x1 == x2: # Mark horizontal fence 
            step = 1 if y2 > y1 else -1 
            for y in range(y1+step, y2, step): 
                fence_grid[x1][y] = 2 # Mark as horizontal fence 
        else: # Mark vertical fence 
            step = 1 if x2 > x1 else -1 
            for x in range(x1+step, x2, step): 
                fence_grid[x][y1] = 1 # Mark as vertical fence 
        deg[a] += 1 # Increase degree for a 
        deg[b] += 1 # Increase degree for b 
        dir_map[a][d1] = 1 # Mark direction as used for a 
        dir_map[b][d2] = 1 # Mark direction as used for b 
        edges.append((a, b)) # Add edge to list 
        tries = 0 # Reset tries after successful edge 
    for (i, j) in connectors: # Update grid with final degree for each connector 
        grid[i][j] = sum(dir_map[(i,j)]) 
    for (i, j) in connectors: # Remove isolated connectors (degree 0) 
        if grid[i][j] == 0: 
            grid[i][j] = 0 
    connector_count = sum(1 for (i, j) in connectors if grid[i][j] > 0) # Count non-isolated connectors 
    if connector_count < 2: # Ensure at least two connectors are not isolated 
        return gen_case(n, m, min_connectors, max_connectors, min_edges, max_edges) # Retry recursively 
    return grid # Return the generated grid 

def save_case(grid, path):
    n = len(grid) # Number of rows 
    m = len(grid[0]) # Number of columns 
    with open(path, 'w') as f: # Open file for writing 
        f.write(f"{n} {m}\n") # Write grid size 
        for row in grid: # Write each row 
            f.write(' '.join(str(x) for x in row) + '\n') # Write row values separated by spaces 

def main():
    random.seed(42)
    outdir = "../data/input/random"
    os.makedirs(outdir, exist_ok=True)
    for idx in range(10):
        n = random.randint(2, 50)
        m = random.randint(2, 50)
        grid = gen_case(n, m)
        save_case(grid, f"{outdir}/{idx}.in")

if __name__ == "__main__":
    main()
