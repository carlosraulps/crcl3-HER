#!/bin/bash
#SBATCH -J cdd_slabs
#SBATCH -p nanotubo
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH -o /home/carlos.primo/crcl3-HER/cdd_frozen_slabs/cdd_slabs.%j.out
#SBATCH -e /home/carlos.primo/crcl3-HER/cdd_frozen_slabs/cdd_slabs.%j.err

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

module purge
module load gnu12 openmpi4 vasp/6.2.0 2>/dev/null || module load vasp/6.4.2 2>/dev/null || module load vasp 2>/dev/null

BASE=/home/carlos.primo/crcl3-HER/cdd_frozen_slabs

for name in Fe_slab_Ucr Ni_slab_Ucr Fe_slab_Uall Ni_slab_Uall; do
    echo "=========================================="
    echo "[$(date)] Starting $name..."
    cd $BASE/$name
    mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1
    if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
        echo "[$(date)] $name CONVERGED!"
    else
        echo "[$(date)] WARNING: $name check status in vasp.out"
    fi
done

echo "=========================================="
echo "[$(date)] All 4 frozen slabs completed!"
