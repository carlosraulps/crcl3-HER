#!/usr/bin/env python3
"""
PHYSICAL & COORDINATION ANALYSIS: Co ADSORPTION SITES ON CrCl3 (2x2)
"""
import math
import numpy as np

A_2X2 = 12.092548997049326
C_VAC = 20.000000000000000

LAT = np.array([
    [A_2X2, 0.0, 0.0],
    [-0.5 * A_2X2, 0.5 * math.sqrt(3.0) * A_2X2, 0.0],
    [0.0, 0.0, C_VAC]
])

def frac_to_cart(frac):
    return np.array(frac) @ LAT

def main():
    print("=" * 80)
    print("   COORDINATION SPHERE AND INTERATOMIC DISTANCE ANALYSIS FOR Co")
    print("=" * 80)

    cl11_frac = np.array([0.50000, 0.3203499, 0.566786])
    cl11_cart = frac_to_cart(cl11_frac)

    cr3_frac = np.array([2.0/3.0, 1.0/3.0, 0.500000])
    cr3_cart = frac_to_cart(cr3_frac)

    s1_tm_cart = np.array([cl11_cart[0], cl11_cart[1], cl11_cart[2] + 2.25])
    d_s1_cl = np.linalg.norm(s1_tm_cart - cl11_cart)
    print("\n[Site S1: Top-Cl]")
    print("  Target atom: Cl11 at ({:.3f}, {:.3f}, {:.3f}) A".format(*cl11_cart))
    print("  Co placement: ({:.3f}, {:.3f}, {:.3f}) A".format(*s1_tm_cart))
    print("  Direct Co-Cl11 distance: {:.4f} A".format(d_s1_cl))

    s2_frac = np.array([0.5, 0.5, 0.5])
    s2_cart = frac_to_cart(s2_frac)
    s2_tm_cart = np.array([s2_cart[0], s2_cart[1], s2_cart[2] + 1.9])
    dz_s2 = s2_tm_cart[2] - s2_cart[2]
    d_s2_cl = math.sqrt(2.1724**2 + (dz_s2 - (cl11_cart[2] - s2_cart[2]))**2)
    d_s2_cr = math.sqrt(3.4908**2 + dz_s2**2)
    print("\n[Site S2: Hollow (Cr honeycomb ring center)]")
    print("  Center coordinates: ({:.3f}, {:.3f}, {:.3f}) A".format(*s2_cart))
    print("  Co placement: ({:.3f}, {:.3f}, {:.3f}) A".format(*s2_tm_cart))
    print("  Height above Cr plane: {:.4f} A".format(dz_s2))
    print("  Distance to 3 aperture Cl atoms: {:.4f} A".format(d_s2_cl))
    print("  Distance to 6 honeycomb Cr atoms: {:.4f} A".format(d_s2_cr))

    s3_tm_cart = np.array([cr3_cart[0], cr3_cart[1], cr3_cart[2] + 2.45])
    d_s3_cr = np.linalg.norm(s3_tm_cart - cr3_cart)
    dz_s3 = s3_tm_cart[2] - cr3_cart[2]
    d_s3_cl = math.sqrt(1.942**2 + (dz_s3 - (cl11_cart[2] - cr3_cart[2]))**2)
    print("\n[Site S3: Top-Cr]")
    print("  Target atom: Cr3 at ({:.3f}, {:.3f}, {:.3f}) A".format(*cr3_cart))
    print("  Co placement: ({:.3f}, {:.3f}, {:.3f}) A".format(*s3_tm_cart))
    print("  Direct Co-Cr3 distance: {:.4f} A".format(d_s3_cr))
    print("  Distance to 3 coordinated Cl atoms: {:.4f} A".format(d_s3_cl))
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
