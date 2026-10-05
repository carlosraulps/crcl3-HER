# 5-Minute Oral Presentation Script: Coordination-Dependent Hydrogen Adsorption on Functionalized Monolayer $\text{CrCl}_3$

**Presenter:** Carlos R. Primo Sapillado  
**Affiliations:** Center for Natural and Human Sciences (CCNH), Universidade Federal do ABC (UFABC), Brazil $\,\vert\,$ Facultad de Ciencias Físicas, Universidad Nacional Mayor de San Marcos (UNMSM), Peru  
**Corresponding Author:** Pedro A. S. Autreto (`pedro.autreto@ufabc.edu.br`)  
**Target Duration:** Exactly 5:00 minutes (300 seconds)  
**Tone & Pacing:** Fast, energetic, mathematically grounded, concise (~130–140 words/min).

---

## Timing Overview & Slide Budget

| Slide | Subject | Timing | Cumulative Time | Visual Anchor |
| :---: | :--- | :---: | :---: | :--- |
| **1** | Title & Presenter Introduction | 0:25 | 0:00 – 0:25 | Framed UFABC badge, authorship |
| **2** | Motivation: Acidic HER & Active-Site Dilemma | 0:25 | 0:25 – 0:50 | `toc.png`, Sabatier equation |
| **3** | Methodology & Energy Partitioning | 0:25 | 0:50 – 1:15 | Hubbard $U^*$, CHE, distortion decomposition |
| **4** | Pristine Monolayer $\text{CrCl}_3$: Inert Basal Plane | 0:25 | 1:15 – 1:40 | `Fig1.png` (honeycomb, bands, inert sites) |
| **5** | Coordination Motifs & AIMD Kinetic Trapping | 0:25 | 1:40 – 2:05 | `Fig3.png` (3-fold vs 6-fold, 300 K trajectories) |
| **6** | Charge Transfer & In-Gap Electronic States | 0:25 | 2:05 – 2:30 | `Fig4.png` ($\Delta\rho$ isosurfaces, spin channels) |
| **7** | Chemical Bonding & The Coordination Trade-Off | 0:25 | 2:30 – 2:55 | `Fig6.png` (-COHP curves, ICOHP integration) |
| **8** | Hydrogen Adsorption & Sabatier Optimum | 0:30 | 2:55 – 3:25 | `Fig7.png` ($\Delta G_{\text{H}^*}$ profiles, Pt(111) comparison) |
| **9** | Descriptor Breakdown & Spin Coupling | 0:30 | 3:25 – 3:55 | `new_mu_vs_dG.png` ($\varepsilon_d^{\text{occ}}$ plot, spin quenching) |
| **10** | Master Benchmark Table & Design Principles | 0:25 | 3:55 – 4:20 | Comprehensive DFT table ($\eta = 69$~mV) |
| **11** | References & Funding Acknowledgments | 0:20 | 4:20 – 4:40 | Nørskov, FAPESP, CAPES, CNPq, UNMSM |
| **12** | Summary Triad & Open Discussion | 0:20 | 4:40 – 5:00 | Three takeaway cards, contact info |

---

## Detailed Slide-by-Slide Script

### Slide 1: Title & Author Introduction

- **Time:** `0:00 – 0:25` (25 seconds)
- **Visual Focus:** Title header, Presenter name (**Carlos R. Primo Sapillado**), UFABC & UNMSM institutions.
- **Presenter Spoken Script:**
  > Well!
  > Today, I present our work on **coordination-dependent hydrogen adsorption on single transition-metal functionalized monolayer chromium trichloride**, revealing the physical interplay between spin polarization, local coordination trade-offs, and near-zero overpotential electrocatalysis for the hydrogen evolution reaction."
- **Transition:** *"Let us start by looking at the fundamental challenge in clean hydrogen production..."*

---

### Slide 2: Motivation & The Active-Site Dilemma

- **Time:** `0:25 – 0:50` (25 seconds)
- **Visual Focus:** HER reaction equation $\eta = |\Delta G_{\text{H}^*}|/e$, Pt(111) benchmark ($-0.090$~eV), and `toc.png` graphic.
- **Presenter Spoken Script:**
  > "In acidic water electrolysis, the cathodic half-reaction—the Hydrogen Evolution Reaction—reaches maximum catalytic turnover when the intermediate hydrogen adsorption free energy $\Delta G_{\text{H}^*}$ approaches zero, known as the **Sabatier optimum**. While benchmark platinum terrace achieves minus 90 millielectronvolts, its high cost demands Earth-abundant 2D alternatives.
  >
  > Here, monolayer chromium trichloride provides an ideal 2D magnetic semiconductor platform with an intrinsic ferromagnetic ground state. However, its fully saturated chlorine basal plane creates an **active-site dilemma**: the surface is completely inert. Overcoming this requires engineering single-atom transition metal centers."
