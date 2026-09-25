#!/bin/bash
#SBATCH -J Ni_S2_U3
#SBATCH -p fulereno
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --signal=B:USR1@300
#SBATCH --requeue
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

echo "=========================================================="
echo "Job Name:    $SLURM_JOB_NAME"
echo "Job ID:      $SLURM_JOB_ID"
echo "Host:        $(hostname)"
echo "Directory:   $(pwd)"
echo "Start Time:  $(date)"
echo "CPUs Alloc:  $SLURM_NTASKS"
echo "Time Limit:  04:00:00 (Micro-Batch Chained)"
echo "=========================================================="

ulimit -s unlimited 2>/dev/null || true
export OMP_NUM_THREADS=1

checkpoint_and_resubmit() {
    echo "[$(date)] Slurm USR1 intercepted — graceful checkpoint..."
    echo "LSTOP = .TRUE." > STOPCAR
    if [ -n "$VASP_PID" ]; then
        wait $VASP_PID
    fi
    if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
        echo "Calculated converged! No resubmission needed."
        rm -f STOPCAR
        exit 0
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp POSCAR "POSCAR.step_${SLURM_JOB_ID}"
        cp CONTCAR POSCAR
        cp OUTCAR  "OUTCAR.step_${SLURM_JOB_ID}" 2>/dev/null || true
    fi
    rm -f STOPCAR
    sbatch job.sh
    exit 0
}
trap 'checkpoint_and_resubmit' USR1 TERM

if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    NLINES=$(wc -l < CONTCAR)
    if [ "$NLINES" -ge 8 ]; then
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
    fi
fi

sed -i "s/.*NCORE.*/NCORE    = 8/" INCAR

module purge
module load vasp/6.2.0

mpirun --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1 &
VASP_PID=$!
wait $VASP_PID
EXIT_CODE=$?

rm -f STOPCAR

if grep -q "reached required accuracy" OUTCAR 2>/dev/null; then
    echo "VASP converged within walltime window!"
    exit 0
else
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
        sbatch job.sh
    fi
fi

exit $EXIT_CODE
