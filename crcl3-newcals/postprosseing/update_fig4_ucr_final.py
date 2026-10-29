#!/usr/bin/env python3
"""
update_fig4_ucr_final.py
========================
1. Generates authentic standalone panel_b_Fe_CDD_Ucr.png and panel_c_Ni_CDD_Ucr.png (1400x1140)
   using the converged single-atom subtraction CHGCAR_diff renders from Carbono.
2. Updates Fig4_Ucr.png (4518x2539) by splicing the authentic +U_Cr Fe and Ni 3D CDD rhombuses
   into panels (b) and (c), strictly preserving:
     - Panel (a) (+U_Cr Co authentic render)
     - All panel titles and subpanel labels (a), (b), (c)
     - The left side-view column (x in [0, 320])
     - All bottom-half panels (d), (e), (f) containing the user's manual Affinity Designer edits
       and numerical Bader cards (+0.77 e, +0.94 e, +0.59 e).
3. Updates Fig4_Ucr.svg and Fig4.svg with the new base64 PNG raster.
4. Exports pixel-perfect Fig4_Ucr.pdf and Fig4.pdf using Inkscape.
5. Synchronizes outputs across:
     - ACS_version/ACS_resubmission/figure/
     - crcl3-newcals/postprosseing/
     - crcl3-newcals/postprosseing/images-juan/04_Fig4_CDD_and_Bader_Charge/
"""

import os
import sys
import base64
import subprocess
from PIL import Image
import numpy as np

# Base paths
ROOT_DIR = "/home/cr/simulations/crcl3-HER"
POST_DIR = os.path.join(ROOT_DIR, "crcl3-newcals/postprosseing")
FIG4_DIR = os.path.join(POST_DIR, "images-juan/04_Fig4_CDD_and_Bader_Charge")
ACS_FIG_DIR = os.path.join(ROOT_DIR, "ACS_version/ACS_resubmission/figure")
CDD_FE_NI_DIR = os.path.join(POST_DIR, "cdd_ucr_fe_ni")

RHOMBUS_FE = os.path.join(CDD_FE_NI_DIR, "fe/rhombus_fe.png")
RHOMBUS_NI = os.path.join(CDD_FE_NI_DIR, "ni/rhombus_ni.png")

BASE_FIG4_UCR = os.path.join(ACS_FIG_DIR, "Fig4_Ucr.png")

