#!/usr/bin/env python3
"""
setup_bands_suite.py
Automated generation and dispatch preparation for electronic band structure and PDOS calculations:
1. Tier 2 (U_Cr = 3.29 eV, U_TM = 0.00 eV, IVDW = 12) for Co, Fe, Ni (Adsorbed & Embedded)
2. Tier 3 (U_all = U_Cr = U_TM = 3.29 eV, IVDW = 12) for Co, Fe, Ni (Adsorbed & Embedded)

Adheres strictly to:
- Ponytail VASP Protocol: Zero redundancy, minimal tags, native defaults first.
- Slurm HPC Protocol: 32-core allocation, micro-batching, proper thread/MPI binding.
"""

import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWCALS_DIR = BASE_DIR
STRUCTURES_DIR = os.path.join(NEWCALS_DIR, "crcl3_2x2_CoFeNi_vdw12_U_structures")
UALL_DIR = os.path.join(NEWCALS_DIR, "crcl3-2x2-CoFeNi-vdw12-U_all3.29")

KPOINTS_PATH_2X2 = """K-Path for Monolayer CrCl3 2x2 Supercell (Gamma - M - K - Gamma)
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

KPOINTS_SCF_2X2 = """Uniform mesh for SCF and PDOS (Gamma-centered 5x5x1)
0
Gamma
5 5 1
0 0 0
"""

TM_MAGS = {
    'Co': 3.0,
    'Fe': 4.0,
    'Ni': 2.0
}

def create_potcar(target_dir, tm):
    src_pot = os.path.join(UALL_DIR, "adsorbed", tm, "clean", "POTCAR")
    if os.path.exists(src_pot):
        shutil.copy(src_pot, os.path.join(target_dir, "POTCAR"))
    else:
        raise FileNotFoundError(f"POTCAR for {tm} not found at {src_pot}")

def create_calc(target_dir, poscar_src, tm, mode, tier_u_tm):
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. POSCAR
    shutil.copy(poscar_src, os.path.join(target_dir, "POSCAR"))
    
    # 2. POTCAR
    create_potcar(target_dir, tm)
    
    # 3. KPOINTS
    with open(os.path.join(target_dir, "KPOINTS_SCF"), "w") as f:
        f.write(KPOINTS_SCF_2X2)
    with open(os.path.join(target_dir, "KPOINTS_BANDS"), "w") as f:
        f.write(KPOINTS_PATH_2X2)
        
    mag_tm = TM_MAGS[tm]
    magmom_str = f"8*3.0 24*0.0 1*{mag_tm}"
    u_tm_str = f"{tier_u_tm:.2f}"
    
    # 4. INCAR_SCF (Ponytail compliant: minimal tags, native defaults)
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
LDAUL    = 2 -1 2
LDAUU    = 3.29 0.00 {u_tm_str}
LMAXMIX  = 4
LASPH    = .TRUE.

LORBIT   = 11
NEDOS    = 2001
EMIN     = -15
EMAX     = 10
"""
    with open(os.path.join(target_dir, "INCAR_SCF"), "w") as f:
        f.write(incar_scf)
        
    # 5. INCAR_BANDS (Ponytail compliant)
    incar_bands = f"""PREC     = Accurate
ENCUT    = 400.0
EDIFF    = 1.0E-06

ISPIN    = 2
ICHARG   = 11

ISMEAR   = 0
SIGMA    = 0.05
NCORE    = 4

IVDW     = 12

LDAU     = .TRUE.
LDAUL    = 2 -1 2
LDAUU    = 3.29 0.00 {u_tm_str}
LMAXMIX  = 4
LASPH    = .TRUE.

LORBIT   = 11

LWAVE    = .FALSE.
LCHARG   = .FALSE.
"""
    with open(os.path.join(target_dir, "INCAR_BANDS"), "w") as f:
        f.write(incar_bands)

    # 6. Workflow Runner Script
    workflow_sh = f"""#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

echo "=== Running Step 1: Ground-State SCF ({mode} {tm}) ==="
cp INCAR_SCF INCAR
cp KPOINTS_SCF KPOINTS

if [ -n "$SLURM_JOB_ID" ]; then
    srun vasp_std > vasp_scf.out 2>&1
elif [ -f /home/cr/.local/bin/micromamba ]; then
    /home/cr/.local/bin/micromamba run -n materials-env mpirun -np 16 /home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std > vasp_scf.out 2>&1
else
    mpirun -np 16 vasp_std > vasp_scf.out 2>&1
fi

if ! grep -q "1 F=" OSZICAR; then
    echo "ERROR: SCF calculation did not converge!"
    exit 1
fi
echo "SCF Completed. Generating DOSCAR backup..."
cp DOSCAR DOSCAR.scf

echo "=== Running Step 2: Non-Self-Consistent Band Structure ({mode} {tm}) ==="
cp INCAR_BANDS INCAR
cp KPOINTS_BANDS KPOINTS

if [ -n "$SLURM_JOB_ID" ]; then
    srun vasp_std > vasp_bands.out 2>&1
elif [ -f /home/cr/.local/bin/micromamba ]; then
    /home/cr/.local/bin/micromamba run -n materials-env mpirun -np 16 /home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std > vasp_bands.out 2>&1
else
    mpirun -np 16 vasp_std > vasp_bands.out 2>&1
fi

if [ ! -s EIGENVAL ] && ! grep -q "General timing" OUTCAR && ! grep -q "1 F=" OSZICAR; then
    echo "ERROR: Band calculation did not converge!"
    exit 1
fi
echo "Band Structure Completed successfully for {mode} {tm}!"
"""
    with open(os.path.join(target_dir, "run_bands.sh"), "w") as f:
        f.write(workflow_sh)
    os.chmod(os.path.join(target_dir, "run_bands.sh"), 0o755)

    # 7. Slurm batch script for Carbono
    job_carbono = f"""#!/bin/bash
#SBATCH --job-name={tm[:2]}_{mode[:3]}_band
#SBATCH --output={tm}_{mode}_band.%j.out
#SBATCH --error={tm}_{mode}_band.%j.err
#SBATCH --partition=nanotubo
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=03:00:00
#SBATCH --signal=B:USR1@300

module purge
module load vasp/6.4.2-intel2021.4 2>/dev/null || module load vasp 2>/dev/null || true

export OMP_NUM_THREADS=1
ulimit -s unlimited

bash ./run_bands.sh
"""
    with open(os.path.join(target_dir, "job_carbono.sh"), "w") as f:
        f.write(job_carbono)

    # 8. Slurm batch script for Huk
    job_huk = f"""#!/bin/bash
#SBATCH --job-name={tm[:2]}_{mode[:3]}_band
#SBATCH --output={tm}_{mode}_band.%j.out
#SBATCH --error={tm}_{mode}_band.%j.err
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=03:00:00

export OMP_NUM_THREADS=1
ulimit -s unlimited

bash ./run_bands.sh
"""
    with open(os.path.join(target_dir, "job_huk.sh"), "w") as f:
        f.write(job_huk)

