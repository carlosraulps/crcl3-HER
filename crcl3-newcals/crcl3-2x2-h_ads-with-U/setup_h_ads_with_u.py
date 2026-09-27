#!/usr/bin/env python3
"""
setup_h_ads_with_u.py

Sets up calculation directories for monolayer CrCl3 (2x2) with H adsorption
under PBE+D3(BJ) + Hubbard U (U=3.29 eV) across sites S1, S2, and S3.
"""

import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_BASE = os.path.abspath(os.path.join(BASE_DIR, "..", "crcl3-2x2-h_ads-without-U", "yes_vdw_ivdw12"))

sites = {
    "S1": "Top-Cl (Global Minimum)",
    "S2": "Hollow",
    "S3": "Top-Cr"
}

incar_template = """# =========================================================================
# SYSTEM: CrCl3 2x2 + H ({site_name}) (D3(BJ) + U=3.29eV)
# Cell: CrCl3 2x2 Monolayer Supercell (8 Cr, 24 Cl, 1 H)
# Vacuum: c = 20.0000 Angstroms (Fixed vacuum layer)
# Method: PBE + Grimme DFT-D3(BJ) (IVDW=12) + Dudarev DFT+U (U=3.29 eV on Cr 3d)
# =========================================================================

# --- 1. Electronic Minimization & Plane-Wave Basis ---
SYSTEM   = CrCl3 2x2 + H ({site_code}) (D3, U=3.29eV)
PREC     = Accurate
ENCUT    = 400.0
ALGO     = Normal
EDIFF    = 1.0E-06
NELM     = 100

# --- 2. Spin Polarization & Magnetic Moments ---
ISPIN    = 2
MAGMOM   = 8*3.0 24*0.0 1*0.0

# --- 3. Brillouin-Zone Integration & Smearing ---
ISMEAR   = 0
SIGMA    = 0.05

# --- 4. Parallelization & Computational Performance ---
NCORE    = 4
LREAL    = Auto

# --- 5. van der Waals Dispersion Correction (Becke-Johnson Damping) ---
IVDW     = 12

# --- 6. Ionic Relaxation & Convergence Criteria ---
IBRION   = 2
NSW      = 100
ISIF     = 2
EDIFFG   = -0.025

# --- 7. PAW Density Mixing & Aspherical Gradients ---
LASPH    = .TRUE.
LMAXMIX  = 4

# --- 8. Hubbard U Correction (Cr 3d Dudarev Formulation) ---
LDAU     = .TRUE.
LDAUTYPE = 2
LDAUL    = 2 -1 -1
LDAUU    = 3.29 0.0 0.0
LDAUJ    = 0.0 0.0 0.0

# --- 9. Surface Dipole Correction (2D Slab Standard) ---
LDIPOL   = .TRUE.
IDIPOL   = 3
DIPOL    = 0.5 0.5 0.5

# --- 10. Wavefunction & Charge Output Management ---
LWAVE    = .FALSE.
LCHARG   = .FALSE.
"""

