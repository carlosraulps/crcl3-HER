#!/bin/bash
#SBATCH -J Co_adsorbed_cohp_Ucr
#SBATCH -p medio
#SBATCH --nodes=1
#SBATCH --ntasks=28
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

module purge
module load vasp/6.2.0 2>/dev/null || module load vasp 2>/dev/null

# 1. Run VASP static SCF
mpirun -np $SLURM_NTASKS vasp_std > vasp.out 2>&1

# 2. Run LOBSTER
if [ -s WAVECAR ]; then
    echo "[$(date)] VASP SCF completed. Running LOBSTER COHP analysis..."
    if [ -x ~/.local/bin/lobster ]; then
        ~/.local/bin/lobster > lobster.out 2>&1
    elif which lobster >/dev/null 2>&1; then
        lobster > lobster.out 2>&1
    fi
    echo "[$(date)] LOBSTER completed with exit code $?"
fi
