#!/usr/bin/env python3
"""
================================================================================
 SETUP TRANSITION METAL (Co, Fe, Ni) ADSORPTION ON CrCl3 2x2 SUPERCELL (No U)
================================================================================
 Generates complete VASP input files and directory structures for:
   1. crcl3-2x2-co_ads-without-U  (Cobalt)
   2. crcl3-2x2-fe_ads-without-U  (Iron)
   3. crcl3-2x2-ni_ads-without-U  (Nickel)

 Each directory contains:
   - no_vdw/
       clean/  -- Pristine CrCl3 2x2 monolayer substrate (8 Cr + 24 Cl)
       S1/     -- TM atop Atom 19 (Cl11) at (0.50000, 0.32035) with d(TM-Cl)=2.25 A
       S2/     -- TM at hollow site (0.50000, 0.50000) with dz=1.90 A above Cr plane
       S3/     -- TM atop Atom 3 (Cr3) at (0.66667, 0.33333) with d(TM-Cr)=2.50 A
   - yes_vdw/
       clean/  -- Pristine CrCl3 2x2 substrate with IVDW = 12 (DFT-D3)
       S1/     -- TM atop Cl11 with IVDW = 12
       S2/     -- TM at hollow site with IVDW = 12
       S3/     -- TM atop Cr3 with IVDW = 12
   - setup_<tm>_ads.py
   - verify_supercell.py
   - calculate_<tm>_adsorption_physics.py
   - pack_calculations.py
   - crcl3_2x2_<tm>_ads_without_U.tar.gz
   - crcl3_2x2_<tm>_ads_without_U.zip
================================================================================
"""

import os
import sys
import math
import subprocess
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
H_ADS_DIR = os.path.join(SCRIPT_DIR, "crcl3-2x2-h_ads-without-U")

CONTCAR_1X1 = os.path.join(SCRIPT_DIR, "crcl3-1x1", "quick_test_k551", "CONTCAR")
POTCAR_DIR = "/Users/apple/Research/abc/potentials/potpaw_PBE.64"
POTCAR_CR = os.path.join(POTCAR_DIR, "Cr", "POTCAR")
POTCAR_CL = os.path.join(POTCAR_DIR, "Cl", "POTCAR")

CLUSTER_BASE = "/home/cr/mnt/google-drive/Proyectos/paper-adaptation/crcl3-newcals"
SCRATCH_BASE = "/home/cr/scratch_vasp"

C_VACUUM = 20.0000

# TM site distances (Angstrom)
TM_DIST_S1 = 2.25  # TM above Atom 19 (Cl11)
TM_DIST_S2 = 1.90  # TM above slab center z=0.5
TM_DIST_S3 = 2.50  # TM above Atom 3 (Cr3)

TM_METALS = {
    "co": {
        "symbol": "Co",
        "name": "Cobalt",
        "moment": 3.0,
        "d_config": "d7 high-spin (3 unpaired electrons)",
        "potcar": os.path.join(POTCAR_DIR, "Co", "POTCAR"),
        "dir_name": "crcl3-2x2-co_ads-without-U",
    },
    "fe": {
        "symbol": "Fe",
        "name": "Iron",
        "moment": 4.0,
        "d_config": "d6 high-spin (4 unpaired electrons)",
        "potcar": os.path.join(POTCAR_DIR, "Fe", "POTCAR"),
        "dir_name": "crcl3-2x2-fe_ads-without-U",
    },
    "ni": {
        "symbol": "Ni",
        "name": "Nickel",
        "moment": 2.0,
        "d_config": "d8 high-spin (2 unpaired electrons)",
        "potcar": os.path.join(POTCAR_DIR, "Ni", "POTCAR"),
        "dir_name": "crcl3-2x2-ni_ads-without-U",
    }
}


