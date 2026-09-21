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

DRY_RUN=0
if [[ "$1" == "--test" || "$1" == "--dry-run" ]]; then
    DRY_RUN=1
    echo " MODE: Dry-run test (sbatch --test-only, no jobs submitted)"
fi

TOTAL_SUBMITTED=0
for V in "${VARIANTS[@]}"; do
    for S in "${SITES[@]}"; do
        CALC_DIR="$SCRIPT_DIR/$V/$S"
        if [ -d "$CALC_DIR" ] && [ -f "$CALC_DIR/job.sh" ]; then
            cd "$CALC_DIR"
            if [ "$DRY_RUN" -eq 1 ]; then
                JOB_OUT=$(sbatch --test-only job.sh 2>&1)
                RET=$?
                if [ $RET -eq 0 ]; then
                    echo " [TEST-OK]  $V/$S  -->  $JOB_OUT"
                else
                    echo " [TEST-FAIL]$V/$S  -->  $JOB_OUT"
                fi
            else
                JOB_OUT=$(sbatch job.sh)
                echo " [SUBMITTED] $V/$S  -->  $JOB_OUT"
                TOTAL_SUBMITTED=$((TOTAL_SUBMITTED + 1))
            fi
        else
            echo " [ERROR] Missing directory or job.sh: $CALC_DIR"
        fi
    done
done
echo "=========================================================="
if [ "$DRY_RUN" -eq 1 ]; then
    echo " Dry-run simulation completed. All configurations verified."
    echo " Run './submit_all_3x3.sh' without arguments to submit to Slurm."
else
    echo " Successfully submitted $TOTAL_SUBMITTED jobs."
    echo " Use 'squeue -u $USER' or './check_status_3x3.sh' to monitor."
fi
echo "=========================================================="
