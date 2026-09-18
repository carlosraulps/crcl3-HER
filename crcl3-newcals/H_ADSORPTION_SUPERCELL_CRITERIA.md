# Scientific Criteria for Multi-Scale Supercell Adsorption of Hydrogen on Monolayer CrCl₃
**Systematic Coverage Scaling: 1×1 vs 2×2 vs 3×3 (Pure PBE vs PBE+D3, U=0 eV)**

---

## 1. Overview & Research Motivation

In density functional theory (DFT) investigations of 2D electrocatalysts for the Hydrogen Evolution Reaction (HER), the calculated hydrogen adsorption free energy $\Delta G_{\mathrm{H}^*}$ is strongly influenced by adsorbate coverage $\theta$. In a periodic slab calculation, placing a single hydrogen atom into a supercell of size $N \times N \times 1$ imposes an artificial periodic array of adsorbates with separation $d_{\mathrm{H-H}} = N \cdot a_{1\times1}$.

By systematically modeling the hierarchy:
1. **$1\times1$ Primitive Cell:** $\theta = 1.0$ H/cell ($0.50$ H/Cr), $d_{\mathrm{H-H}} \approx 6.05$ Å (High-coverage limit).
2. **$2\times2$ Supercell (Paper Benchmark):** $\theta = 0.25$ H/cell ($0.125$ H/Cr), $d_{\mathrm{H-H}} \approx 12.09$ Å (Moderate coverage).
3. **$3\times3$ Supercell:** $\theta = 0.111$ H/cell ($0.0556$ H/Cr), $d_{\mathrm{H-H}} \approx 18.14$ Å (Dilute, isolated adsorbate limit).

This hierarchy enables rigorous extrapolation of the thermodynamic descriptor $\Delta G_{\mathrm{H}^*}(\theta \to 0)$, isolating true single-atom adsorption from periodic dipole-dipole and elastic strain interactions.

---

## 2. The 6 Non-Trivial Supercell Construction Criteria

### Criterion 1: Local Triad Invariance ($S_1, S_2, S_3$)
To ensure that energy differences between supercell sizes reflect solely coverage effects rather than site mismatch, the local chemical neighborhood must remain strictly identical across all scales:
- **$S_2$ (Hollow):** Located at the Wyckoff $1a$ center of the Cr honeycomb ring. Surrounded by a 6-Cr planar ring at radius $r = a_{1\times1}/\sqrt{3} = 3.4908$ Å, and an upper 3-Cl triangular aperture at lateral radius $r_{xy} = 2.1724$ Å.
- **$S_3$ (Top-Cr):** Located directly above one of the 6 Cr atoms forming that exact honeycomb ring.
- **$S_1$ (Top-Cl):** Located directly above one of the 3 top-layer Cl atoms forming that exact aperture, which is simultaneously coordinated to the Cr atom of $S_3$ ($d_{\mathrm{Cr-Cl}} = 2.3568$ Å).

| Scale | $S_2$ Hollow Center | $S_3$ Top-Cr Center | $S_1$ Top-Cl Center |
|:---:|:---:|:---:|:---:|
| **$1\times1$** | $(0.00000, 0.00000)$ | $(0.66667, 0.33333)$ | $(0.35930, 0.35930)$ |
| **$2\times2$** | $(0.50000, 0.50000)$ | $(0.66667, 0.33333)$ | $(0.50000, 0.32035)$ |
| **$3\times3$** | $(0.33333, 0.33333)$ | $(0.44444, 0.22222)$ | $(0.33333, 0.21357)$ |