def parse_contcar(filepath):
    with open(filepath, "r") as f:
        lines = [l.rstrip() for l in f.readlines()]
    scale = float(lines[1].split()[0])
    v1 = np.array([float(x) for x in lines[2].split()[:3]]) * scale
    v2 = np.array([float(x) for x in lines[3].split()[:3]]) * scale
    v3 = np.array([float(x) for x in lines[4].split()[:3]]) * scale
    lattice = np.array([v1, v2, v3])
    species_names = lines[5].split()
    species_counts = [int(x) for x in lines[6].split()]
    idx = 7
    if lines[idx].strip()[0].upper() in ("S",):
        idx += 1
    idx += 1
    coords = []
    for i in range(sum(species_counts)):
        parts = lines[idx + i].split()
        coords.append([float(parts[0]), float(parts[1]), float(parts[2])])
    return scale, lattice, species_names, species_counts, np.array(coords)


def build_2x2_supercell(contcar_path):
    scale, lattice, species, counts, coords = parse_contcar(contcar_path)
    a_1x1 = np.linalg.norm(lattice[0])
    orig_c = np.linalg.norm(lattice[2])
    n_cr, n_cl = counts[0], counts[1]
    cr_coords_1x1 = coords[:n_cr]
    cl_coords_1x1 = coords[n_cr:n_cr + n_cl]
    a_2x2 = 2.0 * a_1x1
    lat_2x2 = np.array([
        [a_2x2, 0.0, 0.0],
        [-0.5 * a_2x2, 0.5 * math.sqrt(3.0) * a_2x2, 0.0],
        [0.0, 0.0, C_VACUUM]
    ])

    def convert_z(z_frac_orig):
        delta_z_cart = (z_frac_orig - 0.5) * orig_c
        return 0.5 + (delta_z_cart / C_VACUUM)

    shifts = [(0.0, 0.0), (0.5, 0.0), (0.0, 0.5), (0.5, 0.5)]
    cr_2x2 = []
    for s in shifts:
        for c in cr_coords_1x1:
            pos = [c[0] / 2.0 + s[0], c[1] / 2.0 + s[1], convert_z(c[2])]
            pos[0] %= 1.0
            pos[1] %= 1.0
            cr_2x2.append(pos)
    cl_2x2 = []
    for s in shifts:
        for c in cl_coords_1x1:
            pos = [c[0] / 2.0 + s[0], c[1] / 2.0 + s[1], convert_z(c[2])]
            pos[0] %= 1.0
            pos[1] %= 1.0
            cl_2x2.append(pos)

    return lat_2x2, a_2x2, cr_2x2, cl_2x2, a_1x1, orig_c


def write_poscar(filepath, comment, lattice, species, counts, all_coords):
    with open(filepath, "w") as f:
        f.write("{}\n".format(comment))
        f.write("1.0\n")
        for v in lattice:
            f.write("  {:20.16f}  {:20.16f}  {:20.16f}\n".format(v[0], v[1], v[2]))
        f.write("  " + "  ".join(species) + "\n")
        f.write("  " + "  ".join(str(c) for c in counts) + "\n")
        f.write("Direct\n")
        for coord in all_coords:
            f.write("  {:20.16f}  {:20.16f}  {:20.16f}\n".format(coord[0], coord[1], coord[2]))


