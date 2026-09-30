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
    # Fe: Surface S2 = -6.126 eV, Embedded Interstitial = -7.531 eV
    # Co: Surface S1 = -5.141 eV (S2 = -5.064 eV), Embedded = -5.380 eV
    # Ni: Surface S2 = -4.372 eV, Embedded = -2.558 eV (interim Step 7)
    e_surf = [-6.126, -5.141, -4.372]
    e_emb  = [-7.531, -5.380, -2.558]

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
                xy=(x[0] + width/2, -7.531), xytext=(x[0] + 0.1, -8.6),
                arrowprops=dict(arrowstyle='->', color='#922b21', lw=1.2),
                fontsize=9.5, fontweight='bold', color='#922b21', bbox=CARD_STYLE, ha='center')

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
    # Pristine CrCl3:
    #   Hollow (S2): Delta G = +2.071 eV
    #   Top-Cl (S1): Delta G = +1.156 eV
    # Co-Embedded CrCl3:
    #   H_ads: Delta G = +1.341 eV (or +0.670 eV)
    catalysts = [
        ('Pristine $\\mathrm{CrCl}_3$ (Hollow S2)', 2.071, '#e74c3c', '--'),
        ('Pristine $\\mathrm{CrCl}_3$ (Top-Cl S1)', 1.156, '#e67e22', '-.'),
        ('Co-Embedded $\\mathrm{CrCl}_3$ (Hole Pore)', 1.341, '#27ae60', '-'),
        ('Co-Embedded (Reflexion Model)', 0.670, '#16a085', ':')
    ]

    rxn_x = [0.0, 1.0, 2.0]
    rxn_labels = [r'$\mathrm{H}^+ + \mathrm{e}^-$', r'$\mathrm{H}^*$', r'$\frac{1}{2}\mathrm{H}_2$']

    for name, dg, col, lst in catalysts:
        y_vals = [0.0, dg, 0.0]
        # Plot horizontal plateau segments
        for i in range(3):
            ax.hlines(y_vals[i], rxn_x[i] - 0.25, rxn_x[i] + 0.25, color=col, linewidth=2.5, zorder=3)
        # Connect dashed lines
        ax.plot([0.25, 0.75], [0.0, dg], color=col, linestyle=lst, linewidth=1.5, alpha=0.8)
        ax.plot([1.25, 1.75], [dg, 0.0], color=col, linestyle=lst, linewidth=1.5, alpha=0.8)

        # Label intermediate
        ax.annotate(f'{dg:+.2f} eV', xy=(1.0, dg), xytext=(0, 6), textcoords='offset points',
                    ha='center', fontsize=9.5, fontweight='bold', color=col, bbox=CARD_STYLE)

    # Ideal Sabatier benchmark
    ax.axhline(0.0, color='#2c3e50', linestyle='-', linewidth=1.2, zorder=2)
    ax.annotate(r'Ideal Sabatier Optimum ($\Delta G_{\mathrm{H}^*} = 0\,\mathrm{eV}$)', xy=(0.5, 0.0), xytext=(0.5, -0.28),
                fontsize=9.5, fontweight='bold', color='#2c3e50', ha='center')

    ax.set_xticks(rxn_x)
    ax.set_xticklabels(rxn_labels, fontsize=12, fontweight='bold')
    ax.set_ylabel(r'Gibbs Free Energy $\Delta G\ (\mathrm{eV})$', fontsize=12, fontweight='bold')
    ax.set_title(r'(c) HER Reaction Coordinate Diagram ($T = 298.15\,\mathrm{K}$)', fontsize=12.5, fontweight='bold', pad=10)
    ax.set_ylim(-0.5, 2.65)
    ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)

    # Custom legend for panel c
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color=col, lw=2.5, linestyle=lst) for _, _, col, lst in catalysts]
    ax.legend(custom_lines, [c[0] for c in catalysts], loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=9.2)

    # -------------------------------------------------------------
    # PANEL (d): Magnetic Moment & Spin Compensation
    # -------------------------------------------------------------
    ax = axs[1, 1]

    systems = [
        r'Pristine Clean' + '\n' + r'($\mathrm{Cr}_8\mathrm{Cl}_{24}$)',
        r'Pristine + H' + '\n' + r'(Top-Cl)',
        r'Co-Emb Clean' + '\n' + r'($\mathrm{Cr}_8\mathrm{Cl}_{24}\mathrm{Co}$)',
        r'Co-Emb + H' + '\n' + r'(Adsorbed)',
        r'Fe-Emb Clean' + '\n' + r'($\mathrm{Cr}_8\mathrm{Cl}_{24}\mathrm{Fe}$)',
        r'Fe-Emb (S1)' + '\n' + r'(Octahedral)'
    ]
    mag_vals = [24.00, 25.00, 28.14, 24.00, 29.77, 29.97]
    colors = ['#7f8c8d', '#95a5a6', '#3498db', '#2980b9', '#e74c3c', '#c0392b']

    x_d = np.arange(len(systems))
    bars = ax.bar(x_d, mag_vals, width=0.55, color=colors, edgecolor='#2c3e50', linewidth=1.1, zorder=3)

    for bar, val in zip(bars, mag_vals):
        h = bar.get_height()
        ax.annotate(f'{val:.2f}' + r' $\mu_{\mathrm{B}}$', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 6), textcoords='offset points', ha='center', va='bottom',
                    fontsize=9.2, fontweight='bold', bbox=CARD_STYLE)

    ax.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}\ (\mu_{\mathrm{B}})$', fontsize=12, fontweight='bold')
    ax.set_title(r'(d) Total Magnetic Moment across Pristine & Embedded Configurations', fontsize=12.5, fontweight='bold', pad=10)
    ax.set_xticks(x_d)
    ax.set_xticklabels(systems, fontsize=9.5, fontweight='bold')
    ax.set_ylim(0, 36.0)
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
