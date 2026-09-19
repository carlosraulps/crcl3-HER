# 🛡️ Professional Slurm Job Submission & Verification Protocol

A standardized engineering protocol for preparing, submitting, and validating HPC jobs across Iskay, Huk, and Carbono.

---

## 1. Pre-Submission Checklist

Before running `sbatch job.slurm`, verify the following items:

- [ ] **Cluster Target**: Is this calculation suited for Iskay (high-core density), Huk (dedicated partitions), or Carbono?
- [ ] **Memory Check**: Does the memory request (`#SBATCH --mem=`) exceed the physical node limit?
  - Huk `alto`/`medio`/`normal`: **Max 120 GB**
  - Huk `hram`: **Max 490 GB**
  - Iskay `normal`: **Max 720 GB**
- [ ] **Walltime Check**: Does the requested `#SBATCH --time=` fit within the partition ceiling?
  - Huk `alto` / `hram`: **7 days max**
  - Huk `medio`: **30 days max**
  - Huk `normal`: **90 days max**
- [ ] **Input File Integrity**:
  - VASP: Verify `POSCAR`, `POTCAR`, `INCAR`, `KPOINTS` exist and have non-zero file sizes.
  - Check that `POTCAR` titles match the element sequence in `POSCAR`.
- [ ] **Parallelization Tags**:
  - `NCORE` is set to 4, 6, or 8 (not 1).
  - `KPAR` divides total k-points.
- [ ] **Disk Space**: Verify target filesystem has at least 10 GB free (`df -h .`).

---

## 2. Dry-Run Verification Procedure

For new or complex calculations, execute a **3-minute dry-run test**:

```bash
# 1. Temporarily edit INCAR:
#    NELM = 3     (stop after 3 electronic steps)
#    NSW  = 0     (no ionic steps)

# 2. Run interactive test or short job:
srun -p alto -n 16 --mem=16G --time=00:10:00 vasp_std

# 3. Check memory & convergence behavior in OUTCAR:
grep "total amount of memory used" OUTCAR
grep "General timing and accounting informations" OUTCAR
```

If memory consumption and timing look healthy, restore full `NELM`/`NSW` and submit the production job with `sbatch`.

---

## 3. Post-Submission Monitoring

1. **Verify Job Entered Queue**:
   ```bash
   squeue -u $USER
   ```
2. **Discord Notification**:
   Confirm that your personal Discord bot (SQ#6816) alerted:
   `⏳ [HUK] New Job Queued!` or `🟢 [HUK] Job Started Running!`
3. **Check Output Error Stream**:
   Within 60 seconds of starting, inspect the `job_%j.err` log:
   ```bash
   tail -n 20 *_*.err
   ```
   Verify no immediate MPI aborts, license issues, or segmentation faults.
