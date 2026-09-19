#!/bin/bash
#SBATCH -J H_S3_no_vdw
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --exclusive
#SBATCH --time=24:00:00

PROJECT_DIR="/home/cr/mnt/google-drive/Proyectos/paper-adaptation/crcl3-newcals/crcl3-2x2-h_ads-without-U/no_vdw/S3"
SCRATCH_DIR="/home/cr/scratch_vasp/crcl3-2x2-h_ads-without-U/no_vdw/S3"

echo "Starting VASP job on $(hostname) at $(date)"
echo "Scratch directory: $SCRATCH_DIR"
echo "Project destination: $PROJECT_DIR"

# Clean scratch directory to guarantee fresh execution
rm -rf "$SCRATCH_DIR"
mkdir -p "$SCRATCH_DIR"
cp "$PROJECT_DIR"/INCAR "$PROJECT_DIR"/POSCAR "$PROJECT_DIR"/POTCAR "$PROJECT_DIR"/KPOINTS "$SCRATCH_DIR"/
cd "$SCRATCH_DIR"

export OMP_NUM_THREADS=1
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_rmaps_default_mapping_policy=:oversubscribe

# Execute VASP with 16 ranks and 1 OpenMP thread per rank
run_vasp -np 16 -nt 1 > vasp_run.log 2>&1

EXIT_CODE=$?
echo "VASP finished with exit code $EXIT_CODE. Syncing results back to project..."
cp "$SCRATCH_DIR"/OUTCAR "$SCRATCH_DIR"/CONTCAR "$SCRATCH_DIR"/EIGENVAL "$SCRATCH_DIR"/DOSCAR "$SCRATCH_DIR"/vasprun.xml "$SCRATCH_DIR"/OSZICAR "$SCRATCH_DIR"/vasp_run.log "$PROJECT_DIR"/ 2>/dev/null || true

echo "Completed at $(date) with exit code $EXIT_CODE"
exit $EXIT_CODE
