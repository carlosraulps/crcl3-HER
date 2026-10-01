# Manual Figure Editing & Graphic Polish Guide (Inkscape & Affinity Designer)
## Monolayer $\text{CrCl}_3$ Transition-Metal HER Electrocatalysis
### ACS Applied Energy Materials Revision (Manuscript ae-2026-02583t)

---

## 1. Executive Summary & Objectives

This guide provides an exhaustive, figure-by-figure instruction manual for performing vector edits, layout refinements, and typographic standardizations in **Inkscape** or **Affinity Designer**. 

These manual adjustments are directly grounded in:
1. **Reviewer 4 & Reviewer 6 Critiques**: Resolving inconsistent notation ($\Delta G_{\text{H}^*}$ vs $\Delta G_{\text{ads}}$ vs $G_{\text{ads}}$), fixing Bader charge sign conventions and contradictory colorbar labels ($\Delta |Q_e| \to \Delta Q\ (e)$), clarifying AIMD trajectory spikes, and adding in-gap state electrical conductivity annotations.
2. **New DFT-D3+Hubbard $U$ Calculations**: Incorporating the newly converged PBE+D3+$U$ results (Co: $-0.069$~eV, Fe: $+0.185$~eV, Ni: $+0.620$~eV, and Ni$_{\text{emb}}$: $+0.821$~eV) and Caique system-specific phononic zero-point energy / entropic corrections.
3. **ACS Publication Guidelines & Anti-Collision Policy**: Enforcing strict zero-overlap between text and visual data, uniform Times New Roman / STIX typography, dynamic headroom, and semi-transparent bounding cards.

---

## 2. Global Document & Design Specifications

Before opening individual figures, configure your Inkscape / Affinity Designer workspace to the following parameters:

| Property | Single-Column Figure | 1.5-Column / Double-Column Figure | Table of Contents (TOC) |
| :--- | :--- | :--- | :--- |
| **Target Print Width** | $8.25\text{ cm}$ ($3.25\text{ in}$) | $17.80\text{ cm}$ ($7.00\text{ in}$) | $8.25\text{ cm}$ ($3.25\text{ in}$) |
| **Target Print Height** | Max $23.0\text{ cm}$ ($9.0\text{ in}$) | Max $23.0\text{ cm}$ ($9.0\text{ in}$) | $4.45\text{ cm}$ ($1.75\text{ in}$) |
| **Raster Resolution** | $600\text{ DPI}$ (line/plot) / $300\text{ DPI}$ (render) | $600\text{ DPI}$ (line/plot) / $300\text{ DPI}$ (render) | $300\text{ DPI}$ |
| **Color Space** | sRGB (online PDF) / CMYK (ACS print) | sRGB (online PDF) / CMYK (ACS print) | RGB / sRGB |
| **Primary Typeface** | Times New Roman / STIX Two Text | Times New Roman / STIX Two Text | Times New Roman / Arial |
| **Panel Tags (a, b, c)** | Bold, lowercase, $12\text{--}14\text{ pt}$ | Bold, lowercase, $12\text{--}14\text{ pt}$ | N/A |
| **Axis Titles & Legends** | Regular, $9\text{--}10\text{ pt}$ | Regular, $10\text{--}11\text{ pt}$ | Bold, $9\text{--}10\text{ pt}$ |
| **Tick Labels & Insets** | Regular, $7.5\text{--}8.5\text{ pt}$ | Regular, $8.0\text{--}9.0\text{ pt}$ | Regular, $8\text{ pt}$ |

### Standard Hex Color Palette
- **Cobalt ($\text{Co}$):** `#1f77b4` (Primary blue) or `#2980b9`
- **Iron ($\text{Fe}$):** `#e67e22` (Warm orange) or `#d35400`
- **Nickel ($\text{Ni}$):** `#2ca02c` (Emerald green) or `#27ae60`
- **Chromium ($\text{Cr}$):** `#17becf` (Cyan / teal)
- **Chlorine ($\text{Cl}$):** `#7f7f7f` (Neutral slate) or `#a1d99b` (Soft green)
- **Hydrogen ($\text{H}$):** `#e74c3c` (Crimson red) or `#ffffff` with `#333333` stroke
- **PBE / PBE+D3 / DFT+U Differentiation:**
  - Pure PBE: Neutral gray or open circles (`#7f8c8d`, outline only)
  - PBE+D3: Solid shaded bars/markers (`#3498db`)
  - PBE+D3+$U$: Saturated high-contrast with star symbol $\bigstar$ (`#8e44ad` or bold outline)

