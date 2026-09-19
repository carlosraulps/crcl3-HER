#!/bin/bash
#SBATCH -J H3x3_S2_yesvdw
#SBATCH -p fulereno
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=5-00:00:00
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

# 1. System Limits & OpenMP Environment
ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

# 2. Fault Tolerance: Intercept termination/preemption signals for graceful VASP exit
trap 'echo "LABORT = .TRUE." > STOPCAR; echo "[$(date)] Intercepted termination signal! Flushed STOPCAR for clean exit."; wait' SIGTERM SIGINT SIGHUP

# 3. Resumption Logic: Check if valid CONTCAR exists from previous step/interruption
if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    NLINES=$(wc -l < CONTCAR)
    if [ "$NLINES" -ge 8 ]; then
        echo "[$(date)] Found existing valid CONTCAR ($NLINES lines). Resuming relaxation..."
        cp POSCAR POSCAR.bak_$(date +%s)
        cp CONTCAR POSCAR
    fi
fi

# 4. Environment Preparation (Carbono OpenHPC Stack)
module purge
module load vasp/6.2.0

# 5. In-Situ VASP Execution
echo "Executing VASP 6.2.0 with $SLURM_NTASKS MPI ranks (OpenMPI 4.1.4, --bind-to none)..."
mpirun --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1
EXIT_CODE=$?

# Remove STOPCAR if present after clean termination
rm -f STOPCAR

echo "=========================================================="
echo "Finished at $(date) with exit code $EXIT_CODE"
echo "=========================================================="
exit $EXIT_CODE
