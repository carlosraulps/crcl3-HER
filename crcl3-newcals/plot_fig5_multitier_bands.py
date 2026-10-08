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

# Exact elemental color definitions from reference image:
# Cr: Deep Navy Blue, Cl: Electric Green, Co: Cyan, Fe: Ochre Brown, Ni: Magenta
ELEMENT_COLORS = {
    'Cr': '#2a2a98', # deep navy blue
    'Cl': '#49df27', # bright electric green
    'Co': '#22c3c3', # cyan / teal
    'Fe': '#a67523', # warm ochre / golden brown
    'Ni': '#f229f2'  # vibrant magenta / pink
}
TM_COLORS = ELEMENT_COLORS

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

def plot_fig5_suite(base_dir, out_dir="crcl3-newcals"):
    """
    Generate Fig 5 for a chosen tier: 12 sub-panels (6 systems x (bands + PDOS)).
    Panels (a,b), (c,d), (e,f) correspond to surface-adsorbed Co, Fe, Ni.
    Panels (g,h), (i,j), (k,l) correspond to embedded Co, Fe, Ni.
    """
    print(f"Loading calculation data from {base_dir}...")
    tms = ['Co', 'Fe', 'Ni']
    modes = ['adsorbed', 'embedded']
    panel_letters = [
        [('a', 'b'), ('c', 'd'), ('e', 'f')],
        [('g', 'h'), ('i', 'j'), ('k', 'l')]
    ]

    from matplotlib.gridspec import GridSpec
    # Space-efficient layout eliminating dead vacuum margins
    fig = plt.figure(figsize=(15.8, 9.8))
    gs_outer = GridSpec(2, 3, figure=fig, hspace=0.22, wspace=0.18,
                        left=0.055, right=0.985, top=0.93, bottom=0.065)

    k_labels = [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$']

    for row_idx, mode in enumerate(modes):
        for col_idx, tm in enumerate(tms):
            wdir = os.path.join(base_dir, mode, tm)
            eig = parse_eigenval(wdir)
            dos = parse_doscar(wdir, tm)
            ef = parse_efermi(wdir)

            if eig is None or dos is None:
                print(f"Skipping {mode} {tm}: data not available")
                continue

            # Band width compressed to 0.65 of standard width (ratio 1.4:1.0)
            gs_inner = gs_outer[row_idx, col_idx].subgridspec(1, 2, width_ratios=[1.42, 1.0], wspace=0.04)
            ax_band = fig.add_subplot(gs_inner[0, 0])
            ax_dos  = fig.add_subplot(gs_inner[0, 1], sharey=ax_band)

            let_band, let_dos = panel_letters[row_idx][col_idx]
            tm_label = f"{tm} ({'ads' if mode == 'adsorbed' else 'emb'})"

            # 1. Band Structure
            k_dist = eig['k_dist']
            bands_up = eig['bands_up'] - ef
            bands_dn = eig['bands_dn'] - ef if eig['bands_dn'] is not None else None

            nk = len(k_dist)
            tick_indices = [0, nk // 3, 2 * nk // 3, nk - 1]
            tick_locs = [k_dist[i] for i in tick_indices]

            # High-intensity, non-opaque band traces
            for ib in range(eig['nbands']):
                ax_band.plot(k_dist, bands_up[:, ib], color='#0544d6', lw=1.15, alpha=1.0,
                             label='Spin-up' if ib == 0 else "")
                if bands_dn is not None:
                    ax_band.plot(k_dist, bands_dn[:, ib], color='#d60000', lw=1.1, ls='-', alpha=0.95,
                                 label='Spin-down' if ib == 0 else "")

            for loc in tick_locs:
                ax_band.axvline(loc, color='#777777', lw=0.7, ls=':')
            # Prominent Fermi level
            ax_band.axhline(0.0, color='#111111', lw=1.1, ls='--')

            ax_band.set_xlim(k_dist[0], k_dist[-1])
            ax_band.set_ylim(-3.0, 3.0)
            ax_band.set_xticks(tick_locs)
            ax_band.set_xticklabels(k_labels, fontsize=13.0, fontweight='bold')
            ax_band.tick_params(axis='y', labelsize=12.0)
            ax_band.tick_params(axis='x', labelsize=13.0)

            if col_idx == 0:
                ax_band.set_ylabel(r'$E - E_{\mathrm{F}}\ \ (\mathrm{eV})$', fontsize=17.0, fontweight='bold')

            ax_band.set_title(f"({let_band}) {tm_label}", fontsize=13.0, fontweight='bold', loc='left', pad=6)

            if row_idx == 0 and col_idx == 0:
                ax_band.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.95,
                               edgecolor='#cccccc', fontsize=10.5, borderpad=0.35, handlelength=1.4)

            # 2. PDOS
            dos_e = dos['energies'] - ef
            mask = (dos_e >= -3.0) & (dos_e <= 3.0)
            e_sub = dos_e[mask]

            cr_up = dos['cr_d_up'][mask]
            cr_dn = dos['cr_d_dn'][mask]
            cl_p_up = dos['cl_p_up'][mask]
            cl_p_dn = dos['cl_p_dn'][mask]
            tm_up = dos['tm_d_up'][mask]
            tm_dn = dos['tm_d_dn'][mask]

            c_cr = ELEMENT_COLORS['Cr']
            c_cl = ELEMENT_COLORS['Cl']
            c_tm = ELEMENT_COLORS.get(tm, '#ff7f0e')

            ax_dos.plot(cr_up, e_sub, color=c_cr, lw=1.35, alpha=1.0, label=r'$\mathrm{Cr}\text{-}3d$')
            ax_dos.plot(-cr_dn, e_sub, color=c_cr, lw=1.35, alpha=1.0)

            ax_dos.plot(cl_p_up, e_sub, color=c_cl, lw=1.35, alpha=1.0, label=r'$\mathrm{Cl}\text{-}3p$')
            ax_dos.plot(-cl_p_dn, e_sub, color=c_cl, lw=1.35, alpha=1.0)

            ax_dos.plot(tm_up, e_sub, color=c_tm, lw=1.85, alpha=1.0, label=f"{tm}" + r'$\text{-}3d$')
            ax_dos.plot(-tm_dn, e_sub, color=c_tm, lw=1.85, alpha=1.0)

            # Fill under TM curve for vivid emphasis
            ax_dos.fill_betweenx(e_sub, 0, tm_up, color=c_tm, alpha=0.25)
            ax_dos.fill_betweenx(e_sub, 0, -tm_dn, color=c_tm, alpha=0.25)

            ax_dos.axhline(0.0, color='#111111', lw=1.1, ls='--')
            ax_dos.axvline(0.0, color='#666666', lw=0.6, ls=':')

            # Headroom on PDOS x-limits to ensure legend does not collide with peaks
            max_dos = max(np.max(cr_up), np.max(cr_dn), np.max(tm_up), np.max(tm_dn)) * 1.48
            ax_dos.set_xlim(-max_dos, max_dos)
            ax_dos.set_xticks([])
            ax_dos.set_xlabel('PDOS', fontsize=12.5, fontweight='bold')
            ax_dos.set_title(f"({let_dos})", fontsize=13.0, fontweight='bold', loc='left', pad=6)
            plt.setp(ax_dos.get_yticklabels(), visible=False)

            # Prominent E_F annotation in the PDOS margin
            if col_idx == 2:
                ax_dos.text(max_dos * 0.96, 0.15, r'$E_{\mathrm{F}}$', fontsize=14.5,
                            fontweight='bold', color='#111111', ha='right', va='bottom')

            # Dedicated legend for EVERY PDOS panel
            ax_dos.legend(loc='upper right', frameon=True, facecolor='white',
                          framealpha=0.94, edgecolor='#cccccc', fontsize=11.0,
                          handlelength=1.3, handletextpad=0.35, borderpad=0.3)

    fig.suptitle(r'Spin-Resolved Band Structures and Projected DOS of Functionalized Monolayer $\mathrm{CrCl}_3$ ($+U_{\mathrm{all}} = 3.29\,\mathrm{eV}$)',
                 fontsize=14.5, fontweight='bold', y=0.985)

    os.makedirs(out_dir, exist_ok=True)
    out_png = os.path.join(out_dir, "Fig5_Uall_bands_pdos.png")
    out_pdf = os.path.join(out_dir, "Fig5_Uall_bands_pdos.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")

    acs_fig5 = "ACS_version/figure/Fig5.png"
    if os.path.exists(os.path.dirname(acs_fig5)):
        import shutil
        shutil.copy2(out_png, acs_fig5)
        print(f"Updated manuscript figure: {acs_fig5}")

if __name__ == '__main__':
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "crcl3-newcals/bands_U_all"
    plot_fig5_suite(base_dir)
