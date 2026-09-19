#!/bin/bash
#SBATCH --job-name=vasp_huk_alto
#SBATCH --partition=alto
#SBATCH --nodes=1
#SBATCH --ntasks=36
#SBATCH --time=7-00:00:00
#SBATCH --mem=80G
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

# ==============================================================================
# Production VASP Template for Huk Cluster (Alto Partition - 36 cores, 126 GB)
# ==============================================================================

# Threading & Memory Optimization
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

# Diagnostic Header
echo "Job $SLURM_JOB_ID started on $(hostname) at $(date)"
echo "Partition: $SLURM_JOB_PARTITION | Nodes: $SLURM_NODELIST ($SLURM_NTASKS cores)"

# Execute VASP via MPI launcher
mpirun -np $SLURM_NTASKS vasp_std

echo "Job $SLURM_JOB_ID completed at $(date)"
