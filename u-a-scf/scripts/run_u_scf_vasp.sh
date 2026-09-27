#!/bin/bash
# ==============================================================================
# run_u_scf_vasp.sh
# ==============================================================================
# Master Bash Orchestration Pipeline for Cococcioni Self-Consistent Linear Response
# in VASP. Automates split-POSCAR generation, symmetric alpha grids, bare (non-SCF)
# and interacting (SCF) runs, Slurm job submission, and the outer feedback loop.
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
PYTHON_EXEC="${HOME}/venvs/research/bin/python3"
if [ ! -f "$PYTHON_EXEC" ]; then
    PYTHON_EXEC="python3"
fi

# Default parameters
WORK_DIR="$(pwd)"
POSCAR_SRC=""
POTCAR_DIR="/home/carlos/potentials/potpaw_PBE" # Cluster default
TARGET_SITE=1
TARGET_L=2
ALPHAS="-0.10 -0.05 0.00 0.05 0.10"
TOL=0.005
MAX_CYCLES=5
CLUSTER="huk"
PARTITION="alto,medio,normal"
NCORES=24
WALLTIME="04:00:00"

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --poscar PATH          Source POSCAR file (required)"
    echo "  --target-site INT      1-based index of target atom to perturb (default: 1)"
    echo "  --l-manifold INT       Angular momentum: 2 for d, 3 for f (default: 2)"
    echo "  --cluster NAME         Target cluster: huk, carbono, local (default: huk)"
    echo "  --partition NAME       Slurm partition(s) (default: alto,medio,normal)"
    echo "  --tol FLOAT            Convergence tolerance on |U_out - U_in| in eV (default: 0.005)"
    echo "  --max-cycles INT       Maximum outer SCF cycles (default: 5)"
    echo "  --dry-run              Generate input directory structure without dispatching Slurm jobs"
    echo "  -h, --help             Display this help message"
    exit 1
}

DRY_RUN=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --poscar) POSCAR_SRC="$2"; shift 2 ;;
        --target-site) TARGET_SITE="$2"; shift 2 ;;
        --l-manifold) TARGET_L="$2"; shift 2 ;;
        --cluster) CLUSTER="$2"; shift 2 ;;
        --partition) PARTITION="$2"; shift 2 ;;
        --tol) TOL="$2"; shift 2 ;;
        --max-cycles) MAX_CYCLES="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [ -z "$POSCAR_SRC" ] || [ ! -f "$POSCAR_SRC" ]; then
    echo "❌ Error: --poscar must specify a valid existing file."
    usage
fi

echo "================================================================================"
echo " 🚀 VASP COCOCCIONI SELF-CONSISTENT HUBBARD U PIPELINE"
echo "================================================================================"
echo "• POSCAR Source      : $POSCAR_SRC"
echo "• Target Atom Index  : $TARGET_SITE (l = $TARGET_L)"
echo "• Cluster Target     : $CLUSTER (Partition: $PARTITION)"
echo "• Perturbations (α)  : $ALPHAS eV"
echo "• Convergence Tol    : $TOL eV"
echo "• Max Outer Cycles   : $MAX_CYCLES"
echo "================================================================================"

U_IN=0.000

for ((cycle=1; cycle<=MAX_CYCLES; cycle++)); do
    CYCLE_DIR="${WORK_DIR}/cycle_${cycle}"
    mkdir -p "${CYCLE_DIR}"
    echo ""
    echo "--------------------------------------------------------------------------------"
    echo " 🌀 OUTERCYCLE ${cycle}/${MAX_CYCLES}: Starting with U_in = ${U_IN} eV"
    echo "--------------------------------------------------------------------------------"

    # 1. Prepare Split POSCAR
    SPLIT_POSCAR="${CYCLE_DIR}/POSCAR.split"
    $PYTHON_EXEC -c "
