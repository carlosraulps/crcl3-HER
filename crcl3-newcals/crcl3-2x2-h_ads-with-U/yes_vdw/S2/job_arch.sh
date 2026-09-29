#!/bin/bash
#SBATCH -J H2x2_S2_U3_arch
#SBATCH -p batch
#SBATCH -n 16
#SBATCH --time=12:00:00
#SBATCH -o job.arch.%j.out
#SBATCH -e job.arch.%j.err

ulimit -s unlimited
export OMP_NUM_THREADS=1

renice -n 15 $$ 2>/dev/null || true

sed -i "s/.*NCORE.*/NCORE    = 4/" INCAR

echo "=========================================================="
echo "Starting Slurm Job on Arch: $SLURM_JOB_NAME ($SLURM_JOB_ID)"
echo "Executing on Host         : $(hostname)"
echo "Working Directory         : $(pwd)"
echo "Start Timestamp           : $(date)"
echo "=========================================================="

/home/cr/.local/share/mamba/envs/vasp-env/bin/mpirun --bind-to none -np $SLURM_NTASKS /home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std > run.arch.log 2>&1
EXIT_CODE=$?

echo "=========================================================="
echo "Execution finished at $(date) with exit code: $EXIT_CODE"
if grep -q "reached required accuracy" run.arch.log 2>/dev/null || grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo ">>> STATUS: VASP CALCULATION CONVERGED SUCCESSFULLY <<<"
fi
echo "=========================================================="
exit $EXIT_CODE
