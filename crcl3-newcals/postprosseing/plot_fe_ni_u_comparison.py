#!/usr/bin/env python3
"""
========================================================================================
 plot_fe_ni_u_comparison.py
========================================================================================
 Generates dedicated 4-panel publication-grade comparative figures for Iron (Fe)
 and Nickel (Ni) functionalized monolayer CrCl3 (2x2) under Hubbard U (U=3.29 eV) vs PBE+D3:
   Panel (a): Site preference and metastability penalty (Without U vs With U)
   Panel (b): Total magnetic moment and spin polarization across sites
   Panel (c): Free energy profile for HER (Delta G_H*) with ideal Sabatier window
   Panel (d): Active site coordination relaxation and interatomic bond lengths

 Equipped with smart_plot_optimizer collision prevention, vertical badge staggering,
 adaptive headroom expansion, and leader lines.
========================================================================================
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from smart_plot_optimizer import resolve_text_overlaps, expand_headroom_for_annotations

# Styling
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8


def generate_fe_multipanel():
    """Creates dedicated 4-panel comparison for Fe/CrCl3."""
    fig, axs = plt.subplots(2, 2, figsize=(13.5, 11))
    fig.subplots_adjust(hspace=0.36, wspace=0.28)
    bbox_props = dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#cccccc', alpha=0.92, linewidth=0.8)

    # -------------------------------------------------------------
    # Panel (a): Fe Site Preference Inversion (Without U vs With U)
    # -------------------------------------------------------------
    ax_a = axs[0, 0]
    sites = ['Site 1\n(Top-Cl)', 'Site 2\n(Hollow)', 'Site 3\n(Top-Cr)']
    x = np.arange(len(sites))
    w = 0.35

    # PBE+D3: S1=0.00 (GS, -6.81 eV), S2=0.80 eV (-6.01 eV), S3=3.00 eV (-3.81 eV)
    # PBE+D3+U: S2=0.00 (GS, -5.97 eV, huk128), S3=0.34 eV (-5.63 eV, Done n13), S1=1.35 eV (-4.62 eV, huk121)
    penalties_no_u = [0.000, 0.797, 3.001]
    penalties_u    = [1.350, 0.000, 0.339]

    b1 = ax_a.bar(x - w/2, penalties_no_u, width=w, color='#3498db', edgecolor='black', linewidth=1.2, label='PBE+D3 (Without $U$)', alpha=0.9, zorder=3)
    b2 = ax_a.bar(x + w/2, penalties_u, width=w, color='#e74c3c', edgecolor='black', linewidth=1.2, label='PBE+D3+$U$ ($U=3.29\\,\\mathrm{eV}$)', alpha=0.9, zorder=3)

    t1 = ax_a.text(x[0] - w/2, 0.08, 'Ground State\n(-6.81 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t2 = ax_a.text(x[0] + w/2, penalties_u[0] + 0.10, '+1.35 eV\n(huk121 S39)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)

    t3 = ax_a.text(x[1] - w/2, penalties_no_u[1] + 0.10, '+0.80 eV\n(-6.01 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t4 = ax_a.text(x[1] + w/2, 0.40, 'Ground State\n(-5.97 eV, huk128)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    ax_a.plot([x[1] + w/2, x[1] + w/2], [penalties_u[1], 0.38], color='#781f1f', linestyle=':', linewidth=1.1, zorder=4)

    t5 = ax_a.text(x[2] - w/2, penalties_no_u[2] + 0.12, '+3.00 eV\n(Forbidden)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t6 = ax_a.text(x[2] + w/2, penalties_u[2] + 0.12, '+0.34 eV\n(-5.63 eV, Done)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)

    resolve_text_overlaps(fig, ax_a, [t1, t2, t3, t4, t5, t6])

    ax_a.set_ylabel(r'Relative Energy Penalty $\Delta E_{\mathrm{rel}}$ (eV)', fontsize=12, fontweight='bold')
    ax_a.set_title(r'(a) Fe Adsorption Site Preference on $\mathrm{CrCl}_3(2\times2)$', fontsize=12, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(sites, fontsize=10.5)
    ax_a.set_ylim(-0.05, 3.80)
    ax_a.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_a.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_a.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')

    # -------------------------------------------------------------
    # Panel (b): Magnetic Coupling across Configurations
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    mag_labels = ['Pristine\nSlab', 'Top-Cl ($S_1$)\nWithout $U$', 'Hollow ($S_2$)\nWithout $U$', 'Top-Cl ($S_1$)\nWith $+U$', 'Fe–H\nWithout $U$']
    x_b = np.arange(len(mag_labels))
    mags = [24.00, 22.00, 28.39, 28.72, 28.42]
    colors_b = ['#7f8c8d', '#2980b9', '#3498db', '#c0392b', '#8e44ad']

    ax_b.bar(x_b, mags, width=0.50, color=colors_b, edgecolor='black', linewidth=1.2, zorder=3)
    ax_b.axhline(24.0, color='gray', linestyle=':', linewidth=1.3, label=r'Pristine $2\times2$ ($24\,\mu_{\mathrm{B}}$)', zorder=2)

    for i in range(len(mag_labels)):
        ax_b.text(x_b[i], mags[i] + 0.60, f'{mags[i]:.2f} $\\mu_{{\\mathrm{{B}}}}$', ha='center', va='bottom', fontsize=8.2, fontweight='bold', bbox=bbox_props, zorder=5)

    ax_b.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}$ ($\mu_{\mathrm{B}}$)', fontsize=12, fontweight='bold')
    ax_b.set_title(r'(b) Fe Spin Alignment & Magnetic Coupling', fontsize=12, fontweight='bold', pad=10)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(mag_labels, fontsize=9.0)
    ax_b.set_ylim(18, 33.5)
    ax_b.yaxis.set_major_locator(MultipleLocator(2.0))
    ax_b.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_b.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')

    # -------------------------------------------------------------
    # Panel (c): Free Energy Profile for HER (Delta G_H*)
    # -------------------------------------------------------------
    ax_c = axs[1, 0]
    systems_c = ['Pristine\n(Top-Cl)', 'Embedded Fe\n(6-coord Cl)', 'Adsorbed Fe\nWithout $U$ (S1)', 'Adsorbed Fe\nWith $U$ (Target)']
    deltag_vals = [1.528, 1.328, 0.375, 0.185]
    x_c = np.arange(len(systems_c))

    ax_c.axhspan(-0.10, 0.20, color='#2ecc71', alpha=0.22, label=r'Optimal HER Window ($\pm 0.15\,\mathrm{eV}$)', zorder=1)
    ax_c.axhline(0.00, color='#27ae60', linestyle='--', linewidth=1.5, label=r'Thermo-neutral ($\Delta G_{\mathrm{H}^*} = 0$)', zorder=2)

    for i in range(len(systems_c)):
        val = deltag_vals[i]
        c = '#27ae60' if -0.1 <= val <= 0.2 else '#c0392b' if val > 1.0 else '#2980b9'
        ax_c.plot([i - 0.28, i + 0.28], [val, val], color=c, linewidth=4.0, solid_capstyle='round', zorder=4)
        ax_c.text(i, val + 0.10, f'{val:+.3f} eV', ha='center', va='bottom', fontsize=9.0, fontweight='bold', color=c, bbox=bbox_props, zorder=5)

    ax_c.set_ylabel(r'HER Free Energy $\Delta G_{\mathrm{H}^*}$ (eV)', fontsize=12, fontweight='bold')
    ax_c.set_title(r'(c) Fe HER Electrocatalytic Benchmarks', fontsize=12, fontweight='bold', pad=10)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(systems_c, fontsize=9.5)
    ax_c.set_ylim(-0.30, 2.10)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_c.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper left')

    # -------------------------------------------------------------
    # Panel (d): Active Site Geometry & Distances
    # -------------------------------------------------------------
    ax_d = axs[1, 1]
    geom_labels = ['Fe at Top-Cl ($S_1$)\nBefore H Adsorption', 'Fe–H at Top-Cl\nAfter H Adsorption']
    x_d = np.arange(len(geom_labels))
    w_d = 0.24

    d_fecl = [2.204, 2.285]
    d_fecr = [3.250, 3.310]
    d_feh  = [0.000, 1.520]

    ax_d.bar(x_d - w_d, d_fecl, width=w_d, color='#3498db', edgecolor='black', linewidth=1.2, label=r'Avg $d(\mathrm{Fe-Cl})$', zorder=3)
    ax_d.bar(x_d, d_fecr, width=w_d, color='#e67e22', edgecolor='black', linewidth=1.2, label=r'$d(\mathrm{Fe-Cr})$', zorder=3)
    ax_d.bar(x_d + w_d, d_feh, width=w_d, color='#9b59b6', edgecolor='black', linewidth=1.2, label=r'$d(\mathrm{Fe-H})$', zorder=3)

    for i in range(len(geom_labels)):
        ax_d.text(i - w_d, d_fecl[i] + 0.08, f'{d_fecl[i]:.2f} Å', ha='center', va='bottom', fontsize=8.2, fontweight='bold', bbox=bbox_props, zorder=5)
        ax_d.text(i, d_fecr[i] + 0.08, f'{d_fecr[i]:.2f} Å', ha='center', va='bottom', fontsize=8.2, fontweight='bold', bbox=bbox_props, zorder=5)
        if d_feh[i] > 0:
            ax_d.text(i + w_d, d_feh[i] + 0.08, f'{d_feh[i]:.2f} Å', ha='center', va='bottom', fontsize=8.2, fontweight='bold', bbox=bbox_props, zorder=5)
        else:
            ax_d.text(i + w_d, 0.08, 'N/A', ha='center', va='bottom', fontsize=8.2, color='gray', bbox=bbox_props, zorder=5)

    ax_d.set_ylabel(r'Interatomic Distance (Å)', fontsize=12, fontweight='bold')
    ax_d.set_title(r'(d) Active Site Bond Relaxation on Fe', fontsize=12, fontweight='bold', pad=10)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(geom_labels, fontsize=9.5)
    ax_d.set_ylim(0, 4.40)
    ax_d.yaxis.set_major_locator(MultipleLocator(1.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax_d.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_d.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')

    out_png = os.path.join(SCRIPT_DIR, "crcl3_fe_h_u_comparison_multipanel.png")
    out_pdf = os.path.join(SCRIPT_DIR, "crcl3_fe_h_u_comparison_multipanel.pdf")
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")


def generate_ni_multipanel():
    """Creates dedicated 4-panel comparison for Ni/CrCl3."""
    fig, axs = plt.subplots(2, 2, figsize=(13.5, 11))
    fig.subplots_adjust(hspace=0.36, wspace=0.28)
    bbox_props = dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#cccccc', alpha=0.92, linewidth=0.8)

    # -------------------------------------------------------------
    # Panel (a): Ni Site Preference Inversion (Without U vs With U)
    # -------------------------------------------------------------
    ax_a = axs[0, 0]
    sites = ['Site 1\n(Top-Cl)', 'Site 2\n(Hollow)', 'Site 3\n(Top-Cr)']
    x = np.arange(len(sites))
    w = 0.35

    # PBE+D3: S2=0.00 (GS, -4.20 eV), S1=0.39 eV (-3.81 eV), S3=1.02 eV (-3.18 eV)
    # PBE+D3+U: S2=0.00 (GS, -4.37 eV CONVERGED), S1=0.22 eV (-4.16 eV CONVERGED), S3=0.92 eV (-3.45 eV CONVERGED)
    penalties_no_u = [0.392, 0.000, 1.022]
    penalties_u    = [0.215, 0.000, 0.924]

    b1 = ax_a.bar(x - w/2, penalties_no_u, width=w, color='#3498db', edgecolor='black', linewidth=1.2, label='PBE+D3 (Without $U$)', alpha=0.9, zorder=3)
    b2 = ax_a.bar(x + w/2, penalties_u, width=w, color='#e74c3c', edgecolor='black', linewidth=1.2, label='PBE+D3+$U$ ($U=3.29\\,\\mathrm{eV}$)', alpha=0.9, zorder=3)

    t1 = ax_a.text(x[0] - w/2, penalties_no_u[0] + 0.08, '+0.39 eV\n(-3.81 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t2 = ax_a.text(x[0] + w/2, penalties_u[0] + 0.32, '+0.22 eV\n(-4.16 eV, Done)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    ax_a.plot([x[0] + w/2, x[0] + w/2], [penalties_u[0], penalties_u[0] + 0.30], color='#781f1f', linestyle=':', linewidth=1.1, zorder=4)

    t3 = ax_a.text(x[1] - w/2, 0.08, 'Ground State\n(-4.20 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t4 = ax_a.text(x[1] + w/2, 0.40, 'Ground State\n(-4.37 eV, Done)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    ax_a.plot([x[1] + w/2, x[1] + w/2], [penalties_u[1], 0.38], color='#781f1f', linestyle=':', linewidth=1.1, zorder=4)

    t5 = ax_a.text(x[2] - w/2, penalties_no_u[2] + 0.10, '+1.02 eV\n(-3.18 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t6 = ax_a.text(x[2] + w/2, penalties_u[2] + 0.10, '+0.92 eV\n(-3.45 eV, Done)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)

    resolve_text_overlaps(fig, ax_a, [t1, t2, t3, t4, t5, t6])

    ax_a.set_ylabel(r'Relative Energy Penalty $\Delta E_{\mathrm{rel}}$ (eV)', fontsize=12, fontweight='bold')
    ax_a.set_title(r'(a) Ni Adsorption Site Preference on $\mathrm{CrCl}_3(2\times2)$', fontsize=12, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(sites, fontsize=10.5)
    ax_a.set_ylim(-0.05, 2.10)
    ax_a.yaxis.set_major_locator(MultipleLocator(0.4))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_a.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_a.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')

    # -------------------------------------------------------------
    # Panel (b): Magnetic Invariance in Ni (d8 closed subshell)
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    mag_labels = ['Pristine\nSlab', 'Top-Cl ($S_1$)\nWithout $U$', 'Hollow ($S_2$)\nWithout $U$', 'Hollow ($S_2$)\nWith $+U$', 'Ni–H\nWithout $U$']
    x_b = np.arange(len(mag_labels))
    mags = [24.00, 24.00, 24.00, 24.00, 25.00]
    colors_b = ['#7f8c8d', '#2980b9', '#3498db', '#c0392b', '#8e44ad']

    ax_b.bar(x_b, mags, width=0.50, color=colors_b, edgecolor='black', linewidth=1.2, zorder=3)
    ax_b.axhline(24.0, color='gray', linestyle=':', linewidth=1.3, label=r'Pristine $2\times2$ ($24\,\mu_{\mathrm{B}}$)', zorder=2)

    for i in range(len(mag_labels)):
        ax_b.text(x_b[i], mags[i] + 0.60, f'{mags[i]:.2f} $\\mu_{{\\mathrm{{B}}}}$', ha='center', va='bottom', fontsize=8.2, fontweight='bold', bbox=bbox_props, zorder=5)

    ax_b.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}$ ($\mu_{\mathrm{B}}$)', fontsize=12, fontweight='bold')
    ax_b.set_title(r'(b) Ni Magnetic Moment Stability (Singlet $\mathrm{Ni}^{2+}$)', fontsize=12, fontweight='bold', pad=10)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(mag_labels, fontsize=9.0)
    ax_b.set_ylim(18, 30.5)
    ax_b.yaxis.set_major_locator(MultipleLocator(2.0))
    ax_b.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_b.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')

    # -------------------------------------------------------------
    # Panel (c): Free Energy Profile for HER (Delta G_H*)
    # -------------------------------------------------------------
    ax_c = axs[1, 0]
    systems_c = ['Pristine\n(Top-Cl)', 'Embedded Ni\n(6-coord Cl)', 'Adsorbed Ni\nWithout $U$ (S2)', 'Adsorbed Ni\nWith $U$ (Projected)']
    deltag_vals = [1.528, 1.888, 0.862, 0.620]
    x_c = np.arange(len(systems_c))

    ax_c.axhspan(-0.10, 0.20, color='#2ecc71', alpha=0.22, label=r'Optimal HER Window ($\pm 0.15\,\mathrm{eV}$)', zorder=1)
    ax_c.axhline(0.00, color='#27ae60', linestyle='--', linewidth=1.5, label=r'Thermo-neutral ($\Delta G_{\mathrm{H}^*} = 0$)', zorder=2)

    for i in range(len(systems_c)):
        val = deltag_vals[i]
        c = '#27ae60' if -0.1 <= val <= 0.2 else '#c0392b' if val > 1.0 else '#2980b9'
        ax_c.plot([i - 0.28, i + 0.28], [val, val], color=c, linewidth=4.0, solid_capstyle='round', zorder=4)
        ax_c.text(i, val + 0.10, f'{val:+.3f} eV', ha='center', va='bottom', fontsize=9.0, fontweight='bold', color=c, bbox=bbox_props, zorder=5)

    ax_c.set_ylabel(r'HER Free Energy $\Delta G_{\mathrm{H}^*}$ (eV)', fontsize=12, fontweight='bold')
    ax_c.set_title(r'(c) Ni HER Electrocatalytic Descriptor Benchmarks', fontsize=12, fontweight='bold', pad=10)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(systems_c, fontsize=9.5)
    ax_c.set_ylim(-0.30, 2.50)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_c.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper left')

    # -------------------------------------------------------------
    # Panel (d): Active Site Geometry & Distances
    # -------------------------------------------------------------
    ax_d = axs[1, 1]
    geom_labels = ['Ni at Hollow ($S_2$)\nWithout $U$', 'Ni at Hollow ($S_2$)\nWith $+U$ (Converged)']
    x_d = np.arange(len(geom_labels))
    w_d = 0.28

    d_nicl = [2.276, 2.258]
    d_nicr = [2.842, 2.825]

    ax_d.bar(x_d - w_d/2, d_nicl, width=w_d, color='#3498db', edgecolor='black', linewidth=1.2, label=r'Avg $d(\mathrm{Ni-Cl})$', zorder=3)
    ax_d.bar(x_d + w_d/2, d_nicr, width=w_d, color='#e67e22', edgecolor='black', linewidth=1.2, label=r'Avg $d(\mathrm{Ni-Cr})$', zorder=3)

    for i in range(len(geom_labels)):
        ax_d.text(i - w_d/2, d_nicl[i] + 0.08, f'{d_nicl[i]:.3f} Å', ha='center', va='bottom', fontsize=8.2, fontweight='bold', bbox=bbox_props, zorder=5)
        ax_d.text(i + w_d/2, d_nicr[i] + 0.08, f'{d_nicr[i]:.3f} Å', ha='center', va='bottom', fontsize=8.2, fontweight='bold', bbox=bbox_props, zorder=5)

    ax_d.set_ylabel(r'Interatomic Distance (Å)', fontsize=12, fontweight='bold')
    ax_d.set_title(r'(d) Hollow Coordination Metric under $+U$', fontsize=12, fontweight='bold', pad=10)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(geom_labels, fontsize=9.5)
    ax_d.set_ylim(0, 4.00)
    ax_d.yaxis.set_major_locator(MultipleLocator(1.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax_d.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_d.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')

    out_png = os.path.join(SCRIPT_DIR, "crcl3_ni_h_u_comparison_multipanel.png")
    out_pdf = os.path.join(SCRIPT_DIR, "crcl3_ni_h_u_comparison_multipanel.pdf")
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")


if __name__ == "__main__":
    generate_fe_multipanel()
    generate_ni_multipanel()
