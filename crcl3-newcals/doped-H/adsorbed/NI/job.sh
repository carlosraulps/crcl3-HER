#!/bin/bash
#SBATCH --job-name=vasp_job
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --time=24:00:00

mpirun -np 16 vasp_std > run.log
