# Comprehensive Comparison of CrCl3 Structures: Project Monolayers vs. Materials Project

This report resolves the structural relationships and distinguishes our project's **2D Monolayer ($1\times 1$ primitive and $2\times 2$ supercell)** from all 3D bulk polymorphs available in the Materials Project database.

## 1. Summary Comparison Table

| Structure Label | Origin / ID | Type | Space Group | $a$ (A) | $b$ (A) | $c$ (A) | $\gamma$ (deg) | Cr-Cl (A) | Cr-Cr (A) | Sites |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Our Monolayer 1x1 (Primitive)** | Project (Pristine 1x1) | 2D Monolayer | P-31m (162) | 6.048 | 6.048 | 17.670 | 120.0 | 2.375 | 3.492 | 8 |
| **Our Monolayer 2x2x1 (Supercell)** | Project (Substrate 2x2) | 2D Supercell | P31m (157) | 12.097 | 12.097 | 17.670 | 120.0 | 2.373 | 3.492 | 32 |
| **MP: mp-1192095 (C2/m)** | mp-1192095 | 3D Bulk | C2/m (12) | 10.939 | 10.939 | 7.790 | 113.9 | 2.420 | 3.983 | 24 |
| **MP: mp-1193047 (C2/m)** | mp-1193047 | 3D Bulk | C2/m (12) | 10.520 | 10.520 | 7.850 | 111.2 | 2.352 | 4.144 | 24 |
| **MP: mp-27630 (C2/m)** | mp-27630 | 3D Bulk | C2/m (12) | 5.996 | 5.996 | 6.290 | 120.0 | 2.351 | 3.462 | 8 |
| **MP: mp-27630 (Conventional)** | mp-27630 (conv) | 3D Bulk (Conv Cell) | C2/m (12) | 6.000 | 10.383 | 6.290 | 90.0 | 2.351 | 3.463 | 16 |
| **MP: mp-567504 (R-3)** | mp-567504 | 3D Bulk | R-3 (148) | 6.895 | 6.894 | 6.893 | 51.6 | 2.351 | 3.461 | 8 |
| **MP: mp-567504 (Conventional)** | mp-567504 (conv) | 3D Bulk (Conv Cell) | R-3 (148) | 5.996 | 5.996 | 17.885 | 120.0 | 2.351 | 3.462 | 24 |
| **MP: mp-569890 (P3_212)** | mp-569890 | 3D Bulk | P3_212 (153) | 5.993 | 5.993 | 19.458 | 120.0 | 2.351 | 3.460 | 24 |


## 2. Detailed Distinctions

### Our Monolayer 1x1 (Primitive)
- **System Type**: 2D Monolayer
- **Space Group**: P-31m (No. 162), trigonal
- **Lattice Vectors**: $a = 6.0485\text{ A}$, $b = 6.0485\text{ A}$, $c = 17.6700\text{ A}$
- **Angles**: $\alpha = 90.00^\circ$, $\beta = 90.00^\circ$, $\gamma = 120.00^\circ$
- **Bonding**: Avg Cr-Cl = $2.375\text{ A}$, Cr-Cr = $3.492\text{ A}$, Coordination = 6-fold Cl octahedron
- **Notes**: Single Cl-Cr-Cl layer with ~15 A vacuum along c. Hexagonal lattice.

### Our Monolayer 2x2x1 (Supercell)
- **System Type**: 2D Supercell
- **Space Group**: P31m (No. 157), trigonal
- **Lattice Vectors**: $a = 12.0970\text{ A}$, $b = 12.0970\text{ A}$, $c = 17.6700\text{ A}$
- **Angles**: $\alpha = 90.00^\circ$, $\beta = 90.00^\circ$, $\gamma = 120.00^\circ$
- **Bonding**: Avg Cr-Cl = $2.373\text{ A}$, Cr-Cr = $3.492\text{ A}$, Coordination = 6-fold Cl octahedron
- **Notes**: 2x2 expansion of 1x1 monolayer (8 Cr, 24 Cl) used for TM dopant / adsorption calculations.

### MP: mp-1192095 (C2/m)
- **System Type**: 3D Bulk
- **Space Group**: C2/m (No. 12), monoclinic
- **Lattice Vectors**: $a = 10.9390\text{ A}$, $b = 10.9390\text{ A}$, $c = 7.7902\text{ A}$
- **Angles**: $\alpha = 69.25^\circ$, $\beta = 69.25^\circ$, $\gamma = 113.93^\circ$
- **Bonding**: Avg Cr-Cl = $2.420\text{ A}$, Cr-Cr = $3.983\text{ A}$, Coordination = 5-fold Cl octahedron
- **Notes**: Bulk CrCl3 (Monoclinic). High-energy bulk phase (E_above_hull > 0.3 eV).

### MP: mp-1193047 (C2/m)
- **System Type**: 3D Bulk
- **Space Group**: C2/m (No. 12), monoclinic
- **Lattice Vectors**: $a = 10.5203\text{ A}$, $b = 10.5203\text{ A}$, $c = 7.8503\text{ A}$
- **Angles**: $\alpha = 70.82^\circ$, $\beta = 70.82^\circ$, $\gamma = 111.24^\circ$
- **Bonding**: Avg Cr-Cl = $2.352\text{ A}$, Cr-Cr = $4.144\text{ A}$, Coordination = 5-fold Cl octahedron
- **Notes**: Bulk CrCl3 (Monoclinic). High-energy bulk phase (E_above_hull > 0.3 eV).

