#!/bin/bash
#SBATCH --job-name=Co_ads_band
#SBATCH --output=Co_adsorbed_band.%j.out
#SBATCH --error=Co_adsorbed_band.%j.err
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=03:00:00

export OMP_NUM_THREADS=1
ulimit -s unlimited

bash ./run_bands.sh
