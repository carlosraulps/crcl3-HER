#!/usr/bin/env python3
"""
================================================================================
 VERIFICATION SCRIPT: H Adsorption VASP Inputs on CrCl3 2x2 Supercell
================================================================================
 Validates that the generated 2x2 supercell inputs are correctly constructed
 from the relaxed 1x1 CONTCAR, including:
   1. Lattice parameter consistency (2x2 = exactly 2 * 1x1)
   2. Vacuum thickness c = 20.0 A
   3. Atomic coordinate mapping (1x1 -> 2x2)
   4. Interatomic distance preservation
   5. Site-specific verification:
      - S1: H strictly atop Atom 19 (Cl11) at (0.50000, 0.32035) with d=1.30 A
      - S2: H strictly at hollow center (0.50000, 0.50000) with dz=1.60 A
      - S3: H strictly atop Atom 3 (Cr3) at (0.66667, 0.33333) with d=1.55 A
   6. POTCAR species order matches POSCAR (Cr, Cl, [H])
   7. MAGMOM count matches total atom count (32 or 33)
   8. INCAR parameter consistency (ISIF=2, U=0, correct vdW, comments on all vars)
   9. Cross-validation against existing crcl3-2x2/H_S3/U_0 structure
================================================================================
"""

import os
import sys
import math
import re
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTCAR_1X1 = os.path.join(SCRIPT_DIR, "..", "crcl3-1x1", "quick_test_k551", "CONTCAR")
EXISTING_H_S3 = os.path.join(SCRIPT_DIR, "..", "past-calculations", "crcl3-2x2", "H_S3", "U_0", "POSCAR")
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


def warn(msg):
    global WARN
    WARN += 1
    print("    [WARN] {}".format(msg))


def parse_poscar(filepath):
    """Parse POSCAR/CONTCAR and return lattice, species, counts, coords."""
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
    """Minimum image distance between two fractional coordinates."""
    diff = np.array(c1) - np.array(c2)
    diff -= np.round(diff)
    cart = diff @ lattice
    return np.linalg.norm(cart)