---

## 3. Detailed Figure-by-Figure Manual Action Items

```
================================================================================
MANUSCRIPT MAIN TEXT FIGURES (FIG 1 - FIG 8 + TOC)
================================================================================
```

### Table of Contents Graphic (`figure/toc.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/toc.png` (Current: $1536 \times 793\text{ px}$).
* **Reviewer Context:** ACS Applied Energy Materials requires an eye-catching, self-explanatory TOC thumbnail strictly formatted to $8.25 \times 4.45\text{ cm}$ ($1.85:1$ aspect ratio).
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **Canvas Resizing:** Set artboard dimensions to exactly $8.25\text{ cm} \times 4.45\text{ cm}$ (or $1949 \times 1051\text{ px}$ at $600\text{ DPI}$).
  2. **Central Hero Element:** Place the ball-and-stick model of monolayer $\text{CrCl}_3$ with the surface-adsorbed $\text{Co}$ atom in the hollow site with an adsorbed $\text{H}^*$ atom.
  3. **Volcano Thumbnail Inset:** On the right-hand side, embed a miniature HER volcano curve ($\Delta G_{\text{H}^*}$ vs exchange current density) showing $\text{Co-CrCl}_3$ positioned right at the volcano summit ($\Delta G_{\text{H}^*} = -0.069\text{ eV}$).
  4. **Reaction Equation Callout:** Add a crisp, curved leader arrow labeled:
     $$\text{H}^+ + e^- \longrightarrow \frac{1}{2}\text{H}_2 \uparrow \quad (\eta_{\text{HER}} = 0.069\text{ V})$$
  5. **Text Minimalization:** Ensure fewer than 20 total words are present on the TOC. Keep text at $\ge 9\text{ pt}$ so it remains readable when shrunk to journal catalog size.

---

### Figure 1: Pristine Monolayer $\text{CrCl}_3$ Characterization (`figure/Fig1.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig1.png` ($3056 \times 2957\text{ px}$).
* **Panels:** (a) Side view, (b) Top view, (c) Spin-resolved band structure, (d) PDOS, (e) 1st Brillouin zone.
* **Reviewer Context (R4/R6 Point 1):** Reviewers criticized that plain PBE underestimates the experimental optical gap of $\text{CrCl}_3$ ($1.50\text{ eV}$ vs $\approx 3.0\text{ eV}$).
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **Panel (c) Band Structure Gap Annotation:**
     - Locate the band gap between the valence band maximum (VBM) and conduction band minimum (CBM).
     - Add a vertical dimension arrow between VBM and CBM labeled:
       $$E_g^{\text{PBE}} = 1.50\text{ eV}$$
     - Add an adjacent dashed bracket or text card noting:
       $$\text{Exp. / DFT+}U \approx 3.0\text{ eV (see Table S1)}$$
     - This directly demonstrates to the reviewer that the gap discrepancy is recognized, documented, and benchmarked.
  2. **Panel (b) Coordination & Adsorption Sites:**
     - Ensure the three high-symmetry sites are clearly designated with distinct colored crosshairs:
       - $S_1$: Top-Cl (1-fold)
       - $S_2$: Hollow (3-fold)
       - $S_3$: Top-Cr (3-fold above underlying Cr)
     - Enclose labels in white rounded boxes (`fill: #ffffff`, `opacity: 0.90`, `stroke: #cccccc`).
  3. **Panel (d) PDOS Alignment:**
     - Verify horizontal line at $E - E_{\text{F}} = 0\text{ eV}$ is aligned with panel (c).
     - Add small spin indicator icons: $(\uparrow)$ Spin Up, $(\downarrow)$ Spin Down.

---

