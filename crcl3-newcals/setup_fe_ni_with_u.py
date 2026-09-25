#!/usr/bin/env python3
"""
setup_fe_ni_with_u.py

Sets up complete VASP calculation suites for Fe and Ni adsorption on CrCl3 (2x2)
with Hubbard U = 3.29 eV on Cr 3d and Grimme D3 (Becke-Johnson damping, IVDW=12):
  - crcl3-2x2-fe_ads-with-U/yes_vdw/{S1, S2, S3, clean}
  - crcl3-2x2-ni_ads-with-U/yes_vdw/{S1, S2, S3, clean}
"""

import os
import shutil
from pathlib import Path

BASE_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals"
CONVERGED_CLEAN_DIR = os.path.join(BASE_DIR, "crcl3-2x2-co_ads-with-U", "yes_vdw", "clean")

TM_CONFIGS = [
    {
        "symbol": "fe",
        "name": "Fe",
        "magmom": "8*3.0 24*0.0 1*4.0",
        "potcar_src": os.path.join(BASE_DIR, "crcl3-2x2-fe_ads-without-U", "yes_vdw", "S1", "POTCAR"),
        "poscar_src_base": os.path.join(BASE_DIR, "crcl3-2x2-fe_ads-without-U", "yes_vdw"),
        "target_dir": os.path.join(BASE_DIR, "crcl3-2x2-fe_ads-with-U", "yes_vdw")
    },
    {
        "symbol": "ni",
        "name": "Ni",
        "magmom": "8*3.0 24*0.0 1*2.0",
        "potcar_src": os.path.join(BASE_DIR, "crcl3-2x2-ni_ads-without-U", "yes_vdw", "S1", "POTCAR"),
        "poscar_src_base": os.path.join(BASE_DIR, "crcl3-2x2-ni_ads-without-U", "yes_vdw"),
        "target_dir": os.path.join(BASE_DIR, "crcl3-2x2-ni_ads-with-U", "yes_vdw")
    }
]

INCAR_TEMPLATE = """# =========================================================================
# VASP INCAR: CrCl3 2x2 + {tm_name} Adatom at {site_name} (PBE+D3(BJ) + U=3.29eV)
# Functional: PBE + Grimme DFT-D3 (BJ damping, IVDW=12)
# Hubbard U: Dudarev formulation on Cr 3d (U=3.29 eV)
# =========================================================================

# --- Electronic Minimization & Plane-Wave Basis ---
PREC     = Accurate
ENCUT    = 400.0
EDIFF    = 1.0E-06
NELM     = 100

# --- Spin Polarization & Magnetic Initialization ---
ISPIN    = 2
MAGMOM   = {magmom}

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

JOB_HUK_TEMPLATE = """#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -o job.%j.out
#SBATCH -e job.%j.err
#SBATCH --partition=medio,hram,alto
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --time=168:00:00

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

echo "=========================================================="
echo "Starting Slurm Job : $SLURM_JOB_NAME ($SLURM_JOB_ID)"
echo "Executing on Host  : $(hostname)"
echo "Partition Selected : $SLURM_JOB_PARTITION"
echo "Allocated Node(s)  : $SLURM_NODELIST"
echo "Allocated CPUs     : $SLURM_CPUS_ON_NODE"
echo "Working Directory  : $(pwd)"
echo "Start Timestamp    : $(date)"
echo "=========================================================="

NPROCS=${{SLURM_CPUS_ON_NODE:-$(nproc)}}
if [ "$NPROCS" -eq 40 ]; then
    NCORE_OPT=5
elif [ "$NPROCS" -eq 36 ]; then
    NCORE_OPT=6
elif [ "$NPROCS" -eq 28 ]; then
    NCORE_OPT=4
else
    NCORE_OPT=4
fi

sed -i "s/.*NCORE.*/NCORE    = $NCORE_OPT/" INCAR

echo "Running VASP with $NPROCS MPI processes (NCORE=$NCORE_OPT)..."
mpirun -np $NPROCS vasp_std > run.log 2>&1
EXIT_CODE=$?

