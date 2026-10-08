#!/usr/bin/env python3
"""
setup_lobster_cohp_calculations.py

Prepares VASP static SCF and LOBSTER calculation directories for:
6 systems:
  - Adsorbed: Co, Fe, Ni (threefold surface hollow S2)
  - Embedded: Co, Fe, Ni (distorted sixfold coordination)

Under:
  PBE + D3(BJ) + U_all (U_Cr = 3.29 eV, U_TM = 3.29 eV)

VASP Requirements for LOBSTER:
  - ISYM = -1 (no symmetry reduction)
  - LWAVE = .TRUE. (write full binary WAVECAR)
  - NSW = 0, IBRION = -1 (static SCF)
  - NBANDS = 216 (sufficient empty bands for LOBSTER projection completeness)
  - EDIFF = 1E-06, PREC = Accurate
"""

import os
import shutil
from ase.io import read, write

BASE_DIR = "/home/cr/simulations/crcl3-HER"
ROOT_CALCS = os.path.join(BASE_DIR, "crcl3-newcals")
TARGET_BASE = os.path.join(ROOT_CALCS, "cohp_lobster_Uall")
os.makedirs(TARGET_BASE, exist_ok=True)

systems = [
    # (motif, tm, src_poscar, magmom, ldau_u)
    ("adsorbed", "Co", "crcl3-2x2-co_ads-with-U/yes_vdw/S2/CONTCAR", "8*3.0 24*0.0 1*3.0", "3.29 0.00 3.29"),
    ("adsorbed", "Fe", "crcl3-2x2-fe_ads-with-U/yes_vdw/S2/CONTCAR", "8*3.0 24*0.0 1*4.0", "3.29 0.00 3.29"),
    ("adsorbed", "Ni", "crcl3-2x2-ni_ads-with-U/yes_vdw/S2/CONTCAR", "8*3.0 24*0.0 1*2.0", "3.29 0.00 3.29"),
    
    ("embedded", "Co", "crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Co/clean/CONTCAR", "8*3.0 24*0.0 1*3.0", "3.29 0.00 3.29"),
    ("embedded", "Fe", "crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Fe/clean/CONTCAR", "8*3.0 24*0.0 1*4.0", "3.29 0.00 3.29"),
    ("embedded", "Ni", "crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Ni/clean/CONTCAR", "8*3.0 24*0.0 1*2.0", "3.29 0.00 3.29"),
]

INCAR_TEMPLATE = """# Monolayer CrCl3 (2x2) + {tm} ({motif}) Static SCF for LOBSTER COHP (U_all = 3.29 eV)
PREC     = Accurate
ENCUT    = 500
EDIFF    = 1E-06
IBRION   = -1
NSW      = 0
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
LREAL    = .FALSE.
NCORE    = 4
ISYM     = -1
NBANDS   = 216
LWAVE    = .TRUE.
LCHARG   = .TRUE.
"""

KPOINTS_551 = """K-Points
0
Gamma
 5  5  1
 0  0  0
"""

LOBSTERIN_TEMPLATE = """basisSet pbeVASPfit2015
COHPstartEnergy -15.0
COHPendEnergy 5.0
saveProjectionToFile

# TM (atom 33) to neighboring Cl atoms
cohpBetweenAtom 33 and 9
cohpBetweenAtom 33 and 10
cohpBetweenAtom 33 and 11
cohpBetweenAtom 33 and 12
cohpBetweenAtom 33 and 13
cohpBetweenAtom 33 and 14
cohpBetweenAtom 33 and 15
cohpBetweenAtom 33 and 16
cohpBetweenAtom 33 and 17
cohpBetweenAtom 33 and 18
cohpBetweenAtom 33 and 19
cohpBetweenAtom 33 and 20
cohpBetweenAtom 33 and 21
cohpBetweenAtom 33 and 22
cohpBetweenAtom 33 and 23
cohpBetweenAtom 33 and 24
cohpBetweenAtom 33 and 25
cohpBetweenAtom 33 and 26
cohpBetweenAtom 33 and 27
cohpBetweenAtom 33 and 28
cohpBetweenAtom 33 and 29
cohpBetweenAtom 33 and 30
cohpBetweenAtom 33 and 31
cohpBetweenAtom 33 and 32
"""

SLURM_TEMPLATE = """#!/bin/bash
#SBATCH -J {tm}_{motif}_cohp
#SBATCH -p nanotubo
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=03:00:00
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

# 1. Run VASP static SCF with LWAVE=.TRUE. and ISYM=-1
mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1

# 2. Run LOBSTER if WAVECAR exists
if [ -s WAVECAR ]; then
    echo "[$(date)] VASP SCF completed. Running LOBSTER COHP analysis..."
    if [ -x ~/.local/bin/lobster ]; then
        ~/.local/bin/lobster > lobster.out 2>&1
    elif which lobster >/dev/null 2>&1; then
        lobster > lobster.out 2>&1
    fi
    echo "[$(date)] LOBSTER completed with exit code $?"
fi
"""

def main():
    created = []
    for motif, tm, src_rel, magmom, ldau_u in systems:
        target_dir = os.path.join(TARGET_BASE, motif, tm)
        os.makedirs(target_dir, exist_ok=True)
        
        src_full = os.path.join(ROOT_CALCS, src_rel)
        if not os.path.exists(src_full):
            print(f"[WARN] Missing source: {src_full}")
            continue
            
        atoms = read(src_full)
        write(os.path.join(target_dir, "POSCAR"), atoms, format="vasp", direct=True, vasp5=True)
        
        # Source POTCAR
        pot_src = os.path.join(ROOT_CALCS, f"crcl3-2x2-co_ads-with-U/yes_vdw/S2/POTCAR")
        # Ensure element order: Cr, Cl, TM
        if tm == "Co":
            shutil.copy2(pot_src, os.path.join(target_dir, "POTCAR"))
        else:
            # Copy from matching directory
            pot_alt = os.path.join(ROOT_CALCS, f"crcl3-2x2-{tm.lower()}_ads-with-U/yes_vdw/S2/POTCAR")
            if os.path.exists(pot_alt):
                shutil.copy2(pot_alt, os.path.join(target_dir, "POTCAR"))
            else:
                shutil.copy2(pot_src, os.path.join(target_dir, "POTCAR"))
                
        with open(os.path.join(target_dir, "KPOINTS"), "w") as f:
            f.write(KPOINTS_551)
            
        incar_str = INCAR_TEMPLATE.format(tm=tm, motif=motif, magmom=magmom, ldau_u=ldau_u)
        with open(os.path.join(target_dir, "INCAR"), "w") as f:
            f.write(incar_str)
            
        with open(os.path.join(target_dir, "lobsterin"), "w") as f:
            f.write(LOBSTERIN_TEMPLATE)
            
        slurm_str = SLURM_TEMPLATE.format(tm=tm, motif=motif)
        with open(os.path.join(target_dir, "run_vasp.sh"), "w") as f:
            f.write(slurm_str)
        os.chmod(os.path.join(target_dir, "run_vasp.sh"), 0o755)
        
        created.append(f"{motif}/{tm}")
        
    print(f"[OK] Successfully prepared {len(created)} COHP LOBSTER calculation directories in:")
    print(f"     {TARGET_BASE}")
    for c in created:
        print(f"     - {c}")

if __name__ == "__main__":
    main()
