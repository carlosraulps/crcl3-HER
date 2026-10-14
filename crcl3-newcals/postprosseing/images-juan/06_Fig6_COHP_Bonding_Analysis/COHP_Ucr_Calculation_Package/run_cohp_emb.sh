#!/bin/bash
#SBATCH -J COHP_emb_Ucr_seq
#SBATCH -p normal         # Adjust partition as needed
#SBATCH -N 1
#SBATCH -n 24             # 24 to 32 cores
#SBATCH -t 48:00:00       # 3 systems x ~7h = ~21h
#SBATCH -o cohp_emb.%j.out
#SBATCH -e cohp_emb.%j.err

# ==============================================================================
# Sequential Batch Script: Embedded Co -> Fe -> Ni on Single Node
# ==============================================================================
# Ideal when cluster has limited nodes and you want one job to process all 3.
# ==============================================================================

export OMP_NUM_THREADS=1
ulimit -s unlimited 2>/dev/null || true

VASP_BIN="$(which vasp_std 2>/dev/null || echo '/opt/vasp/vasp/bin/vasp_std')"
LOBSTER_BIN="$(which lobster 2>/dev/null || echo "$HOME/bin/lobster")"
MPIRUN="$(which mpirun 2>/dev/null || echo 'mpirun')"

BASE_DIR="$SLURM_SUBMIT_DIR"

for tm in Co Fe Ni; do
    echo "=============================================="
    echo "[$(date)] Starting COHP for Embedded $tm (+U_Cr = 3.29 eV)"
    echo "=============================================="
    cd "$BASE_DIR/embedded/$tm" || continue
    
    # Clean previous aborted files
    rm -f WAVECAR CHGCAR CHG vasp.out OSZICAR OUTCAR vasprun.xml lobster.out lobsterout
    
    # 1. Run VASP static SCF
    echo "[$(date)] Running VASP static SCF..."
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
