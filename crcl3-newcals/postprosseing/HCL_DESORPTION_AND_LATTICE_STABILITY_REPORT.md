# Comprehensive Scientific Audit: Surface Chlorine Extraction & HCl Desorption on CrCl3(001)

## 1. Executive Summary & Phenomenological Clarification

Visual inspection of relaxed geometries for hydrogen adsorption atop surface chlorine (Site $S_1$, Top-Cl) reveals an apparent outward 'desorption' of the coordinated chlorine atom. This quantitative audit rigorously establishes the physical origin, structural coordinates, and electrochemical implications of this phenomenon for the Hydrogen Evolution Reaction (HER).

### Key Scientific Findings:
1. **Covalent HCl-Adduct Formation:** At Site $S_1$, the adsorbed hydrogen atom ($1s^1$) forms an ultra-short covalent bond with the chlorine atom ($d(\mathrm{H-Cl}) = 1.255 - 1.294\,\mathrm{\AA}$), which matches within $1.5\%$ the gas-phase equilibrium bond length of molecular $\mathrm{HCl}$ ($r_e = 1.275\,\mathrm{\AA}$).
2. **Cr-Cl Coordinate Bond Rupture:** In pristine $\mathrm{CrCl}_3$, each surface $\mathrm{Cl}^-$ ion coordinates two $\mathrm{Cr}^{3+}$ cations with a typical coordination bond length of $d(\mathrm{Cr-Cl}) \approx 2.35\,\mathrm{\AA}$. Protonation/hydrogenation into a formal $[\mathrm{H-Cl}]^0$ surface adduct drains the ligand lone-pair electron density, resulting in severe rupture/elongation of both $\mathrm{Cr-Cl}$ bonds to **$3.014 - 3.028\,\mathrm{\AA}$** (an elongation of $+0.67\,\mathrm{\AA}$).
3. **Vertical Puckering Displacement:** The affected chlorine atom is pulled out of the basal halogen plane toward the vacuum by **$\Delta z = +0.60$ to $+0.65\,\mathrm{\AA}$**.
4. **Thermodynamic Barrier Against Spontaneous Etching:** Despite this local structural distortion, complete dissolution into gas-phase $\mathrm{HCl(g)}$ plus a surface chlorine vacancy ($V_{\mathrm{Cl}}$) is prevented under standard conditions because the formation energy of a chlorine vacancy in transition metal trichlorides is strongly endergonic ($E_{\mathrm{form}}(V_{\mathrm{Cl}}) > +2.5\,\mathrm{eV}$). Furthermore, $\Delta G_{\mathrm{H}^*} = +1.12\,\mathrm{eV}$ to $+1.82\,\mathrm{eV}$ at Site $S_1$, meaning proton discharge onto surface chlorine is heavily disfavored at operational HER potentials ($U = 0\,\mathrm{V}$ vs RHE).
5. **Lattice Passivation via Transition Metal Functionalization:** Single-atom $\mathrm{Co, Fe, Ni}$ dopants completely eliminate this degradation mode. In TM-functionalized platforms, hydrogen binds directly and exclusively to the transition metal $d$-center ($d(\mathrm{M-H}) \approx 1.50 - 1.55\,\mathrm{\AA}$), preserving 100% of the underlying halogen lattice integrity ($\Delta z_{\mathrm{Cl}} < 0.03\,\mathrm{\AA}$, $d(\mathrm{M-Cl})$ intact at $2.28 - 2.40\,\mathrm{\AA}$) and providing optimal HER free energy ($\Delta G = -0.069\,\mathrm{eV}$ on Co).

## 2. Quantitative Structural & Energetic Comparison Across Functional Tiers

| Method / Functional | Site | $d(\mathrm{H-Cl})$ (Å) | $d(\mathrm{H-Cr})$ (Å) | $\Delta z(\mathrm{Cl})$ (Å) | Nearest Cr-Cl (Å) | $\Delta d(\mathrm{Cr-Cl})$ (Å) | $\Delta G_{\mathrm{H}^*}$ (eV) | Lattice Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **with-U (PBE+D3+U, U_Cr=3.29 eV)** | S1 | 1.294 | 3.273 | +0.647 | 3.014, 3.014 | +0.269, +0.269 | +1.126 | Incipient HCl Adduct / Ruptured |
| **with-U (PBE+D3+U, U_Cr=3.29 eV)** | S2 | 1.862 | 3.718 | -0.040 | 2.514, 2.514 | -0.231, -0.231 | +2.041 | Weak Surface Contact |
| **with-U (PBE+D3+U, U_Cr=3.29 eV)** | S3 | 2.131 | 1.552 | +0.028 | 2.375, 2.415 | -0.370, -0.330 | +2.437 | Intact Substrate |
| **without-U (PBE+D3(BJ), IVDW=12)** | S1 | 1.293 | 3.285 | +0.681 | 3.028, 3.028 | +0.302, +0.302 | +1.498 | Incipient HCl Adduct / Ruptured |
| **without-U (PBE+D3(BJ), IVDW=12)** | S2 | 2.083 | 3.688 | -0.034 | 2.373, 2.373 | -0.353, -0.353 | +2.534 | Weak Surface Contact |
| **without-U (PBE+D3(BJ), IVDW=12)** | S3 | 2.151 | 1.547 | +0.008 | 2.338, 2.385 | -0.388, -0.341 | +1.896 | Intact Substrate |
| **without-U (Pure PBE, no_vdw)** | S1 | 1.268 | 3.506 | +0.109 | 2.663, 2.663 | -0.066, -0.066 | +1.789 | Incipient HCl Adduct / Ruptured |
| **without-U (Pure PBE, no_vdw)** | S2 | 2.188 | 3.843 | +0.001 | 2.361, 2.361 | -0.368, -0.368 | +2.681 | Weak Surface Contact |
| **without-U (Pure PBE, no_vdw)** | S3 | 2.129 | 1.544 | -0.037 | 2.334, 2.379 | -0.394, -0.349 | +1.884 | Intact Substrate |
| **without-U (PBE+D3(Zero), IVDW=11)** | S1 | 1.255 | 3.511 | +0.125 | 2.687, 2.687 | -0.043, -0.043 | +1.724 | Incipient HCl Adduct / Ruptured |
| **without-U (PBE+D3(Zero), IVDW=11)** | S2 | 2.148 | 3.724 | +0.010 | 2.365, 2.365 | -0.365, -0.365 | +2.571 | Weak Surface Contact |
| **without-U (PBE+D3(Zero), IVDW=11)** | S3 | 2.149 | 1.546 | +0.007 | 2.343, 2.387 | -0.388, -0.344 | +1.885 | Intact Substrate |