### Criterion 2: Reciprocal-Space ($k$-Point) Density Conservation
Reciprocal lattice vectors scale inversely with supercell size: $\mathbf{b}_i^{(N)} = \mathbf{b}_i^{(1)} / N$. To guarantee equivalent Brillouin-zone integration accuracy, the reciprocal grid spacing $\Delta k \approx \frac{4\pi}{\sqrt{3} \cdot a \cdot N_k}$ must remain approximately constant ($\Delta k \sim 0.10 - 0.13$ Å$^{-1}$):
- **$1\times1$ ($a = 6.05$ Å):** $10 \times 10 \times 1$ $\Gamma$-centered ($N_k \cdot a = 60.46$ Å, $\Delta k = 0.1200$ Å$^{-1}$).
- **$2\times2$ ($a = 12.09$ Å):** $5 \times 5 \times 1$ $\Gamma$-centered ($N_k \cdot a = 60.46$ Å, $\Delta k = 0.1200$ Å$^{-1}$).
- **$3\times3$ ($a = 18.14$ Å):** $3 \times 3 \times 1$ $\Gamma$-centered ($N_k \cdot a = 54.42$ Å, $\Delta k = 0.1333$ Å$^{-1}$).

### Criterion 3: Fixed Vacuum Layer ($c = 20.0000$ Å) & Dipole Correction
- All systems share an identical vacuum dimension $c = 20.0000$ Å.
- The Cr plane is centered at $z = 0.50000$ ($z = 10.0000$ Å).
- Electrostatic dipole correction is active in all calculations (`LDIPOL = .TRUE.`, `IDIPOL = 3`, `DIPOL = 0.5 0.5 0.5`) to eliminate spurious periodic dipole interactions across the vacuum.

### Criterion 4: Adsorbate "Goldilocks" Initial Placement Distances
- **$S_1$ (Top-Cl):** $\Delta z = 1.3000$ Å above target top-Cl. Avoids Pauli core repulsion ($d < 1.20$ Å) while ensuring smooth outward relaxation into the physisorbed state (~3.42 Å).
- **$S_2$ (Hollow):** $\Delta z = 1.6000$ Å above central Cr plane ($+0.2643$ Å above top-Cl plane). Nestled in the triangular pocket ($d_{\mathrm{H-Cl}} = 2.188$ Å).
- **$S_3$ (Top-Cr):** $\Delta z = 1.5500$ Å above target Cr atom ($+0.2143$ Å above top-Cl plane). Exactly matches the paper's equilibrium chemisorption distance with steric clearance of $+0.62$ Å to the three Cl ligands ($d_{\mathrm{H-Cl}} = 1.9535$ Å).

### Criterion 5: Magnetic Moment Scaling (`MAGMOM`)
Cr³⁺ is high-spin $3d^3$ ($S = 3/2$, ferromagnetic in-plane ground state):
- **$1\times1$ (8/9 atoms):** Clean: `2*3.0 6*0.0` | With H: `2*3.0 6*0.0 1*0.0`.
- **$2\times2$ (32/33 atoms):** Clean: `8*3.0 24*0.0` | With H: `8*3.0 24*0.0 1*0.0`.
- **$3\times3$ (72/73 atoms):** Clean: `18*3.0 54*0.0` | With H: `18*3.0 54*0.0 1*0.0`.

### Criterion 6: Ionic Relaxation Convergence
- Fixed cell shape and volume (`ISIF = 2`).
- Force threshold `EDIFFG = -0.025` eV/Å (paper standard).
- Energy threshold `EDIFF = 1.0E-06` eV.
- Projection in real space (`LREAL = Auto`) and `NCORE = 4`.

---

## 3. Directory Layout & Archives

Three sibling directories staged and verified:
1. `crcl3-1x1-h_ads-without-U/` (8 calcs, verified 162/162 checks PASSED)
   - Archive: `crcl3_1x1_h_ads_without_U.tar.gz` (1.49 MB)
2. `crcl3-2x2-h_ads-without-U/` (8 calcs, verified 180/180 checks PASSED)
   - Archive: `crcl3_2x2_h_ads_without_U.tar.gz` (1.50 MB)
3. `crcl3-3x3-h_ads-without-U/` (8 calcs, verified 162/162 checks PASSED)
   - Archive: `crcl3_3x3_h_ads_without_U.tar.gz` (1.50 MB)

Total: **24 VASP calculations** staged across the full multi-scale supercell matrix ($3 \text{ sizes} \times 2 \text{ vdW variants} \times 4 \text{ configurations}$).
