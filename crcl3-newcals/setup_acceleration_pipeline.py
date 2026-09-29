#!/usr/bin/env python3
"""
setup_acceleration_pipeline.py

Sets up and dispatches parallel accelerated calculations across multi-cluster infrastructure:
  1. Huk Cluster: Fe embedded pipeline (alto partition, 36 cores, T_wait = 0)
  2. Local Arch:  Ni embedded pipeline (batch partition, 16 cores, T_wait = 0)

Incorporate DecisionCouncil-approved algorithmic tuning:
  - Phase 1 (PBE+D3): ALGO = Normal, POTIM = 0.3, EDIFFG = -0.025
  - Phase 2 (+U):     ALGO = Fast, NELMIN = 4, TIME = 0.4, POTIM = 0.25, LMAXMIX = 4, ISTART = 1
"""

import os
import shutil
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NEWCALS_DIR = os.path.join(REPO_ROOT, "crcl3-newcals")

METALS = {
    "fe": {
        "symbol": "Fe",
        "magmom": 4.0,
        "clean_src": os.path.join(NEWCALS_DIR, "embedded/fe"),
        "h_src": os.path.join(NEWCALS_DIR, "doped-H/embeded/Fe"),
    },
    "ni": {
        "symbol": "Ni",
        "magmom": 2.0,
        "clean_src": os.path.join(NEWCALS_DIR, "embedded/ni"),
        "h_src": os.path.join(NEWCALS_DIR, "doped-H/embeded/NI"),
    }
}

KPOINTS_CONTENT = """K-Points 5x5x1 Gamma-centered
0
Gamma
 5  5  1
 0  0  0
"""

def generate_incar_d3(tm_sym: str, tm_mag: float, has_h: bool, ncore: int) -> str:
    magmom_str = f"8*3.0 24*0.0 1*{tm_mag:.1f}"
    if has_h:
        magmom_str += " 1*0.0"

    lines = [
        f"# Phase 1: Embedded {tm_sym} {'+ H' if has_h else 'Clean'} (PBE + D3 BJ)",
        "PREC     = Accurate",
        "ENCUT    = 400.0",
        "EDIFF    = 1.0E-06",
        "NELM     = 100",
        "ISMEAR   = 0",
        "SIGMA    = 0.05",
        "ISPIN    = 2",
        f"MAGMOM   = {magmom_str}",
        "LREAL    = Auto",
        f"NCORE    = {ncore}",
        "IVDW     = 12",
        "IBRION   = 2",
        "POTIM    = 0.3",
        "NSW      = 80",
        "EDIFFG   = -0.025",
    ]
    return "\n".join(lines) + "\n"

def generate_incar_u_addon(has_h: bool, ncore: int) -> str:
    if has_h:
        ldaul = "2 -1 -1 -1"
        ldauu = "3.29 0.0 0.0 0.0"
        ldauj = "0.0 0.0 0.0 0.0"
    else:
        ldaul = "2 -1 -1"
        ldauu = "3.29 0.0 0.0"
        ldauj = "0.0 0.0 0.0"

    lines = [
        "",
        "# Phase 2 (+U) Add-On Tags (Council Reconciled)",
        "LDAU     = .TRUE.",
        "LDAUTYPE = 2",
        f"LDAUL    = {ldaul}",
        f"LDAUU    = {ldauu}",
        f"LDAUJ    = {ldauj}",
        "LMAXMIX  = 4",
        "ISTART   = 1",
        "ALGO     = Fast",
        "NELMIN   = 4",
        "TIME     = 0.4",
        "POTIM    = 0.25",
        "NSW      = 60",
        "EDIFFG   = -0.025",
    ]
    return "\n".join(lines) + "\n"

def generate_huk_script(job_name: str) -> str:
    return f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -p alto
#SBATCH --nodes=1
#SBATCH --ntasks=36
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

echo "=========================================================="
echo "Job Name:    $SLURM_JOB_NAME"
echo "Job ID:      $SLURM_JOB_ID"
echo "Host:        $(hostname)"
echo "Directory:   $(pwd)"
echo "Start Time:  $(date)"
echo "CPUs Alloc:  $SLURM_NTASKS (Partition: alto, Huk Cluster)"
echo "Time Limit:  24:00:00 (In-Allocation Pipeline D3 -> +U)"
echo "=========================================================="

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

