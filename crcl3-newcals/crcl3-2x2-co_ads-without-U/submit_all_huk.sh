#!/bin/bash
# ==============================================================================
# Huk Cluster Submission Script for CrCl3 2x2 CO Adsorption
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Submitting all CO adsorption jobs on Huk..."

for vdw in no_vdw yes_vdw; do
    for site in S1 S2 S3; do
        target="$DIR/$vdw/$site"
        if [ -d "$target" ]; then
            if [ -f "$target/OUTCAR" ] && grep -q "General timing and accounting" "$target/OUTCAR" 2>/dev/null; then
                echo "  [$vdw/$site] Already converged. Skipping."
            else
                cd "$target"
                sbatch job.sh
                echo "  [$vdw/$site] Submitted to Huk (alto,medio)"
                cd "$DIR"
            fi
        fi
    done
done
echo "Done! Check status with: squeue -u $USER"
