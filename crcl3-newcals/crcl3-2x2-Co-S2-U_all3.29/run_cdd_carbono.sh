#!/bin/bash
#SBATCH -J Co_S2_cdd
#SBATCH -p nanotubo
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=03:00:00
#SBATCH -o cdd.%j.out
#SBATCH -e cdd.%j.err

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

module purge
module load gnu12 openmpi4 vasp/6.2.0 2>/dev/null || module load vasp/6.4.2 2>/dev/null || module load vasp 2>/dev/null

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=vader,self,tcp
export OMPI_MCA_mtl=^ofi,psm2
export OMPI_MCA_osc=^ucx
export UCX_TLS=sm,self

BASE_DIR="$SLURM_SUBMIT_DIR"

echo "=========================================================="
echo "[$(date)] Starting CDD Suite for Co (S2 Hollow, +U_all)"
echo "Host: $(hostname) | Cores: $SLURM_NTASKS"
echo "=========================================================="

# 1. Run 03_cdd_isolated_tm
echo "[$(date)] Running 03_cdd_isolated_tm..."
cd "$BASE_DIR/03_cdd_isolated_tm"
mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1
if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "[$(date)] 03_cdd_isolated_tm CONVERGED!"
else
    echo "[$(date)] WARNING: 03_cdd_isolated_tm check status in vasp.out"
fi

# 2. Run 02_cdd_slab
echo "[$(date)] Running 02_cdd_slab..."
cd "$BASE_DIR/02_cdd_slab"
mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1
if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "[$(date)] 02_cdd_slab CONVERGED!"
else
    echo "[$(date)] WARNING: 02_cdd_slab check status in vasp.out"
fi

echo "=========================================================="
echo "[$(date)] All CDD calculations completed!"
echo "=========================================================="
