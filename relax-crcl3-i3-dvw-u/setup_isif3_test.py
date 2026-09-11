#!/usr/bin/env python3
"""
setup_isif3_test.py
Sets up test calculations with VASP 6.6.1 native cell constraint:
LATTICE_CONSTRAINTS = .TRUE. .TRUE. .FALSE.
ISIF = 3
ENCUT = 500 eV
NSW = 100
for U = 0 eV and U = 4 eV.
"""

import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_1X1_DIR = os.path.dirname(BASE_DIR)

test_u_values = [0.0, 4.0]

for u in test_u_values:
    u_str = f"U_{int(u)}"
    u_dir = os.path.join(BASE_DIR, u_str)
    os.makedirs(u_dir, exist_ok=True)
    
    # 1. Copy POSCAR, POTCAR, KPOINTS from original 1x1 U_0
    shutil.copyfile(os.path.join(REF_1X1_DIR, "U_0", "POSCAR"), os.path.join(u_dir, "POSCAR"))
    shutil.copyfile(os.path.join(REF_1X1_DIR, "U_0", "POTCAR"), os.path.join(u_dir, "POTCAR"))
    shutil.copyfile(os.path.join(REF_1X1_DIR, "U_0", "KPOINTS"), os.path.join(u_dir, "KPOINTS"))
    
    # 2. Build INCAR with LATTICE_CONSTRAINTS
    ldau_enabled = ".TRUE." if u > 0.0 else ".FALSE."
    
    incar_content = f"""# =========================================================================
# VASP INCAR: Test 2D Cell Relaxation with LATTICE_CONSTRAINTS (U={u:.1f} eV)
# LATTICE_CONSTRAINTS = .TRUE. .TRUE. .FALSE. (free a and b, strictly fix c/vacuum)
# =========================================================================

SYSTEM   = CrCl3-1x1 ISIF3 LATTICE_CONSTRAINTS U={u:.1f}eV
PREC     = Accurate
ENCUT    = 500.0
ALGO     = Normal
EDIFF    = 1.0E-06
NELM     = 100

ISPIN    = 2
MAGMOM   = 2*3.0 6*0.0

ISMEAR   = 0
SIGMA    = 0.05

IVDW     = 11

# --- Cell & Ionic Relaxation with Fixed Vacuum Constraint ---
IBRION   = 2
NSW      = 100
ISIF     = 3
LATTICE_CONSTRAINTS = .TRUE. .TRUE. .FALSE.
EDIFFG   = -0.01

LORBIT   = 11
LWAVE    = .FALSE.
LCHARG   = .FALSE.

NCORE    = 4
LASPH    = .TRUE.
LMAXMIX  = 4

LDAU     = {ldau_enabled}
LDAUTYPE = 2
LDAUL    = 2 -1
LDAUU    = {u:.1f} 0.0
LDAUJ    = 0.0 0.0
"""
    with open(os.path.join(u_dir, "INCAR"), "w") as f:
        f.write(incar_content)
        
    # 3. Create job script
    scratch_dir = f"/home/cr/scratch_vasp/test_isif3/{u_str}"
    job_script = f"""#!/bin/bash
#SBATCH -J CrCl3_isif3_{u_str}
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --exclusive
#SBATCH --time=12:00:00

PROJECT_DIR="{u_dir}"
SCRATCH_DIR="{scratch_dir}"

echo "Starting VASP job on $(hostname) at $(date)"
echo "Scratch directory: $SCRATCH_DIR"
echo "Project destination: $PROJECT_DIR"

rm -rf "$SCRATCH_DIR"
mkdir -p "$SCRATCH_DIR"
cp "$PROJECT_DIR"/INCAR "$PROJECT_DIR"/POSCAR "$PROJECT_DIR"/POTCAR "$PROJECT_DIR"/KPOINTS "$SCRATCH_DIR"/
cd "$SCRATCH_DIR"

export OMP_NUM_THREADS=1
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_rmaps_default_mapping_policy=:oversubscribe

run_vasp -np 16 -nt 1 > vasp_run.log 2>&1

EXIT_CODE=$?
echo "VASP finished with exit code $EXIT_CODE. Syncing results back to project..."
cp "$SCRATCH_DIR"/OUTCAR "$SCRATCH_DIR"/CONTCAR "$SCRATCH_DIR"/OSZICAR "$SCRATCH_DIR"/vasp_run.log "$PROJECT_DIR"/ 2>/dev/null || true

echo "Completed at $(date) with exit code $EXIT_CODE"
exit $EXIT_CODE
"""
    with open(os.path.join(u_dir, "job.sh"), "w") as f:
        f.write(job_script)
    os.chmod(os.path.join(u_dir, "job.sh"), 0o755)

print("Setup completed for U_0 and U_4 with LATTICE_CONSTRAINTS = .TRUE. .TRUE. .FALSE. and ISIF = 3.")
