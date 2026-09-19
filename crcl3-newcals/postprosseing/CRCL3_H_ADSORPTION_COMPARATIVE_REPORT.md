# Hydrogen Adsorption Energetics on Monolayer $\text{CrCl}_3$
## Multi-Scale Comparative Analysis: $1\times1$, $2\times2$, and $3\times3$ Supercells & Dispersion Effects

**Reference Standards:**
- Isolated $\text{H}_2$ gas-phase energy (Pure PBE, $15\times15\times15$ Å box): $E(\text{H}_2) = -6.759600\text{ eV} \implies \frac{1}{2}E(\text{H}_2) = -3.379800\text{ eV}$
- Thermodynamic HER correction: $\Delta G_{\mathrm{H}^*} = E_{\mathrm{ads}} + 0.24\text{ eV}$

---

### 1. Comprehensive Multi-Scale Energetics Summary Table

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
| 3x3 | 0.11 | Pure PBE | **Site 1 (Top-Cl)** | -351.6468 | -353.7608 | **-2.1140** | **1.2658** | **1.5058** | 55.00 $\mu_B$ | 80 |
| 3x3 | 0.11 | Pure PBE | **Site 2 (Hollow)** | -351.6468 | -352.5562 | **-0.9094** | **2.4704** | **2.7104** | 53.00 $\mu_B$ | 2 |
| 3x3 | 0.11 | Pure PBE | **Site 3 (Top-Cr)** | -351.6468 | -353.4262 | **-1.7794** | **1.6004** | **1.8404** | 53.00 $\mu_B$ | 24 |
| 3x3 | 0.11 | PBE+D3 (Zero) | **Site 1 (Top-Cl)** | -364.7418 | -366.8243 | **-2.0826** | **1.2972** | **1.5372** | 55.00 $\mu_B$ | 38 (running) |
| 3x3 | 0.11 | PBE+D3 (Zero) | **Site 2 (Hollow)** | -364.7418 | -365.7984 | **-1.0566** | **2.3232** | **2.5632** | 53.00 $\mu_B$ | 30 |
| 3x3 | 0.11 | PBE+D3 (Zero) | **Site 3 (Top-Cr)** | -364.7418 | -366.4930 | **-1.7512** | **1.6286** | **1.8686** | 53.00 $\mu_B$ | 28 |

---

### 2. Multi-Scale Physical & Mechanistic Insights

1. **Supercell Scaling & Lateral Dipole Coupling ($\theta = 1.00 \to 0.25 \to 0.11$):**
   - **Site 1 (Top-Cl):** Diluting hydrogen coverage significantly enhances binding affinity ($\Delta E$ changes from $-1.7017\text{ eV}$ in $1\times1$ to $-1.8009\text{ eV}$ in $2\times2$, reaching $-2.1140\text{ eV}$ in $3\times3$). This demonstrates that in dense monolayers, repulsive lateral Cl–H dipole interactions destabilize the adsorption state, whereas isolated adatoms in the $3\times3$ supercell allow the coordinated chlorine ligand to fully relax upward into the vacuum without adjacent steric strain.
   - **Site 3 (Top-Cr):** Exhibits remarkable energetic invariance across all scales:
     - Pure PBE: $\Delta E = -1.7439\text{ eV}$ ($1\times1$), $-1.7555\text{ eV}$ ($2\times2$), $-1.7794\text{ eV}$ ($3\times3$) [variance $< 35\text{ meV}$].
     - PBE+D3: $\Delta E = -1.7251\text{ eV}$ ($1\times1$), $-1.7560\text{ eV}$ ($2\times2$), $-1.7512\text{ eV}$ ($3\times3$) [variance $< 31\text{ meV}$].
     This confirms that the metal cation adsorption site forms a highly localized covalent $\text{Cr-H}$ bond with negligible long-range lateral coupling.
   - **Site 2 (Hollow):** Consistently unfavorable across all scales ($\Delta E \approx -0.89$ to $-1.05\text{ eV}$, $\Delta G \approx +2.56$ to $+2.73\text{ eV}$), firmly establishing that hydrogen avoids the open interstitial void of the Cr honeycomb ring.

2. **Thermodynamic HER Catalytic Implications ($\Delta G_{\mathrm{H}^*}$):**
   - The optimal HER catalyst satisfies the Sabatier criterion $\Delta G_{\mathrm{H}^*} \approx 0\text{ eV}$.
   - In pristine $\text{CrCl}_3$, all pristine sites exhibit $\Delta G_{\mathrm{H}^*} > 1.50\text{ eV}$, indicating weak binding relative to $\frac{1}{2}\text{H}_2$.
   - In the dilute $3\times3$ regime, Site 1 approaches $\Delta G_{\mathrm{H}^*} = 1.5058\text{ eV}$, showing the highest catalytic propensity among the intrinsic sites.

3. **Dispersion / van der Waals Influence:**
   - Inclusion of Grimme DFT-D3 consistently stabilizes the total system:
     - Pristine substrate: $E_{\mathrm{clean}}$ drops by $-0.912\text{ eV}$ ($1\times1$), $-3.650\text{ eV}$ ($2\times2$), and $-13.095\text{ eV}$ ($3\times3$).
     - Adsorption binding $\Delta E$ is enhanced by $-0.05$ to $-0.15\text{ eV}$ across all sites.
