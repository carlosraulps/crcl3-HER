#!/bin/bash
#SBATCH -J Co_S2_cdd
#SBATCH -p medio
#SBATCH -w huk122
#SBATCH -N 1
#SBATCH -n 12
#SBATCH -t 01:00:00
#SBATCH -o cdd.%j.out
#SBATCH -e cdd.%j.err

export OMP_NUM_THREADS=1
ulimit -s unlimited 2>/dev/null || true

VASP_BIN="/opt/vasp/vasp/bin/vasp_std"
MPIRUN="/opt/intel/oneapi/mpi/2021.15/bin/mpirun"

echo "[$(date)] Running 03_cdd_isolated_tm..."
cd /home/carlos/crcl3-HER/co_s2_cdd/03_cdd_isolated_tm
$MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1

echo "[$(date)] Running 02_cdd_slab..."
cd /home/carlos/crcl3-HER/co_s2_cdd/02_cdd_slab
$MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1

echo "[$(date)] All CDD components finished!"
