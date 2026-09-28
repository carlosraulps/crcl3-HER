#!/bin/bash
#SBATCH --job-name=Ni_emb_H_U3
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


# --- Automatic Bootstrap from D3-only calculation ---
D3_DIR="../../crcl3-2x2-ni_emb-without-U/H_ads"
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
    if [ "$(wc -l < CONTCAR)" -ge 8 ]; then
        cp POSCAR "POSCAR.bak_$(date +%s)"
        cp CONTCAR POSCAR
    fi
fi

sed -i "s/.*NCORE.*/NCORE    = 4/" INCAR

mpirun -np 28 /opt/vasp/vasp.6.3.0/bin/vasp_std > run.log 2>&1
