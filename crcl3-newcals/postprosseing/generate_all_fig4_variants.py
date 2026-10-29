#!/usr/bin/env python3
"""
generate_all_fig4_variants.py
==============================
Generates publication-ready, zero-overlap vector SVG, PDF, and 300 DPI PNG figures
for all Figure 4 deliverables:
  1. Fig4.svg / Fig4.pdf / Fig4.png (Dual-tier master composite)
  2. Fig4_Ucr.svg / Fig4_Ucr.pdf / Fig4_Ucr.png (Dedicated +U_Cr single-tier)
  3. Fig4_Uall.svg / Fig4_Uall.pdf / Fig4_Uall.png (Dedicated +U_all single-tier)

Enforces:
  - Strict zero-collision policy (tested via bbox extraction)
  - Non-breaking spaces for mathematical operators to prevent glyph stacking
  - High-visibility semi-transparent white smart cards (0.96 opacity)
  - 300 DPI rasterization and vector PDF export via Inkscape
  - Direct synchronization across images-juan/, postprosseing/, and ACS_resubmission/
"""

import os
import re
import shutil
import subprocess

REPO_ROOT = "/home/cr/simulations/crcl3-HER"
FIG4_JUAN_DIR = os.path.join(REPO_ROOT, "crcl3-newcals", "postprosseing", "images-juan", "04_Fig4_CDD_and_Bader_Charge")
POST_DIR = os.path.join(REPO_ROOT, "crcl3-newcals", "postprosseing")
ACS_RESUB_DIR = os.path.join(REPO_ROOT, "ACS_version", "ACS_resubmission", "figure")
ACS_ORIG_DIR = os.path.join(REPO_ROOT, "ACS_version", "figure")

SVG_SRC = os.path.join(ACS_RESUB_DIR, "Fig4.svg")

with open(SVG_SRC, "r", encoding="utf-8") as f:
    svg_raw = f.read()

# Locate cut point before dynamic cards
idx = svg_raw.find("<g id=\"bader_card_co\">")
if idx == -1:
    idx = svg_raw.find("<!-- Smart Cards")
if idx == -1:
    raise ValueError("Could not find dynamic card insertion anchor in Fig4.svg")

base_clean = svg_raw[:idx]

# -------------------------------------------------------------------------
# 1. Fig4 Master (Dual-Tier)
# -------------------------------------------------------------------------
dual_tier_cards = """
    <!-- Smart Cards and Dual-Tier Bader Charge Transfer Labels -->
    <!-- Panel (d): Co -->
    <g id="bader_card_co">
      <rect x="110" y="337" width="112" height="37" rx="3" ry="3" fill="#ffffff" fill-opacity="0.96" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="166" y="351" font-family="Times New Roman, Times, serif" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#1a1a1a">ΔQ = +0.77 e <tspan font-size="9" fill="#555555">(+U<tspan font-size="7.5" dy="1.5">Cr</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
      <text x="166" y="367" font-family="Times New Roman, Times, serif" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#004499">ΔQ = +0.70 e <tspan font-size="9" fill="#0066cc">(+U<tspan font-size="7.5" dy="1.5">all</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
    </g>

    <!-- Panel (e): Fe -->
    <g id="bader_card_fe">
      <rect x="326" y="337" width="112" height="37" rx="3" ry="3" fill="#ffffff" fill-opacity="0.96" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="382" y="351" font-family="Times New Roman, Times, serif" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#1a1a1a">ΔQ = +0.94 e <tspan font-size="9" fill="#555555">(+U<tspan font-size="7.5" dy="1.5">Cr</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
      <text x="382" y="367" font-family="Times New Roman, Times, serif" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#004499">ΔQ = +0.88 e <tspan font-size="9" fill="#0066cc">(+U<tspan font-size="7.5" dy="1.5">all</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
    </g>

    <!-- Panel (f): Ni -->
    <g id="bader_card_ni">
      <rect x="533" y="337" width="112" height="37" rx="3" ry="3" fill="#ffffff" fill-opacity="0.96" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="589" y="351" font-family="Times New Roman, Times, serif" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#1a1a1a">ΔQ = +0.59 e <tspan font-size="9" fill="#555555">(+U<tspan font-size="7.5" dy="1.5">Cr</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
      <text x="589" y="367" font-family="Times New Roman, Times, serif" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#004499">ΔQ = +0.54 e <tspan font-size="9" fill="#0066cc">(+U<tspan font-size="7.5" dy="1.5">all</tspan><tspan font-size="9" dy="-1.5">)</tspan></tspan></text>
    </g>
</g></svg>
"""

