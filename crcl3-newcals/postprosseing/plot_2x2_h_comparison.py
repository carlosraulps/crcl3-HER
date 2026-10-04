#!/usr/bin/env python3
"""
plot_2x2_h_comparison.py

Generates a dedicated, publication-grade 4-panel comparison for Hydrogen Adsorption
and Catalytic Activation specifically on the 2x2 monolayer CrCl3 supercell (theta = 0.25, d_H-H = 12.09 A):
  Panel (a): Adsorption Energy E_ads across Sites (S1: Top-Cl, S3: Top-Cr, S2: Hollow) & Functionals
  Panel (b): Thermodynamic Binding Energy Delta_E (Pure PBE vs D3-Zero vs D3-BJ vs PBE+D3+U) with Zero Collision
  Panel (c): HER Gibbs Free Energy Diagram (Delta_G_H*) vs Ideal Sabatier Benchmark & TM Activation
  Panel (d): Spin Polarization & Magnetic Moment Compensation across Pristine & TM Functionalized 2x2 Supercells

Strictly obeys GEMINI.md Anti-Collision Policy:
  - Zero-overlap mandate (staggered cards for dense Delta_E and E_ads bars)
  - Adaptive headroom (ymax and ymin scaled to prevent text clipping)
  - STIX math & Times New Roman typography
  - Density-aware legend and callout card placement
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
    fig, axs = plt.subplots(2, 2, figsize=(15.0, 12.0))
    fig.subplots_adjust(hspace=0.34, wspace=0.26)
    
    bbox_card = dict(boxstyle='round,pad=0.20', facecolor='white', edgecolor='#cccccc', alpha=0.94, linewidth=0.8)
    
    # -------------------------------------------------------------------------
    # Method definitions & 2x2 Pristine Converged Data
    # -------------------------------------------------------------------------
    methods = [
        'Pure PBE\n($U=0$, no vdW)',
        'PBE+D3 (Zero)\n($U=0$, Zero-damp)',
        'PBE+D3 (BJ)\n($U=0$, BJ-damp)',
        'PBE+D3 (BJ) + $U$\n($U_{\\mathrm{Cr}}=3.29\\,\\mathrm{eV}$)'
    ]
    x = np.arange(len(methods))
    width = 0.22
    
    # Colors for pristine sites
    c_s1 = '#1f77b4'  # Blue for Top-Cl
    c_s2 = '#d62728'  # Red for Hollow
    c_s3 = '#2ca02c'  # Green for Top-Cr
    
    # E_ads (eV):
    # Pure PBE: S1=1.579, S3=1.624, S2=2.471
    # D3-Zero:  S1=1.513, S3=1.624, S2=2.359
    # D3-BJ:    S1=1.288, S3=1.636, S2=2.324
    # D3-BJ+U:  S1=0.916, S3=2.177, S2=1.831
    e_ads_s1 = [1.579, 1.513, 1.288, 0.916]
    e_ads_s3 = [1.624, 1.624, 1.636, 2.177]
    e_ads_s2 = [2.471, 2.359, 2.324, 1.831]
    
    # Delta_E (eV):
    # Pure PBE: S1=-1.801, S3=-1.756, S2=-0.909
    # D3-Zero:  S1=-1.867, S3=-1.756, S2=-1.021
    # D3-BJ:    S1=-2.093, S3=-1.745, S2=-1.057
    # D3-BJ+U:  S1=-2.466, S3=-1.204, S2=-1.550
    delta_e_s1 = [-1.801, -1.867, -2.093, -2.466]
    delta_e_s3 = [-1.756, -1.756, -1.745, -1.204]
    delta_e_s2 = [-0.909, -1.021, -1.057, -1.550]
    
    # Caique-corrected Delta_G (eV):
    # S1 (corr = +0.21 eV): [1.789, 1.723, 1.498, 1.125]
    # S3 (corr = +0.26 eV): [1.884, 1.884, 1.896, 2.436]
    # S2 (corr = +0.21 eV): [2.681, 2.569, 2.534, 2.040]
    delta_g_s1 = [1.789, 1.723, 1.498, 1.125]
    delta_g_s3 = [1.884, 1.884, 1.896, 2.436]
    delta_g_s2 = [2.681, 2.569, 2.534, 2.040]
    
    # -------------------------------------------------------------------------
    # Panel (a): Hydrogen Adsorption Energy E_ads
    # -------------------------------------------------------------------------
    ax_a = axs[0, 0]
    r1 = ax_a.bar(x - width, e_ads_s1, width,
                  label=r'Site 1: Top-Cl ($S_1$, Ground State)',
                  color=c_s1, edgecolor='#114b73', linewidth=1.1, zorder=3)
    r3 = ax_a.bar(x, e_ads_s3, width,
                  label=r'Site 3: Top-Cr ($S_3$, Metastable)',
                  color=c_s3, edgecolor='#1b611b', linewidth=1.1, zorder=3)
    r2 = ax_a.bar(x + width, e_ads_s2, width,
                  label=r'Site 2: Hollow ($S_2$, High Energy)',
                  color=c_s2, edgecolor='#8a1818', linewidth=1.1, zorder=3)
    
    # Staggered offsets for adjacent bars
    offsets_s1 = [0.06, 0.06, 0.06, 0.06]
    offsets_s3 = [0.18, 0.18, 0.18, 0.18]
    offsets_s2 = [0.06, 0.06, 0.06, 0.06]
    
    for i, (r, val, off) in enumerate(zip(r1, e_ads_s1, offsets_s1)):
        suffix = "\n(GS)" if i == 3 else ""
        ax_a.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV{suffix}',
                  ha='center', va='bottom', fontsize=8.0, fontweight='bold',
                  bbox=bbox_card, zorder=5)
    for r, val, off in zip(r3, e_ads_s3, offsets_s3):
        ax_a.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='bottom', fontsize=8.0, fontweight='bold',
                  bbox=bbox_card, zorder=5)
    for r, val, off in zip(r2, e_ads_s2, offsets_s2):
        ax_a.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='bottom', fontsize=8.0, fontweight='bold',
                  bbox=bbox_card, zorder=5)
            
    ax_a.set_ylabel(r'$E_{\mathrm{ads}} = E_{\mathrm{tot}} - E_{\mathrm{clean}} - \frac{1}{2}E(\mathrm{H}_2)\ \ (\mathrm{eV})$', fontsize=11.5)
    ax_a.set_title(r'(a) $2\times2$ Hydrogen Adsorption Energy ($E_{\mathrm{ads}}$)', fontsize=12.5, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(methods, fontsize=9.0)
    ax_a.set_ylim(0, 3.65)
    ax_a.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_a.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    ax_a.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.2)
    
    # -------------------------------------------------------------------------
    # Panel (b): Thermodynamic Binding Energy Delta_E (Zero Collision Design)
    # -------------------------------------------------------------------------
    ax_b = axs[0, 1]
    rb1 = ax_b.bar(x - width, delta_e_s1, width,
                   label=r'Site 1: Top-Cl ($S_1$)',
                   color=c_s1, edgecolor='#114b73', linewidth=1.1, zorder=3)
    rb3 = ax_b.bar(x, delta_e_s3, width,
                   label=r'Site 3: Top-Cr ($S_3$)',
                   color=c_s3, edgecolor='#1b611b', linewidth=1.1, zorder=3)
    rb2 = ax_b.bar(x + width, delta_e_s2, width,
                   label=r'Site 2: Hollow ($S_2$)',
                   color=c_s2, edgecolor='#8a1818', linewidth=1.1, zorder=3)
    
    # ANTI-COLLISION STAGGERING:
    # S1 and S3 in cols 0, 1, 2 are nearly identical (-1.80 vs -1.76, -1.87 vs -1.76, -2.09 vs -1.75).
    # S3 is placed significantly deeper (-0.30 eV) to guarantee ZERO text overlap!
    b_offsets_s1 = [-0.07, -0.07, -0.07, -0.07]
    b_offsets_s3 = [-0.30, -0.30, -0.30, -0.07]  # Col 3 has 0.35 eV clearance so -0.07 is safe
    b_offsets_s2 = [-0.07, -0.07, -0.07, -0.07]
    
    for r, val, off in zip(rb1, delta_e_s1, b_offsets_s1):
        ax_b.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='top', fontsize=8.0, fontweight='bold',
                  bbox=bbox_card, zorder=5)
    for r, val, off in zip(rb3, delta_e_s3, b_offsets_s3):
        # Draw subtle leader line when staggered deep
        if off <= -0.20:
            ax_b.plot([r.get_x() + r.get_width()/2.0, r.get_x() + r.get_width()/2.0],
                      [r.get_height(), r.get_height() + off + 0.05],
                      color='#1b611b', linestyle=':', linewidth=0.9, zorder=4)
        ax_b.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='top', fontsize=8.0, fontweight='bold',
                  bbox=bbox_card, zorder=5)
    for r, val, off in zip(rb2, delta_e_s2, b_offsets_s2):
        ax_b.text(r.get_x() + r.get_width()/2.0, r.get_height() + off, f'{val:.2f} eV',
                  ha='center', va='top', fontsize=8.0, fontweight='bold',
                  bbox=bbox_card, zorder=5)
            
    ax_b.axhline(0, color='black', linewidth=1.0, zorder=4)
    ax_b.set_ylabel(r'$\Delta E = E_{\mathrm{slab+H}} - E_{\mathrm{clean}}\ \ (\mathrm{eV})$', fontsize=11.5)
    ax_b.set_title(r'(b) Thermodynamic Binding Energy ($\Delta E$)', fontsize=12.5, fontweight='bold', pad=10)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(methods, fontsize=9.0)
    ax_b.set_ylim(-3.10, 0.45)
    ax_b.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_b.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_b.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    ax_b.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.2)
    
    # -------------------------------------------------------------------------
    # Panel (c): HER Gibbs Free Energy Profile (Pristine vs TM Activation)
    # -------------------------------------------------------------------------
    ax_c = axs[1, 0]
    step_labels = [r'$\mathrm{H}^+ + \mathrm{e}^-$', r'$\mathrm{H}^*_{\mathrm{ads}}$', r'$\frac{1}{2}\mathrm{H}_2$']
    
    # Optimal Sabatier Active Window Shading
    ax_c.axhspan(-0.15, 0.20, color='#2ecc71', alpha=0.18, zorder=1,
                 label=r'Optimal Sabatier Window ($|\Delta G_{\mathrm{H}^*}| \leq 0.20\,\mathrm{eV}$)')
    
    # Ideal catalyst baseline
    ax_c.axhline(0, color='#e67e22', linestyle='--', linewidth=1.8,
                 label=r'Ideal Catalyst Benchmark ($\Delta G = 0$)', zorder=2)
    
    # Pristine Profiles (Caique-corrected)
    pristine_her = [
        (c_s1, '-', r'Pristine $S_1$ (PBE+D3+$U$)', delta_g_s1[3]),
        (c_s1, '--', r'Pristine $S_1$ (PBE+D3 BJ)', delta_g_s1[2]),
        (c_s1, ':', r'Pristine $S_1$ (Pure PBE)', delta_g_s1[0]),
        (c_s2, '-.', r'Pristine $S_2$ (PBE+D3+$U$)', delta_g_s2[3]),
        (c_s3, '-.', r'Pristine $S_3$ (PBE+D3+$U$)', delta_g_s3[3]),
    ]
    
    # Converged Transition-Metal Functionalized Profiles (PBE+D3+U)
    # Co ads (-0.069 eV), Fe ads (+0.185 eV), Ni ads (+0.620 eV), Ni emb (+0.821 eV), Fe emb (+1.114 eV)
    tm_her = [
        ('#8e44ad', '-', r'$\mathbf{CrCl_3\text{-}Co\ (ads)}$ (+U): $\mathbf{-0.07\,eV}$ [Apex]', -0.069, 3.0),
        ('#d35400', '-', r'$\mathbf{CrCl_3\text{-}Fe\ (ads)}$ (+U): $\mathbf{+0.19\,eV}$ [Active]', 0.185, 2.5),
        ('#16a085', '--', r'$\mathrm{CrCl_3\text{-}Ni\ (ads)}$ (+U): $+0.62\,\mathrm{eV}$', 0.620, 1.8),
        ('#16a085', ':', r'$\mathrm{CrCl_3\text{-}Ni\ (emb)}$ (+U): $+0.82\,\mathrm{eV}$', 0.821, 1.8),
        ('#d35400', ':', r'$\mathrm{CrCl_3\text{-}Fe\ (emb)}$ (+U): $+1.11\,\mathrm{eV}$', 1.114, 1.8),
    ]
    
    # Plot pristine lines
    for color, ls, label, dg in pristine_her:
        ax_c.plot([-0.3, 0.3], [0, 0], color='#2c3e50', linewidth=1.5, zorder=3)
        ax_c.plot([0.7, 1.3], [dg, dg], color=color, linestyle=ls, linewidth=2.0,
                  label=f'{label}: +{dg:.2f} eV', zorder=3)
        ax_c.plot([1.7, 2.3], [0, 0], color='#2c3e50', linewidth=1.5, zorder=3)
        ax_c.plot([0.3, 0.7], [0, dg], color=color, linestyle=ls, alpha=0.35, linewidth=1.1, zorder=3)
        ax_c.plot([1.3, 1.7], [dg, 0], color=color, linestyle=ls, alpha=0.35, linewidth=1.1, zorder=3)
        
    # Plot TM lines with distinct markers
    for color, ls, label, dg, lw in tm_her:
        ax_c.plot([0.7, 1.3], [dg, dg], color=color, linestyle=ls, linewidth=lw, label=label, zorder=4)
        ax_c.plot([0.3, 0.7], [0, dg], color=color, linestyle=ls, alpha=0.55, linewidth=1.2, zorder=4)
        ax_c.plot([1.3, 1.7], [dg, 0], color=color, linestyle=ls, alpha=0.55, linewidth=1.2, zorder=4)
        # Highlight Sabatier active candidates
        if dg < 0.25:
            ax_c.plot(1.0, dg, marker='*', markersize=9, color=color, zorder=6)
        
    ax_c.set_xticks([0, 1, 2])
    ax_c.set_xticklabels(step_labels, fontsize=11, fontweight='bold')
    ax_c.set_ylabel(r'$\Delta G_{\mathrm{H}^*} = E_{\mathrm{ads}} + (\Delta E_{\mathrm{ZPE}} - T\Delta S)\ \ (\mathrm{eV})$', fontsize=11.5)
    ax_c.set_title(r'(c) $2\times2$ HER Free Energy Profile: Pristine vs TM Activation', fontsize=12.5, fontweight='bold', pad=10)
    ax_c.set_ylim(-0.45, 3.35)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    ax_c.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.94, fontsize=7.3, ncol=2)
    
    # -------------------------------------------------------------------------
    # Panel (d): Spin Polarization & Magnetic Compensation across 2x2 Systems
    # -------------------------------------------------------------------------
    ax_d = axs[1, 1]
    
    sites_mag = [
        'Clean\n$2\\times2$',
        'Top-Cl\n($S_1$)',
        'Hollow\n($S_2$)',
        'Top-Cr\n($S_3$)',
        'Co (ads)\n+H (Apex)',
        'Fe (ads)\n+H (Act.)',
        'Ni (ads)\n+H'
    ]
    x_d = np.arange(len(sites_mag))
    
    # Converged magnetic moments (mu_B)
    mag_vals = [24.00, 25.00, 25.00, 23.00, 24.00, 28.42, 25.00]
    bar_cols = ['#7f8c8d', c_s1, c_s2, c_s3, '#8e44ad', '#d35400', '#16a085']
    
    rects_d = ax_d.bar(x_d, mag_vals, width=0.52, color=bar_cols, edgecolor='#333333', linewidth=1.1, zorder=3)
    
    for r, val in zip(rects_d, mag_vals):
        diff = val - 24.00
        diff_str = f"({diff:+.0f}" if abs(diff - round(diff)) < 0.05 else f"({diff:+.2f}"
        diff_str += r"$\,\mu_B$)" if diff != 0 else r" ref)"
        ax_d.text(r.get_x() + r.get_width()/2.0, r.get_height() + 0.35,
                  f'{val:.2f} ' + r'$\mu_B$' + f'\n{diff_str}',
                  ha='center', va='bottom', fontsize=7.5, fontweight='bold',
                  bbox=bbox_card, zorder=5)
        
    ax_d.axhline(24.00, color='#34495e', linestyle=':', linewidth=1.4, zorder=4)
    ax_d.set_ylabel(r'Total Cell Magnetization $M_{\mathrm{tot}}\ \ (\mu_B)$', fontsize=11.5)
    ax_d.set_title(r'(d) Spin Polarization & Magnetic Compensation ($2\times2$ Supercell)', fontsize=12.5, fontweight='bold', pad=10)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(sites_mag, fontsize=8.2)
    ax_d.set_ylim(19.5, 35.0)
    ax_d.yaxis.set_major_locator(MultipleLocator(2.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax_d.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    
    # Inset badge for Converged Calculations Benchmark
    status_text = (
        r"$\mathbf{Converged\ Benchmark\ Milestones\ (PBE+D3+U):}$" + "\n"
        r"$\bullet\ \mathrm{Pristine\ 2\times2:}\ S_1\ (+1.13\,\mathrm{eV}),\ S_2\ (+2.04\,\mathrm{eV}),\ S_3\ (+2.44\,\mathrm{eV})\ [\mathbf{CONVERGED}]$" + "\n"
        r"$\bullet\ \mathrm{TM\ Adsorbed:}\ \mathbf{Co\ (-0.07\,eV,\ Apex)},\ \mathbf{Fe\ (+0.19\,eV,\ Active)},\ \mathrm{Ni\ (+0.62\,eV)}\ [\mathbf{CONVERGED}]$" + "\n"
        r"$\bullet\ \mathrm{TM\ Embedded:}\ \mathrm{Ni\ (+0.82\,eV)},\ \mathrm{Fe\ (+1.11\,eV)},\ \mathrm{Co\ (+1.35\,eV)}\ [\mathbf{CONVERGED}]$" + "\n"
        r"$\bullet\ \mathrm{Multi\text{-}Site\ } U_{\mathrm{all}}=3.29\,\mathrm{eV}:\ \mathrm{Fe(emb)}\ \Delta G = +1.82\,\mathrm{eV},\ \mathrm{Co(ads)+H}\ (28\,\mu_B)\ [\mathbf{5\ CONVERGED}]$"
    )
    ax_d.text(0.02, 0.96, status_text, transform=ax_d.transAxes,
              fontsize=7.3, va='top', ha='left',
              fontweight='bold', fontfamily='serif',
              bbox=dict(boxstyle='round,pad=0.35', facecolor='#e8f8f5', edgecolor='#2ecc71', alpha=0.96, linewidth=1.0),
              zorder=6)

    plt.suptitle(r'Comprehensive Hydrogen Adsorption & Catalytic Activation on $2\times2$ Monolayer $\mathrm{CrCl}_3$ ($\theta=0.25$, $d_{\mathrm{H-H}}=12.09\ \mathrm{\AA}$)',
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