# Carbono Slurm submission script with AMD EPYC MCA flags and micro-batch chaining
job_carbono_template = """#!/bin/bash
#SBATCH -J H2x2_{site_code}_U3
#SBATCH -p fulereno
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --signal=B:USR1@300
#SBATCH --requeue
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

echo "=========================================================="
echo "Job Name:    $SLURM_JOB_NAME"
echo "Job ID:      $SLURM_JOB_ID"
echo "Host:        $(hostname)"
echo "Directory:   $(pwd)"
echo "Start Time:  $(date)"
echo "CPUs Alloc:  $SLURM_NTASKS"
echo "Time Limit:  04:00:00 (Micro-Batch Chained)"
echo "=========================================================="

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

checkpoint_and_resubmit() {{
    echo "[$(date)] Slurm USR1 intercepted — graceful checkpoint..."
    echo "LSTOP = .TRUE." > STOPCAR
    if [ -n "$VASP_PID" ]; then
        wait $VASP_PID
    fi
    if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
        echo "Calculation converged! No resubmission needed."
        rm -f STOPCAR
        exit 0
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp POSCAR "POSCAR.step_${{SLURM_JOB_ID}}"
        cp CONTCAR POSCAR
        cp OUTCAR  "OUTCAR.step_${{SLURM_JOB_ID}}" 2>/dev/null || true
    fi
    rm -f STOPCAR
    sbatch job.sh
    exit 0
}}
trap 'checkpoint_and_resubmit' USR1 TERM

if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    NLINES=$(wc -l < CONTCAR)
    if [ "$NLINES" -ge 8 ]; then
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
    fi
fi

sed -i "s/.*NCORE.*/NCORE    = 8/" INCAR

module purge
module load gnu12 openmpi4 vasp/6.2.0

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=vader,self,tcp
export OMPI_MCA_mtl=^ofi,psm2
export OMPI_MCA_osc=^ucx
export UCX_TLS=sm,self

mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1 &
VASP_PID=$!
wait $VASP_PID
EXIT_CODE=$?

rm -f STOPCAR

if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "VASP converged within walltime window!"
    exit 0
else
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
        sbatch job.sh
    fi
fi

exit $EXIT_CODE
"""

# Huk Slurm submission script
job_huk_template = """#!/bin/bash
#SBATCH --job-name=H2x2_{site_code}_U3
#SBATCH --partition=alto,medio
#SBATCH --nodes=1
#SBATCH --ntasks=36
#SBATCH --output=job.%j.out
#SBATCH --error=job.%j.err

source /etc/profile.d/modules.sh 2>/dev/null || true
export OMP_NUM_THREADS=1
ulimit -s unlimited

export NCORE=6

mpirun -np 36 /opt/vasp/vasp.6.3.0/bin/vasp_std > run.log 2>&1
"""

for site_code, site_name in sites.items():
    site_dir = os.path.join(BASE_DIR, "yes_vdw", site_code)
    os.makedirs(site_dir, exist_ok=True)
    
    src_site_dir = os.path.join(SRC_BASE, site_code)
    src_contcar = os.path.join(src_site_dir, "CONTCAR")
    src_poscar = os.path.join(src_site_dir, "POSCAR")
    src_potcar = os.path.join(src_site_dir, "POTCAR")
    src_kpoints = os.path.join(src_site_dir, "KPOINTS")
    
    # Use relaxed CONTCAR as POSCAR if available, fallback to POSCAR
    target_poscar = os.path.join(site_dir, "POSCAR")
    if os.path.exists(src_contcar) and os.path.getsize(src_contcar) > 100:
        shutil.copy2(src_contcar, target_poscar)
        print(f"✔ [{site_code}] Initialized POSCAR from relaxed CONTCAR ({src_contcar})")
    else:
        shutil.copy2(src_poscar, target_poscar)
        print(f"✔ [{site_code}] Initialized POSCAR from raw POSCAR")
        
    shutil.copy2(src_potcar, os.path.join(site_dir, "POTCAR"))
    shutil.copy2(src_kpoints, os.path.join(site_dir, "KPOINTS"))
    
    # Write INCAR
    incar_path = os.path.join(site_dir, "INCAR")
    with open(incar_path, "w") as f:
        f.write(incar_template.format(site_code=site_code, site_name=site_name))
    print(f"✔ [{site_code}] Generated INCAR with U=3.29 eV and IVDW=12")
    
    # Write Slurm scripts
    job_sh_path = os.path.join(site_dir, "job.sh")
    with open(job_sh_path, "w") as f:
        f.write(job_carbono_template.format(site_code=site_code))
    os.chmod(job_sh_path, 0o755)
    
    job_huk_path = os.path.join(site_dir, "job_huk.sh")
    with open(job_huk_path, "w") as f:
        f.write(job_huk_template.format(site_code=site_code))
    os.chmod(job_huk_path, 0o755)
    
print("All H adsorption sites configured successfully.")