# -------------------------------------------------------------------------
# 2. Fig4_Ucr (Dedicated +U_Cr Single-Tier)
# -------------------------------------------------------------------------
ucr_cards = """
    <!-- Non-overlapping Header Badge in Panel (c) Top-Right -->
    <g id="functional_badge_ucr">
      <rect x="572" y="6" width="144" height="22" rx="3" ry="3" fill="#ffffff" fill-opacity="0.95" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="644" y="21" font-family="Times New Roman, Times, serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#1a1a1a">+U<tspan font-size="8.5" dy="2">Cr</tspan><tspan font-size="11" dy="-2">&#160;= 3.29 eV</tspan></text>
    </g>

    <!-- Single-tier Bader Charge Cards (Panels d, e, f) -->
    <!-- Panel (d): Co -->
    <g id="bader_card_co">
      <rect x="110" y="335" width="112" height="24" rx="3" ry="3" fill="#ffffff" fill-opacity="0.96" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="166" y="351" font-family="Times New Roman, Times, serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#1a1a1a">ΔQ = +0.77 e</text>
    </g>

    <!-- Panel (e): Fe -->
    <g id="bader_card_fe">
      <rect x="326" y="335" width="112" height="24" rx="3" ry="3" fill="#ffffff" fill-opacity="0.96" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="382" y="351" font-family="Times New Roman, Times, serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#1a1a1a">ΔQ = +0.94 e</text>
    </g>

    <!-- Panel (f): Ni -->
    <g id="bader_card_ni">
      <rect x="533" y="335" width="112" height="24" rx="3" ry="3" fill="#ffffff" fill-opacity="0.96" stroke="#b0b0b0" stroke-width="0.8" />
      <text x="589" y="351" font-family="Times New Roman, Times, serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#1a1a1a">ΔQ = +0.59 e</text>
    </g>
</g></svg>
"""

# -------------------------------------------------------------------------
# 3. Fig4_Uall (Dedicated +U_all Single-Tier)
# -------------------------------------------------------------------------
uall_cards = """
    <!-- Non-overlapping Header Badge in Panel (c) Top-Right -->
    <g id="functional_badge_uall">
      <rect x="572" y="6" width="144" height="22" rx="3" ry="3" fill="#ffffff" fill-opacity="0.95" stroke="#0066cc" stroke-width="0.8" />
      <text x="644" y="21" font-family="Times New Roman, Times, serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#004499">+U<tspan font-size="8.5" dy="2">all</tspan><tspan font-size="11" dy="-2">&#160;= 3.29 eV</tspan></text>
    </g>

    <!-- Single-tier Bader Charge Cards (Panels d, e, f) -->
    <!-- Panel (d): Co -->
    <g id="bader_card_co">
      <rect x="110" y="335" width="112" height="24" rx="3" ry="3" fill="#ffffff" fill-opacity="0.96" stroke="#0066cc" stroke-width="0.8" />
      <text x="166" y="351" font-family="Times New Roman, Times, serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#004499">ΔQ = +0.70 e</text>
    </g>

    <!-- Panel (e): Fe -->
    <g id="bader_card_fe">
      <rect x="326" y="335" width="112" height="24" rx="3" ry="3" fill="#ffffff" fill-opacity="0.96" stroke="#0066cc" stroke-width="0.8" />
      <text x="382" y="351" font-family="Times New Roman, Times, serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#004499">ΔQ = +0.88 e</text>
    </g>

    <!-- Panel (f): Ni -->
    <g id="bader_card_ni">
      <rect x="533" y="335" width="112" height="24" rx="3" ry="3" fill="#ffffff" fill-opacity="0.96" stroke="#0066cc" stroke-width="0.8" />
      <text x="589" y="351" font-family="Times New Roman, Times, serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#004499">ΔQ = +0.54 e</text>
    </g>
</g></svg>
"""

