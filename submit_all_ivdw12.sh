#!/bin/bash
# ==============================================================================
# SUBMIT ALL IVDW = 12 (DFT-D3 BJ) JOBS ACROSS H2, 1x1, 2x2, and 3x3
# ==============================================================================
# Non-destructive: Runs only the newly created yes_vdw_ivdw12 calculations.
# Leaves existing no_vdw and yes_vdw (IVDW=11) calculations untouched.
# ==============================================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOTAL_SUBMITTED=0

echo "=========================================================="
echo " Submitting CrCl3 H-Adsorption Jobs with IVDW = 12"
echo " Host: $(hostname) | Date: $(date)"
echo " Base Directory: $ROOT_DIR"
echo "=========================================================="

# 1. H2 Reference (yes_vdw_ivdw12)
H2_DIR="$ROOT_DIR/H2_reference/yes_vdw_ivdw12"
if [ -d "$H2_DIR" ] && [ -f "$H2_DIR/job.sh" ]; then
    cd "$H2_DIR"
    JOB_OUT=$(sbatch job.sh)
    echo " [SUBMITTED] H2_reference/yes_vdw_ivdw12  -->  $JOB_OUT"
    TOTAL_SUBMITTED=$((TOTAL_SUBMITTED + 1))
fi

# 2. Supercells (1x1 and 2x2 only; 3x3 excluded per user request)
SCALES=("crcl3-1x1-h_ads-without-U" "crcl3-2x2-h_ads-without-U")
SITES=("clean" "S1" "S2" "S3")

for SCALE in "${SCALES[@]}"; do
    echo "--- Scale: $SCALE ---"
    for SITE in "${SITES[@]}"; do
        CALC_DIR="$ROOT_DIR/$SCALE/yes_vdw_ivdw12/$SITE"
        if [ -d "$CALC_DIR" ] && [ -f "$CALC_DIR/job.sh" ]; then
            cd "$CALC_DIR"
            JOB_OUT=$(sbatch job.sh)
            echo " [SUBMITTED] $SCALE/yes_vdw_ivdw12/$SITE  -->  $JOB_OUT"
            TOTAL_SUBMITTED=$((TOTAL_SUBMITTED + 1))
        else
            echo " [ERROR] Missing $CALC_DIR/job.sh"
        fi
    done
done

echo "=========================================================="
echo " Successfully submitted $TOTAL_SUBMITTED jobs with IVDW = 12."
echo " Monitor with 'squeue -u $USER' or 'python3 cluster_advisor.py'"
echo "=========================================================="
