#!/bin/bash
#SBATCH -J Co_S2_yes_vdw
#SBATCH -p fulereno
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=03:00:00
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
echo "Time Limit:  03:00:00 (Micro-Batch Chained)"
echo "=========================================================="

# 1. System Limits & OpenMP Environment
ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

# 2. Autonomous Checkpoint & Self-Resubmission Handler
checkpoint_and_resubmit() {
    echo "⚠️ [$(date)] Slurm signal intercepted! Initiating graceful checkpoint..."
    echo "LSTOP = .TRUE." > STOPCAR
    if [ -n "$VASP_PID" ]; then
        echo "Waiting for current ionic step to finish cleanly (PID: $VASP_PID)..."
        wait $VASP_PID
    fi
    
    # Check if calculation already reached required accuracy
    if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
        echo "🎉 [$(date)] Calculation fully converged! No resubmission needed."
        rm -f STOPCAR
        exit 0
    fi
    
    # Save checkpoint structure from last finished ionic step
    if [ -s CONTCAR ] && [ $(wc -l < CONTCAR) -ge 8 ]; then
        echo "[$(date)] Found valid CONTCAR. Updating POSCAR for next stage..."
        cp POSCAR "POSCAR.step_${SLURM_JOB_ID}"
        cp CONTCAR POSCAR
        cp OUTCAR "OUTCAR.step_${SLURM_JOB_ID}"
    fi
    rm -f STOPCAR
    
    echo "🚀 [$(date)] Auto-submitting next micro-batch stage to Slurm..."
    NEXT_ID=$(sbatch job.sh | awk '{print $4}')
    echo "Next stage queued with Job ID: $NEXT_ID"
    exit 0
}

# Trap USR1 (sent 300s before walltime by Slurm) as well as TERM
trap 'checkpoint_and_resubmit' USR1 TERM

# 3. Resumption Logic: Check if valid CONTCAR exists from previous step/interruption
if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    NLINES=$(wc -l < CONTCAR)
    if [ "$NLINES" -ge 8 ]; then
        echo "[$(date)] Found existing valid CONTCAR ($NLINES lines). Resuming relaxation..."
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
    fi
fi

# 4. Environment Preparation (Carbono OpenHPC Stack)
module purge
module load vasp/6.2.0

# 5. In-Situ VASP Execution in Background so Trap is Active
echo "Executing VASP 6.2.0 with $SLURM_NTASKS MPI ranks (OpenMPI 4.1.4, --bind-to none)..."
mpirun --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1 &
VASP_PID=$!
wait $VASP_PID
EXIT_CODE=$?

rm -f STOPCAR

# 6. Post-Run Convergence Check
if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "🎉 [$(date)] Calculation completed and converged within 3-hour window!"
    exit 0
else
    if [ -s CONTCAR ] && [ $(wc -l < CONTCAR) -ge 8 ]; then
        echo "[$(date)] VASP exited before timeout but relaxation ongoing. Auto-resubmitting..."
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
        sbatch job.sh
    fi
fi

echo "=========================================================="
echo "Finished at $(date) with exit code $EXIT_CODE"
echo "=========================================================="
exit $EXIT_CODE
