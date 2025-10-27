# garden-fence-reconstruction

A project to reconstruct garden fence layouts from connector positions, including a C solver, test case generator, and evaluation scripts.

## How to Use

### Prepare Sample Inputs

Sample inputs are already provided in `data/input/sample/0.in`, `1.in`, `2.in`.

### Generate Random Inputs

```bash
cd benchmark
python gen_random.py
```

This will generate 10 random input files in `data/input/random/`

### Evaluate All Inputs

```bash
cd benchmark
python evaluate.py
```

This will compile the C code (if not already compiled), run all sample and random inputs, save outputs to `data/output/sample/` and `data/output/random/`, and produce a log file in `benchmark/log/`.

### Compile the C Code Manually (Optional)

If you encounter issues when compiling C code, you may refer to and adopt the manual compilation methods provided below.

```bash
cd code/src
gcc restore_fence.c -o ../bin/restore_fence
```

## Results

Outputs are in `data/output/sample/` and `data/output/random/`.
Evaluation logs are in `benchmark/log/`, named with the evaluation timestamp.