def main():
    print("[1] Loading reference images and rhombus crops...")
    if not os.path.exists(RHOMBUS_FE) or not os.path.exists(RHOMBUS_NI):
        raise FileNotFoundError(f"Missing rhombus crops: {RHOMBUS_FE} or {RHOMBUS_NI}")
        
    im_rhombus_fe = Image.open(RHOMBUS_FE).convert("RGB")
    im_rhombus_ni = Image.open(RHOMBUS_NI).convert("RGB")
    
    # Load base Fig4_Ucr.png (4518 x 2539)
    im_base = Image.open(BASE_FIG4_UCR).convert("RGB")
    arr_base = np.array(im_base)
    H, W, _ = arr_base.shape
    print(f"    Base Fig4_Ucr.png shape: {arr_base.shape}")
    assert (H, W) == (2539, 4518), f"Unexpected shape: {(H, W)}"

    # Template panels for labels
    p_b_templ = Image.open(os.path.join(FIG4_DIR, "panel_b_Fe_CDD_Uall.png")).convert("RGB")
    arr_b_templ = np.array(p_b_templ)
    p_c_templ = Image.open(os.path.join(FIG4_DIR, "panel_c_Ni_CDD_Uall.png")).convert("RGB")
    arr_c_templ = np.array(p_c_templ)

    # -------------------------------------------------------------
    # Step 1: Generate Standalone Panels (b) and (c) (1400 x 1140)
    # -------------------------------------------------------------
    print("[2] Generating standalone panel_b_Fe_CDD_Ucr.png and panel_c_Ni_CDD_Ucr.png...")
    # Fe panel: target size (1400, 880)
    fe_scaled = im_rhombus_fe.resize((1400, 880), Image.Resampling.LANCZOS)
    arr_panel_b = np.ones((1140, 1400, 3), dtype=np.uint8) * 255
    arr_panel_b[0:880, 0:1400] = np.array(fe_scaled)
    # Preserve label (b) exactly from template at y: 950 to 1140
    arr_panel_b[950:1140, :] = arr_b_templ[950:1140, :]
    
    out_b_path = os.path.join(FIG4_DIR, "panel_b_Fe_CDD_Ucr.png")
    Image.fromarray(arr_panel_b).save(out_b_path)
    print(f"    Saved: {out_b_path}")

    # Ni panel: target size (1400, 874)
    ni_scaled = im_rhombus_ni.resize((1400, 874), Image.Resampling.LANCZOS)
    arr_panel_c = np.ones((1140, 1400, 3), dtype=np.uint8) * 255
    arr_panel_c[0:874, 0:1400] = np.array(ni_scaled)
    # Preserve label (c) exactly from template at y: 950 to 1140
    arr_panel_c[950:1140, :] = arr_c_templ[950:1140, :]
    
    out_c_path = os.path.join(FIG4_DIR, "panel_c_Ni_CDD_Ucr.png")
    Image.fromarray(arr_panel_c).save(out_c_path)
    print(f"    Saved: {out_c_path}")

    # -------------------------------------------------------------
    # Step 2: Composite Fig4_Ucr.png (4518 x 2539)
    # -------------------------------------------------------------
    print("[3] Updating composite Fig4_Ucr.png...")
    arr_final = arr_base.copy()
    
    # Panel B rhombus: x in [1650, 3050], y in [40, 950]
    # Clear only the rhombus area (not the label (b) at y > 950)
    arr_final[40:950, 1650:3050] = 255
    arr_final[40:40+880, 1650:1650+1400] = np.array(fe_scaled)
    
    # Panel C rhombus: x in [2980, 4380], y in [40, 950]
    # Clear only the rhombus area (not the label (c) at y > 950)
    arr_final[40:950, 2980:4380] = 255
    arr_final[40:40+874, 2980:2980+1400] = np.array(ni_scaled)

    # Verify that bottom half (y >= 1180) is 100% BIT-FOR-BIT IDENTICAL to base
    assert np.array_equal(arr_final[1180:, :], arr_base[1180:, :]), "CRITICAL: Bottom half was modified!"
    # Verify that panel A is 100% BIT-FOR-BIT IDENTICAL to base
    assert np.array_equal(arr_final[40:1180, 320:1650], arr_base[40:1180, 320:1650]), "CRITICAL: Panel A was modified!"
    # Verify that left column is 100% BIT-FOR-BIT IDENTICAL to base
    assert np.array_equal(arr_final[40:1180, :320], arr_base[40:1180, :320]), "CRITICAL: Left column was modified!"
    print("    [✓] Invariant check passed: Panels (d,e,f), Panel (a), and side axes remain 100% identical!")

    # Save Fig4_Ucr.png across all relevant locations
    dest_pngs = [
        os.path.join(ACS_FIG_DIR, "Fig4_Ucr.png"),
        os.path.join(POST_DIR, "Fig4_Ucr.png"),
        os.path.join(FIG4_DIR, "Fig4_Ucr.png"),
    ]
    im_final = Image.fromarray(arr_final)
    for p in dest_pngs:
        im_final.save(p)
        print(f"    Saved high-res PNG: {p}")

    # -------------------------------------------------------------
    # Step 3: Update SVG files with updated base64 raster
    # -------------------------------------------------------------
    print("[4] Updating Fig4_Ucr.svg and Fig4.svg with new embedded raster...")
    import io
    buf = io.BytesIO()
    im_final.save(buf, format="PNG")
    b64_png = base64.b64encode(buf.getvalue()).decode("ascii")
    data_uri = f"data:image/png;base64,{b64_png}"

    # Update Fig4_Ucr.svg
    svg_ucr_template = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="722.88" height="406.24" viewBox="0 0 722.88 406.24">
  <defs>
    <style type="text/css">
      text {{
        font-family: "Times New Roman", Times, "DejaVu Serif", serif;
      }}
    </style>
  </defs>
  <g id="figure4_ucr">
    <!-- Authentic 600 DPI Background Image with Renders and Manual Affinity Edits -->
    <image id="bg_raster" x="0" y="0" width="722.88" height="406.24" preserveAspectRatio="none" xlink:href="{data_uri}" />

    <!-- Non-Colliding Functional Tier Badge -->
    <g id="badge_ucr" transform="translate(580, 8)">
      <rect x="0" y="0" width="132" height="22" rx="3.5" ry="3.5" fill="#ffffff" fill-opacity="0.96" stroke="#cccccc" stroke-width="0.8" />
      <!-- Distinct text tags to guarantee zero horizontal kerning collision -->
      <text x="14" y="15.5" font-size="11" font-weight="bold" fill="#1a1a1a">+U</text>
      <text x="31" y="17.5" font-size="8.5" font-weight="bold" fill="#1a1a1a">Cr</text>
      <text x="56" y="15.5" font-size="11" font-weight="bold" fill="#1a1a1a">= 3.29 eV</text>
    </g>
  </g>
