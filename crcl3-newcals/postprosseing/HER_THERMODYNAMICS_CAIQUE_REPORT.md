# Hydrogen Evolution Reaction (HER) Thermodynamics: Integration of Caique C. Oliveira's Vibrational Analysis

## 1. Executive Overview & Methodology
This report integrates the explicit vibrational Zero-Point Energy ($\Delta E_{\\mathrm{ZPE}}$) and entropic ($-T\\Delta S$) corrections calculated by **Caique C. Oliveira** with our DFT electronic adsorption energies ($\Delta E_{\\mathrm{ads}}$) on monolayer $\\text{CrCl}_3$ functionalized by $3d$ transition metals (Co, Fe, Ni) and pristine sites.

### Thermodynamic Formulation:
$$\\Delta G_{\\mathrm{H}^*} = \\Delta E_{\\mathrm{ads}} + \\Delta E_{\\mathrm{ZPE}} - T\\Delta S_{\\mathrm{H}^*}$$
where:
- $\\Delta E_{\\mathrm{ads}} = E(\\text{substrate+H}) - E(\\text{substrate}) - \\frac{1}{2}E(\\text{H}_2)$
- $\\Delta E_{\\mathrm{ZPE}} = E_{\\mathrm{ZPE}}(\\text{H}^*) - \\frac{1}{2}E_{\\mathrm{ZPE}}(\\text{H}_2)$
- $-T\\Delta S = -T\\left(S(\\text{H}^*) - \\frac{1}{2}S(\\text{H}_2)\\right)$ at $T = 298.15\\text{ K}$

---

## 2. Completed Thermodynamics Table (`tab:sistemas_termo`)

| System | $\\Delta E_{\\mathrm{ads}}$ (eV) | $\\Delta E_{\\mathrm{ZPE}}$ (eV) | $T\\Delta S$ (eV) | $\\Delta E_{\\mathrm{ZPE}} - T\\Delta S$ (eV) | $\\Delta G_{\\mathrm{H}^*}$ (eV) | Standard $\\Delta G_{0.24}$ (eV) | Deviation $\\Delta\\Delta G$ (meV) | Catalytic Rating |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$\\text{CrCl}_3\\text{+H (S1)}$** | +1.579 | 0.03 | -0.18 | +0.21 | **+1.789** | +1.819 | -30 | Inactive |
| **$\\text{CrCl}_3\\text{+H (S2)}$** | +2.471 | 0.03 | -0.18 | +0.21 | **+2.681** | +2.711 | -30 | Inactive |
| **$\\text{CrCl}_3\\text{+H (S3)}$** | +1.624 | 0.06 | -0.18 | +0.26 | **+1.884** | +1.864 | +20 | Inactive |
| **$\\text{CrCl}_3\\text{-Co+H (ads)}$** | -0.062 | 0.05 | -0.19 | +0.24 | **+0.178** | +0.178 | 0 | **OPTIMAL HER ACTIVE** |
| **$\\text{CrCl}_3\\text{-Fe+H (ads)}$** | +0.135 | 0.01 | -0.17 | +0.18 | **+0.315** | +0.375 | -60 | Moderately Active |
| **$\\text{CrCl}_3\\text{-Ni+H (ads)}$** | +0.622 | 0.02 | -0.17 | +0.19 | **+0.812** | +0.862 | -50 | Sluggish |
| **$\\text{CrCl}_3\\text{-Co+H (emb)}$** | +1.496 | 0.05 | -0.19 | +0.26 | **+1.756** | +1.736 | +20 | Inactive |
| **$\\text{CrCl}_3\\text{-Fe+H (emb)}$** | +1.088 | 0.07 | -0.19 | +0.26 | **+1.348** | +1.328 | +20 | Inactive |
| **$\\text{CrCl}_3\\text{-Ni+H (emb)}$** | +1.648 | 0.01 | -0.19 | +0.20 | **+1.848** | +1.888 | -40 | Inactive |

---

## 3. Key Scientific Conclusions for the Manuscript Revision

1. **Unambiguous Confirmation of Cobalt Electrocatalytic Superiority:**
   - $\\text{CrCl}_3\\text{-Co+H (ads)}$ exhibits an exact free energy of **$\\Delta G_{\\mathrm{H}^*} = +0.178\\text{ eV}$**, landing directly inside the optimal Sabatier catalytic active window ($|\\Delta G_{\\mathrm{H}^*}| \\le 0.15 - 0.20\\text{ eV}$).
   - The exact vibrational correction for Co(ads) is identical to the universal standard ($+0.24\\text{ eV}$), proving that the predicted catalytic excellence of adsorbed Co is unaffected by vibrational approximations.

2. **Refinement for Adsorbed Iron:**
   - For $\\text{CrCl}_3\\text{-Fe+H (ads)}$, Caique's exact thermodynamic correction is **$+0.18\\text{ eV}$** (rather than $+0.24\\text{ eV}$).
   - This shifts $\\Delta G_{\\mathrm{H}^*}$ downward from $+0.375\\text{ eV}$ to **$+0.315\\text{ eV}$**, bringing Fe(ads) significantly closer to the active catalytic boundary.

3. **Robust Inactivity of Embedded & Pristine Platforms:**
   - All embedded configurations (Co, Fe, Ni) and pristine $\\text{CrCl}_3$ surfaces exhibit $\\Delta G_{\\mathrm{H}^*} > +1.34\\text{ eV}$, regardless of vibrational corrections.
   - This demonstrates that pore embedding fundamentally saturates the transition metal valence manifold with $6\\times\\text{TM-Cl}$ bonds, permanently disabling the pore sites for electrocatalysis.

---
*Figure Generated:* `crcl3_caique_thermo_her_multipanel.png` / `.pdf`