def setup_suite():
    print("Setting up Tier 3 (+U_all = 3.29 eV) Band Structure Suite...")
    # Tier 3 Adsorbed
    uall_ads = {
        'Co': os.path.join(UALL_DIR, "adsorbed", "Co", "clean", "CONTCAR"),
        'Fe': os.path.join(UALL_DIR, "adsorbed", "Fe", "clean", "CONTCAR"),
        'Ni': os.path.join(UALL_DIR, "adsorbed", "Ni", "clean", "CONTCAR")
    }
    for tm, pos in uall_ads.items():
        tdir = os.path.join(NEWCALS_DIR, "bands_U_all", "adsorbed", tm)
        create_calc(tdir, pos, tm, "adsorbed", 3.29)
        print(f"  [U_all Ads] {tm} -> {tdir}")

    # Tier 3 Embedded
    uall_emb = {
        'Co': os.path.join(UALL_DIR, "embedded", "Co", "clean", "CONTCAR"),
        'Fe': os.path.join(UALL_DIR, "embedded", "Fe", "clean", "CONTCAR"),
        'Ni': os.path.join(UALL_DIR, "embedded", "Ni", "clean", "CONTCAR")
    }
    for tm, pos in uall_emb.items():
        tdir = os.path.join(NEWCALS_DIR, "bands_U_all", "embedded", tm)
        create_calc(tdir, pos, tm, "embedded", 3.29)
        print(f"  [U_all Emb] {tm} -> {tdir}")

    print("\nSetting up Tier 2 (+U_Cr = 3.29 eV, U_TM = 0.0 eV) Band Structure Suite...")
    # Tier 2 Adsorbed
    ucr_ads = {
        'Co': os.path.join(STRUCTURES_DIR, "adsorbed", "Co", "clean_S3_topCr", "CONTCAR"),
        'Fe': os.path.join(STRUCTURES_DIR, "adsorbed", "Fe", "clean_S1_pore_penetrated_GS", "CONTCAR"),
        'Ni': os.path.join(STRUCTURES_DIR, "adsorbed", "Ni", "clean_S2_hollow_GS", "CONTCAR")
    }
    for tm, pos in ucr_ads.items():
        tdir = os.path.join(NEWCALS_DIR, "bands_U_Cr", "adsorbed", tm)
        create_calc(tdir, pos, tm, "adsorbed", 0.00)
        print(f"  [U_Cr Ads] {tm} -> {tdir}")

    # Tier 2 Embedded
    ucr_emb = {
        'Co': os.path.join(STRUCTURES_DIR, "embedded", "Co", "clean", "CONTCAR"),
        'Fe': os.path.join(STRUCTURES_DIR, "embedded", "Fe", "clean", "CONTCAR"),
        'Ni': os.path.join(STRUCTURES_DIR, "embedded", "Ni", "clean", "CONTCAR")
    }
    for tm, pos in ucr_emb.items():
        tdir = os.path.join(NEWCALS_DIR, "bands_U_Cr", "embedded", tm)
        create_calc(tdir, pos, tm, "embedded", 0.00)
        print(f"  [U_Cr Emb] {tm} -> {tdir}")

if __name__ == '__main__':
    setup_suite()
