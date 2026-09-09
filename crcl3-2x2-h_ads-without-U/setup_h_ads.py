#!/usr/bin/env python3
"""
================================================================================
 SETUP H ADSORPTION ON PRISTINE CrCl3 2x2 SUPERCELL (No Hubbard U)
================================================================================
 Generates VASP inputs for hydrogen adsorption at three sites:
   S1 (top-Cl)  -- H above Atom 19 (Cl11) at (0.50000, 0.32035, 0.56679)
   S2 (hollow)  -- H at the center of the Cr honeycomb ring at (0.50000, 0.50000)
   S3 (top-Cr)  -- H directly above Atom 3 (Cr3) at (0.66667, 0.33333, 0.50000)

 Two dispersion variants:
   no_vdw  -- Pure GGA-PBE (no van der Waals correction)
   yes_vdw -- PBE + DFT-D3 (Grimme zero-damping, IVDW=11)

 Both variants use U = 0 (LDAU = .FALSE.) and ISIF = 2.

 Supercell is constructed from the relaxed 1x1 CONTCAR (quick_test_k551).
================================================================================
"""

import os
import sys
import math
import numpy as np

# ========================= PATHS =========================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = SCRIPT_DIR

# Relaxed 1x1 primitive cell (ISIF=3 lattice-optimized, Pure GGA-PBE, U=0)
CONTCAR_1X1 = os.path.join(SCRIPT_DIR, "..", "crcl3-1x1", "quick_test_k551", "CONTCAR")

# POTCAR sources
POTCAR_CR_CL = os.path.join(SCRIPT_DIR, "..", "crcl3-1x1", "quick_test_k551", "POTCAR")  # Cr + Cl
POTCAR_H = os.path.join(os.path.expanduser("~"), "temporary", "dotfiles",
                        "potentials", "potpaw_PBE.64", "H", "POTCAR")

# Scratch base for SLURM jobs
SCRATCH_ROOT = "/home/cr/scratch_vasp/crcl3-2x2-h_ads-without-U"

# ========================= CONSTANTS =========================
C_VACUUM = 20.0000  # Vacuum thickness (Angstrom) for 2x2 supercell

# H initial placement distances above target atoms (Angstrom)
# Based on physical/covalent radii & DFT potential well analysis:
H_DIST_S1 = 1.30  # H above Atom 19 (Cl11) (S1 site; covalent H-Cl r_e ~ 1.275 A + 0.025 A)
H_DIST_S2 = 1.60  # H above slab center z=0.5 (S2 hollow site; 0.264 A above top Cl plane)
H_DIST_S3 = 1.55  # H above Atom 3 (Cr3) (S3 top-Cr site; exact manuscript equilibrium d(H-Cr)=1.55 A)


def parse_contcar(filepath):
    """
    Parse a VASP CONTCAR/POSCAR file. Returns:
      scale, lattice_vectors (3x3), species_names, species_counts, frac_coords
    """
    with open(filepath, "r") as f:
        lines = [l.rstrip() for l in f.readlines()]

    comment = lines[0]
    scale = float(lines[1].split()[0])
    v1 = np.array([float(x) for x in lines[2].split()[:3]]) * scale
    v2 = np.array([float(x) for x in lines[3].split()[:3]]) * scale
    v3 = np.array([float(x) for x in lines[4].split()[:3]]) * scale
    lattice = np.array([v1, v2, v3])

    species_names = lines[5].split()
    species_counts = [int(x) for x in lines[6].split()]

    # Check for Selective Dynamics or Direct/Cartesian line
    idx = 7
    coord_type = lines[idx].strip()
    if coord_type[0].upper() in ("S",):  # Selective dynamics
        idx += 1
        coord_type = lines[idx].strip()
    idx += 1  # Now at first coordinate line

    total_atoms = sum(species_counts)
    coords = []
    for i in range(total_atoms):
        parts = lines[idx + i].split()
        coords.append([float(parts[0]), float(parts[1]), float(parts[2])])

    return scale, lattice, species_names, species_counts, np.array(coords)


