import random
import os

def gen_case(n, m):
    grid = [[0 for _ in range(m)] for _ in range(n)]
    # Randomly place connectors
    for i in range(n):
        for j in range(m):
            if random.random() < 0.25:
                grid[i][j] = random.randint(1, 4)
    # Ensure at least one connector
    if all(grid[i][j] == 0 for i in range(n) for j in range(m)):
        grid[random.randint(0, n-1)][random.randint(0, m-1)] = random.randint(1, 4)
    return grid

def save_case(grid, path):
    n = len(grid)
    m = len(grid[0])
    with open(path, 'w') as f:
        f.write(f"{n} {m}\n")
        for row in grid:
            f.write(' '.join(str(x) for x in row) + '\n')

def main():
    random.seed(42)
    outdir = "../data/input/random"
    os.makedirs(outdir, exist_ok=True)
    for idx in range(10):
        n = random.randint(2, 8)
        m = random.randint(2, 8)
        grid = gen_case(n, m)
        save_case(grid, f"{outdir}/{idx}.in")

if __name__ == "__main__":
    main()
