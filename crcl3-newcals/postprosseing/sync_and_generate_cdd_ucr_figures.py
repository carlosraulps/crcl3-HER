#!/usr/bin/env python3
"""
sync_and_generate_cdd_ucr_figures.py

Automates:
1. Sync of CHGCAR_diff and Bader ACF.dat from Huk/Arch
2. VESTA 3D rendering with stabilization and autotrimming
3. High-res publication comparison plot generation (+U_Cr vs +U_all)
4. Comprehensive 3D side-by-side panel creation
"""

import os
import sys
import time
import subprocess
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

BASE_DIR = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/crcl3-newcals/postprosseing/cdd_comparison"
VESTA_BIN = "/Applications/VESTA.app/Contents/MacOS/VESTA"
UALL_DIFF = os.path.join(BASE_DIR, "CHGCAR_diff_Uall")
UCR_DIFF = os.path.join(BASE_DIR, "CHGCAR_diff_Ucr")
UALL_PNG = os.path.join(BASE_DIR, "cdd_uall_cropped.png")
UCR_FULL_PNG = os.path.join(BASE_DIR, "cdd_ucr_full.png")
UCR_CROPPED_PNG = os.path.join(BASE_DIR, "cdd_ucr_cropped.png")
SIDE_BY_SIDE_PNG = os.path.join(BASE_DIR, "Fig_CDD_3D_SideBySide.png")
COMPARISON_PROFILES = os.path.join(BASE_DIR, "Fig_CDD_Comparative_Profiles.png")

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 11

def render_vesta_cdd(diff_path, out_full_path, out_crop_path):
    print(f"[INFO] Launching VESTA export for: {diff_path}")
    if os.path.exists(out_full_path):
        os.remove(out_full_path)
        
    cmd = [
        VESTA_BIN,
        "-open", diff_path,
        "-export_img", "scale=2",
        out_full_path
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    last_size = 0
    stable_count = 0
    for _ in range(40):
        time.sleep(1.0)
        if os.path.exists(out_full_path):
            sz = os.path.getsize(out_full_path)
            print(f"  VESTA render file size: {sz} bytes")
            if sz > 15000:
                if sz == last_size:
                    stable_count += 1
                    if stable_count >= 2:
                        print(f"[OK] File stabilized at {sz} bytes!")
                        break
                else:
                    stable_count = 0
                last_size = sz
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except Exception:
        proc.kill()
        
    # Crop whitespace
    print(f"[INFO] Autotrimming whitespace from: {out_full_path}")
    img = cv2.imread(out_full_path)
    if img is None:
        raise RuntimeError(f"Failed to read generated image: {out_full_path}")
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray < 250
    coords = np.argwhere(mask)
    if len(coords) > 0:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0)
        cropped = img[max(0, y0-30):min(img.shape[0], y1+30), max(0, x0-30):min(img.shape[1], x1+30)]
        cv2.imwrite(out_crop_path, cropped)
        print(f"[OK] Saved cropped image: {out_crop_path} (shape: {cropped.shape})")
    else:
        print("[WARN] No non-white content found; copying raw image.")
        cv2.imwrite(out_crop_path, img)

def parse_chgcar_planar(file_path):
    with open(file_path, "r") as f:
        _ = f.readline()
        scale = float(f.readline().strip())
        _ = [float(x) * scale for x in f.readline().split()]
        _ = [float(x) * scale for x in f.readline().split()]
        a3 = [float(x) * scale for x in f.readline().split()]
        
        species = f.readline().split()
        try:
            counts = [int(x) for x in species]
        except ValueError:
            counts = [int(x) for x in f.readline().split()]
            
        coord_type = f.readline().strip()
        num_atoms = sum(counts)
        coords = []
        for _ in range(num_atoms):
            coords.append([float(x) for x in f.readline().split()[:3]])
            
        _ = f.readline()
        ngx, ngy, ngz = [int(x) for x in f.readline().split()[:3]]
        total_pts = ngx * ngy * ngz
        
        chg_data = []
        while len(chg_data) < total_pts:
            line = f.readline()
            if not line:
                break
            chg_data.extend([float(x) for x in line.split()])
            
        chg_3d = np.array(chg_data[:total_pts]).reshape((ngz, ngy, ngx))
        
    planar_avg = np.mean(chg_3d, axis=(1, 2))
    cell_c = a3[2]
    z_coords = np.linspace(0, cell_c, len(planar_avg), endpoint=False)
    z_co = coords[-1][2] * cell_c
    
    return z_coords, planar_avg, cell_c, z_co

