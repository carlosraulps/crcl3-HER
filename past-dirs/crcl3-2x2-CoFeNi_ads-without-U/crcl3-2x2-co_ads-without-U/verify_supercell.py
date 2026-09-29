#!/usr/bin/env python3
"""
VERIFICATION SCRIPT: Co Adsorption VASP Inputs on CrCl3 2x2 Supercell
"""
import os
import sys
import math
import re
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = "/home/cr/Downloads/crcl3-newcals"
CONTCAR_1X1 = os.path.join(PARENT_DIR, "crcl3-1x1", "quick_test_k551", "CONTCAR")
C_VACUUM = 20.0000
TM_SYMBOL = "Co"
DIST_S1 = 2.25
DIST_S2 = 1.9
DIST_S3 = 2.45

PASS = 0
FAIL = 0

def check(condition, msg_pass, msg_fail):
    global PASS, FAIL
    if condition:
        PASS += 1
        print("    [PASS] {}".format(msg_pass))
    else:
        FAIL += 1
        print("    [FAIL] {}".format(msg_fail))

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

def verify_structure(poscar_path, contcar_1x1_path, has_tm, site_name):
    print("\n  --- Verifying Structure: {} ---".format(os.path.relpath(poscar_path, SCRIPT_DIR)))
    lat_2x2, species, counts, coords = parse_poscar(poscar_path)
    lat_1x1, sp_1x1, cnt_1x1, crd_1x1 = parse_poscar(contcar_1x1_path)

    a_1x1 = np.linalg.norm(lat_1x1[0])
    a_2x2 = np.linalg.norm(lat_2x2[0])
    c_2x2 = np.linalg.norm(lat_2x2[2])

    expected_a = 2.0 * a_1x1
    check(abs(a_2x2 - expected_a) < 0.001,
          "a_2x2 = {:.4f} A == 2 * a_1x1 = {:.4f} A".format(a_2x2, expected_a),
          "a_2x2 = {:.4f} A != 2 * a_1x1 = {:.4f} A".format(a_2x2, expected_a))

    check(abs(c_2x2 - C_VACUUM) < 0.001,
          "c = {:.4f} A == {:.4f} A (target vacuum)".format(c_2x2, C_VACUUM),
          "c = {:.4f} A != {:.4f} A".format(c_2x2, C_VACUUM))

    angle = np.degrees(np.arccos(np.dot(lat_2x2[0], lat_2x2[1]) /
                                 (np.linalg.norm(lat_2x2[0]) * np.linalg.norm(lat_2x2[1]))))
    check(abs(angle - 120.0) < 0.1,
          "Hexagonal angle = {:.2f} deg".format(angle),
          "Hexagonal angle = {:.2f} deg (expected 120)".format(angle))

    if has_tm:
        check(counts == [8, 24, 1],
              "Atom counts: {} = [8, 24, 1] (Cr, Cl, {})".format(counts, TM_SYMBOL),
              "Atom counts: {} != [8, 24, 1]".format(counts))
        check(species == ["Cr", "Cl", TM_SYMBOL],
              "Species order: {} = ['Cr', 'Cl', '{}']".format(species, TM_SYMBOL),
              "Species order: {} != ['Cr', 'Cl', '{}']".format(species, TM_SYMBOL))
    else:
        check(counts == [8, 24],
              "Atom counts: {} = [8, 24] (Cr, Cl)".format(counts),
              "Atom counts: {} != [8, 24]".format(counts))

    cr_coords = coords[:8]
    cr_dists = []
    for i in range(8):
        for j in range(i + 1, 8):
            d = min_image_dist(cr_coords[i], cr_coords[j], lat_2x2)
            cr_dists.append(d)

    cr_1x1 = crd_1x1[:2]
    d_crcr_1x1 = min_image_dist(cr_1x1[0], cr_1x1[1], lat_1x1)
    min_crcr = min(cr_dists)
    check(abs(min_crcr - d_crcr_1x1) < 0.05,
          "Min Cr-Cr dist = {:.4f} A (1x1 ref = {:.4f} A)".format(min_crcr, d_crcr_1x1),
          "Min Cr-Cr dist = {:.4f} A != 1x1 ref {:.4f} A".format(min_crcr, d_crcr_1x1))

    if has_tm:
        tm_coord = coords[-1]
        check(tm_coord[2] > 0.5,
              "{} is above slab center (z_frac = {:.6f} > 0.5)".format(TM_SYMBOL, tm_coord[2]),
              "{} is below slab center (z_frac = {:.6f})".format(TM_SYMBOL, tm_coord[2]))

        if site_name == "S1":
            cl11 = coords[18]
            d_xy = np.linalg.norm(((tm_coord[:2] - cl11[:2]) - np.round(tm_coord[:2] - cl11[:2])) @ lat_2x2[:2, :2])
            d_tm_cl11 = (tm_coord[2] - cl11[2]) * c_2x2
            check(d_xy < 1e-4,
                  "S1: {} atop Cl11 in-plane (d_xy = {:.6f} A)".format(TM_SYMBOL, d_xy),
                  "S1: {} not atop Cl11 in-plane (d_xy = {:.6f} A)".format(TM_SYMBOL, d_xy))
            check(abs(d_tm_cl11 - DIST_S1) < 1e-3,
                  "S1: {}-Cl11 dist = {:.4f} A (target {:.2f} A)".format(TM_SYMBOL, d_tm_cl11, DIST_S1),
                  "S1: {}-Cl11 dist = {:.4f} A != {:.2f} A".format(TM_SYMBOL, d_tm_cl11, DIST_S1))

        elif site_name == "S2":
            d_xy = np.linalg.norm(((tm_coord[:2] - [0.5, 0.5]) - np.round(tm_coord[:2] - [0.5, 0.5])) @ lat_2x2[:2, :2])
            dz_slab = (tm_coord[2] - 0.5) * c_2x2
            check(d_xy < 1e-4,
                  "S2: {} at hollow site (0.5, 0.5) in-plane (d_xy = {:.6f} A)".format(TM_SYMBOL, d_xy),
                  "S2: {} not at hollow center (d_xy = {:.6f} A)".format(TM_SYMBOL, d_xy))
            check(abs(dz_slab - DIST_S2) < 1e-3,
                  "S2: {} height above slab center = {:.4f} A (target {:.2f} A)".format(TM_SYMBOL, dz_slab, DIST_S2),
                  "S2: {} height above slab center = {:.4f} A != {:.2f} A".format(TM_SYMBOL, dz_slab, DIST_S2))

        elif site_name == "S3":
            cr3 = coords[2]
            d_xy = np.linalg.norm(((tm_coord[:2] - cr3[:2]) - np.round(tm_coord[:2] - cr3[:2])) @ lat_2x2[:2, :2])
            d_tm_cr3 = (tm_coord[2] - cr3[2]) * c_2x2
            check(d_xy < 1e-4,
                  "S3: {} atop Cr3 in-plane (d_xy = {:.6f} A)".format(TM_SYMBOL, d_xy),
                  "S3: {} not atop Cr3 in-plane (d_xy = {:.6f} A)".format(TM_SYMBOL, d_xy))
            check(abs(d_tm_cr3 - DIST_S3) < 1e-3,
                  "S3: {}-Cr3 dist = {:.4f} A (target {:.2f} A)".format(TM_SYMBOL, d_tm_cr3, DIST_S3),
                  "S3: {}-Cr3 dist = {:.4f} A != {:.2f} A".format(TM_SYMBOL, d_tm_cr3, DIST_S3))

