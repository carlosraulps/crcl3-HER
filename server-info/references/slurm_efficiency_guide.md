# ⚙️ Slurm Scheduling Efficiency & Hardware Topology Guide

Professional HPC systems engineering guidelines for job placement, core pinning, memory cgroups, and Amdahl's Law parallel efficiency.

---

## 1. Amdahl's Law & Core Over-Allocation

One of the most common mistakes in research computing is requesting all available cores on a node without checking parallel scaling.

According to Amdahl's Law:
$$S(N) = \frac{1}{(1 - P) + \frac{P}{N}}$$

Where:
* $S(N)$ is the theoretical speedup with $N$ cores.
* $P$ is the parallel fraction of the code (typically 0.94 to 0.97 for DFT).
* $1 - P$ is the serial fraction (I/O, MPI communications, matrix distribution).

### The Diminishing Returns Threshold
* If $P = 0.95$:
  * 16 cores $\rightarrow$ **11.4x speedup** (71% parallel efficiency)
  * 32 cores $\rightarrow$ **16.4x speedup** (51% parallel efficiency)
  * 64 cores $\rightarrow$ **21.7x speedup** (34% parallel efficiency)
  * 128 cores $\rightarrow$ **25.9x speedup** (20% parallel efficiency)
* **Takeaway**: Doubling cores from 32 to 64 uses 2x compute units for only 32% extra speedup! For small and medium systems, running two 32-core jobs concurrently is **much more efficient** than running one 64-core job.

---

## 2. Process Pinning & NUMA Affinity

On multi-socket nodes (e.g. Iskay with 2 sockets of 128 cores, or Huk with 2 sockets of 18 cores):
* An MPI process accessing memory attached to the remote socket experiences **NUMA penalties (2x to 3x higher latency)**.
* When processes bounce between cores, CPU cache lines are constantly invalidated.

### Recommended Slurm Directives:
```bash
# Pin each MPI process strictly to its allocated physical core:
#SBATCH --cpu-bind=cores

# Or when running srun:
srun --cpu-bind=cores ./my_mpi_program
```

### Environment Variables:
```bash
# Prevent OpenMP threads from wandering:
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export KMP_AFFINITY=granularity=fine,compact,1,0
```

---

## 3. Slurm Memory Management

* If `#SBATCH --mem` is omitted, Slurm will either allocate the node's entire RAM (blocking other jobs) or use a low default limit.
* Always specify `--mem` explicitly with a safety headroom:
  $$\text{Slurm Memory Request} = \text{Estimated Peak Memory} \times 1.20$$