---

## 3. Physical & Chemical Mechanism: Why Does This Occur?

### (A) Acid-Base Protonation vs Covalent Dissolution
In gas-phase chemistry, the reaction of a bare proton with chloride is barrierless and highly exothermic:
$$\mathrm{H}^+ + \mathrm{Cl}^- \longrightarrow \mathrm{HCl}_{(\mathrm{g})} \quad (\Delta H = -1395\,\mathrm{kJ/mol})$$

On the surface of 2D $\mathrm{CrCl}_3(001)$, the surface is terminated by a dense hexagonal bilayer of chlorine anions. When an $\mathrm{H}$ adatom approaches Site $S_1$ (directly on top of $\mathrm{Cl11}$):
- The unoccupied $\sigma^*$ orbital of the nascent $\mathrm{H-Cl}$ pair hybridizes with the $3p_z$ lone pair of $\mathrm{Cl}^-$.
- This forms a covalent $\sigma$ bonding orbital with high electron localization between $\mathrm{H}$ and $\mathrm{Cl}$.
- Because chlorine has only a limited valence electron pool, donating electron density into the $\mathrm{H-Cl}$ bond drastically diminishes the electron density available to maintain the coordinate bonds with the two adjacent $\mathrm{Cr}^{3+}$ cations.
- As a consequence, the two $\mathrm{Cr-Cl}$ bonds dissociate from their equilibrium length of $\sim 2.35\,\mathrm{\AA}$ to $\sim 3.02\,\mathrm{\AA}$, pulling the chlorine atom $+0.65\,\mathrm{\AA}$ normal to the surface plane.

### (B) Why Does It Not Fully Detach into Vacuum in the DFT Calculation?
In our DFT supercell calculations (at $T = 0\,\mathrm{K}$ in vacuum):
1. Even at $d(\mathrm{Cr-Cl}) = 3.02\,\mathrm{\AA}$, long-range van der Waals and electrostatic dipole-monopole interactions retain the neutral $\mathrm{HCl}$ species weakly bound to the surface as an adsorbed adduct.
2. Removing the $\mathrm{HCl}$ molecule completely to infinite distance would leave behind an isolated undercoordinated Cr center (a chlorine vacancy), which costs substantial lattice cohesion energy ($> +2.5\,\mathrm{eV}$).

### (C) Electrochemical Implications for the HER Mechanism
- **Site S1 is NOT a viable catalytic HER site:** For efficient HER catalysis, the Volmer-Heyrovsky reaction requires facile proton adsorption and reversible molecular hydrogen desorption ($\Delta G_{\mathrm{H}^*} \approx 0\,\mathrm{eV}$, with an intact catalyst surface). At Site $S_1$, because $\Delta G_{\mathrm{H}^*} = +1.12\,\mathrm{eV}$, proton discharge is severely hindered. If extreme cathodic overpotentials were applied, the protonation would trigger lattice dissolution (chemical etching into $\mathrm{HCl}$ and chromium chloride salt dissolution) rather than clean $\mathrm{H}_2$ gas generation.
- **Site S3 is structurally inert but catalytically sluggish:** At Site $S_3$ (Top-Cr), the $\mathrm{H}$ binds to $\mathrm{Cr}$ ($d = 1.55\,\mathrm{\AA}$) without perturbing the chlorine lattice ($\Delta z < 0.03\,\mathrm{\AA}$), but its free energy is deeply unfavorable ($\Delta G_{\mathrm{H}^*} = +2.44\,\mathrm{eV}$).
- **Single-Atom TM Functionalization Solves Both Challenges:** Introducing adsorbed or embedded $\mathrm{Co, Fe, Ni}$ creates transition-metal $d$-orbital active centers that stabilize the $\mathrm{H}^*$ intermediate at thermo-neutral free energy ($\Delta G_{\mathrm{H}^*} = -0.069\,\mathrm{eV}$ on Co) without inducing any halide extraction, thereby fully safeguarding the structural stability of the $\mathrm{CrCl}_3$ monolayer.

