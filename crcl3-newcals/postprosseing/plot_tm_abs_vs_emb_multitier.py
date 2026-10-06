#!/usr/bin/env python3
"""
plot_tm_abs_vs_emb_multitier.py

Generates a publication-grade, 4-panel comprehensive comparative figure analyzing
Transition-Metal Functionalized (Co, Fe, Ni) Monolayer CrCl3 in both Adsorbed and
Embedded Configurations across three systematic methodological tiers:
  Tier 1: vdW Dispersion (PBE+D3 Becke-Johnson, U = 0) [100% Converged]
  Tier 2: Single-Site Hubbard U (PBE+D3 + U_Cr, U_Cr = 3.29 eV) [100% Converged]
  Tier 3: Multi-Site Hubbard U (PBE+D3 + U_all, U_Cr = 3.29 eV & U_TM = 3.29 eV)
          [Partially Converged: Fe(emb) complete; remaining 5 pairs computing/queued]

Panels:
  (a) HER Gibbs Free Energy (Delta G_H*) vs. Optimal Sabatier Catalytic Window
  (b) Electronic Hydrogen Adsorption Energy (E_ads = E_tot - E_clean - 1/2 E_H2)
  (c) Thermodynamic Anchoring Stability (Delta E_bind) & Embedding Driving Force (Delta Delta E)
  (d) Spin Polarization & Total Cell Magnetization (M_tot) across Configurations & Tiers

Strict Scientific Integrity & Anti-Collision Policy:
  - ZERO INVENTED DATA: Only truly converged DFT calculations are plotted as solid bars.
  - Active HPC jobs are transparently identified as [Running] or [Queued].
  - Zero-overlap mandate (adaptive vertical staggering and semi-transparent bounding cards)
  - Dynamic headroom (ymax and ymin scaled to prevent text clipping)
  - STIX math & Times New Roman typography
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
RUNNING_CARD = dict(boxstyle='round,pad=0.20', facecolor='#fef9e7', edgecolor='#f39c12', alpha=0.94, linewidth=0.9)
QUEUED_CARD = dict(boxstyle='round,pad=0.20', facecolor='#f2f4f4', edgecolor='#bdc3c7', alpha=0.94, linewidth=0.8)


def resolve_vertical_overlaps(fig, ax, pad_px=3.0, max_iter=3000):
    """Push overlapping value cards apart vertically (zero-overlap mandate).

    Data-coordinate labels are movable; annotations and axes-fraction texts
    (e.g. the provenance badge) are fixed obstacles. Labels move away from y=0.
    """
    from matplotlib.text import Annotation
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    movable, fixed = [], []
    for t in ax.texts:
        (fixed if isinstance(t, Annotation) or t.get_transform() != ax.transData else movable).append(t)

    fixed_ext = {}
    for t in fixed:
        patch = t.get_bbox_patch()
        fixed_ext[id(t)] = patch.get_window_extent(renderer) if patch is not None else t.get_window_extent(renderer)

    def ext(t):
        if id(t) in fixed_ext:
            return fixed_ext[id(t)]
        card_pad = 0.25 * t.get_fontsize() * fig.dpi / 72.0  # matches round,pad=0.20 cards
        return t.get_window_extent(renderer).padded(card_pad)

    y0_px = ax.transData.transform((0, 0))[1]
    inv = ax.transData.inverted()
    for _ in range(max_iter):
        moved = False
        boxes = {id(t): ext(t) for t in movable + fixed}
        for a in movable:
            ba = boxes[id(a)]
            for b in movable + fixed:
                if a is b:
                    continue
                bb = boxes[id(b)]
                if ba.x0 < bb.x1 and ba.x1 > bb.x0 and ba.y0 < bb.y1 + pad_px and ba.y1 > bb.y0 - pad_px:
                    # move `a` only if it is the outer label (farther from zero) or b is fixed
                    a_c, b_c = (ba.y0 + ba.y1) / 2, (bb.y0 + bb.y1) / 2
                    outward_up = a_c >= y0_px
                    if b in movable:
                        da, db = abs(a_c - y0_px), abs(b_c - y0_px)
                        if da < db or (da == db and id(a) < id(b)):
                            continue
                    if b in fixed:
                        outward_up = a_c >= b_c
                    shift = (bb.y1 + pad_px - ba.y0) if outward_up else -(ba.y1 - bb.y0 + pad_px)
                    x, y = a.get_position()
                    y_new = inv.transform((0, ax.transData.transform((0, y))[1] + shift))[1]
                    a.set_position((x, y_new))
                    moved = True
                    break
            if moved:
                break
        if not moved:
            return

def generate_multitier_comparison_plot():
    fig, axs = plt.subplots(2, 2, figsize=(16.5, 13.0))
    fig.subplots_adjust(top=0.885, bottom=0.065, hspace=0.32, wspace=0.24)

    metals = ['Cobalt (Co)', 'Iron (Fe)', 'Nickel (Ni)']
    x = np.arange(len(metals))
    width = 0.13

    # =========================================================================
    # MASTER DATASET: Adsorbed vs Embedded across vdW, +U_Cr, +U_all
    # Strictly Verified: np.nan denotes in-progress/queued calculations
    # =========================================================================
    # Delta G_H* (eV)
    # Adsorbed:
    dg_ads_vdw  = [0.178, 0.375, 0.862]   # Converged (vdW)
    dg_ads_ucr  = [-0.069, 0.185, 0.620] # Converged (+U_Cr)
    # Co_ads is 100% converged in Tier 3 (clean: -150.583 eV, +H: -154.160 eV) -> Delta G = +0.065 eV!
    # Fe_ads is 100% converged in Tier 3 (clean: -153.947 eV, +H: -155.751 eV) -> Delta G = +1.837 eV!
    # Ni_ads +H converged (-152.740 eV), clean relaxing on Huk (Job 8087)
    dg_ads_uall = [0.065, 1.837, np.nan]
    label_ads_uall = ['+0.06', '+1.84', '[Running]']

    # Embedded:
    dg_emb_vdw  = [1.743, 1.367, 0.927]   # Converged (vdW)
    dg_emb_ucr  = [1.375, 1.114, 0.821]   # Converged (+U_Cr)
    # Co_emb (clean: -152.311 eV, +H: -154.564 eV) -> Delta G = +1.389 eV!
    # Fe_emb (clean: -153.791 eV, +H: -155.610 eV) -> Delta G = +1.821 eV!
    # Ni_emb (clean: -150.788 eV [Job 167940], +H: -153.406 eV [Job 167941]) -> Delta G = +1.024 eV
    dg_emb_uall = [1.389, 1.821, 1.024]
    label_emb_uall = ['1.39', '1.82', '1.02']

    # E_ads (eV)
    # Adsorbed:
    eads_ads_vdw  = [-0.062, 0.195, 0.672]
    eads_ads_ucr  = [-0.309, 0.005, 0.430]
    eads_ads_uall = [-0.191, 1.581, np.nan]

    # Embedded:
    eads_emb_vdw  = [1.483, 1.107, 0.727]
    eads_emb_ucr  = [1.115, 0.854, 0.621]
    # Fe_emb: -155.610 - (-153.791) + 3.386 = 1.566 eV (previous 1.561 was a transcription slip)
    eads_emb_uall = [1.133, 1.566, 0.768]

    # Delta E_bind (eV)
    # Adsorbed:
    ebind_ads_vdw  = [-5.467, -5.845, -4.112]
    ebind_ads_ucr  = [-5.141, -6.126, -4.372]
    # Co_ads clean converged (-150.583 eV) -> -3.279 eV; Fe_ads clean converged (-153.947 eV) -> -6.643 eV
    ebind_ads_uall = [-3.279, -6.643, np.nan]

    # Embedded:
    ebind_emb_vdw  = [-6.192, -6.693, -6.044]
    ebind_emb_ucr  = [-5.380, -7.531, -3.914]
    # Co_emb clean converged (-152.311 eV) -> -5.008 eV; Fe_emb clean converged (-153.791 eV) -> -6.487 eV
    # Ni_emb clean converged (-150.788 eV) -> -3.484 eV (same convention: E_clean - E_pristine(-147.304 eV))
    ebind_emb_uall = [-5.008, -6.487, -3.484]

    # Total Cell Magnetization (mu_B)
    mag_ads_vdw  = [24.00, 28.42, 25.00]
    mag_ads_ucr  = [24.00, 28.42, 25.00]
    mag_ads_uall = [27.00, 30.00, np.nan] # Co_ads clean: 27.0 (+H: 28.0); Fe_ads clean: 30.0 mu_B

    mag_emb_vdw  = [24.00, 27.37, 25.00]
    mag_emb_ucr  = [24.00, 27.37, 25.00]
    mag_emb_uall = [29.00, 30.00, 28.00] # Co_emb 29.0 (+H 28.0); Fe_emb 30.0 (+H 29.0); Ni_emb 28.0 (+H 27.0)

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

    # Plot Bars
    b_a1 = ax_a.bar(x + offsets[0], dg_ads_vdw,  width, color=c_ads_vdw,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_a2 = ax_a.bar(x + offsets[1], dg_ads_ucr,  width, color=c_ads_ucr,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    # Tier 3 Adsorbed: Co_ads converged (+0.065 eV); Fe and Ni in progress
    for m_idx in range(3):
        x_pos = x[m_idx] + offsets[2]
        val = dg_ads_uall[m_idx]
        if not np.isnan(val):
            ax_a.bar(x_pos, val, width, color=c_ads_uall, edgecolor='#0e2f44', linewidth=0.9, zorder=3)
            va_align = 'bottom' if val >= 0 else 'top'
            y_pos = val + 0.05 if val >= 0 else val - 0.06
            txt = f'{val:+.2f}' if abs(val) < 1.0 else f'{val:.2f}'
            if abs(val - 0.065) < 0.01:
                txt = f'{val:+.2f}\n$\\star$ Apex'
            ax_a.text(x_pos, y_pos, txt, ha='center', va=va_align,
                      fontsize=7.0, fontweight='bold', bbox=CARD_STYLE, zorder=5)
        else:
            ax_a.bar(x_pos, 0.08, width, bottom=0.0, fill=False, edgecolor=c_ads_uall,
                     linestyle='--', hatch='///', linewidth=0.9, zorder=3)
            ax_a.text(x_pos, 0.14, label_ads_uall[m_idx], ha='center', va='bottom',
                      fontsize=6.2, fontweight='bold',
                      bbox=RUNNING_CARD if 'Run' in label_ads_uall[m_idx] else QUEUED_CARD, zorder=5)

    b_a4 = ax_a.bar(x + offsets[3], dg_emb_vdw,  width, color=c_emb_vdw,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_a5 = ax_a.bar(x + offsets[4], dg_emb_ucr,  width, color=c_emb_ucr,  edgecolor='#935116', linewidth=0.9, zorder=3)
    # Tier 3 Embedded: Fe_emb converged (1.821 eV); Co and Ni queued
    for m_idx in range(3):
        x_pos = x[m_idx] + offsets[5]
        val = dg_emb_uall[m_idx]
        if not np.isnan(val):
            ax_a.bar(x_pos, val, width, color=c_emb_uall, edgecolor='#4a2800', linewidth=0.9, zorder=3)
            ax_a.text(x_pos, val + 0.05, f'{val:.2f}', ha='center', va='bottom',
                      fontsize=7.0, fontweight='bold', bbox=CARD_STYLE, zorder=5)
        else:
            ax_a.bar(x_pos, 0.08, width, bottom=0.0, fill=False, edgecolor=c_emb_uall,
                     linestyle='--', hatch='///', linewidth=0.9, zorder=3)
            ax_a.text(x_pos, 0.14, label_emb_uall[m_idx], ha='center', va='bottom',
                      fontsize=6.2, fontweight='bold', bbox=QUEUED_CARD, zorder=5)

    # Annotate converged Tier 1 & Tier 2 bars
    for g_idx, (actual_bars, vals) in enumerate([(b_a1, dg_ads_vdw), (b_a2, dg_ads_ucr), (b_a4, dg_emb_vdw), (b_a5, dg_emb_ucr)]):
        y_stagger = 0.05 if (g_idx % 2 == 0) else 0.14
        for bar, val in zip(actual_bars, vals):
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
    # Tier 3 Adsorbed: Co_ads converged (-0.191 eV); Fe and Ni in progress
    for m_idx in range(3):
        x_pos = x[m_idx] + offsets[2]
        val = eads_ads_uall[m_idx]
        if not np.isnan(val):
            ax_b.bar(x_pos, val, width, color=c_ads_uall, edgecolor='#0e2f44', linewidth=0.9, zorder=3)
            va_align = 'bottom' if val >= 0 else 'top'
            y_pos = val + 0.05 if val >= 0 else val - 0.06
            txt = f'{val:+.2f}' if abs(val) < 1.0 else f'{val:.2f}'
            ax_b.text(x_pos, y_pos, txt, ha='center', va=va_align,
                      fontsize=7.0, fontweight='bold', bbox=CARD_STYLE, zorder=5)
        else:
            ax_b.bar(x_pos, 0.08, width, bottom=0.0, fill=False, edgecolor=c_ads_uall,
                     linestyle='--', hatch='///', linewidth=0.9, zorder=3)
            y_label = 0.26 if m_idx == 1 else 0.16
            ax_b.text(x_pos, y_label, label_ads_uall[m_idx], ha='center', va='bottom',
                      fontsize=6.2, fontweight='bold',
                      bbox=RUNNING_CARD if 'Run' in label_ads_uall[m_idx] else QUEUED_CARD, zorder=5)

    b_b4 = ax_b.bar(x + offsets[3], eads_emb_vdw,  width, color=c_emb_vdw,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_b5 = ax_b.bar(x + offsets[4], eads_emb_ucr,  width, color=c_emb_ucr,  edgecolor='#935116', linewidth=0.9, zorder=3)
    for m_idx in range(3):
        x_pos = x[m_idx] + offsets[5]
        val = eads_emb_uall[m_idx]
        if not np.isnan(val):
            ax_b.bar(x_pos, val, width, color=c_emb_uall, edgecolor='#4a2800', linewidth=0.9, zorder=3)
            ax_b.text(x_pos, val + 0.05, f'{val:.2f}', ha='center', va='bottom',
                      fontsize=7.0, fontweight='bold', bbox=CARD_STYLE, zorder=5)
        else:
            ax_b.bar(x_pos, 0.08, width, bottom=0.0, fill=False, edgecolor=c_emb_uall,
                     linestyle='--', hatch='///', linewidth=0.9, zorder=3)
            ax_b.text(x_pos, 0.16, label_emb_uall[m_idx], ha='center', va='bottom',
                      fontsize=6.2, fontweight='bold', bbox=QUEUED_CARD, zorder=5)

    for g_idx, (actual_bars, vals) in enumerate([(b_b1, eads_ads_vdw), (b_b2, eads_ads_ucr), (b_b4, eads_emb_vdw), (b_b5, eads_emb_ucr)]):
        y_stagger = 0.05 if (g_idx % 2 == 0) else 0.12
        for bar, val in zip(actual_bars, vals):
            va_align = 'bottom' if val >= 0 else 'top'
            # For Fe Ads +U_Cr (+0.005 eV), shift down to avoid collision with [Running]
            if abs(val - 0.005) < 0.001:
                y_pos = -0.06
                va_align = 'top'
            else:
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
    # Tier 3 Adsorbed: Fe_ads clean converged (-6.643 eV); Co and Ni queued/running
    for m_idx in range(3):
        x_pos = x[m_idx] + offsets[2]
        val = ebind_ads_uall[m_idx]
        if not np.isnan(val):
            ax_c.bar(x_pos, val, width, color=c_ads_uall, edgecolor='#0e2f44', linewidth=0.9, zorder=3)
            ax_c.text(x_pos, val - 0.16, f'{val:.2f}', ha='center', va='top',
                      fontsize=6.8, fontweight='bold', bbox=CARD_STYLE, zorder=5)
        else:
            ax_c.bar(x_pos, -0.40, width, bottom=0.0, fill=False, edgecolor=c_ads_uall,
                     linestyle='--', hatch='///', linewidth=0.9, zorder=3)
            ax_c.text(x_pos, -0.55, label_ads_uall[m_idx], ha='center', va='top',
                      fontsize=6.2, fontweight='bold',
                      bbox=RUNNING_CARD if 'Run' in label_ads_uall[m_idx] else QUEUED_CARD, zorder=5)

    b_c4 = ax_c.bar(x + offsets[3], ebind_emb_vdw,  width, color=c_emb_vdw,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_c5 = ax_c.bar(x + offsets[4], ebind_emb_ucr,  width, color=c_emb_ucr,  edgecolor='#935116', linewidth=0.9, zorder=3)
    # Tier 3 Embedded: Co_emb clean (-5.01 eV) and Fe_emb clean (-6.49 eV) converged; Ni queued
    for m_idx in range(3):
        x_pos = x[m_idx] + offsets[5]
        val = ebind_emb_uall[m_idx]
        if not np.isnan(val):
            ax_c.bar(x_pos, val, width, color=c_emb_uall, edgecolor='#4a2800', linewidth=0.9, zorder=3)
            ax_c.text(x_pos, val - 0.16, f'{val:.2f}', ha='center', va='top',
                      fontsize=6.8, fontweight='bold', bbox=CARD_STYLE, zorder=5)
        else:
            ax_c.bar(x_pos, -0.40, width, bottom=0.0, fill=False, edgecolor=c_emb_uall,
                     linestyle='--', hatch='///', linewidth=0.9, zorder=3)
            ax_c.text(x_pos, -0.55, label_emb_uall[m_idx], ha='center', va='top',
                      fontsize=6.2, fontweight='bold', bbox=QUEUED_CARD, zorder=5)

    for g_idx, (actual_bars, vals) in enumerate([(b_c1, ebind_ads_vdw), (b_c2, ebind_ads_ucr), (b_c4, ebind_emb_vdw), (b_c5, ebind_emb_ucr)]):
        y_stagger = 0.14 if (g_idx % 2 == 0) else 0.50
        for bar, val in zip(actual_bars, vals):
            ax_c.text(bar.get_x() + bar.get_width()/2.0, val - y_stagger, f'{val:.2f}',
                      ha='center', va='top', fontsize=6.8, fontweight='bold',
                      bbox=CARD_STYLE, zorder=5)

    # Penetration driving force Delta Delta E = E_emb - E_ads (under +U_Cr)
    ax_c.annotate(r'$\mathbf{\Delta\Delta E = -1.41\,\mathrm{eV}}$' + '\n' + r'Pore Favored ($+U_{\mathrm{Cr}}$)',
                  xy=(x[1] + offsets[4], 0.0), xytext=(x[1], 1.05),
                  arrowprops=dict(arrowstyle='->', color='#935116', lw=1.3),
                  fontsize=8.0, fontweight='bold', color='#935116', bbox=CARD_STYLE, ha='center', zorder=6)

    ax_c.annotate(r'$\mathbf{\Delta\Delta E = -0.24\,\mathrm{eV}}$' + '\n' + r'Near Bistable ($+U_{\mathrm{Cr}}$)',
                  xy=(x[0] + offsets[4], 0.0), xytext=(x[0], 1.05),
                  arrowprops=dict(arrowstyle='->', color='#935116', lw=1.3),
                  fontsize=8.0, fontweight='bold', color='#935116', bbox=CARD_STYLE, ha='center', zorder=6)

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

    ax_d.axhline(24.00, color='#34495e', linestyle=':', linewidth=1.5,
                 label=r'Pristine $\mathrm{CrCl}_3$ Baseline ($24.0\,\mu_B$)', zorder=2)

    b_d1 = ax_d.bar(x + offsets[0], mag_ads_vdw,  width, color=c_ads_vdw,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    b_d2 = ax_d.bar(x + offsets[1], mag_ads_ucr,  width, color=c_ads_ucr,  edgecolor='#1a5276', linewidth=0.9, zorder=3)
    # Tier 3 Adsorbed: Co_ads (28.0) and Fe_ads (30.0) converged; Ni queued
    for m_idx in range(3):
        x_pos = x[m_idx] + offsets[2]
        val = mag_ads_uall[m_idx]
        if not np.isnan(val):
            ax_d.bar(x_pos, val, width, color=c_ads_uall, edgecolor='#0e2f44', linewidth=0.9, zorder=3)
            diff = val - 24.00
            ax_d.text(x_pos, val + 0.35, f'{val:.1f}\n(+{diff:.0f}$\\,\\mu_B$)',
                      ha='center', va='bottom', fontsize=6.5, fontweight='bold', bbox=CARD_STYLE, zorder=5)
        else:
            ax_d.bar(x_pos, 1.0, width, bottom=24.0, fill=False, edgecolor=c_ads_uall,
                     linestyle='--', hatch='///', linewidth=0.9, zorder=3)
            y_stub = 26.6 if m_idx == 2 else 25.3
            ax_d.text(x_pos, y_stub, label_ads_uall[m_idx], ha='center', va='bottom',
                      fontsize=6.2, fontweight='bold', bbox=QUEUED_CARD, zorder=5)

    b_d4 = ax_d.bar(x + offsets[3], mag_emb_vdw,  width, color=c_emb_vdw,  edgecolor='#935116', linewidth=0.9, zorder=3)
    b_d5 = ax_d.bar(x + offsets[4], mag_emb_ucr,  width, color=c_emb_ucr,  edgecolor='#935116', linewidth=0.9, zorder=3)
    # Tier 3 Embedded: Co_emb (29.0) and Fe_emb (29.0) converged; Ni queued
    for m_idx in range(3):
        x_pos = x[m_idx] + offsets[5]
        val = mag_emb_uall[m_idx]
        if not np.isnan(val):
            ax_d.bar(x_pos, val, width, color=c_emb_uall, edgecolor='#4a2800', linewidth=0.9, zorder=3)
            diff = val - 24.00
            ax_d.text(x_pos, val + 1.25, f'{val:.1f}\n(+{diff:.0f}$\\,\\mu_B$)',
                      ha='center', va='bottom', fontsize=6.5, fontweight='bold', bbox=CARD_STYLE, zorder=5)
        else:
            ax_d.bar(x_pos, 1.0, width, bottom=24.0, fill=False, edgecolor=c_emb_uall,
                     linestyle='--', hatch='///', linewidth=0.9, zorder=3)
            y_stub = 26.6 if m_idx == 2 else 25.3
            ax_d.text(x_pos, y_stub, label_emb_uall[m_idx], ha='center', va='bottom',
                      fontsize=6.2, fontweight='bold', bbox=QUEUED_CARD, zorder=5)

    # Systematically label grouped Tier 1 & Tier 2 bars across all transition metals (Zero-collision)
    # 1. Cobalt (Co):
    ax_d.text(x[0] - 2.0*width, 24.0 + 0.45,
              r'$\mathbf{24.0\,\mu_B}$' + '\n' + r'$(+0\ \mathrm{ref})$' + '\n' + r'Ads (v/U)',
              ha='center', va='bottom', fontsize=6.8, fontweight='bold', bbox=CARD_STYLE, zorder=5)
    ax_d.text(x[0] + 1.0*width, 24.0 + 0.45,
              r'$\mathbf{24.0\,\mu_B}$' + '\n' + r'$(+0\ \mathrm{ref})$' + '\n' + r'Emb (v/U)',
              ha='center', va='bottom', fontsize=6.8, fontweight='bold', bbox=CARD_STYLE, zorder=5)

    # 2. Iron (Fe):
    ax_d.text(x[1] - 2.0*width, 28.42 + 0.45,
              r'$\mathbf{28.4\,\mu_B}$' + '\n' + r'$(+4.4\,\mu_B)$' + '\n' + r'Ads (v/U)',
              ha='center', va='bottom', fontsize=6.8, fontweight='bold', bbox=CARD_STYLE, zorder=5)
    ax_d.text(x[1] + 1.0*width, 27.37 + 0.45,
              r'$\mathbf{27.4\,\mu_B}$' + '\n' + r'$(+3.4\,\mu_B)$' + '\n' + r'Emb (v/U)',
              ha='center', va='bottom', fontsize=6.8, fontweight='bold', bbox=CARD_STYLE, zorder=5)

    # 3. Nickel (Ni):
    ax_d.text(x[2] - 2.0*width, 25.0 + 0.45,
              r'$\mathbf{25.0\,\mu_B}$' + '\n' + r'$(+1\,\mu_B)$' + '\n' + r'Ads (v/U)',
              ha='center', va='bottom', fontsize=6.8, fontweight='bold', bbox=CARD_STYLE, zorder=5)
    ax_d.text(x[2] + 1.0*width, 25.0 + 0.45,
              r'$\mathbf{25.0\,\mu_B}$' + '\n' + r'$(+1\,\mu_B)$' + '\n' + r'Emb (v/U)',
              ha='center', va='bottom', fontsize=6.8, fontweight='bold', bbox=CARD_STYLE, zorder=5)

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
        "Scientific Provenance & HPC Calculation Status:\n"
        r"$\bullet$ Tier 1 (vdW): PBE+D3(BJ) [100% Converged, 12/12 Systems]" + "\n"
        r"$\bullet$ Tier 2 (+$U_{\mathrm{Cr}}$): $U_{\mathrm{Cr}}=3.29\,\mathrm{eV}$ [100% Converged, Caique Dataset]" + "\n"
        r"$\bullet$ Tier 3 (+$U_{\mathrm{all}}$): $U_{\mathrm{Cr}}=3.29\,\mathrm{eV},\ U_{\mathrm{TM}}=3.29\,\mathrm{eV}$ [11/12 Converged (92%)]" + "\n"
        r"  - Converged: Co(ads) [$\Delta G = +0.07\,\mathrm{eV}$]; Fe(ads) [$\Delta G = +1.84\,\mathrm{eV}$]" + "\n"
        r"  - Converged: Emb Co/Fe/Ni [$\Delta G = +1.39 / +1.82 / +1.02\,\mathrm{eV}$]" + "\n"
        r"  - Active Job: Ni(ads) clean relaxing on Huk (Job 8087, huk125)" + "\n"
        r"$\bullet$ Hatched boxes denote in-progress calculations (zero invented data)."
    )
    ax_d.text(0.03, 0.95, status_text, transform=ax_d.transAxes,
              fontsize=7.0, va='top', ha='left',
              fontweight='bold', fontfamily='serif',
              bbox=dict(boxstyle='round,pad=0.35', facecolor='#e8f8f5', edgecolor='#2ecc71', alpha=0.96, linewidth=1.0),
              zorder=6)

    fig.suptitle(r'Comprehensive Multitier Benchmark: Adsorbed vs. Embedded $\mathrm{CrCl}_3\text{-}\mathrm{TM}$ ($\mathrm{TM}=\mathrm{Co,Fe,Ni}$)' + '\n' +
                 r'Systematic Comparison across vdW Dispersion, Single-Site $+U_{\mathrm{Cr}}$, and Multi-Site $+U_{\mathrm{all}}$ ($U_{\mathrm{Cr}}+U_{\mathrm{TM}}$)',
                 fontsize=14.5, fontweight='bold', y=0.985)

    out_png = os.path.join(SCRIPT_DIR, "crcl3_tm_abs_vs_emb_multitier.png")
    out_pdf = os.path.join(SCRIPT_DIR, "crcl3_tm_abs_vs_emb_multitier.pdf")

    ax_d.set_ylim(20.0, 41.0)  # headroom so the provenance badge clears the bar labels
    for ax in axs.flat:
        resolve_vertical_overlaps(fig, ax)

    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")

if __name__ == '__main__':
    generate_multitier_comparison_plot()
