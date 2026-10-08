#!/bin/bash
#SBATCH -J Co_S2_relax_huk
#SBATCH -p medio
#SBATCH -w huk124
#SBATCH -N 1
#SBATCH -n 28
#SBATCH -t 08:00:00
#SBATCH -o co_s2_relax.%j.out
#SBATCH -e co_s2_relax.%j.err

export OMP_NUM_THREADS=1
ulimit -s unlimited 2>/dev/null || true

VASP_BIN="/opt/vasp/vasp/bin/vasp_std"
MPIRUN="/opt/intel/oneapi/mpi/2021.15/bin/mpirun"

echo "[$(date)] Starting Co S2 relaxation on huk124 (28 cores)..."
$MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1
echo "[$(date)] VASP finished with exit code $?"
