#!/usr/bin/env python3
"""
SETUP Co ADSORPTION ON PRISTINE CrCl3 2x2 SUPERCELL (No Hubbard U)
"""
import os
import sys
import math
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = SCRIPT_DIR
PARENT_DIR = "/home/cr/Downloads/crcl3-newcals"

CONTCAR_1X1 = os.path.join(PARENT_DIR, "crcl3-1x1", "quick_test_k551", "CONTCAR")
POTCAR_CR_CL = os.path.join(PARENT_DIR, "crcl3-1x1", "quick_test_k551", "POTCAR")
POTCAR_TM = os.path.join(os.path.expanduser("~"), "temporary", "dotfiles",
                         "potentials", "potpaw_PBE.64", "Co", "POTCAR")

SCRATCH_ROOT = "/home/cr/scratch_vasp/crcl3-2x2-co_ads-without-U"
C_VACUUM = 20.0000

TM_SYMBOL = "Co"
TM_MAGMOM = 3.0
TM_MOM_DESC = "3.0 for Co (d7 high-spin)"
DIST_S1 = 2.25
DIST_S2 = 1.9
DIST_S3 = 2.45

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
    total_atoms = sum(species_counts)
    coords = []
    for i in range(total_atoms):
        parts = lines[idx + i].split()
        coords.append([float(parts[0]), float(parts[1]), float(parts[2])])
    return scale, lattice, species_names, species_counts, np.array(coords)

def build_2x2_supercell(contcar_path):
    scale, lattice, species, counts, coords = parse_contcar(contcar_path)
    a_1x1 = np.linalg.norm(lattice[0])
    orig_c = np.linalg.norm(lattice[2])
    n_cr = counts[0]
    n_cl = counts[1]
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
            pos[0] = pos[0] % 1.0
            pos[1] = pos[1] % 1.0
            cr_2x2.append(pos)
    cl_2x2 = []
    for s in shifts:
        for c in cl_coords_1x1:
            pos = [c[0] / 2.0 + s[0], c[1] / 2.0 + s[1], convert_z(c[2])]
            pos[0] = pos[0] % 1.0
            pos[1] = pos[1] % 1.0
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

def generate_incar(vdw, site_name, a_2x2, has_tm):
    vdw_label = "D3" if vdw else "No vdW"
    system_tag = "CrCl3 2x2 + {} ({})".format(TM_SYMBOL, site_name) if has_tm else "CrCl3 2x2 Clean Substrate"
    magmom = "8*3.0 24*0.0 1*{:.1f}".format(TM_MAGMOM) if has_tm else "8*3.0 24*0.0"
    magmom_comment = ("# Initial magnetic moments (muB): 3.0 for Cr3+ (d3, S=3/2), "
                      "0.0 for Cl- (closed shell)" +
                      (", " + TM_MOM_DESC if has_tm else ""))
    tm_count_str = ", 1 {}".format(TM_SYMBOL) if has_tm else ""
    d3_method = " + Grimme DFT-D3 (IVDW=12 Zero-Damping)" if vdw else " (Pure GGA, no dispersion)"
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
ENCUT    = 400.0       # Kinetic energy cutoff (eV); ~1.33x max ENMAX (Cl ~300 eV), consistent with 1x1 and references
ALGO     = Normal      # Blocked-Davidson electronic minimization; numerically stable for magnetic 3d ions
EDIFF    = 1.0E-06     # Energy convergence threshold for electronic SCF loop (eV); ensures well-converged wavefunctions
NELM     = 100         # Maximum number of electronic SCF cycles per ionic step; provides headroom while halting stalled loops

# --- 2. Spin Polarization & Magnetic Moments ---
ISPIN    = 2           # Spin-polarized calculation; mandatory for open-shell magnetic 3d ions
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
IVDW     = 12          # Grimme DFT-D3 zero-damping dispersion correction (IVDW=12); models non-local vdW interactions
"""
    else:
        incar += """
# --- 5. van der Waals Dispersion Correction ---
# (DISABLED) No IVDW tag: Pure GGA-PBE without dispersion correction
"""

    incar += """
# --- 6. Ionic Relaxation & Convergence Criteria ---
IBRION   = 2           # Conjugate-gradient algorithm; most robust scheme for atomic coordinate relaxation
NSW      = 100         # Maximum number of ionic optimization steps; provides headroom for relaxation
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

def build_potcar(dest_path, include_tm=False):
    with open(POTCAR_CR_CL, "r", encoding="utf-8", errors="ignore") as f:
        cr_cl_content = f.read()
    if include_tm:
        with open(POTCAR_TM, "r", encoding="utf-8", errors="ignore") as f:
            tm_content = f.read()
        full_content = cr_cl_content + tm_content
    else:
        full_content = cr_cl_content
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_content)