def generate_incar(vdw, site_name, a_2x2, has_tm, tm_symbol, tm_moment, tm_desc):
    vdw_label = "D3" if vdw else "No vdW"
    system_tag = "CrCl3 2x2 + {} ({})".format(tm_symbol, site_name) if has_tm else "CrCl3 2x2 Clean Substrate"
    magmom = "8*3.0 24*0.0 1*{:.1f}".format(tm_moment) if has_tm else "8*3.0 24*0.0"
    magmom_comment = ("# Initial magnetic moments (muB): 3.0 for Cr3+ (d3, S=3/2), "
                      "0.0 for Cl- (closed shell)" +
                      (", {:.1f} for {} ({})".format(tm_moment, tm_symbol, tm_desc) if has_tm else ""))
    tm_count_str = ", 1 {}".format(tm_symbol) if has_tm else ""
    d3_method = " + Grimme DFT-D3 (IVDW=12)" if vdw else " (Pure GGA, no dispersion)"
    d3_baseline = "DFT-D3" if vdw else "GGA-PBE"

    incar = """# =========================================================================
# SYSTEM: {system_tag} ({vdw_label}, U=0eV)
# Cell: CrCl3 2x2 Monolayer Supercell (8 Cr, 24 Cl{tm_count_str})
# Vacuum: c = {c_vac:.4f} Angstroms (Fixed vacuum layer, slab centered at z = 0.5)
# Method: PBE{d3_method}, U = 0 eV
# Equilibrium In-Plane Cell Parameter: a_2x2 = {a_2x2:.4f} Angstroms (from ISIF=3 1x1 zero-stress)
# =========================================================================

# --- 1. Electronic Minimization & Plane-Wave Basis ---
SYSTEM   = {system_tag} ({vdw_label}, U=0eV) # Informative calculation title printed in OUTCAR
PREC     = Accurate    # High-precision FFT and integration grid; eliminates grid-aliasing forces in 2D sheets
ENCUT    = 400.0       # Kinetic energy cutoff (eV); ~1.33x max ENMAX (Cl ~300 eV), consistent with 1x1 references
ALGO     = Normal      # Blocked-Davidson electronic minimization; numerically stable for magnetic Cr3+ d3 ions
EDIFF    = 1.0E-06     # Energy convergence threshold for electronic SCF loop (eV); ensures well-converged wavefunctions
NELM     = 100         # Maximum number of electronic SCF cycles per ionic step; provides headroom while halting stalled loops

# --- 2. Spin Polarization & Magnetic Moments ---
ISPIN    = 2           # Spin-polarized calculation; mandatory for open-shell magnetic Cr3+ (3d3) ions
MAGMOM   = {magmom} {magmom_comment}

# --- 3. Brillouin-Zone Integration & Smearing ---
ISMEAR   = 0           # Gaussian smearing; required for 2D semiconductor slab to guarantee variational ionic forces
SIGMA    = 0.05        # Smearing width (eV); 50 meV minimizes artificial electronic entropy (-TS ~ 0) in semiconductors

# --- 4. Parallelization & Computational Performance ---
NCORE    = 4           # Number of CPU cores per orbital group; optimizes FFT communication on 16-core nodes (4 cores/CCX)
LREAL    = Auto        # Projection operators evaluated in real space; optimal performance for 32/33-atom supercells
""".format(
        system_tag=system_tag, vdw_label=vdw_label, tm_count_str=tm_count_str,
        c_vac=C_VACUUM, d3_method=d3_method, a_2x2=a_2x2,
        magmom=magmom, magmom_comment=magmom_comment
    )

    if vdw:
        incar += """
# --- 5. van der Waals Dispersion Correction ---
IVDW     = 12          # Grimme DFT-D3 (IVDW=12 per user specification)
"""
    else:
        incar += """
# --- 5. van der Waals Dispersion Correction ---
# (DISABLED) No IVDW tag: Pure GGA-PBE without dispersion correction
"""

    incar += """
# --- 6. Ionic Relaxation & Convergence Criteria ---
IBRION   = 2           # Conjugate-gradient algorithm; most robust scheme for atomic coordinate relaxation
NSW      = 100         # Maximum number of ionic optimization steps; provides headroom for adatom relaxation
ISIF     = 2           # Relax atomic positions only; cell vectors and vacuum thickness (c={c_vac:.1f} A) strictly fixed
EDIFFG   = -0.025      # Force convergence criterion (eV/Angstrom); optimization stops when all forces < 0.025 eV/A (paper standard)

# --- 7. PAW Density Mixing & Aspherical Gradients ---
LASPH    = .TRUE.      # Non-spherical gradient corrections inside PAW augmentation spheres; essential for directional 3d orbitals
LMAXMIX  = 4           # Mix charge density up to l=4; strictly required for d-orbital PAW occupancy matrix convergence

# --- 8. Hubbard U Correction ---
LDAU     = .FALSE.     # Hubbard U disabled (U = 0 eV); pure {d3_baseline} baseline without on-site Coulomb correction

# --- 9. Surface Dipole Correction (2D Slab Standard) ---
LDIPOL   = .TRUE.      # Activate dipole correction; cancels spurious electrostatic field across the vacuum region
IDIPOL   = 3           # Correct dipole moment along the out-of-plane z direction (normal to 2D slab)
DIPOL    = 0.5 0.5 0.5 # Slab center of mass in fractional coordinates (slab centered at z = 0.5)

# --- 10. Wavefunction & Charge Output Management ---
LWAVE    = .FALSE.     # Do NOT write WAVECAR; eliminates disk I/O bottleneck and prevents storage bloat during relaxation
LCHARG   = .FALSE.     # Do NOT write CHGCAR; optimizes I/O bandwidth during ionic relaxation
""".format(c_vac=C_VACUUM, d3_baseline=d3_baseline)

    return incar


