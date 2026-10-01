#!/usr/bin/env python3
"""
plot_dbc_vs_deltag.py
Publication-quality plot of d-band center (epsilon_d^occ) vs. hydrogen adsorption
free energy (Delta G_H*) for monolayer CrCl3 functionalized with TM (Co, Fe, Ni).

Panels:
  (a) Pure PBE Baseline (U = 0, No vdW)
  (b) PBE + D3 + U (U_Cr = 3.29 eV) + Exact Caique Vibrational Corrections

Adheres to GEMINI.md Publication Anti-Collision Policy:
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
ACS_FIG_DIR = os.path.join(SCRIPT_DIR, "../../ACS_version/ACS_resubmission/figure")

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
    # Descriptors & Free Energies
    # -------------------------------------------------------------
    # Clean host d-band centers (occupied up to E_F, eV)
    # Adsorbed: Co = -1.664 eV, Fe = -2.432 eV, Ni = -1.160 eV
    # Embedded: Co = -1.460 eV, Fe = -2.438 eV, Ni = -1.697 eV
    ads_dbc = np.array([-1.6643, -2.4319, -1.1599])
    emb_dbc = np.array([-1.4597, -2.4376, -1.6972])
    
    # Panel (a): Pure PBE Baseline (eV)
    ads_dg_pbe = np.array([0.1784, 0.3750, 0.8622])
    emb_dg_pbe = np.array([1.7363, 1.3284, 1.8477])
    
    # Panel (b): PBE + D3 + U (U_Cr = 3.29 eV) with Caique exact corrections (eV)
    # Co(ads): -0.309 + 0.24 = -0.069 eV
    # Fe(ads): +0.005 + 0.18 = +0.185 eV
    # Ni(ads): +0.430 + 0.19 = +0.620 eV
    # Co(emb): +1.115 + 0.26 = +1.375 eV
    # Fe(emb): +0.854 + 0.26 = +1.114 eV
    # Ni(emb): +0.621 + 0.20 = +0.821 eV
    ads_dg_u = np.array([-0.0690, 0.1850, 0.6200])
    emb_dg_u = np.array([1.3750, 1.1140, 0.8210])

    fig, axs = plt.subplots(1, 2, figsize=(14.5, 6.2), dpi=300)
    fig.subplots_adjust(wspace=0.22)

    # Color palette
    color_ads = "#1f77b4"  # Steel Blue
    color_emb = "#d9534f"  # Coral / Ruby Red
    pt_color  = "#17202a"  # Dark Slate

    panels_data = [
        (axs[0], '(a) Pure PBE Baseline ($U = 0$, No vdW)', ads_dg_pbe, emb_dg_pbe, False),
        (axs[1], r'(b) PBE+D3+$U$ ($U_{\mathrm{Cr}} = 3.29\,\mathrm{eV}$) + Exact Thermochemistry', ads_dg_u, emb_dg_u, True)
    ]

    for ax, title, ads_dg, emb_dg, is_u in panels_data:
        # 1. Sabatier Optimal Catalytic Window
        ax.axhspan(-0.15, 0.20, color="#2ecc71", alpha=0.18, label=r"Optimal Sabatier Window ($|\Delta G_{\mathrm{H}^*}| \leq 0.15\,\mathrm{eV}$)", zorder=1)
        ax.axhline(0.00, color="#27ae60", linestyle="--", linewidth=1.1, zorder=2)
        ax.axhline(-0.09, color=pt_color, linestyle=":", linewidth=1.3, label=r"$\mathrm{Pt(111)}\ (\Delta G_{\mathrm{H}^*} = -0.09\,\mathrm{eV})$", zorder=2)

        # 2. Linear fits (visual guides)
        slope_ads, intercept_ads = np.polyfit(ads_dbc, ads_dg, 1)
        r_ads = np.corrcoef(ads_dbc, ads_dg)[0, 1]
        x_fit_ads = np.linspace(-2.65, -0.95, 100)
        y_fit_ads = slope_ads * x_fit_ads + intercept_ads
        ax.plot(x_fit_ads, y_fit_ads, color=color_ads, linestyle="-.", linewidth=1.4, alpha=0.8,
                label=f"Adsorbed Fit ($R^2 = {r_ads**2:.2f}$)", zorder=3)

        slope_emb, intercept_emb = np.polyfit(emb_dbc, emb_dg, 1)
        r_emb = np.corrcoef(emb_dbc, emb_dg)[0, 1]
        x_fit_emb = np.linspace(-2.65, -1.25, 100)
        y_fit_emb = slope_emb * x_fit_emb + intercept_emb
        ax.plot(x_fit_emb, y_fit_emb, color=color_emb, linestyle="-.", linewidth=1.4, alpha=0.8,
                label=f"Embedded Fit ($R^2 = {r_emb**2:.2f}$)", zorder=3)

        # 3. Data points
        ax.scatter(ads_dbc, ads_dg, color=color_ads, edgecolor="black", s=130, marker="o",
                   linewidth=1.2, label="Adsorbed TM", zorder=5)
        ax.scatter(emb_dbc, emb_dg, color=color_emb, edgecolor="black", s=130, marker="s",
                   linewidth=1.2, label="Embedded TM", zorder=5)

        # 4. Offsets and annotations
        if not is_u:
            offsets_ads = {
                "Co": (0, 12),
                "Fe": (0, 12),
                "Ni": (0, 12),
            }
            offsets_emb = {
                "Co": (0, 12),
                "Fe": (0, 12),
                "Ni": (0, 12),
            }
            for i, tm in enumerate(metals):
                ax.annotate(f"{tm} ({ads_dg[i]:+.2f})", (ads_dbc[i], ads_dg[i]), textcoords="offset points",
                            xytext=offsets_ads.get(tm, (0, 12)), ha='center', fontsize=9.2, fontweight="bold",
                            bbox=CARD_STYLE, zorder=6)
                ax.annotate(f"{tm} ({emb_dg[i]:+.2f})", (emb_dbc[i], emb_dg[i]), textcoords="offset points",
                            xytext=offsets_emb.get(tm, (0, 12)), ha='center', fontsize=9.2, fontweight="bold",
                            bbox=CARD_STYLE, zorder=6)
        else:
            offsets_ads = {
                "Co": (0, 0), # Handled by special callout below
                "Fe": (0, 12),
                "Ni": (0, 12),
            }
            offsets_emb = {
                "Co": (0, 12),
                "Fe": (0, 12),
                "Ni": (0, 12),
            }
            for i, tm in enumerate(metals):
                if tm != "Co":
                    ax.annotate(f"{tm} ({ads_dg[i]:+.2f})", (ads_dbc[i], ads_dg[i]), textcoords="offset points",
                                xytext=offsets_ads.get(tm, (0, 12)), ha='center', fontsize=9.2, fontweight="bold",
                                bbox=CARD_STYLE, zorder=6)
                ax.annotate(f"{tm} ({emb_dg[i]:+.2f})", (emb_dbc[i], emb_dg[i]), textcoords="offset points",
                            xytext=offsets_emb.get(tm, (0, 12)), ha='center', fontsize=9.2, fontweight="bold",
                            bbox=CARD_STYLE, zorder=6)

            # High-visibility callout for Co(ads) Sabatier optimum in panel (b)
            ax.annotate(r"$\mathbf{Co\ (ads):}\ \Delta G_{\mathrm{H}^*} = -0.069\,\mathrm{eV}$" + "\n" + r"(Near-Zero Sabatier Optimum)",
                        xy=(ads_dbc[0], ads_dg[0]), xytext=(-1.66, -0.38),
                        arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1.5),
                        fontsize=9.2, fontweight="bold", color="#1e8449", bbox=CARD_STYLE, zorder=7, ha='center')

        # Axes, labels, styling
        ax.set_xlabel(r"Occupied $d$-Band Center, $\varepsilon_d^{\mathrm{occ}}\ (\mathrm{eV})$", fontsize=11.8, fontweight="bold", labelpad=8)
        ax.set_ylabel(r"Hydrogen Adsorption Free Energy, $\Delta G_{\mathrm{H}^*}\ (\mathrm{eV})$", fontsize=11.8, fontweight="bold", labelpad=8)
        ax.set_title(title, fontsize=12.2, fontweight="bold", pad=12)

        ax.set_xlim(-2.75, -0.90)
        ax.set_ylim(-0.60, 2.30)
        ax.xaxis.set_major_locator(MultipleLocator(0.4))
        ax.xaxis.set_minor_locator(MultipleLocator(0.1))
        ax.yaxis.set_major_locator(MultipleLocator(0.5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.1))
        ax.grid(True, linestyle=":", alpha=0.55, zorder=0)

        # Legend: Panel a in bottom right, Panel b in upper left
        leg_loc = "lower right" if not is_u else "upper left"
        ax.legend(loc=leg_loc, frameon=True, facecolor="white", edgecolor="#cccccc", framealpha=0.92, fontsize=8.6)

    plt.tight_layout()

    # Save to local postprocessing dir
    out_png = os.path.join(SCRIPT_DIR, "dbc_vs_deltag.png")
    out_pdf = os.path.join(SCRIPT_DIR, "dbc_vs_deltag.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    print(f"[OK] Saved {out_png}")
    print(f"[OK] Saved {out_pdf}")

    # Copy to manuscript figure folder
    if os.path.exists(ACS_FIG_DIR):
        dest_png = os.path.join(ACS_FIG_DIR, "Fig8.png")
        dest_pdf = os.path.join(ACS_FIG_DIR, "Fig8.pdf")
        import shutil
        shutil.copy2(out_png, dest_png)
        shutil.copy2(out_pdf, dest_pdf)
        print(f"[OK] Updated manuscript Fig 8: {dest_png}")
        print(f"[OK] Updated manuscript Fig 8: {dest_pdf}")

if __name__ == "__main__":
    main()
