#!/usr/bin/env python3
"""
================================================================================
 PHYSICAL & MATHEMATICAL JUSTIFICATION FOR HYDROGEN ADSORPTION SITES AND
 OPTIMAL INITIAL z-DISTANCES ON CrCl3 (2x2) MONOLAYER
================================================================================

 This script documents and computes:
  1. Crystallographic coordinates of pristine monolayer CrCl3 (2x2 supercell).
  2. Exact mapping of target adsorption sites:
     - S1: Top-Cl directly above Atom 19 (Cl11)
     - S2: Hollow site at the center of the Cr honeycomb ring
     - S3: Top-Cr directly above Atom 3 (Cr3)
  3. Coordination spheres, interatomic distances, and sterics around each site.
  4. Physical justification of the initial z-distance (Goldilocks window):
     - Avoids Pauli core-repulsion catastrophe (d too small -> F > 50 eV/A)
     - Avoids flat asymptotic vacuum traps (d too large -> F ~ 0, barrier blocked)
  5. Mathematical modeling of Morse interaction potential and restoring forces.
================================================================================
"""

import math
import numpy as np

# ==============================================================================
# 1. CRYSTALLOGRAPHIC PARAMETERS & LATTICE
# ==============================================================================
# 2x2 supercell constructed from relaxed 1x1 zero-stress primitive cell
A_2X2 = 12.092548997049326  # In-plane lattice parameter (Angstrom)
C_VAC = 20.000000000000000  # Out-of-plane vacuum box height (Angstrom)

# Hexagonal lattice vectors in Cartesian coordinates:
# a1 = (a, 0, 0)
# a2 = (-a/2, a*sqrt(3)/2, 0)
# a3 = (0, 0, c)
LAT = np.array([
    [A_2X2, 0.0, 0.0],
    [-0.5 * A_2X2, 0.5 * math.sqrt(3.0) * A_2X2, 0.0],
    [0.0, 0.0, C_VAC]
])

def frac_to_cart(frac):
    """Convert fractional coordinates to Cartesian (Angstrom)."""
    return np.array(frac) @ LAT

def cart_to_frac(cart):
    """Convert Cartesian coordinates to fractional."""
    return np.array(cart) @ np.linalg.inv(LAT)

def pbc_diff(v_frac):
    """Apply periodic boundary conditions in in-plane fractional coordinates."""
    v = np.copy(v_frac)
    v[0] -= np.round(v[0])
    v[1] -= np.round(v[1])
    return v

# ==============================================================================
# 2. KEY SUBSTRATE ATOMS SPECIFIED BY CRYSTALLOGRAPHY
# ==============================================================================
# Atom 3: Cr3
FRAC_CR3 = np.array([2.0 / 3.0, 1.0 / 3.0, 0.5000000000000000])
CART_CR3 = frac_to_cart(FRAC_CR3)

# Atom 19: Cl11 (top-layer Cl)
# Relaxed fractional coordinates from DFT 1x1 expansion
U_CL = 0.3203499015681922
Z_TOP_CL = 0.5667861932599265
FRAC_CL11 = np.array([0.5000000000000000, U_CL, Z_TOP_CL])
CART_CL11 = frac_to_cart(FRAC_CL11)

# Hollow Site S2
FRAC_S2 = np.array([0.5000000000000000, 0.5000000000000000, 0.5000000000000000])
CART_S2 = frac_to_cart(FRAC_S2)

# ==============================================================================
# 3. PHYSICAL RADII & BONDING BENCHMARKS (from IUPAC / NIST / Literature)
# ==============================================================================
# Covalent radii (Pyykko & Atsumi, Chem. Eur. J. 2009; Cordero et al., Dalton Trans. 2008)
R_COV_H  = 0.31   # Angstrom (single bond)
R_COV_CL = 1.02   # Angstrom (single bond)
R_COV_CR = 1.28   # Angstrom (low-spin / covalent)

# Van der Waals radii (Bondi 1964; Alvarez, Dalton Trans. 2013)
R_VDW_H  = 1.20   # Angstrom
R_VDW_CL = 1.75   # Angstrom
R_VDW_CR = 2.00   # Angstrom

