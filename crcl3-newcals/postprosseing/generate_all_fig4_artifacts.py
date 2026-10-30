#!/usr/bin/env python3
"""
generate_all_fig4_artifacts.py
==============================
Assembles publication-grade Figure 4 deliverables for both +U_Cr and +U_all tiers:
1. Imports authentic 3D CDD isosurfaces rendered by VESTA for Co, Fe, Ni.
2. Extracts rhombuses with preserved aspect ratio and embeds them into the master template.
3. Preserves atom legend, sublabels (a-f), Bader maps, and dual-tier Bader smart cards.
4. Generates:
   - Full figures: Fig4_Ucr.png, Fig4_Ucr.pdf, Fig4_Uall.png, Fig4_Uall.pdf, Fig4.png, Fig4.pdf
   - Standalone panels for Affinity Designer:
     * panel_a_Co_CDD_Ucr.png, panel_b_Fe_CDD_Ucr.png, panel_c_Ni_CDD_Ucr.png
     * panel_a_Co_CDD_Uall.png, panel_b_Fe_CDD_Uall.png, panel_c_Ni_CDD_Uall.png
5. Syncs deliverables across all manuscript figure directories.
"""

import os
import sys
import shutil
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

REPO_ROOT = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER"
BASE_DIR = os.path.join(REPO_ROOT, "crcl3-newcals", "postprosseing", "cdd_comparison")
FIG4_DIR = os.path.join(REPO_ROOT, "crcl3-newcals", "postprosseing", "images-juan", "04_Fig4_CDD_and_Bader_Charge")
GIT_UCR_BASE = os.path.join(BASE_DIR, "orig_ucr_git.png")

DEST_DIRS = [
    FIG4_DIR,
    os.path.join(REPO_ROOT, "crcl3-newcals", "postprosseing"),
    os.path.join(REPO_ROOT, "temporary", "ACS_resubmission", "figure"),
    os.path.join(REPO_ROOT, "temporary", "ACS_resubmission", "new_figures"),
    os.path.join(REPO_ROOT, "ACS_version", "ACS_resubmission", "figure"),
    os.path.join(REPO_ROOT, "ACS_version", "figure"),
]

def extract_rhombus(crop_png):
    img = cv2.imread(crop_png)
    if img is None:
        raise FileNotFoundError(f"Cannot read {crop_png}")
    main = img.copy()
    main[:, :900] = 255
    gray = cv2.cvtColor(main, cv2.COLOR_BGR2GRAY)
    mask = gray < 250
    coords = np.argwhere(mask)
    y0, y1 = coords[:, 0].min(), coords[:, 0].max()
    x0, x1 = coords[:, 1].min(), coords[:, 1].max()
    return img[y0:y1+1, x0:x1+1]

