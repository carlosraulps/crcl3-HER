# ⚡ VASP HPC Tuning & Optimization Guide

A comprehensive guide for configuring VASP electronic minimization and ionic relaxations on multi-core clusters (Iskay, Huk, Carbono).

---

## 1. Golden Rules for VASP Parallelization

VASP parallelizes across three distinct dimensions:
1. **K-Points (`KPAR`)**: Independent electronic problem per k-point (almost zero communication overhead).
2. **Bands / Orbitals (`NCORE`)**: Distributes orbitals over cores working on individual FFTs.
3. **Plane Waves / Grid**: Automatic intra-band FFT distribution.

### 🌟 Rule 1: Always Maximize `KPAR` First
* If your calculation has $K$ k-points:
  * Set `KPAR` to a divisor of $K$ and a divisor of total cores.
  * **Efficiency**: Almost 100% linear scaling up to `KPAR = K`.
  * *Note*: If Gamma-point only ($K=1$), `KPAR` must be 1.

### 🌟 Rule 2: Tune `NCORE` to Match Sockets / L3 Cache
* **Do NOT use default `NCORE=1`**! On modern 24–128 core nodes, `NCORE=1` creates massive all-to-all communication bottlenecks.
* **Optimal `NCORE` values**:
  * **Huk (Intel Xeon Gold, 12-18 cores/socket)**: `NCORE = 4` or `NCORE = 6`.
  * **Iskay (High-density 128 cores/socket)**: `NCORE = 4`, `8`, or `16`.
  * **General Formula**: $NCORE \approx \sqrt{N_{cores} / KPAR}$ rounded to a core-divisor.

### 🌟 Rule 3: The 4-Bands-Per-Core Rule
* Ensure:
  $$\frac{\text{NBANDS}}{N_{cores}} \ge 4$$
* If $\frac{\text{NBANDS}}{N_{cores}} < 2$, cores spend more time waiting on MPI barriers than doing real matrix operations. Request fewer cores!

---

## 2. Supercell Sizing & Memory Scaling

Based on empirical benchmarks on the CrCl3 project:

| Supercell | Atoms Count | Typical RAM | Recommended Cores | Huk Target | Iskay Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1x1** | 8–9 atoms | 10–14 GB | 16–24 cores | `alto` (huk120) | `normal` (16 cores) |
| **2x2** | 32–33 atoms | 22–38 GB | 28–36 cores | `alto` or `medio` | `normal` (32 cores) |
| **3x3** | 72–73 atoms | **70–110 GB** | 40–64 cores | **`hram`** (huk119) | `normal` (64 cores) |
| **Hybrid (HSE06)**| 32+ atoms | **150–400 GB**| 40+ cores | **`hram`** (huk119) | `normal` (128 cores)|

---

## 3. Recommended `INCAR` Parallel Block

Include this block in your production `INCAR` files:

```fortran
# ==============================================================================
# Parallelization Settings
# ==============================================================================
KPAR  = 4          # Number of k-point groups (matches node count or k-point divisor)
NCORE = 4          # Cores per orbital (divide cores-per-socket)
LPLANE = .TRUE.    # Data distribution over plane-wave grid
NWRITE = 1         # Concise OUTCAR to reduce I/O pressure on shared NFS
```

---

## 4. Avoiding Out-Of-Memory (OOM) Termination

If your calculation crashes with `slurmstepd: error: Detected 1 oom-kill event(s)`:
1. **Reduce `KPAR`**: Higher `KPAR` replicates wavefunctions in memory across groups. Reducing `KPAR` consolidates memory per MPI rank.
2. **Move to Huk `hram`**: Node `huk119` has **504 GB RAM**, compared to 126 GB on standard nodes.
3. **Increase Slurm `--mem` buffer**: Always request 15–20% higher memory in `#SBATCH --mem=` than estimated to account for peak electronic iteration allocations.
