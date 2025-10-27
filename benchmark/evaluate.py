import os
import subprocess
import time
import json
from datetime import datetime

def compile_code():
    src = "../code/src/restore_fence.c"
    out = "../code/bin/restore_fence"
    cmd = f"gcc {src} -o {out}"
    res = subprocess.run(cmd, shell=True, capture_output=True)
    if res.returncode != 0:
        print("Compilation failed!")
        print(res.stderr.decode())
        exit(1)
    return out

def run_case(exe, input_path, output_path):
    with open(input_path, 'r') as fin, open(output_path, 'w') as fout:
        start = time.time()
        res = subprocess.run([exe], stdin=fin, stdout=fout, stderr=subprocess.PIPE)
        end = time.time()
        elapsed = end - start
    return elapsed, res.returncode

def check_output(input_path, output_path):
    # Only check format and if "No Solution" is possible
    with open(output_path, 'r') as f:
        lines = f.readlines()
    if len(lines) == 0:
        return False
    if lines[0].strip() == "No Solution":
        return True
    # Check each line format
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 6:
            return False
        for i in range(6):
            if i < 2:
                if not parts[i].isdigit():
                    return False
            else:
                if parts[i] not in ("0", "1"):
                    return False
    return True

def main():
    exe = compile_code()
    input_dirs = ["../data/input/sample", "../data/input/random"]
    output_dirs = ["../data/output/sample", "../data/output/random"]
    for d in output_dirs:
        os.makedirs(d, exist_ok=True)
    log = []
    for in_dir, out_dir in zip(input_dirs, output_dirs):
        for fname in sorted(os.listdir(in_dir)):
            if not fname.endswith(".in"):
                continue
            input_path = os.path.join(in_dir, fname)
            output_path = os.path.join(out_dir, fname.replace(".in", ".out"))
            elapsed, retcode = run_case(exe, input_path, output_path)
            correct = check_output(input_path, output_path)
            with open(output_path, 'r') as f:
                output_content = f.read()
            log.append({
                "input_file": input_path,
                "output_file": output_path,
                "output": output_content,
                "elapsed_time": elapsed,
                "correct": correct
            })
            print(f"Test {fname}: {'OK' if correct else 'FAIL'} ({elapsed:.3f}s)")
    # Write log
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("log", exist_ok=True)
    with open(f"log/eval_{now}.json", 'w') as f:
        json.dump(log, f, indent=2)

if __name__ == "__main__":
    main()
