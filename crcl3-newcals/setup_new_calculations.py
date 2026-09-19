import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_H_DIR = os.path.join(BASE_DIR, "doped-H")

# Configuration types and their specific INCAR additions with detailed physical explanations
CONFIGS = {
    # --- DFT+U: Hubbard correction for Cr 3d correlation ---
    "DFT_U": [
        "LDAU      = .TRUE.      # Enables DFT+U (Hubbard U correction for localized d-electrons)",
        "LDAUTYPE  = 2           # Dudarev et al. formulation where only U_eff = (U - J) matters",
        "LDAUL     = 2 -1 -1 -1  # Orbital l quantum number: Cr=2 (d-orbitals), Cl=-1 (no U), TM=-1 (no U), H=-1 (no U)",
        "LDAUU     = 4.0 0 0 0   # On-site Coulomb parameter U (eV): Cr=4.0 eV to correct self-interaction error",
        "LDAUJ     = 0 0 0 0     # On-site exchange parameter J (eV): set to 0 in Dudarev approach",
        "LMAXMIX   = 4           # Mix PAW one-center charges up to l=4; mandatory for d-orbitals to prevent convergence errors"
    ],
    # --- DFT-D3: Grimme empirical dispersion correction ---
    "DFT_D3": [
        "IVDW = 11               # Grimme DFT-D3 method with zero damping (D3(0)) for van der Waals interactions"
    ],
    # --- Freq: Finite-difference vibrational analysis & ZPE ---
    "Freq": [
        "IBRION = 5              # Finite differences method to compute Hessian matrix (vibrational frequencies)",
        "POTIM = 0.015           # Displacement step size (in Angstroms) for numerical differentiation",
        "NFREE = 2               # Central differences (+/- POTIM displacements) along x, y, z directions",
        "NSW = 1                 # Triggers displacement loop; VASP overrides this to the 6 displacements for H",
        "EDIFF = 1.0e-07         # High electronic SCF precision (eV) to minimize numerical noise in force differences"
    ]
}

SYSTEMS = [
    "adsorbed/Co", "adsorbed/Fe", "adsorbed/NI",
    "embeded/Co", "embeded/Fe", "embeded/NI"
]

# Mapping for clean substrate references without H (needed to evaluate Delta E_ads = E_slab+H - E_slab - 1/2 E_H2)
# Format: (site_type, TM_label): (source_reference_dir, TM_initial_magnetic_moment_muB)
CLEAN_SOURCES = {
    # --- Surface Adsorbed site (3-fold hollow coordination above monolayer) ---
    ("adsorbed", "Co"): ("adsorbed/co", "3.0"),  # Co dopant: source clean slab, 3.0 muB initial moment (d7 high-spin)
    ("adsorbed", "Fe"): ("adsorbed/fe", "4.0"),  # Fe dopant: source clean slab, 4.0 muB initial moment (d6 high-spin, 4 unpaired electrons)
    ("adsorbed", "NI"): ("adsorbed/ni", "2.0"),  # Ni dopant: source clean slab, 2.0 muB initial moment (d8 high-spin, 2 unpaired electrons)
    # --- In-plane Embedded site (6-fold hollow coordination substituting Cr vacancy) ---
    ("embeded", "Co"): ("embedded/co", "3.0"),   # Embedded Co: source clean slab, 3.0 muB initial moment
    ("embeded", "Fe"): ("embedded/fe", "4.0"),   # Embedded Fe: source clean slab, 4.0 muB initial moment
    ("embeded", "NI"): ("embedded/ni", "2.0"),   # Embedded Ni: source clean slab, 2.0 muB initial moment
}

def apply_selective_dynamics(poscar_path, dest_poscar):
    with open(poscar_path, "r") as f:
        lines = f.readlines()
    
    with open(dest_poscar, "w") as f:
        if "Selective" in lines[7]:
            for line in lines:
                f.write(line)
            return
        
        for i in range(7):
            f.write(lines[i])
            
        f.write("Selective dynamics\n")
        f.write(lines[7])
        
        coord_start = 8
        for i in range(coord_start, coord_start + 33):
            coords = lines[i].split()
            f.write(f" {coords[0]:>18} {coords[1]:>18} {coords[2]:>18}   F   F   F\n")
        
        coords = lines[coord_start + 33].split()
        f.write(f" {coords[0]:>18} {coords[1]:>18} {coords[2]:>18}   T   T   T\n")
        
        for i in range(coord_start + 34, len(lines)):
            f.write(lines[i])