- **Transition:** *"To address this , we use a theoretical computational framework..."*

---

### Slide 3: Computational Methodology & Energy Partitioning

- **Time:** `0:50 – 1:15` (25 seconds)
- **Visual Focus:** Dudarev $U^* = 3.29$~eV calibration, CHE equation, and the distortion-interaction decomposition $\Delta E_{\text{ads}} = E_{\text{int}} + E_{\text{def}}$.
- **Presenter Spoken Script:**
  > "We performed spin-polarized density functional theory using VASP with PAW pseudopotentials on a $2\times 2\times 1$ supercell. To accurately capture strong on-site electron correlation on the Cr $3d$ electronic structure, we applied Dudarev's Hubbard $U$ formalism with $U^* = 3.29$~eV, strictly calibrated to reproduce the experimental optical gap of $2.56$~eV and linear response values, combined with Grimme D3 van der Waals corrections.
  >
  > Thermochemistry was evaluated via Nørskov’s Computational Hydrogen Electrode with explicit phononics from finite differences. Crucially, we decoupled total binding into intrinsic interaction affinity $E_{\text{int}}$ and host lattice distortion strain $E_{\text{def}}$."
- **Transition:** *"First, let us examine the baseline pristine surface..."*

---

### Slide 4: Pristine Monolayer $\text{CrCl}_3$: Structure & Catalytic Inertness

- **Time:** `1:15 – 1:40` (25 seconds)
- **Visual Focus:** `Fig1.png` panels: honeycomb structure (a,b), spin-polarized band structure with $2.56$~eV gap (c,d), and the three candidate adsorption sites ($S_1, S_2, S_3$).
- **Presenter Spoken Script:**
  > "Pristine monolayer $\text{CrCl}_3$ adopts a honeycomb structure of edge-sharing $\text{CrCl}_6$ octahedra, featuring a robust ferromagnetic state with $3$ Bohr magnetons per formula unit and a direct band gap of $2.56$~eV under PBE+$U$.
  >
  > When probing hydrogen chemisorption on pristine sites, top-chlorine $S_1$ spontaneously expels hydrogen to over $3.4$ angstroms, the hollow site $S_2$ is geometrically unstable, and top-chromium $S_3$ yields a severely endergonic $\Delta G_{\text{H}^*}$ of **plus $2.44$~eV**, requiring a prohibitive $2.44$~V overpotential. The pristine basal plane is utterly dead for catalysis."
- **Transition:** *"To activate it, we functionalized the surface with isolated cobalt, iron, and nickel single atoms..."*

---

### Slide 5: Coordination Motifs & AIMD Kinetic Trapping

- **Time:** `1:40 – 2:05` (25 seconds)
- **Visual Focus:** `Fig3.png`: surface 3-fold hollow vs. embedded 6-fold pore geometry, and 300 K AIMD vertical height trajectories $z(t)$.
- **Presenter Spoken Script:**
  > "Two distinct structural motifs emerge: an exposed **3-fold surface hollow** where the metal sits roughly $1.5$ to $1.9$ angstroms above the surface, and an **embedded 6-fold octahedral pore** where the atom sinks into the layer core.
  >
  > Thermodynamically, deep embedding provides strong binding up to minus $4.95$~eV. However, our 5-picosecond AIMD simulations at room temperature demonstrate that **cobalt and iron remain kinetically trapped in the exposed surface state**, protected by steric Cl diffusion barriers, whereas nickel rapidly sinks within 1 picosecond."
- **Transition:** *"How does this local coordination affect electronic structure and charge transfer? Let us look at Slide 6..."*

---

### Slide 6: Charge Redistribution & In-Gap Electronic States

