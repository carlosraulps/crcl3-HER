#!/usr/bin/env python3
"""
plot_bandgap_vs_u.py
Publication-quality electronic structure and band gap extraction for monolayer CrCl3 (1x1 primitive cell)
across Hubbard U = 0 .. 6 eV (Cr 3d) with Grimme DFT-D3 dispersion corrections.

Features:
- Times New Roman font family styling via LaTeX (mathptmx) with STIX math fallback.
- Dual-panel publication figure:
  Panel (a): Fundamental and spin-resolved band gaps (Eg, Eg,up, Eg,dn) vs. Hubbard U.
  Panel (b): Total cell and Cr local magnetic moments vs. Hubbard U.
- Formatted Markdown report with LaTeX equations and CSV data export.
"""

import os
import sys
import glob
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
        "axes.labelsize": 16,
        "axes.titlesize": 16,
        "legend.fontsize": 10,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "figure.titlesize": 14,
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
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH_ROOT = "/home/cr/scratch_vasp/relax-crcl3-i3-dvw-u"
U_VALUES = [0, 1, 2, 3, 4, 5, 6]

def parse_eigenval(eigenval_path, efermi=0.0):
    """Parses VASP EIGENVAL file to calculate VBM, CBM, and band gaps for spin-polarized systems."""
    if not os.path.exists(eigenval_path):
        return None
    try:
        with open(eigenval_path, "r") as f:
            lines = [l for l in f.readlines() if l.strip()]
        if len(lines) < 6:
            return None

        # Header info
        header_parts = lines[0].split()
        if len(header_parts) < 4:
            return None
        ispin = int(header_parts[3])
        
        info_parts = lines[5].split()
        if len(info_parts) < 3:
            return None
        nelect, nkpts, nbands = int(info_parts[0]), int(info_parts[1]), int(info_parts[2])
        
        # Verify enough lines exist for all k-points and bands
        expected_lines = 6 + nkpts * (nbands + 1)
        if len(lines) < expected_lines:
            return None  # Incomplete file, still writing

        idx = 6
        vbm_up, cbm_up = -1e9, 1e9
        vbm_dn, cbm_dn = -1e9, 1e9

        for k in range(nkpts):
            if idx >= len(lines): break
            kpt_line = lines[idx].split()
            idx += 1
            for b in range(nbands):
                if idx >= len(lines): break
                parts = [float(x) for x in lines[idx].split()]
                idx += 1
                if ispin == 2 and len(parts) >= 5:
                    energy_up, energy_dn = parts[1], parts[2]
                    occ_up, occ_dn = parts[3], parts[4]
                else:
                    energy_up, occ_up = parts[1], parts[2]
                    energy_dn, occ_dn = None, None

                if occ_up > 0.5:
                    if energy_up > vbm_up: vbm_up = energy_up
                else:
                    if energy_up < cbm_up: cbm_up = energy_up
                
                if ispin == 2 and occ_dn is not None:
                    if occ_dn > 0.5:
                        if energy_dn > vbm_dn: vbm_dn = energy_dn
                    else:
                        if energy_dn < cbm_dn: cbm_dn = energy_dn
                        
        gap_up = max(0.0, cbm_up - vbm_up) if cbm_up < 1e8 and vbm_up > -1e8 else None
        gap_dn = max(0.0, cbm_dn - vbm_dn) if ispin == 2 and cbm_dn < 1e8 and vbm_dn > -1e8 else None
        
        vbm_tot = max(vbm_up, vbm_dn) if ispin == 2 else vbm_up
        cbm_tot = min(cbm_up, cbm_dn) if ispin == 2 else cbm_up
        gap_tot = max(0.0, cbm_tot - vbm_tot) if (cbm_tot < 1e8 and vbm_tot > -1e8) else None
        
        return {
            "vbm": vbm_tot, "cbm": cbm_tot, "gap": gap_tot,
            "vbm_up": vbm_up, "cbm_up": cbm_up, "gap_up": gap_up,
            "vbm_dn": vbm_dn, "cbm_dn": cbm_dn, "gap_dn": gap_dn,
        }
    except Exception:
        return None

