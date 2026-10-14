#!/bin/bash
#SBATCH -J CoFeNi_Cohesive_PBE_D3
#SBATCH -o job.%j.out
#SBATCH -e job.%j.err
#SBATCH --partition=medio
#SBATCH --nodes=1
#SBATCH --ntasks=28
#SBATCH --time=12:00:00

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

ROOT_DIR=/home/carlos/crcl3-newcals/cohesive_energies_CoFeNi_PBE-D3
cd "$ROOT_DIR"

NPROCS=${SLURM_NTASKS:-28}

echo "=================================================================="
echo " 🚀 BATCH RUNNING COHESIVE ENERGY CALCULATIONS FOR Co, Fe, Ni"
echo " Date: $(date)"
echo " Host: $(hostname)"
echo " Node: $SLURM_NODELIST"
echo " Cores: $NPROCS"
echo "=================================================================="

RUN_DIRS=(
    "atom/Co"
    "atom/Fe"
    "atom/Ni"
    "bulk/Co"
    "bulk/Fe"
    "bulk/Ni"
)

for d in "${RUN_DIRS[@]}"; do
    echo "--------------------------------------------------"
    echo " ▶ Running calculation in $d..."
    cd "$ROOT_DIR/$d" || continue
    start_t=$(date +%s)
    mpirun -np $NPROCS /opt/vasp/vasp/bin/vasp_std > run.log 2>&1
    ret=$?
    end_t=$(date +%s)
    elap=$((end_t - start_t))
    
    if grep -q "General timing and accounting informations for this job" run.log 2>/dev/null; then
        echo "   ✅ $d converged successfully in ${elap}s."
    else
        echo "   ⚠️ $d finished with exit code $ret in ${elap}s. Check run.log!"
    fi
done

cd "$ROOT_DIR"
echo "=================================================================="
echo " 📊 CALCULATING FINAL COHESIVE ENERGIES (PBE-D3(BJ))"
echo "=================================================================="

python3 - << 'EOF'
import os

configs = {
    'Co': ('atom/Co', 'bulk/Co', 2),
    'Fe': ('atom/Fe', 'bulk/Fe', 2),
    'Ni': ('atom/Ni', 'bulk/Ni', 4),
}

def get_e0(path):
    osz = os.path.join(path, 'OSZICAR')
    if not os.path.exists(osz):
        return None
    e0 = None
    with open(osz) as f:
        for line in f:
            if 'E0=' in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p == 'E0=':
                        e0 = float(parts[i+1])
    return e0

def get_mag(path):
    out = os.path.join(path, 'OUTCAR')
    if not os.path.exists(out): return None
    mag = None
    with open(out, errors='ignore') as f:
        for line in f:
            if 'number of electron' in line and 'magnetization' in line:
                mag = float(line.split()[-1])
    return mag

print(f"{'Metal':<8} | {'E_atom (eV)':<14} | {'E_bulk (eV)':<14} | {'N_atoms':<8} | {'E_bulk/N (eV)':<14} | {'E_coh (eV/atom)':<16} | {'Mag (mu_B/at)'}")
print("-" * 105)

summary_lines = []
for metal, (atom_dir, bulk_dir, n_atoms) in configs.items():
    e_atom = get_e0(atom_dir)
    e_bulk = get_e0(bulk_dir)
    mag_bulk = get_mag(bulk_dir)
    mag_atom = get_mag(atom_dir)
    
    if e_atom is not None and e_bulk is not None:
        e_bulk_per_atom = e_bulk / n_atoms
        e_coh = e_atom - e_bulk_per_atom
        mag_per_at = (mag_bulk / n_atoms) if mag_bulk is not None else 0.0
        line = f"{metal:<8} | {e_atom:<14.6f} | {e_bulk:<14.6f} | {n_atoms:<8} | {e_bulk_per_atom:<14.6f} | {e_coh:<16.4f} | {mag_per_at:<.3f}"
        print(line)
        summary_lines.append(f"{metal}: E_coh = {e_coh:.4f} eV/atom (E_atom={e_atom:.4f} eV, E_bulk/N={e_bulk_per_atom:.4f} eV, mu={mag_per_at:.2f} mu_B/atom)")
    else:
        print(f"{metal:<8} | ERROR: Incomplete outputs (E_atom={e_atom}, E_bulk={e_bulk})")

with open('COHESIVE_ENERGY_SUMMARY.txt', 'w') as f:
    f.write("\n".join(summary_lines) + "\n")
EOF

echo "=================================================================="
echo " Calculation finished at $(date)"
