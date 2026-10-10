#!/bin/bash
#SBATCH -J Ni_S2_cont
#SBATCH -p medio
#SBATCH -w huk124
#SBATCH -N 1
#SBATCH -n 28
#SBATCH -t 48:00:00
#SBATCH -o ni_s2_cont.%j.out
#SBATCH -e ni_s2_cont.%j.err

export OMP_NUM_THREADS=1
ulimit -s unlimited 2>/dev/null || true

VASP_BIN="/opt/vasp/vasp/bin/vasp_std"
MPIRUN="/opt/intel/oneapi/mpi/2021.15/bin/mpirun"

echo "[$(date)] Starting Ni S2 continuation on huk124 (28 cores, medio)..."
$MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1
echo "[$(date)] VASP finished with exit code $?"