# -------------------------------------------------------------
# PHASE 1: PBE + D3 (BJ) RELAXATION
# -------------------------------------------------------------
if [ ! -f "d3_converged/OUTCAR" ] || ! grep -q "reached required accuracy" d3_converged/OUTCAR 2>/dev/null; then
    echo "[$(date)] Starting Phase 1: PBE + D3 (BJ)..."
    cp INCAR.d3 INCAR
    
    mpirun -np $SLURM_NTASKS /opt/vasp/vasp/bin/vasp_std > vasp_d3.out 2>&1
    
    if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
        echo "[$(date)] Phase 1 (D3) CONVERGED successfully!"
        mkdir -p d3_converged
        cp CONTCAR POSCAR
        cp CONTCAR d3_converged/
        cp OUTCAR   d3_converged/
        cp OSZICAR  d3_converged/
        cp vasprun.xml d3_converged/ 2>/dev/null || true
    else
        echo "[$(date)] Phase 1 did not reach target threshold in single run. Exiting."
        exit 1
    fi
else
    echo "[$(date)] Phase 1 (D3) already converged. Proceeding to Phase 2..."
fi

# -------------------------------------------------------------
# PHASE 2: PBE + D3(BJ) + U (U_Cr = 3.29 eV) CONTINUATION
# -------------------------------------------------------------
echo "[$(date)] Starting Phase 2: PBE + D3(BJ) + U (Immediate In-Allocation Continuation)..."
cp d3_converged/CONTCAR POSCAR
cp INCAR.d3 INCAR
cat INCAR.u >> INCAR

mpirun -np $SLURM_NTASKS /opt/vasp/vasp/bin/vasp_std > vasp_u.out 2>&1

if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "[$(date)] Phase 2 (+U) CONVERGED successfully!"
    mkdir -p u_converged
    cp CONTCAR u_converged/
    cp OUTCAR   u_converged/
    cp OSZICAR  u_converged/
    cp vasprun.xml u_converged/ 2>/dev/null || true
    echo "=========================================================="
    echo " ALL PIPELINE PHASES (D3 AND +U) COMPLETED IN SINGLE JOB!"
    echo " Finished At: $(date)"
    echo "=========================================================="
    exit 0
else
    echo "[$(date)] Phase 2 finished iteration block. Checkpointing."
    exit 0
fi
"""

def generate_arch_script(job_name: str) -> str:
    return f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -p batch
#SBATCH -n 16
#SBATCH --time=24:00:00
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

echo "=========================================================="
echo "Job Name:    $SLURM_JOB_NAME"
echo "Job ID:      $SLURM_JOB_ID"
echo "Host:        $(hostname)"
echo "Directory:   $(pwd)"
echo "Start Time:  $(date)"
echo "CPUs Alloc:  $SLURM_NTASKS (Partition: batch, Local Arch)"
echo "Time Limit:  24:00:00 (In-Allocation Pipeline D3 -> +U)"
echo "=========================================================="

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

MPI_RUN="/home/cr/.local/share/mamba/envs/vasp-env/bin/mpirun"
VASP_BIN="/home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std"

# -------------------------------------------------------------
# PHASE 1: PBE + D3 (BJ) RELAXATION
# -------------------------------------------------------------
if [ ! -f "d3_converged/OUTCAR" ] || ! grep -q "reached required accuracy" d3_converged/OUTCAR 2>/dev/null; then
    echo "[$(date)] Starting Phase 1: PBE + D3 (BJ)..."
    cp INCAR.d3 INCAR
    
    $MPI_RUN --bind-to none -np $SLURM_NTASKS $VASP_BIN > vasp_d3.out 2>&1
    
    if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
        echo "[$(date)] Phase 1 (D3) CONVERGED successfully!"
        mkdir -p d3_converged
        cp CONTCAR POSCAR
        cp CONTCAR d3_converged/
        cp OUTCAR   d3_converged/
        cp OSZICAR  d3_converged/
        cp vasprun.xml d3_converged/ 2>/dev/null || true
    else
        echo "[$(date)] Phase 1 finished iteration block."
        exit 1
    fi
else
    echo "[$(date)] Phase 1 (D3) already converged. Proceeding to Phase 2..."
fi

# -------------------------------------------------------------
# PHASE 2: PBE + D3(BJ) + U (U_Cr = 3.29 eV) CONTINUATION
# -------------------------------------------------------------
echo "[$(date)] Starting Phase 2: PBE + D3(BJ) + U (Immediate In-Allocation Continuation)..."
cp d3_converged/CONTCAR POSCAR
cp INCAR.d3 INCAR
cat INCAR.u >> INCAR

$MPI_RUN --bind-to none -np $SLURM_NTASKS $VASP_BIN > vasp_u.out 2>&1

if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "[$(date)] Phase 2 (+U) CONVERGED successfully!"
    mkdir -p u_converged
    cp CONTCAR u_converged/
    cp OUTCAR   u_converged/
    cp OSZICAR  u_converged/
    cp vasprun.xml u_converged/ 2>/dev/null || true
    echo "=========================================================="
    echo " ALL PIPELINE PHASES (D3 AND +U) COMPLETED IN SINGLE JOB!"
    echo " Finished At: $(date)"
    echo "=========================================================="
    exit 0
else
    echo "[$(date)] Phase 2 finished iteration block. Checkpointing."
    exit 0
fi
"""

