#!/bin/bash
#SBATCH -J Co_emb_H_met
#SBATCH -p metano
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
echo "CPUs Alloc:  $SLURM_NTASKS (Partition: metano)"
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
