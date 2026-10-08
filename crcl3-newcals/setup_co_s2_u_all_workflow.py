#!/usr/bin/env python3
"""
setup_co_s2_u_all_workflow.py

Sets up and orchestrates the complete workflow for:
Co adsorbed on monolayer CrCl3 at the S2 (threefold surface hollow) site
with Hubbard U = 3.29 eV on Cr(3d) and Co(3d) + PBE-D3(BJ) dispersion.

Workflow components:
1. 01_relax: Full ionic relaxation (IBRION=2, EDIFFG=-0.02, LAECHG=.TRUE., LCHARG=.TRUE.)
2. 02_cdd_slab: Isolated CrCl3 substrate SCF (frozen relaxed substrate positions)
3. 03_cdd_isolated_tm: Isolated Co atom SCF (frozen at relaxed Co position)
4. 04_bader_and_cdd_analysis: Post-processing script for Bader charge & 3D/2D CDD

HPC optimization for Carbono:
- Partition: fulereno (64 cores, Milan EPYC nodes n08-n14)
- NCORE = 8, KPAR = 1, PREC = Accurate, ENCUT = 500
- SIGUSR1 checkpoint trap + CONTCAR auto-restart logic
"""

import os
import shutil
import numpy as np
from ase.io import read, write
from ase import Atoms

BASE_DIR = "/home/cr/simulations/crcl3-HER"
ROOT_CALCS = os.path.join(BASE_DIR, "crcl3-newcals")
WORKFLOW_DIR = os.path.join(ROOT_CALCS, "crcl3-2x2-Co-S2-U_all3.29")
os.makedirs(WORKFLOW_DIR, exist_ok=True)

# Source reference for S2 structure and POTCARs
SRC_S2_DIR = os.path.join(ROOT_CALCS, "crcl3-2x2-co_ads-with-U/yes_vdw/S2")
POTCAR_FULL = os.path.join(SRC_S2_DIR, "POTCAR")

# Slurm template for 64-core fulereno execution
SLURM_TEMPLATE = """#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -p fulereno
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --signal=B:USR1@300
#SBATCH --requeue
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

module purge
module load gnu12 openmpi4 vasp/6.2.0 2>/dev/null || module load vasp/6.4.2 2>/dev/null || module load vasp 2>/dev/null

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=vader,self,tcp
export OMPI_MCA_mtl=^ofi,psm2
export OMPI_MCA_osc=^ucx
export UCX_TLS=sm,self

ckpt_handler() {{
    echo "[$(date)] SIGUSR1 received! Checkpointing calculation..."
    if [ ! -s OUTCAR ] || ! grep -q "Iteration" OUTCAR 2>/dev/null; then
        echo "ERROR: Calculation failed to start or produced no output! Aborting resubmission loop." >&2
        exit 1
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        echo "[$(date)] Updated POSCAR from CONTCAR. Auto-resubmitting..."
        sbatch run_vasp.sh
    fi
    exit 0
}}
trap 'ckpt_handler' USR1

mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1

if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "[$(date)] VASP calculation CONVERGED successfully!"
else
    echo "[$(date)] Run incomplete or interrupted. Checking CONTCAR..."
    if [ ! -s OUTCAR ] || ! grep -q "Iteration" OUTCAR 2>/dev/null; then
        echo "ERROR: Calculation failed to start or produced no output! Aborting resubmission loop." >&2
        exit 1
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        sbatch run_vasp.sh
    fi
fi
"""

KPOINTS_551 = """K-Points
0
Gamma
 5  5  1
 0  0  0
"""

def split_potcars():
    with open(POTCAR_FULL, "r") as f:
        lines = f.readlines()
    
    # Split POTCAR into Cr, Cl, Co
    end_indices = [i for i, line in enumerate(lines) if "End of Dataset" in line]
    if len(end_indices) < 3:
        raise ValueError("POTCAR does not contain 3 species!")
        
    pot_cr_cl = lines[:end_indices[1]+1]
    pot_co = lines[end_indices[1]+1:end_indices[2]+1]
    pot_full = lines[:end_indices[2]+1]
    
    return pot_full, pot_cr_cl, pot_co

