#!/bin/bash
#SBATCH -J Ni_S1_yes_vdw
#SBATCH -o job.%j.out
#SBATCH -e job.%j.err
#SBATCH --partition=alto,medio
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --time=168:00:00

# ==============================================================================
# HUK CLUSTER OPTIMIZED SLURM EXECUTION SCRIPT
# System: CrCl3 2x2 + Adatom (Ni_S1_yes_vdw)
# Target Node: huk120 (alto, 36 cores) or huk123/124 (medio, 28 cores)
# ==============================================================================

# --- 1. Thread Affinity & Environment Settings ---
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

# --- 2. Slurm Job Diagnostics ---
echo "=========================================================="
echo "Starting Slurm Job : $SLURM_JOB_NAME ($SLURM_JOB_ID)"
echo "Executing on Host  : $(hostname)"
echo "Partition Selected : $SLURM_JOB_PARTITION"
echo "Allocated Node(s)  : $SLURM_NODELIST"
echo "Working Directory  : $(pwd)"
echo "Start Timestamp    : $(date)"
echo "=========================================================="

# --- 3. Dynamic Parallelization Sizing (Amdahl's Law Tuning) ---
NPROCS=${SLURM_NPROCS:-$SLURM_NTASKS}
if [ -z "$NPROCS" ] || [ "$NPROCS" -eq 0 ]; then
    NPROCS=$(nproc)
fi

# Determine optimal NCORE divisor based on node topology:
# - huk120 (alto, 36 cores): NCORE = 6 (6 orbital groups)
# - huk123/124 (medio, 28 cores): NCORE = 4 (7 orbital groups)
# - huk126 (normal, 24 cores): NCORE = 4 (6 orbital groups)
if [ "$NPROCS" -eq 36 ]; then
    NCORE_OPT=6
elif [ "$NPROCS" -eq 28 ]; then
    NCORE_OPT=4
elif [ "$NPROCS" -eq 24 ]; then
    NCORE_OPT=4
else
    NCORE_OPT=4
fi

if grep -q "NCORE" INCAR 2>/dev/null; then
    sed -i "s/.*NCORE.*/NCORE    = $NCORE_OPT           # Dynamically tuned for $NPROCS cores on $(hostname)/" INCAR
fi

echo "Running VASP with $NPROCS MPI processes (NCORE=$NCORE_OPT)..."

# --- 4. Execute VASP via Intel MPI ---
mpirun -np $NPROCS vasp_std > run.log 2>&1
EXIT_CODE=$?

echo "=========================================================="
echo "Execution finished at $(date) with exit code: $EXIT_CODE"
if grep -q "General timing and accounting informations for this job" run.log 2>/dev/null || grep -q "reached required accuracy" run.log 2>/dev/null; then
    echo ">>> STATUS: VASP CALCULATION CONVERGED SUCCESSFULLY <<<"
else
    echo ">>> WARNING: Check run.log for convergence or SCF abort <<<"
fi
echo "=========================================================="
exit $EXIT_CODE
