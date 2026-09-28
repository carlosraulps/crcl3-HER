#!/bin/bash
#SBATCH --job-name=Fe_emb_H_D3
#SBATCH --partition=alto,medio
#SBATCH --nodes=1
#SBATCH --ntasks=28
#SBATCH --time=04:00:00
#SBATCH --output=job.%j.out
#SBATCH --error=job.%j.err

echo "=========================================================="
echo "Starting Huk Calculation: $SLURM_JOB_NAME ($SLURM_JOB_ID)"
echo "Executing on: $(hostname) at $(date)"
echo "=========================================================="

source /etc/profile.d/modules.sh 2>/dev/null || true
export OMP_NUM_THREADS=1
ulimit -s unlimited



if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    if [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
    fi
fi

sed -i "s/.*NCORE.*/NCORE    = 4/" INCAR

mpirun -np 28 /opt/vasp/vasp.6.3.0/bin/vasp_std > run.log 2>&1