- **Time:** `2:05 – 2:30` (25 seconds)
- **Visual Focus:** `Fig4.png`: Charge density difference isosurfaces $\Delta\rho(\mathbf{r})$ and Bader charge transfers for Fe, Co, and Ni.
- **Presenter Spoken Script:**
  > "Charge density difference and Bader analysis demonstrate that all three transition metals act as net electron donors to the chlorinated substrate. Iron transfers nearly one full electron, cobalt transfers $0.77$, and nickel $0.59$ electrons. Fe and Co align ferromagnetically with the chromium lattice, while nickel couples antiferromagnetically.
  >
  > Electronically, the 3-fold surface adatoms introduce sharp, spin-polarized TM-$3d$ in-gap states right at the Fermi level, creating accessible frontier orbitals for proton reception. In contrast, 6-fold pore embedding shifts these states deep into the valence band, completely depopulating the Fermi level."
- **Transition:** *"This distinction is governed by chemical bonding, as revealed by COHP analysis..."*

---

### Slide 7: Chemical Bonding & The Coordination Trade-Off

- **Time:** `2:30 – 2:55` (25 seconds)
- **Visual Focus:** `Fig6.png`: Crystal Orbital Hamilton Population (-COHP) curves and cumulative bonding integrals.
- **Presenter Spoken Script:**
  > "By computing the Crystal Orbital Hamilton Population, we uncover the **coordination trade-off principle**. In the 3-fold surface state, individual metal-chlorine bonds are exceptionally strong, with average integrated values of minus $2.23$~eV for cobalt and minus $2.28$~eV for iron.
  >
  > In the 6-fold embedded state, individual bonds weaken to minus $1.87$~eV, but the higher coordination number yields an enormous cumulative bonding energy of minus $11.4$~eV. This proves that high thermodynamic host anchoring does not equate to catalytic excellence—deep coordination electronically passivates the metal center toward incoming reactants."
- **Transition:** *"Now let us observe the resulting electrocatalytic hydrogen evolution performance..."*

---

### Slide 8: Hydrogen Adsorption Thermodynamics: Sabatier Optimum

- **Time:** `2:55 – 3:25` (30 seconds)
- **Visual Focus:** `Fig7.png`: Adsorption geometries, distortion-interaction bar charts, and free energy profiles $\Delta G_{\text{H}^*}$.
- **Presenter Spoken Script:**
  > "Evaluating full vibrational free energy under operating conditions reveals our primary breakthrough: **surface-adsorbed cobalt lands precisely at the Sabatier sweet spot**, exhibiting:
  > $$\Delta G_{\text{H}^*} = \mathbf{-0.069\text{ eV}}$$
  > corresponding to an ultra-low overpotential of only **$69$~millivolts—outperforming pristine platinum terrace** at minus $90$~millivolts!
  >
  > Surface iron also performs favorably with an overpotential of $185$~millivolts. All embedded motifs, however, suffer overpotentials exceeding $820$~millivolts. Our distortion-interaction analysis explains why: Co(ads) combines strong intrinsic binding of minus $2.46$~eV with minimal substrate deformation of only $0.18$~eV, whereas iron incurs double the distortion penalty."
- **Transition:** *"Can traditional catalytic descriptors capture this behavior? Direct your attention to Slide 9..."*

---

### Slide 9: Descriptor Breakdown & Spin Coupling

- **Time:** `3:25 – 3:55` (30 seconds)
- **Visual Focus:** Centerpiece figure `new_mu_vs_dG.png` showing $\Delta G_{\text{H}^*}$ plotted against the occupied $d$-band center $\varepsilon_d^{\text{occ}}$.
- **Presenter Spoken Script:**
  > "In traditional heterogeneous catalysis, Hammer and Nørskov’s $d$-band center model predicts that higher occupied centroids correlate monotonically with stronger adsorption. As plotted here in Figure 9, this single-variable descriptor completely breaks down ($R^2 \le 0.28$).
  >
  > Notice the striking anomalies: surface nickel has the highest $d$-band center closest to Fermi at minus $1.15$~eV, yet exhibits the worst surface activity; while embedded iron has the deepest centroid, yet achieves the lowest embedded free energy!
  >
  > Single-variable scaling fails because strong exchange splitting separates spin channels, and local ligand-field coordination dominates. Crucially, hydrogen chemisorption systematically quenches the local cobalt magnetic moment from plus $1.99$ to $1.01$ Bohr magnetons, directly confirming that spin channels actively participate in proton-electron transfer."
- **Transition:** *"Let us synthesize these results into our master benchmark..."*

---

### Slide 10: Master Benchmark Table & Design Principles