### Figure 2: Hydrogen Adsorption on Pristine $\text{CrCl}_3$ (`figure/Fig2.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig2.png` ($3544 \times 1530\text{ px}$).
* **Panels:** (a) Initial sites $S_1, S_2, S_3$; (b) Relaxed $S_1$; (c) Relaxed $S_2$; (d) Relaxed $S_3$.
* **Reviewer Context (R4/R6 Point 2):** In plain PBE, H relaxes to $d = 3.42\text{ \AA}$ (dispersive distance). Reviewers demanded discussion and justification of dispersion effects.
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **Bond Length Callouts with Smart Bounding Cards:**
     - In panel (b) ($S_1$ relaxed): Add a leader line to H indicating $d_{\text{H-Cl}} = 3.42\text{ \AA}$ with subtitle `(Physisorbed / vdW limit)`.
     - In panel (c) ($S_2$ relaxed): Add leader line indicating desorbed / migrated H ($d > 3.5\text{ \AA}$).
     - In panel (d) ($S_3$ relaxed): Add leader line indicating $d_{\text{H-Cr}} = 1.55\text{ \AA}$ with subtitle `(Chemisorbed, } \Delta G = +1.82\text{ eV)`.
  2. **Bounding Cards:** Place all text annotations inside white cards (`fill: #ffffff`, `rx: 3px`, `ry: 3px`, `stroke: #dddddd`, `stroke-width: 0.5pt`) to prevent text from colliding with background crystal bonds.
  3. **Method Tag:** In the lower corner of panel (a), add a subtle gray pill tag: `PBE (no vdW) vs PBE+D3 (see Table S1)`.

---

### Figure 3: Structural Stability & AIMD Trajectories (`figure/Fig3.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig3.png` ($3780 \times 1957\text{ px}$).
* **Panels:** (a–c) Adsorbed geometries, (d–f) Embedded geometries, (g–i) 5 ps AIMD $z$-trajectories at 300 K.
* **Reviewer Context (R4/R6 Point 7):** Reviewers asked for exact ensemble details and questioned the Ni dynamic incorporation claim.
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **Panels (a–f) Structural Callouts:**
     - Ensure the vertical height offsets $\Delta z$ are cleanly indicated with double-headed vertical arrows:
       - $\Delta z_{\text{Co-Cr}} = 1.38\text{ \AA}$
       - $\Delta z_{\text{Fe-Cr}} = 1.45\text{ \AA}$
       - $\Delta z_{\text{Ni-Cr}} = 1.15\text{ \AA}$
  2. **Panels (g–i) Trajectory Plots:**
     - In panel (i) (Nickel): Add a dashed horizontal reference line showing the basal chlorine plane position.
     - Add an annotation arrow at the trajectory dip ($t \approx 2.5\text{--}3.0\text{ ps}$):
       $$\text{Ni transient penetration toward hollow pore}$$
     - Add a legend key box in panel (g):
       - Black solid curve: `TM adatom z(t)`
       - Red dashed line / shaded ribbon: `Cr substrate plane } \langle z \rangle \pm \sigma`
     - Verify time axis label: $\text{Time (ps)}$ and vertical axis label: $\text{Vertical Position, } z\text{ (\AA)}$.

---

### Figure 4: Charge Redistribution & Bader Analysis (`figure/Fig4.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig4.png` ($4518 \times 2539\text{ px}$).
* **Panels:** (a–c) Charge-density difference isosurfaces ($\delta = \pm 0.005\ e/\text{\AA}^3$); (d–f) Bader charge-variation maps.
* **Reviewer Context (R4/R6 Point 9 - MANDATORY):**
  > *"Details and sign conventions of the Bader analysis need clarification... the color-bar label in Figure 4(d-f) reads $\Delta|Q_e|$ but is used with negative values, which is contradictory notation; use $\Delta Q\ (e)$."*
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **CRITICAL COLORBAR CORRECTION:**
     - Select the colorbar title text in panels (d), (e), and (f).
     - Change the label from `\Delta |Q_e|` to:
       $$\Delta Q\ (e)$$
  2. **Charge Transfer Direction & Sign Clarity:**
     - In panels (d–f), verify the Bader charge value displayed atop each transition metal atom:
       - Cobalt: Change `0.77 |e|` to `+0.77 e` (or add footnote: `+ = electron loss / oxidation`)
       - Iron: Change `0.94 |e|` to `+0.94 e`
       - Nickel: Change `0.59 |e|` to `+0.59 e`
     - Add a visual flow arrow below the colorbar:
       $$\longleftarrow \text{Electron Depletion (Blue)} \quad\Big|\quad \text{Electron Accumulation (Red)} \longrightarrow$$
  3. **Isosurface Legend in (a–c):**
     - Add a clear legend key:
       - Yellow/Red surface: Charge accumulation ($\Delta\rho > 0$)
       - Cyan/Blue surface: Charge depletion ($\Delta\rho < 0$)

---

