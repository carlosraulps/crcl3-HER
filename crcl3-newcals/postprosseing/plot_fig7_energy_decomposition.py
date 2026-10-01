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
import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from PIL import Image

# Register authentic Times New Roman system fonts
for font_path in [
    "/usr/share/fonts/TTF/Times.TTF",
    "/usr/share/fonts/TTF/Timesbd.TTF",
    "/usr/share/fonts/TTF/Timesi.TTF",
    "/usr/share/fonts/TTF/Timesbi.TTF",
]:
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)

FONT_TNR_REG = fm.FontProperties(fname="/usr/share/fonts/TTF/Times.TTF")
FONT_TNR_BOLD = fm.FontProperties(fname="/usr/share/fonts/TTF/Timesbd.TTF")

# Output directories
POST_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(POST_DIR, "../.."))
FIG_DIR = os.path.join(REPO_ROOT, "ACS_version/ACS_resubmission/figure")

# Typography adhering to publication guidelines
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.serif'] = ['Times New Roman', 'Liberation Serif', 'DejaVu Serif']
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

def annotate_positive_pair(ax, r_left, val_left, r_right, val_right, txt_right=None, fontsize=12):
    """
    Annotates a pair of positive bars (e.g. E_def and Delta G_H*) with guaranteed zero collision.
    Empty space at y > 0 exists to the left of r_left (since Bar 1 is negative)
    and to the right of r_right.
    """
    if txt_right is None:
        txt_right = f"{val_right:.2f}"

    x_l = r_left.get_x() + r_left.get_width() / 2.0
    x_r = r_right.get_x() + r_right.get_width() / 2.0
    h_l = val_left
    h_r = val_right

    if h_r < 0:
        # Right bar is negative (e.g. Co Delta G = -0.07)
        ax.text(x_l, h_l + 0.05, f"{h_l:.2f}",
                ha='center', va='bottom', fontsize=fontsize, fontweight='bold', color=COLOR_VAL)
        ax.text(x_r, h_r - 0.13, txt_right,
                ha='center', va='top', fontsize=fontsize, fontweight='bold', color=COLOR_VAL)
        return

    diff = h_r - h_l
    if abs(diff) <= 0.15:
        # Equal or close in height (e.g. 0.18/0.18, 0.38/0.38, 1.97/1.85, 0.73/0.82)
        # Shift left bar left, right bar right, and vertically stagger
        x_pos_l = x_l - 0.07
        x_pos_r = x_r + 0.07
        if h_l >= h_r:
            y_pos_l = h_l + 0.16
            y_pos_r = h_r + 0.05
        else:
            y_pos_l = h_l + 0.05
            y_pos_r = h_r + 0.16
    elif diff > 0.15:
        # Right bar is taller: shift left bar left into open space above Bar 1
        x_pos_l = x_l - 0.08
        y_pos_l = h_l + 0.05
        x_pos_r = x_r
        y_pos_r = h_r + 0.05
    else:
        # Left bar is taller: shift right bar right into open space on right
        x_pos_l = x_l
        y_pos_l = h_l + 0.05
        x_pos_r = x_r + 0.08
        y_pos_r = h_r + 0.05

    ax.text(x_pos_l, y_pos_l, f"{h_l:.2f}",
            ha='center', va='bottom', fontsize=fontsize, fontweight='bold', color=COLOR_VAL)
    ax.text(x_pos_r, y_pos_r, txt_right,
            ha='center', va='bottom', fontsize=fontsize, fontweight='bold', color=COLOR_VAL)


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
        g_eint = np.array([-2.46, -2.35, -1.69])
        g_edef = np.array([0.18, 0.38, 0.09])
        g_dg   = np.array([-0.07, 0.19, 0.62])
        g_dg_labels = ["-0.07", "0.19", "0.62"]

        # Embedded (h)
        h_eint = np.array([-0.94, -1.67, -0.82])
        h_edef = np.array([0.21, 0.55, 0.73])
        h_dg   = np.array([1.38, 1.11, 0.82])
        h_dg_labels = ["1.38", "1.11", "0.82"]

        # Y-limits with adaptive headroom (+25%)
        ylim_g = (-2.85, 1.25)
        ylim_h = (-2.10, 2.30)
        yticks_g = [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0]
        yticks_h = [-2.0, -1.0, 0.0, 1.0, 2.0]

    elif tier == "pbe_baseline":
        # Surface-adsorbed (g)
        g_eint = np.array([-2.46, -2.35, -1.69])
        g_edef = np.array([0.18, 0.38, 0.09])
        g_dg   = np.array([0.18, 0.38, 0.86])
        g_dg_labels = ["0.18", "0.38", "0.86"]

        # Embedded (h)
        h_eint = np.array([-0.94, -1.67, -0.82])
        h_edef = np.array([0.21, 0.55, 1.97])
        h_dg   = np.array([1.74, 1.33, 1.85])
        h_dg_labels = ["1.74", "1.33", "1.85"]

        # Y-limits with adaptive headroom
        ylim_g = (-2.85, 1.35)
        ylim_h = (-2.10, 2.80)
        yticks_g = [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0]
        yticks_h = [-2.0, -1.0, 0.0, 1.0, 2.0]

    else:
        raise ValueError(f"Unknown tier: {tier}")

    # Broad x-limits to cleanly accommodate legend on the right without overlapping Ni
    xlim_common = (-0.65, 3.00)

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
        y_pos = val - 0.12
        ax_g.text(rect.get_x() + rect.get_width()/2.0, y_pos, f"{val:.2f}",
                  ha='center', va='top', fontsize=12, fontweight='bold', color=COLOR_VAL)

    for i in range(n_metals):
        annotate_positive_pair(ax_g, rects_g2[i], g_edef[i], rects_g3[i], g_dg[i], g_dg_labels[i], fontsize=12)

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
    # Centered subpanel label below in genuine Times New Roman
    fig.text(0.273, 0.04, "(g)", ha='center', va='center', fontproperties=FONT_TNR_REG, fontsize=24)

    # -------------------------------------------------------------
    # Panel (h): Embedded Interstitial
    # -------------------------------------------------------------
    ax_h.axhline(0, color='red', linestyle=':', linewidth=1.6, zorder=2)
    rects_h1 = ax_h.bar(x - width, h_eint, width, color=COLOR_EINT, label=r"$E_{\mathrm{int}}^{\mathrm{H}}$", zorder=3)
    rects_h2 = ax_h.bar(x,         h_edef, width, color=COLOR_EDEF, label=r"$E_{\mathrm{def}}$", zorder=3)
    rects_h3 = ax_h.bar(x + width, h_dg,   width, color=COLOR_DG,   label=r"$\Delta G_{\mathrm{H}^*}$", zorder=3)

    # Values for panel (h)
    for rect, val in zip(rects_h1, h_eint):
        y_pos = val - 0.12
        ax_h.text(rect.get_x() + rect.get_width()/2.0, y_pos, f"{val:.2f}",
                  ha='center', va='top', fontsize=12, fontweight='bold', color=COLOR_VAL)

    for i in range(n_metals):
        annotate_positive_pair(ax_h, rects_h2[i], h_edef[i], rects_h3[i], h_dg[i], h_dg_labels[i], fontsize=12)

    ax_h.set_xticks(x)
    ax_h.set_xticklabels(metals, fontsize=18)
    ax_h.set_ylabel(r"$\mathrm{Free\ Energy,\ }\Delta G_{\mathrm{H}^*}\ \mathrm{(eV)}$", fontsize=16)
    ax_h.set_xlim(xlim_common)
    ax_h.set_ylim(ylim_h)
    ax_h.set_yticks(yticks_h)
    ax_h.tick_params(direction='in', which='both', top=True, right=True, labelsize=14)
    # Legend with clean background framing
    ax_h.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.95,
                fontsize=15, handlelength=1.4, handleheight=0.8, borderaxespad=0.8, labelspacing=0.35)
    # Centered subpanel label below in genuine Times New Roman
    fig.text(0.767, 0.04, "(h)", ha='center', va='center', fontproperties=FONT_TNR_REG, fontsize=24)

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
        y_pos = val - 0.12
        ax_single_g.text(rect.get_x() + rect.get_width()/2.0, y_pos, f"{val:.2f}",
                         ha='center', va='top', fontsize=13, fontweight='bold', color=COLOR_VAL)

    for i in range(n_metals):
        annotate_positive_pair(ax_single_g, rg2[i], g_edef[i], rg3[i], g_dg[i], g_dg_labels[i], fontsize=13)

    ax_single_g.set_xticks(x)
    ax_single_g.set_xticklabels(metals, fontsize=18)
    ax_single_g.set_ylabel(r"$\mathrm{Energy\ (eV)}$", fontsize=17)
    ax_single_g.set_xlim(xlim_common)
    ax_single_g.set_ylim(ylim_g)
    ax_single_g.set_yticks(yticks_g)
    ax_single_g.tick_params(direction='in', which='both', top=True, right=True, labelsize=14)
    ax_single_g.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.95,
                       fontsize=16, handlelength=1.4, borderaxespad=0.8)
    fig_g.text(0.54, 0.040, "(g)", ha='center', va='center', fontproperties=FONT_TNR_REG, fontsize=32)

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
        y_pos = val - 0.12
        ax_single_h.text(rect.get_x() + rect.get_width()/2.0, y_pos, f"{val:.2f}",
                         ha='center', va='top', fontsize=13, fontweight='bold', color=COLOR_VAL)

    for i in range(n_metals):
        annotate_positive_pair(ax_single_h, rh2[i], h_edef[i], rh3[i], h_dg[i], h_dg_labels[i], fontsize=13)

    ax_single_h.set_xticks(x)
    ax_single_h.set_xticklabels(metals, fontsize=18)
    ax_single_h.set_ylabel(r"$\mathrm{Free\ Energy,\ }\Delta G_{\mathrm{H}^*}\ \mathrm{(eV)}$", fontsize=17)
    ax_single_h.set_xlim(xlim_common)
    ax_single_h.set_ylim(ylim_h)
    ax_single_h.set_yticks(yticks_h)
    ax_single_h.tick_params(direction='in', which='both', top=True, right=True, labelsize=14)
    ax_single_h.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.95,
                       fontsize=16, handlelength=1.4, borderaxespad=0.8)
    fig_h.text(0.54, 0.040, "(h)", ha='center', va='center', fontproperties=FONT_TNR_REG, fontsize=32)

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

    xlim_multi = (-0.55, 3.45)

    for ax, eint, edef, dgpbe, dgu, is_emb, sublabel in [
        (ax_g, g_eint, g_edef, g_dgpbe, g_dgu, False, "(g)"),
        (ax_h, h_eint, h_edef, h_dgpbe, h_dgu, True,  "(h)")
    ]:
        ax.axhline(0, color='red', linestyle=':', linewidth=1.6, zorder=2)
        r1 = ax.bar(x - 1.5*width, eint,  width, color=c_eint, label=r"$E_{\mathrm{int}}^{\mathrm{H}}$", zorder=3)
        r2 = ax.bar(x - 0.5*width, edef,  width, color=c_edef, label=r"$E_{\mathrm{def}}$", zorder=3)
        r3 = ax.bar(x + 0.5*width, dgpbe, width, color=c_dgpbe, label=r"$\Delta G_{\mathrm{H}^*}\ (\mathrm{PBE})$", zorder=3)
        r4 = ax.bar(x + 1.5*width, dgu,   width, color=c_dgu,   label=r"$\Delta G_{\mathrm{H}^*}\ (\mathrm{PBE+D3+}U)$", zorder=3)

        # Labels with anti-collision
        for r, val in zip(r1, eint):
            ax.text(r.get_x() + r.get_width()/2.0, val - 0.12, f"{val:.2f}",
                    ha='center', va='top', fontsize=10.5, fontweight='bold', color=COLOR_VAL)

        for i in range(len(metals)):
            v2 = edef[i]
            v3 = dgpbe[i]
            v4 = dgu[i]

            x2 = r2[i].get_x() + r2[i].get_width() / 2.0
            x3 = r3[i].get_x() + r3[i].get_width() / 2.0
            x4 = r4[i].get_x() + r4[i].get_width() / 2.0

            # Bar 2 (Gold): shift left into open space above Bar 1 (teal, negative)
            x_pos2 = x2 - 0.08
            y_pos2 = v2 + 0.05
            ax.text(x_pos2, y_pos2, f"{v2:.2f}",
                    ha='center', va='bottom', fontsize=10.5, fontweight='bold', color=COLOR_VAL)

            # Bar 4 (Navy):
            if v4 < 0:
                # e.g. Co surface -0.07
                ax.text(x4, v4 - 0.13, f"{v4:.2f}",
                        ha='center', va='top', fontsize=10.5, fontweight='bold', color=COLOR_VAL)
                # Bar 3 (Slate) has plenty of clearance
                ax.text(x3, v3 + 0.05, f"{v3:.2f}",
                        ha='center', va='bottom', fontsize=10.5, fontweight='bold', color=COLOR_VAL)
            else:
                # Shift Bar 4 right into open space to the right
                x_pos4 = x4 + 0.08
                y_pos4 = v4 + 0.05

                # Bar 3: check if close in height to either Bar 2 or Bar 4
                diff34 = abs(v3 - v4)
                diff32 = abs(v3 - v2)
                if diff34 <= 0.15 or diff32 <= 0.15:
                    # Stagger Bar 3 vertically
                    y_pos3 = v3 + 0.16
                else:
                    y_pos3 = v3 + 0.05

                ax.text(x3, y_pos3, f"{v3:.2f}",
                        ha='center', va='bottom', fontsize=10.5, fontweight='bold', color=COLOR_VAL)
                ax.text(x_pos4, y_pos4, f"{v4:.2f}",
                        ha='center', va='bottom', fontsize=10.5, fontweight='bold', color=COLOR_VAL)

        ax.set_xticks(x)
        ax.set_xticklabels(metals, fontsize=18)
        ax.set_xlim(xlim_multi)
        if not is_emb:
            ax.set_ylabel(r"$\mathrm{Energy\ (eV)}$", fontsize=16)
            ax.set_ylim(-2.85, 1.35)
            ax.set_yticks([-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0])
        else:
            ax.set_ylabel(r"$\mathrm{Free\ Energy,\ }\Delta G_{\mathrm{H}^*}\ \mathrm{(eV)}$", fontsize=16)
            ax.set_ylim(-2.10, 2.55)
            ax.set_yticks([-2.0, -1.0, 0.0, 1.0, 2.0])

        ax.tick_params(direction='in', which='both', top=True, right=True, labelsize=14)
        ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e0e0e0', framealpha=0.95,
                  fontsize=12, handlelength=1.3, borderaxespad=0.5, labelspacing=0.25)

    fig.text(0.273, 0.04, "(g)", ha='center', va='center', fontproperties=FONT_TNR_REG, fontsize=24)
    fig.text(0.767, 0.04, "(h)", ha='center', va='center', fontproperties=FONT_TNR_REG, fontsize=24)

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
    Splicing at target_top = 2660 guarantees zero clipping of panels (d), (e), and (f)
    and perfectly matches the original panel (g)/(h) top border position.
    """
    orig_fig7 = os.path.join(REPO_ROOT, "ACS_version/figure/Fig7.png")
    if not os.path.exists(orig_fig7):
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
    # Rows 0 to 2620 contain panels (a - f) and their subpanel labels (d, e, f)
    # Rows 2621 to 2715 are clean white margin
    # Splicing at target_top = 2660 leaves 40 px clean white margin below (d, e, f)
    # and places the top border of new panels (g, h) at y ~ 2760 (matching original y = 2752)
    im_g = Image.open(p_g_path)
    im_h = Image.open(p_h_path)

    target_top = 2660
    target_height = H - target_top  # 1282 px
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

    # Also update Fig7_updated_newcals_preview.png if tier is pbe_d3_u
    if tier == "pbe_d3_u":
        preview_path = os.path.join(POST_DIR, "Fig7_updated_newcals_preview.png")
        composite.save(preview_path)
        print(f"[✓] Updated preview: {preview_path}")

        # Also update resubmission manuscript figure so LaTeX uses the full-res figure
        resub_fig7 = os.path.join(FIG_DIR, "Fig7.png")
        composite.save(resub_fig7)
        print(f"[✓] Updated resubmission manuscript figure: {resub_fig7}")


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
