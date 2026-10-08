#!/bin/bash
#SBATCH -J Co_S3_Uall
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

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

module purge
module load gnu12 openmpi4 vasp/6.2.0 2>/dev/null || module load vasp/6.4.2 2>/dev/null || module load vasp 2>/dev/null

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=vader,self,tcp
export OMPI_MCA_mtl=^ofi,psm2
export OMPI_MCA_osc=^ucx
export UCX_TLS=sm,self

ckpt_handler() {
    echo "[$(date)] SIGUSR1 received! Checkpointing calculation..."
    if [ ! -s OUTCAR ] || ! grep -q "Iteration" OUTCAR 2>/dev/null; then
        echo "ERROR: Calculation failed to start or produced no output! Aborting resubmission loop." >&2
        exit 1
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        echo "[$(date)] Updated POSCAR from CONTCAR. Auto-resubmitting..."
        sbatch run_vasp.sh
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
        sbatch run_vasp.sh
    fi
fi
