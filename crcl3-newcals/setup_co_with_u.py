#!/usr/bin/env python3
"""
setup_co_with_u.py

Sets up CrCl3(2x2) with Co adatom under Hubbard U = 3.29 eV and DFT-D3 (IVDW=12).
Target directory: crcl3-newcals/crcl3-2x2-co_ads-with-U/yes_vdw/

Focuses specifically on:
1. S1 (Top-Cl site - testing unconstrained relaxation & barrierless sliding under U):
   - Starting structure: Initial Top-Cl POSCAR from crcl3-2x2-co_ads-without-U/yes_vdw/S1
   - POTCAR: Cr, Cl, Co
   - INCAR: Dudarev DFT+U (LDAU = .TRUE., LDAUL = 2 -1 -1, LDAUU = 3.29 0.0 0.0, LMAXMIX = 4)
   - KPOINTS: 5x5x1 Gamma-centered
2. S3 (Top-Cr site - testing direct on-site Cr 3d repulsion effect):
   - Starting structure: Pre-relaxed CONTCAR from crcl3-2x2-co_ads-without-U/yes_vdw/S3
   - POTCAR: Cr, Cl, Co
   - INCAR: Dudarev DFT+U (same as S1)
   - KPOINTS: 5x5x1 Gamma-centered
3. clean (Clean CrCl3 2x2 monolayer under same U = 3.29 eV for reference energy):
   - Starting structure: Relaxed CONTCAR from crcl3-2x2-co_ads-without-U/yes_vdw/clean
   - POTCAR: Cr, Cl
   - INCAR: LDAU = .TRUE., LDAUL = 2 -1, LDAUU = 3.29 0.0, LMAXMIX = 4
   - KPOINTS: 5x5x1 Gamma-centered
4. Subsequent H adsorption generator setup_h_on_co_u.py
"""

import os
import shutil

BASE_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals"
TARGET_DIR = os.path.join(BASE_DIR, "crcl3-2x2-co_ads-with-U", "yes_vdw")
SOURCE_WITHOUT_U = os.path.join(BASE_DIR, "crcl3-2x2-co_ads-without-U", "yes_vdw")

INCAR_TM_TEMPLATE = """# =========================================================================
# VASP INCAR: CrCl3 2x2 + Co Adatom at {site_desc} (PBE+D3(BJ) + U=3.29eV)
# Functional: PBE + Grimme DFT-D3 (IVDW=12) + Dudarev DFT+U (U=3.29eV on Cr 3d)
# =========================================================================

# --- Electronic Minimization & Plane-Wave Basis ---
PREC     = Accurate
ENCUT    = 400.0
EDIFF    = 1.0E-06
NELM     = 100

# --- Spin Polarization & Magnetic Initialization ---
ISPIN    = 2
MAGMOM   = 8*3.0 24*0.0 1*3.0

# --- Brillouin Zone & Smearing ---
ISMEAR   = 0
SIGMA    = 0.05

# --- Parallelization & Performance ---
NCORE    = 4
LREAL    = Auto

# --- Dispersion Correction (Becke-Johnson Damping) ---
IVDW     = 12

# --- Ionic Relaxation ---
IBRION   = 2
NSW      = 100
EDIFFG   = -0.025

# --- PAW & Density Mixing for d-Electrons ---
LASPH    = .TRUE.
LMAXMIX  = 4

# --- Hubbard U Correction (Cr 3d Dudarev Formulation) ---
LDAU     = .TRUE.
LDAUL    = 2 -1 -1
LDAUU    = 3.29 0.0 0.0

# --- Dipole Correction ---
LDIPOL   = .TRUE.
IDIPOL   = 3
DIPOL    = 0.5 0.5 0.5

# --- Wavefunction & Charge Output Management ---
LWAVE    = .FALSE.
LCHARG   = .FALSE.
"""

INCAR_CLEAN = """# =========================================================================
# VASP INCAR: Clean CrCl3 2x2 Monolayer Reference (PBE+D3(BJ) + U=3.29eV)
# Pristine substrate reference for Delta E_ads under identical functional
# =========================================================================

# --- Electronic Minimization & Plane-Wave Basis ---
PREC     = Accurate
ENCUT    = 400.0
EDIFF    = 1.0E-06
NELM     = 100

# --- Spin Polarization & Magnetic Initialization ---
ISPIN    = 2
MAGMOM   = 8*3.0 24*0.0

# --- Brillouin Zone & Smearing ---
ISMEAR   = 0
SIGMA    = 0.05

# --- Parallelization & Performance ---
NCORE    = 4
LREAL    = Auto

# --- Dispersion Correction (Becke-Johnson Damping) ---
IVDW     = 12

# --- Ionic Relaxation ---
IBRION   = 2
NSW      = 100
EDIFFG   = -0.025

# --- PAW & Density Mixing for d-Electrons ---
LASPH    = .TRUE.
LMAXMIX  = 4

# --- Hubbard U Correction (Cr 3d Dudarev Formulation) ---
LDAU     = .TRUE.
LDAUL    = 2 -1
LDAUU    = 3.29 0.0

# --- Dipole Correction ---
LDIPOL   = .TRUE.
IDIPOL   = 3
DIPOL    = 0.5 0.5 0.5

# --- Wavefunction & Charge Output Management ---
LWAVE    = .FALSE.
LCHARG   = .FALSE.
"""