def generate_job_script(job_name, project_dir, scratch_subdir):
    scratch_dir = os.path.join(SCRATCH_ROOT, scratch_subdir)
    return """#!/bin/bash
#SBATCH -J {job_name}
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --exclusive
#SBATCH --time=24:00:00

PROJECT_DIR="{project_dir}"
SCRATCH_DIR="{scratch_dir}"

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
""".format(job_name=job_name, project_dir=project_dir, scratch_dir=scratch_dir)

def setup_all():
    lat_2x2, a_2x2, cr_2x2, cl_2x2, a_1x1, orig_c = build_2x2_supercell(CONTCAR_1X1)
    cl11 = cl_2x2[10]
    cr3 = cr_2x2[2]
    s2_frac = [0.50000, 0.50000, 0.50000]

    tm_positions = {
        "S1": {
            "label": "S1 top-Cl",
            "desc": "{} above Atom 19 (Cl11) at (0.50000, 0.32035)".format(TM_SYMBOL),
            "coords": [cl11[0], cl11[1], cl11[2] + DIST_S1 / C_VACUUM],
        },
        "S2": {
            "label": "S2 hollow",
            "desc": "{} at center of Cr honeycomb ring at (0.50000, 0.50000)".format(TM_SYMBOL),
            "coords": [s2_frac[0], s2_frac[1], s2_frac[2] + DIST_S2 / C_VACUUM],
        },
        "S3": {
            "label": "S3 top-Cr",
            "desc": "{} directly above Atom 3 (Cr3) at (0.66667, 0.33333)".format(TM_SYMBOL),
            "coords": [cr3[0], cr3[1], cr3[2] + DIST_S3 / C_VACUUM],
        },
    }

    kpoints_content = generate_kpoints()
    vdw_configs = [
        ("no_vdw", False, "Pure PBE (no dispersion)"),
        ("yes_vdw", True, "PBE + DFT-D3 (IVDW=12)"),
    ]

    total_calcs = 0
    for vdw_name, vdw_flag, vdw_desc in vdw_configs:
        vdw_dir = os.path.join(BASE_DIR, vdw_name)
        clean_dir = os.path.join(vdw_dir, "clean")
        os.makedirs(clean_dir, exist_ok=True)
        write_poscar(
            os.path.join(clean_dir, "POSCAR"),
            "CrCl3 2x2 Clean Substrate ({}, U=0) (a_2x2={:.4f}A, c={:.4f}A)".format(
                "D3" if vdw_flag else "no_vdw", a_2x2, C_VACUUM),
            lat_2x2, ["Cr", "Cl"], [8, 24],
            cr_2x2 + cl_2x2,
        )
        with open(os.path.join(clean_dir, "INCAR"), "w") as f:
            f.write(generate_incar(vdw_flag, "clean", a_2x2, has_tm=False))
        with open(os.path.join(clean_dir, "KPOINTS"), "w") as f:
            f.write(kpoints_content)
        build_potcar(os.path.join(clean_dir, "POTCAR"), include_tm=False)
        job_name = "{}_cln_{}".format(TM_SYMBOL, vdw_name)
        with open(os.path.join(clean_dir, "job.sh"), "w") as f:
            f.write(generate_job_script(job_name, os.path.abspath(clean_dir), "{}/clean".format(vdw_name)))
        os.chmod(os.path.join(clean_dir, "job.sh"), 0o755)
        total_calcs += 1

        for site_key, site_info in tm_positions.items():
            site_dir = os.path.join(vdw_dir, site_key)
            os.makedirs(site_dir, exist_ok=True)
            tm_coord = site_info["coords"]
            all_coords = cr_2x2 + cl_2x2 + [tm_coord]

            write_poscar(
                os.path.join(site_dir, "POSCAR"),
                "CrCl3 2x2 + {} {} ({}, U=0) (a_2x2={:.4f}A, c={:.4f}A)".format(
                    TM_SYMBOL, site_info["label"], "D3" if vdw_flag else "no_vdw", a_2x2, C_VACUUM),
                lat_2x2, ["Cr", "Cl", TM_SYMBOL], [8, 24, 1],
                all_coords,
            )
            with open(os.path.join(site_dir, "INCAR"), "w") as f:
                f.write(generate_incar(vdw_flag, site_info["label"], a_2x2, has_tm=True))
            with open(os.path.join(site_dir, "KPOINTS"), "w") as f:
                f.write(kpoints_content)
            build_potcar(os.path.join(site_dir, "POTCAR"), include_tm=True)
            job_name = "{}_{}_{}".format(TM_SYMBOL, site_key, vdw_name)
            with open(os.path.join(site_dir, "job.sh"), "w") as f:
                f.write(generate_job_script(job_name, os.path.abspath(site_dir), "{}/{}".format(vdw_name, site_key)))
            os.chmod(os.path.join(site_dir, "job.sh"), 0o755)
            total_calcs += 1

    print("  Staged {} calculations for {}.".format(total_calcs, TM_SYMBOL))

if __name__ == "__main__":
    setup_all()