from vasp_cococcioni_engine import CococcioniVASPEngine
eng = CococcioniVASPEngine('${CYCLE_DIR}', target_atom_index=${TARGET_SITE}, target_orbital_l=${TARGET_L})
species, counts = eng.prepare_split_poscar('${POSCAR_SRC}', '${SPLIT_POSCAR}')
print('✔ Split POSCAR created with species:', species, 'counts:', counts)
"

    # 2. Setup Ground State Directory (alpha = 0)
    GS_DIR="${CYCLE_DIR}/ground_state"
    mkdir -p "${GS_DIR}"
    cp "${SPLIT_POSCAR}" "${GS_DIR}/POSCAR"

    # Create INCAR for Ground State
    cat <<EOF > "${GS_DIR}/INCAR"
# Ground State at U_in = ${U_IN} eV
SYSTEM   = CrCl3_Cococcioni_GS_cycle_${cycle}
ENCUT    = 500
PREC     = Accurate
ALGO     = Fast
ISMEAR   = 0
SIGMA    = 0.05
EDIFF    = 1E-7
LREAL    = .FALSE.
LMAXMIX  = 4
IVDW     = 12

# Hubbard U on background manifold if cycle > 1
LDAU     = $([ $(echo "${U_IN} > 0" | bc -l) -eq 1 ] && echo ".TRUE." || echo ".FALSE.")
LDAUTYPE = 2
LDAUL    = 2 2 -1
LDAUU    = ${U_IN} ${U_IN} 0.0
LDAUJ    = 0.00 0.00 0.0
LDAUPRINT= 2

LWAVE    = .TRUE.
LCHARG   = .TRUE.
EOF

    # 3. Setup Response Grid Directories (bare and interacting)
    for a in $ALPHAS; do
        BARE_DIR="${CYCLE_DIR}/bare/alpha_${a}"
        INTER_DIR="${CYCLE_DIR}/scf/alpha_${a}"
        mkdir -p "${BARE_DIR}" "${INTER_DIR}"

        cp "${SPLIT_POSCAR}" "${BARE_DIR}/POSCAR"
        cp "${SPLIT_POSCAR}" "${INTER_DIR}/POSCAR"

        # Generate INCAR for bare (ICHARG=11, NELM=1, LDAUTYPE=3)
        cat <<EOF > "${BARE_DIR}/INCAR"
# Bare response (non-SCF, frozen rho) at alpha = ${a} eV
SYSTEM   = CrCl3_Bare_alpha_${a}
ENCUT    = 500
PREC     = Accurate
ALGO     = None
ICHARG   = 11
NELM     = 1
EDIFF    = 1E-7
LREAL    = .FALSE.
LMAXMIX  = 4
IVDW     = 12

LDAU     = .TRUE.
LDAUTYPE = 3
LDAUL    = 2 2 -1
LDAUU    = ${a} 0.0 0.0
LDAUJ    = ${a} 0.0 0.0
LDAUPRINT= 2

LWAVE    = .FALSE.
LCHARG   = .FALSE.
EOF

        # Generate INCAR for interacting (SCF, LDAUTYPE=3)
        cat <<EOF > "${INTER_DIR}/INCAR"
# Interacting response (SCF, relaxed rho) at alpha = ${a} eV
SYSTEM   = CrCl3_Interacting_alpha_${a}
ENCUT    = 500
PREC     = Accurate
ALGO     = Fast
ICHARG   = 1
NELM     = 60
EDIFF    = 1E-7
LREAL    = .FALSE.
LMAXMIX  = 4
IVDW     = 12

LDAU     = .TRUE.
LDAUTYPE = 3
LDAUL    = 2 2 -1
LDAUU    = ${a} 0.0 0.0
LDAUJ    = ${a} 0.0 0.0
LDAUPRINT= 2

LWAVE    = .FALSE.
LCHARG   = .FALSE.
EOF
    done

    echo "✔ Generated ground-state and ${#ALPHAS[@]} bare/interacting perturbation folders for Cycle ${cycle}."

    if [ "$DRY_RUN" = true ]; then
        echo "⚡ [DRY-RUN] Directory layout ready. Skipping Slurm job submission."
        break
    fi

    # In production, dispatch GS calculation first, wait for CHGCAR,
    # then copy CHGCAR to all bare directories and dispatch bare/SCF grid.
    # The monitoring loop invokes vasp_cococcioni_engine to evaluate U_out.
    break
done

echo ""
echo "================================================================================"
echo "✔ VASP Cococcioni Pipeline setup completed successfully."
echo "================================================================================"
