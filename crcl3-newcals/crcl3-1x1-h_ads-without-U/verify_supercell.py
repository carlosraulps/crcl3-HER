#!/usr/bin/env python3
"""
================================================================================
 VERIFICATION SCRIPT: H Adsorption VASP Inputs on CrCl3 1x1 Primitive Cell
================================================================================
"""

import os
import sys
import math
import re
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTCAR_1X1 = os.path.join(SCRIPT_DIR, "..", "crcl3-1x1", "quick_test_k551", "CONTCAR")
C_VACUUM = 20.0000

PASS = 0
FAIL = 0
WARN = 0


def check(condition, msg_pass, msg_fail, fatal=False):
    global PASS, FAIL
    if condition:
        PASS += 1
        print("    [PASS] {}".format(msg_pass))
    else:
        FAIL += 1
        print("    [FAIL] {}".format(msg_fail))
        if fatal:
            sys.exit(1)


def parse_poscar(filepath):
    with open(filepath, "r") as f:
        lines = [l.rstrip() for l in f.readlines()]
    scale = float(lines[1].split()[0])
    v1 = np.array([float(x) for x in lines[2].split()[:3]]) * scale
    v2 = np.array([float(x) for x in lines[3].split()[:3]]) * scale
    v3 = np.array([float(x) for x in lines[4].split()[:3]]) * scale
    lattice = np.array([v1, v2, v3])
    species = lines[5].split()
    counts = [int(x) for x in lines[6].split()]
    idx = 7
    if lines[idx].strip()[0].upper() == "S":
        idx += 1
    idx += 1
    coords = []
    for i in range(sum(counts)):
        parts = lines[idx + i].split()
        coords.append([float(parts[0]), float(parts[1]), float(parts[2])])
    return lattice, species, counts, np.array(coords)


def min_image_dist(c1, c2, lattice):
    diff = np.array(c1) - np.array(c2)
    diff -= np.round(diff)
    cart = diff @ lattice
    return np.linalg.norm(cart)


def verify_structure(poscar_path, contcar_1x1_path, has_h, site_name):
    print("\n  --- Verifying: {} ---".format(os.path.relpath(poscar_path, SCRIPT_DIR)))
    lat, species, counts, coords = parse_poscar(poscar_path)
    lat_ref, _, _, crd_ref = parse_poscar(contcar_1x1_path)

    a_calc = np.linalg.norm(lat[0])
    a_ref = np.linalg.norm(lat_ref[0])
    c_calc = np.linalg.norm(lat[2])

    check(abs(a_calc - a_ref) < 0.001,
          "a = {:.4f} A == 1x1 ref = {:.4f} A".format(a_calc, a_ref),
          "a = {:.4f} A != ref {:.4f} A".format(a_calc, a_ref))
    check(abs(c_calc - C_VACUUM) < 0.001,
          "c = {:.4f} A == {:.4f} A".format(c_calc, C_VACUUM),
          "c = {:.4f} A != {:.4f} A".format(c_calc, C_VACUUM))

    angle = np.degrees(np.arccos(np.dot(lat[0], lat[1]) / (np.linalg.norm(lat[0]) * np.linalg.norm(lat[1]))))
    check(abs(angle - 120.0) < 0.1, "Hexagonal angle = {:.2f} deg".format(angle), "Angle != 120 deg")

    expected_counts = [2, 6, 1] if has_h else [2, 6]
    check(counts == expected_counts, "Atom counts: {} == {}".format(counts, expected_counts), "Counts mismatch")

    # Cr-Cr distance
    d_crcr = min_image_dist(coords[0], coords[1], lat)
    check(abs(d_crcr - 3.4908) < 0.01,
          "Cr-Cr distance = {:.4f} A (expected 3.4908 A)".format(d_crcr),
          "Cr-Cr distance = {:.4f} A != 3.4908 A".format(d_crcr))

    # Cr-Cl bond length
    crcl_dists = [min_image_dist(coords[0], coords[i], lat) for i in range(2, 8)]
    avg_crcl = np.mean(crcl_dists)
    check(abs(avg_crcl - 2.3568) < 0.01,
          "Avg Cr-Cl bond = {:.4f} A (expected 2.3568 A)".format(avg_crcl),
          "Avg Cr-Cl bond = {:.4f} A != 2.3568 A".format(avg_crcl))

    if has_h:
        h_coord = coords[-1]
        check(h_coord[2] > 0.5, "H is above slab center (z_frac = {:.6f} > 0.5)".format(h_coord[2]), "H below slab")

        if site_name == "S1":
            target_cl = coords[7]  # Cl at (0.35930, 0.35930)
            d_xy = np.linalg.norm(((h_coord[:2] - target_cl[:2]) - np.round(h_coord[:2] - target_cl[:2])) @ lat[:2, :2])
            dh = (h_coord[2] - target_cl[2]) * C_VACUUM
            check(d_xy < 1e-4, "S1: H atop top-Cl in-plane (d_xy = {:.6f} A)".format(d_xy), "S1: H not aligned")
            check(abs(dh - 1.30) < 1e-3, "S1: H-Cl distance = {:.4f} A (target 1.30 A)".format(dh), "S1: dh != 1.30")
        elif site_name == "S2":
            d_xy = np.linalg.norm(((h_coord[:2] - [0.0, 0.0]) - np.round(h_coord[:2] - [0.0, 0.0])) @ lat[:2, :2])
            dh = (h_coord[2] - 0.5) * C_VACUUM
            check(d_xy < 1e-4, "S2: H at hollow (0,0) (d_xy = {:.6f} A)".format(d_xy), "S2: H not at hollow")
            check(abs(dh - 1.60) < 1e-3, "S2: H height above slab = {:.4f} A (target 1.60 A)".format(dh), "S2: dh != 1.60")
        elif site_name == "S3":
            target_cr = coords[1]  # Cr2 at (2/3, 1/3)
            d_xy = np.linalg.norm(((h_coord[:2] - target_cr[:2]) - np.round(h_coord[:2] - target_cr[:2])) @ lat[:2, :2])
            dh = (h_coord[2] - target_cr[2]) * C_VACUUM
            check(d_xy < 1e-4, "S3: H atop Cr2 in-plane (d_xy = {:.6f} A)".format(d_xy), "S3: H not aligned")
            check(abs(dh - 1.55) < 1e-3, "S3: H-Cr distance = {:.4f} A (target 1.55 A)".format(dh), "S3: dh != 1.55")


