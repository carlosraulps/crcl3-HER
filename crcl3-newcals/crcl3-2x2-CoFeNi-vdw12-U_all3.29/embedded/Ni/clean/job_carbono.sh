#!/bin/bash
#SBATCH -J Ni_emb_c_Uall
#SBATCH -p nanotubo
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=48:00:00
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
ckpt_handler() {
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
}
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
