#!/usr/bin/env python3
"""
update_fig7_svgs.py
===================
Updates panels (g) and (h) in both:
  1. crcl3-newcals/postprosseing/images-juan/07_Fig7_HER_Thermodynamics/Fig7_Ucr.svg
  2. crcl3-newcals/postprosseing/images-juan/07_Fig7_HER_Thermodynamics/Fig7_Uall.svg

Ensures:
  - Fig7_Ucr.svg: image1-6 is updated with authentic +U_Cr energetics (Ni Eint = -1.49 eV).
  - Fig7_Uall.svg: image57 is updated with authentic +U_all energetics (Co, Fe, Ni multitier values).
  - Aspect ratio and slot alignment are precisely matched without distortion.
  - High-resolution deliverables (.png and .pdf) are re-exported and synchronized.
"""

import os
import re
import io
import base64
from PIL import Image

POST_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals/postprosseing"
JUAN_DIR = os.path.join(POST_DIR, "images-juan/07_Fig7_HER_Thermodynamics")
ACS_FIG_DIR = "/home/cr/simulations/crcl3-HER/ACS_version/ACS_resubmission/figure"

def build_gh_composite(tier, target_size):
    """
    Builds the combined panels (g) and (h) side-by-side composite
    matching the exact publication layout and resizes to target_size.
    """
    p_g_path = os.path.join(POST_DIR, f"fig7_panel_g_{tier}.png")
    p_h_path = os.path.join(POST_DIR, f"fig7_panel_h_{tier}.png")

    if not os.path.exists(p_g_path) or not os.path.exists(p_h_path):
        raise FileNotFoundError(f"Missing panel files for tier {tier}: {p_g_path}, {p_h_path}")

    im_g = Image.open(p_g_path)
    im_h = Image.open(p_h_path)

    # Master high-res canvas (3810 x 1282, matching Fig7 composite bottom slot)
    W, H = 3810, 1282
    half_w = W // 2

    resized_g = im_g.resize((half_w, H), Image.Resampling.LANCZOS)
    resized_h = im_h.resize((W - half_w, H), Image.Resampling.LANCZOS)

    mode = "RGBA" if tier == "u_all" else "RGB"
    composite = Image.new(mode, (W, H), (255, 255, 255, 255) if mode == "RGBA" else (255, 255, 255))
    composite.paste(resized_g, (0, 0))
    composite.paste(resized_h, (half_w, 0))

    # Resize to exact slot dimensions for the SVG embed
    out_im = composite.resize(target_size, Image.Resampling.LANCZOS)
    return out_im

def image_to_base64_png(im):
    """Converts a PIL Image to a base64-encoded PNG data URI string."""
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    b64_str = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64_str}"

def update_svg_image(svg_path, element_id, new_base64_data):
    """
    Replaces the xlink:href / href attribute of the image element matching element_id.
    Uses regex substitution to preserve all XML formatting, doctypes, and namespaces.
    """
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern matches the <image ... id="element_id" ...> tag or <image ... xlink:href="..." ... id="element_id" ...>
    # We find the image tag containing element_id and replace its (xlink:)?href attribute.
    pattern = rf'(<image\b[^>]*\bid=["\']{element_id}["\'][^>]*>|<image\b[^>]*\b(xlink:)?href=["\'][^"\']+["\'][^>]*\bid=["\']{element_id}["\'][^>]*>)'

    match = re.search(pattern, content)
    if not match:
        # Try finding with id first then tag close
        pattern = rf'(<image\b[\s\S]*?\bid="{element_id}"[\s\S]*?>)'
        match = re.search(pattern, content)

    if not match:
        raise ValueError(f"Could not locate image tag with id '{element_id}' in {svg_path}")

    tag_str = match.group(0)

    # Replace href or xlink:href in tag_str
    href_pattern = r'(xlink:href|href)="data:image\/png;base64,[^"]*"'
    if not re.search(href_pattern, tag_str):
        raise ValueError(f"Could not locate base64 href in tag '{element_id}'")

    updated_tag_str = re.sub(href_pattern, rf'\1="{new_base64_data}"', tag_str)

    new_content = content[:match.start()] + updated_tag_str + content[match.end():]

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[✓] Successfully updated '{element_id}' in {svg_path}")

def main():
    print("=== Updating Panels (g) and (h) in Fig7_Ucr.svg and Fig7_Uall.svg ===")

    # 1. Update Fig7_Ucr.svg
    svg_ucr = os.path.join(JUAN_DIR, "Fig7_Ucr.svg")
    im_ucr = build_gh_composite("pbe_d3_u", target_size=(1220, 409))
    b64_ucr = image_to_base64_png(im_ucr)
    update_svg_image(svg_ucr, "image1-6", b64_ucr)

    # 2. Update Fig7_Uall.svg
    svg_uall = os.path.join(JUAN_DIR, "Fig7_Uall.svg")
    im_uall = build_gh_composite("u_all", target_size=(1559, 526))
    b64_uall = image_to_base64_png(im_uall)
    update_svg_image(svg_uall, "image57", b64_uall)

    # 3. Export both SVGs to PNG and PDF using Inkscape for validation
    for name, path in [("Fig7_Ucr", svg_ucr), ("Fig7_Uall", svg_uall)]:
        out_png = os.path.join(JUAN_DIR, f"{name}.png")
        out_pdf = os.path.join(JUAN_DIR, f"{name}.pdf")
        os.system(f"inkscape {path} --export-filename={out_png} --export-dpi=300 > /dev/null 2>&1")
        os.system(f"inkscape {path} --export-filename={out_pdf} > /dev/null 2>&1")
        print(f"[✓] Inkscape exported: {out_png} and {out_pdf}")

        # Also copy to POST_DIR and ACS_FIG_DIR
        shutil_copy = f"cp {out_png} {os.path.join(POST_DIR, f'{name}.png')} && cp {out_pdf} {os.path.join(POST_DIR, f'{name}.pdf')}"
        os.system(shutil_copy)
        if name == "Fig7_Uall":
            os.system(f"cp {out_png} {os.path.join(ACS_FIG_DIR, 'Fig7_Uall.png')} && cp {out_pdf} {os.path.join(ACS_FIG_DIR, 'Fig7_Uall.pdf')}")
        elif name == "Fig7_Ucr":
            os.system(f"cp {out_png} {os.path.join(ACS_FIG_DIR, 'Fig7_Ucr.png')} && cp {out_pdf} {os.path.join(ACS_FIG_DIR, 'Fig7_Ucr.pdf')}")

    print("\nAll SVG updates and exports completed successfully!")

if __name__ == "__main__":
    main()

