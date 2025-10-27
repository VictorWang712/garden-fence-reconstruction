import os
import subprocess
import time
import json

def compile_code():  # Compile the C source code and return the executable path 
    src = "../code/src/restore_fence.c"  # Path to the C source file 
    out = "../code/bin/restore_fence"  # Output binary path 
    cmd = f"gcc {src} -o {out}"  # GCC command to compile the code 
    res = subprocess.run(cmd, shell=True, capture_output=True)  # Run the compilation command 
    if res.returncode != 0:  # Check if compilation failed 
        print("Compilation failed!")  # Print error message if compilation fails 
        print(res.stderr.decode())  # Print the compilation error output 
        exit(1)  # Exit the script with error code 
    return out  # Return the path to the compiled executable 

def run_case(exe, input_path, output_path):  # Run a single test case with the executable 
    with open(input_path, 'r') as fin, open(output_path, 'w') as fout:  # Open input and output files 
        start = time.time()  # Record start time 
        res = subprocess.run([exe], stdin=fin, stdout=fout, stderr=subprocess.PIPE)  # Run the executable with redirected IO 
        end = time.time()  # Record end time 
        elapsed = end - start  # Calculate elapsed time 
    return elapsed, res.returncode  # Return elapsed time and process return code 

def parse_input(input_path):  # Parse the input file and extract grid information 
    with open(input_path) as f:  # Open the input file 
        n, m = map(int, f.readline().split())  # Read grid dimensions 
        grid = []  # Initialize the grid list 
        for _ in range(n):  # Loop over each row 
            grid.append(list(map(int, f.readline().split())))  # Append row values to the grid 
    return n, m, grid  # Return grid dimensions and the grid itself 

def parse_output(output_path):  # Parse the output file and extract solution 
    with open(output_path) as f:  # Open the output file 
        lines = [line.strip() for line in f if line.strip()]  # Read non-empty lines 
    if not lines:  # Check if output is empty 
        return None  # Return None for empty output 
    if lines[0] == "No Solution":  # Check for "No Solution" output 
        return "No Solution"  # Return special marker for no solution 
    out = []  # Initialize output list 
    for line in lines:  # Loop through each line 
        parts = list(map(int, line.split()))  # Convert line to list of integers 
        if len(parts) != 6:  # Each line must have 6 integers 
            return None  # Return None if format is incorrect 
        out.append(parts)  # Append parsed line to output 
    return out  # Return the parsed output 

