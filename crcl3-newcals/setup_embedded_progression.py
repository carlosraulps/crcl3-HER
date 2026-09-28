#!/usr/bin/env python3
"""
========================================================================================
 setup_embedded_progression.py
========================================================================================
 Sets up progressive D3 and +U calculation directories for embedded Co, Fe, and Ni
 in monolayer CrCl3 (2x2 supercell):
   1. Progressive Branch A: crcl3-2x2-{tm}_emb-without-U (PBE + D3 BJ, U=0)
   2. Progressive Branch B: crcl3-2x2-{tm}_emb-with-U    (PBE + D3 BJ + U, U_Cr=3.29 eV)

 Both clean and H-adsorbed states are generated for each metal:
   - clean: embedded metal in the 2D Cr honeycomb hollow (CN = 6)
   - H_ads: H adsorbed atop the embedded metal (CN = 6+1)

 Automatically configures:
   - POSCAR from existing converged PBE structures
   - Accurate POTCAR (Cr, Cl, TM, [H])
   - Standard KPOINTS (5x5x1 Gamma-centered)
   - Minimal zero-redundancy INCAR complying with ponytail VASP protocol
   - Optimized Slurm batch scripts for Carbono (64 cores, USR1 trap) and Huk (alto/medio)
   - Chained Slurm dependency workflow: D3 -> automatically bootstraps into +U!
========================================================================================
"""

import os
import shutil
import subprocess

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

def generate_incar(tm_sym: str, tm_mag: float, has_h: bool, with_u: bool) -> str:
    magmom_str = f"8*3.0 24*0.0 1*{tm_mag:.1f}"
    if has_h:
        magmom_str += " 1*0.0"

    incar_lines = [
        f"# INCAR for Embedded {tm_sym} {'+ H' if has_h else 'Clean'} (D3 {'+ U' if with_u else 'only'})",
        "PREC     = Accurate",
        "ENCUT    = 400.0",
        "EDIFF    = 1.0E-06",
        "NELM     = 100",
        "ISMEAR   = 0",
        "SIGMA    = 0.05",
        "ISPIN    = 2",
        f"MAGMOM   = {magmom_str}",
        "LREAL    = Auto",
        "NCORE    = 8",
        "IVDW     = 12",
        "IBRION   = 2",
        "NSW      = 100",
        "EDIFFG   = -0.025",
    ]

    if with_u:
        if has_h:
            ldaul = "2 -1 -1 -1"
            ldauu = "3.29 0.0 0.0 0.0"
            ldauj = "0.0 0.0 0.0 0.0"
        else:
            ldaul = "2 -1 -1"
            ldauu = "3.29 0.0 0.0"
            ldauj = "0.0 0.0 0.0"

        incar_lines.extend([
            "LDAU     = .TRUE.",
            "LDAUTYPE = 2",
            f"LDAUL    = {ldaul}",
            f"LDAUU    = {ldauu}",
            f"LDAUJ    = {ldauj}",
            "LMAXMIX  = 4"
        ])

    return "\n".join(incar_lines) + "\n"


def generate_carbono_script(job_name: str, tm: str, subdir: str, with_u: bool) -> str:
    bootstrap_snippet = ""
    if with_u:
        bootstrap_snippet = f"""
# --- Automatic Bootstrap from D3-only calculation ---
D3_DIR="../../crcl3-2x2-{tm}_emb-without-U/{subdir}"
if [ -s "${{D3_DIR}}/CONTCAR" ] && [ "$(wc -l < "${{D3_DIR}}/CONTCAR")" -ge 8 ]; then
    echo "Bootstrapping from converged D3 geometry: ${{D3_DIR}}/CONTCAR"
    cp "${{D3_DIR}}/CONTCAR" POSCAR
    if [ -s "${{D3_DIR}}/WAVECAR" ]; then
        echo "Found D3 WAVECAR, enabling wavefunction continuation..."
        cp "${{D3_DIR}}/WAVECAR" .
        sed -i 's/.*ISTART.*/ISTART   = 1/' INCAR 2>/dev/null || echo "ISTART = 1" >> INCAR
    fi
fi
"""

    return f"""#!/bin/bash
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
    sbatch job_carbono.sh
    exit 0
}}
trap 'checkpoint_and_resubmit' USR1 TERM

{bootstrap_snippet}

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
        sbatch job_carbono.sh
    fi
fi

exit $EXIT_CODE
"""


def generate_huk_script(job_name: str, tm: str, subdir: str, with_u: bool) -> str:
    bootstrap_snippet = ""
    if with_u:
        bootstrap_snippet = f"""
# --- Automatic Bootstrap from D3-only calculation ---
D3_DIR="../../crcl3-2x2-{tm}_emb-without-U/{subdir}"
if [ -s "${{D3_DIR}}/CONTCAR" ] && [ "$(wc -l < "${{D3_DIR}}/CONTCAR")" -ge 8 ]; then
    echo "Bootstrapping from converged D3 geometry: ${{D3_DIR}}/CONTCAR"
    cp "${{D3_DIR}}/CONTCAR" POSCAR
    if [ -s "${{D3_DIR}}/WAVECAR" ]; then
        echo "Found D3 WAVECAR, enabling wavefunction continuation..."
        cp "${{D3_DIR}}/WAVECAR" .
        sed -i 's/.*ISTART.*/ISTART   = 1/' INCAR 2>/dev/null || echo "ISTART = 1" >> INCAR
    fi
fi
"""

    return f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition=alto,medio
#SBATCH --nodes=1
#SBATCH --ntasks=28
#SBATCH --time=04:00:00
#SBATCH --output=job.%j.out
#SBATCH --error=job.%j.err

