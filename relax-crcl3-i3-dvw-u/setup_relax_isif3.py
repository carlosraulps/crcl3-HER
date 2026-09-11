#!/usr/bin/env python3
"""
setup_relax_isif3.py
Sets up the complete U = 0 .. 6 eV calculation suite for CrCl3 1x1 with:
- LATTICE_CONSTRAINTS = .TRUE. .TRUE. .FALSE.
- ISIF = 3
All other inputs (POSCAR, POTCAR, KPOINTS, and INCAR flags) are kept identical
to the verified relaxed-crcl3-vdw-u baseline.
"""

import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.dirname(SCRIPT_DIR) # crcl3-1x1/

U_VALUES = [0, 1, 2, 3, 4, 5, 6]

print("Setting up relax-crcl3-i3-dvw-u suite for U = 0 .. 6 eV...")

for u in U_VALUES:
    u_str = f"U_{u}"
    target_dir = os.path.join(SCRIPT_DIR, u_str)
    ref_u_dir = os.path.join(REF_DIR, u_str)
    scratch_dir = f"/home/cr/scratch_vasp/relax-crcl3-i3-dvw-u/{u_str}"
    
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(scratch_dir, exist_ok=True)
    
    # 1. Copy POSCAR, POTCAR, KPOINTS from ref
    for f in ["POSCAR", "POTCAR", "KPOINTS"]:
        src = os.path.join(ref_u_dir, f)
        dst = os.path.join(target_dir, f)
        shutil.copyfile(src, dst)
        
    # 2. Generate INCAR by modifying ref INCAR:
    # Replace ISIF = 2 with ISIF = 3 and insert LATTICE_CONSTRAINTS
    ref_incar_path = os.path.join(ref_u_dir, "INCAR")
    with open(ref_incar_path, "r") as f:
        incar_lines = f.readlines()
        
    new_incar_lines = []
    for line in incar_lines:
        if line.strip().startswith("ISIF"):
            new_incar_lines.append("ISIF     = 3           # Relax ions and in-plane lattice parameters with fixed vacuum constraint\n")
            new_incar_lines.append("LATTICE_CONSTRAINTS = .TRUE. .TRUE. .FALSE. # Free a and b (x and y), strictly fix c (z-axis / vacuum preservation)\n")
        elif "SYSTEM" in line and "SYSTEM   =" in line:
            new_incar_lines.append(f"SYSTEM   = CrCl3-1x1 ISIF3 LATTICE_CONSTRAINTS (D3 + U={u}eV)\n")
        else:
            new_incar_lines.append(line)
            
    with open(os.path.join(target_dir, "INCAR"), "w") as f:
        f.writelines(new_incar_lines)
        
    # 3. Generate job.sh
    job_sh_content = f"""#!/bin/bash
#SBATCH -J CrCl3_i3_U_{u}
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --exclusive
#SBATCH --time=12:00:00

PROJECT_DIR="{target_dir}"
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
cp "$SCRATCH_DIR"/OUTCAR "$SCRATCH_DIR"/CONTCAR "$SCRATCH_DIR"/EIGENVAL "$SCRATCH_DIR"/DOSCAR "$SCRATCH_DIR"/vasprun.xml "$SCRATCH_DIR"/OSZICAR "$SCRATCH_DIR"/vasp_run.log "$PROJECT_DIR"/ 2>/dev/null || true

echo "Completed at $(date) with exit code $EXIT_CODE"
exit $EXIT_CODE
"""
    job_sh_path = os.path.join(target_dir, "job.sh")
    with open(job_sh_path, "w") as f:
        f.write(job_sh_content)
    os.chmod(job_sh_path, 0o755)
    
    print(f"  -> {u_str} successfully prepared.")

print("\nAll 7 calculation directories generated with verified inputs.")
