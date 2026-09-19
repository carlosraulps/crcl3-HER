# Comprehensive Memory & Lessons Learned: $\text{CrCl}_3$ ($1\times 1$), DFT+$U$, & Reviewer Protocol

**Permanent Memory Document**  
**Synced to NotebookLM**: `DFT Documentation` (`ffe299da-ae89-4141-b480-09ce50c763c4`) — Source ID: `145c9820-aaa9-4ef8-88f1-d3b18c0f6eed`  
**Workspace Locations**:
- [`MEMORY_LESSONS_LEARNED.md`](file:///home/cr/cr-gd/google-drive/Proyectos/paper-adaptation/crcl3-newcals/crcl3-1x1/MEMORY_LESSONS_LEARNED.md)
- [`MEMORY_CRCL3_LESSONS.md`](file:///home/cr/cr-gd/google-drive/Proyectos/paper-adaptation/MEMORY_CRCL3_LESSONS.md)

---

## 1. Computational Physics & VASP Best Practices

### A. 2D Cell Relaxation (`ISIF = 3` vs. `ISIF = 2`)
- In VASP, unconstrained variable-cell relaxation (`ISIF = 3` or `vc-relax`) cannot be applied to 2D materials. Unconstrained out-of-plane stress ($\sigma_{zz} = 0$) causes the vacuum layer ($c \approx 17.67\text{ \AA}$) to collapse to zero.
- **Rule**: 2D materials strictly require **`ISIF = 2`** (fixed in-plane cell and fixed vacuum separation, relaxing internal ionic coordinates).

### B. Static Single-Point vs. Ionic Relaxation Benchmark
- **$U \le 3\text{ eV}$**: The electronic band gap is essentially independent of ionic relaxation ($|\Delta E_g| \le 14.4\text{ meV}$, well below $k_{\text{B}}T \approx 25.7\text{ meV}$).
- **$U \ge 4\text{ eV}$**: On-site Coulomb repulsion induces an inward octahedral relaxation of $\text{Cl}^-$ by $\sim 0.015\text{ \AA}$, lowering total energy by $20 - 59\text{ meV}$ and shifting $E_g$ by $54 - 150\text{ meV}$.
- **Strategy**: Ultra-minimal static runs provide rapid, high-fidelity screening ($4\times$ faster), while full ionic relaxation (`NSW = 100`) provides final publication-grade accuracy.

### C. Essential PAW Flags for Transition-Metal Halides
- **`LASPH = .TRUE.`**: Includes non-spherical gradient corrections inside PAW spheres, critical for $3d$ orbital energies.
- **`LMAXMIX = 4`**: Enables charge density mixing up to $l=4$ ($d$-orbitals), eliminating crystal-field splitting errors and preventing electronic SCF stalling in $\text{Cr}^{3+}$ ($3d^3$).

### D. Hardware Topology & Thread Pinning (Ryzen 9 5950X, 16 Cores)
- **Over-subscription Hazard**: Default `run_vasp` `-nt 2` across multiple SLURM jobs produces 64 compute threads on 16 physical cores, causing severe L3 cache thrashing (load average 67.8, step time 177.1 s).
- **Optimized Setting**: Setting `#SBATCH --exclusive` with `run_vasp -np 16 -nt 1` delivers an exclusive 1:1 hardware core mapping, stabilizing system load at 8.3 and achieving a **$26.7\times$ real-time speedup** (6.62 s per SCF step).

### E. In-Plane Lattice Parameter Optimization vs. Vacuum Preservation in 2D Slabs
- **$1\times 1$ Suite Behavior**: Because `ISIF = 2` was employed across `U_0` to `U_6`, the in-plane lattice parameter was locked at $a = b = 6.0485\text{ \AA}$ ($\Delta a = 0.0000\text{ \AA}$). Only internal ionic coordinates (Cl $z$-buckling and bond angles) relaxed.
- **Vacuum Stability**: Vacuum along $c$ was strictly fixed at $c = 17.6700\text{ \AA}$ ($\sigma_{zz} \approx 0\text{ kB}$), preventing spurious inter-slab interactions.
- **VASP 6.6.1 Constraints (NotebookLM & Code Audit)**: Standard VASP lacks any native INCAR tag to selectively relax $x,y$ while freezing $z$. `ISIF = 3` collapses the vacuum into 3D bulk, and `ISIF = 4` distorts the vacuum ratio. Equation of State (EOS) with `ISIF = 2` is the required standard.
- **Calibrated In-Plane Equilibrium Relation**: With direct VASP calibration ($d\sigma_{xx}/da = -40.08\text{ kB/\AA}$), the true zero-stress equilibrium lattice parameter is:
  $$a_0(U) = 5.979 + 0.0213 \times U\ \text{\AA}$$
- **Zero-Strain Match**: At $U = 3.25\text{ eV}$, $a_{\text{nom}} = 6.0485\text{ \AA}$ matches zero stress ($\sigma_{xx} \approx 0$). At $U = 4.0\text{ eV}$, $a_0 = 6.064\text{ \AA}$, in direct agreement with literature ($6.056\text{ \AA}$ [Webster 2018, Luo 2020]).
- **Supercell $2\times 2$ Guidance**: Use $a = 12.128\text{ \AA}$ ($2 \times 6.064\text{ \AA}$ at $U=4\text{ eV}$), $c \ge 20.0\text{ \AA}$, and dipole corrections (`LDIPOL = .TRUE.`, `IDIPOL = 3`, `DIPOL = 0.5 0.5 0.5`).

---

## 2. Resolving the Band Gap Controversy (Addressing Reviewer 4)

### A. The Core Reviewer Challenge
> *"The experimental band gap of $\text{CrCl}_3$ is $\sim 3\text{ eV}$, whereas conventional PBE gives $\sim 1.5\text{ eV}$."*

### B. The Physical Resolution (Pollini & Spinolo 1970)
Bulk $\text{CrCl}_3$ exhibits **two fundamentally distinct optical absorption regimes**:
1. **Sub-Gap Visible Absorption Onset ($\sim 1.5 - 1.7\text{ eV}$)**:
   - Originates from localized intra-ionic $3d \to 3d$ crystal-field transitions ($^4A_{2g} \to\ ^4T_{2g}$, peak at $1.68\text{ eV}$ at 300 K / $1.70\text{ eV}$ at 80 K).
   - Generates negligible photocurrent (charge transport occurs only via thermally activated polaron hopping).
   - Conventional PBE reproduces this feature ($1.50\text{ eV}$ this work; $1.58\text{ eV}$ Webster 2018; $1.59\text{ eV}$ Luo 2020; $1.6\text{ eV}$ Gao 2018).
2. **Fundamental Charge-Transfer Edge ($(3.2 \pm 0.2)\text{ eV}$)**:
   - Steep absorption edge ($\alpha \approx 10^4 - 10^5\text{ cm}^{-1}$) with a **two orders of magnitude ($100\times$) surge in photoconductivity yield**.
   - Confirms true free carrier transport across the fundamental band gap ($\text{Cl } 3p \to \text{Cr } 3d/4s$).

### C. The Physical Role of Hubbard $+U$
- Standard PBE underestimates Coulomb repulsion, misplacing occupied $\text{Cr } 3d$ states near the valence top.
- Applying on-site $+U$ ($U = 1 \dots 6\text{ eV}$) penalizes double occupancy on $\text{Cr } 3d$, pushing occupied $d$-levels below the $\text{Cl } 3p$ valence manifold (Gao et al. 2018).
- This converts the system from a Mott/crystal-field insulator into a **charge-transfer insulator**, widening the gap from $1.50\text{ eV}$ to $2.59\text{ eV}$ (relaxed) / $2.67\text{ eV}$ (static) and bridging the gap toward the $3.2\text{ eV}$ experimental edge.

---

## 3. Verified Citations & Literature Protocol

### A. Zero-Unverified-Overlay Mandate
- **Permanent Rule**: Never plot an external reference line or shaded band unless 100% verified against primary digital source text.
- If paywalled or unverified, omit the overlay from the plot and request the exact PDF.

### B. Professional Figure Citation Design
- **Journal Submissions**: Use clean, concise legend labels (e.g., `Monolayer PBE Lit. [2-4]`, `Bulk Charge-Transfer Edge [1]`) with formal LaTeX `\cite{...}` commands in the manuscript figure caption.
- **Reviewer Response Packages**: Use an elegant **Footnote Citation Banner** along the bottom margin of the canvas (`References: [1] ... [2] ... [3] ... [4] ...` on a light gray `#f8f9fa` box). This gives reviewers immediate verification without requiring cross-referencing.

---

## 4. Document Processing & Extraction Standards

### A. Two-Column Academic PDF Processing
- Standard PDF-to-Markdown tools (like Microsoft MarkItDown) mistake two-column layouts for table cells, introducing pipe characters (`| ... |`).
- Neural vision OCR (Baidu Unlimited-OCR) requires dedicated CUDA GPUs and is designed for scans; running vision OCR on digital vector PDFs introduces hallucination risks for sub/superscripts and Greek symbols.

### B. Gold Standard Three-Way Extraction
To guarantee 100% certainty:
1. **Poppler `pdftotext -layout`**: Preserves physical column alignment and ASCII spacing.
2. **Python `pymupdf`**: Extracts continuous semantic text streams for clean reading.
3. **Clean Markdown Sanitization (`*_clean.md`)**: Converts clean text streams into readable narrative Markdown with proper headers and blockquotes.

---

## 5. Directory & Package Standards

- Standardize strictly on canonical spelling: **`vdw`** and **`crcl3`** (never `dvw` or `crlc3`).
- Rebuild distribution archives with complete provenance:
  - `relaxed-crcl3-vdw-u.zip`: Complete relaxed suite (114 files), scripts, figures, `REFERENCES_ANALYSIS.md`, and clean literature extractions.
  - `ultraminimal-crcl3-vdw-u.zip`: Reproduction benchmark archive (61 files).
