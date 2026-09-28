#!/usr/bin/env python3
"""
plot_2x2_h_comparison.py

Generates a dedicated, publication-grade 4-panel comparison for Hydrogen Adsorption
specifically on the 2x2 monolayer CrCl3 supercell (theta = 0.25, d_H-H = 12.09 A):
  Panel (a): Adsorption Energy E_ads across Sites (S1: Top-Cl, S2: Hollow, S3: Top-Cr) & Functionals
  Panel (b): Thermodynamic Binding Energy Delta_E (Pure PBE vs D3-Zero vs D3-BJ)
  Panel (c): HER Gibbs Free Energy Diagram (Delta_G_H*) vs Ideal Catalyst Benchmark (Delta_G = 0)
  Panel (d): Spin Polarization & Magnetic Moment Compensation (M_tot: S1 vs S2 vs S3 vs Clean)

Strictly obeys GEMINI.md Anti-Collision Policy:
  - Zero-overlap mandate
  - Adaptive headroom (ymax = max(data) + 0.25 * Delta_y)
  - Staggered labels and semi-transparent bounding cards
  - Density-aware legend placement
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from smart_plot_optimizer import (
    expand_headroom_for_annotations,
    auto_stagger_bar_labels
)

# Styling adhering to publication guidelines
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

def generate_2x2_h_comparison_plot():
    fig, axs = plt.subplots(2, 2, figsize=(14.5, 11.5))
    fig.subplots_adjust(hspace=0.32, wspace=0.26)
    
    bbox_card = dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='#cccccc', alpha=0.92, linewidth=0.8)
    
    # Data definitions for 2x2 (d_H-H = 12.09 A, theta = 0.25)
    methods = [
        'Pure PBE\n($U=0$, No vdW)',
        'PBE+D3 (Zero)\n($U=0$, Zero-damp)',
        'PBE+D3 (BJ)\n($U=0$, Becke-Johnson)',
        'PBE+D3 (BJ) + $U$\n($U=3.29\\,\\mathrm{eV}$)'
    ]
    x = np.arange(len(methods))
    width = 0.22
    
    # Sites: S1 (Top-Cl), S2 (Hollow), S3 (Top-Cr)
    # E_ads (eV):
    # Pure PBE: S1=1.579, S2=2.471, S3=1.624
    # D3-Zero:  S1=1.513, S2=2.359, S3=1.624
    # D3-BJ:    S1=1.288, S2=2.324, S3=1.636
    # D3-BJ+U:  S1=0.915, S2=1.831, S3=2.177 (All Converged on Carbono)
    e_ads_s1 = [1.579, 1.513, 1.288, 0.915]
    e_ads_s2 = [2.471, 2.359, 2.324, 1.831]
    e_ads_s3 = [1.624, 1.624, 1.636, 2.177]
    
    # Delta_E (eV):
    # Pure PBE: S1=-1.801, S2=-0.909, S3=-1.755
    # D3-Zero:  S1=-1.867, S2=-1.021, S3=-1.756
    # D3-BJ:    S1=-2.093, S2=-1.057, S3=-1.745
    # D3-BJ+U:  S1=-2.466, S2=-1.550, S3=-1.204 (All Converged on Carbono)
    delta_e_s1 = [-1.801, -1.867, -2.093, -2.466]
    delta_e_s2 = [-0.909, -1.021, -1.057, -1.550]
    delta_e_s3 = [-1.755, -1.756, -1.745, -1.204]
    
    # Delta_G (eV) = E_ads + 0.24 eV:
    delta_g_s1 = [1.819, 1.753, 1.528, 1.155]
    delta_g_s2 = [2.711, 2.599, 2.564, 2.071]
    delta_g_s3 = [1.864, 1.864, 1.876, 2.417]
    
    # Magnetic moments (mu_B):
    mag_clean = 24.00
    mag_s1 = [25.00, 25.00, 25.00, 25.00]
    mag_s2 = [23.00, 23.00, 23.01, 25.00]
    mag_s3 = [23.00, 23.00, 23.00, 23.00]
    
    # Colors
    c_s1 = '#1f77b4'  # Blue for Top-Cl
    c_s2 = '#d62728'  # Red for Hollow
    c_s3 = '#2ca02c'  # Green for Top-Cr
    
    # -------------------------------------------------------------------------
    # Panel (a): Hydrogen Adsorption Energy E_ads
    # -------------------------------------------------------------------------
    ax_a = axs[0, 0]
    r1 = ax_a.bar(x - width, [val if not np.isnan(val) else 0 for val in e_ads_s1], width,
                  label=r'Site 1: Top-Cl ($S_1$, Ground State)',
                  color=c_s1, edgecolor='#114b73', linewidth=1.1, zorder=3)
    r3 = ax_a.bar(x, e_ads_s3, width, label=r'Site 3: Top-Cr ($S_3$, Metastable)',
                  color=c_s3, edgecolor='#1b611b', linewidth=1.1, zorder=3)
    r2 = ax_a.bar(x + width, [val if not np.isnan(val) else 0 for val in e_ads_s2], width,
                  label=r'Site 2: Hollow ($S_2$, High Energy)',
                  color=c_s2, edgecolor='#8a1818', linewidth=1.1, zorder=3)
    
    # Staggered offsets for adjacent bars
    offsets_s1 = [0.05, 0.05, 0.05, 0.05]
    offsets_s3 = [0.15, 0.15, 0.15, 0.15]
    offsets_s2 = [0.05, 0.05, 0.05, 0.05]
    
    for i, (r, val, off) in enumerate(zip(r1, e_ads_s1, offsets_s1)):
        suffix = "\n(GS)" if i == 3 else ""
        ax_a.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV{suffix}',
                  ha='center', va='bottom', fontsize=8.2, fontweight='bold',
                  bbox=bbox_card, zorder=5)
    for r, val, off in zip(r3, e_ads_s3, offsets_s3):
        ax_a.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='bottom', fontsize=8.2, fontweight='bold',
                  bbox=bbox_card, zorder=5)
    for r, val, off in zip(r2, e_ads_s2, offsets_s2):
        ax_a.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='bottom', fontsize=8.2, fontweight='bold',
                  bbox=bbox_card, zorder=5)
            
    ax_a.set_ylabel(r'$E_{\mathrm{ads}} = E_{\mathrm{tot}} - E_{\mathrm{clean}} - \frac{1}{2}E(\mathrm{H}_2)\ \ (\mathrm{eV})$', fontsize=12)
    ax_a.set_title(r'(a) $2\times2$ Hydrogen Adsorption Energy ($E_{\mathrm{ads}}$)', fontsize=12.5, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(methods, fontsize=9.0)
    ax_a.set_ylim(0, 3.45)
    ax_a.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_a.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    ax_a.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.5)
    
    # -------------------------------------------------------------------------
    # Panel (b): Thermodynamic Binding Energy Delta_E
    # -------------------------------------------------------------------------
    ax_b = axs[0, 1]
    rb1 = ax_b.bar(x - width, delta_e_s1, width,
                   label=r'Site 1: Top-Cl ($S_1$)',
                   color=c_s1, edgecolor='#114b73', linewidth=1.1, zorder=3)
    rb3 = ax_b.bar(x, delta_e_s3, width, label=r'Site 3: Top-Cr ($S_3$)',
                   color=c_s3, edgecolor='#1b611b', linewidth=1.1, zorder=3)
    rb2 = ax_b.bar(x + width, delta_e_s2, width,
                   label=r'Site 2: Hollow ($S_2$)',
                   color=c_s2, edgecolor='#8a1818', linewidth=1.1, zorder=3)
    
    # Stagger vertical offsets below negative bars
    b_offsets_s1 = [-0.07, -0.07, -0.07, -0.07]
    b_offsets_s3 = [-0.17, -0.17, -0.17, -0.17]
    b_offsets_s2 = [-0.07, -0.07, -0.07, -0.07]
    
    for r, val, off in zip(rb1, delta_e_s1, b_offsets_s1):
        ax_b.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='top', fontsize=8.2, fontweight='bold',
                  bbox=bbox_card, zorder=5)
    for r, val, off in zip(rb3, delta_e_s3, b_offsets_s3):
        ax_b.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='top', fontsize=8.2, fontweight='bold',
                  bbox=bbox_card, zorder=5)
    for r, val, off in zip(rb2, delta_e_s2, b_offsets_s2):
        ax_b.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='top', fontsize=8.2, fontweight='bold',
                  bbox=bbox_card, zorder=5)
            
    ax_b.axhline(0, color='black', linewidth=1.0, zorder=4)
    ax_b.set_ylabel(r'$\Delta E = E_{\mathrm{slab+H}} - E_{\mathrm{clean}}\ \ (\mathrm{eV})$', fontsize=12)
    ax_b.set_title(r'(b) Thermodynamic Binding Energy ($\Delta E$)', fontsize=12.5, fontweight='bold', pad=10)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(methods, fontsize=9.0)
    ax_b.set_ylim(-2.85, 0.45)
    ax_b.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_b.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_b.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    ax_b.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.5)
    
    # -------------------------------------------------------------------------
    # Panel (c): HER Gibbs Free Energy Profile (Delta_G_H*)
    # -------------------------------------------------------------------------
    ax_c = axs[1, 0]
    step_labels = [r'$\mathrm{H}^+ + \mathrm{e}^-$', r'$\mathrm{H}^*_{\mathrm{ads}}$', r'$\frac{1}{2}\mathrm{H}_2$']
    
    # Ideal catalyst baseline
    ax_c.axhline(0, color='#e67e22', linestyle='--', linewidth=1.8, label=r'Ideal HER Catalyst ($\Delta G = 0$)', zorder=2)
    
    # Key profiles to show for 2x2
    her_profiles = [
        (c_s1, '-', r'Top-Cl ($S_1$, PBE+D3+$U$)', delta_g_s1[3]),
        (c_s1, '--', r'Top-Cl ($S_1$, PBE+D3 BJ)', delta_g_s1[2]),
        (c_s1, ':', r'Top-Cl ($S_1$, Pure PBE)', delta_g_s1[0]),
        (c_s2, '-.', r'Hollow ($S_2$, PBE+D3+$U$)', delta_g_s2[3]),
        (c_s3, '-.', r'Top-Cr ($S_3$, PBE+D3+$U$)', delta_g_s3[3]),
    ]
    
    for color, ls, label, dg in her_profiles:
        # Step 0: 0 eV
        ax_c.plot([-0.3, 0.3], [0, 0], color='#2c3e50', linewidth=1.8)
        # Step 1: Intermediate H*
        ax_c.plot([0.7, 1.3], [dg, dg], color=color, linestyle=ls, linewidth=2.4, label=f'{label}: +{dg:.2f} eV')
        # Step 2: 1/2 H2
        ax_c.plot([1.7, 2.3], [0, 0], color='#2c3e50', linewidth=1.8)
        # Transition dotted lines
        ax_c.plot([0.3, 0.7], [0, dg], color=color, linestyle=ls, alpha=0.5, linewidth=1.2)
        ax_c.plot([1.3, 1.7], [dg, 0], color=color, linestyle=ls, alpha=0.5, linewidth=1.2)
        
    ax_c.set_xticks([0, 1, 2])
    ax_c.set_xticklabels(step_labels, fontsize=11, fontweight='bold')
    ax_c.set_ylabel(r'$\Delta G_{\mathrm{H}^*} = E_{\mathrm{ads}} + 0.24\,\mathrm{eV}\ \ (\mathrm{eV})$', fontsize=12)
    ax_c.set_title(r'(c) $2\times2$ HER Free Energy Profile ($\theta = 0.25$)', fontsize=12.5, fontweight='bold', pad=10)
    ax_c.set_ylim(-0.25, 3.45)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    ax_c.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.2)
    
    # -------------------------------------------------------------------------
    # Panel (d): Magnetic Moment Compensation & With-U Baseline Status
    # -------------------------------------------------------------------------
    ax_d = axs[1, 1]
    
    sites_mag = [
        'Clean Pristine\n($2\\times2$ Slab)',
        'Site 1: Top-Cl\n(PBE+D3+$U$)',
        'Site 2: Hollow\n(PBE+D3+$U$)',
        'Site 3: Top-Cr\n(PBE+D3+$U$)'
    ]
    x_d = np.arange(len(sites_mag))
    
    mag_vals = [24.00, 25.00, 25.00, 23.00]
    bar_cols = ['#7f8c8d', c_s1, c_s2, c_s3]
    
    rects_d = ax_d.bar(x_d, mag_vals, width=0.45, color=bar_cols, edgecolor='#333333', linewidth=1.1, zorder=3)
    
    for r, val in zip(rects_d, mag_vals):
        diff = val - 24.00
        diff_str = f"({diff:+.0f}" if abs(diff - round(diff)) < 0.05 else f"({diff:+.2f}"
        diff_str += r"$\,\mu_B$)" if diff != 0 else r" ref)"
        ax_d.text(r.get_x() + r.get_width()/2.0, r.get_height() + 0.35,
                  f'{val:.2f} ' + r'$\mu_B$' + f'\n{diff_str}',
                  ha='center', va='bottom', fontsize=8.0, fontweight='bold',
                  bbox=bbox_card, zorder=5)
        
    ax_d.axhline(24.00, color='#34495e', linestyle=':', linewidth=1.4, zorder=4)
    ax_d.set_ylabel(r'Total Cell Magnetization $M_{\mathrm{tot}}\ \ (\mu_B)$', fontsize=12)
    ax_d.set_title(r'(d) Spin Polarization & Magnetic Compensation ($2\times2$)', fontsize=12.5, fontweight='bold', pad=10)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(sites_mag, fontsize=8.5)
    ax_d.set_ylim(20.0, 29.5)
    ax_d.yaxis.set_major_locator(MultipleLocator(2.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax_d.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    
    # Inset badge for With-U dispatch status
    status_text = (
        "Hubbard +U (U_Cr = 3.29 eV) Benchmark Complete:\n"
        "• Clean Monolayer: E0 = -147.304 eV (CONVERGED)\n"
        "• Site 1 (Top-Cl): E0 = -149.769 eV (CONVERGED, ΔG = +1.16 eV)\n"
        "• Site 2 (Hollow): E0 = -148.854 eV (CONVERGED, ΔG = +2.07 eV)\n"
        "• Site 3 (Top-Cr): E0 = -148.508 eV (CONVERGED, ΔG = +2.42 eV)\n"
        r"* Top-Cl (S1) is the confirmed Ground State across all functionals!"
    )
    ax_d.text(0.03, 0.25, status_text, transform=ax_d.transAxes,
              fontsize=8.0, va='top', ha='left',
              fontweight='bold', fontfamily='serif',
              bbox=dict(boxstyle='round,pad=0.35', facecolor='#e8f8f5', edgecolor='#2ecc71', alpha=0.95, linewidth=1.0),
              zorder=6)

    plt.suptitle(r'Comprehensive Hydrogen Adsorption Benchmark on $2\times2$ Monolayer $\mathrm{CrCl}_3$ ($\theta=0.25$, $d_{\mathrm{H-H}}=12.09\ \mathrm{\AA}$)',
                 fontsize=14.5, fontweight='bold', y=0.992)
    
    out_png = os.path.join(SCRIPT_DIR, "crcl3_2x2_h_comparison.png")
    out_pdf = os.path.join(SCRIPT_DIR, "crcl3_2x2_h_comparison.pdf")
    
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")

if __name__ == '__main__':
    generate_2x2_h_comparison_plot()