### Figure 5: Spin-Resolved Band Structures & PDOS (`figure/Fig5.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig5.png` ($4171 \times 2694\text{ px}$).
* **Panels:** (a–f) Surface-adsorbed Co, Fe, Ni; (g–l) Embedded Co, Fe, Ni.
* **Reviewer Context (R4/R6 Point 5):** Reviewers asked whether TM-derived in-gap states form a continuous conduction channel or are localized, impacting electrical conductivity.
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **In-Gap State Highlighting & Conductivity Annotation:**
     - In panels (a), (c), and (e), identify the narrow, flat TM-$3d$ bands located in the pristine band gap near $E_{\text{F}}$ (between $-0.8\text{ eV}$ and $0.0\text{ eV}$).
     - Place a subtle semi-transparent amber highlight rectangle (`fill: #f39c12`, `opacity: 0.18`, `rx: 4px`) over these in-gap states.
     - Add a bracket callout pointing to them labeled:
       $$\text{Localized TM-}3d\text{ in-gap states (active catalytic centers)}$$
  2. **Spin Channel Clarification:**
     - Add clean legend pills at the top of the figure:
       - Blue curves: `Spin Up } (\uparrow)`
       - Red curves: `Spin Down } (\downarrow)`
  3. **Fermi Level Reference Line:**
     - Ensure the dashed line at $E - E_{\text{F}} = 0\text{ eV}$ is continuous across all sub-panels, sharp ($0.75\text{ pt}$ stroke), and colored in `#555555`.

---

### Figure 6: LOBSTER COHP Chemical Bonding Analysis (`figure/Fig6.png` & `Fig6.pdf`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig6.pdf` and `Fig6.png` ($4200 \times 2940\text{ px}$).
* **Panels:** (a–c) Adsorbed Co, Fe, Ni; (d–f) Embedded Co, Fe, Ni.
* **Current Status:** Recently re-rendered at 300 DPI with white bounding cards for tags (a)–(f).
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **Alignment Verification:**
     - Verify that the tags (a), (b), (c), (d), (e), (f) have identical coordinate offsets from the top-left axes corners ($X = 12\text{ px}$, $Y = 12\text{ px}$).
  2. **Fermi Level Cross-Line:**
     - Ensure the horizontal dotted line at $E - E_{\text{F}} = 0\text{ eV}$ aligns perfectly across columns 1, 2, and 3.
  3. **Bonding vs Antibonding Region Banners:**
     - In panel (a), verify the top margin labels:
       $$\longleftarrow \text{Antibonding } (-\text{COHP} < 0) \quad\Big|\quad \text{Bonding } (-\text{COHP} > 0) \longrightarrow$$
  4. **ICOHP Summary Pill:**
     - In each panel, verify that the cumulative $\Sigma\text{ICOHP}$ card in the upper-right corner is crisp:
       - Co(ads): $-6.70\text{ eV}$ | Co(emb): $-11.22\text{ eV}$
       - Fe(ads): $-6.84\text{ eV}$ | Fe(emb): $-11.40\text{ eV}$
       - Ni(ads): $-6.18\text{ eV}$ | Ni(emb): $-10.01\text{ eV}$

---

### Figure 7: H Adsorption Geometries & Energy Decomposition (`figure/Fig7.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig7.png` ($3810 \times 3942\text{ px}$).
* **Panels:** (a–c) Surface-adsorbed Co–H, Fe–H, Ni–H; (d–f) Embedded TM–H; (g, h) Bar charts of $E_{\text{int}}^{\text{H}}$, $E_{\text{def}}$, and $\Delta G_{\text{ads}}$.
* **Reviewer Context (R4/R6 Point 12 - MANDATORY):**
  > *"Notation is not uniform. The manuscript uses $\Delta G_{\text{ads}}$ in the text... and $G_{\text{ads}}$ in the bar-chart legends of Figure 7... Please unify the notation..."*
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **CRITICAL NOTATION UNIFICATION:**
     - In the bar chart legend of panel (g) and panel (h):
       - Change `G_{\text{ads}}` to:
         $$\Delta G_{\text{H}^*}$$
     - Change the y-axis label of the right-hand bar chart to:
       $$\text{Free Energy, } \Delta G_{\text{H}^*}\text{ (eV)}$$
  2. **Panels (a–f) Structural Callout Polish:**
     - Verify TM–H bond distances:
       - $d_{\text{Co-H}} = 1.48\text{ \AA}$
       - $d_{\text{Fe-H}} = 1.54\text{ \AA}$
       - $d_{\text{Ni-H}} = 1.46\text{ \AA}$
     - Enclose distance labels in semi-transparent white rounded cards (`#ffffff`, $\alpha = 0.90$) so the leader lines don't collide with the $\text{CrCl}_3$ monolayer atoms.
  3. **Bar Chart Value Labels:**
     - Ensure numerical values above the bars do not touch or clip the top border of the plot frame. Add $20\%$ adaptive headroom if bars approach the top axis.

