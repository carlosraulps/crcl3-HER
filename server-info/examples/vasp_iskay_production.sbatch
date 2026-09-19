#!/bin/bash
#SBATCH --job-name=vasp_iskay
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --time=14-00:00:00
#SBATCH --mem=120G
#SBATCH --cpu-bind=cores
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

# ==============================================================================
# Production VASP Template for Iskay Cluster (256-core AMD/Intel Node)
# Allocates 64 dedicated physical cores with CPU core pinning
# ==============================================================================

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

echo "Iskay Calculation $SLURM_JOB_ID started on $(hostname) at $(date)"
echo "Allocated: $SLURM_NODELIST with $SLURM_NTASKS tasks"

srun --cpu-bind=cores vasp_std

echo "Iskay Calculation completed at $(date)"
