import re

with open('manuscript_marked.tex', 'r') as f:
    manuscript = f.read()

def extract_revcolor_blocks(text):
    blocks = []
    idx = 0
    while True:
        idx = text.find(r'{\color{revcolor}', idx)
        if idx == -1:
            break
        
        brace_count = 0
        start = idx
        for i in range(idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    blocks.append(text[start+17:i]) # Extract text inside {\color{revcolor}...}
                    idx = i + 1
                    break
    return blocks

blocks = extract_revcolor_blocks(manuscript)

with open('Response_letter_clean.tex', 'r') as f:
    resp = f.read()

def replacer(match):
    return match.group(0)

# 1. R1C2 - Selection of Co, Fe, Ni (Block 0)
resp = resp.replace(r'\manuscriptchange{A comprehensive physical rationalization has been added to Section~3.2 (highlighted in blue in the marked manuscript), providing the Goodenough--Kanamori--Anderson super-exchange arguments for each metal.}',
r'\manuscriptchange{A comprehensive physical rationalization has been added to Section~3.2 (highlighted in blue in the marked manuscript):' + '\n\\begin{addedtext}\n' + blocks[0].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')

# 2. R1C5 - Hubbard U (Block 3)
resp = resp.replace(r'\manuscriptchange{A new paragraph has been added to Section~2 (highlighted in blue): ``\textit{The plain PBE functional was used without a Hubbard $U$ correction. It is well established that PBE underestimates the band gap of CrCl$_3$ (calculated: $\sim$1.50~eV; experimental optical gap: $\sim$3~eV). This limitation affects the absolute position of the in-gap TM-derived states and the local Cr moments, but does not alter the qualitative relative trends in binding energy, $d$-band center, and $\Delta G_{\mathrm{ads}}$ across the three metals and two coordination motifs, which are governed primarily by TM-$3d$ valence-electron count, TM--Cl covalent overlap, and TM--H orbital hybridization\ldots A DFT$+U$ benchmark for Cr-$3d$ ($U_{\mathrm{Cr}} \approx 2$--3~eV) is identified as a future validation.}''}',
r'\manuscriptchange{A new paragraph has been added to Section~2 (highlighted in blue):' + '\n\\begin{addedtext}\n' + blocks[3].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')

# 3. R1C6 - vdW correction (Block 4)
resp = resp.replace(r'\manuscriptchange{An explicit statement has been added to Section~2 (highlighted in blue): ``\textit{No van der Waals (dispersion) correction was applied. The dominant TM--CrCl$_3$ and TM--H interactions are covalent, as confirmed by the TM--Cl ICOHP values ($-6.7$ to $-11.4$~eV) and the TM--H bond lengths (1.43--1.57~\AA). Dispersion corrections (e.g., DFT-D3) would contribute approximately 0.1--0.4~eV to TM binding energies -- insufficient to alter the metal ranking\ldots}''}',
r'\manuscriptchange{An explicit statement has been added to Section~2 (highlighted in blue):' + '\n\\begin{addedtext}\n' + blocks[4].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')

# 4. R1C8 - Cohesive energies (Block 8)
resp = resp.replace(r'\manuscriptchange{A new paragraph has been added to Section~3.2 (highlighted in blue): ``\textit{Comparing $|E_{\mathrm{bind}}|$ to the PBE cohesive energies of the bulk metals (Co: 4.39~eV/atom; Fe: 4.28~eV/atom; Ni: 4.44~eV/atom) reveals that only embedded Ni ($|E_{\mathrm{bind}}| = 4.95$~eV) is thermodynamically stable against bulk-metal formation\ldots In practice, isolated Co and Fe surface sites are kinetically stabilized by the energy barrier required to migrate through the constrained CrCl$_3$ hollow region.}''}',
r'\manuscriptchange{A new paragraph has been added to Section~3.2 (highlighted in blue):' + '\n\\begin{addedtext}\n' + blocks[8].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')

# 5. R2C2 - Semiconducting nature (Block 11)
resp = resp.replace(r'\manuscriptchange{A new paragraph has been added to Section~3.3 (highlighted in blue): ``\textit{The semiconducting nature of pristine CrCl$_3$ (PBE gap $\sim$1.50~eV; experimental gap $\sim$3~eV) is a practical consideration for electrocatalytic applications. The TM-derived in-gap states shown in Figure~5 are weakly dispersive and spatially localized around the functionalizing center, and they do not form a percolating conduction channel\ldots Practical implementation would therefore require a conducting support electrode.}''}',
r'\manuscriptchange{A new paragraph has been added to Section~3.3 (highlighted in blue):' + '\n\\begin{addedtext}\n' + blocks[11].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')

# 6. R2C5 - AIMD parameters (Block 6)
resp = resp.replace(r'\manuscriptchange{All AIMD computational details have been added to Section~2 (highlighted in blue): ``\textit{The Nosé--Hoover chain was used with the default VASP coupling parameter (SMASS~$=0$). The Brillouin zone was sampled at the $\Gamma$ point only during the dynamics. The electronic self-consistency criterion during the AIMD was set to $10^{-5}$~eV. The first 0.5~ps of each trajectory was treated as equilibration\ldots Single trajectories per metal were used, consistent with the standard approach for exploratory AIMD studies of adatoms on 2D materials; multiple independent seeds are identified as a future validation.}''}',
r'\manuscriptchange{All AIMD computational details have been added to Section~2 (highlighted in blue):' + '\n\\begin{addedtext}\n' + blocks[6].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')

# 7. R2C7 - Charge transfer (Block 9)
resp = resp.replace(r'\manuscriptchange{The text in Section~3.2 has been corrected (highlighted in blue): ``\textit{The TM atoms act as electron donors: Co, Fe, and Ni each transfer electrons to the CrCl$_3$ substrate, with Bader-integrated charge transfers of $\Delta Q = 0.77$, $0.94$, and $0.59~e$, respectively.}'' The Figure~4(d--f) color-bar label has been corrected from ``$\Delta|Q_e|$'' to ``$\Delta Q\,(e)$'' with a signed convention.}',
r'\manuscriptchange{The text in Section~3.2 has been corrected (highlighted in blue):' + '\n\\begin{addedtext}\n' + blocks[9].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}\n\nThe Figure~4(d--f) color-bar label has been corrected from ``$\\Delta|Q_e|$'' to ``$\\Delta Q\\,(e)$'' with a signed convention.}')

# 8. R3C3 - Static and dynamical calculations regimes (Block 10)
resp = resp.replace(r'\manuscriptchange{An explicit paragraph distinguishing thermodynamic preference from kinetic accessibility has been added to Section~3.2 (highlighted in blue): ``\textit{The static and dynamical calculations therefore identify two regimes. Co and Fe form locally anchored centers that remain predominantly surface exposed over 5~ps, whereas Ni displays stronger substrate coupling and a rapid tendency toward deeper incorporation. The trajectories reveal short-time structural accessibility but do not determine long-time diffusion kinetics, incorporation barriers, or equilibrium populations of the two coordination motifs.}''}',
r'\manuscriptchange{An explicit paragraph distinguishing thermodynamic preference from kinetic accessibility has been added to Section~3.2 (highlighted in blue):' + '\n\\begin{addedtext}\n' + blocks[10].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')

# 9. R4C1 - Conclusions additions (Block 14)
resp = resp.replace(r'\manuscriptchange{A statement has been added to the Conclusions (Section~4, highlighted in blue): ``\textit{\ldots the calculations are performed for an ideal neutral monolayer in vacuum; solvation, applied potential, electrolyte effects, and surface reconstruction under realistic electrochemical conditions may shift the absolute $\Delta G_{\mathrm{ads}}$ values, and their inclusion via implicit-solvent or constant-potential DFT methods is identified as a further extension.}''}',
r'\manuscriptchange{A statement has been added to the Conclusions (Section~4, highlighted in blue):' + '\n\\begin{addedtext}\n' + blocks[14].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')

# 10. R4C2 - Data availability (Block 15)
resp = resp.replace(r'\manuscriptchange{The Data Availability section has been updated (highlighted in blue): ``\textit{The optimized atomic structures (POSCAR files) for all seven configurations (pristine monolayer CrCl$_3$, and surface-adsorbed and embedded Co, Fe, and Ni) are provided in the Supporting Information. OUTCAR energy and magnetic-moment summaries, LOBSTER COHPCAR files, and AIMD XDATCAR trajectories will be deposited in a public repository upon acceptance; the DOI will be provided in the final published version.}''}',
r'\manuscriptchange{The Data Availability section has been updated (highlighted in blue):' + '\n\\begin{addedtext}\n' + blocks[15].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')

# 11. R4C10 - Ni moment (Block 13)
resp = resp.replace(r'\manuscriptchange{This analysis has been added to Section~3.2 (highlighted in blue in the marked manuscript).}',
r'\manuscriptchange{This analysis has been added to Section~3.2 (highlighted in blue in the marked manuscript):' + '\n\\begin{addedtext}\n' + blocks[13].strip().replace(r'\par', '\n\n') + '\n\\end{addedtext}}')


# Write back
with open('Response_letter_clean.tex', 'w') as f:
    f.write(resp)

print("Modifications applied.")