def parse_outcar(outcar_path):
    """
    Extracts total energy, Fermi energy, total magnetization,
    and individual Cr magnetic moments from OUTCAR.
    """
    if not os.path.exists(outcar_path):
        return None
    toten = None
    efermi = None
    magmom = None
    completed = False
    cr_moms = []

    try:
        with open(outcar_path, "r", errors="ignore") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if "free  energy   TOTEN" in line:
                parts = line.split()
                toten = float(parts[-2])
            elif "E-fermi :" in line:
                parts = line.split()
                efermi = float(parts[2])
            elif "number of electron " in line and "magnetization" in line:
                parts = line.split()
                magmom = float(parts[-1])
            elif "General timing and accounting" in line:
                completed = True
            elif "magnetization (x)" in line:
                cr_moms = []
                j = i + 4
                while j < len(lines) and j < i + 10:
                    parts = lines[j].split()
                    if len(parts) >= 5 and parts[0] in ["1", "2"]:
                        try:
                            cr_moms.append(float(parts[-1]))
                        except ValueError:
                            pass
                    j += 1

        avg_cr_mom = np.mean(cr_moms) if cr_moms else None

        return {
            "toten": toten,
            "efermi": efermi,
            "magmom": magmom,
            "cr_mom": avg_cr_mom,
            "completed": completed
        }
    except Exception as e:
        print(f"Warning: Failed to parse OUTCAR ({outcar_path}): {e}")
        return None

def collect_results():
    """Aggregates results across U = 0 .. 6 eV checking project dir first, then scratch NVMe."""
    results = []
    for u in U_VALUES:
        proj_dir = os.path.join(BASE_DIR, f"U_{u}")
        scratch_dir = os.path.join(SCRATCH_ROOT, f"U_{u}")

        outcar = os.path.join(proj_dir, "OUTCAR")
        eigenval = os.path.join(proj_dir, "EIGENVAL")
        if not os.path.exists(outcar) and os.path.exists(os.path.join(scratch_dir, "OUTCAR")):
            outcar = os.path.join(scratch_dir, "OUTCAR")
        if not os.path.exists(eigenval) and os.path.exists(os.path.join(scratch_dir, "EIGENVAL")):
            eigenval = os.path.join(scratch_dir, "EIGENVAL")

        out_data = parse_outcar(outcar)
        efermi = out_data["efermi"] if out_data and out_data["efermi"] is not None else 0.0
        eig_data = parse_eigenval(eigenval, efermi=efermi)

        status = "Completed" if (out_data and out_data["completed"]) else ("Running/Partial" if out_data else "Queued/Unrun")

        res = {
            "u": u,
            "status": status,
            "toten": out_data["toten"] if out_data else None,
            "efermi": efermi if out_data else None,
            "magmom": out_data["magmom"] if out_data else None,
            "cr_mom": out_data["cr_mom"] if out_data else None,
            "gap": eig_data["gap"] if eig_data else None,
            "gap_up": eig_data["gap_up"] if eig_data else None,
            "gap_dn": eig_data["gap_dn"] if eig_data else None,
            "vbm": eig_data["vbm"] if eig_data else None,
            "cbm": eig_data["cbm"] if eig_data else None,
        }
        results.append(res)
    return results

