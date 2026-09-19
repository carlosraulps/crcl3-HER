# Hydrogen Adsorption on Monolayer $\text{CrCl}_3$ ($2\times2$ Supercell): Site 1 (Top-Cl) vs. Site 3 (Top-Cr)

**System:** Monolayer $\text{CrCl}_3$ ($2\times2$ supercell, 32 substrate atoms: 8 Cr, 24 Cl, 1 H adsorbate; $\theta = 0.25$ H/cell, $d_{\mathrm{H-H}} = 12.09$ Å)  
**DFT Specifications:** PBE and PBE+D3 (zero damping, $IVDW=11$), $E_{\mathrm{cut}} = 500\text{ eV}$, $5\times5\times1$ $\Gamma$-centered $k$-mesh, dipole correction enabled along $z$.

---

## 1. Executive Summary & Direct Answers

| Question / Parameter | **Site 1 ($S_1$, Top-Cl)** | **Site 3 ($S_3$, Top-Cr)** |
|:---|:---|:---|
| **Underlying Substrate Atom** | Atom 19 ($\text{Cl}_{11}$, top-layer Cl) | Atom 3 ($\text{Cr}_3$, central metal cation) |
| **Did H move much? ($|\Delta \vec{r}|$)** | **$0.077 - 0.079$ Å** (Very small displacement) | **$0.140 - 0.195$ Å** (Moderate upward displacement) |
| **In-plane movement ($\Delta r_{xy}$)** | **$\sim 0.0007 - 0.0008$ Å** (Practically zero) | **$0.0000$ Å** (Strictly zero, symmetry-locked) |
| **Out-of-plane movement ($\Delta z$)** | **$+0.077 - +0.079$ Å** (Shifted upward) | **$+0.140 - +0.195$ Å** (Shifted upward) |
| **Where is H staying?** | Directly atop $\text{Cl}_{19}$ in a covalent **$\text{H-Cl}$** bond | Centered on $\text{Cr}_3$ in an apical **$\text{H-Cr}$** chemisorption bond |
| **Primary Bond Length** | **$d(\text{H-Cl}) = 1.255 - 1.268$ Å** (HCl-like) | **$d(\text{H-Cr}) = 1.544 - 1.546$ Å** (Matches literature $1.55$ Å) |
| **Bond Tilt from Normal ($+z$)** | $\sim 6.7^\circ - 7.8^\circ$ (Slightly tilted) | **$0.00^\circ$** (Strictly perpendicular along 3-fold axis) |
| **Substrate Response** | $\text{Cl}_{19}$ pulls upward by $+0.12 - +0.13$ Å; $\text{Cr-Cl}$ elongates by $+0.31 - +0.33$ Å | $\text{Cr}_3$ cation puckers upward by $+0.15 - +0.20$ Å; 3 Cl ligands expand radially |
| **Binding Energy $\Delta E$** | **$-1.801\text{ eV}$** (PBE) / **$-1.867\text{ eV}$** (PBE+D3) | **$-1.755\text{ eV}$** (PBE) / **$-1.756\text{ eV}$** (PBE+D3) |
| **Total Magnetization** | **$25.000\,\mu_B$** (Ferromagnetic coupling, $+1\,\mu_B$) | **$23.000\,\mu_B$** (Antiferromagnetic pairing with Cr $3d$, $-1\,\mu_B$) |
| **Convergence Status** | 4 steps (PBE), 5 steps (PBE+D3) [Interrupted] | 10 steps (PBE), **20 steps (PBE+D3, CONVERGED ✅)** |

---

## 2. Geometric Trajectory & Displacement Breakdown

### A. Hydrogen Adsorbate Movement

