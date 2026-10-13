#!/usr/bin/env python3
"""
setup_cohp_lobster_ucr.py
=========================
Prepares the static SCF + LOBSTER calculation directories for single-site +U_Cr
(U_Cr = 3.29 eV, U_TM = 0.00 eV, IVDW = 12) on relaxed ground-state structures.

Systems:
  Adsorbed: Co, Fe, Ni (S2 hollow site)
  Embedded: Co, Fe, Ni (6-fold pore hollow site)
"""

import os
import shutil

BASE_DIR = "/home/cr/simulations/crcl3-HER"
UCR_STRUCT_DIR = os.path.join(BASE_DIR, "crcl3-newcals/crcl3_2x2_CoFeNi_vdw12_U_structures")
UALL_COHP_DIR = os.path.join(BASE_DIR, "crcl3-newcals/cohp_lobster_Uall")
TARGET_DIR = os.path.join(BASE_DIR, "crcl3-newcals/cohp_lobster_Ucr")

systems = [
    {
        "mode": "adsorbed",
        "metal": "Co",
        "poscar_src": os.path.join(UCR_STRUCT_DIR, "adsorbed/Co/clean_S2_hollow/CONTCAR"),
        "potcar_src": os.path.join(UALL_COHP_DIR, "adsorbed/Co/POTCAR"),
        "kpoints_src": os.path.join(UALL_COHP_DIR, "adsorbed/Co/KPOINTS"),
        "lobsterin_src": os.path.join(UALL_COHP_DIR, "adsorbed/Co/lobsterin"),
        "cluster": "huk",
        "partition": "medio",
        "ntasks": 28
    },
    {
        "mode": "adsorbed",
        "metal": "Fe",
        "poscar_src": os.path.join(UCR_STRUCT_DIR, "adsorbed/Fe/clean_S2_hollow/CONTCAR"),
        "potcar_src": os.path.join(UALL_COHP_DIR, "adsorbed/Fe/POTCAR"),
        "kpoints_src": os.path.join(UALL_COHP_DIR, "adsorbed/Fe/KPOINTS"),
        "lobsterin_src": os.path.join(UALL_COHP_DIR, "adsorbed/Fe/lobsterin"),
        "cluster": "huk",
        "partition": "medio",
        "ntasks": 28
    },
    {
        "mode": "adsorbed",
        "metal": "Ni",
        "poscar_src": os.path.join(UCR_STRUCT_DIR, "adsorbed/Ni/clean_S2_hollow_GS/CONTCAR"),
        "potcar_src": os.path.join(UALL_COHP_DIR, "adsorbed/Ni/POTCAR"),
        "kpoints_src": os.path.join(UALL_COHP_DIR, "adsorbed/Ni/KPOINTS"),
        "lobsterin_src": os.path.join(UALL_COHP_DIR, "adsorbed/Ni/lobsterin"),
        "cluster": "huk",
        "partition": "medio",
        "ntasks": 28
    },
    {
        "mode": "embedded",
        "metal": "Co",
        "poscar_src": os.path.join(UCR_STRUCT_DIR, "embedded/Co/clean/CONTCAR"),
        "potcar_src": os.path.join(UALL_COHP_DIR, "embedded/Co/POTCAR"),
        "kpoints_src": os.path.join(UALL_COHP_DIR, "embedded/Co/KPOINTS"),
        "lobsterin_src": os.path.join(UALL_COHP_DIR, "embedded/Co/lobsterin"),
        "cluster": "carbono",
        "partition": "fulereno",
        "ntasks": 32
    },
    {
        "mode": "embedded",
        "metal": "Fe",
        "poscar_src": os.path.join(UCR_STRUCT_DIR, "embedded/Fe/clean/CONTCAR"),
        "potcar_src": os.path.join(UALL_COHP_DIR, "embedded/Fe/POTCAR"),
        "kpoints_src": os.path.join(UALL_COHP_DIR, "embedded/Fe/KPOINTS"),
        "lobsterin_src": os.path.join(UALL_COHP_DIR, "embedded/Fe/lobsterin"),
        "cluster": "carbono",
        "partition": "fulereno",
        "ntasks": 32
    },
    {
        "mode": "embedded",
        "metal": "Ni",
        "poscar_src": os.path.join(UCR_STRUCT_DIR, "embedded/Ni/clean/CONTCAR"),
        "potcar_src": os.path.join(UALL_COHP_DIR, "embedded/Ni/POTCAR"),
        "kpoints_src": os.path.join(UALL_COHP_DIR, "embedded/Ni/KPOINTS"),
        "lobsterin_src": os.path.join(UALL_COHP_DIR, "embedded/Ni/lobsterin"),
        "cluster": "carbono",
        "partition": "fulereno",
        "ntasks": 32
    }
]

