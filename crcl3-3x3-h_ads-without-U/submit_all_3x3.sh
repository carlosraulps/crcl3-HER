#!/bin/bash
# ==============================================================================
# SUBMIT ALL 8 CALCULATION JOBS FOR CrCl3 3x3 H-ADSORPTION (No Hubbard U)
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS=("no_vdw" "yes_vdw")
SITES=("clean" "S1" "S2" "S3")

echo "=========================================================="
echo " Submitting CrCl3 3x3 H-Adsorption Jobs to SLURM"
echo " Host: $(hostname) | Date: $(date)"
echo " Base Directory: $SCRIPT_DIR"
echo "=========================================================="

TOTAL_SUBMITTED=0
for V in "${VARIANTS[@]}"; do
    for S in "${SITES[@]}"; do
        CALC_DIR="$SCRIPT_DIR/$V/$S"
        if [ -d "$CALC_DIR" ] && [ -f "$CALC_DIR/job.sh" ]; then
            cd "$CALC_DIR"
            JOB_OUT=$(sbatch job.sh)
            echo " [SUBMITTED] $V/$S  -->  $JOB_OUT"
            TOTAL_SUBMITTED=$((TOTAL_SUBMITTED + 1))
        else
            echo " [ERROR] Missing directory or job.sh: $CALC_DIR"
        fi
    done
done
echo "=========================================================="
echo " Successfully submitted $TOTAL_SUBMITTED jobs."
echo " Use 'squeue -u $USER' or './check_status_3x3.sh' to monitor."
echo "=========================================================="
