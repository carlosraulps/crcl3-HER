#!/bin/bash
#SBATCH -J Co_emb_H_U3
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
        echo "Calculation converged! No resubmission needed."
        rm -f STOPCAR
        exit 0
    fi
    if [ -s CONTCAR ] && [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp POSCAR "POSCAR.step_${SLURM_JOB_ID}"
        cp CONTCAR POSCAR
        cp OUTCAR  "OUTCAR.step_${SLURM_JOB_ID}" 2>/dev/null || true
    fi
    rm -f STOPCAR
    sbatch job_carbono.sh
    exit 0
}
trap 'checkpoint_and_resubmit' USR1 TERM


# --- Automatic Bootstrap from D3-only calculation ---
D3_DIR="../../crcl3-2x2-co_emb-without-U/H_ads"
if [ -s "${D3_DIR}/CONTCAR" ] && [ "$(wc -l < "${D3_DIR}/CONTCAR")" -ge 8 ]; then
    echo "Bootstrapping from converged D3 geometry: ${D3_DIR}/CONTCAR"
    cp "${D3_DIR}/CONTCAR" POSCAR
    if [ -s "${D3_DIR}/WAVECAR" ]; then
        echo "Found D3 WAVECAR, enabling wavefunction continuation..."
        cp "${D3_DIR}/WAVECAR" .
        sed -i 's/.*ISTART.*/ISTART   = 1/' INCAR 2>/dev/null || echo "ISTART = 1" >> INCAR
    fi
fi


if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    NLINES=$(wc -l < CONTCAR)
    if [ "$NLINES" -ge 8 ]; then
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
    fi
fi

sed -i "s/.*NCORE.*/NCORE    = 8/" INCAR

module purge
module load gnu12 openmpi4 vasp/6.2.0

export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=vader,self,tcp
export OMPI_MCA_mtl=^ofi,psm2
export OMPI_MCA_osc=^ucx
export UCX_TLS=sm,self

mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np $SLURM_NTASKS vasp_std > vasp.out 2>&1 &
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
        sbatch job_carbono.sh
    fi
fi

exit $EXIT_CODE