def verify_structure(poscar_path, contcar_1x1_path, has_h, site_name):
    """Verify a single POSCAR against the 1x1 reference."""
    print("\n  --- Verifying: {} ---".format(os.path.relpath(poscar_path, SCRIPT_DIR)))

    lat_2x2, species, counts, coords = parse_poscar(poscar_path)
    lat_1x1, sp_1x1, cnt_1x1, crd_1x1 = parse_poscar(contcar_1x1_path)

    a_1x1 = np.linalg.norm(lat_1x1[0])
    a_2x2 = np.linalg.norm(lat_2x2[0])
    c_2x2 = np.linalg.norm(lat_2x2[2])

    # 1. Lattice parameter
    expected_a = 2.0 * a_1x1
    check(abs(a_2x2 - expected_a) < 0.001,
          "a_2x2 = {:.4f} A == 2 * a_1x1 = {:.4f} A".format(a_2x2, expected_a),
          "a_2x2 = {:.4f} A != 2 * a_1x1 = {:.4f} A (diff = {:.6f})".format(
              a_2x2, expected_a, a_2x2 - expected_a))

    # 2. Vacuum
    check(abs(c_2x2 - C_VACUUM) < 0.001,
          "c = {:.4f} A == {:.4f} A (target vacuum)".format(c_2x2, C_VACUUM),
          "c = {:.4f} A != {:.4f} A".format(c_2x2, C_VACUUM))

    # 3. Hexagonal angle
    angle = np.degrees(np.arccos(np.dot(lat_2x2[0], lat_2x2[1]) /
                                 (np.linalg.norm(lat_2x2[0]) * np.linalg.norm(lat_2x2[1]))))
    check(abs(angle - 120.0) < 0.1,
          "Hexagonal angle = {:.2f} deg".format(angle),
          "Hexagonal angle = {:.2f} deg (expected 120)".format(angle))

    # 4. Atom counts
    if has_h:
        check(counts == [8, 24, 1],
              "Atom counts: {} = [8, 24, 1] (Cr, Cl, H)".format(counts),
              "Atom counts: {} != [8, 24, 1]".format(counts))
        check(species == ["Cr", "Cl", "H"],
              "Species order: {} = ['Cr', 'Cl', 'H']".format(species),
              "Species order: {} != ['Cr', 'Cl', 'H']".format(species))
    else:
        check(counts == [8, 24],
              "Atom counts: {} = [8, 24] (Cr, Cl)".format(counts),
              "Atom counts: {} != [8, 24]".format(counts))

    # 5. Cr-Cr distances (should match 1x1 nearest-neighbor)
    cr_coords = coords[:8]
    cr_dists = []
    for i in range(8):
        for j in range(i + 1, 8):
            d = min_image_dist(cr_coords[i], cr_coords[j], lat_2x2)
            cr_dists.append(d)

    # In 1x1, the Cr-Cr nearest neighbor distance
    cr_1x1 = crd_1x1[:2]
    d_crcr_1x1 = min_image_dist(cr_1x1[0], cr_1x1[1], lat_1x1)
    min_crcr = min(cr_dists)
    check(abs(min_crcr - d_crcr_1x1) < 0.05,
          "Min Cr-Cr dist = {:.4f} A (1x1 ref = {:.4f} A)".format(min_crcr, d_crcr_1x1),
          "Min Cr-Cr dist = {:.4f} A != 1x1 ref {:.4f} A".format(min_crcr, d_crcr_1x1))

    # 6. Cr-Cl distances
    cl_coords = coords[8:32]
    crcl_dists = []
    for i in range(8):
        for j in range(24):
            d = min_image_dist(cr_coords[i], cl_coords[j], lat_2x2)
            if d < 3.0:  # only nearest neighbors
                crcl_dists.append(d)

    # 1x1 Cr-Cl reference
    cl_1x1 = crd_1x1[2:8]
    crcl_ref = []
    for i in range(2):
        for j in range(6):
            d = min_image_dist(cr_1x1[i], cl_1x1[j], lat_1x1)
            if d < 3.0:
                crcl_ref.append(d)

    if crcl_dists and crcl_ref:
        avg_crcl = np.mean(crcl_dists)
        avg_crcl_ref = np.mean(crcl_ref)
        check(abs(avg_crcl - avg_crcl_ref) < 0.05,
              "Avg Cr-Cl bond = {:.4f} A (1x1 ref = {:.4f} A)".format(avg_crcl, avg_crcl_ref),
              "Avg Cr-Cl bond = {:.4f} A != {:.4f} A".format(avg_crcl, avg_crcl_ref))

    # 7. Site-Specific H Verification
    if has_h:
        h_coord = coords[-1]
        h_z_cart = h_coord[2] * c_2x2

        # Check H is above the slab (z > 0.5 in fractional)
        check(h_coord[2] > 0.5,
              "H is above slab center (z_frac = {:.6f} > 0.5)".format(h_coord[2]),
              "H is below slab center (z_frac = {:.6f})".format(h_coord[2]))

        if site_name == "S1":
            # Target is Atom 19 (Cl11) at index 18 (coords[18])
            cl11 = coords[18]
            d_xy = np.linalg.norm(((h_coord[:2] - cl11[:2]) - np.round(h_coord[:2] - cl11[:2])) @ lat_2x2[:2, :2])
            d_h_cl11 = (h_coord[2] - cl11[2]) * c_2x2
            check(d_xy < 1e-4,
                  "S1: H is positioned exactly atop Cl11 in-plane (d_xy = {:.6f} A)".format(d_xy),
                  "S1: H is not aligned atop Cl11 in-plane (d_xy = {:.6f} A)".format(d_xy))
            check(abs(d_h_cl11 - 1.30) < 1e-3,
                  "S1: H-Cl11 distance = {:.4f} A (target 1.30 A)".format(d_h_cl11),
                  "S1: H-Cl11 distance = {:.4f} A != 1.30 A".format(d_h_cl11))

        elif site_name == "S2":
            # Target is hollow site at (0.5, 0.5)
            d_xy = np.linalg.norm(((h_coord[:2] - [0.5, 0.5]) - np.round(h_coord[:2] - [0.5, 0.5])) @ lat_2x2[:2, :2])
            dz_slab = (h_coord[2] - 0.5) * c_2x2
            check(d_xy < 1e-4,
                  "S2: H is positioned exactly at hollow site (0.5, 0.5) (d_xy = {:.6f} A)".format(d_xy),
                  "S2: H is not at hollow center (d_xy = {:.6f} A)".format(d_xy))
            check(abs(dz_slab - 1.60) < 1e-3,
                  "S2: H height above slab center = {:.4f} A (target 1.60 A)".format(dz_slab),
                  "S2: H height above slab center = {:.4f} A != 1.60 A".format(dz_slab))

        elif site_name == "S3":
            # Target is Atom 3 (Cr3) at index 2 (coords[2])
            cr3 = coords[2]
            d_xy = np.linalg.norm(((h_coord[:2] - cr3[:2]) - np.round(h_coord[:2] - cr3[:2])) @ lat_2x2[:2, :2])
            d_h_cr3 = (h_coord[2] - cr3[2]) * c_2x2
            check(d_xy < 1e-4,
                  "S3: H is positioned exactly atop Cr3 in-plane (d_xy = {:.6f} A)".format(d_xy),
                  "S3: H is not aligned atop Cr3 in-plane (d_xy = {:.6f} A)".format(d_xy))
            check(abs(d_h_cr3 - 1.55) < 1e-3,
                  "S3: H-Cr3 distance = {:.4f} A (matches paper equilibrium 1.55 A)".format(d_h_cr3),
                  "S3: H-Cr3 distance = {:.4f} A != 1.55 A".format(d_h_cr3))


