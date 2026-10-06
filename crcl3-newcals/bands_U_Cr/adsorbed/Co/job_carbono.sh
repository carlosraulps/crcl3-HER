#!/bin/bash
#SBATCH --job-name=Co_ads_band
#SBATCH --output=Co_adsorbed_band.%j.out
#SBATCH --error=Co_adsorbed_band.%j.err
#SBATCH --partition=nanotubo
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=03:00:00
#SBATCH --signal=B:USR1@300

module purge
module load vasp/6.4.2-intel2021.4 2>/dev/null || module load vasp 2>/dev/null || true

export OMP_NUM_THREADS=1
ulimit -s unlimited

bash ./run_bands.sh