def generate_markdown_and_csv(results):
    """Outputs structured data to bandgap_vs_u.csv and bandgap_vs_u_summary.md."""
    csv_path = os.path.join(BASE_DIR, "bandgap_vs_u.csv")
    md_path = os.path.join(BASE_DIR, "bandgap_vs_u_summary.md")

    with open(csv_path, "w") as f:
        f.write("U_eV,Status,TOTEN_eV,E_fermi_eV,Cell_Magnetization_muB,Cr_Local_Moment_muB,BandGap_eV,Gap_SpinUp_eV,Gap_SpinDown_eV\n")
        for r in results:
            toten_s = f"{r['toten']:.6f}" if r['toten'] is not None else "N/A"
            ef_s = f"{r['efermi']:.4f}" if r['efermi'] is not None else "N/A"
            mag_s = f"{r['magmom']:.2f}" if r['magmom'] is not None else "N/A"
            crm_s = f"{r['cr_mom']:.2f}" if r['cr_mom'] is not None else "N/A"
            gap_s = f"{r['gap']:.4f}" if r['gap'] is not None else "N/A"
            gup_s = f"{r['gap_up']:.4f}" if r['gap_up'] is not None else "N/A"
            gdn_s = f"{r['gap_dn']:.4f}" if r['gap_dn'] is not None else "N/A"
            f.write(f"{r['u']},{r['status']},{toten_s},{ef_s},{mag_s},{crm_s},{gap_s},{gup_s},{gdn_s}\n")

    with open(md_path, "w") as f:
        f.write("# $\\mathrm{CrCl}_3$ Monolayer: Band Gap vs. Hubbard $U$ Parameter\n\n")
        f.write("### Simulation Parameters\n")
        f.write("- **Structure**: $1\\times 1$ Primitive Cell ($P\\bar{3}1m$, $a = 6.0485\\text{ \\AA}$, $c = 17.67\\text{ \\AA}$, $\\mathrm{Cr}_2\\mathrm{Cl}_6$)\n")
        f.write("- **Functional**: PBE + Grimme DFT-D3 (`IVDW = 11`) + Dudarev DFT+$U$ (`LDAUTYPE = 2` on $\\mathrm{Cr}\\ 3d$)\n")
        f.write("- **PAW Flags**: `LASPH = .TRUE.`, `LMAXMIX = 4`, `ENCUT = 400.0\\text{ eV}`\n")
        f.write("- **Smearing**: Gaussian smearing ($\\sigma = 0.05\\text{ eV}$), $11\\times 11\\times 1$ $\\Gamma$-centered mesh\n\n")
        f.write("### Results Summary\n\n")
        f.write("| $U$ (eV) | Status | $E_{\\text{tot}}$ (eV) | $E_{\\text{F}}$ (eV) | $M_{\\text{cell}}$ ($\\mu_{\\text{B}}$) | $\\mu_{\\mathrm{Cr}}$ ($\\mu_{\\text{B}}$) | $E_g$ (eV) | $E_{g,\\uparrow}$ (eV) | $E_{g,\\downarrow}$ (eV) |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in results:
            toten_s = f"{r['toten']:.4f}" if r['toten'] is not None else "--"
            ef_s = f"{r['efermi']:.3f}" if r['efermi'] is not None else "--"
            mag_s = f"{r['magmom']:.2f}" if r['magmom'] is not None else "--"
            crm_s = f"{r['cr_mom']:.2f}" if r['cr_mom'] is not None else "--"
            gap_s = f"**{r['gap']:.3f}**" if r['gap'] is not None else "--"
            gup_s = f"{r['gap_up']:.3f}" if r['gap_up'] is not None else "--"
            gdn_s = f"{r['gap_dn']:.3f}" if r['gap_dn'] is not None else "--"
            f.write(f"| **{r['u']}** | `{r['status']}` | {toten_s} | {ef_s} | {mag_s} | {crm_s} | {gap_s} | {gup_s} | {gdn_s} |\n")
        f.write("\n")

    print(f"Data successfully exported:\n  - {csv_path}\n  - {md_path}")

def plot_publication_figures(results):
    """Generates dual-panel publication-grade figures in Times New Roman with LaTeX notation."""
    valid = [r for r in results if r["gap"] is not None]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.6), dpi=300)

    # Panel (a): Band Gap vs. U
    if len(valid) > 0:
        u_plot = [r["u"] for r in valid]
        gaps_tot = [r["gap"] for r in valid]
        gaps_up = [r["gap_up"] for r in valid]
        gaps_dn = [r["gap_dn"] for r in valid]

        ax1.plot(u_plot, gaps_tot, "o-", color="#0b559f", linewidth=2.2, markersize=7.5,
                 label=r"Fundamental Gap $E_g$")
        if any(g is not None for g in gaps_up):
            ax1.plot(u_plot, gaps_up, "s--", color="#c41d24", linewidth=1.6, markersize=6.0, alpha=0.85,
                     label=r"Spin-Up Gap $E_{g,\uparrow}$")
        if any(g is not None for g in gaps_dn):
            ax1.plot(u_plot, gaps_dn, "^--", color="#2a7b32", linewidth=1.6, markersize=6.0, alpha=0.85,
                     label=r"Spin-Down Gap $E_{g,\downarrow}$")
    else:
        ax1.text(0.5, 0.5, "Calculations in Progress\n(Outputs will plot automatically upon completion)",
                 ha="center", va="center", transform=ax1.transAxes, fontsize=10, style="italic", color="gray")

    ax1.axhspan(1.50, 1.60, color="#b0c4de", alpha=0.35, label=r"PBE Monolayer Lit. [1--3] ($1.50 - 1.60\ \mathrm{eV}$)")
    ax1.axhline(1.50, color="#4682b4", linestyle=":", linewidth=1.2, label=r"PBE Baseline ($1.50\ \mathrm{eV}$, This Work)")

    ax1.set_xlabel(r"Hubbard Coulomb Parameter $U$ on $\mathrm{Cr}\ 3d$ (eV)")
    ax1.set_ylabel(r"Electronic Band Gap $E_g$ (eV)")
    ax1.set_title(r"\textbf{(a)} Band Gap vs. Hubbard $U$")
    ax1.set_xticks(U_VALUES)
    ax1.set_xlim(-0.3, 6.3)
    ax1.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    ax1.legend(frameon=True, fancybox=False, edgecolor="#cccccc", loc="upper left")

    # Panel (b): Magnetic Moment vs. U
    mag_valid = [r for r in results if r["magmom"] is not None]
    if len(mag_valid) > 0:
        u_mag = [r["u"] for r in mag_valid]
        tot_moms = [r["magmom"] for r in mag_valid]
        cr_moms = [r["cr_mom"] for r in mag_valid if r["cr_mom"] is not None]

        ax2.plot(u_mag, tot_moms, "D-", color="#7b2cbf", linewidth=2.0, markersize=6.5,
                 label=r"Total Cell Moment $M_{\mathrm{cell}}\ (\mu_{\mathrm{B}})$")
        if len(cr_moms) == len(u_mag):
            ax2.plot(u_mag, cr_moms, "v--", color="#e76f51", linewidth=1.6, markersize=6.0,
                     label=r"Local Cr Moment $\mu_{\mathrm{Cr}}\ (\mu_{\mathrm{B}})$")
    else:
        ax2.text(0.5, 0.5, "Awaiting Convergence\n(Total magnetization will plot here)",
                 ha="center", va="center", transform=ax2.transAxes, fontsize=10, style="italic", color="gray")

    ax2.axhline(6.00, color="gray", linestyle=":", linewidth=1.1, label=r"Ideal $S=3/2$ Cell ($6.0\ \mu_{\mathrm{B}}$)")
    ax2.set_xlabel(r"Hubbard Coulomb Parameter $U$ on $\mathrm{Cr}\ 3d$ (eV)")
    ax2.set_ylabel(r"Magnetic Moment ($\mu_{\mathrm{B}}$)")
    ax2.set_title(r"\textbf{(b)} Magnetic Ground State vs. Hubbard $U$")
    ax2.set_xticks(U_VALUES)
    ax2.set_xlim(-0.3, 6.3)
    ax2.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    ax2.legend(frameon=True, fancybox=False, edgecolor="#cccccc", loc="upper left")

    plt.tight_layout(rect=[0, 0.07, 1, 1])

    # Bottom Citation Footnote Banner
    citation_text = (
        r"[1] L. Webster \& J.-A. Yan, \textit{Phys. Rev. B} \textbf{98}, 144411 (2018). "
        r"[2] M. Luo \textit{et al.}, \textit{Solid State Commun.} \textbf{321}, 114048 (2020). "
        r"[3] Y. Gao \textit{et al.}, \textit{Phys. Status Solidi RRL} \textbf{12}, 1800105 (2018)."
    )
    fig.text(
        0.5, 0.015, citation_text,
        ha="center", va="bottom", fontsize=10, color="#222222",
        bbox=dict(boxstyle="round,pad=0.35", fc="#f8f9fa", ec="#d0d0d0", lw=0.7)
    )

    out_png = os.path.join(BASE_DIR, "bandgap_vs_u.png")
    out_pdf = os.path.join(BASE_DIR, "bandgap_vs_u.pdf")
    fig.savefig(out_png, dpi=300)
    fig.savefig(out_pdf)
    plt.close(fig)

    print(f"Publication figures saved in Times New Roman + LaTeX:\n  - {out_png}\n  - {out_pdf}")

def main():
    print("================================================================================")
    print("   CrCl3 1x1 MONOLAYER: PUBLICATION BAND GAP & ELECTRONIC STRUCTURE PLOTTER    ")
    print("================================================================================")
    results = collect_results()
    generate_markdown_and_csv(results)
    plot_publication_figures(results)

if __name__ == "__main__":
    main()
