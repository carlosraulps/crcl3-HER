# CrCl₃ Hydrogen Adsorption Structures (Initial & Optimized)

This directory contains standardized `.vasp` POSCAR/CONTCAR structure files for hydrogen adsorption on monolayer $\text{CrCl}_3$ across multi-scale supercell dimensions ($3\times3$, $2\times2$, and $1\times1$), comparing both Pure PBE (`no_vdw`) and PBE+D3 (`yes_vdw`).

All files are directly compatible with visualization and modeling packages (**VESTA**, **OVITO**, **ASE**, **pymatgen**, **XCrySDen**).

---

## 1. Directory Layout & File Naming Convention

```
structures_vasp/
├── 3x3/
│   ├── no_vdw/
│   │   ├── crcl3_3x3_no_vdw_clean_pristine_initial.vasp
│   │   ├── crcl3_3x3_no_vdw_clean_pristine_optimized.vasp
│   │   ├── crcl3_3x3_no_vdw_S1_top_Cl_initial.vasp
│   │   ├── crcl3_3x3_no_vdw_S1_top_Cl_optimized.vasp
│   │   ├── crcl3_3x3_no_vdw_S2_hollow_initial.vasp
│   │   ├── crcl3_3x3_no_vdw_S2_hollow_optimized.vasp
│   │   ├── crcl3_3x3_no_vdw_S3_top_Cr_initial.vasp
│   │   └── crcl3_3x3_no_vdw_S3_top_Cr_optimized.vasp
│   └── yes_vdw/
│       ├── crcl3_3x3_yes_vdw_clean_pristine_initial.vasp
│       ├── crcl3_3x3_yes_vdw_clean_pristine_optimized.vasp
│       ├── crcl3_3x3_yes_vdw_S1_top_Cl_initial.vasp
│       ├── crcl3_3x3_yes_vdw_S1_top_Cl_optimized.vasp
│       ├── crcl3_3x3_yes_vdw_S2_hollow_initial.vasp
│       ├── crcl3_3x3_yes_vdw_S2_hollow_optimized.vasp
│       ├── crcl3_3x3_yes_vdw_S3_top_Cr_initial.vasp
│       └── crcl3_3x3_yes_vdw_S3_top_Cr_optimized.vasp
├── 2x2/
│   ├── no_vdw/ ...
│   └── yes_vdw/ ...
└── 1x1/
    ├── no_vdw/ ...
    └── yes_vdw/ ...
```

**Naming Template:**  
`crcl3_{SCALE}_{VARIANT}_{SITE}_{DESCRIPTION}_{STATE}.vasp`
- `{SCALE}`: `3x3` ($a = 18.14$ Å, $\theta = 0.11$, 73 atoms), `2x2` ($a = 12.09$ Å, $\theta = 0.25$, 33 atoms), or `1x1` ($a = 6.05$ Å, $\theta = 1.00$, 9 atoms)
- `{VARIANT}`: `no_vdw` (Pure PBE) or `yes_vdw` (PBE + Grimme DFT-D3)
- `{SITE}`: `S1` (Top-Cl), `S2` (Hollow), `S3` (Top-Cr), or `clean` (Pristine slab)
- `{STATE}`: `initial` (unrelaxed input POSCAR) or `optimized` (DFT-relaxed CONTCAR)

---

## 2. Adsorption Site Key Coordinates & Geometries ($3\times3$ Supercell)

| Site | Target Atom | Initial $d(\text{H-Target})$ | Relaxed $d(\text{H-Target})$ | Out-of-Plane Shift $\Delta z$ | Adsorption Character |
|:---|:---|:---:|:---:|:---:|:---|
| **$S_1$ (Top-Cl)** | $\text{Cl}_{41}$ (top layer) | $1.300$ Å | **$1.291$ Å** | $+0.541 - +0.874$ Å | Covalent chemisorption |
| **$S_2$ (Hollow)** | Center of Cr ring | $1.600$ Å above Cr | $2.120 - 2.188$ Å (to nearest Cl) | $-0.172 - +0.262$ Å | Unfavorable void state |
| **$S_3$ (Top-Cr)** | $\text{Cr}_7$ (metal cation) | $1.550$ Å | **$1.546 - 1.550$ Å** | $+1.546 - +1.550$ Å | Robust localized chemisorption |
| **Clean** | Pristine 3x3 substrate | — | Fully relaxed (72 atoms) | — | Substrate reference |

---

## 3. Substrate Restructuring Highlights

- **Site $S_1$:** The coordinated chlorine ligand pulls outward into vacuum. In the diluted $3\times3$ limit ($\theta = 0.11$), lateral repulsion is minimal, yielding strong thermodynamic stabilization ($\Delta E = -2.11$ eV).
- **Site $S_3$:** The $\text{Cr}$ cation forms a directional, localized $\text{Cr-H}$ bond with $d(\text{Cr-H}) \approx 1.55$ Å, virtually invariant across $1\times1$, $2\times2$, and $3\times3$ supercells ($\Delta E \approx -1.75$ to $-1.78$ eV).