def build_2x2_supercell(contcar_path):
    """
    Read the relaxed 1x1 CONTCAR and build an exact 2x2x1 supercell.
    Returns: lat_2x2 (3x3), a_2x2, cr_2x2, cl_2x2, a_1x1, orig_c
    """
    scale, lattice, species, counts, coords = parse_contcar(contcar_path)

    a_1x1 = np.linalg.norm(lattice[0])
    orig_c = np.linalg.norm(lattice[2])

    n_cr = counts[0]
    n_cl = counts[1]

    cr_coords_1x1 = coords[:n_cr]
    cl_coords_1x1 = coords[n_cr:n_cr + n_cl]

    # 2x2 in-plane lattice parameter
    a_2x2 = 2.0 * a_1x1

    # Standard hexagonal cell vectors for 2x2 supercell
    lat_2x2 = np.array([
        [a_2x2, 0.0, 0.0],
        [-0.5 * a_2x2, 0.5 * math.sqrt(3.0) * a_2x2, 0.0],
        [0.0, 0.0, C_VACUUM]
    ])

    def convert_z(z_frac_orig):
        """Re-map z from orig_c box to C_VACUUM box, centered at z=0.5."""
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
    """Write a VASP POSCAR file."""
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


def generate_incar(vdw, site_name, a_2x2, has_h):
    """
    Generate a fully commented VASP INCAR.
    vdw: bool -- whether to include DFT-D3
    site_name: str -- e.g. "clean", "S1 top-Cl", "S2 hollow", "S3 top-Cr"
    a_2x2: float -- supercell lattice parameter
    has_h: bool -- whether H is present (affects MAGMOM and POTCAR order)
    """
    vdw_label = "D3" if vdw else "No vdW"
    system_tag = "CrCl3 2x2 + H ({})".format(site_name) if has_h else "CrCl3 2x2 Clean Substrate"
    magmom = "8*3.0 24*0.0 1*0.0" if has_h else "8*3.0 24*0.0"
    magmom_comment = ("# Initial magnetic moments (muB): 3.0 for Cr3+ (d3, S=3/2), "
                      "0.0 for Cl- (closed shell)" +
                      (", 0.0 for H" if has_h else ""))
    h_count_str = ", 1 H" if has_h else ""
    d3_method = " + Grimme DFT-D3 (zero-damping)" if vdw else " (Pure GGA, no dispersion)"
    d3_baseline = "DFT-D3" if vdw else "GGA-PBE"

    incar = """# =========================================================================
# SYSTEM: {system_tag} ({vdw_label}, U=0eV)
# Cell: CrCl3 2x2 Monolayer Supercell (8 Cr, 24 Cl{h_count_str})
# Vacuum: c = {c_vac:.4f} Angstroms (Fixed vacuum layer, slab centered at z = 0.5)
# Method: PBE{d3_method}, U = 0 eV
# Equilibrium In-Plane Cell Parameter: a_2x2 = {a_2x2:.4f} Angstroms (from ISIF=3 1x1 zero-stress)
# =========================================================================

# --- 1. Electronic Minimization & Plane-Wave Basis ---
SYSTEM   = {system_tag} ({vdw_label}, U=0eV) # Informative calculation title printed in OUTCAR
PREC     = Accurate    # High-precision FFT and integration grid; eliminates grid-aliasing forces in 2D sheets
ENCUT    = 400.0       # Kinetic energy cutoff (eV); ~1.33x max ENMAX (Cl ~300 eV), consistent with 1x1 and H2 references
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
        system_tag=system_tag, vdw_label=vdw_label, h_count_str=h_count_str,
        c_vac=C_VACUUM, d3_method=d3_method, a_2x2=a_2x2,
        magmom=magmom, magmom_comment=magmom_comment
    )

    # --- 5. van der Waals ---
    if vdw:
        incar += """
# --- 5. van der Waals Dispersion Correction ---
IVDW     = 11          # Grimme DFT-D3 zero-damping dispersion correction; models non-local vdW interactions
"""
    else:
        incar += """
