#!/usr/bin/env python3
"""
update_fig4_dual_tier.py
========================
Updates Figure 4 vector SVG and high-resolution raster/PDF outputs with dual-tier
Bader charge variation annotations (+U_Cr and +U_all):
  - Panel (d) Co: ΔQ = +0.77 e (+U_Cr) / +0.70 e (+U_all)
  - Panel (e) Fe: ΔQ = +0.94 e (+U_Cr) / +0.88 e (+U_all)
  - Panel (f) Ni: ΔQ = +0.59 e (+U_Cr) / +0.54 e (+U_all)

Follows publication plotting guidelines:
  - Times New Roman typography
  - High-visibility semi-transparent white smart cards (0.95 opacity) with subtle borders
  - Exact geometric centering over transition-metal sites
"""

import os
import subprocess

REPO_ROOT = "/home/cr/simulations/crcl3-HER"
SVG_SRC = os.path.join(REPO_ROOT, "ACS_version", "ACS_resubmission", "figure", "Fig4.svg")
PNG_OUT = os.path.join(REPO_ROOT, "ACS_version", "ACS_resubmission", "figure", "Fig4.png")
PDF_OUT = os.path.join(REPO_ROOT, "ACS_version", "ACS_resubmission", "figure", "Fig4.pdf")

ORIG_PNG = os.path.join(REPO_ROOT, "ACS_version", "figure", "Fig4.png")
ORIG_PDF = os.path.join(REPO_ROOT, "ACS_version", "figure", "Fig4.pdf")

with open(SVG_SRC, "r", encoding="utf-8") as f:
    svg = f.read()

# Locate where the old raster image cards start (id='image1-9')
idx = svg.find('id="image1-9"')
if idx == -1:
    raise ValueError("Could not find image1-9 in Fig4.svg")

tag_start = svg.rfind("<image", 0, idx)
tag_end = svg.rfind("</g></svg>")

# Authentic vector smart cards + crisp dual-tier typography
replacement = """
    <!-- Smart Cards and Dual-Tier Bader Charge Transfer Labels -->
    <!-- Panel (d): Co -->
    <g id="bader_card_co">
      <rect x="110" y="338" width="112" height="36" rx="3" ry="3" fill="#ffffff" fill-opacity="0.95" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="166" y="352" font-family="Times New Roman" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#1a1a1a">ΔQ = +0.77 e <tspan font-size="9" fill="#555555">(+U<tspan font-size="7.5" dy="1.5">Cr</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
      <text x="166" y="367" font-family="Times New Roman" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#004499">ΔQ = +0.70 e <tspan font-size="9" fill="#0066cc">(+U<tspan font-size="7.5" dy="1.5">all</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
    </g>

    <!-- Panel (e): Fe -->
    <g id="bader_card_fe">
      <rect x="326" y="338" width="112" height="36" rx="3" ry="3" fill="#ffffff" fill-opacity="0.95" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="382" y="352" font-family="Times New Roman" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#1a1a1a">ΔQ = +0.94 e <tspan font-size="9" fill="#555555">(+U<tspan font-size="7.5" dy="1.5">Cr</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
      <text x="382" y="367" font-family="Times New Roman" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#004499">ΔQ = +0.88 e <tspan font-size="9" fill="#0066cc">(+U<tspan font-size="7.5" dy="1.5">all</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
    </g>

    <!-- Panel (f): Ni -->
    <g id="bader_card_ni">
      <rect x="533" y="338" width="112" height="36" rx="3" ry="3" fill="#ffffff" fill-opacity="0.95" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="589" y="352" font-family="Times New Roman" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#1a1a1a">ΔQ = +0.59 e <tspan font-size="9" fill="#555555">(+U<tspan font-size="7.5" dy="1.5">Cr</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
      <text x="589" y="367" font-family="Times New Roman" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#004499">ΔQ = +0.54 e <tspan font-size="9" fill="#0066cc">(+U<tspan font-size="7.5" dy="1.5">all</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
    </g>
"""

new_svg = svg[:tag_start] + replacement + svg[tag_end:]

# Write updated Fig4.svg
with open(SVG_SRC, "w", encoding="utf-8") as f:
    f.write(new_svg)

print(f"[✓] Successfully updated {SVG_SRC}")

# Export to PNG and PDF at 300 DPI using Inkscape
for png_path in [PNG_OUT, ORIG_PNG]:
    if os.path.exists(os.path.dirname(png_path)):
        cmd = f"inkscape --export-filename={png_path} --export-dpi=300 {SVG_SRC}"
        subprocess.run(cmd, shell=True, check=True)
        print(f"[✓] Rendered PNG: {png_path}")

for pdf_path in [PDF_OUT, ORIG_PDF]:
    if os.path.exists(os.path.dirname(pdf_path)):
        cmd = f"inkscape --export-filename={pdf_path} {SVG_SRC}"
        subprocess.run(cmd, shell=True, check=True)
        print(f"[✓] Rendered PDF: {pdf_path}")

print("[✓] All Figure 4 deliverables compiled successfully!")
