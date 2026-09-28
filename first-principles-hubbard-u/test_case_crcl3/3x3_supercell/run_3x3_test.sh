#!/bin/bash
# ==============================================================================
# run_3x3_test.sh
# Run Cococcioni Linear Response test on CrCl3 3x3 supercell (d_image = 18.14 A)
# ==============================================================================
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
U_SCRIPTS="${SCRIPT_DIR}/../../scripts"

cd "${SCRIPT_DIR}"

echo "================================================================================"
echo " 🧪 Launching Cococcioni Linear Response on CrCl3 3x3 Supercell (72 atoms)"
echo "    Isolated atomic limit regime (d_image = 18.14 A)"
echo "================================================================================"

bash "${U_SCRIPTS}/run_u_scf_vasp.sh" \
    --poscar "${SCRIPT_DIR}/POSCAR" \
    --target-site 1 \
    --l-manifold 2 \
    --cluster huk \
    --partition "alto,medio,normal" \
    --tol 0.005 \
    --max-cycles 5 \
    --dry-run

echo ""
echo "✅ 3x3 supercell perturbation grid setup verified successfully."
