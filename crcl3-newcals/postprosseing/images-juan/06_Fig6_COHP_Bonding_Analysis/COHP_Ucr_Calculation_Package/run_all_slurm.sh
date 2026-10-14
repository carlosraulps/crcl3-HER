#!/bin/bash
# ==============================================================================
# Master Slurm Submission Script: All 6 Systems in Parallel
# ==============================================================================
# Submits 6 independent Slurm jobs for maximum throughput if multiple nodes/cores
# are available on the private cluster.
#
# Usage:
#   chmod +x run_all_slurm.sh
#   ./run_all_slurm.sh [partition_name]
# ==============================================================================

PARTITION="${1:-normal}"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================================="
echo " Submitting all 6 COHP (+U_Cr) calculations in parallel"
echo " Target Partition: $PARTITION"
echo " Base Directory   : $BASE_DIR"
echo "=================================================================="

for mode in adsorbed embedded; do
    for tm in Co Fe Ni; do
        calc_dir="$BASE_DIR/$mode/$tm"
        if [ -d "$calc_dir" ]; then
            cd "$calc_dir" || continue
            echo -n "Submitting $mode/$tm ... "
            JOB_OUT=$(sbatch -p "$PARTITION" run_slurm.sh)
            echo "$JOB_OUT"
        fi
    done
done

echo "=================================================================="
echo "All 6 jobs submitted! Check queue status with: squeue -u \$USER"
echo "=================================================================="
