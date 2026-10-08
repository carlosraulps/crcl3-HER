#!/usr/bin/env python3
"""
dispatch_huk_opportunity.py
Automates the opportunistic deployment of LOBSTER COHP calculations and 
companion Co S2 relaxations onto idle nodes (huk124, huk125, huk128) on Huk.
"""

import os
import subprocess

REMOTE_HOST = "huk"
REMOTE_BASE = "~/crcl3-HER"
LOCAL_COHP_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals/cohp_lobster_Uall"
LOCAL_CO_RELAX_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-Co-S2-U_all3.29/01_relax"

def prepare_huk_cohp_scripts():
    # 1. Adsorbed suite script for huk125 (28 cores, normal)
    ads_script = """#!/bin/bash
#SBATCH -J COHP_ads_Uall
#SBATCH -p normal
#SBATCH -w huk125
#SBATCH -N 1
#SBATCH -n 28
#SBATCH -t 03:00:00
#SBATCH -o cohp_ads.%j.out
#SBATCH -e cohp_ads.%j.err

export OMP_NUM_THREADS=1
ulimit -s unlimited 2>/dev/null || true

VASP_BIN="/opt/vasp/vasp/bin/vasp_std"
LOBSTER_BIN="/home/carlos/bin/lobster"
MPIRUN="/opt/intel/oneapi/mpi/2021.15/bin/mpirun"

BASE_DIR="$SLURM_SUBMIT_DIR"

for tm in Co Fe Ni; do
    echo "=============================================="
    echo "[$(date)] Starting COHP for Adsorbed $tm"
    echo "=============================================="
    cd "$BASE_DIR/adsorbed/$tm" || continue
    
    # Run VASP static SCF
    $MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1
    
    # Run LOBSTER
    if [ -s WAVECAR ]; then
        echo "[$(date)] Running LOBSTER for $tm..."
        $LOBSTER_BIN > lobster.out 2>&1
        echo "[$(date)] LOBSTER finished for $tm (code $?)"
    else
        echo "[$(date)] ERROR: WAVECAR not generated for $tm"
    fi
done

echo "=============================================="
echo "[$(date)] All Adsorbed COHP calculations complete!"
echo "=============================================="
"""
    with open(os.path.join(LOCAL_COHP_DIR, "run_cohp_ads_huk.sh"), "w") as f:
        f.write(ads_script)

    # 2. Embedded suite script for huk128 (24 cores, normal)
    emb_script = """#!/bin/bash
#SBATCH -J COHP_emb_Uall
#SBATCH -p normal
#SBATCH -w huk128
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -t 03:00:00
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
    echo "[$(date)] Starting COHP for Embedded $tm"
    echo "=============================================="
    cd "$BASE_DIR/embedded/$tm" || continue
    
    # Run VASP static SCF
    $MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1
    
    # Run LOBSTER
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
"""
    with open(os.path.join(LOCAL_COHP_DIR, "run_cohp_emb_huk.sh"), "w") as f:
        f.write(emb_script)

    # 3. Companion Co S2 relaxation on huk124 (28 cores, medio)
    huk_relax_script = """#!/bin/bash
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
"""
    with open(os.path.join(LOCAL_CO_RELAX_DIR, "run_huk_relax.sh"), "w") as f:
        f.write(huk_relax_script)

    print("Scripts successfully generated for Huk.")

if __name__ == "__main__":
    prepare_huk_cohp_scripts()
