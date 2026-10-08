#!/bin/bash
#SBATCH -J Ni_embedded_cohp
#SBATCH -p nanotubo
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=03:00:00
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

# 1. Run VASP static SCF with LWAVE=.TRUE. and ISYM=-1
mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1

# 2. Run LOBSTER if WAVECAR exists
if [ -s WAVECAR ]; then
    echo "[$(date)] VASP SCF completed. Running LOBSTER COHP analysis..."
    if [ -x ~/.local/bin/lobster ]; then
        ~/.local/bin/lobster > lobster.out 2>&1
    elif which lobster >/dev/null 2>&1; then
        lobster > lobster.out 2>&1
    fi
    echo "[$(date)] LOBSTER completed with exit code $?"
fi
