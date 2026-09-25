#!/usr/bin/env python3
"""
setup_h_on_co_u.py

Reads the converged CONTCAR of CrCl3-2x2-Co with U=3.29 eV (S1, S3, or S2),
places H directly atop Co at d(Co-H) = 1.44 Angstroms,
concatenates H POTCAR, and generates the corresponding H_ads calculation directory.

Usage:
  python3 setup_h_on_co_u.py --site S1
  python3 setup_h_on_co_u.py --site S3
  python3 setup_h_on_co_u.py --site S2
"""

import os
import sys
import shutil
import argparse
import numpy as np
from ase.io import read, write
from ase import Atom

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H_POTCAR_SRC = "/home/cr/simulations/crcl3-HER/crcl3-newcals/H2_reference/yes_vdw/POTCAR"

INCAR_H_ADS = """# =========================================================================
# VASP INCAR: CrCl3 2x2 + Co-H Adsorbed State (PBE+D3(BJ) + U=3.29eV)
# Hydrogen adsorbed directly atop Co adatom
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


def stage_site(site_name: str):
    site_clean = site_name.strip("/").split("/")[-1]
    site_dir = os.path.join(BASE_DIR, "yes_vdw", site_clean)
    h_ads_dir = os.path.join(BASE_DIR, "yes_vdw", f"{site_clean}_H")

    contcar_path = os.path.join(site_dir, "CONTCAR")
    if not os.path.exists(contcar_path) or os.path.getsize(contcar_path) < 100:
        print(f"WAIT: {site_clean} calculation has not yet produced a valid CONTCAR ({contcar_path}).")
        return False

    os.makedirs(h_ads_dir, exist_ok=True)
    atoms = read(contcar_path)

    # Locate Co atom
    co_indices = [i for i, a in enumerate(atoms) if a.symbol == "Co"]
    if not co_indices:
        raise ValueError(f"No Co atom found in {site_clean} CONTCAR!")
    co_idx = co_indices[0]
    co_pos = atoms.positions[co_idx]

    # Place H 1.44 A above Co along z
    h_pos = co_pos.copy()
    h_pos[2] += 1.44

    # Add H
    atoms.append(Atom("H", position=h_pos))

    # Write POSCAR
    poscar_out = os.path.join(h_ads_dir, "POSCAR")
    write(poscar_out, atoms, format="vasp", sort=False)
    print(f"Generated {poscar_out} with H placed at d(Co-H) = 1.44 A above {site_clean}.")

    # Write INCAR
    with open(os.path.join(h_ads_dir, "INCAR"), "w") as f:
        f.write(INCAR_H_ADS)

    # Build POTCAR: Cr + Cl + Co + H
    co_potcar = os.path.join(site_dir, "POTCAR")
    target_potcar = os.path.join(h_ads_dir, "POTCAR")
    with open(target_potcar, "wb") as f_out:
        with open(co_potcar, "rb") as f_in1:
            f_out.write(f_in1.read())
        with open(H_POTCAR_SRC, "rb") as f_in2:
            f_out.write(f_in2.read())
    print(f"Built POTCAR (Cr+Cl+Co+H) -> {target_potcar}")

    # Copy KPOINTS
    shutil.copyfile(os.path.join(site_dir, "KPOINTS"), os.path.join(h_ads_dir, "KPOINTS"))

    # Create job.sh
    job_sh_src = os.path.join(site_dir, "job.sh")
    if os.path.exists(job_sh_src):
        with open(job_sh_src, "r") as f:
            content = f.read()
        content = content.replace(f"Co_{site_clean}_U3", f"Co_{site_clean}H_U3")
        with open(os.path.join(h_ads_dir, "job.sh"), "w") as f:
            f.write(content)
        os.chmod(os.path.join(h_ads_dir, "job.sh"), 0o755)

    print(f"✔ Successfully prepared H adsorption calculation in: {h_ads_dir}!\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Setup H adsorption atop Co (with U=3.29 eV)")
    parser.add_argument("--site", default="S3", choices=["S1", "S2", "S3", "all"], help="Target site (default: S3)")
    args = parser.parse_args()

    if args.site == "all":
        for s in ["S1", "S3", "S2"]:
            stage_site(s)
    else:
        stage_site(args.site)


if __name__ == "__main__":
    main()
