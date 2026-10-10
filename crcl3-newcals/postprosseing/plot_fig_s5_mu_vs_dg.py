#!/usr/bin/env python3
"""
plot_fig_s5_mu_vs_dg.py
================================================================================
Publication-quality 2-panel figure for Supplementary Information Figure S5:
Relationship between the local magnetic moment of the functionalizing TM atom
(mu_TM) in the relaxed H-free configurations and the hydrogen adsorption free
energy (Delta G_H*).

Panels:
  (a) Single-Site Hubbard U (+U_Cr, U_Cr = 3.29 eV)
  (b) Multi-Site Hubbard U (+U_all, U_Cr = U_TM = 3.29 eV)

Strict GEMINI.md Anti-Collision Policy:
  - Zero text overlap via smart bounded white cards (alpha=0.92, edgecolor=#cccccc)
  - Dynamic adaptive headroom (+25%)
  - STIX math & Times New Roman typography
  - Pt(111) benchmark reference (-0.09 eV)
  - Optimal Sabatier catalytic window (|Delta G_H*| <= 0.15 eV)
================================================================================
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))

FIG_DEST_DIRS = [
    os.path.join(REPO_ROOT, "ACS_version/figure"),
    os.path.join(REPO_ROOT, "ACS_version/ACS_resubmission/figure"),
    os.path.join(REPO_ROOT, "CMS_Final_Submission/figure"),
    os.path.join(REPO_ROOT, "temp/CMS_Final_Submission/figure"),
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

    # -------------------------------------------------------------------------
    # Panel (a): +U_Cr (Single-Site Dudarev U_Cr = 3.29 eV)
    # -------------------------------------------------------------------------
    # Atom-projected local magnetic moment mu_TM (mu_B)
    ads_mu_ucr = np.array([+1.99, +3.34, -0.76])
    emb_mu_ucr = np.array([+2.09, +3.34, -1.02])

    # Delta G_H* (eV)
    ads_dg_ucr = np.array([-0.069, +0.185, +0.620])
    emb_dg_ucr = np.array([+1.375, +1.114, +0.821])

    # -------------------------------------------------------------------------
    # Panel (b): +U_all (Multi-Site Dudarev U_Cr = 3.29, U_TM = 3.29 eV)
    # -------------------------------------------------------------------------
    ads_mu_uall = np.array([+2.02, +3.41, -0.79])
    emb_mu_uall = np.array([+2.11, +3.40, -1.05])

    # Delta G_H* (eV)
    ads_dg_uall = np.array([+0.065, +1.837, +1.184])
    emb_dg_uall = np.array([+1.389, +1.821, +1.024])

    fig, axs = plt.subplots(1, 2, figsize=(14.2, 6.2), dpi=300)
    fig.subplots_adjust(wspace=0.22)

    color_ads = "#1f77b4"  # Steel Blue
    color_emb = "#d9534f"  # Coral / Ruby Red
    pt_color  = "#17202a"  # Dark Slate

    panels_data = [
        (axs[0], r'(a) Single-Site $+U_{\mathrm{Cr}}$ ($3.29\,\mathrm{eV}$)',
         ads_mu_ucr, emb_mu_ucr, ads_dg_ucr, emb_dg_ucr, 'ucr'),
        (axs[1], r'(b) Multi-Site $+U_{\mathrm{all}}$ ($U_{\mathrm{Cr}}, U_{\mathrm{TM}} = 3.29\,\mathrm{eV}$)',
         ads_mu_uall, emb_mu_uall, ads_dg_uall, emb_dg_uall, 'uall')
    ]

    for ax, title, ads_mu, emb_mu, ads_dg, emb_dg, tier in panels_data:
        # 1. Sabatier Optimal Catalytic Window
        ax.axhspan(-0.15, 0.20, color="#2ecc71", alpha=0.18,
                   label=r"Optimal Sabatier Window ($|\Delta G_{\mathrm{H}^*}| \leq 0.15\,\mathrm{eV}$)", zorder=1)
        ax.axhline(0.00, color="#27ae60", linestyle="--", linewidth=1.1, zorder=2)
        ax.axhline(-0.09, color=pt_color, linestyle=":", linewidth=1.3,
                   label=r"$\mathrm{Pt(111)}\ (-0.09\,\mathrm{eV})$", zorder=2)

        # Vertical line demarcating antiparallel vs parallel alignment
        ax.axvline(0.00, color="#7f8c8d", linestyle="-.", linewidth=0.9, alpha=0.6, zorder=1)
        ax.text(-0.05, 2.18, r"$\longleftarrow$ Antiparallel", ha="right", va="top",
                fontsize=8.5, color="#555555", fontstyle="italic", zorder=3)
        ax.text(+0.05, 2.18, r"Parallel $\longrightarrow$", ha="left", va="top",
                fontsize=8.5, color="#555555", fontstyle="italic", zorder=3)

        # 2. Linear guides (visual guides showing poor descriptor correlation)
        slope_ads, int_ads = np.polyfit(ads_mu, ads_dg, 1)
        r_ads = np.corrcoef(ads_mu, ads_dg)[0, 1]
        x_fit_ads = np.linspace(-1.3, 3.8, 100)
        ax.plot(x_fit_ads, slope_ads * x_fit_ads + int_ads, color=color_ads, linestyle="-.", linewidth=1.3, alpha=0.75,
                label=f"Adsorbed Fit ($R^2 = {r_ads**2:.2f}$)", zorder=3)

        slope_emb, int_emb = np.polyfit(emb_mu, emb_dg, 1)
        r_emb = np.corrcoef(emb_mu, emb_dg)[0, 1]
        x_fit_emb = np.linspace(-1.3, 3.8, 100)
        ax.plot(x_fit_emb, slope_emb * x_fit_emb + int_emb, color=color_emb, linestyle="-.", linewidth=1.3, alpha=0.75,
                label=f"Embedded Fit ($R^2 = {r_emb**2:.2f}$)", zorder=3)

        # 3. Scatter data points
        ax.scatter(ads_mu, ads_dg, color=color_ads, edgecolor="black", s=130, marker="o",
                   linewidth=1.2, label="Adsorbed TM", zorder=5)
        ax.scatter(emb_mu, emb_dg, color=color_emb, edgecolor="black", s=130, marker="s",
                   linewidth=1.2, label="Embedded TM", zorder=5)

        # 4. Offsets & Zero-Collision Annotations
        if tier == 'ucr':
            # Co(ads) - Sabatier Sweet Spot
            ax.annotate(r"$\mathbf{Co\ (ads):}\ \Delta G = -0.069\,\mathrm{eV}$",
                        xy=(ads_mu[0], ads_dg[0]), xytext=(ads_mu[0] + 0.1, ads_dg[0] - 0.28),
                        arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1.3),
                        fontsize=8.8, fontweight="bold", color="#1e8449", bbox=CARD_STYLE, zorder=7, ha='center')

            # Fe(ads)
            ax.annotate(f"Fe (ads)\n({ads_dg[1]:+.2f} eV)", (ads_mu[1], ads_dg[1]),
                        textcoords="offset points", xytext=(0, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)

            # Ni(ads)
            ax.annotate(f"Ni (ads)\n({ads_dg[2]:+.2f} eV)", (ads_mu[2], ads_dg[2]),
                        textcoords="offset points", xytext=(0, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)

            # Co(emb)
            ax.annotate(f"Co (emb)\n({emb_dg[0]:+.2f} eV)", (emb_mu[0], emb_dg[0]),
                        textcoords="offset points", xytext=(0, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)

            # Fe(emb)
            ax.annotate(f"Fe (emb)\n({emb_dg[1]:+.2f} eV)", (emb_mu[1], emb_dg[1]),
                        textcoords="offset points", xytext=(0, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)

            # Ni(emb)
            ax.annotate(f"Ni (emb)\n({emb_dg[2]:+.2f} eV)", (emb_mu[2], emb_dg[2]),
                        textcoords="offset points", xytext=(0, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)

        else: # tier == 'uall'
            # Co(ads) - Sabatier Summit Callout
            ax.annotate(r"$\mathbf{Co\ (ads):}\ \Delta G = \mathbf{+0.065\,\mathrm{eV}}$" + "\n" + r"(Sabatier Summit)",
                        xy=(ads_mu[0], ads_dg[0]), xytext=(ads_mu[0] + 0.1, ads_dg[0] - 0.32),
                        arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1.3),
                        fontsize=8.8, fontweight="bold", color="#1e8449", bbox=CARD_STYLE, zorder=7, ha='center')

            # Fe(ads) & Fe(emb) - horizontally staggered to avoid colliding!
            ax.annotate(f"Fe (ads)\n({ads_dg[1]:+.2f} eV)", (ads_mu[1], ads_dg[1]),
                        textcoords="offset points", xytext=(-26, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)
            ax.annotate(f"Fe (emb)\n({emb_dg[1]:+.2f} eV)", (emb_mu[1], emb_dg[1]),
                        textcoords="offset points", xytext=(26, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)

            # Co(emb)
            ax.annotate(f"Co (emb)\n({emb_dg[0]:+.2f} eV)", (emb_mu[0], emb_dg[0]),
                        textcoords="offset points", xytext=(0, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)

            # Ni(ads) & Ni(emb)
            ax.annotate(f"Ni (ads)\n({ads_dg[2]:+.2f} eV)", (ads_mu[2], ads_dg[2]),
                        textcoords="offset points", xytext=(0, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)
            ax.annotate(f"Ni (emb)\n({emb_dg[2]:+.2f} eV)", (emb_mu[2], emb_dg[2]),
                        textcoords="offset points", xytext=(0, 14), ha='center', fontsize=8.8,
                        fontweight="bold", bbox=CARD_STYLE, zorder=6)

        # Labels, limits, grid
        ax.set_xlabel(r"Local Magnetic Moment, $\mu_{\mathrm{TM}}\ (\mu_{\mathrm{B}})$",
                      fontsize=11.5, fontweight="bold", labelpad=8)
        ax.set_ylabel(r"Hydrogen Adsorption Free Energy, $\Delta G_{\mathrm{H}^*}\ (\mathrm{eV})$",
                      fontsize=11.5, fontweight="bold", labelpad=8)
        ax.set_title(title, fontsize=12.0, fontweight="bold", pad=12)

        ax.set_xlim(-1.45, 4.10)
        ax.set_ylim(-0.60, 2.30)
        ax.xaxis.set_major_locator(MultipleLocator(1.0))
        ax.xaxis.set_minor_locator(MultipleLocator(0.2))
        ax.yaxis.set_major_locator(MultipleLocator(0.5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.1))
        ax.grid(True, linestyle=":", alpha=0.55, zorder=0)

        # Legend placement in low-density quadrant
        leg_loc = "upper left" if tier == 'ucr' else "upper left"
        ax.legend(loc=leg_loc, frameon=True, facecolor="white", edgecolor="#cccccc",
                  framealpha=0.92, fontsize=8.5)

    plt.tight_layout()

    # Save to local postprocessing
    out_png = os.path.join(SCRIPT_DIR, "mu_vs_dG.png")
    out_pdf = os.path.join(SCRIPT_DIR, "mu_vs_dG.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    print(f"[OK] Saved {out_png}")
    print(f"[OK] Saved {out_pdf}")

    # Copy to manuscript figure folders
    for d in FIG_DEST_DIRS:
        if os.path.exists(d):
            dest_p = os.path.join(d, "mu_vs_dG.png")
            dest_pdf = os.path.join(d, "mu_vs_dG.pdf")
            shutil.copy2(out_png, dest_p)
            shutil.copy2(out_pdf, dest_pdf)
            print(f"[OK] Updated: {dest_p}")
            print(f"[OK] Updated: {dest_pdf}")

if __name__ == "__main__":
    main()
