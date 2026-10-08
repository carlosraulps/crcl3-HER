#!/usr/bin/env python3
"""
setup_full_u_all_sites.py

Prepares VASP calculation directories and inputs for:
CrCl3 (2x2) Monolayer functionalized with Co, Fe, Ni across all 3 sites (S1, S2, S3)
with Hubbard U = 3.29 eV applied to ALL transition metal species:
  - U(Cr) = 3.29 eV
  - U(TM) = 3.29 eV (TM = Co, Fe, Ni)
under PBE + DFT-D3(BJ) (IVDW = 12).
"""

import os
import shutil

BASE_DIR = "/home/cr/simulations/crcl3-HER"
ROOT_CALCS = os.path.join(BASE_DIR, "crcl3-newcals")
TARGET_BASE = os.path.join(ROOT_CALCS, "crcl3-2x2-CoFeNi-sites-vdw12-U_all3.29")
os.makedirs(TARGET_BASE, exist_ok=True)

tm_configs = [
    # (metal, site_label, src_dir, magmom, ldau_u)
    ("Co", "S1", "crcl3-2x2-co_ads-with-U/yes_vdw/S1", "8*3.0 24*0.0 1*3.0", "3.29 0.00 3.29"),
    ("Co", "S2", "crcl3-2x2-co_ads-with-U/yes_vdw/S2", "8*3.0 24*0.0 1*3.0", "3.29 0.00 3.29"),
    ("Co", "S3", "crcl3-2x2-co_ads-with-U/yes_vdw/S3", "8*3.0 24*0.0 1*3.0", "3.29 0.00 3.29"),
    
    ("Fe", "S1", "crcl3-2x2-fe_ads-with-U/yes_vdw/S1", "8*3.0 24*0.0 1*4.0", "3.29 0.00 3.29"),
    ("Fe", "S2", "crcl3-2x2-fe_ads-with-U/yes_vdw/S2", "8*3.0 24*0.0 1*4.0", "3.29 0.00 3.29"),
    ("Fe", "S3", "crcl3-2x2-fe_ads-with-U/yes_vdw/S3", "8*3.0 24*0.0 1*4.0", "3.29 0.00 3.29"),
    
    ("Ni", "S1", "crcl3-2x2-ni_ads-with-U/yes_vdw/S1", "8*3.0 24*0.0 1*2.0", "3.29 0.00 3.29"),
    ("Ni", "S2", "crcl3-2x2-ni_ads-with-U/yes_vdw/S2", "8*3.0 24*0.0 1*2.0", "3.29 0.00 3.29"),
    ("Ni", "S3", "crcl3-2x2-ni_ads-with-U/yes_vdw/S3", "8*3.0 24*0.0 1*2.0", "3.29 0.00 3.29"),
]

INCAR_TEMPLATE = """# Monolayer CrCl3 (2x2) + {tm} ({site}) Relaxation with U_all = 3.29 eV + PBE-D3(BJ)
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
MAGMOM   = {magmom}
IVDW     = 12
LDAU     = .TRUE.
LDAUTYPE = 2
LDAUL    = 2 -1 2
LDAUU    = {ldau_u}
LDAUJ    = 0.00 0.00 0.00
LREAL    = Auto
NCORE    = 4
LCHARG   = .FALSE.
LWAVE    = .FALSE.
LDIPOL   = .TRUE.
IDIPOL   = 3
DIPOL    = 0.5 0.5 0.5
"""

KPOINTS_CONTENT = """K-Points
0
Gamma
 5  5  1
 0  0  0
"""

SLURM_TEMPLATE = """#!/bin/bash
#SBATCH -J {tm}_{site}_Uall
#SBATCH -p nanotubo
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
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

def main():
    created = []
    for tm, site, src_rel, magmom, ldau_u in tm_configs:
        target_dir = os.path.join(TARGET_BASE, tm, site)
        os.makedirs(target_dir, exist_ok=True)
        
        src_full = os.path.join(ROOT_CALCS, src_rel)
        pos_src = os.path.join(src_full, "CONTCAR")
        if not os.path.exists(pos_src) or os.path.getsize(pos_src) < 100:
            pos_src = os.path.join(src_full, "POSCAR")
        shutil.copy2(pos_src, os.path.join(target_dir, "POSCAR"))
        
        pot_src = os.path.join(src_full, "POTCAR")
        shutil.copy2(pot_src, os.path.join(target_dir, "POTCAR"))
        
        with open(os.path.join(target_dir, "KPOINTS"), "w") as f:
            f.write(KPOINTS_CONTENT)
            
        incar_str = INCAR_TEMPLATE.format(tm=tm, site=site, magmom=magmom, ldau_u=ldau_u)
        with open(os.path.join(target_dir, "INCAR"), "w") as f:
            f.write(incar_str)
            
        slurm_str = SLURM_TEMPLATE.format(tm=tm, site=site)
        with open(os.path.join(target_dir, "run_vasp.sh"), "w") as f:
            f.write(slurm_str)
        os.chmod(os.path.join(target_dir, "run_vasp.sh"), 0o755)
        
        created.append(f"{tm}/{site}")

    print(f"[OK] Successfully set up {len(created)} U_all site calculation directories in:")
    print(f"     {TARGET_BASE}")
    for c in created:
        print(f"     - {c}")

if __name__ == "__main__":
    main()