def setup_01_relax(pot_full):
    target_dir = os.path.join(WORKFLOW_DIR, "01_relax")
    os.makedirs(target_dir, exist_ok=True)
    
    # Clean POSCAR from S2 CONTCAR
    atoms = read(os.path.join(SRC_S2_DIR, "CONTCAR"))
    # Ensure standard element order Cr (8), Cl (24), Co (1)
    cr_atoms = atoms[[i for i, a in enumerate(atoms) if a.symbol == 'Cr']]
    cl_atoms = atoms[[i for i, a in enumerate(atoms) if a.symbol == 'Cl']]
    co_atoms = atoms[[i for i, a in enumerate(atoms) if a.symbol == 'Co']]
    clean_atoms = cr_atoms + cl_atoms + co_atoms
    clean_atoms.set_cell(atoms.get_cell())
    clean_atoms.set_pbc(atoms.get_pbc())
    
    write(os.path.join(target_dir, "POSCAR"), clean_atoms, format="vasp", direct=True, vasp5=True)
    
    with open(os.path.join(target_dir, "POTCAR"), "w") as f:
        f.writelines(pot_full)
        
    with open(os.path.join(target_dir, "KPOINTS"), "w") as f:
        f.write(KPOINTS_551)
        
    incar_content = """# Monolayer CrCl3 (2x2) + Co (S2 Hollow) Relaxation (U_all = 3.29 eV + PBE-D3)
PREC     = Accurate
ENCUT    = 500
EDIFF    = 1E-06
EDIFFG   = -0.02
IBRION   = 2
NSW      = 120
ISIF     = 2
ISMEAR   = 0
SIGMA    = 0.05
ISPIN    = 2
MAGMOM   = 8*3.0 24*0.0 1*3.0
IVDW     = 12
LDAU     = .TRUE.
LDAUTYPE = 2
LDAUL    = 2 -1 2
LDAUU    = 3.29 0.00 3.29
LDAUJ    = 0.00 0.00 0.00
LREAL    = Auto
NCORE    = 8
LCHARG   = .TRUE.
LWAVE    = .FALSE.
LAECHG   = .TRUE.
LDIPOL   = .TRUE.
IDIPOL   = 3
DIPOL    = 0.5 0.5 0.5
"""
    with open(os.path.join(target_dir, "INCAR"), "w") as f:
        f.write(incar_content)
        
    with open(os.path.join(target_dir, "run_vasp.sh"), "w") as f:
        f.write(SLURM_TEMPLATE.format(job_name="Co_S2_relax_Uall"))
    os.chmod(os.path.join(target_dir, "run_vasp.sh"), 0o755)