def verify_incar(incar_path, vdw_expected, has_tm):
    print("\n  --- Verifying INCAR: {} ---".format(os.path.relpath(incar_path, SCRIPT_DIR)))
    with open(incar_path, "r") as f:
        content = f.read()

    isif_match = re.search(r"^ISIF\s*=\s*(\d+)", content, re.MULTILINE)
    check(isif_match and isif_match.group(1) == "2",
          "ISIF = 2 (relax ions only, fixed cell)", "ISIF tag error")

    ldau_match = re.search(r"LDAU\s*=\s*\.(\w+)\.", content)
    check(ldau_match and ldau_match.group(1).upper() == "FALSE",
          "LDAU = .FALSE. (no Hubbard U)", "LDAU tag error")

    ediffg_match = re.search(r"EDIFFG\s*=\s*([\-\d.]+)", content)
    check(ediffg_match and abs(float(ediffg_match.group(1)) - (-0.025)) < 0.001,
          "EDIFFG = -0.025 eV/A (paper standard)", "EDIFFG tag error")

    ivdw_match = re.search(r"IVDW\s*=\s*(\d+)", content)
    if vdw_expected:
        check(ivdw_match and ivdw_match.group(1) == "12",
              "IVDW = 12 (DFT-D3 Zero Damping per specification)",
              "IVDW = {} (expected 12)".format(ivdw_match.group(1) if ivdw_match else "missing"))
    else:
        check(ivdw_match is None,
              "No IVDW tag (pure GGA-PBE)", "IVDW found in no_vdw calculation")

    magmom_match = re.search(r"MAGMOM\s*=\s*(.+?)#", content)
    if magmom_match:
        magmom_str = magmom_match.group(1).strip()
        total = 0
        for part in magmom_str.split():
            if "*" in part:
                n, val = part.split("*")
                total += int(n)
            else:
                total += 1
        expected_atoms = 33 if has_tm else 32
        check(total == expected_atoms,
              "MAGMOM count = {} (matches {} atoms)".format(total, expected_atoms),
              "MAGMOM count = {} (expected {})".format(total, expected_atoms))

    ldipol_match = re.search(r"LDIPOL\s*=\s*\.(\w+)\.", content)
    check(ldipol_match and ldipol_match.group(1).upper() == "TRUE",
          "LDIPOL = .TRUE. (dipole correction active)", "LDIPOL tag error")

