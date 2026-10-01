#!/usr/bin/env python3
"""
================================================================================
 plot_fig7_energy_decomposition.py
================================================================================
 Generates publication-quality bar charts for Panels (g) and (h) of Figure 7:
   - Panel (g): Surface-adsorbed TM (Co, Fe, Ni) energy decomposition
   - Panel (h): Interstitial pore embedded TM (Co, Fe, Ni) energy decomposition

 Components Plotted:
   1. E_int^H: Interaction energy with atomic hydrogen (teal)
   2. E_def: Substrate deformation penalty upon H coordination (gold)
   3. Delta G_H*: Hydrogen adsorption Gibbs free energy (navy blue)

 Fully Implements Reviewer 4/6 Point 12 & GEMINI.md Anti-Collision Policy:
   - Critical notation unification: G_ads -> Delta G_H*
   - Right y-axis label updated: Free Energy, Delta G_H* (eV)
   - Dynamic adaptive headroom (+25% buffer) so numerical values never clip top frame
   - Expanded x-axis headroom ([-0.65, 2.95]) so lower-right legend NEVER overlaps Ni bars
   - Intelligent vertical staggering for adjacent equal/close values
   - Times New Roman & STIX math typography
   - Inward tick marks, thick publication frames
   - Generates both PBE+D3+U (Tier 3 new calculations) and Converged PBE baseline
   - Automatically composites into complete Figure 7 replacements
================================================================================
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from PIL import Image

# Output directories
POST_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(POST_DIR, "../.."))
FIG_DIR = os.path.join(REPO_ROOT, "ACS_version/ACS_resubmission/figure")

# Typography adhering to publication guidelines
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.3
plt.rcParams['xtick.major.width'] = 1.3
plt.rcParams['ytick.major.width'] = 1.3
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

# Color Palette matching original Fig7
COLOR_EINT = "#48a999"   # Teal / Sea Green
COLOR_EDEF = "#f1c40f"   # Gold / Mustard Yellow
COLOR_DG   = "#0011a8"   # Royal / Navy Blue
COLOR_VAL  = "#c0392b"   # High-contrast bold red for value annotations

def render_panels(tier="pbe_d3_u", dpi=300):
    """
    Renders panels (g) and (h) for either:
      - 'pbe_d3_u': PBE+D3+U (U_Cr = 3.29 eV) + Caique exact thermochemistry
      - 'pbe_baseline': Pure PBE converged results with unified Delta G_H*
    """
    metals = ["Co", "Fe", "Ni"]
    n_metals = len(metals)
    x = np.arange(n_metals)
    width = 0.22

    # -------------------------------------------------------------
    # Energetics Data
    # -------------------------------------------------------------
    if tier == "pbe_d3_u":
        # Surface-adsorbed (g)
        # Co: -0.069 eV (optimal Sabatier)
        # Fe: +0.185 eV (promoted into active window)
        # Ni: +0.620 eV
        g_eint = np.array([-2.46, -2.35, -1.69])
        g_edef = np.array([0.18, 0.38, 0.09])
        g_dg   = np.array([-0.07, 0.19, 0.62])
        g_dg_labels = ["-0.07", "0.19", "0.62"]

        # Embedded (h)
        # Co: +1.375 -> +1.38 eV
        # Fe: +1.114 -> +1.11 eV
        # Ni: +0.821 -> +0.82 eV (Converged Step 52)
        h_eint = np.array([-0.94, -1.67, -0.82])
        h_edef = np.array([0.21, 0.55, 0.73])  # Relaxed pore deformation
        h_dg   = np.array([1.38, 1.11, 0.82])
        h_dg_labels = ["1.38", "1.11", "0.82"]

        # Y-limits with adaptive headroom (+25%)
        ylim_g = (-2.85, 1.20)
        ylim_h = (-2.10, 2.25)
        yticks_g = [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0]
        yticks_h = [-2.0, -1.0, 0.0, 1.0, 2.0]

    elif tier == "pbe_baseline":
        # Surface-adsorbed (g)
        g_eint = np.array([-2.46, -2.35, -1.69])
        g_edef = np.array([0.18, 0.38, 0.09])
        g_dg   = np.array([0.18, 0.38, 0.86])
        g_dg_labels = ["0.18", "0.38", "0.86"]

        # Embedded (h) - updated with converged Ni_emb (+1.85 eV vs old 3.62 eV)
        h_eint = np.array([-0.94, -1.67, -0.82])
        h_edef = np.array([0.21, 0.55, 1.97])
        h_dg   = np.array([1.74, 1.33, 1.85])
        h_dg_labels = ["1.74", "1.33", "1.85"]

        # Y-limits with adaptive headroom
        ylim_g = (-2.85, 1.35)
        ylim_h = (-2.10, 2.75)
        yticks_g = [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0]
        yticks_h = [-2.0, -1.0, 0.0, 1.0, 2.0]

    else:
        raise ValueError(f"Unknown tier: {tier}")

    # Broad x-limits to cleanly accommodate legend on the right without overlapping Ni
    xlim_common = (-0.65, 2.95)

    # =============================================================
    # 1. Combined Two-Panel Figure: (g) and (h) side by side
    # =============================================================
    fig, (ax_g, ax_h) = plt.subplots(1, 2, figsize=(15.2, 5.8), dpi=dpi)
    fig.subplots_adjust(left=0.08, right=0.96, bottom=0.18, top=0.90, wspace=0.28)

    # -------------------------------------------------------------
    # Panel (g): Surface-Adsorbed
    # -------------------------------------------------------------
    ax_g.axhline(0, color='red', linestyle=':', linewidth=1.6, zorder=2)
    rects_g1 = ax_g.bar(x - width, g_eint, width, color=COLOR_EINT, label=r"$E_{\mathrm{int}}^{\mathrm{H}}$", zorder=3)
    rects_g2 = ax_g.bar(x,         g_edef, width, color=COLOR_EDEF, label=r"$E_{\mathrm{def}}$", zorder=3)
    rects_g3 = ax_g.bar(x + width, g_dg,   width, color=COLOR_DG,   label=r"$\Delta G_{\mathrm{H}^*}$", zorder=3)

    # Values for panel (g)
    for rect, val in zip(rects_g1, g_eint):
        y_pos = rect.get_height() - 0.12
        ax_g.text(rect.get_x() + rect.get_width()/2.0, y_pos, f"{val:.2f}",
                  ha='center', va='top', fontsize=12, fontweight='bold', color=COLOR_VAL)

    for i, (rect, val) in enumerate(zip(rects_g2, g_edef)):
        y_pos = rect.get_height() + 0.05
        ax_g.text(rect.get_x() + rect.get_width()/2.0, y_pos, f"{val:.2f}",
                  ha='center', va='bottom', fontsize=12, fontweight='bold', color=COLOR_VAL)

    for i, (rect, (val, txt)) in enumerate(zip(rects_g3, zip(g_dg, g_dg_labels))):
        if val >= 0:
            # Check if adjacent to edef bar and close in height (e.g. Co or Fe in PBE baseline)
            diff = abs(val - g_edef[i])
            if diff < 0.05:
                y_pos = rect.get_height() + 0.16  # Stagger upward to avoid horizontal collision
            else:
                y_pos = rect.get_height() + 0.05
            va_align = 'bottom'
        else:
            # Stagger slightly lower so it doesn't touch zero-line or bar edge
            y_pos = rect.get_height() - 0.15
            va_align = 'top'
        ax_g.text(rect.get_x() + rect.get_width()/2.0, y_pos, txt,
                  ha='center', va=va_align, fontsize=12, fontweight='bold', color=COLOR_VAL)

    ax_g.set_xticks(x)
    ax_g.set_xticklabels(metals, fontsize=18)
    ax_g.set_ylabel(r"$\mathrm{Energy\ (eV)}$", fontsize=16)
    ax_g.set_xlim(xlim_common)
    ax_g.set_ylim(ylim_g)
    ax_g.set_yticks(yticks_g)
    ax_g.tick_params(direction='in', which='both', top=True, right=True, labelsize=14)
    # Legend with clean background framing
    ax_g.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.95,
                fontsize=15, handlelength=1.4, handleheight=0.8, borderaxespad=0.8, labelspacing=0.35)
    # Centered subpanel label below
    fig.text(0.28, 0.04, "(g)", ha='center', va='center', fontsize=22)

    # -------------------------------------------------------------
    # Panel (h): Embedded Interstitial
    # -------------------------------------------------------------
    ax_h.axhline(0, color='red', linestyle=':', linewidth=1.6, zorder=2)
    rects_h1 = ax_h.bar(x - width, h_eint, width, color=COLOR_EINT, label=r"$E_{\mathrm{int}}^{\mathrm{H}}$", zorder=3)
    rects_h2 = ax_h.bar(x,         h_edef, width, color=COLOR_EDEF, label=r"$E_{\mathrm{def}}$", zorder=3)
    rects_h3 = ax_h.bar(x + width, h_dg,   width, color=COLOR_DG,   label=r"$\Delta G_{\mathrm{H}^*}$", zorder=3)

    # Values for panel (h)
    for rect, val in zip(rects_h1, h_eint):
        y_pos = rect.get_height() - 0.12
        ax_h.text(rect.get_x() + rect.get_width()/2.0, y_pos, f"{val:.2f}",
                  ha='center', va='top', fontsize=12, fontweight='bold', color=COLOR_VAL)

    for i, (rect, val) in enumerate(zip(rects_h2, h_edef)):
        # For Ni in pbe_baseline (1.97 and 1.85 are close), elevate 1.97 slightly
        if tier == "pbe_baseline" and i == 2:
            y_pos = rect.get_height() + 0.15
        else:
            y_pos = rect.get_height() + 0.05
        ax_h.text(rect.get_x() + rect.get_width()/2.0, y_pos, f"{val:.2f}",
                  ha='center', va='bottom', fontsize=12, fontweight='bold', color=COLOR_VAL)

    for i, (rect, (val, txt)) in enumerate(zip(rects_h3, zip(h_dg, h_dg_labels))):
        # If Ni in pbe_d3_u (0.73 and 0.82 are close), stagger 0.82 slightly higher
        y_offset = 0.14 if (tier == "pbe_d3_u" and i == 2) else 0.05
        y_pos = rect.get_height() + y_offset
        ax_h.text(rect.get_x() + rect.get_width()/2.0, y_pos, txt,
                  ha='center', va='bottom', fontsize=12, fontweight='bold', color=COLOR_VAL)

    ax_h.set_xticks(x)
    ax_h.set_xticklabels(metals, fontsize=18)
    # Reviewer 4/6 Point 12 mandate: right y-axis Free Energy, \Delta G_{H^*} (eV)
    ax_h.set_ylabel(r"$\mathrm{Free\ Energy,\ }\Delta G_{\mathrm{H}^*}\ \mathrm{(eV)}$", fontsize=16)
    ax_h.set_xlim(xlim_common)
    ax_h.set_ylim(ylim_h)
    ax_h.set_yticks(yticks_h)
    ax_h.tick_params(direction='in', which='both', top=True, right=True, labelsize=14)
    # Legend with clean background framing
    ax_h.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.95,
                fontsize=15, handlelength=1.4, handleheight=0.8, borderaxespad=0.8, labelspacing=0.35)
    # Centered subpanel label below
    fig.text(0.74, 0.04, "(h)", ha='center', va='center', fontsize=22)

    # Save combined
    combined_png = os.path.join(POST_DIR, f"fig7_panels_gh_{tier}.png")
    combined_pdf = os.path.join(POST_DIR, f"fig7_panels_gh_{tier}.pdf")
    fig.savefig(combined_png, dpi=dpi)
    fig.savefig(combined_pdf)
    plt.close(fig)
    print(f"[✓] Saved combined figure: {combined_png} and {combined_pdf}")

    # =============================================================
    # 2. Standalone Panel (g)
    # =============================================================
    fig_g, ax_single_g = plt.subplots(figsize=(7.5, 5.2), dpi=dpi)
    fig_g.subplots_adjust(left=0.15, right=0.94, bottom=0.18, top=0.92)

    ax_single_g.axhline(0, color='red', linestyle=':', linewidth=1.6, zorder=2)
    rg1 = ax_single_g.bar(x - width, g_eint, width, color=COLOR_EINT, label=r"$E_{\mathrm{int}}^{\mathrm{H}}$", zorder=3)
    rg2 = ax_single_g.bar(x,         g_edef, width, color=COLOR_EDEF, label=r"$E_{\mathrm{def}}$", zorder=3)
    rg3 = ax_single_g.bar(x + width, g_dg,   width, color=COLOR_DG,   label=r"$\Delta G_{\mathrm{H}^*}$", zorder=3)

    for rect, val in zip(rg1, g_eint):
        ax_single_g.text(rect.get_x() + rect.get_width()/2.0, rect.get_height() - 0.12, f"{val:.2f}",
                         ha='center', va='top', fontsize=13, fontweight='bold', color=COLOR_VAL)
    for i, (rect, val) in enumerate(zip(rg2, g_edef)):
        ax_single_g.text(rect.get_x() + rect.get_width()/2.0, rect.get_height() + 0.05, f"{val:.2f}",
                         ha='center', va='bottom', fontsize=13, fontweight='bold', color=COLOR_VAL)
    for i, (rect, (val, txt)) in enumerate(zip(rg3, zip(g_dg, g_dg_labels))):
        if val >= 0:
            diff = abs(val - g_edef[i])
            y_pos = rect.get_height() + (0.16 if diff < 0.05 else 0.05)
            va_pos = 'bottom'
        else:
            y_pos = rect.get_height() - 0.15
            va_pos = 'top'
        ax_single_g.text(rect.get_x() + rect.get_width()/2.0, y_pos, txt,
                         ha='center', va=va_pos, fontsize=13, fontweight='bold', color=COLOR_VAL)

    ax_single_g.set_xticks(x)
    ax_single_g.set_xticklabels(metals, fontsize=18)
    ax_single_g.set_ylabel(r"$\mathrm{Energy\ (eV)}$", fontsize=17)
    ax_single_g.set_xlim(xlim_common)
    ax_single_g.set_ylim(ylim_g)
    ax_single_g.set_yticks(yticks_g)
    ax_single_g.tick_params(direction='in', which='both', top=True, right=True, labelsize=14)
    ax_single_g.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.95,
                       fontsize=16, handlelength=1.4, borderaxespad=0.8)
    fig_g.text(0.55, 0.04, "(g)", ha='center', va='center', fontsize=24)

    single_g_png = os.path.join(POST_DIR, f"fig7_panel_g_{tier}.png")
    fig_g.savefig(single_g_png, dpi=dpi)
    plt.close(fig_g)
    print(f"[✓] Saved standalone panel (g): {single_g_png}")

    # =============================================================
    # 3. Standalone Panel (h)
    # =============================================================
    fig_h, ax_single_h = plt.subplots(figsize=(7.5, 5.2), dpi=dpi)
    fig_h.subplots_adjust(left=0.15, right=0.94, bottom=0.18, top=0.92)

    ax_single_h.axhline(0, color='red', linestyle=':', linewidth=1.6, zorder=2)
    rh1 = ax_single_h.bar(x - width, h_eint, width, color=COLOR_EINT, label=r"$E_{\mathrm{int}}^{\mathrm{H}}$", zorder=3)
    rh2 = ax_single_h.bar(x,         h_edef, width, color=COLOR_EDEF, label=r"$E_{\mathrm{def}}$", zorder=3)
    rh3 = ax_single_h.bar(x + width, h_dg,   width, color=COLOR_DG,   label=r"$\Delta G_{\mathrm{H}^*}$", zorder=3)

    for rect, val in zip(rh1, h_eint):
        ax_single_h.text(rect.get_x() + rect.get_width()/2.0, rect.get_height() - 0.12, f"{val:.2f}",
                         ha='center', va='top', fontsize=13, fontweight='bold', color=COLOR_VAL)
    for i, (rect, val) in enumerate(zip(rh2, h_edef)):
        if tier == "pbe_baseline" and i == 2:
            y_pos = rect.get_height() + 0.15
        else:
            y_pos = rect.get_height() + 0.05
        ax_single_h.text(rect.get_x() + rect.get_width()/2.0, y_pos, f"{val:.2f}",
                         ha='center', va='bottom', fontsize=13, fontweight='bold', color=COLOR_VAL)
    for i, (rect, (val, txt)) in enumerate(zip(rh3, zip(h_dg, h_dg_labels))):
        y_offset = 0.14 if (tier == "pbe_d3_u" and i == 2) else 0.05
        ax_single_h.text(rect.get_x() + rect.get_width()/2.0, rect.get_height() + y_offset, txt,
                         ha='center', va='bottom', fontsize=13, fontweight='bold', color=COLOR_VAL)

    ax_single_h.set_xticks(x)
    ax_single_h.set_xticklabels(metals, fontsize=18)
    ax_single_h.set_ylabel(r"$\mathrm{Free\ Energy,\ }\Delta G_{\mathrm{H}^*}\ \mathrm{(eV)}$", fontsize=17)
    ax_single_h.set_xlim(xlim_common)
    ax_single_h.set_ylim(ylim_h)
    ax_single_h.set_yticks(yticks_h)
    ax_single_h.tick_params(direction='in', which='both', top=True, right=True, labelsize=14)
    ax_single_h.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.95,
                       fontsize=16, handlelength=1.4, borderaxespad=0.8)
    fig_h.text(0.55, 0.04, "(h)", ha='center', va='center', fontsize=24)

    single_h_png = os.path.join(POST_DIR, f"fig7_panel_h_{tier}.png")
    fig_h.savefig(single_h_png, dpi=dpi)
    plt.close(fig_h)
    print(f"[✓] Saved standalone panel (h): {single_h_png}")


def render_multitier_comparison(dpi=300):
    """
    Renders a multi-tier comparison bar chart in panels (g) and (h):
    Directly compares E_int, E_def, Delta G_H*(PBE), and Delta G_H*(PBE+D3+U).
    """
    metals = ["Co", "Fe", "Ni"]
    x = np.arange(len(metals))
    width = 0.18

    # Colors
    c_eint = COLOR_EINT
    c_edef = COLOR_EDEF
    c_dgpbe = "#34495e"   # Slate Charcoal Blue
    c_dgu   = COLOR_DG   # Royal Navy Blue

    # Data
    # Surface
    g_eint = np.array([-2.46, -2.35, -1.69])
    g_edef = np.array([0.18, 0.38, 0.09])
    g_dgpbe = np.array([0.18, 0.38, 0.86])
    g_dgu   = np.array([-0.07, 0.19, 0.62])

    # Embedded
    h_eint = np.array([-0.94, -1.67, -0.82])
    h_edef = np.array([0.21, 0.55, 0.73])
    h_dgpbe = np.array([1.74, 1.33, 1.85])
    h_dgu   = np.array([1.38, 1.11, 0.82])

    fig, (ax_g, ax_h) = plt.subplots(1, 2, figsize=(16.0, 6.0), dpi=dpi)
    fig.subplots_adjust(left=0.08, right=0.96, bottom=0.18, top=0.90, wspace=0.28)

    xlim_multi = (-0.65, 3.10)

    for ax, eint, edef, dgpbe, dgu, is_emb, sublabel in [
        (ax_g, g_eint, g_edef, g_dgpbe, g_dgu, False, "(g)"),
        (ax_h, h_eint, h_edef, h_dgpbe, h_dgu, True,  "(h)")
    ]:
        ax.axhline(0, color='red', linestyle=':', linewidth=1.6, zorder=2)
        r1 = ax.bar(x - 1.5*width, eint,  width, color=c_eint, label=r"$E_{\mathrm{int}}^{\mathrm{H}}$", zorder=3)
        r2 = ax.bar(x - 0.5*width, edef,  width, color=c_edef, label=r"$E_{\mathrm{def}}$", zorder=3)
        r3 = ax.bar(x + 0.5*width, dgpbe, width, color=c_dgpbe, label=r"$\Delta G_{\mathrm{H}^*}\ (\mathrm{PBE})$", zorder=3)
        r4 = ax.bar(x + 1.5*width, dgu,   width, color=c_dgu,   label=r"$\Delta G_{\mathrm{H}^*}\ (\mathrm{PBE+D3+}U)$", zorder=3)

        # Labels
        for r, val in zip(r1, eint):
            ax.text(r.get_x() + r.get_width()/2.0, val - 0.12, f"{val:.2f}",
                    ha='center', va='top', fontsize=10.5, fontweight='bold', color=COLOR_VAL)
        for r, val in zip(r2, edef):
            ax.text(r.get_x() + r.get_width()/2.0, val + 0.05, f"{val:.2f}",
                    ha='center', va='bottom', fontsize=10.5, fontweight='bold', color=COLOR_VAL)
        for r, val in zip(r3, dgpbe):
            ax.text(r.get_x() + r.get_width()/2.0, val + 0.05, f"{val:.2f}",
                    ha='center', va='bottom', fontsize=10.5, fontweight='bold', color=COLOR_VAL)
        for r, val in zip(r4, dgu):
            y_pos = val + (0.05 if val >= 0 else -0.15)
            va_align = 'bottom' if val >= 0 else 'top'
            ax.text(r.get_x() + r.get_width()/2.0, y_pos, f"{val:.2f}",
                    ha='center', va=va_align, fontsize=10.5, fontweight='bold', color=COLOR_VAL)

        ax.set_xticks(x)
        ax.set_xticklabels(metals, fontsize=18)
        ax.set_xlim(xlim_multi)
        if not is_emb:
            ax.set_ylabel(r"$\mathrm{Energy\ (eV)}$", fontsize=16)
            ax.set_ylim(-2.85, 1.25)
            ax.set_yticks([-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0])
        else:
            ax.set_ylabel(r"$\mathrm{Free\ Energy,\ }\Delta G_{\mathrm{H}^*}\ \mathrm{(eV)}$", fontsize=16)
            ax.set_ylim(-2.10, 2.45)
            ax.set_yticks([-2.0, -1.0, 0.0, 1.0, 2.0])

        ax.tick_params(direction='in', which='both', top=True, right=True, labelsize=14)
        ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.95,
                  fontsize=13, handlelength=1.4, borderaxespad=0.6)

    fig.text(0.28, 0.04, "(g)", ha='center', va='center', fontsize=22)
    fig.text(0.74, 0.04, "(h)", ha='center', va='center', fontsize=22)

    comp_png = os.path.join(POST_DIR, "fig7_panels_gh_multitier.png")
    comp_pdf = os.path.join(POST_DIR, "fig7_panels_gh_multitier.pdf")
    fig.savefig(comp_png, dpi=dpi)
    fig.savefig(comp_pdf)
    plt.close(fig)
    print(f"[✓] Saved multitier comparison figure: {comp_png}")


def generate_composite_fig7_replacement(tier="pbe_d3_u"):
    """
    Creates an updated full Fig7 image by cleanly splicing the new panels (g) and (h)
    into the original composite Fig7.png at exact alignment.
    """
    orig_fig7 = os.path.join(FIG_DIR, "Fig7.png")
    if not os.path.exists(orig_fig7):
        print(f"[!] Original Fig7 not found at {orig_fig7}")
        return

    orig_im = Image.open(orig_fig7).convert("RGB")
    W, H = orig_im.size

    # Load the standalone panels generated at 300 DPI
    p_g_path = os.path.join(POST_DIR, f"fig7_panel_g_{tier}.png")
    p_h_path = os.path.join(POST_DIR, f"fig7_panel_h_{tier}.png")
    if not (os.path.exists(p_g_path) and os.path.exists(p_h_path)):
        return

    # In original Fig7 (3810 x 3942):
    # Rows 0 to 2640 contain panels (a - f) and their subpanel labels (d, e, f)
    # Rows 2660 to 3942 contain panels (g, h)
    im_g = Image.open(p_g_path)
    im_h = Image.open(p_h_path)

    target_top = 2650
    target_height = H - target_top  # 1292 px
    half_width = W // 2             # 1905 px

    # Resize individual panels to precisely fit the composite slots
    resized_g = im_g.resize((half_width, target_height), Image.Resampling.LANCZOS)
    resized_h = im_h.resize((W - half_width, target_height), Image.Resampling.LANCZOS)

    composite = orig_im.copy()
    composite.paste(resized_g, (0, target_top))
    composite.paste(resized_h, (half_width, target_top))

    out_comp = os.path.join(POST_DIR, f"Fig7_composite_{tier}.png")
    composite.save(out_comp)
    print(f"[✓] Saved full composite: {out_comp}")


if __name__ == "__main__":
    print("Generating Figure 7 panels (g) and (h) with new calculation results...")
    # 1. PBE+D3+U (Tier 3)
    render_panels(tier="pbe_d3_u", dpi=300)
    generate_composite_fig7_replacement(tier="pbe_d3_u")

    # 2. Pure PBE baseline (converged)
    render_panels(tier="pbe_baseline", dpi=300)
    generate_composite_fig7_replacement(tier="pbe_baseline")

    # 3. Multitier comparison
    render_multitier_comparison(dpi=300)

    print("All tasks completed successfully!")
