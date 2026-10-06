#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Running Step 1: Ground-State SCF (pristine 2x2) ==="
cp INCAR_SCF INCAR
cp KPOINTS_SCF KPOINTS

if command -v srun &>/dev/null; then
    srun vasp_std > vasp_scf.out 2>&1
elif [ -f /home/cr/.local/bin/micromamba ]; then
    /home/cr/.local/bin/micromamba run -n materials-env mpirun -np 16 /home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std > vasp_scf.out 2>&1
else
    mpirun vasp_std > vasp_scf.out 2>&1
fi

if ! grep -q "1 F=" OSZICAR; then
    echo "ERROR: SCF calculation did not converge!"
    exit 1
fi
echo "SCF Completed. Generating DOSCAR backup..."
cp DOSCAR DOSCAR.scf

echo "=== Running Step 2: Non-Self-Consistent Band Structure (pristine 2x2) ==="
cp INCAR_BANDS INCAR
cp KPOINTS_BANDS KPOINTS

if command -v srun &>/dev/null; then
    srun vasp_std > vasp_bands.out 2>&1
elif [ -f /home/cr/.local/bin/micromamba ]; then
    /home/cr/.local/bin/micromamba run -n materials-env mpirun -np 16 /home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std > vasp_bands.out 2>&1
else
    mpirun vasp_std > vasp_bands.out 2>&1
fi

if [ ! -s EIGENVAL ] && ! grep -q "General timing" OUTCAR && ! grep -q "1 F=" OSZICAR; then
    echo "ERROR: Band calculation did not converge!"
    exit 1
fi
echo "Band Structure Completed successfully for pristine 2x2!"