# --- 5. van der Waals Dispersion Correction ---
# (DISABLED) No IVDW tag: Pure GGA-PBE without dispersion correction
"""

    incar += """
# --- 6. Ionic Relaxation & Convergence Criteria ---
IBRION   = 2           # Conjugate-gradient algorithm; most robust scheme for atomic coordinate relaxation
NSW      = 100         # Maximum number of ionic optimization steps; provides headroom for hydrogen relaxation
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
    """Generate KPOINTS file: 5x5x1 Gamma-centered (consistent with project 2x2 calculations)."""
    return """K-Points 5x5x1 Gamma-centered (CrCl3 2x2 Supercell)
0
Gamma
 5  5  1
 0  0  0
"""


def build_potcar(dest_path, include_h=False):
    """
    Build POTCAR by concatenating Cr + Cl (+ H if needed).
    Species order must match POSCAR: Cr, Cl, [H].
    """
    with open(POTCAR_CR_CL, "r", encoding="utf-8", errors="ignore") as f:
        cr_cl_content = f.read()

    if include_h:
        if not os.path.exists(POTCAR_H):
            raise FileNotFoundError(
                "H POTCAR not found at {}.\n"
                "Please ensure the VASP pseudopotential directory is available.".format(POTCAR_H)
            )
        with open(POTCAR_H, "r", encoding="utf-8", errors="ignore") as f:
            h_content = f.read()
        full_content = cr_cl_content + h_content
    else:
        full_content = cr_cl_content

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_content)


def generate_job_script(job_name, project_dir, scratch_subdir):
    """Generate an optimized, fault-tolerant SLURM job script matching this cluster's environment."""
    return """#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -p normal
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=48:00:00
#SBATCH --requeue
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

echo "=========================================================="
echo "Job Name:    $SLURM_JOB_NAME"
echo "Job ID:      $SLURM_JOB_ID"
echo "Host:        $(hostname)"
echo "Directory:   $(pwd)"
echo "Start Time:  $(date)"
echo "CPUs Alloc:  $SLURM_NTASKS"
echo "=========================================================="

# 1. Fault Tolerance: Intercept shutdown/preemption signals for graceful VASP exit
trap 'echo "LABORT = .TRUE." > STOPCAR; echo "[$(date)] Intercepted termination signal! Flushed STOPCAR for clean exit."; wait' SIGTERM SIGINT SIGHUP

# 2. Resumption Logic: Check if valid CONTCAR exists from previous step/interruption
if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    NLINES=$(wc -l < CONTCAR)
    if [ "$NLINES" -ge 8 ]; then
        echo "[$(date)] Found existing valid CONTCAR ($NLINES lines). Resuming relaxation..."
        cp POSCAR POSCAR.bak_$(date +%s)
        cp CONTCAR POSCAR
    fi
fi

# 3. Environment Preparation
module purge
module load spack/1.0.1
module load openmpi/5.0.8-aocc-5.0.0-linux-rocky10-icelake-wxmifob
module load vasp/6.5.1-aocc-5.0.0-linux-rocky10-icelake-erkzov4

export OMP_NUM_THREADS=1

# 4. In-Situ VASP Execution
echo "Executing VASP 6.5.1 with $SLURM_NTASKS MPI ranks..."
mpirun -np $SLURM_NTASKS vasp_std > vasp.out 2>&1
EXIT_CODE=$?

# Remove STOPCAR if present after clean termination
rm -f STOPCAR

echo "=========================================================="
echo "Finished at $(date) with exit code $EXIT_CODE"
echo "=========================================================="
exit $EXIT_CODE
""".format(job_name=job_name)