- **Time:** `3:55 – 4:20` (25 seconds)
- **Visual Focus:** Slide 10 comprehensive comparison table, highlighting the bold green row for $\text{CrCl}_3$--Co (ads) and the design guidelines.
- **Presenter Spoken Script:**
  > "Here in our master benchmark table, we compare all nine configurations against Pt(111). Surface Co achieves the lowest overpotential of $0.069$~V, while delivering high magnetic moment and robust charge donation.
  >
  > From these insights, we extract two foundational catalyst design principles:
  > First, **kinetic trapping of under-coordinated surface states** preserves reactive in-gap orbitals.
  > Second, coupling functionalized $\text{CrCl}_3$ monolayers with conductive carbon substrates will bypass semiconductor host resistance, enabling rapid interfacial charge transport in industrial electrolyzers."
- **Transition:** *"Before concluding, I wish to express our gratitude..."*

---

### Slide 11: References & Institutional Acknowledgments

- **Time:** `4:20 – 4:40` (20 seconds)
- **Visual Focus:** Citations (Nørskov, Webster, Quispe/Primo 2026) and funding agency logos/credits (FAPESP, CAPES, CNPq, UNMSM, PROCIENCIA).
- **Presenter Spoken Script:**
  > "We acknowledge fundamental works by Nørskov and collaborators on electrochemical free energy, and Webster on $\text{CrCl}_3$ electronic properties.
  >
  > We gratefully acknowledge financial support from FAPESP, CAPES, CNPq, and the National University of San Marcos in Peru, as well as the high-performance supercomputing facilities at the UFABC Multiuser Center and LMSC-GMCAN laboratory."
- **Transition:** *"To summarize our key conclusions..."*

---

### Slide 12: Summary Triad & Open Discussion

- **Time:** `4:40 – 5:00` (20 seconds)
- **Visual Focus:** Three conclusion cards (Sabatier Champion, Coordination Trade-Off, Spin-Coupled HER), presenter email, and discussion invitation.
- **Presenter Spoken Script:**
  > "To conclude:
  > 1. Single cobalt adatoms on monolayer $\text{CrCl}_3$ achieve a record overpotential of **$69$~millivolts**, outperforming platinum.
  > 2. The **coordination trade-off** dictates that under-coordinated surface sites preserve catalytic activity, whereas deep interstitial embedding passivates the center.
  > 3. Spin-moment quenching proves direct **spin-catalysis coupling**, opening new avenues for 2D spintronic electrocatalysts.
  >
  > Thank you for your attention. I am now open to your questions and discussion."

---

## Speaker Quick Cue Card (Pocket Reference)

| Minute | Slide | Cue Keywords | Must-Say Key Values |
| :---: | :---: | :--- | :--- |
| **0:00** | 1 | Intro & Title | Carlos R. Primo S., UFABC, UNMSM, spin-coordination |
| **0:25** | 2 | Motivation | Sabatier sweet spot, $\text{CrCl}_3$ 2D magnet, Pt benchmark ($-0.090$~eV) |
| **0:50** | 3 | Method | Dudarev $U^* = 3.29$~eV, CHE phononics, distortion-interaction $E_{\text{def}}$ |
| **1:15** | 4 | Pristine | FM $3\,\mu_{\text{B}}/\text{f.u.}$, $2.56$~eV gap, basal plane dead ($\mathbf{+2.44\text{ eV}}$) |
| **1:40** | 5 | Motifs & AIMD | 3-fold surface vs 6-fold pore; Co/Fe trapped at 300 K; Ni sinks |
| **2:05** | 6 | Charge & DOS | Electron donors ($\Delta Q > 0$), in-gap Fermi states vs deep pore states |
| **2:30** | 7 | -COHP Trade-Off | Strong individual bonds ($-2.23$~eV) vs cumulative coordination ($-11.4$~eV) |
| **2:55** | 8 | Sabatier Peak | **Co(ads) $\mathbf{\Delta G_{\text{H}^*} = -0.069\text{ eV}}$ ($\mathbf{69\text{ mV}}$)**, beats Pt(111) |
| **3:25** | 9 | Descriptor | $d$-band breakdown ($R^2 \le 0.28$), Ni/Fe anomalies, Co spin quenching ($\Delta\mu = -0.98$) |
| **3:55** | 10 | Master Benchmark | 9 sites vs Pt, kinetic trapping, conductive carbon support coupling |
| **4:20** | 11 | References | Nørskov, Webster, FAPESP, CAPES, CNPq, UNMSM, PROCIENCIA |
| **4:40** | 12 | Summary & Q&A | Champion Co ($69$~mV), coordination trade-off, spin-coupled HER |