echo "=========================================================="
echo "Execution finished at $(date) with exit code: $EXIT_CODE"
if grep -q "reached required accuracy" run.log 2>/dev/null; then
    echo ">>> STATUS: VASP CALCULATION CONVERGED SUCCESSFULLY <<<"
fi
echo "=========================================================="
exit $EXIT_CODE
"""

JOB_CARBONO_TEMPLATE = """#!/bin/bash
#SBATCH -J {job_name}
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
        echo "Calculated converged! No resubmission needed."
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
module load vasp/6.2.0

mpirun --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1 &
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

def setup_all():
    print("=" * 80)
    print("SETTING UP Fe AND Ni CALCULATION SUITES WITH HUBBARD U = 3.29 eV (2x2 SUPERCELL)")
    print("=" * 80)

    for cfg in TM_CONFIGS:
        tm_sym = cfg["symbol"]
        tm_name = cfg["name"]
        target_dir = cfg["target_dir"]
        potcar_src = cfg["potcar_src"]
        poscar_base = cfg["poscar_src_base"]
        magmom = cfg["magmom"]

        print(f"\n📁 Processing {tm_name} ({tm_sym.upper()}) -> {target_dir}...")
        os.makedirs(target_dir, exist_ok=True)

        # 1. Copy converged clean substrate reference
        clean_target = os.path.join(target_dir, "clean")
        os.makedirs(clean_target, exist_ok=True)
        for fname in ["INCAR", "KPOINTS", "POSCAR", "POTCAR", "CONTCAR", "OSZICAR", "OUTCAR"]:
            src_f = os.path.join(CONVERGED_CLEAN_DIR, fname)
            if os.path.exists(src_f):
                shutil.copyfile(src_f, os.path.join(clean_target, fname))
        print(f"  ✔ Inherited converged clean reference (E0 = -147.30384 eV) in: {clean_target}")

        # 2. Setup S1, S2, S3
        for site_key, site_label in [("S1", "Site 1 (Top-Cl)"), ("S2", "Site 2 (Hollow)"), ("S3", "Site 3 (Top-Cr)")]:
            site_dir = os.path.join(target_dir, site_key)
            os.makedirs(site_dir, exist_ok=True)

            # POSCAR
            poscar_src = os.path.join(poscar_base, site_key, "POSCAR")
            if not os.path.exists(poscar_src):
                raise FileNotFoundError(f"Missing POSCAR source: {poscar_src}")
            shutil.copyfile(poscar_src, os.path.join(site_dir, "POSCAR"))

            # POTCAR
            if not os.path.exists(potcar_src):
                raise FileNotFoundError(f"Missing POTCAR source: {potcar_src}")
            shutil.copyfile(potcar_src, os.path.join(site_dir, "POTCAR"))

            # KPOINTS
            kpoints_src = os.path.join(poscar_base, site_key, "KPOINTS")
            shutil.copyfile(kpoints_src, os.path.join(site_dir, "KPOINTS"))

            # INCAR
            incar_content = INCAR_TEMPLATE.format(
                tm_name=tm_name,
                site_name=f"{site_key} {site_label}",
                magmom=magmom
            )
            with open(os.path.join(site_dir, "INCAR"), "w") as f:
                f.write(incar_content)

            # job.sh (Carbono)
            job_name = f"{tm_name}_{site_key}_U3"
            with open(os.path.join(site_dir, "job.sh"), "w") as f:
                f.write(JOB_CARBONO_TEMPLATE.format(job_name=job_name))
            os.chmod(os.path.join(site_dir, "job.sh"), 0o755)

            # job_huk.sh (Huk)
            with open(os.path.join(site_dir, "job_huk.sh"), "w") as f:
                f.write(JOB_HUK_TEMPLATE.format(job_name=job_name))
            os.chmod(os.path.join(site_dir, "job_huk.sh"), 0o755)

            print(f"  ✔ Staged {site_key} ({site_label}) -> {site_dir}")

    print("\n🎉 Fe and Ni suites with U=3.29 eV successfully generated!")

if __name__ == "__main__":
    setup_all()