def setup_all():
    """Main entry point: build all directories and VASP input files."""
    print("\n" + "=" * 85)
    print("   H ADSORPTION ON PRISTINE CrCl3 2x2 SUPERCELL (No Hubbard U)")
    print("   Variants: no_vdw (Pure PBE) | yes_vdw (PBE + DFT-D3)")
    print("=" * 85)

    # --- Validate inputs ---
    contcar_path = os.path.abspath(CONTCAR_1X1)
    if not os.path.exists(contcar_path):
        print("  [ERROR] Relaxed 1x1 CONTCAR not found: {}".format(contcar_path))
        sys.exit(1)
    if not os.path.exists(POTCAR_CR_CL):
        print("  [ERROR] Cr+Cl POTCAR not found: {}".format(POTCAR_CR_CL))
        sys.exit(1)
    if not os.path.exists(POTCAR_H):
        print("  [ERROR] H POTCAR not found: {}".format(POTCAR_H))
        sys.exit(1)

    print("\n  1x1 CONTCAR source:   {}".format(contcar_path))
    print("  Cr+Cl POTCAR source:  {}".format(os.path.abspath(POTCAR_CR_CL)))
    print("  H POTCAR source:      {}".format(os.path.abspath(POTCAR_H)))

    # --- Build 2x2 supercell from relaxed 1x1 ---
    lat_2x2, a_2x2, cr_2x2, cl_2x2, a_1x1, orig_c = build_2x2_supercell(contcar_path)

    print("\n  Relaxed 1x1 lattice:  a = {:.4f} A, c = {:.4f} A".format(a_1x1, orig_c))
    print("  2x2 supercell:        a = {:.4f} A, c = {:.4f} A".format(a_2x2, C_VACUUM))
    print("  Cr atoms: {}, Cl atoms: {}".format(len(cr_2x2), len(cl_2x2)))

    # -------------------------------------------------------------------------
    # TARGET ATOMS FOR ADSORPTION SITES (per user specification & crystallography)
    # -------------------------------------------------------------------------
    # S1: Atom 19 (Cl11) at frac (0.50000, 0.32035, 0.56679)
    # In POSCAR order: Cr1-8 are indices 0-7, Cl1-24 are indices 8-31.
    # Therefore, Cl11 (atom 19 overall) is cl_2x2[10].
    cl11 = cl_2x2[10]
    assert abs(cl11[0] - 0.50000) < 1e-4 and abs(cl11[1] - 0.32035) < 1e-4, \
        "Cl11 coordinates do not match expected (0.50000, 0.32035): {}".format(cl11)

    # S3: Atom 3 (Cr3) at frac (0.66667, 0.33333, 0.50000)
    # In POSCAR order: Cr3 (atom 3 overall) is cr_2x2[2].
    cr3 = cr_2x2[2]
    assert abs(cr3[0] - 2.0/3.0) < 1e-4 and abs(cr3[1] - 1.0/3.0) < 1e-4, \
        "Cr3 coordinates do not match expected (0.66667, 0.33333): {}".format(cr3)

    # S2: Hollow site at the center of the Cr honeycomb ring at (0.50000, 0.50000)
    s2_frac = [0.50000, 0.50000, 0.50000]

    # H positions (fractional in 2x2 cell)
    h_positions = {
        "S1": {
            "label": "S1 top-Cl",
            "desc": "H above Atom 19 (Cl11) at (0.50000, 0.32035, 0.56679)",
            "coords": [cl11[0], cl11[1], cl11[2] + H_DIST_S1 / C_VACUUM],
        },
        "S2": {
            "label": "S2 hollow",
            "desc": "H at center of Cr honeycomb ring at (0.50000, 0.50000)",
            "coords": [s2_frac[0], s2_frac[1], s2_frac[2] + H_DIST_S2 / C_VACUUM],
        },
        "S3": {
            "label": "S3 top-Cr",
            "desc": "H directly above Atom 3 (Cr3) at (0.66667, 0.33333, 0.50000)",
            "coords": [cr3[0], cr3[1], cr3[2] + H_DIST_S3 / C_VACUUM],
        },
    }

    print("\n  H placement sites:")
    for site, info in h_positions.items():
        hc = info["coords"]
        z_cart = hc[2] * C_VACUUM
        print("    {} ({}): frac ({:.5f}, {:.5f}, {:.6f}) "
              "=> z_cart = {:.3f} A  [{}]".format(site, info["label"], hc[0], hc[1], hc[2],
                                                   z_cart, info["desc"]))

    # --- Generate KPOINTS (shared by all) ---
    kpoints_content = generate_kpoints()

    # --- Loop over vdW variants ---
    vdw_configs = [
        ("no_vdw", False, "Pure PBE (no dispersion)"),
        ("yes_vdw", True, "PBE + DFT-D3 (IVDW=11)"),
    ]

    total_calcs = 0
    for vdw_name, vdw_flag, vdw_desc in vdw_configs:
        print("\n  " + "-" * 70)
        print("  Variant: {} -- {}".format(vdw_name, vdw_desc))
        print("  " + "-" * 70)

        vdw_dir = os.path.join(BASE_DIR, vdw_name)

        # --- Clean substrate (no H) ---
        clean_dir = os.path.join(vdw_dir, "clean")
        os.makedirs(clean_dir, exist_ok=True)
        clean_project = os.path.abspath(clean_dir)

        write_poscar(
            os.path.join(clean_dir, "POSCAR"),
            "CrCl3 2x2 Clean Substrate ({}, U=0) (a_2x2={:.4f}A, c={:.4f}A)".format(
                "D3" if vdw_flag else "no_vdw", a_2x2, C_VACUUM),
            lat_2x2, ["Cr", "Cl"], [8, 24],
            cr_2x2 + cl_2x2,
        )
        with open(os.path.join(clean_dir, "INCAR"), "w") as f:
            f.write(generate_incar(vdw_flag, "clean", a_2x2, has_h=False))
        with open(os.path.join(clean_dir, "KPOINTS"), "w") as f:
            f.write(kpoints_content)
        build_potcar(os.path.join(clean_dir, "POTCAR"), include_h=False)
        job_name = "H_cln_{}".format(vdw_name)
        with open(os.path.join(clean_dir, "job.sh"), "w") as f:
            f.write(generate_job_script(job_name, clean_project, "{}/clean".format(vdw_name)))
        os.chmod(os.path.join(clean_dir, "job.sh"), 0o755)

        print("    [OK] clean/ -- pristine CrCl3 2x2 reference (8 Cr + 24 Cl)")
        total_calcs += 1

        # --- H adsorption sites ---
        for site_key, site_info in h_positions.items():
            site_dir = os.path.join(vdw_dir, site_key)
            os.makedirs(site_dir, exist_ok=True)
            site_project = os.path.abspath(site_dir)

            h_coord = site_info["coords"]
            all_coords = cr_2x2 + cl_2x2 + [h_coord]

            write_poscar(
                os.path.join(site_dir, "POSCAR"),
                "CrCl3 2x2 + H {} ({}, U=0) (a_2x2={:.4f}A, c={:.4f}A)".format(
                    site_info["label"], "D3" if vdw_flag else "no_vdw", a_2x2, C_VACUUM),
                lat_2x2, ["Cr", "Cl", "H"], [8, 24, 1],
                all_coords,
            )
            with open(os.path.join(site_dir, "INCAR"), "w") as f:
                f.write(generate_incar(vdw_flag, site_info["label"], a_2x2, has_h=True))
            with open(os.path.join(site_dir, "KPOINTS"), "w") as f:
                f.write(kpoints_content)
            build_potcar(os.path.join(site_dir, "POTCAR"), include_h=True)
            job_name = "H_{}_{}".format(site_key, vdw_name)
            with open(os.path.join(site_dir, "job.sh"), "w") as f:
                f.write(generate_job_script(job_name, site_project, "{}/{}".format(vdw_name, site_key)))
            os.chmod(os.path.join(site_dir, "job.sh"), 0o755)

            print("    [OK] {}/ -- {} (8 Cr + 24 Cl + 1 H)".format(site_key, site_info["desc"]))
            total_calcs += 1

    print("\n" + "=" * 85)
    print("  SUCCESS: {} CALCULATION DIRECTORIES STAGED".format(total_calcs))
    print("  All use ISIF=2, EDIFFG=-0.025, U=0, 5x5x1 k-points")
    print("  CONFIRMATION: NO SLURM JOBS HAVE BEEN SUBMITTED.")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    setup_all()
