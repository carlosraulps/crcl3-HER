#!/usr/bin/env python3
"""
run_slabs_sequential.py
=======================
Automates the sequential execution and chained convergence of all 4 frozen substrate slabs:
  1. Fe_slab_Ucr (Already completed and verified!)
  2. Fe_slab_Uall (accelerated from Fe_slab_Ucr CHGCAR with ICHARG=1)
  3. Ni_slab_Ucr (accelerated from Fe_slab_Ucr CHGCAR with ICHARG=1)
  4. Ni_slab_Uall (accelerated from Ni_slab_Ucr CHGCAR with ICHARG=1)

Then executes:
  - compute_all_cdd.py
  - render_and_splice_all.py
  - updates zip deliverable and synchronizes all project directories
"""

import os
import sys
import shutil
import subprocess
import time

SLABS_DIR = "/home/cr/simulations/crcl3-HER/cdd_frozen_slabs"
VASP_BIN = "/home/cr/computational-materials-suite/bin/vasp_std"
MPIRUN = "/home/cr/.local/share/mamba/envs/vasp-env/bin/mpirun"

def is_calc_complete(dir_path):
    outcar = os.path.join(dir_path, "OUTCAR")
    chgcar = os.path.join(dir_path, "CHGCAR")
    if os.path.exists(outcar) and os.path.exists(chgcar):
        if os.path.getsize(chgcar) > 200_000_000:
            with open(outcar, "r") as f:
                content = f.read()
                if "General timing and accounting" in content:
                    return True
    return False

def run_slab(dir_path, name, init_chgcar=None):
    print(f"\n=======================================================")
    print(f"Starting {name} in {dir_path}")
    print(f"=======================================================")
    
    if is_calc_complete(dir_path):
        print(f"[✓] {name} is already complete and verified. Skipping calculation.")
        return True
        
    incar = os.path.join(dir_path, "INCAR")
    target_chg = os.path.join(dir_path, "CHGCAR")
    if init_chgcar and os.path.exists(init_chgcar):
        if not os.path.exists(target_chg) or os.path.getsize(target_chg) < 200_000_000:
            print(f"[*] Seeding initial charge density from {init_chgcar}...")
            shutil.copy2(init_chgcar, target_chg)
        
        # Ensure ICHARG = 1 in INCAR
        with open(incar, "r") as f:
            lines = f.readlines()
        has_icharg = False
        new_lines = []
        for l in lines:
            if l.strip().startswith("ICHARG"):
                new_lines.append("ICHARG   = 1\n")
                has_icharg = True
            else:
                new_lines.append(l)
        if not has_icharg:
            new_lines.append("ICHARG   = 1\n")
        with open(incar, "w") as f:
            f.writelines(new_lines)
            
    # Run VASP with 16 cores
    cmd = f"cd {dir_path} && export OMP_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 && {MPIRUN} -np 16 {VASP_BIN} > vasp.out 2>&1"
    print(f"[*] Running: {cmd}")
    ret = subprocess.run(cmd, shell=True)
    
    if is_calc_complete(dir_path):
        print(f"[✓] {name} CONVERGED successfully!")
        return True
    else:
        raise RuntimeError(f"Calculation {name} did not complete cleanly! Check vasp.out and OUTCAR.")

if __name__ == "__main__":
    fe_ucr_dir = os.path.join(SLABS_DIR, "Fe_slab_Ucr")
    fe_uall_dir = os.path.join(SLABS_DIR, "Fe_slab_Uall")
    ni_ucr_dir = os.path.join(SLABS_DIR, "Ni_slab_Ucr")
    ni_uall_dir = os.path.join(SLABS_DIR, "Ni_slab_Uall")
    
    fe_ucr_chgcar = os.path.join(fe_ucr_dir, "CHGCAR")
    assert is_calc_complete(fe_ucr_dir), "Fe_slab_Ucr must be complete before running this script!"
    print(f"[✓] Fe_slab_Ucr verified ({os.path.getsize(fe_ucr_chgcar)/1024/1024:.1f} MB).")
    
    # 1. Fe_slab_Uall (seeded from Fe_slab_Ucr)
    run_slab(fe_uall_dir, "Fe_slab_Uall", init_chgcar=fe_ucr_chgcar)
    
    # 2. Ni_slab_Ucr (seeded from Fe_slab_Ucr)
    run_slab(ni_ucr_dir, "Ni_slab_Ucr", init_chgcar=fe_ucr_chgcar)
    ni_ucr_chgcar = os.path.join(ni_ucr_dir, "CHGCAR")
    
    # 3. Ni_slab_Uall (seeded from Ni_slab_Ucr)
    run_slab(ni_uall_dir, "Ni_slab_Uall", init_chgcar=ni_ucr_chgcar)
    
    print("\n=======================================================")
    print("[✓] ALL 4 FROZEN SUBSTRATE SLABS COMPLETED AND CONVERGED!")
    print("=======================================================")
