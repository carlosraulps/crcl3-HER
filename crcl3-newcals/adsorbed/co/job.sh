#!/bin/bash
#SBATCH -J VASP_LOBSTER
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=24:00:00

# 1. Run VASP Static Calculation (MPI)
mpirun -np $SLURM_NTASKS vasp_std > vasp_run.log 2>&1

# 2. Verify VASP finished successfully
if grep -q "reached required accuracy" vasp_run.log || grep -q "writing wavefunctions" vasp_run.log; then
    echo "VASP completed. Starting LOBSTER..."
    
    # 3. Configure OpenMP for LOBSTER
    export OMP_NUM_THREADS=$SLURM_CPUS_ON_NODE
    
    # 4. Run LOBSTER
    lobster > lobster_run.log 2>&1
else
    echo "VASP failed. Skipping LOBSTER."
    exit 1
fi