def export_pdf(img_bgr, out_pdf_path):
    H, W = img_bgr.shape[:2]
    fig, ax = plt.subplots(figsize=(W / 300, H / 300), dpi=300)
    ax.imshow(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    ax.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(out_pdf_path, dpi=300)
    plt.close()

def main():
    base_img = cv2.imread(GIT_UCR_BASE)
    if base_img is None:
        raise FileNotFoundError(f"Base image not found: {GIT_UCR_BASE}")
    H, W, _ = base_img.shape

    target_w = 1330
    centers_x = [1045, 2390, 3715]
    center_y = 475

    produced_files = {}

    for tier, tier_label in [('ucr', 'Ucr'), ('uall', 'Uall')]:
        print(f"\n=======================================================")
        print(f"  Generating Figure 4 Deliverables: +{tier_label}")
        print(f"=======================================================")
        
        # 1. Load VESTA renders
        p_co = os.path.join(BASE_DIR, f"cdd_co_{tier}_cropped.png")
        p_fe = os.path.join(BASE_DIR, f"cdd_fe_{tier}_cropped.png")
        p_ni = os.path.join(BASE_DIR, f"cdd_ni_{tier}_cropped.png")
        
        rh_co = extract_rhombus(p_co)
        rh_fe = extract_rhombus(p_fe)
        rh_ni = extract_rhombus(p_ni)
        
        scale_co = target_w / rh_co.shape[1]
        scale_fe = target_w / rh_fe.shape[1]
        scale_ni = target_w / rh_ni.shape[1]
        
        rh_co_s = cv2.resize(rh_co, (target_w, int(round(rh_co.shape[0] * scale_co))), interpolation=cv2.INTER_LANCZOS4)
        rh_fe_s = cv2.resize(rh_fe, (target_w, int(round(rh_fe.shape[0] * scale_fe))), interpolation=cv2.INTER_LANCZOS4)
        rh_ni_s = cv2.resize(rh_ni, (target_w, int(round(rh_ni.shape[0] * scale_ni))), interpolation=cv2.INTER_LANCZOS4)
        
        # 2. Assemble figure canvas
        canvas = base_img.copy()
        # Clear from x = 230 to 4450 to eliminate leftover old panel corners near the legend
        canvas[20:980, 230:4450] = 255
        
        rh_list = [rh_co_s, rh_fe_s, rh_ni_s]
        for cx, rh in zip(centers_x, rh_list):
            h, w = rh.shape[:2]
            x0 = cx - w // 2
            y0 = center_y - h // 2
            canvas[y0:y0+h, x0:x0+w] = np.minimum(canvas[y0:y0+h, x0:x0+w], rh)
            
        # 3. Export standalone panels for Affinity Designer
        panel_a = canvas[40:1180, 320:1720]
        panel_b = canvas[40:1180, 1650:3050]
        panel_c = canvas[40:1180, 2980:4380]
        
        path_panel_a = os.path.join(FIG4_DIR, f"panel_a_Co_CDD_{tier_label}.png")
        path_panel_b = os.path.join(FIG4_DIR, f"panel_b_Fe_CDD_{tier_label}.png")
        path_panel_c = os.path.join(FIG4_DIR, f"panel_c_Ni_CDD_{tier_label}.png")
        
        cv2.imwrite(path_panel_a, panel_a)
        cv2.imwrite(path_panel_b, panel_b)
        cv2.imwrite(path_panel_c, panel_c)
        print(f"[✓] Exported standalone panel A: {path_panel_a}")
        print(f"[✓] Exported standalone panel B: {path_panel_b}")
        print(f"[✓] Exported standalone panel C: {path_panel_c}")
        
        # 4. Save primary Fig4 files in FIG4_DIR
        out_png = os.path.join(FIG4_DIR, f"Fig4_{tier_label}.png")
        out_pdf = os.path.join(FIG4_DIR, f"Fig4_{tier_label}.pdf")
        cv2.imwrite(out_png, canvas)
        export_pdf(canvas, out_pdf)
        print(f"[✓] Exported {out_png}")
        print(f"[✓] Exported {out_pdf}")
        
        produced_files[tier_label] = (out_png, out_pdf, canvas)

    # 5. Make +U_Cr the default Fig4.png / Fig4.pdf
    default_png = os.path.join(FIG4_DIR, "Fig4.png")
    default_pdf = os.path.join(FIG4_DIR, "Fig4.pdf")
    shutil.copy2(produced_files['Ucr'][0], default_png)
    shutil.copy2(produced_files['Ucr'][1], default_pdf)
    print(f"\n[✓] Set Fig4.png and Fig4.pdf default to +U_Cr tier.")

    def safe_copy(src, dst):
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copy2(src, dst)

    # 6. Distribute across destination directories
    for d in DEST_DIRS:
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
            
        # Copy tier-specific
        safe_copy(produced_files['Ucr'][0], os.path.join(d, "Fig4_Ucr.png"))
        safe_copy(produced_files['Ucr'][1], os.path.join(d, "Fig4_Ucr.pdf"))
        safe_copy(produced_files['Uall'][0], os.path.join(d, "Fig4_Uall.png"))
        safe_copy(produced_files['Uall'][1], os.path.join(d, "Fig4_Uall.pdf"))
        
        # Copy standard Fig4
        safe_copy(default_png, os.path.join(d, "Fig4.png"))
        safe_copy(default_pdf, os.path.join(d, "Fig4.pdf"))
        print(f"[✓] Synced Fig4 files to: {d}")

    print("\n🎉 ALL FIGURE 4 DELIVERABLES ASSEMBLED AND SYNCHRONIZED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
