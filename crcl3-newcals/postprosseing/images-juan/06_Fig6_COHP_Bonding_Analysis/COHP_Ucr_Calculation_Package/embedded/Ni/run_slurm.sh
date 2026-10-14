#!/bin/bash
#SBATCH -J Ni_embedded_cohp_Ucr
#SBATCH -p normal         # Adjust partition for target cluster (e.g., standard, compute, batch)
#SBATCH -N 1
#SBATCH -n 24             # 24 to 32 cores recommended
#SBATCH -t 24:00:00       # ~6-8 hours required
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

export OMP_NUM_THREADS=1
ulimit -s unlimited 2>/dev/null || true

# Module environment (uncomment/adapt for target cluster)
# module purge 2>/dev/null || true
# module load vasp 2>/dev/null || module load vasp/6.2.0 2>/dev/null || true

# Detect binaries or fallback to PATH
VASP_BIN="$(which vasp_std 2>/dev/null || echo '/opt/vasp/vasp/bin/vasp_std')"
LOBSTER_BIN="$(which lobster 2>/dev/null || echo "$HOME/bin/lobster")"
MPIRUN="$(which mpirun 2>/dev/null || echo 'mpirun')"

echo "=============================================="
echo "[$(date)] Starting COHP for Ni (embedded, U_Cr = 3.29 eV)"
echo "Host: $(hostname)"
echo "Tasks: $SLURM_NTASKS"
echo "VASP: $VASP_BIN"
echo "LOBSTER: $LOBSTER_BIN"
echo "=============================================="

# Clean any previous aborted run files
rm -f WAVECAR CHGCAR CHG vasp.out OSZICAR OUTCAR vasprun.xml lobster.out lobsterout

# 1. Run VASP static SCF
echo "[$(date)] Running VASP static SCF..."
$MPIRUN -np $SLURM_NTASKS $VASP_BIN > vasp.out 2>&1
VASP_RET=$?

if [ $VASP_RET -ne 0 ] || [ ! -s WAVECAR ]; then
    echo "[$(date)] ERROR: VASP failed with exit code $VASP_RET (WAVECAR valid: $([ -s WAVECAR ] && echo YES || echo NO))"
    exit 1
fi

echo "[$(date)] VASP SCF completed successfully."

# 2. Run LOBSTER
echo "[$(date)] Running LOBSTER projection..."
$LOBSTER_BIN > lobster.out 2>&1
LOBSTER_RET=$?

if [ $LOBSTER_RET -eq 0 ] && [ -s COHPCAR.lobster ]; then
    echo "[$(date)] SUCCESS: LOBSTER finished cleanly. COHPCAR.lobster generated ($(wc -c < COHPCAR.lobster) bytes)."
else
    echo "[$(date)] ERROR: LOBSTER exited with code $LOBSTER_RET."
    exit 2
fi

echo "=============================================="
echo "[$(date)] Calculation complete for Ni (embedded)!"
echo "=============================================="
