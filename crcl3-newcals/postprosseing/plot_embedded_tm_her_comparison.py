#!/usr/bin/env python3
"""
plot_embedded_tm_her_comparison.py

Generates publication-quality figures analyzing Single-Atom Transition Metal (TM = Fe, Co, Ni)
Embedding in 2x2 monolayer CrCl3 and its impact on stability and HER electrocatalysis.

Panels:
  (a) Surface Adsorption vs Interstitial Pore Embedding Stability (Fe, Co, Ni)
  (b) Fe Spontaneous Penetration Dynamics (z-position and potential energy relaxation profile)
  (c) HER Gibbs Free Energy Profile (Delta_G_H*) vs Ideal Sabatier Benchmark
  (d) Magnetic Moment and Spin Compensation (Clean vs TM-Embedded vs H-Adsorbed)

Strictly adheres to GEMINI.md Publication Plotting Anti-Collision Policy:
  - Zero-overlap mandate
  - Adaptive headroom
  - Smart cards with semi-transparent background
  - Lowest-density legend placement
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from ase.io import read

# Styling
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

CARD_STYLE = dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor='#cccccc', alpha=0.92, linewidth=0.8)

def get_fe_trajectory():
    """Extracts Fe z-position and potential energy along the S1 relaxation trajectory."""
    outcar_path = os.path.join(BASE_DIR, 'crcl3-2x2-fe_ads-with-U', 'yes_vdw', 'S1', 'OUTCAR')
    if not os.path.exists(outcar_path):
        return None, None
    traj = read(outcar_path, index=':')
    steps = np.arange(len(traj))
    z_fe = [atoms.positions[-1, 2] for atoms in traj]
    energies = [atoms.get_potential_energy() for atoms in traj]
    return steps, np.array(z_fe), np.array(energies)

def plot_embedded_analysis():
    fig, axs = plt.subplots(2, 2, figsize=(15.5, 12.0))
    fig.subplots_adjust(hspace=0.32, wspace=0.26)

    # -------------------------------------------------------------
    # PANEL (a): Surface Adsorption vs Interstitial Embedding
    # -------------------------------------------------------------
    ax = axs[0, 0]
    metals = ['Iron (Fe)', 'Cobalt (Co)', 'Nickel (Ni)']
    x = np.arange(len(metals))
    width = 0.32

    # Data under PBE+D3+U:
    # Fe: Surface S2 = -6.126 eV, Embedded Interstitial = -7.531 eV (Pore favored by 1.41 eV)
    # Co: Surface S1 = -5.141 eV, Embedded Interstitial = -5.380 eV (Pore favored by 0.24 eV)
    # Ni: Surface S2 = -4.372 eV, Embedded Interstitial = -3.914 eV (Surface favored by 0.46 eV)
    e_surf = [-6.126, -5.141, -4.372]
    e_emb  = [-7.531, -5.380, -3.914]

    b1 = ax.bar(x - width/2, e_surf, width, label='Surface Adsorption (Ground State)', color='#3498db', edgecolor='#1a5276', linewidth=1.2, zorder=3)
    b2 = ax.bar(x + width/2, e_emb,  width, label='Interstitial Pore Embedding', color='#e74c3c', edgecolor='#922b21', linewidth=1.2, zorder=3)

    # Annotations
    for bar in b1:
        h = bar.get_height()
        ax.annotate(f'{h:.2f} eV', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, -14), textcoords='offset points', ha='center', va='top',
                    fontsize=9.5, fontweight='bold', bbox=CARD_STYLE)

    for bar in b2:
        h = bar.get_height()
        ax.annotate(f'{h:.2f} eV', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, -14), textcoords='offset points', ha='center', va='top',
                    fontsize=9.5, fontweight='bold', bbox=CARD_STYLE)

    # Delta Delta E markers
    ax.annotate(r'$\Delta\Delta E = -1.41\,\mathrm{eV}$' + '\n(Pore Favored)',
                xy=(x[0] + width/2, -7.531), xytext=(x[0] + 0.05, -8.65),
                arrowprops=dict(arrowstyle='->', color='#922b21', lw=1.2),
                fontsize=9.0, fontweight='bold', color='#922b21', bbox=CARD_STYLE, ha='center')

    ax.annotate(r'$\Delta\Delta E = -0.24\,\mathrm{eV}$' + '\n(Pore Favored)',
                xy=(x[1] + width/2, -5.380), xytext=(x[1] + 0.05, -6.65),
                arrowprops=dict(arrowstyle='->', color='#922b21', lw=1.2),
                fontsize=9.0, fontweight='bold', color='#922b21', bbox=CARD_STYLE, ha='center')

    ax.annotate(r'$\Delta\Delta E = +0.46\,\mathrm{eV}$' + '\n(Surface Favored)',
                xy=(x[2] - width/2, -4.372), xytext=(x[2] + 0.05, -5.55),
                arrowprops=dict(arrowstyle='->', color='#1a5276', lw=1.2),
                fontsize=9.0, fontweight='bold', color='#1a5276', bbox=CARD_STYLE, ha='center')

    ax.set_ylabel(r'$\Delta E_{\mathrm{bind}} = E_{\mathrm{tot}} - E_{\mathrm{clean}}\ (\mathrm{eV})$', fontsize=12, fontweight='bold')
    ax.set_title(r'(a) Surface Adsorption vs. Interstitial Pore Embedding ($U_{\mathrm{Cr}}=3.29\,\mathrm{eV}$)', fontsize=12.5, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(metals, fontsize=11, fontweight='bold')
    ax.set_ylim(-9.4, -1.0)
    ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=10)

    # -------------------------------------------------------------
    # PANEL (b): Fe Spontaneous Penetration Dynamics
    # -------------------------------------------------------------
    ax = axs[0, 1]
    steps, z_fe, energies = get_fe_trajectory()

    if steps is not None:
        color_z = '#27ae60'
        color_e = '#8e44ad'

        ax2 = ax.twinx()

        l1, = ax.plot(steps, z_fe, color=color_z, marker='o', markersize=4.5, linewidth=2.0, label=r'Fe $z$-Coordinate ($\mathrm{\AA}$)', zorder=4)
        l2, = ax2.plot(steps, energies, color=color_e, marker='s', markersize=4.5, linewidth=2.0, linestyle='--', label=r'Total Energy $E_0$ (eV)', zorder=3)

        # Reference horizontal lines
        top_cl_z = 11.48
        cr_layer_z = 10.09
        ax.axhline(top_cl_z, color='#7f8c8d', linestyle=':', linewidth=1.2, label=r'Top Cl Plane ($z \approx 11.48\,\mathrm{\AA}$)')
        ax.axhline(cr_layer_z, color='#d35400', linestyle='-.', linewidth=1.2, label=r'Cr Monolayer Midplane ($z \approx 10.09\,\mathrm{\AA}$)')

        ax.set_xlabel('Ionic Relaxation Step (S1 Initial Top-Cl Setup)', fontsize=11.5, fontweight='bold')
        ax.set_ylabel(r'Fe Vertical Position $z\ (\mathrm{\AA})$', color=color_z, fontsize=12, fontweight='bold')
        ax2.set_ylabel(r'Total Energy $E_0\ (\mathrm{eV})$', color=color_e, fontsize=12, fontweight='bold')

        ax.tick_params(axis='y', labelcolor=color_z)
        ax2.tick_params(axis='y', labelcolor=color_e)

        ax.set_title(r'(b) Spontaneous Fe Interstitial Pore Penetration Dynamics', fontsize=12.5, fontweight='bold', pad=10)
        ax.set_ylim(9.5, 13.5)
        ax2.set_ylim(-155.5, -151.0)

        # Callouts
        ax.annotate('Initial Top-Cl Perch\n' + r'($z = 12.95\,\mathrm{\AA}$)', xy=(0, 12.95), xytext=(6, 13.1),
                    arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.2),
                    fontsize=9, fontweight='bold', bbox=CARD_STYLE)

        ax.annotate('Pore Traversal\n' + r'(Breaking Cl triangle)', xy=(20, 11.39), xytext=(22, 12.1),
                    arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.2),
                    fontsize=9, fontweight='bold', bbox=CARD_STYLE)

        ax.annotate('Octahedral Core Embedding\n' + r'($z = 10.27\,\mathrm{\AA}$, $\Delta E = -7.53\,\mathrm{eV}$)', xy=(49, 10.27), xytext=(25, 9.8),
                    arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.2),
                    fontsize=9, fontweight='bold', bbox=CARD_STYLE)

        lines = [l1, l2]
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=9.5)

    # -------------------------------------------------------------
    # PANEL (c): HER Free Energy Diagram (Delta_G_H*)
    # -------------------------------------------------------------
    ax = axs[1, 0]

    # Reaction coordinate steps: H+ + e- (0 eV) -> H* (Delta G) -> 1/2 H2 (0 eV)
    # Complete suite under PBE+D3+U with exact Caique thermodynamic corrections:
    # Co (ads): -0.069 eV (Sabatier summit benchmark)
    # Ni (emb): +0.821 eV
    # Fe (emb): +1.114 eV
    # Pristine S1: +1.124 eV
    # Co (emb): +1.375 eV
    catalysts = [
        (r'Co (ads) Optimal Benchmark', -0.069, '#1e8449', '-', 3.0),
        (r'Ni (emb) PBE+D3+$U$', 0.821, '#8e44ad', '-', 2.2),
        (r'Fe (emb) PBE+D3+$U$', 1.114, '#2980b9', '-', 2.2),
        (r'Pristine $\mathrm{CrCl}_3$ ($S_1$ Top-Cl)', 1.124, '#e67e22', '-.', 2.0),
        (r'Co (emb) PBE+D3+$U$', 1.375, '#c0392b', '-', 2.2),
    ]

    rxn_x = [0.0, 1.0, 2.0]
    rxn_labels = [r'$\mathrm{H}^+ + \mathrm{e}^-$', r'$\mathrm{H}^*$', r'$\frac{1}{2}\mathrm{H}_2$']

    # Optimal window shading and Pt(111) benchmark
    ax.axhspan(-0.15, 0.20, color='#2ecc71', alpha=0.18, label=r'Optimal Sabatier Window ($|\Delta G_{\mathrm{H}^*}| \leq 0.15\,\mathrm{eV}$)', zorder=1)
    ax.axhline(-0.09, color='#17202a', linestyle=':', linewidth=1.2, label=r'$\mathrm{Pt(111)}\ (\Delta G = -0.09\,\mathrm{eV})$', zorder=2)
    ax.axhline(0.00, color='#27ae60', linestyle='--', linewidth=1.1, zorder=2)

    for name, dg, col, lst, lw in catalysts:
        y_vals = [0.0, dg, 0.0]
        # Plot horizontal plateau segments
        for i in range(3):
            ax.hlines(y_vals[i], rxn_x[i] - 0.22, rxn_x[i] + 0.22, color=col, linewidth=lw+0.8, zorder=4)
        # Connect lines
        ax.plot([0.22, 0.78], [0.0, dg], color=col, linestyle=lst, linewidth=lw, alpha=0.85, zorder=3)
        ax.plot([1.22, 1.78], [dg, 0.0], color=col, linestyle=lst, linewidth=lw, alpha=0.85, zorder=3)

        # Label intermediate
        y_text_off = 8 if dg >= 0 else -18
        va_align = 'bottom' if dg >= 0 else 'top'
        ax.annotate(f'{dg:+.2f} eV', xy=(1.0, dg), xytext=(0, y_text_off), textcoords='offset points',
                    ha='center', va=va_align, fontsize=9.0, fontweight='bold', color=col, bbox=CARD_STYLE, zorder=5)

    ax.set_xticks(rxn_x)
    ax.set_xticklabels(rxn_labels, fontsize=12, fontweight='bold')
    ax.set_ylabel(r'Gibbs Free Energy $\Delta G_{\mathrm{H}^*}\ (\mathrm{eV})$', fontsize=12, fontweight='bold')
    ax.set_title(r'(c) HER Free Energy Reaction Profiles ($T = 298.15\,\mathrm{K}$)', fontsize=12.5, fontweight='bold', pad=10)
    ax.set_ylim(-0.45, 2.05)
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)

    # Custom legend for panel c
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color=col, lw=lw, linestyle=lst) for _, _, col, lst, lw in catalysts]
    custom_lines.append(Line2D([0], [0], color='#17202a', lw=1.2, linestyle=':'))
    labels_c = [c[0] for c in catalysts] + [r'$\mathrm{Pt(111)}\ (-0.09\,\mathrm{eV})$']
    ax.legend(custom_lines, labels_c, loc='upper left', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.6)

    # -------------------------------------------------------------
    # PANEL (d): Magnetic Moment & Spin Compensation
    # -------------------------------------------------------------
    ax = axs[1, 1]

    systems = [
        r'Pristine' + '\n' + r'Clean',
        r'Pristine' + '\n' + r'+ H',
        r'Co-Emb' + '\n' + r'Clean',
        r'Co-Emb' + '\n' + r'+ H',
        r'Fe-Emb' + '\n' + r'Clean',
        r'Fe-Emb' + '\n' + r'+ H',
        r'Ni-Emb' + '\n' + r'Clean',
        r'Ni-Emb' + '\n' + r'+ H'
    ]
    mag_vals = [24.00, 25.00, 28.14, 24.00, 29.77, 23.00, 24.00, 25.00]
    colors = ['#7f8c8d', '#95a5a6', '#2980b9', '#1b4f72', '#c0392b', '#922b21', '#8e44ad', '#6c3483']

    x_d = np.arange(len(systems))
    bars = ax.bar(x_d, mag_vals, width=0.55, color=colors, edgecolor='#2c3e50', linewidth=1.1, zorder=3)

    for bar, val in zip(bars, mag_vals):
        h = bar.get_height()
        ax.annotate(f'{val:.1f}' + r' $\mu_{\mathrm{B}}$', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 6), textcoords='offset points', ha='center', va='bottom',
                    fontsize=8.5, fontweight='bold', bbox=CARD_STYLE, zorder=5)

    ax.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}\ (\mu_{\mathrm{B}})$', fontsize=12, fontweight='bold')
    ax.set_title(r'(d) Total Magnetic Moment across Pristine & Embedded Platforms', fontsize=12.5, fontweight='bold', pad=10)
    ax.set_xticks(x_d)
    ax.set_xticklabels(systems, fontsize=9.0, fontweight='bold')
    ax.set_ylim(0, 37.0)
    ax.yaxis.set_major_locator(MultipleLocator(5.0))
    ax.yaxis.set_minor_locator(MultipleLocator(1.0))
    ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)

    # Save outputs
    out_png = os.path.join(SCRIPT_DIR, 'embedded_tm_her_analysis_multipanel.png')
    out_pdf = os.path.join(SCRIPT_DIR, 'embedded_tm_her_analysis_multipanel.pdf')
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    print(f"[OK] Saved {out_png}")
    print(f"[OK] Saved {out_pdf}")

if __name__ == '__main__':
    plot_embedded_analysis()