def check_solution(n, m, grid, output):  # Validate the solution against the problem constraints 
    if output == "No Solution":  # If output is "No Solution" 
        return True  # Accept as correct format 
    connectors = []  # List to store connector information 
    idx_map = {}  # Map from (row, col) to connector index 
    for i in range(n):  # Iterate over grid rows 
        for j in range(m):  # Iterate over grid columns 
            if grid[i][j] > 0:  # Check for connector cell 
                idx_map[(i+1, j+1)] = len(connectors)  # Map position to index 
                connectors.append({'row': i+1, 'col': j+1, 'deg': grid[i][j], 'dir': [0,0,0,0]})  # Add connector info 
    if len(output) != len(connectors):  # Check if output matches number of connectors 
        return False  # Return False if mismatch 
    for k, parts in enumerate(output):  # Loop through output lines 
        r, c = parts[0], parts[1]  # Extract row and column 
        if (r, c) not in idx_map:  # Validate connector position 
            return False  # Return False if not found 
        idx = idx_map[(r, c)]  # Get connector index 
        connectors[idx]['dir'] = parts[2:]  # Set direction flags 
        if sum(parts[2:]) != connectors[idx]['deg']:  # Check degree match 
            return False  # Return False if degree mismatch 
        for d in parts[2:]:  # Validate direction values 
            if d not in (0, 1):  # Should be 0 or 1 
                return False  # Return False if invalid value 
    nconn = len(connectors)  # Number of connectors 
    used_fence = set()  # Set to track used fences 
    fence_grid = [[0]*m for _ in range(n)]  # Grid to track fence placement 
    paired = [[0]*4 for _ in range(nconn)]  # Track paired directions for each connector 
    for idx, conn in enumerate(connectors):  # Loop through connectors 
        r, c = conn['row']-1, conn['col']-1  # Convert to 0-based indices 
        for d, flag in enumerate(conn['dir']):  # Loop through directions 
            if not flag:  # Skip if direction is not used 
                continue  # Move to next direction 
            if paired[idx][d]:  # Skip if already paired 
                continue  # Avoid double counting 
            dr, dc = [(-1,0),(1,0),(0,-1),(0,1)][d]  # Direction vectors 
            nr, nc = r+dr, c+dc  # Move to next cell 
            path = []  # Track path for this direction 
            while 0 <= nr < n and 0 <= nc < m:  # Stay within grid 
                if grid[nr][nc] > 0:  # Found another connector 
                    other_idx = idx_map[(nr+1, nc+1)]  # Get other connector index 
                    od = d^1  # Opposite direction 
                    if connectors[other_idx]['dir'][od] != 1:  # Check if paired direction exists 
                        return False  # Return False if not paired 
                    if paired[other_idx][od]:  # Check if already paired 
                        return False  # Return False if already paired 
                    paired[idx][d] = 1  # Mark current direction as paired 
                    paired[other_idx][od] = 1  # Mark opposite direction as paired 
                    break  # Exit loop after successful pairing 
                if fence_grid[nr][nc] == 0:  # No fence yet 
                    fence_grid[nr][nc] = 1 if d < 2 else 2  # Mark fence direction 
                else:  # Fence already exists 
                    if (d < 2 and fence_grid[nr][nc] != 1) or (d >= 2 and fence_grid[nr][nc] != 2):  # Check for crossing 
                        return False  # Return False if crossing detected 
                nr += dr  # Move to next cell in direction 
                nc += dc  # Move to next cell in direction 
            else:  # No connector found in path 
                return False  # Return False for dangling fence 
    for idx, conn in enumerate(connectors):  # Check all connectors 
        for d in range(4):  # Check all directions 
            if conn['dir'][d]:  # If direction is used 
                if not paired[idx][d]:  # Must be paired 
                    return False  # Return False if not paired 
    return True  # All checks passed, solution is valid 

def main():
    exe = compile_code()
    input_dirs = ["../data/input/sample", "../data/input/random"]
    output_dirs = ["../data/output/sample", "../data/output/random"]
    for d in output_dirs:
        os.makedirs(d, exist_ok=True)
    log = []  # List to store test results 
    for in_dir, out_dir in zip(input_dirs, output_dirs):  # Iterate over input/output directories 
        for fname in sorted(os.listdir(in_dir)):  # Loop through input files 
            if not fname.endswith(".in"):  # Skip non-input files 
                continue  # Move to next file 
            input_path = os.path.join(in_dir, fname)  # Build input file path 
            output_path = os.path.join(out_dir, fname.replace(".in", ".out"))  # Build output file path 
            elapsed, retcode = run_case(exe, input_path, output_path)  # Run the test case 
            n, m, grid = parse_input(input_path)  # Parse input file 
            output = parse_output(output_path)  # Parse output file 
            correct = check_solution(n, m, grid, output)  # Validate the solution 
            with open(output_path, 'r') as f:  # Read output file 
                output_content = f.read()  # Store output content 
            log.append({
                "input_file": input_path,  # Log input file path 
                "output_file": output_path,  # Log output file path 
                "output": output_content,  # Log output content 
                "elapsed_time": elapsed,  # Log elapsed time 
                "correct": correct  # Log correctness 
            })
            print(f"Test {fname}: {'Accepted' if correct else 'Wrong Answer'} ({elapsed:.3f}s)")  # Print test result 
    import datetime  # Import datetime for timestamp 
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Get current timestamp 
    os.makedirs("log", exist_ok=True)  # Ensure log directory exists 
    with open(f"log/eval_{now}.json", 'w') as f:  # Open log file for writing 
        json.dump(log, f, indent=2)  # Write log as JSON 

if __name__ == "__main__":
    main()
