#!/bin/bash
# Local CDD Pipeline on Arch (16 cores AMD Ryzen)
set -e

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
MPIRUN="/home/cr/.local/share/mamba/envs/vasp-env/bin/mpirun"
VASP_BIN="/home/cr/computational-materials-suite/bin/vasp_std"
BASE_DIR="/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-Co-S2-U_all3.29"

echo "=========================================================="
echo "[$(date)] Starting Local CDD Pipeline on Arch"
echo "Cores: 16 | Host: $(hostname)"
echo "=========================================================="

# 1. Isolated Co Atom
echo "[$(date)] [1/3] Running 03_cdd_isolated_tm..."
cd "$BASE_DIR/03_cdd_isolated_tm"
$MPIRUN -np 16 $VASP_BIN > vasp.out 2>&1
echo "[$(date)] 03_cdd_isolated_tm finished with exit code $?"

# 2. Pristine CrCl3 Slab
echo "[$(date)] [2/3] Running 02_cdd_slab..."
cd "$BASE_DIR/02_cdd_slab"
$MPIRUN -np 16 $VASP_BIN > vasp.out 2>&1
echo "[$(date)] 02_cdd_slab finished with exit code $?"

# 3. Postprocessing & Bader
echo "[$(date)] [3/3] Running postprocess_cdd_and_bader.py..."
cd "$BASE_DIR"
python3 postprocess_cdd_and_bader.py

echo "=========================================================="
echo "[$(date)] CDD Pipeline Successfully Completed!"
echo "=========================================================="