### MP: mp-27630 (C2/m)
- **System Type**: 3D Bulk
- **Space Group**: C2/m (No. 12), monoclinic
- **Lattice Vectors**: $a = 5.9960\text{ A}$, $b = 5.9961\text{ A}$, $c = 6.2900\text{ A}$
- **Angles**: $\alpha = 98.59^\circ$, $\beta = 98.71^\circ$, $\gamma = 119.95^\circ$
- **Bonding**: Avg Cr-Cl = $2.351\text{ A}$, Cr-Cr = $3.462\text{ A}$, Coordination = 6-fold Cl octahedron
- **Notes**: Bulk CrCl3 (Monoclinic). High-temperature monoclinic C2/m bulk phase.

### MP: mp-27630 (Conventional)
- **System Type**: 3D Bulk (Conv Cell)
- **Space Group**: C2/m (No. 12), monoclinic
- **Lattice Vectors**: $a = 6.0001\text{ A}$, $b = 10.3831\text{ A}$, $c = 6.2900\text{ A}$
- **Angles**: $\alpha = 90.00^\circ$, $\beta = 107.49^\circ$, $\gamma = 90.00^\circ$
- **Bonding**: Avg Cr-Cl = $2.351\text{ A}$, Cr-Cr = $3.463\text{ A}$, Coordination = 6-fold Cl octahedron
- **Notes**: Conventional unit cell for mp-27630, directly showing the in-plane honeycomb dimensions.

### MP: mp-567504 (R-3)
- **System Type**: 3D Bulk
- **Space Group**: R-3 (No. 148), trigonal
- **Lattice Vectors**: $a = 6.8948\text{ A}$, $b = 6.8942\text{ A}$, $c = 6.8931\text{ A}$
- **Angles**: $\alpha = 51.56^\circ$, $\beta = 51.56^\circ$, $\gamma = 51.55^\circ$
- **Bonding**: Avg Cr-Cl = $2.351\text{ A}$, Cr-Cr = $3.461\text{ A}$, Coordination = 6-fold Cl octahedron
- **Notes**: Bulk CrCl3 (Trigonal). Thermodynamic ground state in Materials Project.

### MP: mp-567504 (Conventional)
- **System Type**: 3D Bulk (Conv Cell)
- **Space Group**: R-3 (No. 148), trigonal
- **Lattice Vectors**: $a = 5.9961\text{ A}$, $b = 5.9961\text{ A}$, $c = 17.8852\text{ A}$
- **Angles**: $\alpha = 90.00^\circ$, $\beta = 90.00^\circ$, $\gamma = 120.00^\circ$
- **Bonding**: Avg Cr-Cl = $2.351\text{ A}$, Cr-Cr = $3.462\text{ A}$, Coordination = 6-fold Cl octahedron
- **Notes**: Conventional unit cell for mp-567504, directly showing the in-plane honeycomb dimensions.

### MP: mp-569890 (P3_212)
- **System Type**: 3D Bulk
- **Space Group**: P3_212 (No. 153), trigonal
- **Lattice Vectors**: $a = 5.9931\text{ A}$, $b = 5.9931\text{ A}$, $c = 19.4576\text{ A}$
- **Angles**: $\alpha = 90.00^\circ$, $\beta = 90.00^\circ$, $\gamma = 120.00^\circ$
- **Bonding**: Avg Cr-Cl = $2.351\text{ A}$, Cr-Cr = $3.460\text{ A}$, Coordination = 6-fold Cl octahedron
- **Notes**: Bulk CrCl3 (Trigonal). Metastable trigonal P3_212 bulk phase.

## 3. Key Takeaways for our 1x1 and 2x2 Calculations
1. **Never Confuse 1x1 Monolayer with Bulk MP Primitive Cells**:
   - The primary Materials Project ground state **`mp-567504`** is indexed in a rhombohedral cell ($a=6.895\text{ A}, \alpha=51.56^\circ$). In that setting, all 3 lattice vectors are tilted across layers to capture the ABC rhombohedral stacking.
   - In contrast, our project's **$1\times 1$ Monolayer** has $a = b = 6.0485\text{ A}$, $\gamma = 120^\circ$, with a pure perpendicular $c = 17.67\text{ A}$ ($(\alpha=\beta=90^\circ)$) providing a $15\text{ A}$ vacuum barrier.
2. **Relationship Between our 1x1 and 2x2 Cells**:
   - **$1\times 1$ Primitive Cell**: Formula $\text{Cr}_2\text{Cl}_6$ (8 atoms total). $a = 6.0485\text{ A}$, $b = 6.0485\text{ A}$, $\gamma = 120^\circ$.
   - **$2\times 2\times 1$ Supercell**: Formula $\text{Cr}_8\text{Cl}_{24}$ (32 atoms total). $a = 12.097\text{ A}$, $b = 12.097\text{ A}$, $\gamma = 120^\circ$.
   - The $2\times 2$ cell is an exact $2\times 2$ spatial doubling in the in-plane directions ($a_{2\times 2} = 2a_{1\times 1}, b_{2\times 2} = 2b_{1\times 1}$), preserving the exact same local bond lengths ($d_{\text{Cr-Cl}} = 2.375\text{ A}$) and hexagonal symmetry.
3. **Materials Project In-Plane Consistency**:
   - The conventional in-plane lattice constant of monoclinic **`mp-27630`** is $a = 5.996\text{ A}$.
   - The conventional in-plane lattice constant of rhombohedral **`mp-567504`** is $a_{\text{hex}} = 5.996\text{ A}$.
   - Our relaxed 2D monolayer has $a = 6.048\text{ A}$. The minor expansion ($+0.8\%$) is the standard, well-documented physics of single-layer relaxation following exfoliation from 3D vdW bulk.
