#!/usr/bin/env python3
"""
run_pristine_bands.py
Sets up and executes pristine CrCl3 monolayer band structure and PDOS calculations
under PBE + DFT-D3(BJ) (IVDW = 12) + Dudarev U_Cr = 3.29 eV.
Follows the Ponytail VASP protocol (zero-redundancy, native defaults first).
"""

import os
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRISTINE_DIR = os.path.join(BASE_DIR, "bands_pristine_vdw12_Ucr")
POTCAR_SRC = os.path.join(BASE_DIR, "..", "first-principles-hubbard-u", "pseudopotentials", "POTCAR_CrCl3_1x1")

# High-symmetry path Gamma - M - K - Gamma for 2D hexagonal monolayer
KPOINTS_PATH = """K-Path for Monolayer CrCl3 (Gamma - M - K - Gamma)
25
Line-mode
Reciprocal
0.0000000000  0.0000000000  0.0000000000  \\Gamma
0.5000000000  0.0000000000  0.0000000000  M

0.5000000000  0.0000000000  0.0000000000  M
0.3333333333  0.3333333333  0.0000000000  K

0.3333333333  0.3333333333  0.0000000000  K
0.0000000000  0.0000000000  0.0000000000  \\Gamma
"""

def setup_cell(target_dir, poscar_src, kmesh, magmom_str):
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy(poscar_src, os.path.join(target_dir, "POSCAR"))
    shutil.copy(POTCAR_SRC, os.path.join(target_dir, "POTCAR"))
    
    # 1. KPOINTS for SCF
    with open(os.path.join(target_dir, "KPOINTS_SCF"), "w") as f:
        f.write(f"Uniform mesh for SCF and PDOS\n0\nGamma\n{kmesh[0]} {kmesh[1]} {kmesh[2]}\n0 0 0\n")
        
    # 2. KPOINTS for Bands
    with open(os.path.join(target_dir, "KPOINTS_BANDS"), "w") as f:
        f.write(KPOINTS_PATH)
        
    # 3. INCAR for SCF (Ponytail compliant: zero redundancy)
    incar_scf = f"""PREC     = Accurate
ENCUT    = 400.0
EDIFF    = 1.0E-06

ISPIN    = 2
MAGMOM   = {magmom_str}

ISMEAR   = 0
SIGMA    = 0.05
NCORE    = 4

IVDW     = 12

LDAU     = .TRUE.
LDAUL    = 2 -1
LDAUU    = 3.29 0.00
LMAXMIX  = 4
LASPH    = .TRUE.

LORBIT   = 11
NEDOS    = 2001
EMIN     = -15
EMAX     = 10
"""
    with open(os.path.join(target_dir, "INCAR_SCF"), "w") as f:
        f.write(incar_scf)
        
    # 4. INCAR for Bands (Ponytail compliant)
    incar_bands = """PREC     = Accurate
ENCUT    = 400.0
EDIFF    = 1.0E-06

ISPIN    = 2
ICHARG   = 11

ISMEAR   = 0
SIGMA    = 0.05
NCORE    = 4

IVDW     = 12

LDAU     = .TRUE.
LDAUL    = 2 -1
LDAUU    = 3.29 0.00
LMAXMIX  = 4
LASPH    = .TRUE.

LORBIT   = 11

LWAVE    = .FALSE.
LCHARG   = .FALSE.
"""
    with open(os.path.join(target_dir, "INCAR_BANDS"), "w") as f:
        f.write(incar_bands)
        
    print(f"Setup complete for {target_dir}")

if __name__ == '__main__':
    # 1x1 Primitive Cell
    p1 = os.path.join(PRISTINE_DIR, "1x1_primitive")
    pos1 = os.path.join(BASE_DIR, "..", "past-dirs", "relax-crcl3-i3-vdw-u", "U_3", "CONTCAR")
    setup_cell(p1, pos1, (11, 11, 1), "2*3.0 6*0.0")
    
    # 2x2 Supercell
    p2 = os.path.join(PRISTINE_DIR, "2x2_supercell")
    pos2 = os.path.join(BASE_DIR, "crcl3_2x2_CoFeNi_vdw12_U_structures", "pristine", "substrate", "clean_2x2", "CONTCAR")
    setup_cell(p2, pos2, (5, 5, 1), "8*3.0 24*0.0")