# Gas-phase / literature equilibrium bond lengths
R_EQ_HCL = 1.2746 # Angstrom (NIST experimental equilibrium bond length of HCl)
R_EQ_CRH = 1.5500 # Angstrom (Manuscript reported relaxed H-Cr chemisorption distance)

# ==============================================================================
# 4. OPTIMAL INITIAL PLACEMENT DISTANCES (Delta z)
# ==============================================================================
# Site S1 (Top-Cl, above Cl11):
# Placing H directly along the surface normal (z) above Cl11.
# d(H-Cl) = 1.30 A (slightly larger than gas-phase HCl 1.275 A by ~2%)
# Rationale:
#   - Sits on the attractive slope of the covalent bond potential.
#   - Avoids Pauli core repulsion (steep wall starts at d < 1.20 A).
#   - Allows natural relaxation: either chemisorption if bound, or smooth outward
#     migration to the physisorbed state (~3.42 A) as observed in the paper.
DZ_S1 = 1.3000  # Angstrom above Cl11

# Site S2 (Hollow site):
# S2 is located at the center of the Cr honeycomb ring at (0.5, 0.5).
# The central Cr plane is at z = 10.00 A. The top Cl layer is at z = 11.336 A (dz = 1.336 A).
# Placing H at dz = 1.60 A above the Cr central plane places H at z = 11.60 A, which is
# 0.264 A above the top Cl plane.
# Rationale:
#   - Distance to 3 nearest top-Cl atoms: sqrt(2.172^2 + 0.264^2) = 2.188 A.
#   - Well outside Cl covalent radius (1.33 A) and comfortably within vdW/electrostatic
#     sensing range.
#   - Prevents H from falling into unphysical in-plane steric clashes.
DZ_S2 = 1.6000  # Angstrom above central slab plane (z = 0.5)

# Site S3 (Top-Cr, above Cr3):
# Placing H directly along the surface normal above Cr3.
# The Cr central plane is at z = 10.00 A.
# Placing H at dz = 1.5500 A above Cr3 places H at z = 11.5500 A (0.214 A above the Cl plane).
# Rationale:
#   - Exactly matches the manuscript equilibrium distance: d(H-Cr) = 1.55 A.
#   - Distance to the 3 coordinating top-Cl ligands (Cl10, Cl11, Cl12):
#     d(H-Cl) = sqrt(1.942^2 + 0.214^2) = 1.953 A >> r_cov(H)+r_cov(Cl) = 1.33 A.
#   - Provides immediate overlap with Cr 3d_z2 orbital without Cl ligand steric collision.
#   - Ensures rapid, monotonic convergence during CG relaxation.
DZ_S3 = 1.5500  # Angstrom above Cr3

# ==============================================================================
# 5. MORSE POTENTIAL & FORCE MODELING
# ==============================================================================
def morse_potential(r, de, a, re):
    """Morse potential V(r) = De * [ (1 - exp(-a*(r - re)))^2 - 1 ]."""
    x = 1.0 - math.exp(-a * (r - re))
    return de * (x**2 - 1.0)

def morse_force(r, de, a, re):
    """Restoring force F(r) = -dV/dr = -2 * a * De * (1 - exp(-a*(r-re))) * exp(-a*(r-re))."""
    exp_term = math.exp(-a * (r - re))
    return -2.0 * a * de * (1.0 - exp_term) * exp_term

def analyze_h_cl_potential():
    """Analyze H-Cl potential energy curve (HCl parameters: De ~ 4.62 eV, re = 1.275 A, a ~ 1.87 A^-1)."""
    de = 4.62
    re = 1.2746
    a = 1.87
    distances = [1.00, 1.10, 1.20, 1.25, 1.275, 1.30, 1.35, 1.40, 1.60, 2.00, 2.50, 3.00]
    results = []
    for r in distances:
        v = morse_potential(r, de, a, re)
        f = morse_force(r, de, a, re)
        results.append((r, v, f))
    return results

