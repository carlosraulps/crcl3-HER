#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

DIRNAME=$(basename "$PWD")
echo "=== Running Step 1: Ground-State SCF ($DIRNAME) ==="
cp INCAR_SCF INCAR
cp KPOINTS_SCF KPOINTS

if [ -n "$SLURM_JOB_ID" ]; then
    # Slurm cluster (Carbono / Huk) OpenMPI execution
    export OMPI_MCA_pml=ob1
    export OMPI_MCA_btl=vader,self,tcp
    export OMPI_MCA_mtl=^ofi,psm2
    export OMPI_MCA_osc=^ucx
    export UCX_TLS=sm,self
    mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np ${SLURM_NTASKS:-32} vasp_std > vasp_scf.out 2>&1
elif [ -f /home/cr/.local/bin/micromamba ]; then
    /home/cr/.local/bin/micromamba run -n materials-env mpirun -np 16 /home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std > vasp_scf.out 2>&1
else
    mpirun -np ${SLURM_NTASKS:-16} vasp_std > vasp_scf.out 2>&1
fi

if ! grep -q "1 F=" OSZICAR; then
    echo "ERROR: SCF calculation did not converge!"
    exit 1
fi
echo "SCF Completed. Generating DOSCAR backup..."
cp DOSCAR DOSCAR.scf

echo "=== Running Step 2: Non-Self-Consistent Band Structure ($DIRNAME) ==="
cp INCAR_BANDS INCAR
cp KPOINTS_BANDS KPOINTS

if [ -n "$SLURM_JOB_ID" ]; then
    mpirun --mca pml ob1 --mca btl vader,self,tcp --mca mtl ^ofi,psm2 --bind-to none -np ${SLURM_NTASKS:-32} vasp_std > vasp_bands.out 2>&1
elif [ -f /home/cr/.local/bin/micromamba ]; then
    /home/cr/.local/bin/micromamba run -n materials-env mpirun -np 16 /home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std > vasp_bands.out 2>&1
else
    mpirun -np ${SLURM_NTASKS:-16} vasp_std > vasp_bands.out 2>&1
fi

if [ ! -s EIGENVAL ] && ! grep -q "General timing" OUTCAR && ! grep -q "1 F=" OSZICAR; then
    echo "ERROR: Band calculation did not converge!"
    exit 1
fi
echo "Band Structure Completed successfully for $DIRNAME!"
