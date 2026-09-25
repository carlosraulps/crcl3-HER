#!/bin/bash
#SBATCH --job-name=S1
#SBATCH --partition=alto,medio
#SBATCH --nodes=1
#SBATCH --ntasks=36
#SBATCH --output=job.%j.out
#SBATCH --error=job.%j.err

source /etc/profile.d/modules.sh 2>/dev/null || true
export OMP_NUM_THREADS=1
ulimit -s unlimited

# Auto-detect optimal NCORE
export NCORE=6

mpirun -np 36 /opt/vasp/vasp.6.3.0/bin/vasp_std > run.log 2>&1