def generate_kpoints():
    return """K-Points 5x5x1 Gamma-centered (CrCl3 2x2 Supercell)
0
Gamma
 5  5  1
 0  0  0
"""


def build_potcar(dest_path, tm_potcar_path=None):
    with open(POTCAR_CR, "r", encoding="utf-8", errors="ignore") as f:
        cr_content = f.read()
    with open(POTCAR_CL, "r", encoding="utf-8", errors="ignore") as f:
        cl_content = f.read()
    full = cr_content + cl_content
    if tm_potcar_path:
        with open(tm_potcar_path, "r", encoding="utf-8", errors="ignore") as f:
            full += f.read()
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full)


def generate_job_script(job_name, scratch_subdir, target_dir_name):
    cluster_project = "{}/{}/{}".format(CLUSTER_BASE, target_dir_name, scratch_subdir)
    scratch_dir = "{}/{}/{}".format(SCRATCH_BASE, target_dir_name, scratch_subdir)
    return """#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --exclusive
#SBATCH --time=24:00:00

PROJECT_DIR="{cluster_project}"
SCRATCH_DIR="{scratch_dir}"

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
""".format(job_name=job_name, cluster_project=cluster_project, scratch_dir=scratch_dir)


def adapt_file(src_path, dest_path, replacements):
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)
    if dest_path.endswith(".py") or dest_path.endswith(".sh"):
        os.chmod(dest_path, 0o755)


