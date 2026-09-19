import os
import shutil
import re
from ase.io import read

# Define mapping
SRC_BASE = "/Users/apple/Research/abc/paper-adaptation/f_crcl3-doped-for-HER"
DEST_BASE = "/Users/apple/Research/abc/paper-adaptation/crcl3-newcals"

systems = {
    "adsorbed/co": f"{SRC_BASE}/crcl3-co/static-scf",
    "adsorbed/fe": f"{SRC_BASE}/crcl3-fe/static-scf",
    "adsorbed/ni": f"{SRC_BASE}/crcl3-ni/static-scf",
    "embedded/co": f"{SRC_BASE}/doped_hollow_crcl3/crcl3-co/static-scf",
    "embedded/fe": f"{SRC_BASE}/doped_hollow_crcl3/crcl3-fe/static-scf",
    "embedded/ni": f"{SRC_BASE}/doped_hollow_crcl3/crcl3-ni/static-scf",
}

def extract_nbands(outcar_path):
    if not os.path.exists(outcar_path):
        return None
    with open(outcar_path, 'r') as f:
        for line in f:
            if "NBANDS=" in line:
                match = re.search(r"NBANDS=\s*(\d+)", line)
                if match:
                    return int(match.group(1))
    return None

def modify_incar(src_incar, dest_incar, new_nbands, has_chgcar):
    if not os.path.exists(src_incar):
        return
    
    with open(src_incar, 'r') as f:
        lines = f.readlines()
        
    settings = {
        "LWAVE": ".TRUE.",
        "ISYM": "-1",
        "NSW": "0",
        "IBRION": "-1",
        "LORBIT": "11",
        "NEDOS": "2000",
        "ALGO": "Normal"
    }
    if new_nbands:
        settings["NBANDS"] = str(new_nbands)
    if has_chgcar:
        settings["ICHARG"] = "1"
        
    new_lines = []
    for line in lines:
        stripped = line.strip().upper()
        skip = False
        for key in settings.keys():
            if stripped.startswith(key + "=") or stripped.startswith(key + " "):
                skip = True
                break
        if not skip:
            new_lines.append(line)
            
    with open(dest_incar, 'w') as f:
        for line in new_lines:
            f.write(line)
        f.write("\n# --- LOBSTER SPECIFIC SETTINGS ---\n")
        for k, v in settings.items():
            f.write(f"{k} = {v}\n")

def generate_lobsterin(poscar_path, dest_lobsterin):
    atoms = read(poscar_path)
    
    # TM is the last atom
    tm_idx = len(atoms) - 1
    tm_symbol = atoms[tm_idx].symbol
    
    distances = atoms.get_distances(tm_idx, range(len(atoms)), mic=True)
    
    cl_neighbors = []
    cr_neighbors = []
    
    for i, (dist, atom) in enumerate(zip(distances, atoms)):
        if i == tm_idx:
            continue
        if atom.symbol == "Cl" and dist < 3.0:
            cl_neighbors.append(i + 1) # 1-indexed for LOBSTER
        elif atom.symbol == "Cr" and dist < 4.5:
            cr_neighbors.append(i + 1)
            
    with open(dest_lobsterin, 'w') as f:
        f.write("basisSet pbeVASPfit2015\n")
        f.write("COHPstartEnergy -15.0\n")
        f.write("COHPendEnergy 5.0\n")
        f.write("saveProjectionToFile\n\n")
        
        for cl_idx in cl_neighbors:
            f.write(f"cohpBetweenAtom {tm_idx + 1} and {cl_idx}\n")
        for cr_idx in cr_neighbors:
            f.write(f"cohpBetweenAtom {tm_idx + 1} and {cr_idx}\n")

def write_job_sh(dest_dir):
    job_sh = """#!/bin/bash
#SBATCH -J VASP_LOBSTER
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=24:00:00

# 1. Run VASP Static Calculation (MPI)
mpirun -np $SLURM_NTASKS vasp_std > vasp_run.log 2>&1

# 2. Verify VASP finished successfully
if grep -q "reached required accuracy" vasp_run.log || grep -q "writing wavefunctions" vasp_run.log; then
    echo "VASP completed. Starting LOBSTER..."
    
    # 3. Configure OpenMP for LOBSTER
    export OMP_NUM_THREADS=$SLURM_CPUS_ON_NODE
    
    # 4. Run LOBSTER
    lobster > lobster_run.log 2>&1
else
    echo "VASP failed. Skipping LOBSTER."
    exit 1
fi
"""
    with open(os.path.join(dest_dir, "job.sh"), 'w') as f:
        f.write(job_sh)

def main():
    for name, src_dir in systems.items():
        dest_dir = os.path.join(DEST_BASE, name)
        os.makedirs(dest_dir, exist_ok=True)
        print(f"Setting up {name} in {dest_dir}")
        
        # 1. Copy structure
        contcar = os.path.join(src_dir, "CONTCAR")
        poscar = os.path.join(src_dir, "POSCAR")
        dest_poscar = os.path.join(dest_dir, "POSCAR")
        if os.path.exists(contcar) and os.path.getsize(contcar) > 0:
            shutil.copy(contcar, dest_poscar)
        elif os.path.exists(poscar):
            shutil.copy(poscar, dest_poscar)
        else:
            print(f"Warning: No POSCAR/CONTCAR found for {name}")
            continue
            
        # 2. Copy POTCAR and KPOINTS
        for f in ["POTCAR", "KPOINTS"]:
            src_f = os.path.join(src_dir, f)
            if os.path.exists(src_f):
                shutil.copy(src_f, os.path.join(dest_dir, f))
                
        # 3. Check for CHGCAR
        # Also check relaxation directory if static-scf doesn't have it
        src_chgcar = os.path.join(src_dir, "CHGCAR")
        relax_chgcar = os.path.join(os.path.dirname(src_dir), "CHGCAR")
        has_chgcar = False
        if os.path.exists(src_chgcar):
            shutil.copy(src_chgcar, os.path.join(dest_dir, "CHGCAR"))
            has_chgcar = True
        elif os.path.exists(relax_chgcar):
            shutil.copy(relax_chgcar, os.path.join(dest_dir, "CHGCAR"))
            has_chgcar = True
            
        # 4. Extract NBANDS and modify INCAR
        outcar = os.path.join(src_dir, "OUTCAR")
        nbands = extract_nbands(outcar)
        if nbands:
            nbands *= 2
        
        src_incar = os.path.join(src_dir, "INCAR")
        dest_incar = os.path.join(dest_dir, "INCAR")
        modify_incar(src_incar, dest_incar, nbands, has_chgcar)
        
        # 5. Generate lobsterin
        dest_lobsterin = os.path.join(dest_dir, "lobsterin")
        generate_lobsterin(dest_poscar, dest_lobsterin)
        
        # 6. Generate job.sh
        write_job_sh(dest_dir)
        print(f"  -> Done setup for {name}")

if __name__ == "__main__":
    main()