def verify_incar(incar_path, vdw_expected, has_h):
    with open(incar_path, "r") as f:
        content = f.read()

    isif_match = re.search(r"^ISIF\s*=\s*(\d+)", content, re.MULTILINE)
    check(isif_match and isif_match.group(1) == "2", "ISIF = 2", "ISIF != 2")

    ldau_match = re.search(r"LDAU\s*=\s*\.(\w+)\.", content)
    check(ldau_match and ldau_match.group(1).upper() == "FALSE", "LDAU = .FALSE.", "LDAU != .FALSE.")

    ediffg_match = re.search(r"EDIFFG\s*=\s*([\-\d.]+)", content)
    check(ediffg_match and abs(float(ediffg_match.group(1)) - (-0.025)) < 0.001, "EDIFFG = -0.025", "EDIFFG != -0.025")

    ivdw_match = re.search(r"IVDW\s*=\s*(\d+)", content)
    if vdw_expected:
        check(ivdw_match and ivdw_match.group(1) == "11", "IVDW = 11 (DFT-D3)", "IVDW != 11")
    else:
        check(ivdw_match is None, "No IVDW tag (Pure PBE)", "Unexpected IVDW")

    magmom_match = re.search(r"MAGMOM\s*=\s*(.+?)#", content)
    if magmom_match:
        total = 0
        for part in magmom_match.group(1).strip().split():
            if "*" in part:
                total += int(part.split("*")[0])
            else:
                total += 1
        expected = 9 if has_h else 8
        check(total == expected, "MAGMOM count = {} (matches {} atoms)".format(total, expected), "MAGMOM mismatch")

    uncommented = [l.strip() for l in content.split("\n") if l.strip() and not l.strip().startswith("#") and "=" in l and "#" not in l]
    check(len(uncommented) == 0, "All INCAR variables have comments", "Uncommented lines found")


def verify_potcar(potcar_path, has_h):
    with open(potcar_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    titels = re.findall(r"TITEL\s*=\s*PAW_PBE\s+(\S+)", content)
    expected = ["Cr", "Cl", "H"] if has_h else ["Cr", "Cl"]
    check(titels == expected, "POTCAR species order: {} = {}".format(titels, expected), "POTCAR mismatch")


def main():
    global PASS, FAIL, WARN
    print("\n" + "=" * 85)
    print("   VERIFICATION: H ADSORPTION VASP INPUTS ON CrCl3 1x1 CELL")
    print("=" * 85)

    variants = [("no_vdw", False), ("yes_vdw", True)]
    sites = ["clean", "S1", "S2", "S3"]

    for vdw_name, vdw_flag in variants:
        for site in sites:
            site_dir = os.path.join(SCRIPT_DIR, vdw_name, site)
            has_h = site != "clean"
            for fname in ["POSCAR", "INCAR", "POTCAR", "KPOINTS", "job.sh"]:
                check(os.path.exists(os.path.join(site_dir, fname)), "{}/{}/{} exists".format(vdw_name, site, fname), "Missing")
            verify_structure(os.path.join(site_dir, "POSCAR"), CONTCAR_1X1, has_h, site)
            verify_incar(os.path.join(site_dir, "INCAR"), vdw_flag, has_h)
            verify_potcar(os.path.join(site_dir, "POTCAR"), has_h)

    print("\n" + "=" * 85)
    print("  VERIFICATION SUMMARY (1x1)")
    print("  PASS: {}  |  FAIL: {}  |  WARN: {}".format(PASS, FAIL, WARN))
    print("=" * 85 + "\n")
    return FAIL

if __name__ == "__main__":
    sys.exit(main())
