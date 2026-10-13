#!/usr/bin/env python3
"""
update_fig7_composites.py
=========================
Updates Figure 7 composites by:
  1. Patching Panels (a-f) structural annotations with exact DFT-relaxed distances
     for both single-site +U_Cr and multi-site +U_all tiers.
  2. Splicing the newly verified Panels (g) and (h) energy decomposition bar charts.
  3. Generating both PNG (300 DPI) and vector PDF outputs for:
     - Fig7_composite_pbe_d3_u.png / .pdf
     - Fig7_Ucr.png / .pdf
     - Fig7.png / .pdf
     - Fig7_composite_u_all.png / .pdf
     - Fig7_Uall.png / .pdf
  4. Synchronizing deliverables directly into:
     - crcl3-newcals/postprosseing/images-juan/07_Fig7_HER_Thermodynamics/
     - ACS_version/ACS_resubmission/figure/
"""

import os
import shutil
import numpy as np
from PIL import Image, ImageFont, ImageDraw

POST_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals/postprosseing"
JUAN_DIR = os.path.join(POST_DIR, "images-juan/07_Fig7_HER_Thermodynamics")
ACS_FIG_DIR = "/home/cr/simulations/crcl3-HER/ACS_version/ACS_resubmission/figure"
ORIG_FIG7 = "/home/cr/simulations/crcl3-HER/ACS_version/figure/Fig7.png"

FONT_PATH = "/usr/share/fonts/TTF/Timesbd.TTF"

# Precise label replacement configurations:
# center_x, center_y, angle, whiten_w, whiten_h
LABEL_GEOMETRY = {
    # Panel a (Co ads)
    'a_cl_horiz': (940, 298, 0, 160, 60),
    'a_cl_diag':  (1085, 395, -50, 160, 65),
    'a_h_side':   (1115, 785, 0, 160, 60),

    # Panel b (Fe ads)
    'b_cl_horiz': (1980, 298, 0, 160, 60),
    'b_cl_diag':  (2125, 395, -50, 160, 65),
    'b_h_side':   (2180, 740, 0, 160, 60),

    # Panel c (Ni ads)
    'c_cl_horiz': (3020, 298, 0, 160, 60),
    'c_cl_diag':  (3165, 395, -50, 160, 65),
    'c_h_side':   (3220, 775, 0, 160, 60),

    # Panel d (Co emb)
    'd_cl_left':  (930, 1755, 0, 160, 60),
    'd_cl_right': (1080, 1845, 0, 160, 60),
    'd_h_side':   (1110, 2225, 0, 160, 60),

    # Panel e (Fe emb)
    'e_cl_left':  (1980, 1755, 0, 160, 60),
    'e_cl_right': (2130, 1835, -50, 160, 65),
    'e_h_side':   (2180, 2180, 0, 160, 60),

    # Panel f (Ni emb)
    'f_cl_diag':  (3040, 1835, -50, 160, 65),
    'f_cl_right': (3170, 1755, 0, 160, 60),
    'f_h_side':   (3180, 2225, 0, 160, 60),
}

# Distance values for each tier
TIER_DISTANCES = {
    'pbe_d3_u': {
        'a_cl_horiz': '2.28 Å',
        'a_cl_diag':  '2.33 Å',
        'a_h_side':   '1.55 Å',

        'b_cl_horiz': '2.32 Å',
        'b_cl_diag':  '2.34 Å',
        'b_h_side':   '1.59 Å',

        'c_cl_horiz': '2.19 Å',
        'c_cl_diag':  '2.21 Å',
        'c_h_side':   '1.45 Å',

        'd_cl_left':  '2.40 Å',
        'd_cl_right': '2.54 Å',
        'd_h_side':   '1.47 Å',

        'e_cl_left':  '2.25 Å',
        'e_cl_right': '2.36 Å',
        'e_h_side':   '1.48 Å',

        'f_cl_diag':  '2.29 Å',
        'f_cl_right': '2.44 Å',
        'f_h_side':   '1.52 Å',
    },
    'u_all': {
        'a_cl_horiz': '2.34 Å',
        'a_cl_diag':  '2.42 Å',
        'a_h_side':   '1.55 Å',

        'b_cl_horiz': '2.34 Å',
        'b_cl_diag':  '2.45 Å',
        'b_h_side':   '1.61 Å',

        'c_cl_horiz': '2.20 Å',
        'c_cl_diag':  '2.20 Å',
        'c_h_side':   '1.44 Å',

        'd_cl_left':  '2.42 Å',
        'd_cl_right': '2.69 Å',
        'd_h_side':   '2.38 Å',

        'e_cl_left':  '2.41 Å',
        'e_cl_right': '2.66 Å',
        'e_h_side':   '1.53 Å',

        'f_cl_diag':  '2.33 Å',
        'f_cl_right': '2.44 Å',
        'f_h_side':   '1.63 Å',
    }
}

