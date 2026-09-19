#!/bin/bash
# ==============================================================================
# MONITORING & CONVERGENCE STATUS FOR CrCl3 3x3 H-ADSORPTION CALCULATIONS
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS=("no_vdw" "yes_vdw")
SITES=("clean" "S1" "S2" "S3")

echo "=========================================================================================="
echo " CrCl3 3x3 H-Adsorption Calculation Status Matrix"
echo " Host: $(hostname) | Date: $(date)"
echo "=========================================================================================="
printf "%-10s %-8s %-12s %-12s %-18s %-15s %-10s\n" "Variant" "Site" "Slurm State" "Ionic Steps" "Free Energy (eV)" "Max Force (eV/A)" "Status"
echo "------------------------------------------------------------------------------------------"

for V in "${VARIANTS[@]}"; do
    for S in "${SITES[@]}"; do
        CALC_DIR="$SCRIPT_DIR/$V/$S"
        JOB_NAME="H3x3_${S}_${V//_}"
        
        SLURM_STATE=$(squeue -u "$USER" --name="$JOB_NAME" -h -o "%T" 2>/dev/null)
        if [ -z "$SLURM_STATE" ]; then
            SLURM_STATE="NONE"
        fi

        if [ -f "$CALC_DIR/OSZICAR" ]; then
            IONIC_STEPS=$(grep -c "F=" "$CALC_DIR/OSZICAR" 2>/dev/null | tr -d "\n" || echo "0")
            LAST_ENERGY=$(grep "F=" "$CALC_DIR/OSZICAR" | tail -n 1 | awk '{print $5}' 2>/dev/null || echo "N/A")
        else
            IONIC_STEPS="0"
            LAST_ENERGY="N/A"
        fi

        MAX_FORCE="N/A"
        if [ "$SLURM_STATE" == "RUNNING" ]; then
            STATUS="RUNNING"
        elif [ "$SLURM_STATE" == "PENDING" ]; then
            STATUS="QUEUED"
        else
            STATUS="NOT_SUBMITTED"
        fi

        if [ -f "$CALC_DIR/OUTCAR" ]; then
            if grep -q "reached required accuracy" "$CALC_DIR/OUTCAR" 2>/dev/null; then
                STATUS="CONVERGED"
            elif [ "$SLURM_STATE" == "NONE" ]; then
                STATUS="STOPPED"
            fi
            
            # Compute true maximum residual force magnitude across all atoms in the last step
            LAST_FORCE=$(awk '/TOTAL-FORCE/{flag=1; count=0; maxf=0; next} /---/{if(flag) count++; if(count==2){flag=0; print maxf}; next} flag{f=sqrt($4*$4+$5*$5+$6*$6); if(f>maxf) maxf=f}' "$CALC_DIR/OUTCAR" 2>/dev/null | tail -n 1)
            if [ -n "$LAST_FORCE" ]; then
                printf -v MAX_FORCE "%.4f" "$LAST_FORCE" 2>/dev/null || MAX_FORCE="$LAST_FORCE"
            fi
        fi

        printf "%-10s %-8s %-12s %-12s %-18s %-15s %-10s\n" "$V" "$S" "$SLURM_STATE" "$IONIC_STEPS" "$LAST_ENERGY" "$MAX_FORCE" "$STATUS"
    done
done
echo "=========================================================================================="
