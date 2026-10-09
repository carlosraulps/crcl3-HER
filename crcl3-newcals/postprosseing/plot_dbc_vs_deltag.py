#!/usr/bin/env python3
"""
plot_dbc_vs_deltag.py
Publication-quality plot of d-band center (epsilon_d^occ) vs. hydrogen adsorption
free energy (Delta G_H*) for monolayer CrCl3 functionalized with TM (Co, Fe, Ni)
across three systematic methodological tiers:

Panels:
  (a) Pure PBE Baseline (U = 0, No vdW)
  (b) Single-Site Hubbard U (PBE+D3+U_Cr, U_Cr = 3.29 eV)
  (c) Multi-Site Hubbard U (PBE+D3+U_all, U_Cr = 3.29 eV & U_TM = 3.29 eV)

Adheres strictly to GEMINI.md Publication Anti-Collision Policy:
  - Zero text overlap via smart bounded cards
  - Dynamic adaptive headroom
  - STIX math & Times New Roman typography
  - Pt(111) benchmark reference line (-0.09 eV)
  - Optimal Sabatier catalytic window (|Delta G_H*| <= 0.15 eV)
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ACS_FIG_DIRS = [
    os.path.abspath(os.path.join(SCRIPT_DIR, "../../ACS_version/figure")),
    os.path.abspath(os.path.join(SCRIPT_DIR, "../../ACS_version/ACS_resubmission/figure")),
]

# Typography
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

CARD_STYLE = dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='#cccccc', alpha=0.92, linewidth=0.8)

def main():
    metals = ["Co", "Fe", "Ni"]
    
    # -------------------------------------------------------------
    # Descriptors & Free Energies across Tiers
    # -------------------------------------------------------------
    # 1. Tier 1 & 2: Occupied d-band centers (up to E_F, eV)
    ads_dbc_u_cr = np.array([-1.6643, -2.4319, -1.1599])
    emb_dbc_u_cr = np.array([-1.4597, -2.4376, -1.6972])
    
    # Panel (a): Pure PBE Baseline (eV)
    ads_dg_pbe = np.array([0.1784, 0.3750, 0.8622])
    emb_dg_pbe = np.array([1.7363, 1.3284, 1.8477])
    
    # Panel (b): PBE + D3 + U_Cr (U_Cr = 3.29 eV) (eV)
    ads_dg_ucr = np.array([-0.0690, 0.1850, 0.6200])
    emb_dg_ucr = np.array([1.3750, 1.1140, 0.8210])

    # Panel (c): PBE + D3 + U_all (Multi-site U_Cr=3.29, U_TM=3.29 eV)
    # Converged occupied d-band centers [-3, 0] eV window:
    # Adsorbed: Co = -1.494 eV, Fe = -2.169 eV, Ni = -0.993 eV
    # Embedded: Co = -2.664 eV, Fe = -2.012 eV, Ni = -2.611 eV
    ads_dbc_uall = np.array([-1.4940, -2.1685, -0.9928])
    emb_dbc_uall = np.array([-2.6640, -2.0122, -2.6109])

    # Delta G_H* (eV)
    ads_dg_uall = np.array([0.0650, 1.8370, 1.1840])
    emb_dg_uall = np.array([1.3890, 1.8210, 1.0240])

    fig, axs = plt.subplots(1, 3, figsize=(19.5, 6.2), dpi=300)
    fig.subplots_adjust(wspace=0.24)

    # Color palette
    color_ads = "#1f77b4"  # Steel Blue
    color_emb = "#d9534f"  # Coral / Ruby Red
    pt_color  = "#17202a"  # Dark Slate

    panels_data = [
        (axs[0], '(a) Pure PBE Baseline ($U = 0$)', ads_dbc_u_cr, emb_dbc_u_cr, ads_dg_pbe, emb_dg_pbe, 'pbe'),
        (axs[1], r'(b) Single-Site $+U_{\mathrm{Cr}}$ ($3.29\,\mathrm{eV}$)', ads_dbc_u_cr, emb_dbc_u_cr, ads_dg_ucr, emb_dg_ucr, 'ucr'),
        (axs[2], r'(c) Multi-Site $+U_{\mathrm{all}}$ ($U_{\mathrm{Cr}}, U_{\mathrm{TM}} = 3.29\,\mathrm{eV}$)', ads_dbc_uall, emb_dbc_uall, ads_dg_uall, emb_dg_uall, 'uall')
    ]

    for ax, title, ads_dbc, emb_dbc, ads_dg, emb_dg, tier in panels_data:
        # 1. Sabatier Optimal Catalytic Window
        ax.axhspan(-0.15, 0.20, color="#2ecc71", alpha=0.18, label=r"Optimal Sabatier Window ($|\Delta G| \leq 0.15\,\mathrm{eV}$)", zorder=1)
        ax.axhline(0.00, color="#27ae60", linestyle="--", linewidth=1.1, zorder=2)
        ax.axhline(-0.09, color=pt_color, linestyle=":", linewidth=1.3, label=r"$\mathrm{Pt(111)}\ (-0.09\,\mathrm{eV})$", zorder=2)

        # 2. Linear fits (visual guides)
        slope_ads, intercept_ads = np.polyfit(ads_dbc, ads_dg, 1)
        r_ads = np.corrcoef(ads_dbc, ads_dg)[0, 1]
        x_min_ads = min(ads_dbc) - 0.2
        x_max_ads = max(ads_dbc) + 0.2
        x_fit_ads = np.linspace(x_min_ads, x_max_ads, 100)
        y_fit_ads = slope_ads * x_fit_ads + intercept_ads
        ax.plot(x_fit_ads, y_fit_ads, color=color_ads, linestyle="-.", linewidth=1.4, alpha=0.8,
                label=f"Adsorbed Fit ($R^2 = {r_ads**2:.2f}$)", zorder=3)

        slope_emb, intercept_emb = np.polyfit(emb_dbc, emb_dg, 1)
        r_emb = np.corrcoef(emb_dbc, emb_dg)[0, 1]
        x_min_emb = min(emb_dbc) - 0.2
        x_max_emb = max(emb_dbc) + 0.2
        x_fit_emb = np.linspace(x_min_emb, x_max_emb, 100)
        y_fit_emb = slope_emb * x_fit_emb + intercept_emb
        ax.plot(x_fit_emb, y_fit_emb, color=color_emb, linestyle="-.", linewidth=1.4, alpha=0.8,
                label=f"Embedded Fit ($R^2 = {r_emb**2:.2f}$)", zorder=3)

        # 3. Data points
        ax.scatter(ads_dbc, ads_dg, color=color_ads, edgecolor="black", s=130, marker="o",
                   linewidth=1.2, label="Adsorbed TM", zorder=5)
        ax.scatter(emb_dbc, emb_dg, color=color_emb, edgecolor="black", s=130, marker="s",
                   linewidth=1.2, label="Embedded TM", zorder=5)

        # 4. Offsets and annotations
        if tier == 'pbe':
            for i, tm in enumerate(metals):
                ax.annotate(f"{tm} ({ads_dg[i]:+.2f})", (ads_dbc[i], ads_dg[i]), textcoords="offset points",
                            xytext=(0, 10), ha='center', fontsize=8.8, fontweight="bold",
                            bbox=CARD_STYLE, zorder=6)
                ax.annotate(f"{tm} ({emb_dg[i]:+.2f})", (emb_dbc[i], emb_dg[i]), textcoords="offset points",
                            xytext=(0, 10), ha='center', fontsize=8.8, fontweight="bold",
                            bbox=CARD_STYLE, zorder=6)
        elif tier == 'ucr':
            for i, tm in enumerate(metals):
                if tm != "Co":
                    ax.annotate(f"{tm} ({ads_dg[i]:+.2f})", (ads_dbc[i], ads_dg[i]), textcoords="offset points",
                                xytext=(0, 10), ha='center', fontsize=8.8, fontweight="bold",
                                bbox=CARD_STYLE, zorder=6)
                ax.annotate(f"{tm} ({emb_dg[i]:+.2f})", (emb_dbc[i], emb_dg[i]), textcoords="offset points",
                            xytext=(0, 10), ha='center', fontsize=8.8, fontweight="bold",
                            bbox=CARD_STYLE, zorder=6)

            # High-visibility callout for Co(ads) Sabatier optimum in panel (b)
            ax.annotate(r"$\mathbf{Co\ (ads):}\ \Delta G = -0.069\,\mathrm{eV}$",
                        xy=(ads_dbc[0], ads_dg[0]), xytext=(-1.66, -0.38),
                        arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1.3),
                        fontsize=8.8, fontweight="bold", color="#1e8449", bbox=CARD_STYLE, zorder=7, ha='center')
        else: # tier == 'uall'
            for i, tm in enumerate(metals):
                if tm == "Co":
                    continue
                elif tm == "Fe":
                    # Stagger Fe(ads) left and Fe(emb) right to prevent horizontal overlap
                    ax.annotate(f"{tm} ({ads_dg[i]:+.2f})", (ads_dbc[i], ads_dg[i]), textcoords="offset points",
                                xytext=(-26, 11), ha='center', fontsize=8.8, fontweight="bold",
                                bbox=CARD_STYLE, zorder=6)
                    ax.annotate(f"{tm} ({emb_dg[i]:+.2f})", (emb_dbc[i], emb_dg[i]), textcoords="offset points",
                                xytext=(26, 11), ha='center', fontsize=8.8, fontweight="bold",
                                bbox=CARD_STYLE, zorder=6)
                else: # Ni
                    ax.annotate(f"{tm} ({ads_dg[i]:+.2f})", (ads_dbc[i], ads_dg[i]), textcoords="offset points",
                                xytext=(0, 10), ha='center', fontsize=8.8, fontweight="bold",
                                bbox=CARD_STYLE, zorder=6)
                    ax.annotate(f"{tm} ({emb_dg[i]:+.2f})", (emb_dbc[i], emb_dg[i]), textcoords="offset points",
                                xytext=(0, 10), ha='center', fontsize=8.8, fontweight="bold",
                                bbox=CARD_STYLE, zorder=6)

            # High-visibility callout for Co(ads) Sabatier summit in panel (c)
            ax.annotate(r"$\mathbf{Co\ (ads):}\ \Delta G = \mathbf{+0.065\,\mathrm{eV}}$" + "\n" + r"(Sabatier Summit)",
                        xy=(ads_dbc[0], ads_dg[0]), xytext=(-1.49, -0.38),
                        arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1.4),
                        fontsize=8.8, fontweight="bold", color="#1e8449", bbox=CARD_STYLE, zorder=7, ha='center')

        # Axes, labels, styling
        ax.set_xlabel(r"Occupied $d$-Band Center, $\varepsilon_d^{\mathrm{occ}}\ (\mathrm{eV})$", fontsize=11.5, fontweight="bold", labelpad=8)
        ax.set_ylabel(r"Hydrogen Adsorption Free Energy, $\Delta G_{\mathrm{H}^*}\ (\mathrm{eV})$", fontsize=11.5, fontweight="bold", labelpad=8)
        ax.set_title(title, fontsize=12.0, fontweight="bold", pad=12)

        ax.set_xlim(-2.85, -0.75)
        ax.set_ylim(-0.60, 2.30)
        ax.xaxis.set_major_locator(MultipleLocator(0.4))
        ax.xaxis.set_minor_locator(MultipleLocator(0.1))
        ax.yaxis.set_major_locator(MultipleLocator(0.5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.1))
        ax.grid(True, linestyle=":", alpha=0.55, zorder=0)

        if tier == 'pbe':
            leg_loc = "lower right"
        elif tier == 'ucr':
            leg_loc = "upper left"
        else: # uall
            leg_loc = "upper right"
        ax.legend(loc=leg_loc, frameon=True, facecolor="white", edgecolor="#cccccc", framealpha=0.92, fontsize=8.2)

    plt.tight_layout()

    # Save to local postprocessing dir
    out_png = os.path.join(SCRIPT_DIR, "dbc_vs_deltag.png")
    out_pdf = os.path.join(SCRIPT_DIR, "dbc_vs_deltag.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    print(f"[OK] Saved {out_png}")
    print(f"[OK] Saved {out_pdf}")

    # Copy to manuscript figure folders
    import shutil
    for fig_dir in ACS_FIG_DIRS:
        if os.path.exists(fig_dir):
            dest_png = os.path.join(fig_dir, "Fig8.png")
            dest_pdf = os.path.join(fig_dir, "Fig8.pdf")
            shutil.copy2(out_png, dest_png)
            shutil.copy2(out_pdf, dest_pdf)
            print(f"[OK] Updated manuscript Fig 8: {dest_png}")
            print(f"[OK] Updated manuscript Fig 8: {dest_pdf}")

if __name__ == "__main__":
    main()
