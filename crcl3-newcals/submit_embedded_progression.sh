#!/bin/bash
# ==============================================================================
#  submit_embedded_progression.sh
# ==============================================================================
#  Submits D3-only jobs first, and chains +U jobs with --dependency=afterok!
#  Target cluster selection:
#    Usage: ./submit_embedded_progression.sh [carbono|huk]
# ==============================================================================

CLUSTER=${1:-carbono}
SCRIPT_NAME="job_${CLUSTER}.sh"

echo "=========================================================="
echo " Submitting Progressive Embedded Calculations to $CLUSTER"
echo " Batch Script Target: $SCRIPT_NAME"
echo "=========================================================="

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for TM in co fe ni; do
    for STATE in clean H_ads; do
        D3_DIR="${BASE_DIR}/crcl3-2x2-${TM}_emb-without-U/${STATE}"
        U_DIR="${BASE_DIR}/crcl3-2x2-${TM}_emb-with-U/${STATE}"

        echo ""
        echo "--> Processing System: ${TM} (${STATE})"

        # 1. Submit D3-only calculation
        cd "${D3_DIR}"
        echo "Submitting D3 (without-U) in: ${D3_DIR}"
        SUBMIT_OUT=$(sbatch "${SCRIPT_NAME}")
        echo "Slurm Response: $SUBMIT_OUT"
        JOB_ID_D3=$(echo "$SUBMIT_OUT" | awk '{print $NF}')

        # 2. Submit +U calculation chained to D3 completion
        cd "${U_DIR}"
        echo "Submitting +U chained to Job $JOB_ID_D3 in: ${U_DIR}"
        SUBMIT_U_OUT=$(sbatch --dependency=afterok:${JOB_ID_D3} "${SCRIPT_NAME}")
        echo "Slurm Response: $SUBMIT_U_OUT"
    done
done

echo ""
echo "=========================================================="
echo " All embedded progressive calculations queued successfully!"
echo "=========================================================="
