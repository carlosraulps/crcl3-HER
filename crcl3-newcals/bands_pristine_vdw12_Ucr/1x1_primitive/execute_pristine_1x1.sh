#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Running Step 1: SCF ground state ==="
cp INCAR_SCF INCAR
cp KPOINTS_SCF KPOINTS

/home/cr/.local/bin/micromamba run -n materials-env mpirun -np 16 /home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std > vasp_scf.out 2>&1

if ! grep -q "1 F=" OSZICAR; then
    echo "ERROR: SCF did not complete!"
    exit 1
fi
echo "SCF Completed successfully!"

echo "=== Running Step 2: NSCF Band Structure ==="
cp INCAR_BANDS INCAR
cp KPOINTS_BANDS KPOINTS

/home/cr/.local/bin/micromamba run -n materials-env mpirun -np 16 /home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std > vasp_bands.out 2>&1

if [ ! -s EIGENVAL ] && ! grep -q "General timing" OUTCAR && ! grep -q "1 F=" OSZICAR; then
    echo "ERROR: Band structure run did not complete!"
    exit 1
fi
echo "Band Structure Completed successfully!"
