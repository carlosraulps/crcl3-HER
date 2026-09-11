#!/bin/bash
#SBATCH -J CrCl3_i3_U_4
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --exclusive
#SBATCH --time=12:00:00

PROJECT_DIR="/home/cr/cr-gd/google-drive/Proyectos/paper-adaptation/crcl3-newcals/crcl3-1x1/relax-crcl3-i3-dvw-u/U_4"
SCRATCH_DIR="/home/cr/scratch_vasp/relax-crcl3-i3-dvw-u/U_4"

echo "Starting VASP job on $(hostname) at $(date)"
echo "Scratch directory: $SCRATCH_DIR"
echo "Project destination: $PROJECT_DIR"

rm -rf "$SCRATCH_DIR"
mkdir -p "$SCRATCH_DIR"
cp "$PROJECT_DIR"/INCAR "$PROJECT_DIR"/POSCAR "$PROJECT_DIR"/POTCAR "$PROJECT_DIR"/KPOINTS "$SCRATCH_DIR"/
cd "$SCRATCH_DIR"

export OMP_NUM_THREADS=1
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_rmaps_default_mapping_policy=:oversubscribe

run_vasp -np 16 -nt 1 > vasp_run.log 2>&1

EXIT_CODE=$?
echo "VASP finished with exit code $EXIT_CODE. Syncing results back to project..."
cp "$SCRATCH_DIR"/OUTCAR "$SCRATCH_DIR"/CONTCAR "$SCRATCH_DIR"/EIGENVAL "$SCRATCH_DIR"/DOSCAR "$SCRATCH_DIR"/vasprun.xml "$SCRATCH_DIR"/OSZICAR "$SCRATCH_DIR"/vasp_run.log "$PROJECT_DIR"/ 2>/dev/null || true

echo "Completed at $(date) with exit code $EXIT_CODE"
exit $EXIT_CODE
