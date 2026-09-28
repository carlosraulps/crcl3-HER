#!/usr/bin/env python3
"""
========================================================================================
setup_metano_pipeline.py
========================================================================================
Sets up parallel embedded pipeline calculations targeting the newly discovered
instant GPU nodes on Carbono:
  - metano (node gn01): Co_emb_cln and Co_emb_H (32 CPUs + 1 GPU each)
  - etileno (node gn04): Fe_emb_cln (32 CPUs + 1 GPU)

Preserves ALL existing pending jobs in nanotubo untouched.
========================================================================================
"""

import os
import shutil

BASE_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals"

def create_metano_job_script(job_name: str, partition: str = "metano") -> str:
    return f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -p {partition}
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=24:00:00
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
echo "CPUs Alloc:  $SLURM_NTASKS (Partition: {partition})"
echo "GPU Alloc:   $CUDA_VISIBLE_DEVICES"
echo "Time Limit:  24:00:00 (In-Allocation Pipeline D3 -> +U)"
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

def setup_metano_directories():
    tasks = [
        ("crcl3-2x2-co_emb-pipeline", "crcl3-2x2-co_emb-metano", "Co_emb", "metano"),
        ("crcl3-2x2-fe_emb-pipeline", "crcl3-2x2-fe_emb-metano", "Fe_emb", "etileno"),
    ]

    for src_dir, dst_dir, tag, partition in tasks:
        src_path = os.path.join(BASE_DIR, src_dir)
        dst_path = os.path.join(BASE_DIR, dst_dir)
        
        for sub in ["clean", "H_ads"]:
            src_sub = os.path.join(src_path, sub)
            dst_sub = os.path.join(dst_path, sub)
            if not os.path.exists(src_sub):
                continue
            os.makedirs(dst_sub, exist_ok=True)
            
            for fname in ["INCAR.d3", "INCAR.u", "KPOINTS", "POSCAR", "POTCAR"]:
                s = os.path.join(src_sub, fname)
                d = os.path.join(dst_sub, fname)
                if os.path.exists(s):
                    shutil.copy2(s, d)
            
            # Create default INCAR
            shutil.copy2(os.path.join(dst_sub, "INCAR.d3"), os.path.join(dst_sub, "INCAR"))
            
            # Write specialized job script
            job_name = f"{tag}_{'cln' if sub == 'clean' else 'H'}_{partition[:3]}"
            script_content = create_metano_job_script(job_name, partition=partition)
            with open(os.path.join(dst_sub, "job_carbono.sh"), "w") as f:
                f.write(script_content)
            os.chmod(os.path.join(dst_sub, "job_carbono.sh"), 0o755)
            print(f"✔ Prepared {dst_sub} (Partition: {partition}, Name: {job_name})")

    # Generate master submission script
    submit_script = f"""#!/bin/bash
# Master Dispatch for Instant GPU Node Calculations on Carbono
BASE_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
echo '=========================================================='
echo ' Dispatching Instant Jobs to metano (gn01) & etileno (gn04)'
echo '=========================================================='
echo '--> Submitting Co_emb (clean) to metano...'
cd "${{BASE_DIR}}/crcl3-2x2-co_emb-metano/clean"
sbatch job_carbono.sh

echo '--> Submitting Co_emb (H_ads) to metano...'
cd "${{BASE_DIR}}/crcl3-2x2-co_emb-metano/H_ads"
sbatch job_carbono.sh

echo '--> Submitting Fe_emb (clean) to etileno...'
cd "${{BASE_DIR}}/crcl3-2x2-fe_emb-metano/clean"
sbatch job_carbono.sh

echo '=========================================================='
echo ' All 3 instant pipeline jobs submitted!'
echo '=========================================================='
"""
    submit_path = os.path.join(BASE_DIR, "submit_instant_gpu_pipeline.sh")
    with open(submit_path, "w") as f:
        f.write(submit_script)
    os.chmod(submit_path, 0o755)
    print(f"✔ Generated master submission script: {submit_path}")

if __name__ == "__main__":
    setup_metano_directories()
