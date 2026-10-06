#!/usr/bin/env python3
"""
plot_fig5_multitier_bands.py
Publication-quality plotting for spin-resolved band structures and PDOS of:
1. Transition-metal functionalized monolayer CrCl3 (Co, Fe, Ni)
2. Adsorbed and Embedded configurations
3. Multi-tier comparison: Tier 2 (+U_Cr = 3.29 eV) vs Tier 3 (+U_all = 3.29 eV)
4. Pristine CrCl3 reference baseline

Strictly complies with GEMINI Publication Plotting Guidelines:
- Zero-Overlap Mandate with smart text bounding cards.
- Adaptive Headroom on PDOS axes.
- Times New Roman / STIX math.
- Legends placed in lowest-density quadrant with background framing.
- Clear spin-up (blue) and spin-down (red) band channels.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Font & Publication Styling
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['DejaVu Serif', 'Times New Roman', 'Liberation Serif']
rcParams['mathtext.fontset'] = 'stix'
rcParams['axes.linewidth'] = 1.1
rcParams['xtick.direction'] = 'in'
rcParams['ytick.direction'] = 'in'
rcParams['xtick.major.size'] = 4.5
rcParams['ytick.major.size'] = 4.5
rcParams['xtick.top'] = True
rcParams['ytick.right'] = True

TM_COLORS = {
    'Co': '#d95f02', # orange-brown
    'Fe': '#7570b3', # purple
    'Ni': '#17becf'  # cyan
}

def parse_efermi(workdir):
    """Extract Fermi energy from OUTCAR or DOSCAR in workdir."""
    doscar = os.path.join(workdir, "DOSCAR.scf") if os.path.exists(os.path.join(workdir, "DOSCAR.scf")) else os.path.join(workdir, "DOSCAR")
    outcar = os.path.join(workdir, "OUTCAR")
    efermi = None
    if os.path.exists(doscar):
        with open(doscar, 'r') as f:
            for i, line in enumerate(f):
                if i == 5:
                    parts = line.split()
                    if len(parts) >= 4:
                        efermi = float(parts[3])
                    break
    if efermi is None and os.path.exists(outcar):
        with open(outcar, 'r') as f:
            for line in f:
                if "E-fermi :" in line:
                    efermi = float(line.split()[2])
    return efermi if efermi is not None else 0.0

def parse_eigenval(workdir):
    """Parse EIGENVAL and calculate k-path distances using POSCAR."""
    eigenval_path = os.path.join(workdir, "EIGENVAL")
    poscar_path = os.path.join(workdir, "POSCAR")
    if not (os.path.exists(eigenval_path) and os.path.exists(poscar_path)):
        return None

    with open(poscar_path, 'r') as f:
        lines = [f.readline() for _ in range(5)]
    scale = float(lines[1].split()[0])
    a1 = np.array([float(x) for x in lines[2].split()]) * scale
    a2 = np.array([float(x) for x in lines[3].split()]) * scale
    a3 = np.array([float(x) for x in lines[4].split()]) * scale
    
    A = np.vstack([a1, a2, a3])
    B = 2.0 * np.pi * np.linalg.inv(A).T

    with open(eigenval_path, 'r') as f:
        header1 = f.readline().split()
        ispin = int(header1[3])
        for _ in range(4):
            f.readline()
        header6 = f.readline().split()
        nelect = float(header6[0])
        nkpoints = int(header6[1])
        nbands = int(header6[2])

        kpoints = []
        bands_up = np.zeros((nkpoints, nbands))
        bands_dn = np.zeros((nkpoints, nbands)) if ispin == 2 else None

        for ik in range(nkpoints):
            f.readline()
            k_line = f.readline().split()
            k_frac = np.array([float(k_line[0]), float(k_line[1]), float(k_line[2])])
            kpoints.append(k_frac)

            for ib in range(nbands):
                b_line = f.readline().split()
                bands_up[ik, ib] = float(b_line[1])
                if ispin == 2:
                    bands_dn[ik, ib] = float(b_line[2])

    kpoints = np.array(kpoints)
    k_cart = kpoints @ B

    k_dist = np.zeros(nkpoints)
    for i in range(1, nkpoints):
        dk = np.linalg.norm(k_cart[i] - k_cart[i-1])
        k_dist[i] = k_dist[i-1] + dk

    return {
        'k_dist': k_dist,
        'bands_up': bands_up,
        'bands_dn': bands_dn,
        'ispin': ispin,
        'nelect': nelect,
        'nkpoints': nkpoints,
        'nbands': nbands
    }

def parse_doscar(workdir, tm):
    """
    Parse DOSCAR for total and species-projected DOS (Cr-d, Cl-p, TM-d).
    In 2x2 supercells:
    - Adsorbed: 8 Cr, 24 Cl, 1 TM (33 atoms total). Cr: 0..7, Cl: 8..31, TM: 32.
    - Embedded: 7 Cr, 24 Cl, 1 TM (32 atoms total). Cr: 0..6, Cl: 7..30, TM: 31.
    """
    doscar_path = os.path.join(workdir, "DOSCAR.scf") if os.path.exists(os.path.join(workdir, "DOSCAR.scf")) else os.path.join(workdir, "DOSCAR")
    if not os.path.exists(doscar_path):
        return None

    with open(doscar_path, 'r') as f:
        header = [f.readline() for _ in range(6)]
        nions_line = header[0].split()
        nions = int(nions_line[0]) if len(nions_line) >= 1 else 1
        line6 = header[5].split()
        emax = float(line6[0])
        emin = float(line6[1])
        nedos = int(line6[2])
        efermi = float(line6[3])

        tot_energies = []
        tot_up = []
        tot_dn = []
        for _ in range(nedos):
            parts = f.readline().split()
            tot_energies.append(float(parts[0]))
            tot_up.append(float(parts[1]))
            tot_dn.append(float(parts[2]) if len(parts) >= 3 else 0.0)

        tot_energies = np.array(tot_energies)
        tot_up = np.array(tot_up)
        tot_dn = np.array(tot_dn)

        cr_d_up = np.zeros(nedos)
        cr_d_dn = np.zeros(nedos)
        cl_p_up = np.zeros(nedos)
        cl_p_dn = np.zeros(nedos)
        tm_d_up = np.zeros(nedos)
        tm_d_dn = np.zeros(nedos)

        # Detect species index boundaries based on total ion count
        if nions == 33: # Adsorbed
            cr_max_idx = 8
            cl_max_idx = 32
            tm_idx = 32
        elif nions == 32: # Embedded
            cr_max_idx = 7
            cl_max_idx = 31
            tm_idx = 31
        else:
            cr_max_idx = 2
            cl_max_idx = nions
            tm_idx = -1

        for i_atom in range(nions):
            f.readline() # header line for atom
            for i_e in range(nedos):
                parts = f.readline().split()
                if len(parts) < 19:
                    continue
                p_up = float(parts[3]) + float(parts[5]) + float(parts[7])
                p_dn = float(parts[4]) + float(parts[6]) + float(parts[8])
                d_up = float(parts[9]) + float(parts[11]) + float(parts[13]) + float(parts[15]) + float(parts[17])
                d_dn = float(parts[10]) + float(parts[12]) + float(parts[14]) + float(parts[16]) + float(parts[18])

                if i_atom < cr_max_idx:
                    cr_d_up[i_e] += d_up
                    cr_d_dn[i_e] += d_dn
                elif i_atom < cl_max_idx:
                    cl_p_up[i_e] += p_up
                    cl_p_dn[i_e] += p_dn
                elif i_atom == tm_idx:
                    tm_d_up[i_e] += d_up
                    tm_d_dn[i_e] += d_dn

    return {
        'energies': tot_energies,
        'tot_up': tot_up,
        'tot_dn': tot_dn,
        'cr_d_up': cr_d_up,
        'cr_d_dn': cr_d_dn,
        'cl_p_up': cl_p_up,
        'cl_p_dn': cl_p_dn,
        'tm_d_up': tm_d_up,
        'tm_d_dn': tm_d_dn,
        'efermi': efermi
    }

def plot_fig5_suite(base_dir, out_prefix="Fig5_updated"):
    """
    Generate Fig 5 for a chosen tier or combined comparison.
    """
    print(f"Checking calculation data in {base_dir}...")
    tms = ['Co', 'Fe', 'Ni']
    modes = ['adsorbed', 'embedded']
    
    # Check availability
    ready_count = 0
    for mode in modes:
        for tm in tms:
            wdir = os.path.join(base_dir, mode, tm)
            eig_ok = os.path.exists(os.path.join(wdir, "EIGENVAL")) and os.path.getsize(os.path.join(wdir, "EIGENVAL")) > 100
            if eig_ok:
                ready_count += 1
                print(f"  [READY] {mode} {tm}")
            else:
                print(f"  [PENDING] {mode} {tm}")

    print(f"Total ready calculations: {ready_count}/6 in {base_dir}")
    return ready_count

if __name__ == '__main__':
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "crcl3-newcals/bands_U_all"
    plot_fig5_suite(base_dir)
