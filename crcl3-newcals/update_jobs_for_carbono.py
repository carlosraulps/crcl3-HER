#!/usr/bin/env python3
"""
================================================================================
 update_jobs_for_carbono.py
 Adapts all 24 CoFeNi 2x2 adsorption job.sh scripts in crcl3-newcals
 from the Huk cluster format to the Carbono (UFABC) cluster format.

 Changes applied:
   - Partition: alto,medio  -> fulereno
   - Tasks: exclusive/dynamic -> --ntasks=64 --cpus-per-task=1
   - Memory: (none) -> --mem=64G
   - Time: 168h -> 5-00:00:00 (5 days, fulereno max)
   - Signal+requeue: adds --signal=B:USR1@300 --requeue
   - Module load: adds module purge + module load vasp/6.2.0
   - MPI invocation: mpirun -np $NPROCS vasp_std
                  -> mpirun --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1 &
   - Adds STOPCAR trap + CONTCAR resumption logic
   - NCORE: dynamic sed -> sets NCORE=8 (optimal for 64-rank AMD EPYC)
   - Also updates INCAR: NCORE = 8 (from 4)

Usage:
   python3 update_jobs_for_carbono.py [--dry-run]
================================================================================
"""

import os
import re
import argparse
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CARBONO_JOB_TEMPLATE = """\
#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -p fulereno
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=5-00:00:00
#SBATCH --signal=B:USR1@300
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
echo "Time Limit:  5-00:00:00 (Micro-Batch Chained, fulereno)"
echo "=========================================================="

# 1. System Limits & OpenMP Environment
ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

# 2. Autonomous Checkpoint & Self-Resubmission Handler (runs 300s before walltime)
checkpoint_and_resubmit() {{
    echo "⚠️  [$( date)] Slurm USR1 intercepted — graceful checkpoint..."
    echo "LSTOP = .TRUE." > STOPCAR
    if [ -n "$VASP_PID" ]; then
        echo "Waiting for current ionic step to finish (PID: $VASP_PID)..."
        wait $VASP_PID
    fi
    if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
        echo "🎉 [$(date)] Calculation converged! No resubmission needed."
        rm -f STOPCAR
        exit 0
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        echo "[$(date)] Valid CONTCAR found — updating POSCAR for next stage..."
        cp POSCAR "POSCAR.step_${{SLURM_JOB_ID}}"
        cp CONTCAR POSCAR
        cp OUTCAR  "OUTCAR.step_${{SLURM_JOB_ID}}" 2>/dev/null || true
    fi
    rm -f STOPCAR
    echo "🚀 [$(date)] Auto-submitting next stage to Slurm..."
    NEXT_ID=$(sbatch job.sh | awk '{{print $4}}')
    echo "Next stage queued: Job ID $NEXT_ID"
    exit 0
}}
trap 'checkpoint_and_resubmit' USR1 TERM

# 3. Resumption Logic: restart from last valid CONTCAR
if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    NLINES=$(wc -l < CONTCAR)
    if [ "$NLINES" -ge 8 ]; then
        echo "[$(date)] Found valid CONTCAR ($NLINES lines). Resuming relaxation..."
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
    fi
fi

# 4. Environment — Carbono OpenHPC Stack (vasp/6.2.0 provides OpenMPI 4.1.4)
module purge
module load vasp/6.2.0

# 5. Execute VASP in background so USR1 trap remains active
echo "Executing VASP 6.2.0 with $SLURM_NTASKS MPI ranks (--bind-to none)..."
mpirun --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1 &
VASP_PID=$!
wait $VASP_PID
EXIT_CODE=$?

rm -f STOPCAR

# 6. Post-Run Convergence Check
if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "🎉 [$(date)] VASP converged within walltime window!"
    exit 0
else
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        echo "[$(date)] Relaxation ongoing — auto-resubmitting next micro-batch..."
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
        sbatch job.sh
    fi
fi

echo "=========================================================="
echo "Finished at $(date) with exit code $EXIT_CODE"
echo "=========================================================="
exit $EXIT_CODE
"""


def extract_job_name(content: str) -> str:
    m = re.search(r'^#SBATCH\s+-J\s+(\S+)', content, re.MULTILINE)
    return m.group(1) if m else "VASP_job"


def update_incar_ncore(incar_path: str, dry_run: bool) -> bool:
    """Update NCORE from 4 to 8 in INCAR for Carbono 64-rank runs."""
    if not os.path.isfile(incar_path):
        return False
    with open(incar_path, 'r') as f:
        content = f.read()

    new_content = re.sub(
        r'^(NCORE\s*=\s*)\d+(\s*#.*)?$',
        r'NCORE    = 8           # AMD EPYC Zen3 CCD: 8 cores/L3, optimal for 64 MPI ranks on Carbono',
        content,
        flags=re.MULTILINE
    )
    if new_content == content:
        return False  # No change needed

    if dry_run:
        print(f"  [DRY-RUN] Would update NCORE->8 in {incar_path}")
        return True

    with open(incar_path, 'w') as f:
        f.write(new_content)
    print(f"  ✓ Updated NCORE=8 in {os.path.relpath(incar_path, BASE_DIR)}")
    return True


def update_job_sh(job_path: str, dry_run: bool) -> bool:
    """Replace the job.sh with Carbono-compatible version."""
    with open(job_path, 'r') as f:
        old_content = f.read()

    job_name = extract_job_name(old_content)
    new_content = CARBONO_JOB_TEMPLATE.format(job_name=job_name)

    if dry_run:
        print(f"  [DRY-RUN] Would rewrite {os.path.relpath(job_path, BASE_DIR)} (job={job_name})")
        return True

    with open(job_path, 'w') as f:
        f.write(new_content)
    print(f"  ✓ Wrote Carbono job.sh for {os.path.relpath(job_path, BASE_DIR)} (job={job_name})")
    return True


def main():
    parser = argparse.ArgumentParser(description="Update CoFeNi job.sh scripts for Carbono cluster")
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without writing')
    args = parser.parse_args()

    pattern = os.path.join(BASE_DIR, 'crcl3-2x2-*_ads-without-U', '*', '*', 'job.sh')
    job_files = sorted(glob.glob(pattern))

    if not job_files:
        print(f"ERROR: No job.sh files found matching {pattern}")
        return

    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Updating {len(job_files)} job.sh files for Carbono cluster...")
    print("=" * 70)

    updated_jobs = 0
    updated_incars = 0

    for job_path in job_files:
        calc_dir = os.path.dirname(job_path)
        incar_path = os.path.join(calc_dir, 'INCAR')
        print(f"\n→ {os.path.relpath(job_path, BASE_DIR)}")

        if update_job_sh(job_path, args.dry_run):
            updated_jobs += 1
        if update_incar_ncore(incar_path, args.dry_run):
            updated_incars += 1

    print("\n" + "=" * 70)
    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Summary:")
    print(f"  job.sh files  updated : {updated_jobs}")
    print(f"  INCAR NCORE   updated : {updated_incars}")
    print(f"  Total calculations    : {len(job_files)}")
    if not args.dry_run:
        print("\n✅ All scripts updated for Carbono (fulereno, 64 cores, --bind-to none, vasp/6.2.0)")


if __name__ == "__main__":
    main()
