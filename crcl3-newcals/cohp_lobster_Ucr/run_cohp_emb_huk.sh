#!/bin/bash
#SBATCH -J COHP_emb_Ucr
#SBATCH -p normal
#SBATCH -w huk128
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -t 48:00:00
#SBATCH -o cohp_emb.%j.out
#SBATCH -e cohp_emb.%j.err

export OMP_NUM_THREADS=1
ulimit -s unlimited 2>/dev/null || true

VASP_BIN="/opt/vasp/vasp/bin/vasp_std"
LOBSTER_BIN="/home/carlos/bin/lobster"
MPIRUN="/opt/intel/oneapi/mpi/2021.15/bin/mpirun"

BASE_DIR="$SLURM_SUBMIT_DIR"

for tm in Co Fe Ni; do
    echo "=============================================="
    echo "[$(date)] Starting COHP for Embedded $tm (+U_Cr)"
    echo "=============================================="
    cd "$BASE_DIR/embedded/$tm" || continue
    
    # Clean previous aborted outputs
    rm -f WAVECAR CHGCAR CHG vasp.out OSZICAR OUTCAR vasprun.xml lobster.out lobsterout
    
    # 1. Run VASP static SCF
    $MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1
    
    # 2. Run LOBSTER
    if [ -s WAVECAR ]; then
        echo "[$(date)] Running LOBSTER for $tm..."
        $LOBSTER_BIN > lobster.out 2>&1
        echo "[$(date)] LOBSTER finished for $tm (code $?)"
    else
        echo "[$(date)] ERROR: WAVECAR not generated for $tm"
    fi
done

echo "=============================================="
echo "[$(date)] All Embedded COHP calculations complete!"
echo "=============================================="