echo "=========================================================="
echo "Starting Huk Calculation: $SLURM_JOB_NAME ($SLURM_JOB_ID)"
echo "Executing on: $(hostname) at $(date)"
echo "=========================================================="

source /etc/profile.d/modules.sh 2>/dev/null || true
export OMP_NUM_THREADS=1
ulimit -s unlimited

{bootstrap_snippet}

if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    if [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
    fi
fi

sed -i "s/.*NCORE.*/NCORE    = 4/" INCAR

mpirun -np 28 /opt/vasp/vasp.6.3.0/bin/vasp_std > run.log 2>&1
"""


def main():
    print("=" * 70)
    print(" Setting up Progressive Embedded D3 and +U Calculations for CrCl3")
    print("=" * 70)

    for tm_key, tm_info in METALS.items():
        tm_sym = tm_info["symbol"]
        tm_mag = tm_info["magmom"]

        for with_u in [False, True]:
            u_suffix = "with-U" if with_u else "without-U"
            base_dir = os.path.join(NEWCALS_DIR, f"crcl3-2x2-{tm_key}_emb-{u_suffix}")

            for state in ["clean", "H_ads"]:
                has_h = (state == "H_ads")
                calc_dir = os.path.join(base_dir, state)
                os.makedirs(calc_dir, exist_ok=True)

                # 1. Source POSCAR
                src_dir = tm_info["h_src"] if has_h else tm_info["clean_src"]
                src_contcar = os.path.join(src_dir, "CONTCAR")
                dst_poscar = os.path.join(calc_dir, "POSCAR")

                if os.path.exists(src_contcar) and os.path.getsize(src_contcar) > 100:
                    shutil.copy(src_contcar, dst_poscar)
                else:
                    print(f"Error: Missing source CONTCAR at {src_contcar}")
                    continue

                # 2. POTCAR
                src_potcar = os.path.join(src_dir, "POTCAR")
                dst_potcar = os.path.join(calc_dir, "POTCAR")
                if os.path.exists(src_potcar):
                    shutil.copy(src_potcar, dst_potcar)

                # 3. KPOINTS
                with open(os.path.join(calc_dir, "KPOINTS"), "w") as f:
                    f.write(KPOINTS_CONTENT)

                # 4. INCAR
                incar_content = generate_incar(tm_sym, tm_mag, has_h, with_u)
                with open(os.path.join(calc_dir, "INCAR"), "w") as f:
                    f.write(incar_content)

                # 5. Slurm Scripts
                u_tag = "U3" if with_u else "D3"
                h_tag = "H" if has_h else "cln"
                job_name = f"{tm_sym}_emb_{h_tag}_{u_tag}"

                carbono_script = generate_carbono_script(job_name, tm_key, state, with_u)
                with open(os.path.join(calc_dir, "job_carbono.sh"), "w") as f:
                    f.write(carbono_script)
                os.chmod(os.path.join(calc_dir, "job_carbono.sh"), 0o755)

                huk_script = generate_huk_script(job_name, tm_key, state, with_u)
                with open(os.path.join(calc_dir, "job_huk.sh"), "w") as f:
                    f.write(huk_script)
                os.chmod(os.path.join(calc_dir, "job_huk.sh"), 0o755)

                print(f"  [+] Created: {calc_dir}")

    # Generate Master Dispatch Script
    dispatch_script_path = os.path.join(NEWCALS_DIR, "submit_embedded_progression.sh")
    with open(dispatch_script_path, "w") as f:
        f.write("""#!/bin/bash
# ==============================================================================
#  submit_embedded_progression.sh
# ==============================================================================
#  Submits D3-only jobs first, and chains +U jobs with --dependency=afterok!
#  Target cluster selection:
#    Usage: ./submit_embedded_progression.sh [carbono|huk]
# ==============================================================================

CLUSTER=${1:-carbono}
SCRIPT_NAME="job_${CLUSTER}.sh"

echo "=========================================================="
echo " Submitting Progressive Embedded Calculations to $CLUSTER"
echo " Batch Script Target: $SCRIPT_NAME"
echo "=========================================================="

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for TM in co fe ni; do
    for STATE in clean H_ads; do
        D3_DIR="${BASE_DIR}/crcl3-2x2-${TM}_emb-without-U/${STATE}"
        U_DIR="${BASE_DIR}/crcl3-2x2-${TM}_emb-with-U/${STATE}"

        echo ""
        echo "--> Processing System: ${TM} (${STATE})"

        # 1. Submit D3-only calculation
        cd "${D3_DIR}"
        echo "Submitting D3 (without-U) in: ${D3_DIR}"
        SUBMIT_OUT=$(sbatch "${SCRIPT_NAME}")
        echo "Slurm Response: $SUBMIT_OUT"
        JOB_ID_D3=$(echo "$SUBMIT_OUT" | awk '{print $NF}')

        # 2. Submit +U calculation chained to D3 completion
        cd "${U_DIR}"
        echo "Submitting +U chained to Job $JOB_ID_D3 in: ${U_DIR}"
        SUBMIT_U_OUT=$(sbatch --dependency=afterok:${JOB_ID_D3} "${SCRIPT_NAME}")
        echo "Slurm Response: $SUBMIT_U_OUT"
    done
done

echo ""
echo "=========================================================="
echo " All embedded progressive calculations queued successfully!"
echo "=========================================================="
""")
    os.chmod(dispatch_script_path, 0o755)
    print(f"\n[+] Master workflow submission script generated: {dispatch_script_path}")


if __name__ == "__main__":
    main()
