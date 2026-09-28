#!/usr/bin/env python3
"""
========================================================================================
 setup_embedded_pipeline.py
========================================================================================
 Sets up unified In-Allocation Pipeline calculation directories for embedded Co, Fe, Ni
 in monolayer CrCl3 (2x2 supercell):
   Phase 1: PBE + D3 (BJ) (U = 0)
   Phase 2: PBE + D3 (BJ) + U (U_Cr = 3.29 eV)

 Both phases execute within a SINGLE 4-hour Slurm allocation on Carbono (32 cores, nanotubo),
 eliminating 100% of second-stage queue wait times!

 Outputs for both phases are automatically organized:
   - d3_converged/: CONTCAR, OUTCAR, OSZICAR for PBE+D3
   - u_converged/ : CONTCAR, OUTCAR, OSZICAR for PBE+D3+U
========================================================================================
"""

import os
import shutil

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NEWCALS_DIR = os.path.join(REPO_ROOT, "crcl3-newcals")

METALS = {
    "co": {
        "symbol": "Co",
        "magmom": 3.0,
        "clean_src": os.path.join(NEWCALS_DIR, "embedded/co"),
        "h_src": os.path.join(NEWCALS_DIR, "doped-H/embeded/Co"),
    },
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

def generate_incar_d3(tm_sym: str, tm_mag: float, has_h: bool) -> str:
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
        "NCORE    = 4",
        "IVDW     = 12",
        "IBRION   = 2",
        "NSW      = 80",
        "EDIFFG   = -0.025",
    ]
    return "\n".join(lines) + "\n"

def generate_incar_u_addon(has_h: bool) -> str:
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
        "# Phase 2 (+U) Add-On Tags",
        "LDAU     = .TRUE.",
        "LDAUTYPE = 2",
        f"LDAUL    = {ldaul}",
        f"LDAUU    = {ldauu}",
        f"LDAUJ    = {ldauj}",
        "LMAXMIX  = 4",
        "ISTART   = 1",
        "NSW      = 60",
    ]
    return "\n".join(lines) + "\n"

def generate_pipeline_carbono_script(job_name: str) -> str:
    return f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -p nanotubo
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
echo "CPUs Alloc:  $SLURM_NTASKS (Partition: nanotubo)"
echo "Time Limit:  04:00:00 (In-Allocation Pipeline D3 -> +U)"
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

# -------------------------------------------------------------
# PHASE 1: PBE + D3 (BJ) RELAXATION
# -------------------------------------------------------------
if [ ! -f "d3_converged/OUTCAR" ] || ! grep -q "reached required accuracy" d3_converged/OUTCAR 2>/dev/null; then
    echo "[$(date)] Starting Phase 1: PBE + D3 (BJ)..."
    cp INCAR.d3 INCAR
    
    mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp_d3.out 2>&1
    
    if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
        echo "[$(date)] Phase 1 (D3) CONVERGED successfully!"
        mkdir -p d3_converged
        cp CONTCAR POSCAR
        cp CONTCAR d3_converged/
        cp OUTCAR   d3_converged/
        cp OSZICAR  d3_converged/
        cp vasprun.xml d3_converged/ 2>/dev/null || true
    else
        echo "[$(date)] Phase 1 reached walltime or need continuation. Checkpointing..."
        if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
            cp CONTCAR POSCAR
            sbatch job_carbono.sh
        fi
        exit 0
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

mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp_u.out 2>&1

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
    echo "[$(date)] Phase 2 checkpointing for final steps..."
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        sbatch job_carbono.sh
    fi
fi
"""

def main():
    print("=" * 70)
    print(" Setting up In-Allocation Pipeline (D3 -> +U) for Embedded CrCl3")
    print(" Partition: nanotubo | Cores: 32 | Time: 04:00:00")
    print("=" * 70)

    dispatch_script_lines = [
        "#!/bin/bash",
        "# Master Dispatch for 32-core Embedded In-Allocation Pipeline on Carbono",
        "BASE_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"",
        "echo '=========================================================='",
        "echo ' Dispatching 32-core Embedded Pipeline Jobs to Carbono'",
        "echo '=========================================================='",
    ]

    for tm_key, tm_info in METALS.items():
        tm_sym = tm_info["symbol"]
        tm_mag = tm_info["magmom"]

        base_dir = os.path.join(NEWCALS_DIR, f"crcl3-2x2-{tm_key}_emb-pipeline")

        for state in ["clean", "H_ads"]:
            has_h = (state == "H_ads")
            calc_dir = os.path.join(base_dir, state)
            os.makedirs(calc_dir, exist_ok=True)

            # 1. POSCAR from PBE
            src_dir = tm_info["h_src"] if has_h else tm_info["clean_src"]
            src_contcar = os.path.join(src_dir, "CONTCAR")
            dst_poscar = os.path.join(calc_dir, "POSCAR")
            if os.path.exists(src_contcar) and os.path.getsize(src_contcar) > 100:
                shutil.copy(src_contcar, dst_poscar)

            # 2. POTCAR
            src_potcar = os.path.join(src_dir, "POTCAR")
            dst_potcar = os.path.join(calc_dir, "POTCAR")
            if os.path.exists(src_potcar):
                shutil.copy(src_potcar, dst_potcar)

            # 3. KPOINTS
            with open(os.path.join(calc_dir, "KPOINTS"), "w") as f:
                f.write(KPOINTS_CONTENT)

            # 4. INCAR.d3 and INCAR.u
            incar_d3 = generate_incar_d3(tm_sym, tm_mag, has_h)
            with open(os.path.join(calc_dir, "INCAR.d3"), "w") as f:
                f.write(incar_d3)
            with open(os.path.join(calc_dir, "INCAR"), "w") as f:
                f.write(incar_d3)

            incar_u = generate_incar_u_addon(has_h)
            with open(os.path.join(calc_dir, "INCAR.u"), "w") as f:
                f.write(incar_u)

            # 5. Slurm script (32 cores, nanotubo, in-allocation chaining)
            h_tag = "H" if has_h else "cln"
            job_name = f"{tm_sym}_emb_{h_tag}_pipe"
            script_content = generate_pipeline_carbono_script(job_name)
            script_path = os.path.join(calc_dir, "job_carbono.sh")
            with open(script_path, "w") as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)

            print(f"  [+] Created: {calc_dir}")

            dispatch_script_lines.extend([
                f"echo '--> Submitting {tm_sym} ({state})...'",
                f"cd \"${{BASE_DIR}}/crcl3-2x2-{tm_key}_emb-pipeline/{state}\"",
                "sbatch job_carbono.sh",
            ])

    dispatch_script_lines.append("echo 'All 6 pipeline jobs submitted to nanotubo!'\n")
    dispatch_path = os.path.join(NEWCALS_DIR, "submit_embedded_pipeline.sh")
    with open(dispatch_path, "w") as f:
        f.write("\n".join(dispatch_script_lines))
    os.chmod(dispatch_path, 0o755)
    print(f"\n[+] Master pipeline dispatch script: {dispatch_path}")

if __name__ == "__main__":
    main()
