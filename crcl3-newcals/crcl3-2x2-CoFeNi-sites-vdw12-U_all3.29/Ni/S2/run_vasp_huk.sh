#!/bin/bash
#SBATCH -J Ni_S2_huk
#SBATCH -p hram
#SBATCH -w huk118
#SBATCH -N 1
#SBATCH -n 16
#SBATCH -t 04:00:00
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

VASP_BIN="/opt/vasp/vasp/bin/vasp_std"
MPIRUN="/opt/intel/oneapi/mpi/2021.15/bin/mpirun"

echo "[$(date)] Starting Ni S2 relaxation continuation on huk118 (16 cores)..."
$MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1
echo "[$(date)] VASP finished with exit code $?"
