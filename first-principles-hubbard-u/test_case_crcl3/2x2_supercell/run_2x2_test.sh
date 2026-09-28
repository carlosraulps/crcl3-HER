#!/bin/bash
# ==============================================================================
# run_2x2_test.sh
# Run Cococcioni Linear Response test on pristine CrCl3 2x2 supercell
# ==============================================================================
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
U_SCF_SCRIPTS="${SCRIPT_DIR}/../../scripts"

cd "${SCRIPT_DIR}"

echo "================================================================================"
echo " 🧪 Launching Cococcioni Linear Response on CrCl3 2x2 Supercell"
echo "================================================================================"

# Dry run / preparation
bash "${U_SCF_SCRIPTS}/run_u_scf_vasp.sh" \
    --poscar "${SCRIPT_DIR}/POSCAR" \
    --target-site 1 \
    --l-manifold 2 \
    --cluster huk \
    --partition "alto,medio,normal" \
    --tol 0.005 \
    --max-cycles 5 \
    --dry-run

echo ""
echo "✅ Directory preparation and perturbation grid setup verified successfully."
echo "To dispatch to Slurm on Huk, re-run without --dry-run."
