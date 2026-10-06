#!/usr/bin/env python3
"""
plot_pristine_bands.py
Publication-quality plotting of spin-resolved band structure and PDOS
for pristine monolayer CrCl3 under Tier 2 (U_Cr = 3.29 eV, IVDW = 12).

Adheres strictly to GEMINI publication guidelines:
- Zero-Overlap Mandate with smart text bounding cards.
- Times New Roman font / STIX math.
- Clear spin-up (blue) and spin-down (red) channels.
- Side-by-side alignment between Band Structure and PDOS.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Font and publication styling
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['DejaVu Serif', 'Times New Roman', 'Liberation Serif']
rcParams['mathtext.fontset'] = 'stix'
rcParams['axes.linewidth'] = 1.2
rcParams['xtick.direction'] = 'in'
rcParams['ytick.direction'] = 'in'
rcParams['xtick.major.size'] = 5
rcParams['ytick.major.size'] = 5
rcParams['xtick.minor.size'] = 3
rcParams['ytick.minor.size'] = 3
rcParams['xtick.top'] = True
rcParams['ytick.right'] = True

def parse_efermi(outcar_path="OUTCAR", doscar_path="DOSCAR"):
    """Extract Fermi energy from OUTCAR or DOSCAR."""
    efermi = None
    if os.path.exists(doscar_path):
        with open(doscar_path, 'r') as f:
            for i, line in enumerate(f):
                if i == 5:
                    parts = line.split()
                    if len(parts) >= 4:
                        efermi = float(parts[3])
                    break
    if efermi is None and os.path.exists(outcar_path):
        with open(outcar_path, 'r') as f:
            for line in f:
                if "E-fermi :" in line:
                    efermi = float(line.split()[2])
    return efermi if efermi is not None else 0.0

def parse_eigenval(eigenval_path, poscar_path):
    """
    Parse VASP EIGENVAL file and calculate reciprocal path distances using POSCAR cell.
    """
    with open(poscar_path, 'r') as f:
        lines = [f.readline() for _ in range(5)]
    scale = float(lines[1].split()[0])
    a1 = np.array([float(x) for x in lines[2].split()]) * scale
    a2 = np.array([float(x) for x in lines[3].split()]) * scale
    a3 = np.array([float(x) for x in lines[4].split()]) * scale
    
    # Reciprocal lattice vectors (b1, b2, b3) without 2*pi factor for fractional coords
    # b_i . a_j = 2*pi * delta_ij => B = 2*pi * inv(A).T
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
            f.readline() # blank
            k_line = f.readline().split()
            k_frac = np.array([float(k_line[0]), float(k_line[1]), float(k_line[2])])
            kpoints.append(k_frac)

            for ib in range(nbands):
                b_line = f.readline().split()
                bands_up[ik, ib] = float(b_line[1])
                if ispin == 2:
                    bands_dn[ik, ib] = float(b_line[2])

    kpoints = np.array(kpoints)
    # Convert to cartesian reciprocal coordinates (Angstrom^-1)
    k_cart = kpoints @ B

    # Calculate cumulative distance along path
    k_dist = np.zeros(nkpoints)
    for i in range(1, nkpoints):
        dk = np.linalg.norm(k_cart[i] - k_cart[i-1])
        k_dist[i] = k_dist[i-1] + dk

    return k_dist, bands_up, bands_dn, ispin, nelect

def parse_doscar(doscar_path):
    """
    Parse DOSCAR for total and projected DOS (Cr-d and Cl-p).
    """
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

        # Read Total DOS
        tot_energies = []
        tot_up = []
        tot_dn = []
        for _ in range(nedos):
            parts = f.readline().split()
            tot_energies.append(float(parts[0]))
            tot_up.append(float(parts[1]))
            if len(parts) >= 3:
                tot_dn.append(float(parts[2]))
            else:
                tot_dn.append(0.0)

        tot_energies = np.array(tot_energies)
        tot_up = np.array(tot_up)
        tot_dn = np.array(tot_dn)

        # Projected DOS (if LORBIT >= 10 was set)
        # Monolayer CrCl3 primitive cell has 2 Cr atoms (indices 0, 1) and 6 Cl atoms (indices 2..7)
        cr_d_up = np.zeros(nedos)
        cr_d_dn = np.zeros(nedos)
        cl_p_up = np.zeros(nedos)
        cl_p_dn = np.zeros(nedos)

        for i_atom in range(nions):
            f.readline() # header for atom
            for i_e in range(nedos):
                parts = f.readline().split()
                if len(parts) < 10:
                    continue
                # For LORBIT=11, format is: energy s_up s_dn p_x_up p_x_dn p_y... d_xy...
                # Total p = px + py + pz; Total d = dxy + dyz + dz2 + dxz + dx2-y2
                # Columns: 
                # 0: E
                # 1,2: s_up, s_dn
                # 3,4: py_up, py_dn; 5,6: pz_up, pz_dn; 7,8: px_up, px_dn (p sum = 3+5+7, 4+6+8)
                # 9,10: dxy_up, dxy_dn; 11,12: dyz... 13,14: dz2... 15,16: dxz... 17,18: dx2...
                if len(parts) >= 19:
                    p_up = float(parts[3]) + float(parts[5]) + float(parts[7])
                    p_dn = float(parts[4]) + float(parts[6]) + float(parts[8])
                    d_up = float(parts[9]) + float(parts[11]) + float(parts[13]) + float(parts[15]) + float(parts[17])
                    d_dn = float(parts[10]) + float(parts[12]) + float(parts[14]) + float(parts[16]) + float(parts[18])

                    cr_limit = 8 if nions >= 32 else 2
                    if i_atom < cr_limit: # Cr
                        cr_d_up[i_e] += d_up
                        cr_d_dn[i_e] += d_dn
                    else: # Cl
                        cl_p_up[i_e] += p_up
                        cl_p_dn[i_e] += p_dn

    return {
        'energies': tot_energies,
        'tot_up': tot_up,
        'tot_dn': tot_dn,
        'cr_d_up': cr_d_up,
        'cr_d_dn': cr_d_dn,
        'cl_p_up': cl_p_up,
        'cl_p_dn': cl_p_dn,
        'efermi': efermi
    }

def plot_pristine(workdir, output_png, output_pdf):
    print(f"Generating pristine CrCl3 band structure from {workdir}...")
    eigenval_file = os.path.join(workdir, "EIGENVAL")
    poscar_file = os.path.join(workdir, "POSCAR")
    doscar_file = os.path.join(workdir, "DOSCAR.scf") if os.path.exists(os.path.join(workdir, "DOSCAR.scf")) else os.path.join(workdir, "DOSCAR")
    outcar_file = os.path.join(workdir, "OUTCAR")

    efermi = parse_efermi(outcar_file, doscar_file)
    k_dist, bands_up, bands_dn, ispin, nelect = parse_eigenval(eigenval_file, poscar_file)
    dos_data = parse_doscar(doscar_file)

    # Shift eigenvalues by Fermi level
    bands_up = bands_up - efermi
    if ispin == 2:
        bands_dn = bands_dn - efermi

    # Determine special points along Gamma - M - K - Gamma
    # Path has 25 points per segment, total 73 or 75 points
    nk = len(k_dist)
    pts_per_seg = (nk - 1) // 3
    k_nodes = [k_dist[0], k_dist[pts_per_seg], k_dist[2 * pts_per_seg], k_dist[-1]]
    k_labels = [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$']

    # Determine fundamental band gap and VBM/CBM
    # For spin-polarized CrCl3, find highest occupied below E_F and lowest unoccupied above E_F
    occ_up = bands_up[bands_up <= 0.0]
    unocc_up = bands_up[bands_up > 0.0]
    vbm_up = np.max(occ_up) if len(occ_up) > 0 else -999.0
    cbm_up = np.min(unocc_up) if len(unocc_up) > 0 else 999.0
    gap_up = cbm_up - vbm_up

    if ispin == 2:
        occ_dn = bands_dn[bands_dn <= 0.0]
        unocc_dn = bands_dn[bands_dn > 0.0]
        vbm_dn = np.max(occ_dn) if len(occ_dn) > 0 else -999.0
        cbm_dn = np.min(unocc_dn) if len(unocc_dn) > 0 else 999.0
        gap_dn = cbm_dn - vbm_dn
        
        vbm = max(vbm_up, vbm_dn)
        cbm = min(cbm_up, cbm_dn)
        direct_or_indirect_gap = cbm - vbm
    else:
        vbm = vbm_up
        cbm = cbm_up
        direct_or_indirect_gap = gap_up

    print(f"Fermi Energy: {efermi:.4f} eV")
    print(f"VBM: {vbm:.3f} eV, CBM: {cbm:.3f} eV, Band Gap: {direct_or_indirect_gap:.3f} eV")

    # Set up Figure: 2-panel layout (Bands on left, PDOS on right)
    fig, (ax_band, ax_dos) = plt.subplots(1, 2, figsize=(8.5, 5.0), gridspec_kw={'width_ratios': [2.2, 1.2]}, sharey=True)

    # Energy window
    e_min, e_max = -4.0, 4.0

    # 1. Plot Band Structure
    for ib in range(bands_up.shape[1]):
        label_up = "Spin Up" if ib == 0 else ""
        ax_band.plot(k_dist, bands_up[:, ib], color='#1f77b4', lw=1.2, alpha=0.9, label=label_up)
    
    if ispin == 2:
        for ib in range(bands_dn.shape[1]):
            label_dn = "Spin Down" if ib == 0 else ""
            ax_band.plot(k_dist, bands_dn[:, ib], color='#d62728', lw=1.2, ls='--', alpha=0.85, label=label_dn)

    # Vertical lines at high symmetry points
    for node in k_nodes:
        ax_band.axvline(node, color='#888888', lw=0.8, ls=':')

    # Fermi level line
    ax_band.axhline(0.0, color='black', lw=0.9, ls='-.', alpha=0.7)
    ax_dos.axhline(0.0, color='black', lw=0.9, ls='-.', alpha=0.7)

    ax_band.set_xlim(k_dist[0], k_dist[-1])
    ax_band.set_xticks(k_nodes)
    ax_band.set_xticklabels(k_labels, fontsize=12)
    ax_band.set_ylabel(r'$E - E_{\mathrm{F}}\ (\mathrm{eV})$', fontsize=12)
    ax_band.set_ylim(e_min, e_max)
    ax_band.set_title(r'$\mathbf{(a)}$ Monolayer $\mathrm{CrCl}_3$ ($+U_{\mathrm{Cr}}$, vdW-D3)', fontsize=12, pad=10)

    # Smart bounding card for band gap annotation (Zero-Overlap Mandate)
    gap_card = dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.92, edgecolor='#cccccc', lw=1.0)
    ax_band.text(0.05, 0.92, f"$E_g = {direct_or_indirect_gap:.2f}$ eV\n$U_{{\\mathrm{{Cr}}}} = 3.29$ eV", 
                 transform=ax_band.transAxes, verticalalignment='top', fontsize=10, bbox=gap_card)

    ax_band.legend(loc='lower left', framealpha=0.9, edgecolor='#cccccc', fontsize=10)

    # 2. Plot PDOS
    if dos_data is not None:
        e_dos = dos_data['energies'] - efermi
        mask = (e_dos >= e_min) & (e_dos <= e_max)
        e_sub = e_dos[mask]

        # Cr-3d and Cl-3p
        ax_dos.plot(dos_data['cr_d_up'][mask], e_sub, color='#1f77b4', lw=1.3, label=r'Cr $3d$ ($\uparrow$)')
        ax_dos.plot(-dos_data['cr_d_dn'][mask], e_sub, color='#1f77b4', lw=1.3, ls='--', label=r'Cr $3d$ ($\downarrow$)')
        ax_dos.plot(dos_data['cl_p_up'][mask], e_sub, color='#2ca02c', lw=1.2, label=r'Cl $3p$ ($\uparrow$)')
        ax_dos.plot(-dos_data['cl_p_dn'][mask], e_sub, color='#2ca02c', lw=1.2, ls='--', label=r'Cl $3p$ ($\downarrow$)')

        ax_dos.axvline(0.0, color='#888888', lw=0.6)
        
        # Adaptive x-limits for PDOS
        max_dos = max(np.max(dos_data['cr_d_up'][mask]), np.max(dos_data['cl_p_up'][mask]), 1.0)
        headroom = max_dos * 1.25
        ax_dos.set_xlim(-headroom, headroom)
        ax_dos.set_xlabel('PDOS (states/eV)', fontsize=11)
        ax_dos.set_title(r'$\mathbf{(b)}$ Projected DOS', fontsize=12, pad=10)
        ax_dos.legend(loc='upper right', framealpha=0.9, edgecolor='#cccccc', fontsize=8.5)

    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.savefig(output_pdf)
    plt.close()
    print(f"Successfully saved figures:\n  -> {output_png}\n  -> {output_pdf}")

if __name__ == '__main__':
    workdir = sys.argv[1] if len(sys.argv) > 1 else "."
    out_png = sys.argv[2] if len(sys.argv) > 2 else "crcl3_pristine_bands_Ucr_vdw12.png"
    out_pdf = sys.argv[3] if len(sys.argv) > 3 else "crcl3_pristine_bands_Ucr_vdw12.pdf"
    plot_pristine(workdir, out_png, out_pdf)