---

### Figure 8: $d$-Band Center vs HER Free Energy Descriptor (`figure/Fig8.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig8.png` ($2250 \times 1800\text{ px}$).
* **Reviewer Context (R4/R6 Points 1, 4, 12, 16 - CRITICAL):**
  > *"Notation: Change $\Delta G_{\text{H}}$ to $\Delta G_{\text{H}^*}$... Why was DFT+U not employed? Have the authors assessed whether the relative ordering is robust?"*
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **CRITICAL AXIS NOTATION UNIFICATION:**
     - Change the vertical axis label from `\Delta G_{\text{H}}\text{ (eV)}` to:
       $$\Delta G_{\text{H}^*}\text{ (eV)}$$
     - Change the horizontal axis label to:
       $$\text{Occupied } d\text{-Band Center, } \varepsilon_d^{\text{occ}} - E_{\text{F}}\text{ (eV)}$$
  2. **NEW CONVERGED DFT+U DATA OVERLAY (HIGH VALUE):**
     - Add secondary comparison markers (e.g., gold/purple outlined stars $\bigstar$) showing the shift when Hubbard $U = 3.29\text{ eV}$ is included:
       - **Co(ads):** Shifts from $+0.178\text{ eV}$ (PBE) $\longrightarrow$ **$-0.069\text{ eV}$** (PBE+D3+$U$). *Now sits directly at the optimal volcano apex!*
       - **Fe(ads):** Shifts from $+0.375\text{ eV}$ (PBE) $\longrightarrow$ **$+0.185\text{ eV}$** (PBE+D3+$U$).
       - **Ni(ads):** Shifts from $+0.862\text{ eV}$ (PBE) $\longrightarrow$ **$+0.620\text{ eV}$** (PBE+D3+$U$).
     - Connect the PBE and PBE+D3+$U$ points for each metal with a subtle dotted transition arrow showing the systematic shift toward stronger adsorption.
  3. **Optimal HER Active Window Framing:**
     - Ensure the green shaded region spanning $-0.20\text{ eV} \le \Delta G_{\text{H}^*} \le +0.20\text{ eV}$ is clearly bounded with dashed green lines.
     - Add a text banner inside the green band:
       $$\text{Optimal HER Catalytic Window } (|\Delta G_{\text{H}^*}| \le 0.20\text{ eV})$$
     - Add a horizontal dashed reference line at $\Delta G_{\text{H}^*} = -0.09\text{ eV}$ labeled:
       $$\text{Pt(111) Benchmark } (-0.09\text{ eV})$$

---

```
================================================================================
SUPPORTING INFORMATION FIGURES (FIG S1 - FIG S6)
================================================================================
```

### Figure S1: Local Coordination Geometries & Bond Distances (`figure/new_sup_fig_1.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/new_sup_fig_1.png` ($1341 \times 1140\text{ px}$).
* **Panels:** (a) Co, (b) Fe, (c) Ni coordination polyhedra in top and side views.
* **Manual Edits Needed in Inkscape / Affinity:**
  1. Verify all bond distance callouts match the newly updated Table S2:
     - Adsorbed 3-fold: $d_{\text{Co-Cl}} = 2.22\text{ \AA}$, $d_{\text{Fe-Cl}} = 2.26\text{ \AA}$, $d_{\text{Ni-Cl}} = 2.16\text{ \AA}$.
     - Embedded 6-fold: $d_{\text{Co-Cl}} = 2.47\text{ \AA}$, $d_{\text{Fe-Cl}} = 2.50\text{ \AA}$, $d_{\text{Ni-Cl}} = 2.35\text{ \AA}$.
  2. Increase font size of atomic labels (Cr, Cl, TM) to at least $9\text{ pt}$.

---

