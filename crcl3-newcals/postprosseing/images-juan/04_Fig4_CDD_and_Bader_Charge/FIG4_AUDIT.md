# Figure 4 panels a–c: calculation and rendering audit

Audited 29 October 2026. Scope: Co (a), Fe (b), Ni (c), both Hubbard-U treatments.

The original PDFs combine materially different calculation geometries with inconsistent postprocessing provenance. Their visual differences cannot be fixed reliably by resizing or removing selected charge-density lobes. Separate normalized review copies use corrected frozen-reference Fe/Ni CDD files and the same physical isovalue, view, atom colors, opacity and unit-cell scale. The originals are preserved.

## Calculation status and source structures

| Panel / treatment | Existing output and verification | Geometry traced from local CDD header |
|---|---|---|
| Co / +UCr | Complete density grid and Bader output available. Original three SCF OUTCARs are absent locally; their convergence was not independently verified in this audit. | Same geometry as `crcl3-newcals/crcl3-2x2-Co-S2-U_all3.29/01_relax/CONTCAR`. |
| Co / +Uall | Relaxation and both reference jobs have normal completion and electronic-convergence markers. Reference coordinates match the complex to <1e-12 Å. Raw constituent CHGCARs are absent locally, so direct subtraction was not repeated. | Same Co S2 geometry as +UCr. |
| Fe / +UCr | Corrected frozen-slab job completed and electronically converged on Arch. Exact cell, FFT grid, frozen substrate positions and isolated-metal position verified against the archived constituent densities. | Exact match to `crcl3-newcals/crcl3-2x2-fe_ads-with-U/yes_vdw/S1/CONTCAR`, not a verified surface S2 calculation. |
| Fe / +Uall | Corrected frozen-slab job completed and electronically converged; the same constituent-density checks pass. | Exact match to `crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Fe/clean/CONTCAR`. |
| Ni / +UCr | Corrected frozen-slab job completed and electronically converged; the same constituent-density checks pass. | Exact match to `crcl3-newcals/crcl3-2x2-ni_ads-with-U/yes_vdw/S2/CONTCAR`. |
| Ni / +Uall | Corrected frozen-slab job completed and electronically converged; the same constituent-density checks pass. | Exact match to `crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Ni/clean/CONTCAR`; substantially different from +UCr. |

The Fe/Ni archived complex and isolated-atom CHGCARs were checked directly for cell, coordinates, grid, electron count and subtraction. Their original electronic-convergence histories were not retrieved alongside those archived densities; the explicit convergence checks above refer to the four new frozen-slab jobs. Matching relaxation geometries have completed local OUTCARs, but a coordinate match alone is not proof of the identity of a density calculation.

| Metal / treatment | Metal z (Å) | Mean Cr z (Å) | Metal height above mean Cr plane (Å) | FFT grid |
|---|---:|---:|---:|---|
| Co / +UCr | 11.8304 | 9.9798 | 1.8506 | 180 × 180 × 300 |
| Co / +Uall | 11.8304 | 9.9798 | 1.8506 | 180 × 180 × 300 |
| Fe / +UCr | 10.2691 | 10.0931 | 0.1760 | 160 × 160 × 280 |
| Fe / +Uall | 10.2634 | 10.0938 | 0.1696 | 160 × 160 × 280 |
| Ni / +UCr | 11.4222 | 9.9961 | 1.4261 | 160 × 160 × 280 |
| Ni / +Uall | 10.3267 | 10.0425 | 0.2843 | 160 × 160 × 280 |

Heights are descriptive, not a new adsorption-site classification. Fe lies near the Cr plane; Ni changes height by about 1.1 Å between treatments. Thus the contrast between panels includes actual coordination changes. The Ni comparison is not a fixed-geometry test of Hubbard U alone. Co uses 500 eV, whereas the Fe/Ni sources and corrected frozen slabs use 400 eV; the visualization normalization does not homogenize electronic-structure settings or demonstrate convergence with respect to them.

## Why the older panels differed