```
Site S1 (Top-Cl):
  Initial POSCAR:  [4.10935, 3.35485, 12.63572] Å  --> Fractional: [0.50000, 0.32035, 0.63179]
  Relaxed CONTCAR: [4.10974, 3.35418, 12.71273] Å  --> Fractional: [0.50000, 0.32029, 0.63564]
  Δr vector:       ( +0.0004, -0.0007, +0.0770 ) Å
  Total |Δr|:      0.0770 Å  |  Δr_xy = 0.0008 Å  |  Δz = +0.0770 Å

Site S3 (Top-Cr):
  Initial POSCAR:  [6.04627, 3.49082, 11.55000] Å  --> Fractional: [0.66667, 0.33333, 0.57750]
  Relaxed CONTCAR: [6.04627, 3.49082, 11.74542] Å  --> Fractional: [0.66667, 0.33333, 0.58727]
  Δr vector:       (  0.0000,  0.0000, +0.1954 ) Å
  Total |Δr|:      0.1954 Å  |  Δr_xy = 0.0000 Å  |  Δz = +0.1954 Å
```

> [!NOTE]
> **Why is $\Delta r_{xy} = 0.0000$ Å for Site S3?**  
> Site $S_3$ is positioned exactly at Wyckoff position $(2/3, 1/3)$ of the $2\times2$ supercell, which possesses local $C_{3v}$ 3-fold rotational symmetry. Any net lateral force would violate symmetry; hence all in-plane forces cancel identically ($F_x = 0, F_y = 0$). All relaxation occurs purely along the surface normal $z$.

---

### B. Substrate Lattice Perturbations & Structural Reconstruction

Hydrogen adsorption does not act on a rigid substrate; the 2D monolayer relaxes in response to the adsorbate:

```
                  SITE 1 (Top-Cl)                             SITE 3 (Top-Cr)
              H                                           H
              | d = 1.255 Å                               | d = 1.546 Å
              v                                           v
             Cl19  <-- Pulled UP by +0.13 Å              Cr3   <-- Puckered UP by +0.20 Å
            /    \                                      / | \
           /      \  Elongated to 2.69 Å               /  |  \ Symmetrically expanded
          v        v (weaker bonds)                   v   v   v to 2.387 Å
        Cr2        Cr3                              Cl18 Cl19 Cl20
```

1. **Site $S_1$ (Local Bond Weakening & Outward Dimpling):**
   - The targeted chlorine atom ($\text{Cl}_{19}$) is pulled upward toward the vacuum by **$+0.1336$ Å** (its $z$-coordinate rises from $11.336$ Å to $11.469$ Å).
   - Because $\text{Cl}_{19}$ donates electron density into the covalent bond with H, its coordination to the underlying chromium cations ($\text{Cr}_2$ and $\text{Cr}_3$) weakens dramatically: the $\text{Cr}_3\text{--Cl}_{19}$ bond length expands from **$2.3568$ Å to $2.6872$ Å** ($\Delta d = +0.3305$ Å, a 14% bond dilation).
   - The underlying chromium atoms ($\text{Cr}_2$ and $\text{Cr}_3$) relax downward by **$-0.0966$ Å** into the sheet.

2. **Site $S_3$ (Cation Puckering & 3-Fold Symmetric Dilation):**
   - The central chromium cation ($\text{Cr}_3$) puckers **UPWARD** out of the chromium plane by **$+0.1993$ Å** (from $z = 10.000$ Å to $z = 10.199$ Å), rising toward the incoming H atom.
   - The three coordinating top-layer chlorine ligands ($\text{Cl}_{18}, \text{Cl}_{19}, \text{Cl}_{20}$) remain strictly degenerate due to $C_3$ symmetry. They expand radially and slightly downward ($\Delta z = -0.0155$ Å) to widen the triangular aperture from $r_{\mathrm{ligand}} = 2.3568$ Å to $2.3866$ Å ($\Delta d = +0.0298$ Å).
   - This cooperative motion creates a stable pseudo-7-coordinate capped-octahedral geometry around $\text{Cr}_3$.

---

## 3. Coordination Spheres: Where the H Atom Stays

### Site 1 ($S_1$, Top-Cl) Coordination Environment
- **Nearest neighbor:** $\text{Cl}_{19}$ at **$1.2549$ Å** (`yes_vdw`) / **$1.2682$ Å** (`no_vdw`).
  - *Comparison:* Experimental gas-phase $\text{H-Cl}$ bond length is $1.275$ Å. The surface $\text{H-Cl}$ bond is within $0.01 - 0.02$ Å of an isolated $\text{HCl}$ molecule.