def generate_incar(metal, mode):
    # Single-site +U_Cr: Dudarev U=3.29 on Cr, 0.00 on Cl and TM
    magmom_map = {
        "Co": "8*3.0 24*0.0 1*3.0",
        "Fe": "8*3.0 24*0.0 1*4.0",
        "Ni": "8*3.0 24*0.0 1*2.0"
    }
    mag = magmom_map.get(metal, "8*3.0 24*0.0 1*3.0")
    
    incar_content = f"""# Monolayer CrCl3 (2x2) + {metal} ({mode}) Static SCF for LOBSTER COHP (Single-Site +U_Cr = 3.29 eV)
PREC     = Accurate
ENCUT    = 500
EDIFF    = 1E-06
IBRION   = -1
NSW      = 0
ISMEAR   = 0
SIGMA    = 0.05
ISPIN    = 2
MAGMOM   = {mag}
IVDW     = 12
LDAU     = .TRUE.
LDAUTYPE = 2
LDAUL    = 2 -1 2
LDAUU    = 3.29 0.00 0.00
LDAUJ    = 0.00 0.00 0.00
LREAL    = .FALSE.
NCORE    = 4
ISYM     = -1
NBANDS   = 216
LWAVE    = .TRUE.
LCHARG   = .TRUE.
"""
    return incar_content

def generate_slurm_huk(metal, mode):
    return f"""#!/bin/bash
#SBATCH -J {metal}_{mode}_cohp_Ucr
#SBATCH -p medio
#SBATCH --nodes=1
#SBATCH --ntasks=28
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

module purge
module load vasp/6.2.0 2>/dev/null || module load vasp 2>/dev/null

# 1. Run VASP static SCF
mpirun -np $SLURM_NTASKS vasp_std > vasp.out 2>&1

# 2. Run LOBSTER
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

def generate_slurm_carbono(metal, mode):
    return f"""#!/bin/bash
#SBATCH -J {metal}_{mode}_cohp_Ucr
#SBATCH -p fulereno
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=01:00:00
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

# 1. Run VASP static SCF
mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1

# 2. Run LOBSTER
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

def setup_all():
    print(f"Creating directory tree in: {TARGET_DIR}")
    for item in systems:
        mode = item["mode"]
        metal = item["metal"]
        target_subdir = os.path.join(TARGET_DIR, mode, metal)
        os.makedirs(target_subdir, exist_ok=True)
        
        # Copy POSCAR from relaxed CONTCAR
        shutil.copy2(item["poscar_src"], os.path.join(target_subdir, "POSCAR"))
        shutil.copy2(item["potcar_src"], os.path.join(target_subdir, "POTCAR"))
        shutil.copy2(item["kpoints_src"], os.path.join(target_subdir, "KPOINTS"))
        shutil.copy2(item["lobsterin_src"], os.path.join(target_subdir, "lobsterin"))
        
        # Write INCAR
        with open(os.path.join(target_subdir, "INCAR"), "w") as f:
            f.write(generate_incar(metal, mode))
            
        # Write run script
        if item["cluster"] == "huk":
            slurm_content = generate_slurm_huk(metal, mode)
        else:
            slurm_content = generate_slurm_carbono(metal, mode)
            
        with open(os.path.join(target_subdir, "run_vasp.sh"), "w") as f:
            f.write(slurm_content)
        os.chmod(os.path.join(target_subdir, "run_vasp.sh"), 0o755)
        
        print(f"  [OK] Staged {mode}/{metal} for {item['cluster'].upper()} [{item['partition']}]")

if __name__ == "__main__":
    setup_all()
