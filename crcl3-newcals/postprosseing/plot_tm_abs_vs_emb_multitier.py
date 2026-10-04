#!/usr/bin/env python3
"""
plot_tm_abs_vs_emb_multitier.py

Generates a publication-grade, 4-panel comprehensive comparative figure analyzing
Transition-Metal Functionalized (Co, Fe, Ni) Monolayer CrCl3 in both Adsorbed and
Embedded Configurations across three systematic methodological tiers:
  Tier 1: vdW Dispersion (PBE+D3 Becke-Johnson, U = 0)
  Tier 2: Single-Site Hubbard U (PBE+D3 + U_Cr, U_Cr = 3.29 eV)
  Tier 3: Multi-Site Hubbard U (PBE+D3 + U_all, U_Cr = 3.29 eV & U_TM = 3.29 eV)

Panels:
  (a) HER Gibbs Free Energy (Delta G_H*) vs. Optimal Sabatier Catalytic Window
  (b) Electronic Hydrogen Adsorption Energy (E_ads = E_tot - E_clean - 1/2 E_H2)
  (c) Thermodynamic Anchoring Stability (Delta E_bind) & Embedding Driving Force (Delta Delta E)
  (d) Spin Polarization & Total Cell Magnetization (M_tot) across Configurations & Tiers

Adheres strictly to GEMINI.md Publication Anti-Collision Policy:
  - Zero-overlap mandate (adaptive vertical staggering and semi-transparent bounding cards)
  - Dynamic headroom (ymax and ymin scaled to prevent text clipping)
  - STIX math & Times New Roman typography
  - Unified figure master legend & density-aware quadrant placement
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.patches import Patch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Styling adhering to publication guidelines
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

CARD_STYLE = dict(boxstyle='round,pad=0.20', facecolor='white', edgecolor='#cccccc', alpha=0.94, linewidth=0.8)

def generate_multitier_comparison_plot():
    fig, axs = plt.subplots(2, 2, figsize=(16.5, 13.0))
    fig.subplots_adjust(top=0.885, bottom=0.065, hspace=0.32, wspace=0.24)

    metals = ['Cobalt (Co)', 'Iron (Fe)', 'Nickel (Ni)']
    x = np.arange(len(metals))
    width = 0.13

    # =========================================================================
    # MASTER DATASET: Adsorbed vs Embedded across vdW, +U_Cr, +U_all
    # =========================================================================
    # Delta G_H* (eV)
    # Adsorbed:
    dg_ads_vdw  = [0.178, 0.375, 0.862]
    dg_ads_ucr  = [-0.069, 0.185, 0.620]
    dg_ads_uall = [0.030, 0.500, 0.670]

    # Embedded:
    dg_emb_vdw  = [1.743, 1.367, 0.927]
    dg_emb_ucr  = [1.375, 1.114, 0.821]
    dg_emb_uall = [1.510, 1.821, 0.950]

    # E_ads (eV)
    # Adsorbed:
    eads_ads_vdw  = [-0.062, 0.195, 0.672]
    eads_ads_ucr  = [-0.309, 0.005, 0.430]
    eads_ads_uall = [-0.210, 0.320, 0.480]

    # Embedded:
    eads_emb_vdw  = [1.483, 1.107, 0.727]
    eads_emb_ucr  = [1.115, 0.854, 0.621]
    eads_emb_uall = [1.250, 1.561, 0.750]

    # Delta E_bind (eV)
    # Adsorbed:
    ebind_ads_vdw  = [-5.467, -5.845, -4.112]
    ebind_ads_ucr  = [-5.141, -6.126, -4.372]
    ebind_ads_uall = [-4.950, -6.643, -4.500]

    # Embedded:
    ebind_emb_vdw  = [-6.192, -6.693, -6.044]
    ebind_emb_ucr  = [-5.380, -7.531, -3.914]
    ebind_emb_uall = [-5.008, -6.487, -4.200]

    # Color definitions:
    c_ads_vdw  = '#5dade2'
    c_ads_ucr  = '#2980b9'
    c_ads_uall = '#1b4f72'

    c_emb_vdw  = '#f5b041'
    c_emb_ucr  = '#e67e22'
    c_emb_uall = '#935116'

    offsets = [-2.5*width, -1.5*width, -0.5*width, 0.5*width, 1.5*width, 2.5*width]

    # =========================================================================
    # UNIFIED TOP FIGURE MASTER LEGEND (Zero-collision architecture)
    # =========================================================================
    legend_elements = [
        Patch(facecolor=c_ads_vdw,  edgecolor='#1a5276', linewidth=1.1, label=r'Ads: PBE+D3 (vdW)'),
        Patch(facecolor=c_ads_ucr,  edgecolor='#1a5276', linewidth=1.1, label=r'Ads: $+U_{\mathrm{Cr}}$ ($3.29\,\mathrm{eV}$)'),
        Patch(facecolor=c_ads_uall, edgecolor='#0e2f44', linewidth=1.1, label=r'Ads: $+U_{\mathrm{all}}$ ($U_{\mathrm{Cr}}+U_{\mathrm{TM}}$)'),
        Patch(facecolor=c_emb_vdw,  edgecolor='#935116', linewidth=1.1, label=r'Emb: PBE+D3 (vdW)'),
        Patch(facecolor=c_emb_ucr,  edgecolor='#935116', linewidth=1.1, label=r'Emb: $+U_{\mathrm{Cr}}$ ($3.29\,\mathrm{eV}$)'),
        Patch(facecolor=c_emb_uall, edgecolor='#4a2800', linewidth=1.1, label=r'Emb: $+U_{\mathrm{all}}$ ($U_{\mathrm{Cr}}+U_{\mathrm{TM}}$)')
    ]
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.942),
               ncol=6, frameon=True, facecolor='white', framealpha=0.96, edgecolor='#b2babb',
               fontsize=9.0, handlelength=1.4, handleheight=0.9, columnspacing=1.5)

    # -------------------------------------------------------------------------
    # PANEL (a): HER Gibbs Free Energy Delta G_H* vs Sabatier Window
    # -------------------------------------------------------------------------
    ax_a = axs[0, 0]

    # Shaded Optimal Sabatier Active Window
    ax_a.axhspan(-0.15, 0.20, color='#2ecc71', alpha=0.18, zorder=1,
                 label=r'Optimal Sabatier Window ($|\Delta G_{\mathrm{H}^*}| \leq 0.20\,\mathrm{eV}$)')
    ax_a.axhline(0, color='#e67e22', linestyle='--', linewidth=1.6,
                 label=r'Ideal Catalyst Benchmark ($\Delta G = 0$)', zorder=2)

    b_a1 = ax_a.bar(x + offsets[0], dg_ads_vdw,  width, color=c_ads_vdw,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_a2 = ax_a.bar(x + offsets[1], dg_ads_ucr,  width, color=c_ads_ucr,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_a3 = ax_a.bar(x + offsets[2], dg_ads_uall, width, color=c_ads_uall, edgecolor='#0e2f44', linewidth=0.9, zorder=3)

    b_a4 = ax_a.bar(x + offsets[3], dg_emb_vdw,  width, color=c_emb_vdw,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_a5 = ax_a.bar(x + offsets[4], dg_emb_ucr,  width, color=c_emb_ucr,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_a6 = ax_a.bar(x + offsets[5], dg_emb_uall, width, color=c_emb_uall, edgecolor='#4a2800', linewidth=0.9, zorder=3)

    all_b_a = [b_a1, b_a2, b_a3, b_a4, b_a5, b_a6]
    all_v_a = [dg_ads_vdw, dg_ads_ucr, dg_ads_uall, dg_emb_vdw, dg_emb_ucr, dg_emb_uall]

    for g_idx, (bar_group, vals) in enumerate(zip(all_b_a, all_v_a)):
        y_stagger = 0.05 if (g_idx % 2 == 0) else 0.14
        for bar, val in zip(bar_group, vals):
            va_align = 'bottom' if val >= 0 else 'top'
            y_pos = val + y_stagger if val >= 0 else val - 0.06
            txt = f'{val:+.2f}' if abs(val) < 1.0 else f'{val:.2f}'
            if val == -0.069:
                txt = f'{val:+.2f}\n$\\star$ Apex'
            elif val == 0.185:
                txt = f'{val:+.2f}\n$\\star$ Act'
            ax_a.text(bar.get_x() + bar.get_width()/2.0, y_pos, txt,
                      ha='center', va=va_align, fontsize=7.0, fontweight='bold',
                      bbox=CARD_STYLE, zorder=5)

    ax_a.set_ylabel(r'$\Delta G_{\mathrm{H}^*} = E_{\mathrm{ads}} + (\Delta E_{\mathrm{ZPE}} - T\Delta S)\ \ (\mathrm{eV})$', fontsize=11.5)
    ax_a.set_title(r'(a) HER Free Energy: Adsorbed vs. Embedded across Methodological Tiers', fontsize=12.5, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(metals, fontsize=10.5, fontweight='bold')
    ax_a.set_ylim(-0.55, 2.50)
    ax_a.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_a.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    ax_a.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.94, fontsize=8.2)

    # -------------------------------------------------------------------------
    # PANEL (b): Electronic Hydrogen Adsorption Energy E_ads
    # -------------------------------------------------------------------------
    ax_b = axs[0, 1]
    ax_b.axhline(0, color='black', linewidth=1.0, zorder=2)

    b_b1 = ax_b.bar(x + offsets[0], eads_ads_vdw,  width, color=c_ads_vdw,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_b2 = ax_b.bar(x + offsets[1], eads_ads_ucr,  width, color=c_ads_ucr,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_b3 = ax_b.bar(x + offsets[2], eads_ads_uall, width, color=c_ads_uall, edgecolor='#0e2f44', linewidth=0.9, zorder=3)

    b_b4 = ax_b.bar(x + offsets[3], eads_emb_vdw,  width, color=c_emb_vdw,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_b5 = ax_b.bar(x + offsets[4], eads_emb_ucr,  width, color=c_emb_ucr,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_b6 = ax_b.bar(x + offsets[5], eads_emb_uall, width, color=c_emb_uall, edgecolor='#4a2800', linewidth=0.9, zorder=3)

    all_b_b = [b_b1, b_b2, b_b3, b_b4, b_b5, b_b6]
    all_v_b = [eads_ads_vdw, eads_ads_ucr, eads_ads_uall, eads_emb_vdw, eads_emb_ucr, eads_emb_uall]

    for g_idx, (bar_group, vals) in enumerate(zip(all_b_b, all_v_b)):
        y_stagger = 0.05 if (g_idx % 2 == 0) else 0.14
        for bar, val in zip(bar_group, vals):
            va_align = 'bottom' if val >= 0 else 'top'
            y_pos = val + y_stagger if val >= 0 else val - 0.06
            txt = f'{val:+.2f}' if abs(val) < 1.0 else f'{val:.2f}'
            ax_b.text(bar.get_x() + bar.get_width()/2.0, y_pos, txt,
                      ha='center', va=va_align, fontsize=7.0, fontweight='bold',
                      bbox=CARD_STYLE, zorder=5)

    ax_b.set_ylabel(r'$E_{\mathrm{ads}} = E_{\mathrm{tot}} - E_{\mathrm{clean}} - \frac{1}{2}E(\mathrm{H}_2)\ \ (\mathrm{eV})$', fontsize=11.5)
    ax_b.set_title(r'(b) Electronic Hydrogen Adsorption Energy ($E_{\mathrm{ads}}$)', fontsize=12.5, fontweight='bold', pad=10)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(metals, fontsize=10.5, fontweight='bold')
    ax_b.set_ylim(-0.65, 2.25)
    ax_b.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_b.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_b.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)

    # -------------------------------------------------------------------------
    # PANEL (c): Thermodynamic Anchoring Stability & Embedding Driving Force
    # -------------------------------------------------------------------------
    ax_c = axs[1, 0]
    ax_c.axhline(0, color='black', linewidth=1.0, zorder=2)

    b_c1 = ax_c.bar(x + offsets[0], ebind_ads_vdw,  width, color=c_ads_vdw,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_c2 = ax_c.bar(x + offsets[1], ebind_ads_ucr,  width, color=c_ads_ucr,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_c3 = ax_c.bar(x + offsets[2], ebind_ads_uall, width, color=c_ads_uall, edgecolor='#0e2f44', linewidth=0.9, zorder=3)

    b_c4 = ax_c.bar(x + offsets[3], ebind_emb_vdw,  width, color=c_emb_vdw,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_c5 = ax_c.bar(x + offsets[4], ebind_emb_ucr,  width, color=c_emb_ucr,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_c6 = ax_c.bar(x + offsets[5], ebind_emb_uall, width, color=c_emb_uall, edgecolor='#4a2800', linewidth=0.9, zorder=3)

    all_b_c = [b_c1, b_c2, b_c3, b_c4, b_c5, b_c6]
    all_v_c = [ebind_ads_vdw, ebind_ads_ucr, ebind_ads_uall, ebind_emb_vdw, ebind_emb_ucr, ebind_emb_uall]

    for g_idx, (bar_group, vals) in enumerate(zip(all_b_c, all_v_c)):
        y_stagger = 0.14 if (g_idx % 2 == 0) else 0.50
        for bar, val in zip(bar_group, vals):
            ax_c.text(bar.get_x() + bar.get_width()/2.0, val - y_stagger, f'{val:.2f}',
                      ha='center', va='top', fontsize=6.8, fontweight='bold',
                      bbox=CARD_STYLE, zorder=5)

    # Clean, collision-free placement of penetration driving force Delta Delta E in positive headroom
    # Fe: -1.41 eV (Pore favored)
    ax_c.annotate(r'$\mathbf{\Delta\Delta E = -1.41\,\mathrm{eV}}$' + '\n' + r'Pore Favored ($+U_{\mathrm{Cr}}$)',
                  xy=(x[1] + offsets[4], 0.0), xytext=(x[1], 1.05),
                  arrowprops=dict(arrowstyle='->', color='#935116', lw=1.3),
                  fontsize=8.0, fontweight='bold', color='#935116', bbox=CARD_STYLE, ha='center', zorder=6)

    # Co: -0.24 eV (Near Bistable)
    ax_c.annotate(r'$\mathbf{\Delta\Delta E = -0.24\,\mathrm{eV}}$' + '\n' + r'Near Bistable ($+U_{\mathrm{Cr}}$)',
                  xy=(x[0] + offsets[4], 0.0), xytext=(x[0], 1.05),
                  arrowprops=dict(arrowstyle='->', color='#935116', lw=1.3),
                  fontsize=8.0, fontweight='bold', color='#935116', bbox=CARD_STYLE, ha='center', zorder=6)

    # Ni: +0.46 eV (Surface favored)
    ax_c.annotate(r'$\mathbf{\Delta\Delta E = +0.46\,\mathrm{eV}}$' + '\n' + r'Surface Favored ($+U_{\mathrm{Cr}}$)',
                  xy=(x[2] + offsets[1], 0.0), xytext=(x[2], 1.05),
                  arrowprops=dict(arrowstyle='->', color='#1a5276', lw=1.3),
                  fontsize=8.0, fontweight='bold', color='#1a5276', bbox=CARD_STYLE, ha='center', zorder=6)

    ax_c.set_ylabel(r'$\Delta E_{\mathrm{bind}} = E_{\mathrm{tot}} - E_{\mathrm{clean}} - E_{\mathrm{atom}}\ \ (\mathrm{eV})$', fontsize=11.5)
    ax_c.set_title(r'(c) TM Anchoring Stability & Embedding Driving Force ($\Delta\Delta E$)', fontsize=12.5, fontweight='bold', pad=10)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels(metals, fontsize=10.5, fontweight='bold')
    ax_c.set_ylim(-8.8, 1.9)
    ax_c.yaxis.set_major_locator(MultipleLocator(1.0))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax_c.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)

    # -------------------------------------------------------------------------
    # PANEL (d): Spin Polarization & Magnetic Moment Trends (M_tot)
    # -------------------------------------------------------------------------
    ax_d = axs[1, 1]

    mag_ads_vdw  = [24.00, 28.42, 25.00]
    mag_ads_ucr  = [24.00, 28.42, 25.00]
    mag_ads_uall = [28.00, 30.00, 25.00]

    mag_emb_vdw  = [24.00, 27.37, 25.00]
    mag_emb_ucr  = [24.00, 27.37, 25.00]
    mag_emb_uall = [29.00, 29.00, 25.00]

    ax_d.axhline(24.00, color='#34495e', linestyle=':', linewidth=1.5,
                 label=r'Pristine $\mathrm{CrCl}_3$ Baseline ($24.0\,\mu_B$)', zorder=2)

    b_d1 = ax_d.bar(x + offsets[0], mag_ads_vdw,  width, color=c_ads_vdw,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_d2 = ax_d.bar(x + offsets[1], mag_ads_ucr,  width, color=c_ads_ucr,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_d3 = ax_d.bar(x + offsets[2], mag_ads_uall, width, color=c_ads_uall, edgecolor='#0e2f44', linewidth=0.9, zorder=3)

    b_d4 = ax_d.bar(x + offsets[3], mag_emb_vdw,  width, color=c_emb_vdw,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_d5 = ax_d.bar(x + offsets[4], mag_emb_ucr,  width, color=c_emb_ucr,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_d6 = ax_d.bar(x + offsets[5], mag_emb_uall, width, color=c_emb_uall, edgecolor='#4a2800', linewidth=0.9, zorder=3)

    all_b_d = [b_d1, b_d2, b_d3, b_d4, b_d5, b_d6]
    all_v_d = [mag_ads_vdw, mag_ads_ucr, mag_ads_uall, mag_emb_vdw, mag_emb_ucr, mag_emb_uall]

    # Label Co and Fe with alternating vertical staggering to prevent horizontal collisions
    for g_idx, (bar_group, vals) in enumerate(zip(all_b_d, all_v_d)):
        y_stagger = 0.35 if (g_idx % 2 == 0) else 1.25
        for m_idx in [0, 1]:  # Co and Fe only
            bar = bar_group[m_idx]
            val = vals[m_idx]
            diff = val - 24.00
            diff_str = f"({diff:+.0f}" if abs(diff - round(diff)) < 0.05 else f"({diff:+.1f}"
            diff_str += r"$\,\mu_B$)" if diff != 0 else r" ref)"
            ax_d.text(bar.get_x() + bar.get_width()/2.0, val + y_stagger,
                      f'{val:.1f}\n{diff_str}',
                      ha='center', va='bottom', fontsize=6.5, fontweight='bold',
                      bbox=CARD_STYLE, zorder=5)

    # For Nickel (m_idx = 2), magnetization is strictly invariant (25.0 mu_B) across all 6 tiers
    # Display two high-clarity grouped summary cards instead of 6 colliding duplicate cards
    ax_d.text(x[2] - 1.5*width, 25.0 + 0.45,
              r'$\mathbf{25.0\,\mu_B}$' + '\n' + r'$(+1.0\,\mu_B)$' + '\n' + r'Ads (All)',
              ha='center', va='bottom', fontsize=6.8, fontweight='bold',
              bbox=CARD_STYLE, zorder=5)
    ax_d.text(x[2] + 1.5*width, 25.0 + 0.45,
              r'$\mathbf{25.0\,\mu_B}$' + '\n' + r'$(+1.0\,\mu_B)$' + '\n' + r'Emb (All)',
              ha='center', va='bottom', fontsize=6.8, fontweight='bold',
              bbox=CARD_STYLE, zorder=5)

    ax_d.set_ylabel(r'Total Cell Magnetization $M_{\mathrm{tot}}\ \ (\mu_B)$', fontsize=11.5)
    ax_d.set_title(r'(d) Spin Polarization & Magnetic Moment Trends ($2\times2$ Supercell)', fontsize=12.5, fontweight='bold', pad=10)
    ax_d.set_xticks(x)
    ax_d.set_xticklabels(metals, fontsize=10.5, fontweight='bold')
    ax_d.set_ylim(20.0, 36.8)
    ax_d.yaxis.set_major_locator(MultipleLocator(2.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax_d.grid(axis='y', linestyle='--', alpha=0.45, zorder=0)
    ax_d.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.94, fontsize=8.2)

    # Inset badge for Methodology & Convergence Milestones
    status_text = (
        "Multitier Methodology & Verification Summary:\n"
        r"$\bullet$ Tier 1 (vdW): PBE+D3(BJ) [100% Converged]" + "\n"
        r"$\bullet$ Tier 2 (+$U_{\mathrm{Cr}}$): $U_{\mathrm{Cr}}=3.29\,\mathrm{eV}$ [100% Converged, Caique $\Delta G$]" + "\n"
        r"$\bullet$ Tier 3 (+$U_{\mathrm{all}}$): $U_{\mathrm{Cr}}=3.29\,\mathrm{eV},\ U_{\mathrm{TM}}=3.29\,\mathrm{eV}$ [5 Converged, 3 Live]" + "\n"
        r"$\bullet$ Key Finding: Co(ads) achieves optimal Sabatier summit ($\Delta G = -0.07\,\mathrm{eV}$)," + "\n"
        r"   while 6-fold interstitial embedding pacifies TM $d$-orbitals ($\Delta G > +0.8\,\mathrm{eV}$)."
    )
    ax_d.text(0.03, 0.95, status_text, transform=ax_d.transAxes,
              fontsize=7.2, va='top', ha='left',
              fontweight='bold', fontfamily='serif',
              bbox=dict(boxstyle='round,pad=0.35', facecolor='#e8f8f5', edgecolor='#2ecc71', alpha=0.96, linewidth=1.0),
              zorder=6)

    fig.suptitle(r'Comprehensive Multitier Benchmark: Adsorbed vs. Embedded $\mathrm{CrCl}_3\text{-}\mathrm{TM}$ ($\mathrm{TM}=\mathrm{Co,Fe,Ni}$)' + '\n' +
                 r'Systematic Comparison across vdW Dispersion, Single-Site $+U_{\mathrm{Cr}}$, and Multi-Site $+U_{\mathrm{all}}$ ($U_{\mathrm{Cr}}+U_{\mathrm{TM}}$)',
                 fontsize=14.5, fontweight='bold', y=0.985)

    out_png = os.path.join(SCRIPT_DIR, "crcl3_tm_abs_vs_emb_multitier.png")
    out_pdf = os.path.join(SCRIPT_DIR, "crcl3_tm_abs_vs_emb_multitier.pdf")

    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")

if __name__ == '__main__':
    generate_multitier_comparison_plot()
