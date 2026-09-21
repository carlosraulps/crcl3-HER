#!/bin/bash
# ==============================================================================
# SUBMIT ALL 8 CALCULATION JOBS FOR CrCl3 2x2 H-ADSORPTION (No Hubbard U)
# ==============================================================================
# Variants:
#   - no_vdw: clean, S1, S2, S3 (Pure GGA-PBE)
#   - yes_vdw: clean, S1, S2, S3 (PBE + DFT-D3)
# Resources per job: 32 cores, 32 GB RAM, --requeue enabled
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS=("no_vdw" "yes_vdw")
SITES=("clean" "S1" "S2" "S3")

echo "=========================================================="
echo " Submitting CrCl3 2x2 H-Adsorption Jobs to SLURM"
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
echo " Use 'squeue -u $USER' or './check_status_2x2.sh' to monitor."
echo "=========================================================="
