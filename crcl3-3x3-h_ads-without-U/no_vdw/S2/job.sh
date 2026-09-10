#!/bin/bash
#SBATCH -J H3x3_S2_novdw
#SBATCH -p normal
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
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

# 1. Fault Tolerance: Intercept shutdown/preemption signals for graceful VASP exit
trap 'echo "LABORT = .TRUE." > STOPCAR; echo "[$(date)] Intercepted termination signal! Flushed STOPCAR for clean exit."; wait' SIGTERM SIGINT SIGHUP

# 2. Resumption Logic: Check if valid CONTCAR exists from previous step/interruption
if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    NLINES=$(wc -l < CONTCAR)
    if [ "$NLINES" -ge 8 ]; then
        echo "[$(date)] Found existing valid CONTCAR ($NLINES lines). Resuming relaxation..."
        cp POSCAR POSCAR.bak_$(date +%s)
        cp CONTCAR POSCAR
    fi
fi

# 3. Environment Preparation
module purge
module load spack/1.0.1
module load openmpi/5.0.8-aocc-5.0.0-linux-rocky10-icelake-wxmifob
module load vasp/6.5.1-aocc-5.0.0-linux-rocky10-icelake-erkzov4

export OMP_NUM_THREADS=1

# 4. In-Situ VASP Execution
echo "Executing VASP 6.5.1 with $SLURM_NTASKS MPI ranks..."
mpirun -np $SLURM_NTASKS vasp_std > vasp.out 2>&1
EXIT_CODE=$?

# Remove STOPCAR if present after clean termination
rm -f STOPCAR

echo "=========================================================="
echo "Finished at $(date) with exit code $EXIT_CODE"
echo "=========================================================="
exit $EXIT_CODE