def verify_potcar(potcar_path, has_tm):
    print("\n  --- Verifying POTCAR: {} ---".format(os.path.relpath(potcar_path, SCRIPT_DIR)))
    with open(potcar_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    titels = re.findall(r"TITEL\s*=\s*PAW_PBE\s+(\S+)", content)
    expected = ["Cr", "Cl", TM_SYMBOL] if has_tm else ["Cr", "Cl"]
    check(titels == expected,
          "POTCAR species order: {} = {}".format(titels, expected),
          "POTCAR species order: {} != {}".format(titels, expected))

def run_all_checks():
    print("=" * 85)
    print("   VERIFYING {} ADSORPTION INPUT SUITE".format(TM_SYMBOL))
    print("=" * 85)

    variants = [("no_vdw", False), ("yes_vdw", True)]
    sites = ["clean", "S1", "S2", "S3"]

    for vdw_dir, vdw_flag in variants:
        for s in sites:
            has_tm = (s != "clean")
            calc_dir = os.path.join(SCRIPT_DIR, vdw_dir, s)
            verify_structure(os.path.join(calc_dir, "POSCAR"), CONTCAR_1X1, has_tm, s)
            verify_incar(os.path.join(calc_dir, "INCAR"), vdw_flag, has_tm)
            verify_potcar(os.path.join(calc_dir, "POTCAR"), has_tm)

            with open(os.path.join(calc_dir, "KPOINTS"), "r") as f:
                kp = f.read()
            check("5  5  1" in kp, "KPOINTS is 5x5x1 Gamma-centered in {}".format(s), "KPOINTS error")

            job_sh = os.path.join(calc_dir, "job.sh")
            check(os.path.exists(job_sh) and os.access(job_sh, os.X_OK),
                  "job.sh exists and is executable in {}".format(s), "job.sh error")

    print("\n" + "=" * 85)
    print("   VERIFICATION SUMMARY: {} PASSED, {} FAILED".format(PASS, FAIL))
    print("=" * 85)
    if FAIL > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all_checks()
