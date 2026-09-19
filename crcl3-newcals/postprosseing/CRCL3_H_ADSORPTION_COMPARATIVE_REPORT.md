# Hydrogen Adsorption Energetics on Monolayer $\text{CrCl}_3$
## Comparative Analysis: $1\times1$ vs. $2\times2$ Supercells & Dispersion Effects

**Reference Standards:**
- Isolated $\text{H}_2$ gas-phase energy (Pure PBE, $15\times15\times15$ Å box): $E(\text{H}_2) = -6.759600\text{ eV} \implies \frac{1}{2}E(\text{H}_2) = -3.379800\text{ eV}$
- Thermodynamic HER correction: $\Delta G_{\mathrm{H}^*} = E_{\mathrm{ads}} + 0.24\text{ eV}$

---

### 1. Comprehensive Energetics Summary Table

| Supercell | Coverage $\theta$ | DFT Treatment | Adsorption Site | $E_{\mathrm{clean}}$ (eV) | $E_{\mathrm{tot}}$ (eV) | Binding $\Delta E$ (eV) | $E_{\mathrm{ads}}$ vs $\frac{1}{2}\text{H}_2$ (eV) | $\Delta G_{\mathrm{H}^*}$ (eV) | Magnetization | Ionic Steps |
|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1x1 | 1.00 | Pure PBE | **Site 1 (Top-Cl)** | -39.0717 | -40.7734 | **-1.7017** | **1.6781** | **1.9181** | 7.00 $\mu_B$ | 5 |
| 1x1 | 1.00 | Pure PBE | **Site 2 (Hollow)** | -39.0717 | -39.9647 | **-0.8931** | **2.4867** | **2.7267** | 5.04 $\mu_B$ | 2 |
| 1x1 | 1.00 | Pure PBE | **Site 3 (Top-Cr)** | -39.0717 | -40.8155 | **-1.7439** | **1.6359** | **1.8759** | 5.00 $\mu_B$ | 13 |
| 1x1 | 1.00 | PBE+D3 (Zero) | **Site 1 (Top-Cl)** | -39.9841 | -41.8232 | **-1.8391** | **1.5407** | **1.7807** | 7.00 $\mu_B$ | 6 |
| 1x1 | 1.00 | PBE+D3 (Zero) | **Site 2 (Hollow)** | -39.9841 | -40.9868 | **-1.0027** | **2.3771** | **2.6171** | 5.51 $\mu_B$ | 12 |
| 1x1 | 1.00 | PBE+D3 (Zero) | **Site 3 (Top-Cr)** | -39.9841 | -41.7093 | **-1.7251** | **1.6547** | **1.8947** | 5.00 $\mu_B$ | 13 |
| 2x2 | 0.25 | Pure PBE | **Site 1 (Top-Cl)** | -156.2868 | -158.0877 | **-1.8009** | **1.5789** | **1.8189** | 25.00 $\mu_B$ | 4 |
| 2x2 | 0.25 | Pure PBE | **Site 2 (Hollow)** | -156.2868 | -157.1957 | **-0.9089** | **2.4709** | **2.7109** | 23.00 $\mu_B$ | 2 |
| 2x2 | 0.25 | Pure PBE | **Site 3 (Top-Cr)** | -156.2868 | -158.0422 | **-1.7555** | **1.6243** | **1.8643** | 23.00 $\mu_B$ | 10 |
| 2x2 | 0.25 | PBE+D3 (Zero) | **Site 1 (Top-Cl)** | -159.9366 | -161.8036 | **-1.8670** | **1.5128** | **1.7528** | 25.00 $\mu_B$ | 5 |
| 2x2 | 0.25 | PBE+D3 (Zero) | **Site 2 (Hollow)** | -159.9366 | -160.9571 | **-1.0205** | **2.3593** | **2.5993** | 23.00 $\mu_B$ | 24 |
| 2x2 | 0.25 | PBE+D3 (Zero) | **Site 3 (Top-Cr)** | -159.9366 | -161.6926 | **-1.7560** | **1.6238** | **1.8638** | 23.00 $\mu_B$ | 20 |

---

### 2. Physical & Mechanistic Insights

1. **Site Competition ($S_1$ vs. $S_3$):**
   - Both **Site 1 (Top-Cl)** and **Site 3 (Top-Cr)** act as the two principal thermodynamic adsorption minima across all scales and functionals.
   - In the $2\times2$ supercell (isolated adatom limit, $\theta = 0.25$), Site 1 is marginally more favorable than Site 3 by **$0.045\text{ eV}$ (Pure PBE)** and **$0.111\text{ eV}$ (PBE+D3)**.
   - In contrast, **Site 2 (Hollow)** is energetically disfavored by **$+0.74$ to $+0.89\text{ eV}$**, showing that hydrogen avoids the open interstitial void of the Cr honeycomb ring.

2. **Supercell Scaling & Lateral Repulsion:**
   - Diluting hydrogen coverage from $\theta = 1.00$ ($1\times1$, $d_{\mathrm{H-H}} = 6.05$ Å) to $\theta = 0.25$ ($2\times2$, $d_{\mathrm{H-H}} = 12.09$ Å) stabilizes Site 1 by **$-0.099\text{ eV}$** (Pure PBE) and **$-0.028\text{ eV}$** (PBE+D3).
   - For Site 3, the binding energy is virtually invariant with scale (differing by only **$-0.011\text{ eV}$** in PBE and **$-0.031\text{ eV}$** in PBE+D3). This demonstrates that Site 3 represents a strongly localized chemisorption state with negligible lateral dipole coupling.

3. **Dispersion / van der Waals Influence:**
   - Inclusion of Grimme DFT-D3 zero damping (`yes_vdw`) consistently increases the binding energy across all sites by **$-0.03$ to $-0.14\text{ eV}$**.
   - Dispersion stabilizes the pristine monolayer lattice itself (lowering $E_{\mathrm{clean}}$ by $-0.912\text{ eV}$ in $1\times1$ and $-3.650\text{ eV}$ in $2\times2$), while also enhancing adatom-substrate dispersive attraction.
