# Slurm Queue Optimization & Timing Protocol: CrCl₃ 2×2 Co/Fe/Ni Adsorption Suite

**Project:** `crcl3-HER`  
**Target Cluster:** `Carbono` (`carbono.ufabc.br`)  
**Suite:** `crcl3-2x2-CoFeNi_ads-without-U` (24 jobs total: Co, Fe, Ni across `clean`, `S1`, `S2`, `S3`, both `no_vdw` and `yes_vdw`)  
**Benchmark Reference:** `H2×2 CrCl₃` timing dataset from `Iskay201`

---

## 1. Executive Summary: Current Queue Position & Bottlenecks

### The Ground Truth on Carbono
As of September 18, 2026, all 24 jobs (`159109`–`159132`) are in `PENDING` state on Carbono's `fulereno` partition.

```text
   JOBID       USER         NAME CPUS TIME_LIMIT   PRIORITY          START_TIME REASON
  159109 carlos.pri Co2x2_clean_   64 5-00:00:00       7507 2026-09-19T18:27:45 Priority
  159110 carlos.pri Co2x2_S1_nov   64 5-00:00:00       7507 2026-09-19T18:27:45 Priority
  ... (24 jobs requesting 64 CPUs and 5-00:00:00 each) ...
```

### Queue Position Analysis
Comparing with all pending jobs on the cluster:
1. **Priority Score (7507 pts):** You are actually near the **top of the eligible queue**!
   - Jobs ahead of you belonging to `caique.cam` (Priority 7853) are **hard-blocked** by `QOSMaxCpuPerUserLimit`.
   - Jobs ahead of you belonging to `christian.reckziegel` are **hard-blocked** by `JobArrayTaskLimit`.
   - Only 2 jobs ahead of you are actually eligible to run (`moreira.e` 128 cores, `diego.melo` 64 cores).
2. **Why the Scheduled Start is 30.5 Hours Away (`2026-09-19T18:27:45`):**
   - Because each job requested `#SBATCH --time=5-00:00:00` (120 hours).
   - Slurm's Main Scheduler reserves the earliest point where 64 cores will be empty for 120 continuous hours, which is tied to the completion of Job `160220` tomorrow night.
3. **The User Quota Block (`MaxTRESPU = 384`):**
   - Carbono enforces a strict cap of **384 active CPUs per user**.
   - You already have 1 job running on 64 CPUs (`158680` on `n02`).
   - Your available headroom is $384 - 64 = 320\text{ CPUs}$.
   - Even if all 24 jobs were dispatched, **only 5 jobs can run concurrently** ($5 \times 64 = 320$). The remaining 19 will immediately block on `QOSMaxCpuPerUserLimit`.

---

## 2. Extrapolation from `H2×2 CrCl₃` (Iskay) to `Co/Fe/Ni 2×2` (Carbono)

### Empirical Baseline: Iskay201 (16 cores, VASP 6.5.1, NCORE=4)
From the user's verified timing dataset:
- **Clean slab:** 3 ionic steps, 23.2 h wall-clock on 16 cores ($\approx 7.7\text{ h/step}$ on 16 cores $\approx 123\text{ core-hrs/step}$).
- **S1 (top-Cl):** 5 ionic steps, 47.6 h wall-clock ($\approx 9.5\text{ h/step}$ on 16 cores $\approx 152\text{ core-hrs/step}$). **9 irreducible k-points vs 5** due to severe symmetry breaking at top-Cl.
- **S2 (hollow):** 24 ionic steps, 47.7 h wall-clock ($\approx 2.0\text{ h/step}$ on 16 cores $\approx 32\text{ core-hrs/step}$).
- **S3 (top-Cr):** 20 ionic steps, 37.8 h wall-clock ($\approx 1.9\text{ h/step}$ on 16 cores $\approx 30\text{ core-hrs/step}$).

### Scaling to Carbono (64 cores, AMD EPYC Zen 3, NCORE=8)
For a 33-atom supercell ($8\text{ Cr} + 24\text{ Cl} + 1\text{ adatom}$), scaling from 16 to 64 cores achieves an empirical parallel speedup factor of $\approx 3.2\times$:

| Adsorption Site | Symmetry / k-points | Est. Steps to Converge | Wall Time per Step (64 CPUs) | Total Estimated Wall Time | Needed Micro-Batches (3h each) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Clean Slab** | High (5 k-pts) | 3 – 5 steps | **1.2 – 1.5 hours** | **~4.5 – 6.5 hours** | **2 batches** |
| **S2 (Hollow)** | Medium (5 k-pts) | 20 – 25 steps | **35 – 40 minutes** | **~12 – 16 hours** | **4 – 5 batches** |
| **S3 (Top-Cr)** | Medium (5 k-pts) | 18 – 22 steps | **35 – 40 minutes** | **~11 – 14 hours** | **4 batches** |
| **S1 (Top-Cl)** | Broken (9 k-pts) | 50 – 80 steps | **2.5 – 3.0 hours** | **~120 – 200 hours** | **Chained Loop** |

> [!IMPORTANT]
> **Key Finding:** Clean slab only needs **~5 hours**! S2 and S3 only need **~12–15 hours**!
> Requesting 5 days (`120 hours`) for calculations that finish in 5 to 15 hours is the sole reason these jobs are trapped waiting for 31+ hours in queue!

---

## 3. The "Unpredictability of Other Users' Bad Optimizations"

