#!/usr/bin/env python3
"""
setup_u_all329_calculations.py

Prepares VASP calculation directories and inputs for:
CrCl3 (2x2) Monolayer functionalized with Co, Fe, Ni (Adsorbed and Embedded)
with Hubbard U = 3.29 eV applied to ALL transition metal species:
  - U(Cr) = 3.29 eV
  - U(TM) = 3.29 eV (TM = Co, Fe, Ni)
under PBE + DFT-D3(BJ) (IVDW = 12).

Starting geometries are seeded directly from the converged CONTCARs of the
previous U_Cr = 3.29 eV / PBE+D3 calculations, ensuring ultra-fast relaxation.
"""

import os
import shutil
from ase.io import read, write

BASE_DIR = "/home/cr/simulations/crcl3-HER"
ROOT_CALCS = os.path.join(BASE_DIR, "crcl3-newcals")
DEST_DIR = os.path.join(ROOT_CALCS, "crcl3-2x2-CoFeNi-vdw12-U_all3.29")

systems = [
    # mode, tm, state, src_poscar, potcar_src, magmom, ldau_u, ldau_l, ldau_j
    {
        "mode": "embedded",
        "tm": "Co",
        "state": "clean",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-co_emb-metano", "clean", "u_converged", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-co_emb-metano", "clean", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*3.0",
        "ldau_l": "2 -1 2",
        "ldau_u": "3.29 0.00 3.29",
        "ldau_j": "0.00 0.00 0.00",
        "job_name": "Co_emb_c_Uall"
    },
    {
        "mode": "embedded",
        "tm": "Co",
        "state": "H_ads",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-co_emb-metano", "H_ads", "u_converged", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-co_emb-metano", "H_ads", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*3.0 1*0.0",
        "ldau_l": "2 -1 2 -1",
        "ldau_u": "3.29 0.00 3.29 0.00",
        "ldau_j": "0.00 0.00 0.00 0.00",
        "job_name": "Co_emb_H_Uall"
    },
    {
        "mode": "embedded",
        "tm": "Fe",
        "state": "clean",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-fe_emb-huk", "clean", "u_converged", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-fe_emb-huk", "clean", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*4.0",
        "ldau_l": "2 -1 2",
        "ldau_u": "3.29 0.00 3.29",
        "ldau_j": "0.00 0.00 0.00",
        "job_name": "Fe_emb_c_Uall"
    },
    {
        "mode": "embedded",
        "tm": "Fe",
        "state": "H_ads",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-fe_emb-huk", "H_ads", "u_converged", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-fe_emb-huk", "H_ads", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*4.0 1*0.0",
        "ldau_l": "2 -1 2 -1",
        "ldau_u": "3.29 0.00 3.29 0.00",
        "ldau_j": "0.00 0.00 0.00 0.00",
        "job_name": "Fe_emb_H_Uall"
    },
    {
        "mode": "embedded",
        "tm": "Ni",
        "state": "clean",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-ni_emb-pipeline", "clean", "u_converged", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-ni_emb-pipeline", "clean", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*2.0",
        "ldau_l": "2 -1 2",
        "ldau_u": "3.29 0.00 3.29",
        "ldau_j": "0.00 0.00 0.00",
        "job_name": "Ni_emb_c_Uall"
    },
    {
        "mode": "embedded",
        "tm": "Ni",
        "state": "H_ads",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-ni_emb-pipeline", "H_ads", "u_converged", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-ni_emb-pipeline", "H_ads", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*2.0 1*0.0",
        "ldau_l": "2 -1 2 -1",
        "ldau_u": "3.29 0.00 3.29 0.00",
        "ldau_j": "0.00 0.00 0.00 0.00",
        "job_name": "Ni_emb_H_Uall"
    },
    # Adsorbed Systems
    {
        "mode": "adsorbed",
        "tm": "Co",
        "state": "clean",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-co_ads-with-U", "yes_vdw", "S3", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-co_emb-metano", "clean", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*3.0",
        "ldau_l": "2 -1 2",
        "ldau_u": "3.29 0.00 3.29",
        "ldau_j": "0.00 0.00 0.00",
        "job_name": "Co_ads_c_Uall"
    },
    {
        "mode": "adsorbed",
        "tm": "Co",
        "state": "H_ads",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-co_ads-with-U", "yes_vdw", "S3_H", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-co_emb-metano", "H_ads", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*3.0 1*0.0",
        "ldau_l": "2 -1 2 -1",
        "ldau_u": "3.29 0.00 3.29 0.00",
        "ldau_j": "0.00 0.00 0.00 0.00",
        "job_name": "Co_ads_H_Uall"
    },
    {
        "mode": "adsorbed",
        "tm": "Fe",
        "state": "clean",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-fe_ads-with-U", "yes_vdw", "S1", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-fe_emb-huk", "clean", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*4.0",
        "ldau_l": "2 -1 2",
        "ldau_u": "3.29 0.00 3.29",
        "ldau_j": "0.00 0.00 0.00",
        "job_name": "Fe_ads_c_Uall"
    },
    {
        "mode": "adsorbed",
        "tm": "Fe",
        "state": "H_ads",
        "src_poscar": os.path.join(BASE_DIR, "past-dirs", "doped-H", "adsorbed", "Fe", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-fe_emb-huk", "H_ads", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*4.0 1*0.0",
        "ldau_l": "2 -1 2 -1",
        "ldau_u": "3.29 0.00 3.29 0.00",
        "ldau_j": "0.00 0.00 0.00 0.00",
        "job_name": "Fe_ads_H_Uall"
    },
    {
        "mode": "adsorbed",
        "tm": "Ni",
        "state": "clean",
        "src_poscar": os.path.join(ROOT_CALCS, "crcl3-2x2-ni_ads-with-U", "yes_vdw", "S2", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-ni_emb-pipeline", "clean", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*2.0",
        "ldau_l": "2 -1 2",
        "ldau_u": "3.29 0.00 3.29",
        "ldau_j": "0.00 0.00 0.00",
        "job_name": "Ni_ads_c_Uall"
    },
    {
        "mode": "adsorbed",
        "tm": "Ni",
        "state": "H_ads",
        "src_poscar": os.path.join(BASE_DIR, "past-dirs", "doped-H", "adsorbed", "NI", "CONTCAR"),
        "potcar_src": os.path.join(ROOT_CALCS, "crcl3-2x2-ni_emb-pipeline", "H_ads", "POTCAR"),
        "magmom": "8*3.0 24*0.0 1*2.0 1*0.0",
        "ldau_l": "2 -1 2 -1",
        "ldau_u": "3.29 0.00 3.29 0.00",
        "ldau_j": "0.00 0.00 0.00 0.00",
        "job_name": "Ni_ads_H_Uall"
    },
]

def make_incar(sys_dict):
    incar = f"""# CrCl3 (2x2) Monolayer + {sys_dict['tm']} ({sys_dict['mode']}, {sys_dict['state']})
# Multi-Site DFT+U: U(Cr) = 3.29 eV, U({sys_dict['tm']}) = 3.29 eV | PBE + D3(BJ)
PREC     = Accurate
ENCUT    = 500.0
EDIFF    = 1.0E-06
NELM     = 100
ISMEAR   = 0
SIGMA    = 0.02
ISPIN    = 2
MAGMOM   = {sys_dict['magmom']}
LREAL    = Auto
NCORE    = 4

# Dispersion Correction
IVDW     = 12

# Ionic Relaxation
IBRION   = 2
NSW      = 100
EDIFFG   = -0.02
ISIF     = 2

# Dudarev Multi-Site DFT+U (Cr + {sys_dict['tm']})
LDAU     = .TRUE.
LDAUTYPE = 2
LDAUL    = {sys_dict['ldau_l']}
LDAUU    = {sys_dict['ldau_u']}
LDAUJ    = {sys_dict['ldau_j']}
LMAXMIX  = 4
LDAUPRINT= 1
"""
    return incar

def make_kpoints():
    return """Gamma-centered 5x5x1
0
Gamma
 5  5  1
 0  0  0
"""

def make_job_carbono(sys_dict):
    return f"""#!/bin/bash
#SBATCH -J {sys_dict['job_name']}
#SBATCH -p fulereno,nanotubo,grafeno
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
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
echo "=========================================================="

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

module purge
module load gnu12 openmpi4 vasp/6.2.0

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=vader,self,tcp
export OMPI_MCA_mtl=^ofi,psm2
export OMPI_MCA_osc=^ucx
export UCX_TLS=sm,self

# Trap SIGUSR1 for checkpointing and automated resubmission
ckpt_handler() {{
    echo "[$(date)] SIGUSR1 received! Checkpointing calculation..."
    if [ ! -s OUTCAR ] || ! grep -q "Iteration" OUTCAR 2>/dev/null; then
        echo "ERROR: Calculation failed to start or produced no output! Aborting resubmission loop." >&2
        exit 1
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        echo "[$(date)] Updated POSCAR from CONTCAR. Auto-resubmitting..."
        sbatch job_carbono.sh
    fi
    exit 0
}}
trap 'ckpt_handler' USR1

mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1

if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "[$(date)] VASP calculation CONVERGED successfully!"
else
    echo "[$(date)] Run incomplete or interrupted. Checking CONTCAR..."
    if [ ! -s OUTCAR ] || ! grep -q "Iteration" OUTCAR 2>/dev/null; then
        echo "ERROR: Calculation failed to start or produced no output! Aborting resubmission loop." >&2
        exit 1
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        sbatch job_carbono.sh
    fi
fi
"""

def make_job_huk(sys_dict):
    return f"""#!/bin/bash
#SBATCH -J {sys_dict['job_name']}
#SBATCH -p medio,normal
#SBATCH --nodes=1
#SBATCH --ntasks=28
#SBATCH --cpus-per-task=1
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
echo "=========================================================="

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

module purge
module load vasp/6.3.0 2>/dev/null || module load vasp/6.2.0 2>/dev/null || true

ckpt_handler() {{
    echo "[$(date)] SIGUSR1 received! Checkpointing calculation..."
    if [ ! -s OUTCAR ] || ! grep -q "Iteration" OUTCAR 2>/dev/null; then
        echo "ERROR: Calculation failed to start or produced no output! Aborting resubmission loop." >&2
        exit 1
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        sbatch job_huk.sh
    fi
    exit 0
}}
trap 'ckpt_handler' USR1

mpirun -np $SLURM_NTASKS vasp_std > vasp.out 2>&1

if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "[$(date)] VASP calculation CONVERGED successfully!"
else
    if [ ! -s OUTCAR ] || ! grep -q "Iteration" OUTCAR 2>/dev/null; then
        echo "ERROR: Calculation failed to start or produced no output! Aborting resubmission loop." >&2
        exit 1
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        sbatch job_huk.sh
    fi
fi
"""

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    submit_lines_carbono = ["#!/bin/bash\n# Submit all U_all=3.29 calculations to Carbono\n"]
    submit_lines_huk = ["#!/bin/bash\n# Submit all U_all=3.29 calculations to Huk\n"]
    
    print(f"Creating all calculation inputs in: {DEST_DIR}")
    for s in systems:
        sub_path = os.path.join(DEST_DIR, s["mode"], s["tm"], s["state"])
        os.makedirs(sub_path, exist_ok=True)
        
        # 1. POSCAR
        if not os.path.exists(s["src_poscar"]):
            print(f"[ERROR] Missing source POSCAR: {s['src_poscar']}")
            continue
        shutil.copy2(s["src_poscar"], os.path.join(sub_path, "POSCAR"))
        
        # 2. POTCAR
        if not os.path.exists(s["potcar_src"]):
            print(f"[ERROR] Missing source POTCAR: {s['potcar_src']}")
            continue
        shutil.copy2(s["potcar_src"], os.path.join(sub_path, "POTCAR"))
        
        # 3. INCAR
        with open(os.path.join(sub_path, "INCAR"), "w") as f:
            f.write(make_incar(s))
            
        # 4. KPOINTS
        with open(os.path.join(sub_path, "KPOINTS"), "w") as f:
            f.write(make_kpoints())
            
        # 5. Job scripts
        j_carb = os.path.join(sub_path, "job_carbono.sh")
        with open(j_carb, "w") as f:
            f.write(make_job_carbono(s))
        os.chmod(j_carb, 0o755)
        
        j_huk = os.path.join(sub_path, "job_huk.sh")
        with open(j_huk, "w") as f:
            f.write(make_job_huk(s))
        os.chmod(j_huk, 0o755)
        
        rel_sub = os.path.relpath(sub_path, DEST_DIR)
        submit_lines_carbono.append(f"echo 'Submitting {rel_sub} on Carbono...'\n(cd {sub_path} && sbatch job_carbono.sh)\n")
        submit_lines_huk.append(f"echo 'Submitting {rel_sub} on Huk...'\n(cd {sub_path} && sbatch job_huk.sh)\n")
        
        print(f"  [OK] {rel_sub:30s} | U_all: {s['ldau_u']} | POSCAR: {os.path.basename(s['src_poscar'])}")
        
    sub_carb_file = os.path.join(DEST_DIR, "submit_all_carbono.sh")
    with open(sub_carb_file, "w") as f:
        f.writelines(submit_lines_carbono)
    os.chmod(sub_carb_file, 0o755)
    
    sub_huk_file = os.path.join(DEST_DIR, "submit_all_huk.sh")
    with open(sub_huk_file, "w") as f:
        f.writelines(submit_lines_huk)
    os.chmod(sub_huk_file, 0o755)
    
    print("\n[OK] Setup completed successfully!")
    print(f"Master Carbono submit script: {sub_carb_file}")
    print(f"Master Huk submit script:     {sub_huk_file}")

if __name__ == '__main__':
    main()