def verify_incar(incar_path, vdw_expected, has_h):
    """Verify INCAR parameters."""
    print("\n  --- Verifying INCAR: {} ---".format(os.path.relpath(incar_path, SCRIPT_DIR)))

    with open(incar_path, "r") as f:
        content = f.read()

    # ISIF = 2
    isif_match = re.search(r"^ISIF\s*=\s*(\d+)", content, re.MULTILINE)
    if isif_match:
        check(isif_match.group(1) == "2",
              "ISIF = 2 (relax ions only, fixed cell)",
              "ISIF = {} (expected 2)".format(isif_match.group(1)))
    else:
        check(False, "", "ISIF tag not found in INCAR")

    # LDAU = .FALSE.
    ldau_match = re.search(r"LDAU\s*=\s*\.(\w+)\.", content)
    if ldau_match:
        check(ldau_match.group(1).upper() == "FALSE",
              "LDAU = .FALSE. (no Hubbard U)",
              "LDAU = .{}. (expected .FALSE.)".format(ldau_match.group(1)))

    # EDIFFG
    ediffg_match = re.search(r"EDIFFG\s*=\s*([\-\d.]+)", content)
    if ediffg_match:
        val = float(ediffg_match.group(1))
        check(abs(val - (-0.025)) < 0.001,
              "EDIFFG = {} (paper standard)".format(val),
              "EDIFFG = {} (expected -0.025)".format(val))

    # vdW check
    ivdw_match = re.search(r"IVDW\s*=\s*(\d+)", content)
    if vdw_expected:
        if ivdw_match:
            check(ivdw_match.group(1) == "11",
                  "IVDW = 11 (DFT-D3 enabled as expected)",
                  "IVDW = {} (expected 11)".format(ivdw_match.group(1)))
        else:
            check(False, "", "IVDW tag missing (expected IVDW=11 for yes_vdw)")
    else:
        check(ivdw_match is None,
              "No IVDW tag (correct for no_vdw variant)",
              "IVDW = {} found (should be absent for no_vdw)".format(
                  ivdw_match.group(1) if ivdw_match else "?"))

    # MAGMOM count
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
        expected_atoms = 33 if has_h else 32
        check(total == expected_atoms,
              "MAGMOM count = {} (matches {} atoms)".format(total, expected_atoms),
              "MAGMOM count = {} (expected {})".format(total, expected_atoms))

    # LDIPOL
    ldipol_match = re.search(r"LDIPOL\s*=\s*\.(\w+)\.", content)
    if ldipol_match:
        check(ldipol_match.group(1).upper() == "TRUE",
              "LDIPOL = .TRUE. (dipole correction active)",
              "LDIPOL = .{}. (expected .TRUE.)".format(ldipol_match.group(1)))

    # Check all comments exist (every INCAR line with = should have a # comment)
    uncommented = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            if "#" not in stripped:
                uncommented.append(stripped)
    check(len(uncommented) == 0,
          "All INCAR variables have comments",
          "{} uncommented INCAR lines: {}".format(len(uncommented), uncommented[:3]))