def render_text_patch(text, font, angle=0):
    """Renders bold red text with transparent background, rotated if needed."""
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + 16
    h = bbox[3] - bbox[1] + 16
    
    txt_im = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    d = ImageDraw.Draw(txt_im)
    d.text((-bbox[0] + 8, -bbox[1] + 8), text, font=font, fill=(255, 0, 0, 255))
    
    if angle != 0:
        txt_im = txt_im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    return txt_im

def patch_top_panels(im_top, tier):
    """Patches all 18 distance labels on the top half of Fig 7."""
    patched = im_top.copy()
    draw = ImageDraw.Draw(patched)
    font = ImageFont.truetype(FONT_PATH, 46)
    
    dist_map = TIER_DISTANCES[tier]
    
    for key, (cx, cy, angle, ww, wh) in LABEL_GEOMETRY.items():
        val = dist_map[key]
        
        # 1. Whiten the old label
        if angle == 0:
            x0 = cx - ww // 2
            y0 = cy - wh // 2
            x1 = cx + ww // 2
            y1 = cy + wh // 2
            draw.rectangle([(x0, y0), (x1, y1)], fill=(255, 255, 255))
        else:
            # Diagonal: whiten with rotated rectangle / slightly generous box
            x0 = cx - int(ww * 0.6)
            y0 = cy - int(wh * 0.7)
            x1 = cx + int(ww * 0.6)
            y1 = cy + int(wh * 0.7)
            draw.rectangle([(x0, y0), (x1, y1)], fill=(255, 255, 255))
            
        # 2. Render and paste the new text
        txt_patch = render_text_patch(val, font, angle=angle)
        pw, ph = txt_patch.size
        paste_x = cx - pw // 2
        paste_y = cy - ph // 2
        patched.paste(txt_patch, (paste_x, paste_y), txt_patch)
        
    return patched

def build_composite_deliverables(tier):
    """Builds and saves the full composite image and PDF for a given tier."""
    orig_im = Image.open(ORIG_FIG7).convert("RGB")
    W, H = orig_im.size
    
    target_top = 2660
    top_part = orig_im.crop((0, 0, W, target_top))
    
    # Patch top panels
    patched_top = patch_top_panels(top_part, tier)
    
    # Load corresponding bottom panels (g) and (h)
    p_g_path = os.path.join(POST_DIR, f"fig7_panel_g_{tier}.png")
    p_h_path = os.path.join(POST_DIR, f"fig7_panel_h_{tier}.png")
    
    im_g = Image.open(p_g_path)
    im_h = Image.open(p_h_path)
    
    target_height = H - target_top
    half_width = W // 2
    
    resized_g = im_g.resize((half_width, target_height), Image.Resampling.LANCZOS)
    resized_h = im_h.resize((W - half_width, target_height), Image.Resampling.LANCZOS)
    
    # Assemble full image
    full_im = Image.new("RGB", (W, H), (255, 255, 255))
    full_im.paste(patched_top, (0, 0))
    full_im.paste(resized_g, (0, target_top))
    full_im.paste(resized_h, (half_width, target_top))
    
    # Save targets
    targets = []
    if tier == "pbe_d3_u":
        targets.extend([
            os.path.join(POST_DIR, "Fig7_composite_pbe_d3_u"),
            os.path.join(POST_DIR, "Fig7_Ucr"),
            os.path.join(POST_DIR, "Fig7"),
            os.path.join(JUAN_DIR, "Fig7_composite_pbe_d3_u"),
            os.path.join(JUAN_DIR, "Fig7_Ucr"),
            os.path.join(JUAN_DIR, "Fig7"),
            os.path.join(ACS_FIG_DIR, "Fig7")
        ])
    elif tier == "u_all":
        targets.extend([
            os.path.join(POST_DIR, "Fig7_composite_u_all"),
            os.path.join(POST_DIR, "Fig7_Uall"),
            os.path.join(JUAN_DIR, "Fig7_composite_u_all"),
            os.path.join(JUAN_DIR, "Fig7_Uall"),
            os.path.join(ACS_FIG_DIR, "Fig7_Uall")
        ])
        
    for base_path in targets:
        png_path = f"{base_path}.png"
        pdf_path = f"{base_path}.pdf"
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        full_im.save(png_path, "PNG", dpi=(300, 300))
        full_im.save(pdf_path, "PDF", resolution=300.0)
        print(f"[OK] Generated: {png_path} and {pdf_path}")

def main():
    print("=== Updating Figure 7 Composites with Verified DFT Distances ===")
    print("Processing Tier: PBE+D3+U_Cr (U_Cr = 3.29 eV)...")
    build_composite_deliverables("pbe_d3_u")
    
    print("\nProcessing Tier: PBE+D3+U_all (U_all = 3.29 eV)...")
    build_composite_deliverables("u_all")
    print("\n[DONE] All deliverables generated and synchronized!")

if __name__ == "__main__":
    main()