JOB_SH = """#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -o job.%j.out
#SBATCH -e job.%j.err
#SBATCH --partition=fulereno
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=04:00:00
#SBATCH --signal=B:USR1@300

# ==============================================================================
# CARBONO & HUK DUAL-COMPATIBLE SLURM SCRIPT (Slurm HPC Pre-Flight Optimized)
# System: {job_name}
# Topology: 32 cores (socket architecture divisor), 4-hour micro-batch
# ==============================================================================

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

# Handle SIGUSR1 checkpoint signal for auto-resubmission
resubmit_on_timeout() {{
    echo "[$(date)] SIGUSR1 received (5 min remaining). Checkpointing..."
    if [ -f CONTCAR ] && [ -s CONTCAR ]; then
        cp CONTCAR POSCAR
        echo "Updated POSCAR with CONTCAR for seamless restart."
    fi
    sbatch "$0"
    exit 0
}}
trap 'resubmit_on_timeout' USR1

echo "=========================================================="
echo "Starting Slurm Job : $SLURM_JOB_NAME ($SLURM_JOB_ID)"
echo "Host               : $(hostname)"
echo "Allocated CPUs     : $SLURM_NTASKS"
echo "Working Directory  : $(pwd)"
echo "Start Timestamp    : $(date)"
echo "=========================================================="

# Tune NCORE for 32 cores
if [ "$SLURM_NTASKS" -eq 32 ]; then
    NCORE_OPT=4
elif [ "$SLURM_NTASKS" -eq 64 ]; then
    NCORE_OPT=8
else
    NCORE_OPT=4
fi

sed -i "s/.*NCORE.*/NCORE    = $NCORE_OPT/" INCAR

# Execute VASP
mpirun -np $SLURM_NTASKS vasp_std > run.log 2>&1
EXIT_CODE=$?

echo "Finished at $(date) with exit code $EXIT_CODE"

if grep -q "reached required accuracy" run.log 2>/dev/null; then
    echo ">>> CONVERGED SUCCESSFULLY <<<"
elif [ -f CONTCAR ] && [ -s CONTCAR ]; then
    cp CONTCAR POSCAR
fi

exit $EXIT_CODE
"""

def setup_directory(subdir, incar_content, job_name, source_subdir, source_file="CONTCAR"):
    dir_path = os.path.join(TARGET_DIR, subdir)
    os.makedirs(dir_path, exist_ok=True)
    
    # 1. INCAR
    with open(os.path.join(dir_path, "INCAR"), "w") as f:
        f.write(incar_content)
        
    # 2. POSCAR
    src_poscar = os.path.join(SOURCE_WITHOUT_U, source_subdir, source_file)
    if os.path.exists(src_poscar):
        shutil.copyfile(src_poscar, os.path.join(dir_path, "POSCAR"))
        # Update comment line in POSCAR
        with open(os.path.join(dir_path, "POSCAR"), "r") as f:
            pos_lines = f.readlines()
        pos_lines[0] = f"CrCl3 2x2 {subdir} (D3, U=3.29eV) from {source_file}\n"
        with open(os.path.join(dir_path, "POSCAR"), "w") as f:
            f.writelines(pos_lines)
    else:
        print(f"ERROR: {src_poscar} not found!")
        
    # 3. POTCAR
    src_potcar = os.path.join(SOURCE_WITHOUT_U, source_subdir, "POTCAR")
    if os.path.exists(src_potcar):
        shutil.copyfile(src_potcar, os.path.join(dir_path, "POTCAR"))
    else:
        print(f"ERROR: {src_potcar} not found!")
        
    # 4. KPOINTS
    src_kpoints = os.path.join(SOURCE_WITHOUT_U, source_subdir, "KPOINTS")
    if os.path.exists(src_kpoints):
        shutil.copyfile(src_kpoints, os.path.join(dir_path, "KPOINTS"))
    else:
        with open(os.path.join(dir_path, "KPOINTS"), "w") as f:
            f.write("K-Points 5x5x1 Gamma-centered (CrCl3 2x2)\n0\nGamma\n 5 5 1\n 0 0 0\n")
            
    # 5. job.sh
    job_script = JOB_SH.format(job_name=job_name)
    job_path = os.path.join(dir_path, "job.sh")
    with open(job_path, "w") as f:
        f.write(job_script)
    os.chmod(job_path, 0o755)
    
    print(f"Successfully configured: {dir_path} (POSCAR from {source_file})")

def main():
    print("=" * 70)
    print(f"Setting up CrCl3 2x2 + Co with Hubbard U = 3.29 eV in:\n{TARGET_DIR}")
    print("Focusing on Site 1 (Top-Cl) and Site 3 (Top-Cr)")
    print("=" * 70)
    
    # 1. S1 (Top-Cl): initialized from S1/POSCAR to observe unconstrained relaxation / sliding under U
    incar_s1 = INCAR_TM_TEMPLATE.format(site_desc="S1 Top-Cl")
    setup_directory("S1", incar_s1, "Co_S1_U329", "S1", source_file="POSCAR")
    
    # 2. S3 (Top-Cr): initialized from S3/CONTCAR (z pre-relaxed) to evaluate Cr 3d repulsion
    incar_s3 = INCAR_TM_TEMPLATE.format(site_desc="S3 Top-Cr")
    setup_directory("S3", incar_s3, "Co_S3_U329", "S3", source_file="CONTCAR")
    
    # 3. clean reference: pristine monolayer with U=3.29 eV
    setup_directory("clean", INCAR_CLEAN, "clean_U329", "clean", source_file="CONTCAR")

if __name__ == "__main__":
    main()
