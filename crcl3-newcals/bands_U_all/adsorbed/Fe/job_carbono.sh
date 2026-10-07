#!/bin/bash
#SBATCH --job-name=Fe_ads_b_Uall
#SBATCH --output=%x.%j.out
#SBATCH --error=%x.%j.err
#SBATCH --partition=nanotubo
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=03:00:00
#SBATCH --signal=B:USR1@300

module purge
module load gnu12 openmpi4 vasp/6.2.0

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=vader,self,tcp
export OMPI_MCA_mtl=^ofi,psm2
export OMPI_MCA_osc=^ucx
export UCX_TLS=sm,self
export OMP_NUM_THREADS=1
ulimit -s unlimited 2>/dev/null || true

bash ./run_bands.sh
