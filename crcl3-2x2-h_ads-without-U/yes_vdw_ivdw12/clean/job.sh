#!/bin/bash
#SBATCH -J H2x2_cl_vdw12
#SBATCH -p alto,medio,normal
#SBATCH --nodes=1
#SBATCH --ntasks=24
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
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

# 3. Environment Preparation for HUK Cluster
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

# 4. In-Situ VASP Execution using native HUK oneAPI MPI & VASP 6.5.1
echo "Executing VASP 6.5.1 with $SLURM_NTASKS MPI ranks..."
mpirun -np $SLURM_NTASKS /opt/vasp/vasp/bin/vasp_std > vasp.out 2>&1
EXIT_CODE=$?

# Remove STOPCAR if present after clean termination
rm -f STOPCAR

echo "=========================================================="
echo "Finished at $(date) with exit code $EXIT_CODE"
echo "=========================================================="
exit $EXIT_CODE