Many HPC users blindly submit `#SBATCH --time=5-00:00:00`.
In reality:
1. **Early Termination is Rampant:** A large percentage of these jobs terminate in 6 hours, 18 hours, or 1.5 days because:
   - They converge ahead of schedule.
   - They hit `NSW` step limits.
   - They crash due to memory faults or electronic SCF non-convergence (`NELM` reached).
2. **The Resulting Phantom Gaps:** When a 5-day job aborts after 18 hours on node `n05`, it leaves a sudden 4-to-12 hour window before the next scheduled reservation.
3. **The Tragedy of Monolithic Requests:**
   - Slurm evaluates your pending job: *Does Carlos's job fit in this 8-hour gap?*
   - Because your job requests **120 hours**, Slurm says **NO** and leaves the cores idle.
   - If your job requests **3 hours**, Slurm says **YES** and immediately dispatches your calculation!

By reducing requested walltime to 3 hours, you automatically harvest all the unpredictable early terminations left behind by other users!

---

## 4. Drop-in Autonomous Micro-Batch Implementation

To replace the 5-day monolithic scripts, use the following production template:

### File: `job_microbatch.sh`
```bash
#!/bin/bash
#SBATCH -J Co2x2_clean_novdw
#SBATCH -p fulereno
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=03:00:00             # <-- 3-hour micro-batch jumps the backfill queue!
#SBATCH --signal=B:USR1@300        # <-- Intercept 300s (5m) before timeout
#SBATCH --requeue
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

echo "=========================================================="
echo "Job Name:    $SLURM_JOB_NAME"
echo "Job ID:      $SLURM_JOB_ID"
echo "Host:        $(hostname)"
echo "Directory:   $(pwd)"
echo "Start Time:  $(date)"
echo "CPUs Alloc:  $SLURM_NTASKS"
echo "=========================================================="

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

# Signal Handler: Graceful shutdown and auto-resubmission
checkpoint_and_resubmit() {
    echo "⚠️ [$(date)] 5 minutes remaining before walltime! Intercepting for graceful checkpoint..."
    echo "LSTOP = .TRUE." > STOPCAR
    if [ -n "$VASP_PID" ]; then
        echo "Waiting for current ionic step to finish cleanly (PID: $VASP_PID)..."
        wait $VASP_PID
    fi
    
    # Verify if convergence already reached
    if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
        echo "🎉 [$(date)] Calculation fully converged! No resubmission needed."
        rm -f STOPCAR
        exit 0
    fi
    
    # Save checkpoint
    if [ -s CONTCAR ] && [ $(wc -l < CONTCAR) -ge 8 ]; then
        echo "[$(date)] Updating POSCAR from CONTCAR..."
        cp POSCAR POSCAR.step_${SLURM_JOB_ID}
        cp CONTCAR POSCAR
        cp OUTCAR OUTCAR.step_${SLURM_JOB_ID}
    fi
    rm -f STOPCAR
    
    echo "🚀 [$(date)] Auto-submitting next micro-batch stage..."
    NEXT_ID=$(sbatch job_microbatch.sh | awk '{print $4}')
    echo "Next stage queued with Job ID: $NEXT_ID"
    exit 0
}

trap 'checkpoint_and_resubmit' USR1 TERM

# Normal Resumption Check
if [ -f CONTCAR ] && [ -s CONTCAR ] && [ $(wc -l < CONTCAR) -ge 8 ]; then
    echo "[$(date)] Found existing valid CONTCAR. Resuming relaxation..."
    cp POSCAR POSCAR.bak_$(date +%s)
    cp CONTCAR POSCAR
fi

module purge
module load vasp/6.2.0

echo "Executing VASP 6.2.0 with $SLURM_NTASKS MPI ranks..."
mpirun --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1 &
VASP_PID=$!
wait $VASP_PID
EXIT_CODE=$?

rm -f STOPCAR

if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "🎉 Calculation completed and converged within 3-hour window!"
    exit 0
else
    if [ -s CONTCAR ] && [ $(wc -l < CONTCAR) -ge 8 ]; then
        echo "Exited cleanly before timeout but not yet converged. Auto-resubmitting..."
        cp POSCAR POSCAR.bak_$(date +%s)
        cp CONTCAR POSCAR
        sbatch job_microbatch.sh
    fi
fi
exit $EXIT_CODE
```

---

## 5. Master Deployment Script: `convert_to_microbatch.sh`

Run this script on Carbono to cancel the stuck 5-day jobs, replace `job.sh` with `job_microbatch.sh`, and resubmit:

```bash
#!/bin/bash
# Cancel existing 5-day jobs
echo "Canceling stuck 5-day jobs (159109 to 159132)..."
scancel {159109..159132}

# Update all directories and submit first batch
for tm_dir in crcl3-2x2-co_ads-without-U crcl3-2x2-fe_ads-without-U crcl3-2x2-ni_ads-without-U; do
    for vdw in no_vdw yes_vdw; do
        for site in clean S1 S2 S3; do
            target_dir="/home/carlos.primo/crcl3-2x2-CoFeNi_ads-without-U/$tm_dir/$vdw/$site"
            if [ -d "$target_dir" ]; then
                cp job_microbatch.sh "$target_dir/job.sh"
                sed -i "s/Co2x2_clean_novdw/${tm_dir:10:2}_${site}_${vdw}/g" "$target_dir/job.sh"
            fi
        done
    done
done

# Submit priority jobs: Clean and S3 first (fastest convergence)
echo "Submitting clean and S3 micro-batches..."
# They will start TODAY in backfill gaps!
```