def build_all():
    print("=" * 85)
    print("  CREATING 3 DIRECTORIES: Co, Fe, Ni ADSORPTION ON CrCl3 2x2")
    print("  No Hubbard U (LDAU=.FALSE.) | yes_vdw uses IVDW = 12 (DFT-D3)")
    print("=" * 85)

    if not os.path.exists(CONTCAR_1X1):
        print("ERROR: CONTCAR 1x1 not found: {}".format(CONTCAR_1X1))
        sys.exit(1)

    lat_2x2, a_2x2, cr_2x2, cl_2x2, a_1x1, orig_c = build_2x2_supercell(CONTCAR_1X1)
    kpoints_content = generate_kpoints()

    cl11 = cl_2x2[10]
    cr3 = cr_2x2[2]
    s2_frac = [0.50000, 0.50000, 0.50000]

    for tm_key, tm_info in TM_METALS.items():
        tm_symbol = tm_info["symbol"]
        tm_name = tm_info["name"]
        tm_moment = tm_info["moment"]
        tm_desc = tm_info["d_config"]
        dir_name = tm_info["dir_name"]
        tm_potcar = tm_info["potcar"]

        target_base = os.path.join(SCRIPT_DIR, dir_name)
        os.makedirs(target_base, exist_ok=True)
        print("\n>>> Setting up {} ({}) in {}".format(tm_symbol, tm_name, dir_name))

        tm_positions = {
            "S1": {
                "label": "S1 top-Cl",
                "desc": "{} above Atom 19 (Cl11) at (0.50000, 0.32035, 0.56679)".format(tm_symbol),
                "coords": [cl11[0], cl11[1], cl11[2] + TM_DIST_S1 / C_VACUUM],
            },
            "S2": {
                "label": "S2 hollow",
                "desc": "{} at center of Cr honeycomb ring at (0.50000, 0.50000)".format(tm_symbol),
                "coords": [s2_frac[0], s2_frac[1], s2_frac[2] + TM_DIST_S2 / C_VACUUM],
            },
            "S3": {
                "label": "S3 top-Cr",
                "desc": "{} directly above Atom 3 (Cr3) at (0.66667, 0.33333, 0.50000)".format(tm_symbol),
                "coords": [cr3[0], cr3[1], cr3[2] + TM_DIST_S3 / C_VACUUM],
            },
        }

        vdw_variants = [
            ("no_vdw", False, "Pure PBE (no dispersion)"),
            ("yes_vdw", True, "PBE + DFT-D3 (IVDW=12)"),
        ]

        for vdw_name, vdw_flag, vdw_desc in vdw_variants:
            vdw_dir = os.path.join(target_base, vdw_name)

            # 1. Clean substrate
            clean_dir = os.path.join(vdw_dir, "clean")
            os.makedirs(clean_dir, exist_ok=True)
            write_poscar(
                os.path.join(clean_dir, "POSCAR"),
                "CrCl3 2x2 Clean Substrate ({}, U=0) (a_2x2={:.4f}A, c={:.4f}A)".format(
                    "D3" if vdw_flag else "no_vdw", a_2x2, C_VACUUM),
                lat_2x2, ["Cr", "Cl"], [8, 24],
                cr_2x2 + cl_2x2
            )
            with open(os.path.join(clean_dir, "INCAR"), "w") as f:
                f.write(generate_incar(vdw_flag, "clean", a_2x2, has_tm=False,
                                       tm_symbol=tm_symbol, tm_moment=tm_moment, tm_desc=tm_desc))
            with open(os.path.join(clean_dir, "KPOINTS"), "w") as f:
                f.write(kpoints_content)
            build_potcar(os.path.join(clean_dir, "POTCAR"), tm_potcar_path=None)
            job_name = "{}_cln_{}".format(tm_symbol, vdw_name)
            with open(os.path.join(clean_dir, "job.sh"), "w") as f:
                f.write(generate_job_script(job_name, "{}/clean".format(vdw_name), dir_name))
            os.chmod(os.path.join(clean_dir, "job.sh"), 0o755)

            # 2. S1, S2, S3 sites
            for site_key, site_info in tm_positions.items():
                site_dir = os.path.join(vdw_dir, site_key)
                os.makedirs(site_dir, exist_ok=True)
                all_coords = cr_2x2 + cl_2x2 + [site_info["coords"]]
                write_poscar(
                    os.path.join(site_dir, "POSCAR"),
                    "CrCl3 2x2 + {} {} ({}, U=0) (a_2x2={:.4f}A, c={:.4f}A)".format(
                        tm_symbol, site_info["label"], "D3" if vdw_flag else "no_vdw", a_2x2, C_VACUUM),
                    lat_2x2, ["Cr", "Cl", tm_symbol], [8, 24, 1],
                    all_coords
                )
                with open(os.path.join(site_dir, "INCAR"), "w") as f:
                    f.write(generate_incar(vdw_flag, site_info["label"], a_2x2, has_tm=True,
                                           tm_symbol=tm_symbol, tm_moment=tm_moment, tm_desc=tm_desc))
                with open(os.path.join(site_dir, "KPOINTS"), "w") as f:
                    f.write(kpoints_content)
                build_potcar(os.path.join(site_dir, "POTCAR"), tm_potcar_path=tm_potcar)
                job_name = "{}_{}_{}".format(tm_symbol, site_key, vdw_name)
                with open(os.path.join(site_dir, "job.sh"), "w") as f:
                    f.write(generate_job_script(job_name, "{}/{}".format(vdw_name, site_key), dir_name))
                os.chmod(os.path.join(site_dir, "job.sh"), 0o755)

        # Adapt helper scripts from crcl3-2x2-h_ads-without-U
        # A. setup_<tm>_ads.py
        setup_replacements = [
            ("H ADSORPTION", f"{tm_name.upper()} ADSORPTION"),
            ("H Adsorption", f"{tm_name} Adsorption"),
            ("hydrogen adsorption", f"{tm_name.lower()} adsorption"),
            ("Hydrogen", tm_name),
            ("POTCAR_H = os.path.join(os.path.expanduser(\"~\"), \"temporary\", \"dotfiles\",\n                        \"potentials\", \"potpaw_PBE.64\", \"H\", \"POTCAR\")",
             f"POTCAR_H = \"{tm_potcar}\""),
            ("POTCAR_CR_CL = os.path.join(SCRIPT_DIR, \"..\", \"crcl3-1x1\", \"quick_test_k551\", \"POTCAR\")",
             f"POTCAR_CR = \"{POTCAR_CR}\"\nPOTCAR_CL = \"{POTCAR_CL}\""),
            ("SCRATCH_ROOT = \"/home/cr/scratch_vasp/crcl3-2x2-h_ads-without-U\"",
             f"SCRATCH_ROOT = \"/home/cr/scratch_vasp/{dir_name}\""),
            ("H_DIST_S1 = 1.30", f"H_DIST_S1 = {TM_DIST_S1:.2f}"),
            ("H_DIST_S2 = 1.60", f"H_DIST_S2 = {TM_DIST_S2:.2f}"),
            ("H_DIST_S3 = 1.55", f"H_DIST_S3 = {TM_DIST_S3:.2f}"),
            ("IVDW     = 11", "IVDW     = 12"),
            ("IVDW=11", "IVDW=12"),
            ("1*0.0", f"1*{tm_moment:.1f}"),
            ("0.0 for H", f"{tm_moment:.1f} for {tm_symbol} ({tm_desc})"),
            ("['Cr', 'Cl', 'H']", f"['Cr', 'Cl', '{tm_symbol}']"),
            ("[\"Cr\", \"Cl\", \"H\"]", f"[\"Cr\", \"Cl\", \"{tm_symbol}\"]"),
            ("CrCl3 2x2 + H", f"CrCl3 2x2 + {tm_symbol}"),
            ("CrCl3 2x2 Monolayer Supercell (8 Cr, 24 Cl, 1 H)",
             f"CrCl3 2x2 Monolayer Supercell (8 Cr, 24 Cl, 1 {tm_symbol})"),
            ("H_{}_{}", f"{tm_symbol}_{{site_key}}_{{vdw_name}}"),
            ("H_cln_{}", f"{tm_symbol}_cln_{{vdw_name}}"),
            ("include_h", "include_tm"),
            ("has_h", "has_tm"),
        ]
        adapt_file(os.path.join(H_ADS_DIR, "setup_h_ads.py"),
                   os.path.join(target_base, f"setup_{tm_key}_ads.py"),
                   setup_replacements)

        # B. verify_supercell.py
        verify_replacements = [
            ("H Adsorption", f"{tm_symbol} Adsorption"),
            ("has_h", "has_tm"),
            ("include_h", "include_tm"),
            ("['Cr', 'Cl', 'H']", f"['Cr', 'Cl', '{tm_symbol}']"),
            ("[\"Cr\", \"Cl\", \"H\"]", f"[\"Cr\", \"Cl\", \"{tm_symbol}\"]"),
            ("h_coord", "tm_coord"),
            ("h_z_cart", "tm_z_cart"),
            ("d_h_cl11", "d_tm_cl11"),
            ("d_h_cr3", "d_tm_cr3"),
            ("1.30", f"{TM_DIST_S1:.2f}"),
            ("1.60", f"{TM_DIST_S2:.2f}"),
            ("1.55", f"{TM_DIST_S3:.2f}"),
            ("H is above", f"{tm_symbol} is above"),
            ("H is below", f"{tm_symbol} is below"),
            ("H is positioned", f"{tm_symbol} is positioned"),
            ("H height", f"{tm_symbol} height"),
            ("H-Cl11 distance", f"{tm_symbol}-Cl11 distance"),
            ("H-Cr3 distance", f"{tm_symbol}-Cr3 distance"),
            ("H position", f"{tm_symbol} position"),
            ("H z-distance", f"{tm_symbol} z-distance"),
            ("H z-position", f"{tm_symbol} z-position"),
            ("IVDW\\s*=\\s*(\\d+)\", content)\n    if vdw_expected:\n        if ivdw_match:\n            check(ivdw_match.group(1) == \"11\",\n                  \"IVDW = 11 (DFT-D3 enabled as expected)\",\n                  \"IVDW = {} (expected 11)\".format(ivdw_match.group(1)))",
             "IVDW\\s*=\\s*(\\d+)\", content)\n    if vdw_expected:\n        if ivdw_match:\n            check(ivdw_match.group(1) == \"12\",\n                  \"IVDW = 12 (DFT-D3 enabled as expected per user specification)\",\n                  \"IVDW = {} (expected 12)\".format(ivdw_match.group(1)))"),
            ("existing_poscar = EXISTING_H_S3", "# cross validation disabled for new TM adatom\n    existing_poscar = None"),
            ("cross_validate_existing(new_s3, EXISTING_H_S3)", "pass  # Cross-validation not applicable for TM adatom"),
        ]
        adapt_file(os.path.join(H_ADS_DIR, "verify_supercell.py"),
                   os.path.join(target_base, "verify_supercell.py"),
                   verify_replacements)

        # C. pack_calculations.py
        pack_replacements = [
            ("crcl3_2x2_h_ads_without_U.tar.gz", f"crcl3_2x2_{tm_key}_ads_without_U.tar.gz"),
            ("crcl3_2x2_h_ads_without_U.zip", f"crcl3_2x2_{tm_key}_ads_without_U.zip"),
            ("setup_h_ads.py", f"setup_{tm_key}_ads.py"),
            ("calculate_h_adsorption_physics.py", f"calculate_{tm_key}_adsorption_physics.py"),
            ("H ADSORPTION", f"{tm_symbol.upper()} ADSORPTION"),
            ("H adsorption", f"{tm_symbol} adsorption"),
        ]
        adapt_file(os.path.join(H_ADS_DIR, "pack_calculations.py"),
                   os.path.join(target_base, "pack_calculations.py"),
                   pack_replacements)

        # D. calculate_<tm>_adsorption_physics.py
        physics_replacements = [
            ("HYDROGEN ADSORPTION", f"{tm_name.upper()} ADSORPTION"),
            ("Hydrogen", tm_name),
            ("DZ_S1 = 1.3000", f"DZ_S1 = {TM_DIST_S1:.4f}"),
            ("DZ_S2 = 1.6000", f"DZ_S2 = {TM_DIST_S2:.4f}"),
            ("DZ_S3 = 1.5500", f"DZ_S3 = {TM_DIST_S3:.4f}"),
            ("1.30 A", f"{TM_DIST_S1:.2f} A"),
            ("1.60 A", f"{TM_DIST_S2:.2f} A"),
            ("1.55 A", f"{TM_DIST_S3:.2f} A"),
            ("Optimal Initial H:", f"Optimal Initial {tm_symbol}:"),
            ("r_cov(H)", f"r_cov({tm_symbol})"),
            ("H atom", f"{tm_symbol} atom"),
            ("H-Cl", f"{tm_symbol}-Cl"),
            ("H-Cr", f"{tm_symbol}-Cr"),
            ("setup_h_ads.py", f"setup_{tm_key}_ads.py"),
        ]
        adapt_file(os.path.join(H_ADS_DIR, "calculate_h_adsorption_physics.py"),
                   os.path.join(target_base, f"calculate_{tm_key}_adsorption_physics.py"),
                   physics_replacements)

        print("  -> Helper scripts staged: setup, verify, physics, pack.")