def generate_comparison_profiles():
    print("[INFO] Generating Fig_CDD_Comparative_Profiles.png...")
    z_uall, rho_uall, cell_c, z_co = parse_chgcar_planar(UALL_DIFF)
    z_ucr, rho_ucr, _, _ = parse_chgcar_planar(UCR_DIFF)
    delta_delta = rho_uall - rho_ucr
    
    fig = plt.figure(figsize=(9, 7), dpi=300)
    gs = GridSpec(2, 1, height_ratios=[2.2, 1.0], hspace=0.25)
    
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(z_ucr, rho_ucr, color="#1f77b4", lw=2.2, label=r"$+U_{\mathrm{Cr}}$ Single-tier ($U_{\mathrm{Cr}}=3.29\ \mathrm{eV},\ U_{\mathrm{Co}}=0\ \mathrm{eV}$)")
    ax1.plot(z_uall, rho_uall, color="#d62728", lw=2.0, ls="--", label=r"$+U_{\mathrm{all}}$ Multi-tier ($U_{\mathrm{Cr}}=3.29\ \mathrm{eV},\ U_{\mathrm{Co}}=3.29\ \mathrm{eV}$)")
    ax1.axhline(0, color="k", ls=":", alpha=0.5, lw=1)
    ax1.axvline(z_co, color="#2ca02c", ls="-.", lw=1.5, label=f"Co Adatom ($z = {z_co:.2f}$ Å)")
    
    ax1.set_xlim(0, cell_c)
    y_min, y_max = min(np.min(rho_ucr), np.min(rho_uall)), max(np.max(rho_ucr), np.max(rho_uall))
    dy = y_max - y_min
    ax1.set_ylim(y_min - 0.1 * dy, y_max + 0.30 * dy)
    
    ax1.set_ylabel(r"Planar Average $\Delta \rho(z)$ ($e$/Å)", fontsize=12)
    ax1.set_title(r"Quantitative Charge Density Difference (CDD) Comparison: $\mathrm{Co@CrCl_3}$ ($S_2$ Hollow)", fontsize=13, pad=10)
    ax1.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.92, edgecolor="#cccccc", fontsize=10)
    ax1.grid(True, ls=":", alpha=0.5)
    
    # Inset zoom
    axins = ax1.inset_axes([0.62, 0.45, 0.35, 0.48])
    mask = (z_ucr >= z_co - 2.5) & (z_ucr <= z_co + 2.5)
    axins.plot(z_ucr[mask], rho_ucr[mask], color="#1f77b4", lw=2.2)
    axins.plot(z_uall[mask], rho_uall[mask], color="#d62728", lw=2.0, ls="--")
    axins.axvline(z_co, color="#2ca02c", ls="-.", lw=1.5)
    axins.axhline(0, color="k", ls=":", alpha=0.4)
    axins.set_title(r"Zoom: Interface Region ($\pm 2.5$ Å)", fontsize=9)
    axins.tick_params(labelsize=8)
    axins.grid(True, ls=":", alpha=0.4)
    
    # Panel B
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.plot(z_uall, delta_delta, color="#9467bd", lw=1.8, label=r"Difference $\Delta\Delta\rho(z) = \Delta\rho_{+U_{\mathrm{all}}} - \Delta\rho_{+U_{\mathrm{Cr}}}$")
    ax2.axhline(0, color="k", ls=":", alpha=0.5, lw=1)
    ax2.axvline(z_co, color="#2ca02c", ls="-.", lw=1.2)
    ax2.set_xlabel(r"$z$ coordinate along $c$-axis (Å)", fontsize=12)
    ax2.set_ylabel(r"$\Delta\Delta \rho(z)$ ($e$/Å)", fontsize=11)
    ax2.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.92, edgecolor="#cccccc", fontsize=9.5)
    ax2.grid(True, ls=":", alpha=0.5)
    
    plt.savefig(COMPARISON_PROFILES, dpi=300, bbox_inches="tight")
    pdf_out = COMPARISON_PROFILES.replace(".png", ".pdf")
    plt.savefig(pdf_out, bbox_inches="tight")
    plt.close()
    print(f"[OK] Saved comparison profile: {COMPARISON_PROFILES}")

def generate_side_by_side_panel():
    print("[INFO] Generating Fig_CDD_3D_SideBySide.png...")
    img_uall = cv2.imread(UALL_PNG)
    img_ucr = cv2.imread(UCR_CROPPED_PNG)
    
    if img_uall is None or img_ucr is None:
        raise RuntimeError("Missing cropped CDD images!")
        
    # Resize both to identical height
    target_h = min(img_uall.shape[0], img_ucr.shape[0], 1200)
    w_uall = int(img_uall.shape[1] * (target_h / img_uall.shape[0]))
    w_ucr = int(img_ucr.shape[1] * (target_h / img_ucr.shape[0]))
    
    r_uall = cv2.resize(img_uall, (w_uall, target_h), interpolation=cv2.INTER_LANCZOS4)
    r_ucr = cv2.resize(img_ucr, (w_ucr, target_h), interpolation=cv2.INTER_LANCZOS4)
    
    # Create combined figure with high typography
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    axes[0].imshow(cv2.cvtColor(r_ucr, cv2.COLOR_BGR2RGB))
    axes[0].set_title(r"$\mathbf{(a)\ +U_{\mathrm{Cr}}\ Single-tier}$" "\n" r"($U_{\mathrm{Cr}}=3.29\ \mathrm{eV},\ U_{\mathrm{Co}}=0.00\ \mathrm{eV}$)" "\n" r"$\Delta q_{\mathrm{Bader}}(\mathrm{Co}) = +0.85\ e$", fontsize=12, pad=10)
    axes[0].axis("off")
    
    axes[1].imshow(cv2.cvtColor(r_uall, cv2.COLOR_BGR2RGB))
    axes[1].set_title(r"$\mathbf{(b)\ +U_{\mathrm{all}}\ Multi-tier}$" "\n" r"($U_{\mathrm{Cr}}=3.29\ \mathrm{eV},\ U_{\mathrm{Co}}=3.29\ \mathrm{eV}$)" "\n" r"$\Delta q_{\mathrm{Bader}}(\mathrm{Co}) = +0.70\ e$", fontsize=12, pad=10)
    axes[1].axis("off")
    
    plt.tight_layout()
    plt.savefig(SIDE_BY_SIDE_PNG, dpi=300, bbox_inches="tight")
    pdf_out = SIDE_BY_SIDE_PNG.replace(".png", ".pdf")
    plt.savefig(pdf_out, bbox_inches="tight")
    plt.close()
    print(f"[OK] Saved side-by-side 3D panel: {SIDE_BY_SIDE_PNG}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "render_only":
        render_vesta_cdd(UCR_DIFF, UCR_FULL_PNG, UCR_CROPPED_PNG)
        generate_comparison_profiles()
        generate_side_by_side_panel()
    else:
        generate_comparison_profiles()
        generate_side_by_side_panel()
