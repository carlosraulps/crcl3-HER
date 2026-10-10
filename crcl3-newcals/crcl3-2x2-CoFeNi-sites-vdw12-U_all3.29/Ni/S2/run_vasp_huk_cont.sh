#!/bin/bash
#SBATCH -J Ni_S2_cont
#SBATCH -p hram
#SBATCH -w huk118
#SBATCH -N 1
#SBATCH -n 16
#SBATCH -t 12:00:00
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

cd /home/carlos/crcl3-HER/sites_Uall/Ni/S2

# Check if already converged
if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "[$(date)] Ni S2 already converged in OUTCAR. Exiting."
    exit 0
fi

# Rotate previous outputs and use CONTCAR
if [ -s CONTCAR ] && [ $(wc -l < CONTCAR) -ge 8 ]; then
    echo "[$(date)] Updating POSCAR from CONTCAR..."
    cp -v CONTCAR POSCAR
fi

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

VASP_BIN="/opt/vasp/vasp/bin/vasp_std"
MPIRUN="/opt/intel/oneapi/mpi/2021.15/bin/mpirun"

echo "[$(date)] Starting chained Ni S2 continuation on huk118 (16 cores, 12h)..."
$MPIRUN -np $SLURM_NTASKS $VASP_BIN >> vasp.out 2>&1
echo "[$(date)] VASP finished with exit code $?"
