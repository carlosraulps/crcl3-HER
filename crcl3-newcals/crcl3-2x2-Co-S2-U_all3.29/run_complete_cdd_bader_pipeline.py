#!/usr/bin/env python3
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