def verify_potcar(potcar_path, has_h):
    """Verify POTCAR species order."""
    print("\n  --- Verifying POTCAR: {} ---".format(os.path.relpath(potcar_path, SCRIPT_DIR)))

    with open(potcar_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    titels = re.findall(r"TITEL\s*=\s*PAW_PBE\s+(\S+)", content)
    expected = ["Cr", "Cl", "H"] if has_h else ["Cr", "Cl"]
    check(titels == expected,
          "POTCAR species order: {} = {}".format(titels, expected),
          "POTCAR species order: {} != {}".format(titels, expected))


def cross_validate_existing(new_poscar, existing_poscar):
    """Cross-validate new S3 POSCAR against existing crcl3-2x2/H_S3/U_0 structure."""
    print("\n  --- Cross-validation against existing H_S3/U_0 ---")

    if not os.path.exists(existing_poscar):
        warn("Existing POSCAR not found: {}".format(existing_poscar))
        return

    lat_new, sp_new, cnt_new, crd_new = parse_poscar(new_poscar)
    lat_old, sp_old, cnt_old, crd_old = parse_poscar(existing_poscar)

    a_new = np.linalg.norm(lat_new[0])
    a_old = np.linalg.norm(lat_old[0])

    print("    [INFO] New a_2x2 = {:.4f} A (from quick_test_k551 CONTCAR)".format(a_new))
    print("    [INFO] Old a_2x2 = {:.4f} A (from past-calculations/U_0 CONTCAR)".format(a_old))

    diff_pct = abs(a_new - a_old) / a_old * 100
    check(diff_pct < 1.0,
          "Lattice diff = {:.4f}% (< 1%, consistent)".format(diff_pct),
          "Lattice diff = {:.4f}% (> 1%, inconsistent!)".format(diff_pct))

    check(cnt_new == cnt_old,
          "Atom counts match: {} == {}".format(cnt_new, cnt_old),
          "Atom counts differ: {} != {}".format(cnt_new, cnt_old))

    # Compare Cr z-coordinates
    cr_z_new = np.mean([crd_new[i][2] for i in range(8)])
    cr_z_old = np.mean([crd_old[i][2] for i in range(8)])
    check(abs(cr_z_new - cr_z_old) < 0.01,
          "Cr avg z_frac: new={:.6f}, old={:.6f}".format(cr_z_new, cr_z_old),
          "Cr avg z_frac differ significantly: new={:.6f}, old={:.6f}".format(cr_z_new, cr_z_old))

    # Compare H z-coordinate
    h_new = crd_new[-1]
    h_old = crd_old[-1]
    print("    [INFO] H position new (above Cr3): ({:.6f}, {:.6f}, {:.6f})".format(*h_new))
    print("    [INFO] H position old (above Cr1): ({:.6f}, {:.6f}, {:.6f})".format(*h_old))

    h_z_diff = abs(h_new[2] - h_old[2]) * C_VACUUM
    check(h_z_diff < 0.01,
          "H z-distance above Cr matches old calculation exactly: diff = {:.4f} A".format(h_z_diff),
          "H z-position diff = {:.3f} A (!= old calculation)".format(h_z_diff))


def main():
    global PASS, FAIL, WARN

    print("\n" + "=" * 85)
    print("   VERIFICATION: H ADSORPTION VASP INPUTS ON CrCl3 2x2 SUPERCELL")
    print("=" * 85)

    if not os.path.exists(CONTCAR_1X1):
        print("  [FATAL] 1x1 CONTCAR not found: {}".format(CONTCAR_1X1))
        sys.exit(1)

    variants = [
        ("no_vdw", False),
        ("yes_vdw", True),
    ]
    sites = ["clean", "S1", "S2", "S3"]

    for vdw_name, vdw_flag in variants:
        print("\n" + "=" * 60)
        print("  VARIANT: {} ({})".format(vdw_name, "DFT-D3" if vdw_flag else "Pure PBE"))
        print("=" * 60)

        for site in sites:
            site_dir = os.path.join(SCRIPT_DIR, vdw_name, site)
            has_h = site != "clean"

            poscar_path = os.path.join(site_dir, "POSCAR")
            incar_path = os.path.join(site_dir, "INCAR")
            potcar_path = os.path.join(site_dir, "POTCAR")
            kpoints_path = os.path.join(site_dir, "KPOINTS")
            job_path = os.path.join(site_dir, "job.sh")

            for fpath, fname in [(poscar_path, "POSCAR"), (incar_path, "INCAR"),
                                  (potcar_path, "POTCAR"), (kpoints_path, "KPOINTS"),
                                  (job_path, "job.sh")]:
                check(os.path.exists(fpath),
                      "{}/{}/{} exists".format(vdw_name, site, fname),
                      "{}/{}/{} MISSING".format(vdw_name, site, fname))

            if os.path.exists(poscar_path):
                verify_structure(poscar_path, CONTCAR_1X1, has_h, site)

            if os.path.exists(incar_path):
                verify_incar(incar_path, vdw_flag, has_h)

            if os.path.exists(potcar_path):
                verify_potcar(potcar_path, has_h)

    # Cross-validate S3 against existing calculations
    new_s3 = os.path.join(SCRIPT_DIR, "no_vdw", "S3", "POSCAR")
    if os.path.exists(new_s3):
        cross_validate_existing(new_s3, EXISTING_H_S3)

    print("\n" + "=" * 85)
    print("  VERIFICATION SUMMARY")
    print("  PASS: {}  |  FAIL: {}  |  WARN: {}".format(PASS, FAIL, WARN))
    if FAIL == 0:
        print("  STATUS: ALL CHECKS PASSED PERFECTLY")
    else:
        print("  STATUS: {} FAILURES DETECTED -- REVIEW ABOVE".format(FAIL))
    print("=" * 85 + "\n")

    return FAIL


if __name__ == "__main__":
    sys.exit(main())