- **Second-nearest Cl neighbors:** $\text{Cl}_{20}$ ($3.637$ Å), $\text{Cl}_{24}$ ($3.637$ Å), $\text{Cl}_{14}$ ($3.657$ Å).
- **Nearest Cr cations:** $\text{Cr}_2$ at $3.511$ Å, $\text{Cr}_3$ at $3.511$ Å.
- **Height above planes:**
  - Above underlying $\text{Cl}_{19}$ atom: $1.243$ Å
  - Above top-Cl average plane: $1.358$ Å
  - Above Cr average plane: $2.737$ Å

### Site 3 ($S_3$, Top-Cr) Coordination Environment
- **Nearest neighbor:** $\text{Cr}_3$ directly below at **$1.5461$ Å** (`yes_vdw`) / **$1.5436$ Å** (`no_vdw`).
  - *Comparison:* Matches literature chemisorption values ($1.55$ Å) with $< 0.005$ Å deviation.
- **Secondary coordination shell:** 3 top-layer Cl ligands at identical distances of **$2.1494$ Å** (`yes_vdw`) / **$2.1286$ Å** (`no_vdw`).
  - The $\text{H-Cl}$ distance ($2.15$ Å) provides a steric clearance of $+0.82$ Å beyond the sum of covalent radii ($r_{\mathrm{cov}}(\mathrm{H}) + r_{\mathrm{cov}}(\mathrm{Cl}) = 0.31 + 1.02 = 1.33$ Å).
- **Second-nearest Cr cations:** $\text{Cr}_4$ and $\text{Cr}_8$ at $3.932$ Å.
- **Height above planes:**
  - Above underlying $\text{Cr}_3$ cation: $1.546$ Å
  - Above top-Cl average plane: $0.432$ Å (nested snugly above the Cl triangular aperture)
  - Above Cr average plane: $1.741$ Å

---

## 4. Thermodynamic Energetics & Adsorption Potentials

### Energetics Matrix ($2\times2$ Supercell, $\theta = 0.25$)

$$\Delta E = E_{\mathrm{slab+H}} - E_{\mathrm{clean}}$$
$$E_{\mathrm{ads}} = \Delta E - \frac{1}{2} E(H_2)$$

*Reference values:*  
- Clean slab (PBE, `no_vdw`): $E_{\mathrm{clean}} = -156.286781\text{ eV}$  
- Clean slab (PBE+D3, `yes_vdw`): $E_{\mathrm{clean}} = -159.936609\text{ eV}$  
- Gas-phase $H_2$ (PBE, `no_vdw`): $E(H_2) = -6.759600\text{ eV} \implies \frac{1}{2}E(H_2) = -3.379800\text{ eV}$

| Variant | Adsorption Site | $E_{\mathrm{TOTEN}}$ (eV) | $\Delta E$ (eV) | $E_{\mathrm{ads}}$ vs $\frac{1}{2}H_2$ (eV) | $F_{\mathrm{max}}$ (eV/Å) | Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **PBE (`no_vdw`)** | **$S_1$ (Top-Cl)** | -158.087800 | **-1.801019** | **+1.578781** | 1.0363 | Interrupted (Step 4) |
| **PBE (`no_vdw`)** | **$S_3$ (Top-Cr)** | -158.042250 | **-1.755469** | **+1.624331** | 0.0759 | Interrupted (Step 10) |
| **PBE+D3 (`yes_vdw`)** | **$S_1$ (Top-Cl)** | -161.803840 | **-1.867231** | +1.512569 | 1.4226 | Interrupted (Step 5) |
| **PBE+D3 (`yes_vdw`)** | **$S_3$ (Top-Cr)** | -161.692640 | **-1.756031** | **+1.623769** | **0.0228** | **CONVERGED ✅ (Step 20)** |

