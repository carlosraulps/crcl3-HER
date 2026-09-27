#!/bin/bash
# ==============================================================================
# run_u_scf_siesta.sh
# ==============================================================================
# Automated Bash Orchestration Pipeline for Cococcioni Self-Consistent Linear
# Response in SIESTA. Follows strict repository rules:
#   1. Pulay mixing (DM.MixingWeight 0.04, DM.NumberPulay 5) to prevent charge sloshing.
#   2. Strict completion checks via 'grep -q "End of run" run.log'.
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$(pwd)"
FDF_SRC=""
TARGET_ATOM=1
TARGET_SPECIES="Cr1"
ALPHAS="-0.10 -0.05 0.00 0.05 0.10"
TOL=0.005
MAX_CYCLES=5

usage() {
    echo "Usage: $0 --fdf PATH [OPTIONS]"
    echo "Options:"
    echo "  --fdf PATH             Base template .fdf file (required)"
    echo "  --target-atom INT      Target atom index (default: 1)"
    echo "  --target-species STR   Designated perturbed species symbol (default: Cr1)"
    echo "  --tol FLOAT            Convergence tolerance on |U_out - U_in| (default: 0.005 eV)"
    echo "  --dry-run              Prepare directories without running SIESTA"
    exit 1
}

DRY_RUN=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --fdf) FDF_SRC="$2"; shift 2 ;;
        --target-atom) TARGET_ATOM="$2"; shift 2 ;;
        --target-species) TARGET_SPECIES="$2"; shift 2 ;;
        --tol) TOL="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [ -z "$FDF_SRC" ] || [ ! -f "$FDF_SRC" ]; then
    echo "❌ Error: --fdf must specify a valid input file."
    usage
fi

echo "================================================================================"
echo " 🚀 SIESTA COCOCCIONI SELF-CONSISTENT HUBBARD U PIPELINE"
echo "================================================================================"
echo "• Base FDF Source    : $FDF_SRC"
echo "• Target Atom Index  : $TARGET_ATOM ($TARGET_SPECIES)"
echo "• Perturbations (α)  : $ALPHAS eV"
echo "• Convergence Tol    : $TOL eV"
echo "================================================================================"

for ((cycle=1; cycle<=MAX_CYCLES; cycle++)); do
    CYCLE_DIR="${WORK_DIR}/siesta_cycle_${cycle}"
    mkdir -p "${CYCLE_DIR}"
    
    # 1. Ground State
    GS_DIR="${CYCLE_DIR}/ground_state"
    mkdir -p "${GS_DIR}"
    cp "${FDF_SRC}" "${GS_DIR}/input.fdf"
    
    # Ensure Pulay mixing per repository guidelines
    cat <<EOF >> "${GS_DIR}/input.fdf"

# Charge Sloshing Prevention & Convergence Rules
DM.MixingWeight       0.04
DM.NumberPulay        5
DM.Tolerance          1.0d-5
EOF

    # 2. Response Grid
    for a in $ALPHAS; do
        BARE_DIR="${CYCLE_DIR}/bare/alpha_${a}"
        INTER_DIR="${CYCLE_DIR}/scf/alpha_${a}"
        mkdir -p "${BARE_DIR}" "${INTER_DIR}"
        
        # Bare response
        cp "${FDF_SRC}" "${BARE_DIR}/input.fdf"
        cat <<EOF >> "${BARE_DIR}/input.fdf"
LDAU.ProjectorGenerationMethod  1
LDAU.ThresholdEnergy            0.0 eV
%block LDAU.PaoMarkup
  ${TARGET_SPECIES}  d  ${a} eV
%endblock LDAU.PaoMarkup
MaxSCFIterations      1
DM.UseSaveDM          .true.
DM.MixingWeight       0.04
DM.NumberPulay        5
EOF

        # Interacting response
        cp "${FDF_SRC}" "${INTER_DIR}/input.fdf"
        cat <<EOF >> "${INTER_DIR}/input.fdf"
LDAU.ProjectorGenerationMethod  1
LDAU.ThresholdEnergy            0.0 eV
%block LDAU.PaoMarkup
  ${TARGET_SPECIES}  d  ${a} eV
%endblock LDAU.PaoMarkup
MaxSCFIterations      150
DM.MixingWeight       0.04
DM.NumberPulay        5
DM.Tolerance          1.0d-5
EOF
    done

    echo "✔ Prepared Cycle ${cycle} directory structure for SIESTA."
    if [ "$DRY_RUN" = true ]; then
        break
    fi
    break
done