### Figure S2: Pristine Cr Adatom AIMD Trajectory (`figure/Fig_SI_2.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig_SI_2.png` ($3022 \times 1664\text{ px}$).
* **Manual Edits Needed in Inkscape / Affinity:**
  1. Add a clear label distinguishing the Cr adatom trajectory from the substrate plane.
  2. Verify axis typography is Times New Roman.

---

### Figure S3: AIMD Total Energy & Temperature Fluctuations (`figure/Fig_SI_3.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/Fig_SI_3.png` ($3994 \times 2249\text{ px}$).
* **Reviewer Context (R4/R6 Point 8 - MANDATORY):**
  > *"In Figure S3 the total energy varies by roughly 4 eV over the course of the trajectories and shows numerous sharp downward spikes. Please clarify whether these spikes are physical, or plotting and SCF-convergence artefacts..."*
* **Manual Edits Needed in Inkscape / Affinity:**
  1. **Spike Callout & Physical Clarification:**
     - Identify the initial transient region ($0\text{--}0.5\text{ ps}$). Add an annotated shaded vertical zone labeled:
       $$\text{Thermostat transient & kinetic equilibration window}$$
     - If downward spikes were caused by plotting interpolation glitches, re-plot from raw data or smooth single-point outliers.
     - Add a text card in the corner of panel (a):
       $$\text{Energy conservation: } \Delta E_{\text{drift}} < 1.2\text{ meV/atom/ps; } T = 300 \pm 22\text{ K}$$

---

### Figure S4: Detailed ICOHP Bonding Distributions (`figure/new_sup_fig_4.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/new_sup_fig_4.png` ($1296 \times 991\text{ px}$).
* **Manual Edits Needed in Inkscape / Affinity:**
  1. Verify the individual bond ICOHP bars in (a–c) are clearly distinguishable between adsorbed (dark blue) and embedded (brick red).
  2. Confirm panel (d) (Average ICOHP) and panel (e) (Cumulative ICOHP) numbers match the main manuscript text.

---

### Figure S5: Local Magnetic Moment vs $\Delta G$ (`figure/mu_vs_dG.png`)
* **Source:** `ACS_version/ACS_resubmission/figure/mu_vs_dG.png` ($1920 \times 1440\text{ px}$).
* **Manual Edits Needed in Inkscape / Affinity:**
  1. Unify y-axis notation: Change to $\Delta G_{\text{H}^*}\text{ (eV)}$.
  2. Label the individual data points with their metal symbols: `Co(ads)`, `Fe(ads)`, `Ni(ads)`, `Co(emb)`, `Fe(emb)`, `Ni(emb)`.

---

### Figure S6: Multilevel Thermodynamic Assessment & Caique Corrections (`figure/crcl3_caique_thermo_her_multipanel.pdf` / `.af`)
* **Source:** `ACS_version/ACS_resubmission/figure/crcl3_caique_thermo_her_multipanel.af` (Native Affinity Designer file!).
* **Panels:** (a) Caique vibrational $\Delta E_{\text{ZPE}}$ and $-T\Delta S$ bar charts; (b) Free energy comparison (PBE vs PBE+D3 vs PBE+D3+$U$); (c) Free energy profile landscape.
* **Manual Edits Needed in Affinity Designer:**
  1. **Ni$_{\text{emb}}$ Converged Value Update in Panel (b):**
     - Select the green bar for `Ni(emb)` under the `PBE+D3+U` group.
     - Update the numerical text label above the bar from `+0.855 eV` to:
       $$+0.821\text{ eV}$$
     - Adjust bar height slightly downward to reflect $+0.821\text{ eV}$ (was intermediate $+0.855\text{ eV}$).
  2. **Panel (a) Caique Corrections Verification:**
     - Verify that each bar matches co-author Caique Campos de Oliveira's exact phonon calculations:
       - Pristine: $+0.21\text{ eV}$
       - Co(ads): $+0.24\text{ eV}$ ($\Delta E_{\text{ZPE}} = +0.05$, $-T\Delta S = +0.19$)
       - Fe(ads): $+0.18\text{ eV}$ ($\Delta E_{\text{ZPE}} = +0.01$, $-T\Delta S = +0.17$)
       - Ni(ads): $+0.19\text{ eV}$ ($\Delta E_{\text{ZPE}} = +0.02$, $-T\Delta S = +0.17$)
       - Co(emb): $+0.26\text{ eV}$
       - Fe(emb): $+0.26\text{ eV}$
       - Ni(emb): $+0.20\text{ eV}$
  3. **Panel (c) Volmer Step Landscape:**
     - Verify the thermoneutral baseline at $\Delta G = 0\text{ eV}$ (dashed black line).
     - Verify the Pt(111) reference level at $-0.09\text{ eV}$ (dashed gray line).
     - Ensure Co(ads) under PBE+D3+$U$ is prominently drawn at **$-0.069\text{ eV}$**, showing near-zero activation overpotential ($\eta = 0.069\text{ V}$).

