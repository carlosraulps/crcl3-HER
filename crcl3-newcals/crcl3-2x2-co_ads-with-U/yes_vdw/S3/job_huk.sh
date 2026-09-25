#!/bin/bash
#SBATCH -J Co_S3_U329
#SBATCH -o job.%j.out
#SBATCH -e job.%j.err
#SBATCH --partition=alto,medio
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --time=168:00:00

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

echo "=========================================================="
echo "Starting Slurm Job : $SLURM_JOB_NAME ($SLURM_JOB_ID)"
echo "Executing on Host  : $(hostname)"
echo "Partition Selected : $SLURM_JOB_PARTITION"
echo "Allocated Node(s)  : $SLURM_NODELIST"
echo "Allocated CPUs     : $SLURM_CPUS_ON_NODE"
echo "Working Directory  : $(pwd)"
echo "Start Timestamp    : $(date)"
echo "=========================================================="

NPROCS=${SLURM_CPUS_ON_NODE:-$(nproc)}
if [ -z "$NPROCS" ] || [ "$NPROCS" -le 1 ]; then
    NPROCS=$(nproc)
fi

if [ "$NPROCS" -eq 36 ]; then
    NCORE_OPT=6
elif [ "$NPROCS" -eq 28 ]; then
    NCORE_OPT=4
else
    NCORE_OPT=4
fi

sed -i "s/.*NCORE.*/NCORE    = $NCORE_OPT/" INCAR

echo "Running VASP with $NPROCS MPI processes (NCORE=$NCORE_OPT)..."
mpirun -np $NPROCS vasp_std > run.log 2>&1
EXIT_CODE=$?

echo "=========================================================="
echo "Execution finished at $(date) with exit code: $EXIT_CODE"
if grep -q "General timing and accounting informations for this job" run.log 2>/dev/null || grep -q "reached required accuracy" run.log 2>/dev/null; then
    echo ">>> STATUS: VASP CALCULATION CONVERGED SUCCESSFULLY <<<"
fi
echo "=========================================================="
exit $EXIT_CODE
