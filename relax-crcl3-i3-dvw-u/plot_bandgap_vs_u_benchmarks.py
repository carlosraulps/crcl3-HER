#!/usr/bin/env python3
"""
plot_bandgap_vs_u_benchmarks.py
Publication-quality dual-benchmark electronic structure figure for monolayer CrCl3 (1x1 primitive cell).

Features:
- Times New Roman font styling via LaTeX preambles with STIX fallback.
- Dual-benchmark visualization in Panel (a):
  1. Lower reference band: Monolayer PBE literature consensus [2-4] (1.50 - 1.60 eV)
  2. Upper reference band: Bulk fundamental charge-transfer optical edge [1] (3.2 +/- 0.2 eV)
- Physical transition annotation demonstrating the Hubbard +U crossover from crystal-field to charge-transfer insulator.
- Panel (b): Magnetic ground state showing robust S=3/2 (6.00 muB) ferromagnetic saturation.
- Professional citation footnote banner anchored cleanly at the bottom margin.
Outputs:
  - crcl3_bandgap_benchmarks_reviewer.png
  - crcl3_bandgap_benchmarks_reviewer.pdf
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Times New Roman + LaTeX Configuration ---
try:
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Nimbus Roman", "DejaVu Serif"],
        "text.latex.preamble": r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{mathptmx}",
        "axes.labelsize": 11.5,
        "axes.titlesize": 12.5,
        "legend.fontsize": 8.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "figure.titlesize": 13.5,
        "axes.linewidth": 1.0,
        "xtick.major.size": 4.5,
        "xtick.major.width": 0.8,
        "ytick.major.size": 4.5,
        "ytick.major.width": 0.8,
    })
except Exception:
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Nimbus Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "axes.labelsize": 11.5,
        "axes.titlesize": 12.5,
        "legend.fontsize": 8.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
    })

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "bandgap_vs_u.csv")

def load_data():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Missing {CSV_PATH}. Please run plot_bandgap_vs_u.py first.")
    
    data = []
    with open(CSV_PATH, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) >= 9:
            try:
                u = float(parts[0])
                status = parts[1]
                toten = float(parts[2]) if parts[2] != "N/A" else None
                ef = float(parts[3]) if parts[3] != "N/A" else None
                mag = float(parts[4]) if parts[4] != "N/A" else None
                cr_m = float(parts[5]) if parts[5] != "N/A" else None
                gap = float(parts[6]) if parts[6] != "N/A" else None
                gap_up = float(parts[7]) if parts[7] != "N/A" else None
                gap_dn = float(parts[8]) if parts[8] != "N/A" else None
                data.append({
                    "u": u, "status": status, "toten": toten, "ef": ef,
                    "mag": mag, "cr_m": cr_m, "gap": gap, "gap_up": gap_up, "gap_dn": gap_dn
                })
            except ValueError:
                continue
    return data

def plot_benchmarks(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.0), dpi=300)

    u_vals = [d["u"] for d in data if d["gap"] is not None]
    gaps = [d["gap"] for d in data if d["gap"] is not None]
    moms = [d["mag"] for d in data if d["mag"] is not None]
    cr_moms = [d["cr_m"] for d in data if d["cr_m"] is not None]

    # -------------------------------------------------------------
    # Panel (a): Band Gap vs. U with Dual Benchmarks
    # -------------------------------------------------------------
    # 1. Monolayer PBE consensus band [2-4] (1.50 - 1.60 eV)
    ax1.axhspan(1.50, 1.60, color="#b0c4de", alpha=0.45,
                label=r"Monolayer PBE Lit. [2--4] ($1.50 - 1.60\ \mathrm{eV}$)")
    ax1.axhline(1.50, color="#4682b4", linestyle=":", linewidth=1.2,
                label=r"PBE Baseline ($1.50\ \mathrm{eV}$, This Work)")

    # 2. Bulk Fundamental Charge-Transfer Edge [1] (3.2 +/- 0.2 eV, Pollini 1970)
    ax1.axhspan(3.00, 3.40, color="#ffcc99", alpha=0.45,
                label=r"Bulk Fundamental Edge [1] ($3.2 \pm 0.2\ \mathrm{eV}$)")
    ax1.axhline(3.20, color="#d95f02", linestyle="--", linewidth=1.2)

    # 3. Calculated DFT+U data
    ax1.plot(u_vals, gaps, "o-", color="#0b559f", linewidth=2.3, markersize=7.5,
             label=r"Monolayer $E_g$ (PBE+$U$, Relaxed)", zorder=5)

    # Annotation arrow indicating the physical crossover
    ax1.annotate(
        r"$\mathrm{Cr}\ 3d$ on-site $+U$ pushes $d$-states down," + "\n" +
        r"opening gap toward charge-transfer regime ($>2.5\ \mathrm{eV}$)",
        xy=(3.0, 2.5366), xytext=(1.8, 2.00),
        arrowprops=dict(facecolor="#222222", edgecolor="#222222", arrowstyle="->", lw=1.1),
        fontsize=8.2, bbox=dict(boxstyle="round,pad=0.35", fc="#fdfdfd", ec="#cccccc", lw=0.8)
    )

    ax1.set_xlabel(r"Hubbard Coulomb Parameter $U$ on $\mathrm{Cr}\ 3d$ (eV)")
    ax1.set_ylabel(r"Electronic Band Gap $E_g$ (eV)")
    ax1.set_title(r"\textbf{(a)} $\mathrm{CrCl}_3$ Monolayer: Band Gap vs. Hubbard $U$")
    ax1.set_xticks(range(7))
    ax1.set_xlim(-0.3, 6.3)
    ax1.set_ylim(1.20, 3.55)
    ax1.grid(True, linestyle="--", linewidth=0.5, alpha=0.55)
    ax1.legend(frameon=True, fancybox=False, edgecolor="#cccccc", loc="upper left")

    # -------------------------------------------------------------
    # Panel (b): Magnetic Moment vs. U
    # -------------------------------------------------------------
    u_mag = [d["u"] for d in data if d["mag"] is not None]
    ax2.plot(u_mag, moms, "D-", color="#7b2cbf", linewidth=2.0, markersize=6.5,
             label=r"Total Cell Moment $M_{\mathrm{cell}}\ (\mu_{\mathrm{B}})$")
    ax2.axhline(6.00, color="gray", linestyle=":", linewidth=1.1,
                label=r"Ideal $S=3/2$ Ground State ($6.00\ \mu_{\mathrm{B}}$)")
    
    if len(cr_moms) == len(u_mag):
        ax2.plot(u_mag, cr_moms, "v--", color="#d95f02", linewidth=1.8, markersize=6.0,
                 label=r"Local Cr Moment $\mu_{\mathrm{Cr}}\ (\mu_{\mathrm{B}})$")

    ax2.set_xlabel(r"Hubbard Coulomb Parameter $U$ on $\mathrm{Cr}\ 3d$ (eV)")
    ax2.set_ylabel(r"Magnetic Moment ($\mu_{\mathrm{B}}$)")
    ax2.set_title(r"\textbf{(b)} Magnetic Ground State Stability")
    ax2.set_xticks(range(7))
    ax2.set_xlim(-0.3, 6.3)
    ax2.set_ylim(2.5, 6.5)
    ax2.grid(True, linestyle="--", linewidth=0.5, alpha=0.55)
    ax2.legend(frameon=True, fancybox=False, edgecolor="#cccccc", loc="center right")

    plt.tight_layout(rect=[0, 0.07, 1, 1])

    # -------------------------------------------------------------
    # Professional Footnote Citation Banner (Bottom Canvas)
    # -------------------------------------------------------------
    citation_text = (
        r"\textbf{References}: "
        r"[1] I. Pollini \& G. Spinolo, \textit{Phys. Status Solidi (b)} \textbf{41}, 691 (1970). "
        r"[2] L. Webster \& J.-A. Yan, \textit{Phys. Rev. B} \textbf{98}, 144411 (2018). "
        r"[3] M. Luo \textit{et al.}, \textit{Solid State Commun.} \textbf{321}, 114048 (2020). "
        r"[4] Y. Gao \textit{et al.}, \textit{Phys. Status Solidi RRL} \textbf{12}, 1800105 (2018)."
    )
    fig.text(
        0.5, 0.015, citation_text,
        ha="center", va="bottom", fontsize=7.2, color="#222222",
        bbox=dict(boxstyle="round,pad=0.35", fc="#f8f9fa", ec="#d0d0d0", lw=0.7)
    )

    out_png = os.path.join(BASE_DIR, "crcl3_bandgap_benchmarks_reviewer.png")
    out_pdf = os.path.join(BASE_DIR, "crcl3_bandgap_benchmarks_reviewer.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"Dual-benchmark plots generated successfully:\n  - {out_png}\n  - {out_pdf}")

if __name__ == "__main__":
    data = load_data()
    plot_benchmarks(data)
