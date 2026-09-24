#!/usr/bin/env python3
"""
setup_h_on_co_u.py

Reads the converged S2/CONTCAR (CrCl3-2x2-Co with U=3.29 eV),
places H directly atop Co at d(Co-H) = 1.44 Angstroms,
concatenates H POTCAR, and generates the H_ads/ calculation directory.
"""

import os
import shutil
import numpy as np
from ase.io import read, write

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
S2_DIR = os.path.join(BASE_DIR, "yes_vdw", "S2")
H_ADS_DIR = os.path.join(BASE_DIR, "yes_vdw", "H_ads")
H_POTCAR_SRC = "/home/cr/simulations/crcl3-HER/crcl3-newcals/H2_reference/yes_vdw/POTCAR"

INCAR_H_ADS = """# =========================================================================
# VASP INCAR: CrCl3 2x2 + Co-H Adsorbed State (PBE+D3(BJ) + U=3.29eV)
# Hydrogen adsorbed directly atop Co adatom at S2 Hollow site
# =========================================================================

PREC     = Accurate
ENCUT    = 400.0
EDIFF    = 1.0E-06
NELM     = 100

ISPIN    = 2
MAGMOM   = 8*3.0 24*0.0 1*3.0 1*0.5

ISMEAR   = 0
SIGMA    = 0.05

NCORE    = 4
LREAL    = Auto

IVDW     = 12

IBRION   = 2
NSW      = 100
EDIFFG   = -0.025

LASPH    = .TRUE.
LMAXMIX  = 4

LDAU     = .TRUE.
LDAUL    = 2 -1 -1 -1
LDAUU    = 3.29 0.0 0.0 0.0

LDIPOL   = .TRUE.
IDIPOL   = 3
DIPOL    = 0.5 0.5 0.5

LWAVE    = .FALSE.
LCHARG   = .FALSE.
"""

def main():
    s2_contcar = os.path.join(S2_DIR, "CONTCAR")
    if not os.path.exists(s2_contcar) or os.path.getsize(s2_contcar) == 0:
        print(f"WAIT: S2 calculation has not yet produced CONTCAR ({s2_contcar}).")
        return

    os.makedirs(H_ADS_DIR, exist_ok=True)
    atoms = read(s2_contcar)
    
    # Locate Co atom (last atom in substrate)
    co_indices = [i for i, a in enumerate(atoms) if a.symbol == "Co"]
    if not co_indices:
        raise ValueError("No Co atom found in S2 CONTCAR!")
    co_idx = co_indices[0]
    co_pos = atoms.positions[co_idx]
    
    # Place H 1.44 A above Co along z
    h_pos = co_pos.copy()
    h_pos[2] += 1.44
    
    # Add H to atoms
    from ase import Atom
    atoms.append(Atom("H", position=h_pos))
    
    # Write POSCAR
    poscar_out = os.path.join(H_ADS_DIR, "POSCAR")
    write(poscar_out, atoms, format="vasp", sort=False)
    print(f"Generated {poscar_out} with H placed at d(Co-H) = 1.44 A.")
    
    # Write INCAR
    with open(os.path.join(H_ADS_DIR, "INCAR"), "w") as f:
        f.write(INCAR_H_ADS)
        
    # Build POTCAR: Cr + Cl + Co + H
    co_potcar = os.path.join(S2_DIR, "POTCAR")
    target_potcar = os.path.join(H_ADS_DIR, "POTCAR")
    with open(target_potcar, "wb") as f_out:
        with open(co_potcar, "rb") as f_in1:
            f_out.write(f_in1.read())
        with open(H_POTCAR_SRC, "rb") as f_in2:
            f_out.write(f_in2.read())
    print(f"Built POTCAR (Cr+Cl+Co+H) -> {target_potcar}")
    
    # Copy KPOINTS
    shutil.copyfile(os.path.join(S2_DIR, "KPOINTS"), os.path.join(H_ADS_DIR, "KPOINTS"))
    
    # Create job.sh
    job_sh_src = os.path.join(S2_DIR, "job.sh")
    with open(job_sh_src, "r") as f:
        content = f.read()
    content = content.replace("Co_S2_U329", "Co_H_U329")
    with open(os.path.join(H_ADS_DIR, "job.sh"), "w") as f:
        f.write(content)
    os.chmod(os.path.join(H_ADS_DIR, "job.sh"), 0o755)
    
    print(f"H_ads calculation successfully prepared in {H_ADS_DIR}!")

if __name__ == "__main__":
    main()