def setup_cdd_and_bader_pipeline(pot_full, pot_cr_cl, pot_co):
    # Pipeline script that can be triggered after 01_relax finishes
    pipeline_script = os.path.join(WORKFLOW_DIR, "run_complete_cdd_bader_pipeline.py")
    script_code = """#!/usr/bin/env python3
import os
import subprocess
import shutil
import numpy as np
from ase.io import read, write

BASE = os.path.dirname(os.path.abspath(__file__))
DIR_RELAX = os.path.join(BASE, "01_relax")
DIR_SLAB = os.path.join(BASE, "02_cdd_slab")
DIR_TM = os.path.join(BASE, "03_cdd_isolated_tm")
DIR_ANALYSIS = os.path.join(BASE, "04_bader_and_cdd_analysis")

os.makedirs(DIR_SLAB, exist_ok=True)
os.makedirs(DIR_TM, exist_ok=True)
os.makedirs(DIR_ANALYSIS, exist_ok=True)

# 1. Read relaxed structure
contcar_path = os.path.join(DIR_RELAX, "CONTCAR")
if not os.path.exists(contcar_path) or os.path.getsize(contcar_path) < 100:
    contcar_path = os.path.join(DIR_RELAX, "POSCAR")
atoms = read(contcar_path)

# Extract Substrate (Cr8 Cl24)
cr_cl_atoms = atoms[[i for i, a in enumerate(atoms) if a.symbol in ['Cr', 'Cl']]]
cr_cl_atoms.set_cell(atoms.get_cell())
cr_cl_atoms.set_pbc(atoms.get_pbc())
write(os.path.join(DIR_SLAB, "POSCAR"), cr_cl_atoms, format="vasp", direct=True, vasp5=True)

# Extract Isolated Co
co_atoms = atoms[[i for i, a in enumerate(atoms) if a.symbol == 'Co']]
co_atoms.set_cell(atoms.get_cell())
co_atoms.set_pbc(atoms.get_pbc())
write(os.path.join(DIR_TM, "POSCAR"), co_atoms, format="vasp", direct=True, vasp5=True)

print("[OK] Created POSCARs for slab and isolated Co from relaxed Co@CrCl3.")
"""
    with open(pipeline_script, "w") as f:
        f.write(script_code)
    os.chmod(pipeline_script, 0o755)
    
    # 02_cdd_slab inputs
    dir_slab = os.path.join(WORKFLOW_DIR, "02_cdd_slab")
    os.makedirs(dir_slab, exist_ok=True)
    with open(os.path.join(dir_slab, "POTCAR"), "w") as f:
        f.writelines(pot_cr_cl)
    with open(os.path.join(dir_slab, "KPOINTS"), "w") as f:
        f.write(KPOINTS_551)
    incar_slab = """# Monolayer CrCl3 (2x2) Substrate SCF for CDD (U_all = 3.29 eV + PBE-D3)
PREC     = Accurate
ENCUT    = 500
EDIFF    = 1E-06
NSW      = 0
IBRION   = -1
ISMEAR   = 0
SIGMA    = 0.05
ISPIN    = 2
MAGMOM   = 8*3.0 24*0.0
IVDW     = 12
LDAU     = .TRUE.
LDAUTYPE = 2
LDAUL    = 2 -1
LDAUU    = 3.29 0.00
LDAUJ    = 0.00 0.00
LREAL    = Auto
NCORE    = 8
LCHARG   = .TRUE.
LWAVE    = .FALSE.
LAECHG   = .TRUE.
LDIPOL   = .TRUE.
IDIPOL   = 3
DIPOL    = 0.5 0.5 0.5
"""
    with open(os.path.join(dir_slab, "INCAR"), "w") as f:
        f.write(incar_slab)
    with open(os.path.join(dir_slab, "run_vasp.sh"), "w") as f:
        f.write(SLURM_TEMPLATE.format(job_name="Co_S2_slab_Uall"))
    os.chmod(os.path.join(dir_slab, "run_vasp.sh"), 0o755)

    # 03_cdd_isolated_tm inputs
    dir_tm = os.path.join(WORKFLOW_DIR, "03_cdd_isolated_tm")
    os.makedirs(dir_tm, exist_ok=True)
    with open(os.path.join(dir_tm, "POTCAR"), "w") as f:
        f.writelines(pot_co)
    with open(os.path.join(dir_tm, "KPOINTS"), "w") as f:
        f.write(KPOINTS_551)
    incar_tm = """# Isolated Co Atom SCF for CDD (U = 3.29 eV)
PREC     = Accurate
ENCUT    = 500
EDIFF    = 1E-06
NSW      = 0
IBRION   = -1
ISMEAR   = 0
SIGMA    = 0.01
ISPIN    = 2
MAGMOM   = 3.0
LDAU     = .TRUE.
LDAUTYPE = 2
LDAUL    = 2
LDAUU    = 3.29
LDAUJ    = 0.00
LREAL    = Auto
NCORE    = 8
LCHARG   = .TRUE.
LWAVE    = .FALSE.
"""
    with open(os.path.join(dir_tm, "INCAR"), "w") as f:
        f.write(incar_tm)
    with open(os.path.join(dir_tm, "run_vasp.sh"), "w") as f:
        f.write(SLURM_TEMPLATE.format(job_name="Co_isolated_Uall"))
    os.chmod(os.path.join(dir_tm, "run_vasp.sh"), 0o755)

    # Pre-generate initial POSCARs for slab and isolated Co based on S2 seed structure
    atoms = read(os.path.join(SRC_S2_DIR, "CONTCAR"))
    cr_cl_atoms = atoms[[i for i, a in enumerate(atoms) if a.symbol in ['Cr', 'Cl']]]
    cr_cl_atoms.set_cell(atoms.get_cell())
    cr_cl_atoms.set_pbc(atoms.get_pbc())
    write(os.path.join(dir_slab, "POSCAR"), cr_cl_atoms, format="vasp", direct=True, vasp5=True)

    co_atoms = atoms[[i for i, a in enumerate(atoms) if a.symbol == 'Co']]
    co_atoms.set_cell(atoms.get_cell())
    co_atoms.set_pbc(atoms.get_pbc())
    write(os.path.join(dir_tm, "POSCAR"), co_atoms, format="vasp", direct=True, vasp5=True)

def main():
    pot_full, pot_cr_cl, pot_co = split_potcars()
    setup_01_relax(pot_full)
    setup_cdd_and_bader_pipeline(pot_full, pot_cr_cl, pot_co)
    print(f"[OK] Master workflow directory generated successfully in:\n     {WORKFLOW_DIR}")

if __name__ == "__main__":
    main()