def generate_clean_incar(config, tm_mom):
    common = f"""# --- INCAR (relax clean substrate) ---
ENCUT   = 400     # eV; teste de convergencia recomendado
EDIFF   = 1.0e-06 # criterio eletronico
EDIFFG  = -0.025  # criterio forca ionica
PREC    = Normal
ISPIN   = 2       # spin polarizado
MAGMOM  = 8*3.0 24*0.0 1*{tm_mom}   # sementes muB
ISYM    = 0       # desativa simetria (dopante)
LDIPOL  = .TRUE.
IDIPOL  = 3       # correcao z
LWAVE   = .FALSE.
LCHARG  = .FALSE.
NCORE   = 8
# --- relax ---
IBRION  = 2       # CG
NSW     = 500     # passos max
ISIF    = 2       # relaxa ions, celula fixa 2D
ISMEAR  = 0; SIGMA = 0.05
ISTART  = 0  ICHARG = 2 # superposicao atomica
"""
    if config == "DFT_D3":
        return common + """# --- DFT_D3 ADDITIONS ---
IVDW = 11               # Grimme DFT-D3 method with zero damping (D3(0)) for van der Waals interactions
"""
    elif config == "DFT_U":
        return common + """# --- DFT_U ADDITIONS ---
LDAU      = .TRUE.      # Enables DFT+U (Hubbard U correction for localized d-electrons)
LDAUTYPE  = 2           # Dudarev et al. formulation where only U_eff = (U - J) matters
LDAUL     = 2 -1 -1     # Orbital l quantum number: Cr=2 (d-orbitals), Cl=-1 (no U), TM=-1 (no U)
LDAUU     = 4.0 0 0     # On-site Coulomb parameter U (eV): Cr=4.0 eV to correct self-interaction error
LDAUJ     = 0 0 0       # On-site exchange parameter J (eV): set to 0 in Dudarev approach
LMAXMIX   = 4           # Mix PAW one-center charges up to l=4; mandatory for d-orbitals to prevent convergence errors
"""
    return common

def setup_directories():
    for config_name, incar_adds in CONFIGS.items():
        config_dir = os.path.join(BASE_DIR, config_name)
        os.makedirs(config_dir, exist_ok=True)
        
        for sys_path in SYSTEMS:
            src = os.path.join(SRC_H_DIR, sys_path)
            dest = os.path.join(config_dir, sys_path)
            
            if not os.path.exists(src):
                print(f"Warning: Source {src} not found. Skipping.")
                continue
                
            os.makedirs(dest, exist_ok=True)
            
            for f in ["POTCAR", "KPOINTS", "job.sh"]:
                src_f = os.path.join(src, f)
                if os.path.exists(src_f):
                    shutil.copy(src_f, dest)
            
            src_incar = os.path.join(src, "INCAR")
            dest_incar = os.path.join(dest, "INCAR")
            if os.path.exists(src_incar):
                with open(src_incar, "r") as f:
                    incar_content = f.read()
                
                if config_name == "Freq":
                    lines = incar_content.split("\n")
                    new_lines = []
                    for line in lines:
                        if not (line.strip().startswith("IBRION") or line.strip().startswith("NSW") or line.strip().startswith("EDIFF")):
                            new_lines.append(line)
                    new_lines.append("EDIFF   = 1.0e-07    # criterio eletronico alto para frequencias")
                    incar_content = "\n".join(new_lines)

                with open(dest_incar, "w") as f:
                    f.write(incar_content)
                    f.write(f"\n# --- {config_name} ADDITIONS ---\n")
                    f.write("\n".join(incar_adds) + "\n")
            
            src_contcar = os.path.join(src, "CONTCAR")
            src_poscar = os.path.join(src, "POSCAR")
            src_geom = src_contcar if (os.path.exists(src_contcar) and os.path.getsize(src_contcar) > 0) else src_poscar
            dest_poscar = os.path.join(dest, "POSCAR")
            
            if os.path.exists(src_geom):
                if config_name == "Freq":
                    apply_selective_dynamics(src_geom, dest_poscar)
                else:
                    shutil.copy(src_geom, dest_poscar)
                    
            print(f"Setup {config_name}/{sys_path}")

    kpoints_content = "Automatic mesh\n0\nGamma\n5 5 1\n0 0 0\n"
    job_sh_content = "#!/bin/bash\n#SBATCH --job-name=vasp_job\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=16\n#SBATCH --time=24:00:00\n\nmpirun -np 16 vasp_std > run.log\n"

    for config in ["DFT_D3", "DFT_U"]:
        for (group, tm_folder), (src_rel, tm_mom) in CLEAN_SOURCES.items():
            dest_dir = os.path.join(BASE_DIR, config, "clean", group, tm_folder)
            os.makedirs(dest_dir, exist_ok=True)
            
            src_path = os.path.join(BASE_DIR, src_rel)
            src_contcar = os.path.join(src_path, "CONTCAR")
            src_poscar = os.path.join(src_path, "POSCAR")
            dest_poscar = os.path.join(dest_dir, "POSCAR")
            
            if os.path.exists(src_contcar) and os.path.getsize(src_contcar) > 0:
                shutil.copy(src_contcar, dest_poscar)
            else:
                shutil.copy(src_poscar, dest_poscar)
                
            shutil.copy(os.path.join(src_path, "POTCAR"), os.path.join(dest_dir, "POTCAR"))
            
            with open(os.path.join(dest_dir, "KPOINTS"), "w") as f:
                f.write(kpoints_content)
                
            with open(os.path.join(dest_dir, "job.sh"), "w") as f:
                f.write(job_sh_content)
                
            with open(os.path.join(dest_dir, "INCAR"), "w") as f:
                f.write(generate_clean_incar(config, tm_mom))
                
            print(f"Setup {config}/clean/{group}/{tm_folder}")

if __name__ == "__main__":
    setup_directories()
