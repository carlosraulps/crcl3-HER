#!/bin/bash
#SBATCH --job-name=vasp_huk_hram
#SBATCH --partition=hram
#SBATCH --nodes=1
#SBATCH --ntasks=40
#SBATCH --time=7-00:00:00
#SBATCH --mem=450G
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

# ==============================================================================
# High-RAM VASP Template for Huk Cluster (HRAM Partition - 40 cores, 504 GB)
# Ideal for 3x3 supercells, HSE06 hybrid calculations, or large GW/BSE
# ==============================================================================

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

echo "High-RAM Job $SLURM_JOB_ID started on $(hostname) at $(date)"
echo "Target: huk119 (504 GB RAM partition)"

mpirun -np $SLURM_NTASKS vasp_std

echo "High-RAM Job completed at $(date)"
