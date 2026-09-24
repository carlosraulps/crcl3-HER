#!/bin/bash
#SBATCH -J Co_S2_U329
#SBATCH -o job.%j.out
#SBATCH -e job.%j.err
#SBATCH --partition=fulereno,nanotubo,grafeno
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=04:00:00
#SBATCH --signal=B:USR1@300

# ==============================================================================
# CARBONO & HUK DUAL-COMPATIBLE SLURM SCRIPT (Slurm HPC Pre-Flight Optimized)
# System: Co_S2_U329
# Topology: 32 cores (socket architecture divisor), 4-hour micro-batch
# ==============================================================================

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

# Handle SIGUSR1 checkpoint signal for auto-resubmission
resubmit_on_timeout() {
    echo "[$(date)] SIGUSR1 received (5 min remaining). Checkpointing..."
    if [ -f CONTCAR ] && [ -s CONTCAR ]; then
        cp CONTCAR POSCAR
        echo "Updated POSCAR with CONTCAR for seamless restart."
    fi
    sbatch "$0"
    exit 0
}
trap 'resubmit_on_timeout' USR1

echo "=========================================================="
echo "Starting Slurm Job : $SLURM_JOB_NAME ($SLURM_JOB_ID)"
echo "Host               : $(hostname)"
echo "Allocated CPUs     : $SLURM_NTASKS"
echo "Working Directory  : $(pwd)"
echo "Start Timestamp    : $(date)"
echo "=========================================================="

# Tune NCORE for 32 cores
if [ "$SLURM_NTASKS" -eq 32 ]; then
    NCORE_OPT=4
elif [ "$SLURM_NTASKS" -eq 64 ]; then
    NCORE_OPT=8
else
    NCORE_OPT=4
fi

sed -i "s/.*NCORE.*/NCORE    = $NCORE_OPT/" INCAR

# Execute VASP
mpirun -np $SLURM_NTASKS vasp_std > run.log 2>&1
EXIT_CODE=$?

echo "Finished at $(date) with exit code $EXIT_CODE"

if grep -q "reached required accuracy" run.log 2>/dev/null; then
    echo ">>> CONVERGED SUCCESSFULLY <<<"
elif [ -f CONTCAR ] && [ -s CONTCAR ]; then
    cp CONTCAR POSCAR
fi

exit $EXIT_CODE
