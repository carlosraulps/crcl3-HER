#!/bin/bash
#SBATCH --job-name=Co_emb_band
#SBATCH --output=Co_embedded_band.%j.out
#SBATCH --error=Co_embedded_band.%j.err
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=03:00:00

export OMP_NUM_THREADS=1
ulimit -s unlimited

bash ./run_bands.sh
