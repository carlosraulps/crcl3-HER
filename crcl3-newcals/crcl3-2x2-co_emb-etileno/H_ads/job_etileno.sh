#!/bin/bash
#SBATCH -J Co_emb_H_eti
#SBATCH -p etileno
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --signal=B:USR1@300
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

echo "=========================================================="
echo "Job Name:    $SLURM_JOB_NAME"
echo "Job ID:      $SLURM_JOB_ID"
echo "Host:        $(hostname)"
echo "Directory:   $(pwd)"
echo "Start Time:  $(date)"
echo "CPUs Alloc:  $SLURM_NTASKS (Partition: etileno, Node: gn04)"
echo "Time Limit:  24:00:00"
echo "=========================================================="

trap_timeout() {
    echo "[$(date)] SIGUSR1 received - checkpointing CONTCAR..."
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        sbatch job_etileno.sh
    fi
    exit 0
}
trap trap_timeout USR1

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

module purge
module load gnu12 openmpi4 vasp/6.2.0

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=vader,self,tcp
export OMPI_MCA_mtl=^ofi,psm2
export OMPI_MCA_osc=^ucx
export UCX_TLS=sm,self

echo "[$(date)] Starting Phase 2 (+U) Fast Continuation from Step 12..."
mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp_u.out 2>&1

if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "[$(date)] Phase 2 (+U) CONVERGED successfully!"
    mkdir -p u_converged
    cp CONTCAR u_converged/
    cp OUTCAR   u_converged/
    cp OSZICAR  u_converged/
    cp vasprun.xml u_converged/ 2>/dev/null || true
    echo "Finished At: $(date)"
    exit 0
else
    echo "[$(date)] Need continuation..."
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp CONTCAR POSCAR
        sbatch job_etileno.sh
    fi
fi