variants = [
    ("Fig4", dual_tier_cards),
    ("Fig4_Ucr", ucr_cards),
    ("Fig4_Uall", uall_cards),
]

temp_dir = "/tmp/fig4_build"
os.makedirs(temp_dir, exist_ok=True)

for name, cards_xml in variants:
    print(f"[*] Building {name}...")
    full_svg = base_clean + cards_xml
    svg_path = os.path.join(temp_dir, f"{name}.svg")
    pdf_path = os.path.join(temp_dir, f"{name}.pdf")
    png_path = os.path.join(temp_dir, f"{name}.png")

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(full_svg)

    # Export to vector PDF
    cmd_pdf = f"inkscape --export-filename={pdf_path} {svg_path}"
    subprocess.run(cmd_pdf, shell=True, check=True)

    # Export to 300 DPI PNG
    cmd_png = f"inkscape --export-filename={png_path} --export-dpi=300 {svg_path}"
    subprocess.run(cmd_png, shell=True, check=True)

    # Collision audit with pdftotext
    audit_cmd = f"pdftotext -bbox-layout {pdf_path} -"
    res = subprocess.run(audit_cmd, shell=True, capture_output=True, text=True, check=True)
    words = []
    for line in res.stdout.splitlines():
        if "<word" in line:
            # parse xMin, xMax, yMin, yMax, word
            m = re.search(r'xMin="([^"]+)".*yMin="([^"]+)".*xMax="([^"]+)".*yMax="([^"]+)">(.*)</word>', line)
            if m:
                words.append({
                    "xMin": float(m.group(1)),
                    "yMin": float(m.group(2)),
                    "xMax": float(m.group(3)),
                    "yMax": float(m.group(4)),
                    "text": m.group(5)
                })

    # Check for horizontal collisions among adjacent words in the same line
    collisions = 0
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            w1 = words[i]
            w2 = words[j]
            # Same horizontal line (vertical overlap)
            v_overlap = max(0, min(w1["yMax"], w2["yMax"]) - max(w1["yMin"], w2["yMin"]))
            if v_overlap > 3: # on the same line
                # Horizontal collision
                h_overlap = min(w1["xMax"], w2["xMax"]) - max(w1["xMin"], w2["xMin"])
                if h_overlap > 0.5: # actual collision
                    print(f"  [!] Collision detected in {name}: '{w1['text']}' and '{w2['text']}' (overlap = {h_overlap:.2f} pts)")
                    collisions += 1

    if collisions == 0:
        print(f"  [✓] {name} passed collision audit with 0 overlaps across {len(words)} text elements!")
    else:
        raise ValueError(f"Found {collisions} collisions in {name}!")

    # Synchronize deliverables to all target directories
    # 1. images-juan/04_Fig4_CDD_and_Bader_Charge/
    shutil.copy2(svg_path, os.path.join(FIG4_JUAN_DIR, f"{name}.svg"))
    shutil.copy2(pdf_path, os.path.join(FIG4_JUAN_DIR, f"{name}.pdf"))
    shutil.copy2(png_path, os.path.join(FIG4_JUAN_DIR, f"{name}.png"))

    # 2. crcl3-newcals/postprosseing/
    shutil.copy2(svg_path, os.path.join(POST_DIR, f"{name}.svg"))
    shutil.copy2(pdf_path, os.path.join(POST_DIR, f"{name}.pdf"))
    shutil.copy2(png_path, os.path.join(POST_DIR, f"{name}.png"))

    # 3. For master Fig4, sync to ACS_resubmission and ACS_version
    if name == "Fig4":
        shutil.copy2(svg_path, os.path.join(ACS_RESUB_DIR, "Fig4.svg"))
        shutil.copy2(pdf_path, os.path.join(ACS_RESUB_DIR, "Fig4.pdf"))
        shutil.copy2(png_path, os.path.join(ACS_RESUB_DIR, "Fig4.png"))
        if os.path.exists(ACS_ORIG_DIR):
            shutil.copy2(pdf_path, os.path.join(ACS_ORIG_DIR, "Fig4.pdf"))
            shutil.copy2(png_path, os.path.join(ACS_ORIG_DIR, "Fig4.png"))

print("\n[✓] All Figure 4 deliverables generated and synchronized successfully!")