def setup_huk_fe():
    print("\n[>>>] Setting up Fe Embedded Pipeline for HUK (36 cores, partition alto)...")
    tm_info = METALS["fe"]
    base_dir = os.path.join(NEWCALS_DIR, "crcl3-2x2-fe_emb-huk")
    
    for state in ["clean", "H_ads"]:
        has_h = (state == "H_ads")
        calc_dir = os.path.join(base_dir, state)
        os.makedirs(calc_dir, exist_ok=True)
        
        # POSCAR & POTCAR from source
        src_dir = tm_info["h_src"] if has_h else tm_info["clean_src"]
        shutil.copy(os.path.join(src_dir, "CONTCAR"), os.path.join(calc_dir, "POSCAR"))
        shutil.copy(os.path.join(src_dir, "POTCAR"), os.path.join(calc_dir, "POTCAR"))
        
        # KPOINTS
        with open(os.path.join(calc_dir, "KPOINTS"), "w") as f:
            f.write(KPOINTS_CONTENT)
            
        # INCARs (NCORE = 6 for 36 cores)
        incar_d3 = generate_incar_d3("Fe", 4.0, has_h, ncore=6)
        with open(os.path.join(calc_dir, "INCAR.d3"), "w") as f:
            f.write(incar_d3)
        with open(os.path.join(calc_dir, "INCAR"), "w") as f:
            f.write(incar_d3)
            
        incar_u = generate_incar_u_addon(has_h, ncore=6)
        with open(os.path.join(calc_dir, "INCAR.u"), "w") as f:
            f.write(incar_u)
            
        # Job script
        job_name = f"Fe_emb_{'H' if has_h else 'cln'}_huk"
        script = generate_huk_script(job_name)
        script_path = os.path.join(calc_dir, "job_huk.sh")
        with open(script_path, "w") as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        print(f"  [+] Prepared Huk calc: {calc_dir}")

def setup_arch_ni():
    print("\n[>>>] Setting up Ni Embedded Pipeline for Local ARCH (16 cores, partition batch)...")
    tm_info = METALS["ni"]
    base_dir = os.path.join(NEWCALS_DIR, "crcl3-2x2-ni_emb-arch")
    
    for state in ["clean", "H_ads"]:
        has_h = (state == "H_ads")
        calc_dir = os.path.join(base_dir, state)
        os.makedirs(calc_dir, exist_ok=True)
        
        # POSCAR & POTCAR from source
        src_dir = tm_info["h_src"] if has_h else tm_info["clean_src"]
        shutil.copy(os.path.join(src_dir, "CONTCAR"), os.path.join(calc_dir, "POSCAR"))
        shutil.copy(os.path.join(src_dir, "POTCAR"), os.path.join(calc_dir, "POTCAR"))
        
        # KPOINTS
        with open(os.path.join(calc_dir, "KPOINTS"), "w") as f:
            f.write(KPOINTS_CONTENT)
            
        # INCARs (NCORE = 4 for 16 cores)
        incar_d3 = generate_incar_d3("Ni", 2.0, has_h, ncore=4)
        with open(os.path.join(calc_dir, "INCAR.d3"), "w") as f:
            f.write(incar_d3)
        with open(os.path.join(calc_dir, "INCAR"), "w") as f:
            f.write(incar_d3)
            
        incar_u = generate_incar_u_addon(has_h, ncore=4)
        with open(os.path.join(calc_dir, "INCAR.u"), "w") as f:
            f.write(incar_u)
            
        # Job script
        job_name = f"Ni_emb_{'H' if has_h else 'cln'}_arch"
        script = generate_arch_script(job_name)
        script_path = os.path.join(calc_dir, "job_arch.sh")
        with open(script_path, "w") as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        print(f"  [+] Prepared Arch calc: {calc_dir}")

if __name__ == "__main__":
    setup_huk_fe()
    setup_arch_ni()
    print("\n[+] Setup completed successfully for both Huk and Arch!")