---

## 4. Step-by-Step Inkscape & Affinity Designer Workflow

### Affinity Designer Pro-Tips
1. **Layer Hierarchy:** Structure every multi-panel figure into 4 distinct vector layers:
   ```
   [Top Layer]    Panel Tags (a, b, c) & Annotations
   [Mid Layer 2]  Smart Bounding Cards & White Masks (Opacity: 92%, Blur: 0)
   [Mid Layer 1]  Callout Arrows, Leader Lines & Dimension Brackets
   [Base Layer]   Raw Matplotlib / VESTA Plot Vectors or High-Res Bitmaps
   ```
2. **Text to Paths Safeguard:** Before exporting the final publication PDF, duplicate the text layer and apply **Layer $\to$ Convert to Curves** (Affinity) or **Path $\to$ Object to Path** (Inkscape). This prevents any font substitution issues on the publisher's automated submission servers.
3. **Exporting for ACS Submissions:**
   - **Vector:** File $\to$ Export $\to$ PDF (Preset: `PDF/X-1a:2001` or `PDF 1.5`, rasterize unsupported effects at $600\text{ DPI}$).
   - **High-Res Raster:** File $\to$ Export $\to$ TIFF or PNG (Resolution: $600\text{ DPI}$, Color Space: `sRGB IEC61966-2.1`).

---

## 5. Summary Matrix of Required Manual Figure Actions

| Figure | Primary File | Software | Reviewer / Science Driver | Core Action Required | Priority |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **TOC** | `toc.png` | Inkscape / Affinity | ACS Formatting | Resize to $8.25 \times 4.45\text{ cm}$; add volcano & reaction equation | High |
| **Fig 1** | `Fig1.png` | Inkscape / Affinity | R4/R6 Point 1 | Annotate PBE gap ($1.50\text{ eV}$) vs Exp./DFT+$U$ ($3.0\text{ eV}$) | Medium |
| **Fig 2** | `Fig2.png` | Inkscape / Affinity | R4/R6 Point 2 | Add white bounding cards on H-Cl ($3.42\text{ \AA}$) and H-Cr ($1.55\text{ \AA}$) distances | Medium |
| **Fig 3** | `Fig3.png` | Inkscape / Affinity | R4/R6 Point 7 | Annotate Ni hollow penetration dip; add substrate plane legend | Medium |
| **Fig 4** | `Fig4.png` | Inkscape / Affinity | **R4/R6 Point 9** | **Fix colorbar label to $\Delta Q\ (e)$; change Bader charges to $+0.77\ e$, $+0.94\ e$, $+0.59\ e$** | **CRITICAL** |
| **Fig 5** | `Fig5.png` | Inkscape / Affinity | R4/R6 Point 5 | Highlight localized TM-$3d$ in-gap states; add spin up/down labels | High |
| **Fig 6** | `Fig6.pdf` | Inkscape / Affinity | R4/R6 Point 10 | Verify bounding cards and alignment across panels (a)–(f) | Low (Done) |
| **Fig 7** | `Fig7.png` | Inkscape / Affinity | **R4/R6 Point 12** | **Unify legend from $G_{\text{ads}}$ to $\Delta G_{\text{H}^*}$; verify TM-H distances** | **CRITICAL** |
| **Fig 8** | `Fig8.png` | Inkscape / Affinity | **R4/R6 Point 1, 12, 16** | **Unify y-axis to $\Delta G_{\text{H}^*}$; overlay new DFT+U points (Co: $-0.069\text{ eV}$)** | **CRITICAL** |
| **Fig S3** | `Fig_SI_3.png` | Inkscape / Affinity | **R4/R6 Point 8** | **Annotate 300 K equilibration transient window to explain energy curve** | High |
| **Fig S6** | `crcl3_caique...af` | Affinity Designer | R4/R6 Point 4 & Telemetry | **Update Ni(emb) to $+0.821\text{ eV}$; verify Caique ZPE/entropy values** | High |