def analyze_h_cr_potential():
    """Analyze H-Cr potential energy curve (CrH parameters: De ~ 2.11 eV, re = 1.55 A, a ~ 1.60 A^-1)."""
    de = 2.11
    re = 1.5500
    a = 1.60
    distances = [1.20, 1.30, 1.40, 1.50, 1.55, 1.60, 1.70, 1.80, 2.00, 2.50, 3.00]
    results = []
    for r in distances:
        v = morse_potential(r, de, a, re)
        f = morse_force(r, de, a, re)
        results.append((r, v, f))
    return results

# ==============================================================================
# 6. PRINT DETAILED SCIENTIFIC REPORT
# ==============================================================================
def main():
    print("=" * 85)
    print(" HYDROGEN ADSORPTION PHYSICS & MATHEMATICAL ANALYSIS: CrCl3 (2x2) MONOLAYER")
    print("=" * 85)

    print("\n1. SUBSTRATE AND SITE MAPPING:")
    print("   Supercell dimensions: a = {:.5f} A, c = {:.5f} A".format(A_2X2, C_VAC))
    print("   Cr plane: z = {:.5f} A (frac z = 0.50000)".format(0.5 * C_VAC))
    print("   Top-Cl plane: z = {:.5f} A (frac z = {:.5f})".format(Z_TOP_CL * C_VAC, Z_TOP_CL))
    print("   Cl layer height above Cr: dz = {:.5f} A".format((Z_TOP_CL - 0.5) * C_VAC))

    print("\n2. ADSORPTION SITE SPECIFICATIONS:")
    # S1
    h_s1_cart = CART_CL11 + np.array([0.0, 0.0, DZ_S1])
    h_s1_frac = cart_to_frac(h_s1_cart)
    print("   [Site S1: Top-Cl above Atom 19 (Cl11)]")
    print("     Substrate Atom 19: frac = ({:.5f}, {:.5f}, {:.5f})".format(*FRAC_CL11))
    print("                        cart = ({:.5f}, {:.5f}, {:.5f}) A".format(*CART_CL11))
    print("     Optimal Initial H: cart = ({:.5f}, {:.5f}, {:.5f}) A".format(*h_s1_cart))
    print("                        frac = ({:.5f}, {:.5f}, {:.5f})".format(*h_s1_frac))
    print("     Initial d(H-Cl11): {:.4f} A".format(DZ_S1))

    # S2
    h_s2_cart = CART_S2 + np.array([0.0, 0.0, DZ_S2])
    h_s2_frac = cart_to_frac(h_s2_cart)
    print("\n   [Site S2: Hollow Site at Cr Honeycomb Center]")
    print("     Hollow Center:     frac = ({:.5f}, {:.5f}, {:.5f})".format(*FRAC_S2))
    print("                        cart = ({:.5f}, {:.5f}, {:.5f}) A".format(*CART_S2))
    print("     Optimal Initial H: cart = ({:.5f}, {:.5f}, {:.5f}) A".format(*h_s2_cart))
    print("                        frac = ({:.5f}, {:.5f}, {:.5f})".format(*h_s2_frac))
    print("     Height above Cr plane:   {:.4f} A".format(DZ_S2))
    print("     Height above Cl plane:   {:.4f} A".format(h_s2_cart[2] - CART_CL11[2]))

    # S3
    h_s3_cart = CART_CR3 + np.array([0.0, 0.0, DZ_S3])
    h_s3_frac = cart_to_frac(h_s3_cart)
    print("\n   [Site S3: Top-Cr above Atom 3 (Cr3)]")
    print("     Substrate Atom 3:  frac = ({:.5f}, {:.5f}, {:.5f})".format(*FRAC_CR3))
    print("                        cart = ({:.5f}, {:.5f}, {:.5f}) A".format(*CART_CR3))
    print("     Optimal Initial H: cart = ({:.5f}, {:.5f}, {:.5f}) A".format(*h_s3_cart))
    print("                        frac = ({:.5f}, {:.5f}, {:.5f})".format(*h_s3_frac))
    print("     Initial d(H-Cr3):  {:.4f} A".format(DZ_S3))
    print("     Height above Cl plane:   {:.4f} A".format(h_s3_cart[2] - CART_CL11[2]))

    # Coordination distances for S3
    # Find distance from S3 H to the 3 coordinating Cl ligands of Cr3
    r_xy_cl = math.sqrt((CART_CL11[0] - CART_CR3[0])**2 + (CART_CL11[1] - CART_CR3[1])**2)
    dz_cl_cr = CART_CL11[2] - CART_CR3[2]
    d_h_cl = math.sqrt(r_xy_cl**2 + (DZ_S3 - dz_cl_cr)**2)
    print("     Lateral distance to coordinating Cl ligands: r_xy = {:.4f} A".format(r_xy_cl))
    print("     3D distance to coordinating Cl ligands:      d(H-Cl) = {:.4f} A".format(d_h_cl))
    print("     Steric clearance: d(H-Cl) - [r_cov(H)+r_cov(Cl)] = {:.4f} A (No steric clash!)".format(
        d_h_cl - (R_COV_H + R_COV_CL)))

    print("\n3. MATHEMATICAL FORCE-DISTANCE ANALYSIS (Goldilocks Principle):")
    print("   -------------------------------------------------------------------------")
    print("   Target: H-Cl interaction (Model: Morse Potential, De=4.62 eV, re=1.275 A)")
    print("   -------------------------------------------------------------------------")
    print("     r (A)   |  V(r) (eV)  |  F(r) (eV/A)  | Physical Interpretation")
    print("   ----------+-------------+---------------+---------------------------------")
    for r, v, f in analyze_h_cl_potential():
        if r < 1.15:
            interp = "DANGEROUS: Severe Pauli repulsion (numerical instability)"
        elif abs(r - 1.275) < 0.01:
            interp = "Equilibrium minimum (zero net force)"
        elif r == 1.30:
            interp = "OPTIMAL INITIAL: Moderate restoring force, smooth CG relaxation"
        elif r < 1.60:
            interp = "Attractive well: good gradient pull towards substrate"
        elif r < 2.50:
            interp = "Weak interaction tail: slow descent"
        else:
            interp = "Asymptotic vacuum: forces < EDIFFG, premature termination trap"
        print("     {:5.3f}   |   {:7.3f}   |    {:7.3f}    | {}".format(r, v, f, interp))

    print("\n   -------------------------------------------------------------------------")
    print("   Target: H-Cr interaction (Model: Morse Potential, De=2.11 eV, re=1.550 A)")
    print("   -------------------------------------------------------------------------")
    print("     r (A)   |  V(r) (eV)  |  F(r) (eV/A)  | Physical Interpretation")
    print("   ----------+-------------+---------------+---------------------------------")
    for r, v, f in analyze_h_cr_potential():
        if r < 1.35:
            interp = "DANGEROUS: Core repulsion wall, high initial stresses"
        elif abs(r - 1.550) < 0.01:
            interp = "OPTIMAL INITIAL: Exactly matches paper equilibrium minimum!"
        elif r <= 1.60:
            interp = "Excellent: gentle restoring force directed towards Cr"
        elif r < 2.00:
            interp = "Cl-layer boundary: risk of barrier deflection"
        else:
            interp = "Above Cl plane: electrostatically screened, cannot penetrate to Cr"
        print("     {:5.3f}   |   {:7.3f}   |    {:7.3f}    | {}".format(r, v, f, interp))

    print("\n" + "=" * 85)
    print(" SUMMARY OF FINAL POSITIONS FOR setup_h_ads.py:")
    print("=" * 85)
    print(" Site S1 (top-Cl): [ 0.5000000000000000, 0.3203499015681922, {:.16f} ]".format(h_s1_frac[2]))
    print(" Site S2 (hollow): [ 0.5000000000000000, 0.5000000000000000, {:.16f} ]".format(h_s2_frac[2]))
    print(" Site S3 (top-Cr): [ 0.6666666666666666, 0.3333333333333333, {:.16f} ]".format(h_s3_frac[2]))
    print("=" * 85 + "\n")

if __name__ == "__main__":
    main()
