#!/usr/bin/env python3
"""
plot_embedded_tm_her_comparison.py

Generates publication-quality figures analyzing Single-Atom Transition Metal (TM = Fe, Co, Ni)
Embedding in 2x2 monolayer CrCl3 and its impact on stability and HER electrocatalysis,
incorporating the complete Tier 3 (+U_all) multi-site Hubbard suite.

Panels:
  (a) Surface Adsorption vs Interstitial Pore Embedding Stability across U_Cr and U_all
  (b) Fe Spontaneous Penetration Dynamics (z-position and potential energy relaxation profile)
  (c) HER Gibbs Free Energy Profile (Delta G_H*) vs Ideal Sabatier Benchmark across Tiers
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
from matplotlib.lines import Line2D
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

CARD_STYLE = dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='#cccccc', alpha=0.94, linewidth=0.8)

def get_fe_trajectory():
    """Extracts Fe z-position and potential energy along the S1 relaxation trajectory."""
    outcar_path = os.path.join(BASE_DIR, 'crcl3-2x2-fe_ads-with-U', 'yes_vdw', 'S1', 'OUTCAR')
    if not os.path.exists(outcar_path):
        return None, None, None
    traj = read(outcar_path, index=':')
    steps = np.arange(len(traj))
    z_fe = [atoms.positions[-1, 2] for atoms in traj]
    energies = [atoms.get_potential_energy() for atoms in traj]
    return steps, np.array(z_fe), np.array(energies)

def plot_embedded_analysis():
    fig, axs = plt.subplots(2, 2, figsize=(16.0, 12.5))
    fig.subplots_adjust(hspace=0.34, wspace=0.26)

    # -------------------------------------------------------------
    # PANEL (a): Surface Adsorption vs Interstitial Embedding
    # -------------------------------------------------------------
    ax = axs[0, 0]
    metals = ['Iron (Fe)', 'Cobalt (Co)', 'Nickel (Ni)']
    x = np.arange(len(metals))
    width = 0.20

    # Data under PBE+D3+U_Cr:
    # Fe: Surface S2 = -6.126 eV, Embedded Interstitial = -7.531 eV
    # Co: Surface S1 = -5.141 eV, Embedded Interstitial = -5.380 eV
    # Ni: Surface S2 = -4.372 eV, Embedded Interstitial = -3.914 eV
    e_surf_ucr = [-6.126, -5.141, -4.372]
    e_emb_ucr  = [-7.531, -5.380, -3.914]

    # Data under PBE+D3+U_all:
    # Fe: Surface clean (sunken) = -6.643 eV, Embedded = -6.487 eV
    # Co: Surface clean (S3) = -3.279 eV, Embedded = -5.008 eV
    # Ni: Surface clean (sunken) = -2.979 eV, Embedded = -3.484 eV
    e_surf_uall = [-6.643, -3.279, -2.979]
    e_emb_uall  = [-6.487, -5.008, -3.484]

    b1 = ax.bar(x - 1.5*width, e_surf_ucr, width, label='Surface ($+U_{\\mathrm{Cr}}$)', color='#5dade2', edgecolor='#1b4f72', linewidth=1.1, zorder=3)
    b2 = ax.bar(x - 0.5*width, e_emb_ucr,  width, label='Embedded ($+U_{\\mathrm{Cr}}$)', color='#2980b9', edgecolor='#1b4f72', linewidth=1.1, zorder=3)
    b3 = ax.bar(x + 0.5*width, e_surf_uall, width, label='Surface ($+U_{\\mathrm{all}}$)', color='#f5b041', edgecolor='#935116', linewidth=1.1, zorder=3)
    b4 = ax.bar(x + 1.5*width, e_emb_uall,  width, label='Embedded ($+U_{\\mathrm{all}}$)', color='#e67e22', edgecolor='#935116', linewidth=1.1, zorder=3)

    for bars in [b1, b2, b3, b4]:
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, -12), textcoords='offset points', ha='center', va='top',
                        fontsize=7.8, fontweight='bold', bbox=CARD_STYLE)

    ax.set_ylabel(r'$\Delta E_{\mathrm{bind}} = E_{\mathrm{tot}} - E_{\mathrm{clean}} - E_{\mathrm{TM}}\ (\mathrm{eV})$', fontsize=11.5, fontweight='bold')
    ax.set_title(r'(a) Surface Adsorption vs. Interstitial Pore Embedding across Tiers', fontsize=12.2, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(metals, fontsize=10.5, fontweight='bold')
    ax.set_ylim(-9.4, -1.0)
    ax.yaxis.set_major_locator(MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
    ax.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.6)

    # -------------------------------------------------------------
    # PANEL (b): Fe Spontaneous Penetration Dynamics
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    steps, z_fe, energies = get_fe_trajectory()

    if steps is not None:
        color_z = '#27ae60'
        color_e = '#8e44ad'

        ax2 = ax_b.twinx()

        l1, = ax_b.plot(steps, z_fe, color=color_z, marker='o', markersize=4.5, linewidth=2.0, label=r'Fe $z$-Coordinate ($\mathrm{\AA}$)', zorder=4)
        l2, = ax2.plot(steps, energies, color=color_e, marker='s', markersize=4.5, linewidth=2.0, linestyle='--', label=r'Total Energy $E_0$ (eV)', zorder=3)

        top_cl_z = 11.48
        cr_layer_z = 10.09
        ax_b.axhline(top_cl_z, color='#7f8c8d', linestyle=':', linewidth=1.2, label=r'Top Cl Plane ($z \approx 11.48\,\mathrm{\AA}$)')
        ax_b.axhline(cr_layer_z, color='#d35400', linestyle='-.', linewidth=1.2, label=r'Cr Monolayer Midplane ($z \approx 10.09\,\mathrm{\AA}$)')

        ax_b.set_xlabel('Ionic Relaxation Step (S1 Initial Top-Cl Setup)', fontsize=11.5, fontweight='bold')
        ax_b.set_ylabel(r'Fe Vertical Position $z\ (\mathrm{\AA})$', color=color_z, fontsize=12, fontweight='bold')
        ax2.set_ylabel(r'Total Energy $E_0\ (\mathrm{eV})$', color=color_e, fontsize=12, fontweight='bold')

        ax_b.tick_params(axis='y', labelcolor=color_z)
        ax2.tick_params(axis='y', labelcolor=color_e)

        ax_b.set_title(r'(b) Spontaneous Fe Interstitial Pore Penetration Dynamics', fontsize=12.2, fontweight='bold', pad=10)
        ax_b.set_ylim(9.5, 13.5)
        ax2.set_ylim(-155.5, -151.0)

        ax_b.annotate('Initial Top-Cl Perch\n' + r'($z = 12.95\,\mathrm{\AA}$)', xy=(0, 12.95), xytext=(5, 13.1),
                      arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.2),
                      fontsize=8.5, fontweight='bold', bbox=CARD_STYLE)

        ax_b.annotate('Pore Traversal\n' + r'(Breaking Cl triangle)', xy=(20, 11.39), xytext=(22, 12.1),
                      arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.2),
                      fontsize=8.5, fontweight='bold', bbox=CARD_STYLE)

        ax_b.annotate('Octahedral Core Embedding\n' + r'($z = 10.27\,\mathrm{\AA}$, $\Delta E = -7.53\,\mathrm{eV}$)', xy=(49, 10.27), xytext=(22, 9.8),
                      arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.2),
                      fontsize=8.5, fontweight='bold', bbox=CARD_STYLE)

        lines = [l1, l2]
        labels_b = [l.get_label() for l in lines]
        ax_b.legend(lines, labels_b, loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=9.0)

    # -------------------------------------------------------------
    # PANEL (c): HER Free Energy Diagram (Delta_G_H*)
    # -------------------------------------------------------------
    ax_c = axs[1, 0]

    catalysts = [
        (r'Co (ads) $+U_{\mathrm{all}}$ (Summit)', 0.065, '#1e8449', '-', 3.2),
        (r'Co (ads) $+U_{\mathrm{Cr}}$',          -0.069, '#27ae60', '--', 2.2),
        (r'Ni (emb) $+U_{\mathrm{all}}$',          1.024, '#8e44ad', '-', 2.2),
        (r'Pristine $\mathrm{CrCl}_3$ ($S_1$)',     1.124, '#e67e22', '-.', 2.0),
        (r'Co (emb) $+U_{\mathrm{all}}$',          1.389, '#d35400', '-', 2.2),
        (r'Fe (emb) $+U_{\mathrm{all}}$',          1.821, '#c0392b', '-', 2.2),
        (r'Fe (ads) $+U_{\mathrm{all}}$ (Extruded)', 1.837, '#78281f', '-', 2.2),
    ]

    rxn_x = [0.0, 1.0, 2.0]
    rxn_labels = [r'$\mathrm{H}^+ + \mathrm{e}^-$', r'$\mathrm{H}^*$', r'$\frac{1}{2}\mathrm{H}_2$']

    ax_c.axhspan(-0.15, 0.20, color='#2ecc71', alpha=0.18, label=r'Optimal Sabatier Window ($|\Delta G_{\mathrm{H}^*}| \leq 0.15\,\mathrm{eV}$)', zorder=1)
    ax_c.axhline(-0.09, color='#17202a', linestyle=':', linewidth=1.2, label=r'$\mathrm{Pt(111)}\ (\Delta G = -0.09\,\mathrm{eV})$', zorder=2)
    ax_c.axhline(0.00, color='#27ae60', linestyle='--', linewidth=1.1, zorder=2)

    for name, dg, col, lst, lw in catalysts:
        y_vals = [0.0, dg, 0.0]
        for i in range(3):
            ax_c.hlines(y_vals[i], rxn_x[i] - 0.22, rxn_x[i] + 0.22, color=col, linewidth=lw+0.8, zorder=4)
        ax_c.plot([0.22, 0.78], [0.0, dg], color=col, linestyle=lst, linewidth=lw, alpha=0.85, zorder=3)
        ax_c.plot([1.22, 1.78], [dg, 0.0], color=col, linestyle=lst, linewidth=lw, alpha=0.85, zorder=3)

        y_text_off = 8 if dg >= 0 else -16
        va_align = 'bottom' if dg >= 0 else 'top'
        ax_c.annotate(f'{dg:+.2f} eV', xy=(1.0, dg), xytext=(0, y_text_off), textcoords='offset points',
                      ha='center', va=va_align, fontsize=8.6, fontweight='bold', color=col, bbox=CARD_STYLE, zorder=5)

    ax_c.set_xticks(rxn_x)
    ax_c.set_xticklabels(rxn_labels, fontsize=12, fontweight='bold')
    ax_c.set_ylabel(r'Gibbs Free Energy $\Delta G_{\mathrm{H}^*}\ (\mathrm{eV})$', fontsize=12, fontweight='bold')
    ax_c.set_title(r'(c) HER Free Energy Reaction Profiles across Tiers', fontsize=12.2, fontweight='bold', pad=10)
    ax_c.set_ylim(-0.45, 2.35)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)

    custom_lines = [Line2D([0], [0], color=col, lw=lw, linestyle=lst) for _, _, col, lst, lw in catalysts]
    custom_lines.append(Line2D([0], [0], color='#17202a', lw=1.2, linestyle=':'))
    labels_c = [c[0] for c in catalysts] + [r'$\mathrm{Pt(111)}\ (-0.09\,\mathrm{eV})$']
    ax_c.legend(custom_lines, labels_c, loc='upper left', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.2)

    # -------------------------------------------------------------
    # PANEL (d): Magnetic Moment across Platforms & Tiers
    # -------------------------------------------------------------
    ax_d = axs[1, 1]

    systems_d = [
        r'Pristine' + '\n' + r'Clean',
        r'Pristine' + '\n' + r'+ H',
        r'Co-Emb' + '\n' + r'Clean',
        r'Co-Emb' + '\n' + r'+ H',
        r'Fe-Emb' + '\n' + r'Clean',
        r'Fe-Emb' + '\n' + r'+ H',
        r'Ni-Emb' + '\n' + r'Clean',
        r'Ni-Emb' + '\n' + r'+ H',
        r'Co-Ads' + '\n' + r'Clean',
        r'Co-Ads' + '\n' + r'+ H'
    ]
    # Converged cell magnetic moments under +U_all:
    # Pristine: 24.0, +H: 25.0
    # Co-emb clean: 29.0, +H: 26.0
    # Fe-emb clean: 30.0, +H: 29.0
    # Ni-emb clean: 28.0, +H: 27.0
    # Co-ads clean: 27.0, +H: 28.0
    mag_vals = [24.0, 25.0, 29.0, 26.0, 30.0, 29.0, 28.0, 27.0, 27.0, 28.0]
    colors_d = ['#7f8c8d', '#95a5a6', '#2980b9', '#1b4f72', '#c0392b', '#922b21', '#8e44ad', '#6c3483', '#27ae60', '#1e8449']

    x_d = np.arange(len(systems_d))
    bars_d = ax_d.bar(x_d, mag_vals, width=0.55, color=colors_d, edgecolor='#2c3e50', linewidth=1.1, zorder=3)

    for bar, val in zip(bars_d, mag_vals):
        h = bar.get_height()
        ax_d.annotate(f'{val:.1f}' + r' $\mu_{\mathrm{B}}$', xy=(bar.get_x() + bar.get_width()/2, h),
                      xytext=(0, 6), textcoords='offset points', ha='center', va='bottom',
                      fontsize=8.0, fontweight='bold', bbox=CARD_STYLE, zorder=5)

    ax_d.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}\ (\mu_{\mathrm{B}})$', fontsize=12, fontweight='bold')
    ax_d.set_title(r'(d) Total Magnetic Moment across Platforms under $+U_{\mathrm{all}}$', fontsize=12.2, fontweight='bold', pad=10)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(systems_d, fontsize=8.4, fontweight='bold')
    ax_d.set_ylim(0, 38.0)
    ax_d.yaxis.set_major_locator(MultipleLocator(5.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(1.0))
    ax_d.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)

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