</svg>
'''
    dest_svgs = [
        os.path.join(ACS_FIG_DIR, "Fig4_Ucr.svg"),
        os.path.join(POST_DIR, "Fig4_Ucr.svg"),
        os.path.join(FIG4_DIR, "Fig4_Ucr.svg"),
    ]
    for p in dest_svgs:
        with open(p, "w", encoding="utf-8") as f:
            f.write(svg_ucr_template)
        print(f"    Saved SVG: {p}")

    # Also update Fig4.svg (the main manuscript Figure 4)
    fig4_svg_path = os.path.join(ACS_FIG_DIR, "Fig4.svg")
    if os.path.exists(fig4_svg_path):
        with open(fig4_svg_path, "r", encoding="utf-8") as f:
            content = f.read()
        import re
        content_new = re.sub(r'xlink:href="data:image/png;base64,[^"]+"', f'xlink:href="{data_uri}"', content)
        with open(fig4_svg_path, "w", encoding="utf-8") as f:
            f.write(content_new)
        print(f"    Updated main manuscript Fig4.svg: {fig4_svg_path}")

    # -------------------------------------------------------------
    # Step 4: Compile PDFs using Inkscape
    # -------------------------------------------------------------
    print("[5] Compiling publication-grade PDF files via Inkscape...")
    svg_src = os.path.join(ACS_FIG_DIR, "Fig4_Ucr.svg")
    pdf_out = os.path.join(ACS_FIG_DIR, "Fig4_Ucr.pdf")
    subprocess.run(["inkscape", f"--export-filename={pdf_out}", svg_src], check=True)
    print(f"    Compiled: {pdf_out}")

    # Copy to postprosseing and 04_Fig4_CDD_and_Bader_Charge
    import shutil
    shutil.copy2(pdf_out, os.path.join(POST_DIR, "Fig4_Ucr.pdf"))
    shutil.copy2(pdf_out, os.path.join(FIG4_DIR, "Fig4_Ucr.pdf"))
    print("    Synchronized Fig4_Ucr.pdf across all folders.")

    # Also compile Fig4.pdf for the main manuscript
    if os.path.exists(fig4_svg_path):
        main_pdf = os.path.join(ACS_FIG_DIR, "Fig4.pdf")
        subprocess.run(["inkscape", f"--export-filename={main_pdf}", fig4_svg_path], check=True)
        print(f"    Compiled main manuscript Fig4.pdf: {main_pdf}")

    print("[✓] ALL Figure 4 CDD 3D deliverables updated successfully!")

if __name__ == "__main__":
    main()
