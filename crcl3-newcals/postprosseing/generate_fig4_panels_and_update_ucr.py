#!/usr/bin/env python3
"""
generate_fig4_panels_and_update_ucr.py (pixel-perfect)
======================================================
Takes the original Fig4_Ucr.png from git (with authentic +U_Cr Bader cards),
cleanly updates ONLY panel (a) with the authentic +U_Cr CDD isosurface,
and exports all individual panels for Affinity Designer.
"""

import os
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

FIG4_DIR = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/crcl3-newcals/postprosseing/images-juan/04_Fig4_CDD_and_Bader_Charge"
CDD_DIR = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/crcl3-newcals/postprosseing/cdd_comparison"

GIT_UCR_BASE = os.path.join(CDD_DIR, "orig_ucr_git.png")
UALL_SRC = os.path.join(FIG4_DIR, "Fig4_Uall.png")
UCR_SRC = os.path.join(FIG4_DIR, "Fig4_Ucr.png")
UCR_CDD_CROPPED = os.path.join(CDD_DIR, "cdd_ucr_cropped.png")

def main():
    img_ucr_base = cv2.imread(GIT_UCR_BASE)
    img_uall = cv2.imread(UALL_SRC)
    H, W, _ = img_ucr_base.shape

    # 1. Load Ucr CDD and find rhombus bounding box
    img_ucr_cdd = cv2.imread(UCR_CDD_CROPPED)
    gray = cv2.cvtColor(img_ucr_cdd, cv2.COLOR_BGR2GRAY)
    gray[:, :900] = 255
    mask = gray < 250
    y_idx, x_idx = np.where(mask)
    rhombus_ucr = img_ucr_cdd[y_idx.min():y_idx.max()+1, x_idx.min():x_idx.max()+1]

    # 2. Reference dimensions from panel (b)
    b_crop = img_ucr_base[40:950, 1680:3050]
    b_gray = cv2.cvtColor(b_crop, cv2.COLOR_BGR2GRAY)
    b_mask = b_gray < 250
    by_idx, bx_idx = np.where(b_mask)
    target_rhombus_h = by_idx.max() - by_idx.min() + 1
    target_rhombus_w = bx_idx.max() - bx_idx.min() + 1

    rhombus_scaled = cv2.resize(rhombus_ucr, (target_rhombus_w, target_rhombus_h), interpolation=cv2.INTER_LANCZOS4)

    # 3. Create standalone panels for Affinity Designer
    # Panel A (U_all)
    panel_a_uall = img_uall[40:1180, 320:1720]
    cv2.imwrite(os.path.join(FIG4_DIR, "panel_a_Co_CDD_Uall.png"), panel_a_uall)
    
    # Panel B (Fe)
    panel_b_fe = img_uall[40:1180, 1650:3050]
    cv2.imwrite(os.path.join(FIG4_DIR, "panel_b_Fe_CDD_Uall.png"), panel_b_fe)
    
    # Panel C (Ni)
    panel_c_ni = img_uall[40:1180, 2980:4380]
    cv2.imwrite(os.path.join(FIG4_DIR, "panel_c_Ni_CDD_Uall.png"), panel_c_ni)

    # Panel A (U_Cr)
    frame_h, frame_w = panel_a_uall.shape[0], panel_a_uall.shape[1]
    panel_a_ucr = np.ones((frame_h, frame_w, 3), dtype=np.uint8) * 255
    y_paste, x_paste = by_idx.min(), bx_idx.min()
    panel_a_ucr[y_paste:y_paste+target_rhombus_h, x_paste:x_paste+target_rhombus_w] = rhombus_scaled
    # label (a)
    label_a = panel_a_uall[frame_h-150:frame_h, :]
    panel_a_ucr[frame_h-150:frame_h, :] = label_a
    cv2.imwrite(os.path.join(FIG4_DIR, "panel_a_Co_CDD_Ucr.png"), panel_a_ucr)
    print("[✓] All 4 standalone panels exported successfully.")

    # 4. Update Fig4_Ucr.png cleanly
    img_ucr_final = img_ucr_base.copy()
    # Clean only the rhombus area of panel (a)
    img_ucr_final[30:970, 310:1750] = 255
    # Paste the new authentic +U_Cr rhombus
    a_x = 320 + x_paste
    a_y = 40 + y_paste
    img_ucr_final[a_y:a_y+target_rhombus_h, a_x:a_x+target_rhombus_w] = rhombus_scaled

    cv2.imwrite(UCR_SRC, img_ucr_final)
    print(f"[✓] Pixel-perfect Fig4_Ucr.png updated: {UCR_SRC}")

    # 5. Export matching PDF
    pdf_out = os.path.join(FIG4_DIR, "Fig4_Ucr.pdf")
    fig, ax = plt.subplots(figsize=(W / 300, H / 300), dpi=300)
    ax.imshow(cv2.cvtColor(img_ucr_final, cv2.COLOR_BGR2RGB))
    ax.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(pdf_out, dpi=300)
    plt.close()
    print(f"[✓] Fig4_Ucr.pdf updated: {pdf_out}")

if __name__ == "__main__":
    main()
