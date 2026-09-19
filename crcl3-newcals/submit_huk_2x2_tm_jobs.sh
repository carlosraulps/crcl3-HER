#!/bin/bash
# ==============================================================================
# HUK CLUSTER SUBMISSION DISPATCHER: CrCl3 2x2 Transition Metal Adsorption
# Systems: Co, Fe, Ni (Sites: S1, S2, S3 | Variants: no_vdw, yes_vdw)
# Hardware: Huk Cluster (alto: huk120, medio: huk123/124, normal: huk126)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ELEMENTS=("co" "fe" "ni")
VDW_TYPES=("no_vdw" "yes_vdw")
SITES=("S1" "S2" "S3")

echo "=================================================================="
echo " 🚀 BATCH SUBMITTING CRCL3 2x2 TM ADSORPTION JOBS ON HUK"
echo " Date: $(date)"
echo " Host: $(hostname)"
echo " Base Directory: $SCRIPT_DIR"
echo "=================================================================="

# Check for Slurm availability
if ! command -v sbatch >/dev/null 2>&1; then
    echo "ERROR: 'sbatch' command not found. This script must be run on Huk cluster."
    exit 1
fi

TOTAL_SUBMITTED=0
SKIPPED_CLEAN=0

for elem in "${ELEMENTS[@]}"; do
    ELEM_DIR="$SCRIPT_DIR/crcl3-2x2-${elem}_ads-without-U"
    echo ""
    echo ">>> Processing Transition Metal: ${elem^^} ($ELEM_DIR) <<<"
    
    if [ ! -d "$ELEM_DIR" ]; then
        echo "Warning: Directory $ELEM_DIR not found, skipping."
        continue
    fi
    
    for vdw in "${VDW_TYPES[@]}"; do
        # Verify clean slab status
        CLEAN_DIR="$ELEM_DIR/$vdw/clean"
        if [ -f "$CLEAN_DIR/OUTCAR" ] && grep -q "General timing and accounting" "$CLEAN_DIR/OUTCAR" 2>/dev/null; then
            echo "  [CLEAN] $elem/$vdw/clean already converged. Skipping re-run."
            ((SKIPPED_CLEAN++))
        fi

        for site in "${SITES[@]}"; do
            TARGET_DIR="$ELEM_DIR/$vdw/$site"
            
            if [ ! -d "$TARGET_DIR" ]; then
                echo "  [MISSING] $TARGET_DIR does not exist, skipping."
                continue
            fi
            
            # Check if calculation is already finished
            if [ -f "$TARGET_DIR/OUTCAR" ] && grep -q "General timing and accounting" "$TARGET_DIR/OUTCAR" 2>/dev/null; then
                echo "  [DONE] $elem/$vdw/$site is already fully converged. Skipping."
                continue
            fi
            
            # Check required VASP inputs
            for req in INCAR POSCAR POTCAR KPOINTS job.sh; do
                if [ ! -f "$TARGET_DIR/$req" ]; then
                    echo "  [ERROR] Missing $req in $TARGET_DIR! Cannot submit."
                    continue 2
                fi
            done
            
            # Submit job from within target directory
            cd "$TARGET_DIR"
            JOB_OUT=$(sbatch job.sh)
            JOB_ID=$(echo "$JOB_OUT" | awk '{print $NF}')
            echo "  [SUBMITTED] $elem | $vdw | $site -> Job ID: $JOB_ID (Partition: alto,medio)"
            ((TOTAL_SUBMITTED++))
            cd "$SCRIPT_DIR"
        done
    done
done

echo ""
echo "=================================================================="
echo " Submission complete!"
echo " Total active adatom jobs submitted : $TOTAL_SUBMITTED"
echo " Converged clean calculations kept : $SKIPPED_CLEAN"
echo " Check queue anytime with: squeue -u \$USER"
echo "=================================================================="
