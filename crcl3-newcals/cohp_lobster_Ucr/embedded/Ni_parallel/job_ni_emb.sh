#!/bin/bash
#SBATCH -J Ni_emb_Ucr
#SBATCH -p medio
#SBATCH -w huk122
#SBATCH -N 1
#SBATCH -n 28
#SBATCH -t 24:00:00
#SBATCH -o cohp_ni_emb.%j.out
#SBATCH -e cohp_ni_emb.%j.err

export OMP_NUM_THREADS=1
ulimit -s unlimited 2>/dev/null || true
VASP_BIN="/opt/vasp/vasp/bin/vasp_std"
LOBSTER_BIN="/home/carlos/bin/lobster"
MPIRUN="/opt/intel/oneapi/mpi/2021.15/bin/mpirun"

cd /home/carlos/crcl3-newcals/cohp_lobster_Ucr/embedded/Ni_parallel
rm -f WAVECAR CHGCAR CHG vasp.out OSZICAR OUTCAR vasprun.xml lobster.out lobsterout

echo "[Wed Oct 14 09:22:26 -03 2026] Running VASP SCF for Embedded Ni (+U_Cr)..."
$MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1

if [ -s WAVECAR ]; then
    echo "[Wed Oct 14 09:22:26 -03 2026] Running LOBSTER for Ni..."
    $LOBSTER_BIN > lobster.out 2>&1
    echo "[Wed Oct 14 09:22:26 -03 2026] LOBSTER finished for Ni (code $?)"
else
    echo "[Wed Oct 14 09:22:26 -03 2026] ERROR: WAVECAR missing"
fi