def verify_and_pack_all():
    print("\n" + "=" * 85)
    print("  RUNNING VERIFICATION AND PACKING ACROSS ALL 3 SUITES")
    print("=" * 85)

    py_exe = sys.executable
    for tm_key, tm_info in TM_METALS.items():
        dir_name = tm_info["dir_name"]
        suite_dir = os.path.join(SCRIPT_DIR, dir_name)
        print(f"\n>>> Verifying {dir_name}...")
        res_v = subprocess.run([py_exe, "verify_supercell.py"], cwd=suite_dir, capture_output=True, text=True)
        if res_v.returncode != 0:
            print(f"FAILED verification in {dir_name}!")
            print(res_v.stdout)
            print(res_v.stderr)
            sys.exit(1)
        # Extract summary
        lines = res_v.stdout.strip().split("\n")
        summary_lines = [l for l in lines if "PASS:" in l or "STATUS:" in l]
        for l in summary_lines:
            print("   ", l)

        print(f">>> Packing {dir_name}...")
        res_p = subprocess.run([py_exe, "pack_calculations.py"], cwd=suite_dir, capture_output=True, text=True)
        if res_p.returncode != 0:
            print(f"FAILED packing in {dir_name}!")
            print(res_p.stdout)
            print(res_p.stderr)
            sys.exit(1)
        for l in res_p.stdout.strip().split("\n"):
            print("   ", l)

    print("\n" + "=" * 85)
    print("  ALL 3 DIRECTORIES VERIFIED AND PACKED SUCCESSFULLY!")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    build_all()
    verify_and_pack_all()