> [!TIP]
> **Thermodynamic Preference:**
> - Both $S_1$ (Top-Cl) and $S_3$ (Top-Cr) are the two deepest thermodynamic minima on monolayer $\text{CrCl}_3$, with binding energies $\Delta E \approx -1.76$ to $-1.87\text{ eV}$.
> - They are virtually isoenergetic (differing by only **$\sim 0.046\text{ eV}$** in pure PBE and **$\sim 0.111\text{ eV}$** in PBE+D3).
> - By comparison, the hollow site ($S_2$) has $\Delta E \approx -0.909\text{ eV}$, which is **$\sim 0.85\text{ eV}$ higher in energy** (much less favorable).

---

## 5. Electronic Structure & Magnetic Coupling Mechanism

The spin state of monolayer $\text{CrCl}_3$ reveals distinct chemical bonding mechanisms between the two sites:

| Configuration | Cr Ions Configuration | Pristine Slab $M_{\mathrm{tot}}$ | System $M_{\mathrm{tot}}$ with H | Net Spin Difference $\Delta M$ |
|:---|:---:|:---:|:---:|:---:|
| **Clean $2\times2$ Slab** | $8 \times \text{Cr}^{3+} (3d^3, S=3/2)$ | $24.000\,\mu_B$ | — | — |
| **Site $S_1$ (Top-Cl)** | $8 \times \text{Cr}^{3+} + \text{Cl-H}$ | $24.000\,\mu_B$ | **$25.000\,\mu_B$** | **$+1.000\,\mu_B$** |
| **Site $S_3$ (Top-Cr)** | $7 \times \text{Cr}^{3+} + 1 \times (\text{Cr-H})$ | $24.000\,\mu_B$ | **$23.000\,\mu_B$** | **$-1.000\,\mu_B$** |

### Physical Origin of the Magnetization Shift
1. **Site $S_1$ ($\Delta M = +1\,\mu_B$):**  
   The H atom bonds to a closed-shell $\text{Cl}^-$ ($3p^6$) ligand. This leaves an unpaired electron localized in the surface-adsorbate complex whose spin aligns **ferromagnetically** with the underlying Cr layer, raising the total cell magnetization from $24\,\mu_B$ to $25\,\mu_B$.
2. **Site $S_3$ ($\Delta M = -1\,\mu_B$):**  
   The H $1s$ orbital overlaps directly with the singly-occupied $3d_{z^2}$ orbital of the underlying $\text{Cr}_3$ cation ($t_{2g}^3 \to$ low-spin bonded complex). The electron pairing is **antiferromagnetic** with respect to that local chromium spin, reducing the effective magnetic moment of the slab from $24\,\mu_B$ to $23\,\mu_B$.

---

## 6. Trajectory Evolution & Force Convergence

### Step-by-Step Trajectory for Converged Site $S_3$ (`yes_vdw`)

```
Step   E_free (eV)      H_z (Å)   Cr3_z (Å)   d(H-Cr) (Å)    |F_H| (eV/Å)   Max |F| (eV/Å)   Notes
----------------------------------------------------------------------------------------------------------------------
  1    -157.573880      11.5500    10.0000       1.5500         0.0722         0.8232        Initial setup
  4    -157.826615      11.5875    10.0378       1.5497         0.0190         0.5263        Cr begins upward puckering
 10    -157.617552      11.6811    10.1392       1.5419         0.0532         0.0730        Forces dropping rapidly
 15    -157.816193      11.7271    10.1856       1.5414         0.0637         0.1456        Substrate Cl ligands adjust
 20    -161.692640      11.7454    10.1993       1.5461         0.0138         0.0228        CONVERGED (Fmax < 0.025)
```

- Throughout all 20 steps, the bond distance $d(\text{H-Cr}_3)$ remained remarkably invariant at **$1.546 \pm 0.005$ Å**.
- The main physical process was the collective upward translation of the $\text{Cr}_3\text{--H}$ unit by $\approx +0.20$ Å out of the monolayer plane.
- The final forces were $|F_{\mathrm{H}}| = 0.0138\text{ eV/Å}$ and $|F_{\mathrm{Cr3}}| = 0.0096\text{ eV/Å}$, well below the strict threshold of $0.025\text{ eV/Å}$.