1. **Reference-density inconsistency.** The local Fe/Ni CDD files differ strongly from newer frozen-substrate recomputations already present on Arch. For the corrected files, substrate and isolated-metal coordinates exactly match their subsets of the complex, all three cells/grids match, and `rho_complex - rho_frozen_slab - rho_isolated_metal` reproduces every output voxel within 5e-9 in raw CHGCAR units. The older, much larger substrate-centered features are consistent with displacement contributions from incompatible reference geometries. The original commands that created those older files were not recovered, so their exact reference choice remains unverified.
2. **Spatial masking in existing artwork.** Commit `f94f066764e2a825c39f3fb48e91cad547515563` explicitly records removal of distant substrate features from the Fe/Ni renders. It changes PNGs without retaining a reproducible density-masking recipe. Such masking does not correct the underlying reference density and prevents faithful full-cell comparison. The normalized renders apply no spatial mask.
3. **Unrecorded/default isovalues.** Existing rendering code opens bare CHGCAR files without setting a common native VESTA isosurface block. The separate shared VESTA helper inspected in this audit emits `IMPORT_STRUCTURE` without `IMPORT_DENSITY` and a non-native short `ISURF`/`SURFC` construction. Neither route establishes that the old PNGs show the caption's physical threshold. This audit uses a full native configuration saved by VESTA itself, with explicit volumetric import and separately colored positive/negative surfaces.
4. **Density-unit conversion.** VESTA converts VASP charge densities to e/bohr³. Therefore ±0.005 e/Å³ requires ±0.000740923555853 e/bohr³ in its native isosurface settings. Entering 0.005 directly would mean about 0.0337417 e/Å³. See the [official VESTA manual, VASP volumetric-data format](https://jp-minerals.org/vesta/en/doc/VESTAch18.html).
5. **Caption/source mismatch.** The manuscript calls all three structures surface S2 adsorption and describes red/blue isosurfaces. The current source geometries do not support that blanket site assignment, and both old and normalized renders use yellow/cyan. The normalized copies retain yellow accumulation and cyan depletion; the publication caption needs reconciliation with the actual systems and colors.

## Quantitative comparison of old and corrected Fe/Ni fields

Values below are the 99th percentile of absolute physical CDD over the whole cell, not an isovalue selected separately for each panel. The total volume above the fixed ±0.005 e/Å³ threshold is a field diagnostic; it is not a Bader charge transfer.

| System | Old p99 (e/Å³) | Corrected p99 (e/Å³) | Corrected volume with abs(CDD) ≥ 0.005 (Å³) |
|---|---:|---:|---:|
| Fe / +UCr | 0.390078 | 0.025117 | 159.23 |
| Fe / +Uall | 0.389053 | 0.025015 | 164.77 |
| Ni / +UCr | 0.109597 | 0.011253 | 60.95 |
| Ni / +Uall | 0.183679 | 0.014313 | 78.92 |

Each corrected integral is within 4e-7 electrons of zero. Charge neutrality alone would not have detected the older geometry mismatch: their integrals are also close to zero.

## Review artifacts and reproducibility

- `Fig4_Ucr_normalized.pdf` and `Fig4_Uall_normalized.pdf`: full review copies. Only a–c are replaced; all pixels from row 980 onward, including d–f and their charge labels, are checked against each original PNG and preserved exactly.
- `Fig4_Ucr_abc_normalized.pdf` and `Fig4_Uall_abc_normalized.pdf`: just the requested top panels.
- Six `panel_[a-c]_[Co/Fe/Ni]_CDD_[Ucr/Uall]_normalized.png` files: separate panels for editing.
- Generator: `crcl3-newcals/postprosseing/normalize_fig4_cdd.py`; tests: `test_normalize_fig4_cdd.py`.
- Native projects, full untrimmed renders, settings, three complete corrected text grids and source audits: `crcl3-newcals/postprosseing/cdd_comparison/normalized_2026-10-29/`. The full Ni/+UCr text-grid transfer timed out; that original remains on Arch.
- `local_original_audit.json` records original paths, hashes, geometry matches and density statistics. `remote_source_audit.json` records corrected hashes, constituent electron counts, cell/grid/coordinate checks, subtraction errors, slab convergence and actual OUTCAR settings. `audit_remote_sources.py` retains the read-only validation procedure.
- Remote constituent data: `/home/cr/simulations/crcl3-HER/cdd_archive_cpx/` and `/home/cr/simulations/crcl3-HER/cdd_frozen_slabs/`. Corrected fields: `/home/cr/simulations/crcl3-HER/crcl3-newcals/postprosseing/cdd_rigorous_output/`.

The renderer uses a common c-axis view, full fractional bounds [0,1] on all axes, 60% opacity, yellow positive/cyan negative isosurfaces and the same atom palette. The displayed unit-cell width is calibrated to 1230 pixels in each panel with uniform scaling; no stretching or per-panel threshold adjustment is applied. Bounds checks verify that assembly removes only white margins, not model content. Native VESTA settings and the density arrays remain separate, so the display is reproducible.

For Ni/+UCr, `Ni_Ucr_render_grid.npz` contains a compact rendering-only copy, rounded to steps of 1e-8 e/Å³, with a maximum error checked on Arch of 4.99999986e-9 e/Å³. It records the SHA-256 of the full corrected source verified in `remote_source_audit.json`. The generator reconstructs `CHGCAR_render_Ni_Ucr` locally from that copy for VESTA; no original calculation file is modified. The rounding bound is one millionth of the display isovalue. Scientific statistics in the table above were computed from the full-precision source on Arch, not the rounded rendering copy. An intermediate remote export had no visible isosurfaces and was rejected during visual verification; the final deliverable is rendered locally and checked for surface-colored pixels.

These are comparison drafts, not a validated replacement for the manuscript's claimed uniform S2 series. No new DFT jobs were submitted, no manuscript captions or panels d–f were revised, and no files were distributed to the other manuscript directories. Resolve the intended adsorption sites and the remaining calculation-provenance gaps before publication.
